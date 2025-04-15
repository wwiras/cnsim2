
## Cloud-Native Simulation Framework Validation
This code is for the validation of Cloud Native Simulator.


### Validation Overview

In this repository, we will validate cloud native simulator by 
comparing total propagation time (ms) with other simulators like **mininet**, **peersim**, and **omnet++**. 
All the results are then compared with Bitnodes (real time blokchain propagation time). For the topology,
The simulators will be using network model with distribution degree of 8-32 connections (80% nodes), 100+ for hubs (20%).
This topology will ensure fair comparison.

#### Cloud-Native Simulator
This simulation will be based on previous [repository:cnsim](https://github.com/wwiras/cnsim) except this time
it will be using statefulset instead of deployment. This is because the simulator needs to know the
topology and its neighbor. 
