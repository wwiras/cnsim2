import networkx as nx
import matplotlib.pyplot as plt
import json
from itertools import combinations
import random
import os
from datetime import datetime
import argparse

def set_network_latency(graph,min_latency=1,max_latency=100):

    # Registered network graph with its neighbor
    # and its weight (latency)
    for u, v in combinations(graph, 2):
        if graph.has_edge(u, v) and 'weight' not in graph.edges[u, v]:
            graph.edges[u, v]['weight'] = random.randint(min_latency,max_latency)

    return graph

def set_network_mapping(graph,number_of_nodes):

    # Rename nodes
    mapping = {i: f"gossip-statefulset-{i}" for i in range(number_of_nodes)}
    network = nx.relabel_nodes(graph, mapping)

    return network

def construct_BA_network(number_of_nodes, parameter, adjustment=0):
    # Manually creating BA model network
    # Initial status
    # Print some information about the graph
    print(f"Initial status from the input .....")
    print(f"Number of nodes in the network: {number_of_nodes}")
    print(f"Average neighbor (degree): {parameter}")

    # Construct Barabási – Albert(BA) model topology
    # Create a BA model graph
    print(f"Creating BARABASI ALBERT (BA) network model .....")

    # Make sure all nodes are connected, if not do not proceed
    connected = False
    while not connected:

        # Graph creation depends on adjustment value
        # if adjustment == 0; used default networkx barabasi_albert function
        # if adjustment > 0; Create barabasi_albert network manually
        if adjustment == 0:
            network = nx.barabasi_albert_graph(number_of_nodes, parameter)
        else:
            # Create an empty graph
            network = nx.Graph()
            # print(f"Graph before adding edges: {network}")

            # Get mininum degree (edges)
            min_degree = 1

            # Get maximum degree edges
            if ((parameter + parameter) - adjustment) >= parameter:
                max_degree = (parameter + parameter) - adjustment
            else:
                # max degree (or connections) not logic, do not proceed
                break

            # Add nodes with adjustment (edges/degree) one by one
            for node in range(number_of_nodes):

                # get degree
                degree = random.randint(min_degree, max_degree)
                # print(f"current degree: {degree}")

                # get edges for current node (i)
                for conn in range(degree):
                    potential_neighbor_node = random.randint(0, number_of_nodes-1)
                    if potential_neighbor_node != node:
                        network.add_edge(node, potential_neighbor_node)
                        # print(f" Add neighbor node: {potential_neighbor_node} to node: {node}")

        # After all edges updated
        # print(f"Graph: {network}")

        # Make sure BA network model degree connection average is as input
        # Check current and target average degree connection
        current_avg_degree = sum(dict(network.degree()).values()) / number_of_nodes
        # print(f"Current average degree: {current_avg_degree}")
        target_avg_degree = parameter
        # print(f"Target average degree: {target_avg_degree}")
        # print(f"nx.is_connected(network): {nx.is_connected(network)}")

        if target_avg_degree <= current_avg_degree and nx.is_connected(network):
            print(f"Current average degree: {current_avg_degree} is higher than or the same as Target average degree:{target_avg_degree}  ")
            connected = True
        else:
            print(f"Current average degree: {current_avg_degree} is smaller than Target average degree:{target_avg_degree}")
            print(f"Or connected is {nx.is_connected(network)} ...")
            break

    if connected:
        return network
    else:
        return connected

def construct_ER_network(number_of_nodes, probability_of_edges):

    average_degree_raw = probability_of_edges * (number_of_nodes - 1)  # average_degree float
    average_degree = round(average_degree_raw)  # average_degree rounding

    print(f"Initial status from the input .....")
    print(f"Number of nodes in the network: {number_of_nodes}")
    print(f"Connection probability (degree): {probability_of_edges}")
    print(f"average_degree: {average_degree} with average_degree_raw: {average_degree_raw}")

    # Create an ER model graph
    ER_graph = nx.erdos_renyi_graph(number_of_nodes, probability_of_edges)
    print(f"Graph: {ER_graph}")

    # Get the separate components
    components = list(nx.connected_components(ER_graph))
    # print(f"components: {components}")

    # If there's more than one component, connect them
    if len(components) > 1:
        for i in range(len(components) - 1):
            # Choose a random node from the current component
            node1 = random.choice(list(components[i]))
            # Choose a random node from the next component
            node2 = random.choice(list(components[i + 1]))
            # Add an edge between the two nodes
            ER_graph.add_edge(node1, node2)

            if nx.is_connected(ER_graph):
                break

    avg_graph_degree_raw = sum(dict(ER_graph.degree()).values()) / number_of_nodes
    print(f"avg_graph_degree_raw: {avg_graph_degree_raw}")
    avg_graph_degree = round(avg_graph_degree_raw)
    print(f"avg_graph_degree: {avg_graph_degree}")

    if avg_graph_degree == average_degree:
        print(f"nx.is_connected(ER_graph) 1 : {nx.is_connected(ER_graph)}")

        # Get the separate components
        # components = list(nx.connected_components(ER_graph))

        # Print the components
        # print(f"Separate components: {components}")
        # print(f"Total Separate components: {len(components)}")

        if nx.is_connected(ER_graph):
            return ER_graph
        else:
            return False
    else:
        return False

