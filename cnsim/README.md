
## Cloud-Native Simulation for Gossip Protocol
In this test, cloud native simulation is going to execute gossip protocol. This code is inspired by 
[repository:cnsim](https://github.com/wwiras/cnsim). 

### Implementation Steps

#### Step 1 - Construct network topology (using networkx)
Network topology is required to mimic the topology of distribution networks such as blockchain, VANET,
MANET and IoT. Network models that can be constructed by this script are BA (Barasbi Albert) / ER (Edos Renyi).
Examples of ER/BA network construction (using network_contructor.py file) are as follows:-

```python
# For ER network
# others - between 0.01 to 0.99
$ python network_constructor.py --nodes 10 --model ER --others 0.3
Initial status from the input .....
Number of nodes in the network: 10
Connection probability (degree): 0.3
average_degree: 3 with average_degree_raw: 2.6999999999999997
Graph: Graph with 10 nodes and 14 edges
avg_graph_degree_raw: 2.8
avg_graph_degree: 3
nx.is_connected(ER_graph) : True
Graph Before: Graph with 10 nodes and 14 edges
ER network model is SUCCESSFUL ! ....
Graph After: Graph with 10 nodes and 14 edges
Do you want to save the graph? (y/n): y
Topology saved to nodes10_Apr172025124435_ER0.3.json
```

```python
# For BA network
# others - must be more than 1 and not float format
$ python network_constructor.py --nodes 30 --model BA --others 5
Initial status from the input .....
Number of nodes in the network: 30
Average neighbor (degree): 5
Creating BARABASI ALBERT (BA) network model .....
Current average degree: 8.333333333333334 - Greater than target degree
Target degree:5
nx.is_connected(network): True
Graph Before: Graph with 30 nodes and 125 edges
BA network model is SUCCESSFUL ! ....
Graph After: Graph with 30 nodes and 125 edges
Do you want to save the graph? (y/n): y
Topology saved to nodes30_Apr172025124309_BA5.json
```

Here are some guideline on using **network_constructor.py**
```python
$ python network_constructor.py --help                                   
usage: network_constructor.py [-h] --nodes NODES --others OTHERS --model MODEL [--minlat MINLAT] [--maxlat MAXLAT] [--adjust ADJUST] [--save]

Create network topology using networkx graphs and save it to json file

options:
  -h, --help       show this help message and exit
  --nodes NODES    Total number of nodes for the topology
  --others OTHERS  Total number of probability (ER) or parameter (BA)
  --model MODEL    Total number of nodes for the topology
  --minlat MINLAT  Min latency of nodes for the topology (optional)
  --maxlat MAXLAT  Max latency of nodes for the topology (optional)
  --adjust ADJUST  Adjustment factor for the topology (optional)
  --save           Save new topology to json(default: False) - (optional)

```
> **_NOTE:_** If minlat=0 and maxlat=0, no latency added to the topology.

#### Step 2 - Develop grpc communication protocol (using python3)
gRPC is used for inter-node communication, providing efficient and reliable message passing. gRPC is a
high-performance Remote Procedure Call (RPC) framework that allows nodes to communicate as if they 
were calling local functions. The *gossip.proto* file defines the communication interface, specifying 
the message structure and service definitions. This file is then compiled (with command below) and 
generates two *python* files (python classes) in the same directory:
* *gossip_pb2.py*: Contains the *python* classes for your protocol buffer messages (GossipMessage, Acknowledgment).
* *gossip_pb2_grpc.py*: Contains the *python* classes for your gRPC service (GossipServiceServicer, GossipServiceStub).
```python
python -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. gossip.proto
```

#### Step 3: Gossip Script (Direct Mail Gossip)
The simulator implements a "Direct Mail Gossip" protocol, where nodes directly send messages 
to their neighbors. This is a basic form of gossip protocol, where each node maintains a list of 
its neighbors and forwards messages to them.

- *start.py*: initiates the gossip process by sending a message to the node itself. This simulates a 
node originating a message.
- *node.py*: acts as a gRPC server, receiving and propagating messages to neighboring nodes. It 
listens for incoming messages and, upon receipt, forwards them to the nodes listed in its 
neighbor list.
```shell
# Initiate gossip with the message "Hello, Gossip!" example
python start.py --message "Hello, Gossip!"
```
> **_NOTE:_**  In this simulator, the message will be using a unique ID for easy filtering. Example: '4abf-cubaan50-1'
> This mean this test is for 50 nodes and '-1' as the first test cycle
