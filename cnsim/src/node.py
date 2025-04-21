
import grpc
import os
import socket
from concurrent import futures
import gossip_pb2
import gossip_pb2_grpc
import json
import time
from kubernetes import client, config


class Node(gossip_pb2_grpc.GossipServiceServicer):

    def __init__(self, service_name):
        self.hostname = socket.gethostname()
        print(f"self.hostname: {self.hostname}", flush=True)
        self.host = socket.gethostbyname(self.hostname)
        print(f"self.host: {self.host}", flush=True)
        self.port = '5050'
        self.service_name = service_name
        self.app_name = 'bcgossip'
        self.filename = os.environ['FILENAME']
        # Get topology detail from json file
        self.topology = self.get_topology('topology')
        # List to keep track of IPs of neighboring nodes
        self.susceptible_nodes = []
        # Set to keep track of messages that have been received to prevent loops
        self.received_message = ""
        # self.gossip_initiated = False

    def get_topology(self,topology_folder):
        """
        Reads and returns the content of a specific JSON file from the topology directory.

        Args:
            topology_folder: The name of the folder containing the topology files.
            filename: The exact name of the JSON topology file to read.

        Returns:
            A dictionary representing the loaded JSON data, or None if the file is not found.
        """
        current_directory = os.getcwd()
        topology_dir = os.path.join(current_directory, topology_folder)
        topology_file_path = os.path.join(topology_dir, self.filename)

        if os.path.exists(topology_file_path) and os.path.isfile(topology_file_path):
            try:
                with open(topology_file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {topology_file_path}")
                return None
        else:
            print(f"Topology file not found: {topology_file_path}")
            return None

    def get_neighbours(self):

        # Load in-cluster config (for running inside Kubernetes)
        config.load_incluster_config()

        # Create CoreV1Api instance
        v1 = client.CoreV1Api()

        # Define the namespace and label selector
        namespace = "default"  # Replace with your namespace if different
        label_selector = f"app={self.app_name}"  # Use the correct label key and value

        try:
            # First, we need to get all pod names and IPs
            # Fetch Pods in the specified namespace with the label selector
            ret = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)

            # temporary of all nodes (name, ip) except own IP addr
            all_pods = [(pod.metadata.name, pod.status.pod_ip) for pod in ret.items if self.host != pod.status.pod_ip]

            # Second, pick only neighbors that have edge with current pod/nodes
            # This step will refer to json network topology the we've obtained using
            # get_topology function previously

            latency_option = os.getenv('LATENCY_OPTION', 'weight')  # Default to 'weight'

            # Clear the existing list to refresh it
            self.susceptible_nodes = []

            # get neighbor pod's name and IPs from the all_pods list
            for edge in self.topology['edges']:
                neighbor_name = None
                neighbor_ip = None
                neighbor_latency = None

                if edge['source'] == self.hostname:
                    neighbor_name = edge['target']
                    neighbor_latency = edge.get(latency_option)
                elif edge['target'] == self.hostname:
                    neighbor_name = edge['source']
                    neighbor_latency = edge.get(latency_option)

                if neighbor_name:
                    for pod_name, pod_ip in all_pods:
                        if pod_name == neighbor_name:
                            self.susceptible_nodes.append((pod_name, pod_ip, neighbor_latency))
                            break

            # Optional: Log the list of neighbors for debugging
            # print(f"Susceptible nodes: {self.susceptible_nodes}", flush=True)

        except client.ApiException as e:
            print(f"Failed to fetch Pods: {e}", flush=True)

    def SendMessage(self, request, context):

        """
        Receiving message from other nodes
        and distribute it to others (multi rounds gossip)
        """
        message = request.message
        sender_id = request.sender_id
        received_timestamp = time.time_ns()

        # For initiating acknowledgment only
        if sender_id == self.host:
            self.received_message = message
            log_message = (f"Gossip initiated by {self.hostname} ({self.host}) at "
                           f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(received_timestamp / 1e9))}")
            self._log_event(message, sender_id, received_timestamp, None,
                            'initiate', log_message)
            self.gossip_message(message, sender_id)
            return gossip_pb2.Acknowledgment(details=f"Done propagate! {self.host} received: '{message}'")

        # Check whether the message is already received or no
        # Notify whether accept it or ignore it
        elif self.received_message == message:
            log_message = f"{self.host} ignoring duplicate message: {message} from {sender_id}"
            self._log_event(message, sender_id, received_timestamp, None, 'duplicate', log_message)
            return gossip_pb2.Acknowledgment(details=f"Duplicate message ignored by ({self.host})")
        # Distribute gossip
        # Once received, update message and distribute to connected neighbors
        else:
            self.received_message = message
            propagation_time = (received_timestamp - request.timestamp) / 1e6
            log_message = (f"({self.hostname}({self.host}) received: '{message}' from {sender_id}"
                           f" in {propagation_time:.2f} ms ")
            self._log_event(message, sender_id, received_timestamp, propagation_time, 'received', log_message)
            self.gossip_message(message, sender_id) # key distribution
            return gossip_pb2.Acknowledgment(details=f"{self.host} received: '{message}'")

    def gossip_message(self, message, sender_ip):
        # Refresh list of neighbors before gossiping to capture any changes
        if len(self.susceptible_nodes) == 0:
            self.get_neighbours()
        print(f"self.susceptible_nodes: {self.susceptible_nodes}", flush=True)

        # print(f"self.susceptible_nodes={self.susceptible_nodes}",flush=True)
        for peer_name, peer_ip, neighbor_latency in self.susceptible_nodes:
            # Exclude the sender from the list of nodes to forward the message to
            if peer_ip != sender_ip:

                # Record the send timestamp
                send_timestamp = time.time_ns()

                # Simulate latency
                time.sleep(float(neighbor_latency) / 1000)

                with grpc.insecure_channel(f"{peer_ip}:5050") as channel:
                    try:
                        stub = gossip_pb2_grpc.GossipServiceStub(channel)
                        stub.SendMessage(gossip_pb2.GossipMessage(
                            message=message,
                            sender_id=self.host,
                            timestamp=send_timestamp,
                            latency_ms=neighbor_latency  # Include latency in the gRPC message
                        ))
                    except grpc.RpcError as e:
                        print(f"Failed to send message: '{message}' to {peer_ip}: {e}", flush=True)

    def _log_event(self, message, sender_id, received_timestamp, propagation_time, event_type, log_message):
        """Logs the gossip event as structured JSON data."""
        event_data = {
            'message': message,
            'sender_id': sender_id,
            'receiver_id': self.host,
            'received_timestamp': received_timestamp,
            'propagation_time': propagation_time,
            'event_type': event_type,
            'detail': log_message
        }

        # Print both the log message and the JSON data to the console
        print(json.dumps(event_data), flush=True)

    def start_server(self):
        """ Initiating server """
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        print(f"{self.hostname}({self.host}) listening on port {self.port}", flush=True)
        server.start()
        server.wait_for_termination()

def run_server():
    service_name = os.getenv('SERVICE_NAME', 'bcgossip-svc')
    node = Node(service_name)
    node.start_server()

if __name__ == '__main__':
    run_server()