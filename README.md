# Interactive Tool for Analyzing Polarization & Echo Chambers

This project is an interactive web application built with **Python** and
**Streamlit** for Social Network Analysis (SNA). It helps researchers,
students, and enthusiasts visualize and analyze **polarization** and
**echo chambers** in networks.

## 🚀 Live Application

Use the live tool here:\
**https://rajfauzdar-interactive-tool-for-analyzing-polarizati-app-n71kaq.streamlit.app/**

## 📌 The Problem: Polarization & Echo Chambers

In online social systems, people often interact with like-minded
individuals. This creates **echo chambers**, reinforcing beliefs and
increasing **social and political polarization**.

Understanding these divisions is essential for studying:

-   How information spreads\
-   How misinformation amplifies\
-   How communities isolate themselves

This tool provides a hands-on way to:

-   Measure division using network metrics\
-   Visualize communities and bridge edges\
-   Simulate interventions by adding/removing edges


## ✨ Key Features

### ✔ Easy Data Upload

Upload your network from a simple **edgelist** file (`.edges`, `.txt`,
`.csv`).

### ✔ Community Detection

Automatically identifies communities (echo chambers) using the **Louvain
algorithm**.

### ✔ Interactive Visualization

Built with **pyvis**, showing a draggable, zoomable, color-coded network
graph.

### ✔ Key Metrics Computed

-   **Modularity** -- Strength of community division\
-   **Polarization Score (Assortativity)** -- Preference for
    intra-community links\
-   **Bridge Connections** -- Edges connecting different communities

### ✔ Real-Time Simulation

The simulation uses a **sticky partition** strategy where communities
remain fixed after the initial Louvain detection.\
When edges are added or removed: - Communities are **not
recalculated** - Modularity and polarization are updated instantly

This makes it easy to observe how individual edges affect the network.

## 🚀 How to Use the Tool

1.  Open the app.

2.  Upload a graph in edgelist format like:

        node1 nodeA
        node2 nodeB
        node1 nodeC

3.  Click **Load and Analyze Network**.

4.  View computed metrics and visualizations.

5.  Add or remove edges to see real-time metric updates.

## 📂 Demo Data

Use the **email-univ.edges** dataset included in the repository.

## 💻 Run Locally

### 1. Clone the repository

``` bash
git clone https://github.com/rajfauzdar/interactive-tool-for-analyzing-polarization.git
cd interactive-tool-for-analyzing-polarization
```

### 2. Create & activate virtual environment

#### Windows

``` bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### macOS / Linux

``` bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Run the Streamlit app

``` bash
streamlit run app.py
```

## 🛠️ Libraries Used

-   Streamlit\
-   NetworkX\
-   python-louvain\
-   Pyvis\
-   Pandas


