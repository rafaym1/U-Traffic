# -*- coding: utf-8 -*-
"""U-Traffic.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ostpBI8VN0KFGqitlM_TAmzadpmlM5W1
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import networkx as nx
import numpy as np
import pandas as pd
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
import ot
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

class SyntheticDataGenerator:
    """Generate synthetic traffic data based on PeMS-like patterns"""
    def __init__(self, num_nodes=30, num_timesteps=288):  # 288 = 24 hours * 12 (5-min intervals)
        self.num_nodes = num_nodes
        self.num_timesteps = num_timesteps

    def generate_data(self):
        """Generate synthetic traffic data with realistic patterns"""
        # Generate base traffic patterns
        time = np.linspace(0, 24, self.num_timesteps)

        # Create morning and evening peaks
        morning_peak = 10 * np.exp(-(time - 8)**2 / 4)  # Peak at 8 AM
        evening_peak = 8 * np.exp(-(time - 17)**2 / 4)  # Peak at 5 PM
        base_pattern = morning_peak + evening_peak

        # Generate data for each node with some random variation
        data = np.zeros((self.num_timesteps, self.num_nodes))
        for i in range(self.num_nodes):
            noise = np.random.normal(0, 0.5, self.num_timesteps)
            scale_factor = np.random.uniform(0.8, 1.2)
            data[:, i] = scale_factor * base_pattern + noise

        # Ensure non-negative values
        data = np.maximum(data, 0)

        # Generate adjacency matrix (grid-like structure)
        adj_matrix = self._generate_grid_adjacency()

        return data, adj_matrix

    def _generate_grid_adjacency(self):
        """Generate adjacency matrix for a grid-like road network"""
        # Create a grid network
        grid_size = int(np.sqrt(self.num_nodes))
        G = nx.grid_2d_graph(grid_size, grid_size)

        # Convert to regular graph with numeric node labels
        G = nx.convert_node_labels_to_integers(G)

        # Get adjacency matrix
        adj_matrix = nx.adjacency_matrix(G).todense()
        return np.array(adj_matrix)

class TrafficGNN(nn.Module):
    def __init__(self, num_node_features, hidden_channels, num_classes):
        super(TrafficGNN, self).__init__()
        self.conv1 = GCNConv(num_node_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, num_classes)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)

        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)

        x = self.conv3(x, edge_index)
        return x

class TrafficOptimizer:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.road_network = nx.Graph()
        self.model = TrafficGNN(
            num_node_features=1,  # Traffic flow
            hidden_channels=64,
            num_classes=4  # Signal phases
        )
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)
        self.scaler = StandardScaler()

    def create_road_network(self, adj_matrix):
        """Create road network from adjacency matrix"""
        G = nx.from_numpy_array(adj_matrix)
        self.road_network = G

    def prepare_data(self, features):
        """Prepare data for training"""
        # Scale features
        scaled_features = self.scaler.fit_transform(features)

        # Convert to torch tensors
        features_tensor = torch.FloatTensor(scaled_features)

        # Create edge index from road network
        edge_index = torch.tensor([[e[0], e[1]] for e in self.road_network.edges()]).t().contiguous()

        return features_tensor, edge_index

    def train(self, features, num_epochs=50):
        """Train the model"""
        features_tensor, edge_index = self.prepare_data(features)

        target_phases = torch.zeros((features_tensor.shape[0], self.num_nodes, 4))

        losses = []
        for epoch in range(num_epochs):
            epoch_loss = 0
            for i in range(len(features_tensor)):
                self.model.train()
                self.optimizer.zero_grad()

                # Reshape features for current timestep
                current_features = features_tensor[i].reshape(self.num_nodes, 1)

                # Forward pass
                predicted_phases = self.model(current_features, edge_index)

                # Calculate loss
                loss = F.mse_loss(predicted_phases, target_phases[i])

                # Backward pass
                loss.backward()
                self.optimizer.step()

                epoch_loss += loss.item()

            avg_loss = epoch_loss / len(features_tensor)
            losses.append(avg_loss)

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{num_epochs}, Average Loss: {avg_loss:.4f}")

        return losses

    def visualize_network(self):
        """Visualize the road network"""
        plt.figure(figsize=(10, 10))
        pos = nx.spring_layout(self.road_network)
        nx.draw(self.road_network, pos,
                node_color='lightblue',
                node_size=500,
                with_labels=True,
                font_size=8,
                font_weight='bold')
        plt.title("Road Network Visualization")
        plt.show()

    def visualize_training_loss(self, losses):
        """Visualize training loss"""
        plt.figure(figsize=(10, 5))
        plt.plot(losses)
        plt.title("Training Loss Over Time")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.grid(True)
        plt.show()

def main():
    # Generate synthetic data
    print("Generating synthetic traffic data...")
    data_generator = SyntheticDataGenerator(num_nodes=30, num_timesteps=288)
    features, adj_matrix = data_generator.generate_data()

    # Initialize traffic optimizer
    print("Initializing traffic optimizer...")
    optimizer = TrafficOptimizer(num_nodes=30)

    # Create road network
    optimizer.create_road_network(adj_matrix)

    # Visualize network
    print("Visualizing road network...")
    optimizer.visualize_network()

    # Train model
    print("Training model...")
    losses = optimizer.train(features, num_epochs=50)

    # Visualize training progress
    print("Visualizing training progress...")
    optimizer.visualize_training_loss(losses)

if __name__ == "__main__":
    main()
