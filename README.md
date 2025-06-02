# Distributed Infrastructure Simulators: SimBlock, IOTA, and BlockSim

Description

This repository brings together simulators for blockchain and distributed technologies: SimBlock (Bitcoin model), BlockSim (Bitcoin and Ethereum), and IOTA (Tangle DAG). It includes installation guides, execution instructions, and code structure to facilitate the analysis of simulation results. This repository is aimed at those who want to experiment with consensus algorithms, propagation times, and node behavior in simulated environments.

## SIMBLOCK

### Introduction

SimBlock is an open-source blockchain network simulator developed by the Distributed Systems Group at the Tokyo Institute of Technology (https://github.com/dsg-titech/simblock). It is focused on simulating Bitcoin-like network behavior at the level of block propagation. It allows emulating a network of nodes and modifying node behavior to evaluate how those modifications affect block propagation and chain performance. It is notable for being a discrete-event-driven simulator, easy to extend to test different node strategies. A separate visualization tool called SimBlock Visualizer (https://github.com/dsg-titech/simblock-visualizer) is also available to animate block propagation based on generated simulation data.

In addition to this visualization method, a script called import json.py has been developed to interpret the output data from output.json, located in SimBlock/Simulaciones/Interprete/import json.py. This interpreter converts the output into .xlsx format for better user understanding. The resulting files are located in SimBlock/Simulaciones.

### Installation and Requirements

SimBlock is written in Java and can be run on Windows, macOS, and Linux (Ubuntu). It requires Java JDK 1.8.0 or higher and Gradle 5.1.1 or higher. The simulator repository includes a Gradle Wrapper, so pre-installing Gradle is not necessary.

Once the code is obtained, the typical process is to compile and then run the simulation. If Gradle is installed, compile it from the root project directory with:
```
gradle build
```
To run the simulator, the simplest way is using the following command from the project root:

```
gradle :simulator:run
```

To correctly execute the simulator and interpret the generated results, the following Python packages must be installed:

```
pip install pandas
pip install xlsxwriter
``` 

These are used for data analysis and export once the simulation is complete.

### Download and Structure

To obtain the simulator, clone the official repository with the following command:

``` 
git clone git@github.com:dsg-titech/simblock.git
```

This will generate the following directory structure:

```
simblock
+-- docs
+-- gradle
|   +-- wrapper
+-- simulator
    +-- src
        +-- dist
        |   +-- conf
        |   +-- out
        |       +-- graph
        +-- main
            +-- java
                +-- SimBlock
                    +-- ...
                    :
```

Simulation behavior parameters (such as node distribution, block times, network topology, etc.) are mainly found in the following classes:

| Location                   | SimulationConfiguration.java                                                |
|----------------------------|-----------------------------------------------------------------------------|
| `NUM_OF_NODES`             | Total number of simulated nodes in the network                             |
| `BLOCK_INTERVAL`           | Average time interval (in seconds) between blocks                          |
| `BLOCK_SIZE`               | Block size in bytes                                                        |
| `GENESIS_BLOCK_INTERVAL`   | Time of the genesis block (usually 0)                                      |
| `TOPOLOGY_SWITCH`          | Boolean value to enable/disable topology change during simulation          |
| `END_BLOCK_HEIGHT`         | Block height at which to stop the simulation                               |
| `SEED`                     | Seed for the random number generator (for reproducibility)                 |

| Location                   | NetworkConfiguration.java                                                   |
|----------------------------|-----------------------------------------------------------------------------|
| `REGION_LIST`              | List of simulated geographic regions                                       |
| `REGION_DISTRIBUTION`      | Percentage of nodes per region                                             |
| `LATENCY`                  | Matrix of latencies between regions (in milliseconds)                      |
| `UPLOAD_BANDWIDTH`         | Upload bandwidth per region (in Mbps)                                      |
| `DOWNLOAD_BANDWIDTH`       | Download bandwidth per region (in Mbps)                                    |
| `AVERAGE_MINING_POWER_LIST`| List defining average mining power for different groups of nodes           |
| `MINING_POWER_DISTRIBUTION`| Percentage distribution of mining power by group                           |
| `NUM_CONNECTIONS`          | Number of neighbors per node                                               |


## BLOCKSIM

### Introduction

BlockSim is a modular blockchain simulator designed to analyze and compare different blockchain network models like Bitcoin and Ethereum using a discrete-event-driven architecture (https://github.com/maher243/BlockSim). Its structure enables modeling of nodes, blocks, propagation, rewards, and consensus algorithms, allowing the observation of metrics such as the number of orphaned blocks, miner performance, and network efficiency. The simulator is entirely written in Python, and users can adjust parameters through the InputsConfig.py file.

In addition to the simulation engine, an analysis script Statistics.py is included, which generates a structured Excel report containing detailed information about blocks, miners, and rewards — useful for evaluating system behavior under various configurations.

>[!IMPORTANT]
>For more detailed information: https://www.frontiersin.org/articles/10.3389/fbloc.2020.00028/full

### Installation and Requirements

BlockSim is written in Python and can be run on Windows, macOS, and Linux (Ubuntu). It is developed for Python 3 and requires the following external libraries:

```
pip install pandas
pip install numpy
pip install xlsxwriter
pip install scikit-learn
```

To run the simulator, simply execute the main script from the terminal:

```
python Main.py
```

This will automatically generate the results in an Excel file in the root project directory.

### Download and Structure

To obtain the simulator, clone the official repository:

```
git clone git@github.com:maher243/BlockSim.git
```

This will generate the following structure:

```
BlockSim
+-- Models
|   +-- BaseModel.py
|   +-- BitcoinModel.py
|   +-- EthereumModel.py
+-- Event.py
+-- Scheduler.py
+-- Statistics.py
+-- InputsConfig.py
+-- Main.py
```

All main parameters are centralized in the InputsConfig.py file, allowing adjustment of both network and protocol-level behavior:

| Parameter                   | Description                                                              |
|-----------------------------|-----------------------------------------------------------------------------|
| `blockchain_model`          | Blockchain model to simulate: `0 = Base`, `1 = Bitcoin`, `2 = Ethereum`     |
| `simulation_time`           | Total simulation time in seconds                                            |
| `block_interval`            | Average time interval between blocks                                        |
| `number_of_nodes`           | Total number of nodes in the network                                        |
| `node_hashpower_distribution`| Mining power distribution among nodes                                       |
| `network_delay_mean`        | Average propagation delay between nodes                                     |
| `block_size`                | Maximum block size (in KB)                                                  |
| `transaction_size`          | Average transaction size (in KB)                                            |
| `block_reward`              | Base block reward                                                           |
| `uncle_inclusion`           | (Ethereum) Enables/disables uncle block inclusion                           |
| `uncle_reward_ratio`        | (Ethereum) Reward ratio for uncle blocks                                    |


## IOTA

### Introduction

"IOTA" refers to the IOTA Tangle network, which models the behavior of this DAG (Directed Acyclic Graph) structure used by IOTA instead of a traditional blockchain. This IOTA test setup allows for studying how the transaction graph grows, how transactions are propagated and confirmed, and how different parameters affect performance.

Hornet is the software developed by the IOTA Foundation, written in Go, and implements the full functionality of the latest advancements in the IOTA network (https://github.com/iotaledger/hornet).

### Installation and Requirements

This installation guide was carried out on a Linux system; it may vary on others.

Install git and vim:

```
sudo apt install vim git build-essential curl
```

Install Go Lang 1.19:

```
wget https://go.dev/dl/go1.19.5.linux-amd64.tar.gz 
sudo tar xzvf go1.19.5.linux-amd64.tar.gz -C /usr/local/
export PATH=$PATH:/usr/local/go/bin
source ~/.bashrc
```

Install Node Version Manager and Gallium (LTS version of Node.js):

```
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
nvm install --lts=Gallium
```

Install Rust:

```
curl https://sh.rustup.rs -sSf | sh
source "$HOME/.cargo/env"
```

Install the Solc compiler (used for creating smart contracts):

```
sudo add-apt-repository ppa:ethereum/ethereum
sudo apt update
sudo apt install solc
```

Install Docker:

```
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
apt-cache policy docker-ce
sudo apt install docker-ce
sudo systemctl status docker
sudo usermod -aG docker ${USER}
su - ${USER}
```

Install Docker Compose:

```
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose
```

While Docker focuses on running and creating individual containers, Docker Compose is used to coordinate and manage multiple containers working together — in this case, the nodes of the network we will create.

### Download and Structure

Once the files are downloaded, start the local Hornet node:

```
mkdir ~/iota-dev/private-network
```

This directory will contain all the private network configuration:

```
IOTA
+-- private-network
|   +-- config.json
|   +-- docker-compose.yml
|   +-- Dockerfile.txt
|   +-- supervisord.conf
```

Once configuration is set, build and run the network image. This will generate a sequence of transactions with the established latency and node behavior.

```
docker compose up
```

## Statistics and Results

The BlockSim and SimBlock simulators produce output files after simulations. For the IOTA test network, only configuration parameters are provided, which allow replicating the behavior of the network.
