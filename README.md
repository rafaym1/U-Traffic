# U-Traffic
Traffic Flow Optimization using Graph Neural Networks
# Introduction
This project implements a traffic flow optimization system using Graph Neural Networks (GNNs) and synthetic traffic data. The system models urban road networks as graphs, where intersections are nodes and roads are edges. It uses PyTorch Geometric for GNN implementation and includes traffic pattern generation with realistic morning and evening peak patterns.

# Features

* Graph Neural Network (GNN) based traffic flow optimization
* Synthetic traffic data generation with realistic patterns
* Grid-like road network modeling
* Real-time traffic signal phase prediction
* Network visualization and training progress monitoring
* Scalable to different network sizes

# Project Structure
traffic-flow-optimization/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── gnn.py
│   │   └── optimizer.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── data_generator.py
│   └── utils/
│       ├── __init__.py
│       └── visualization.py
├── requirements.txt
├── main.py
├── README.md
└── .gitignore

# Requirements
* torch>=1.9.0
* torch-geometric>=2.0.0
* networkx>=2.6.3
* numpy>=1.21.0
* pandas>=1.3.0
* matplotlib>=3.4.3
* scikit-learn>=0.24.2
