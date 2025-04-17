
## Cloud-Native Simulation Framework
In this test, cloud native simulation is going to execute gossip protocol. This code is inspired by 
[repository:cnsim](https://github.com/wwiras/cnsim). 

### Implementation Steps

#### Step 1 - Construct network topology (using networkx)

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