def iterate_and_print_graph(graph):
    """Iterates over the graph and prints its content in a structured format."""

    print("\nGraph Data:")
    # Print general graph info
    print("Graph:", graph)
    # print(f"Average weight (in this case - latency): {calculate_average_weight(graph):.4f} ms")
    print(f"Average weight (in this case - latency): {graph.average_weight:.4f} ms")

def calculate_average_weight(graph):

    """Calculates the average weight of edges in a graph.

      Args:
        graph_edges_data: The output of `graph.edges(data=True)`, which is a list of
                           tuples with edge information (source, target, attributes).

      Returns:
        The average weight of the edges in the graph.
      """

    total_weight = 0
    num_edges = 0

    for u, v, data in graph.edges(data=True):
        if 'weight' in data:
            total_weight += data['weight']
            num_edges += 1

    if num_edges > 0:
        average_weight = total_weight / num_edges
        return average_weight
    else:
        return 0  # Or handle the case where there are no edges with weights

def display_graph(graph, title="Network Graph"):
  """
  Displays a network graph using Matplotlib.

  Args:
    graph: The NetworkX graph object.
    title: (Optional) The title of the plot.
  Warning : Do not use this if nodes more than 100 are present in the graph
  It will use lot of memory
  """

  pos = nx.spring_layout(graph)  # Position nodes using spring layout

  # Draw nodes with labels
  nx.draw(graph, pos, with_labels=True, node_size=500, node_color="lightblue")

  # Draw edge labels (if any)
  edge_labels = nx.get_edge_attributes(graph, 'weight')
  if edge_labels:
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

  plt.title(title)
  plt.show()

def save_topology_to_json(graph, others, type="BA"):
    """
    Saves the network topology to a JSON file.

    Args:
    graph: The NetworkX graph object.
    filename: (Optional) The name of the JSON file to save.
    """

    # Get current date and time + second
    now = datetime.now()
    dt_string = now.strftime("%b%d%Y%H%M%S")  # Format: Dec232024194653
    filename = f"nodes{len(graph)}_{dt_string}_{type}{others}.json"

    # Create directory if it doesn't exist
    output_dir = "topology"
    os.makedirs(output_dir, exist_ok=True)

    # prepare topology in json format
    # Successfully installed networkx-3.4.2
    # Use "edges" for forward compatibility
    graph_data = nx.node_link_data(graph, edges="edges")
    graph_data["weight_average"] = graph.average_weight
    graph_data["total_edges"] = graph.total_edges
    graph_data["total_nodes"] = graph.total_nodes
    file_path = os.path.join(output_dir, filename)
    with open(file_path, 'w') as f:
        json.dump(graph_data, f, indent=4)
    print(f"Topology saved to {filename}")

def confirm_save(graph,others,model):
    save_graph = input("Do you want to save the graph? (y/n): ")
    if save_graph.lower() == 'y':
        # Save the topology to a JSON file
        save_topology_to_json(graph, others, model)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create network topology using networkx graphs and save it to json file")
    parser.add_argument('--nodes', required=True, help="Total number of nodes for the topology")
    parser.add_argument('--others', required=True, help="Total number of probability (ER) or parameter (BA)")
    parser.add_argument('--model', required=True, help="Total number of nodes for the topology")
    # Add the optional argument with a default value of False
    parser.add_argument('--minlat', default=0 , help="Min latency of nodes for the topology")
    parser.add_argument('--maxlat', default=0, help="Max latency of nodes for the topology")
    parser.add_argument('--adjust', default=0, help="Adjustment factor for the topology")
    parser.add_argument('--display', action='store_true', help="Display new topology (default: False)")
    parser.add_argument('--save', action='store_true', help="Save new topology to json(default: False)")
    args = parser.parse_args()

    # Getting minimum and maximum latency
    minlat = int(args.minlat)
    # print(f"minlat: {minlat}")
    maxlat = int(args.maxlat)
    # print(f"maxlat: {maxlat}")
    adjust = int(args.adjust)
    # print(f"adjust: {adjust}")

    if args.model== "BA":

        # Using BA Model
        number_of_nodes = int(args.nodes)
        parameter = int(args.others)
        graph = construct_BA_network(number_of_nodes, parameter,adjust)

    else:

        # Using ER Model
        number_of_nodes = int(args.nodes)
        probability_of_edges = float(args.others) # 0.5
        graph = construct_ER_network(number_of_nodes, probability_of_edges)

    if graph:

        print(f"Graph Before: {graph}")

        # Set network mapping (gossip-statefulset labelling)
        network = set_network_mapping(graph, number_of_nodes)

        # Set latency ranging from minimum and maximum latency
        network = set_network_latency(network,minlat,maxlat)

        # Get average latency for the network
        network.average_weight = calculate_average_weight(network)

        # Get nodes and edge info
        network.total_edges = network.number_of_edges()
        network.total_nodes = network.number_of_nodes()

        # Asking to save it or not
        print(f"{args.model} network model is SUCCESSFUL ! ....")
        print(f"Graph After: {network}")
        if args.model == 'BA':
            confirm_save(network,parameter, args.model)
        else:
            confirm_save(network, probability_of_edges, args.model)

    else:
        print(f"{args.model} network model is FAIL ! ....")


