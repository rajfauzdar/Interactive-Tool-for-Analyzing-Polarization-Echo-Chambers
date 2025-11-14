import streamlit as st
import networkx as nx
import community as community_louvain  # This is the python-louvain library
from pyvis.network import Network
import os
import streamlit.components.v1 as components  # Import components
import pandas as pd  # <-- FIX 1: Added pandas back for the bridge table

# --- Constants ---
# Get the absolute path of the directory containing this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# We still need a place to save the temp viz file
HTML_VIZ_PATH = os.path.join(SCRIPT_DIR, "graph_visualization.html")


# --- Page Configuration ---
st.set_page_config(
    page_title="Polarization & Echo Chamber Analyzer",
    page_icon="🕸️",
    layout="wide",
)

# --- Helper Functions ---


@st.cache_data
def load_edgelist_graph(uploaded_file):
    """
    Loads a graph from an edgelist file (.edges, .txt).
    Assumes space or tab-delimited nodes.
    """
    try:
        # Read the uploaded file as text
        string_data = uploaded_file.getvalue().decode("utf-8")
        lines = string_data.splitlines()

        # Parse the edgelist. This handles spaces/tabs.
        G = nx.parse_edgelist(lines)

        if G.number_of_nodes() == 0:
            st.error(
                "Could not parse any nodes/edges. Is the file empty or in the wrong format?"
            )
            return None

        st.success(
            f"Successfully loaded graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges."
        )
        return G
    except Exception as e:
        st.error(f"Error loading edgelist file: {e}")
        return None


# --- FIX 2: LOGIC SPLIT ---


def detect_communities_and_analyze(G):
    """
    HEAVY analysis function.
    Runs community detection ONCE and calculates all metrics.
    """
    # 1. Detect communities (echo chambers)
    partition = community_louvain.best_partition(G)

    # 2. Calculate Modularity
    modularity = community_louvain.modularity(partition, G)

    # 3. Calculate Polarization Score (Attribute Assortativity)
    # We use the detected partition as the 'community' attribute
    nx.set_node_attributes(G, partition, "community")

    try:
        polarization_score = nx.attribute_assortativity_coefficient(G, "community")
    except Exception:
        polarization_score = 0.0  # Default to 0 if calculation fails

    # 4. Identify bridge connections
    bridges = []
    for u, v in G.edges():
        # Check if nodes have community attribute before accessing
        if "community" in G.nodes[u] and "community" in G.nodes[v]:
            if G.nodes[u]["community"] != G.nodes[v]["community"]:
                bridges.append((u, v))
        elif "community" in G.nodes[u] or "community" in G.nodes[v]:
            pass

    return partition, modularity, polarization_score, bridges


def recalculate_metrics(G, original_partition):
    """
    LIGHT analysis function.
    Uses the "sticky" original partition to recalculate metrics
    after an edge add/remove. Does NOT re-detect communities.
    """
    # 1. Calculate Modularity *using the original partition*
    modularity = community_louvain.modularity(original_partition, G)

    # 2. Set attributes *using the original partition*
    # This is crucial. We only set attributes for nodes that
    # were in the original partition.
    nx.set_node_attributes(G, original_partition, "community")

    # 3. Calculate Polarization Score
    try:
        # attribute_assortativity_coefficient gracefully ignores
        # nodes that don't have the 'community' attribute (e.g., new nodes)
        polarization_score = nx.attribute_assortativity_coefficient(G, "community")
    except Exception:
        polarization_score = 0.0

    # 4. Identify bridge connections *using the original partition*
    bridges = []
    for u, v in G.edges():
        # Check if nodes *exist* in the original partition
        if u in original_partition and v in original_partition:
            if original_partition[u] != original_partition[v]:
                bridges.append((u, v))

    return modularity, polarization_score, bridges


def create_interactive_visualization(G, partition):
    """Creates a Pyvis visualization and returns it as HTML."""
    net = Network(
        height="700px", width="100%", bgcolor="#222222", font_color="white", heading=""
    )

    # Add nodes with community-based coloring
    for node, data in G.nodes(data=True):
        # Use .get() for safety. New nodes won't be in the partition.
        community_id = partition.get(node)
        net.add_node(
            node,
            label=str(node),
            group=community_id,
            title=f"Community: {community_id}",
        )

    # Add edges
    net.add_edges(G.edges())

    # Configure physics for better layout
    net.set_options(
        """
    var options = {
      "nodes": {
        "borderWidth": 2,
        "borderWidthSelected": 4
      },
      "edges": {
        "color": {
          "inherit": "from"
        },
        "smooth": {
          "type": "continuous"
        }
      },
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      }
    }
    """
    )

    # Save to an HTML file and return the file's content
    try:
        net.save_graph(HTML_VIZ_PATH)  # <-- Use robust path
        with open(HTML_VIZ_PATH, "r", encoding="utf-8") as f:  # <-- Use robust path
            html_content = f.read()
        return html_content
    except Exception as e:
        return f"Error generating visualization: {e}"


# --- Streamlit UI ---

st.title("🕸️ Interactive Tool for Analyzing Polarization & Echo Chambers")
st.write(
    "This tool allows you to upload, analyze, and interact with networks to study community structure and polarization."
)

# Initialize session state
if "G" not in st.session_state:
    st.session_state.G = None
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}
if "original_partition" not in st.session_state:  # <-- Store the "sticky" partition
    st.session_state.original_partition = None

# --- Sidebar for Data Loading and Controls ---

with st.sidebar:
    st.header("1. Load Network Data")

    uploaded_file = st.file_uploader(
        "Upload your edgelist file",
        type=["edges", "txt", "csv"],
        help="Each line should contain two node IDs separated by a space or tab.",
    )

    if st.button("Load and Analyze Network"):
        if uploaded_file:
            st.session_state.G = load_edgelist_graph(uploaded_file)

            # After loading, run the HEAVY analysis
            if st.session_state.G:
                partition, mod, score, bridges = detect_communities_and_analyze(
                    st.session_state.G
                )
                st.session_state.analysis_results = {
                    "partition": partition,  # Save the partition for the viz
                    "modularity": mod,
                    "polarization_score": score,
                    "bridges": bridges,
                }
                # SAVE THE "STICKY" PARTITION
                st.session_state.original_partition = partition
        else:
            st.warning("Please upload a file first.")

    st.divider()

    # --- Section 2: Interactive Edits ---
    st.header("2. Edit Network")
    st.write("Add or remove edges to see how polarization changes.")

    if st.session_state.G:
        col1, col2 = st.columns(2)
        with col1:
            # Convert nodes to string for text_input
            all_nodes = [str(n) for n in st.session_state.G.nodes()]
            node1 = st.text_input("Node 1", placeholder="e.g., 'NodeA' or '1'")
        with col2:
            node2 = st.text_input("Node 2", placeholder="e.g., 'NodeB' or '2'")

        if st.button("Add Edge", use_container_width=True):
            if node1 and node2:
                # Add edge (nodes will be converted to string if they are int)
                st.session_state.G.add_edge(node1, node2)

                # --- NEW LOGIC ---
                # Run the LIGHT analysis using the sticky partition
                mod, score, bridges = recalculate_metrics(
                    st.session_state.G, st.session_state.original_partition
                )
                # Update results, but KEEP the original partition for the viz
                st.session_state.analysis_results.update(
                    {"modularity": mod, "polarization_score": score, "bridges": bridges}
                )
                st.success(f"Added edge ({node1}, {node2})")
            else:
                st.warning("Please enter both node names.")

        if st.button("Remove Edge", use_container_width=True):
            if node1 and node2:
                if st.session_state.G.has_edge(node1, node2):
                    st.session_state.G.remove_edge(node1, node2)

                    # --- NEW LOGIC ---
                    # Run the LIGHT analysis using the sticky partition
                    mod, score, bridges = recalculate_metrics(
                        st.session_state.G, st.session_state.original_partition
                    )
                    # Update results, but KEEP the original partition for the viz
                    st.session_state.analysis_results.update(
                        {
                            "modularity": mod,
                            "polarization_score": score,
                            "bridges": bridges,
                        }
                    )
                    st.success(f"Removed edge ({node1}, {node2})")
                else:
                    st.error(f"Edge ({node1}, {node2}) does not exist.")
            else:
                st.warning("Please enter both node names.")
    else:
        st.info("Load a network to enable editing.")


# --- Main Page for Visualization and Metrics ---

if st.session_state.G:
    results = st.session_state.analysis_results

    st.header("Network Analysis Results")

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Nodes", st.session_state.G.number_of_nodes())
    with col2:
        st.metric("Total Edges", st.session_state.G.number_of_edges())
    with col3:
        st.metric("Modularity", f"{results.get('modularity', 0):.4f}")
    with col4:
        st.metric("Polarization Score", f"{results.get('polarization_score', 0):.4f}")

    st.info(
        f"""
    **Modularity:** Measures the strength of division into communities. (Higher is more divided).
    **Polarization Score (Assortativity):** Measures the tendency of nodes to connect to similar nodes (based on detected community).
    - **+1:** Perfectly "assortative" or polarized (nodes only connect to their own community).
    - **-1:** Perfectly "disassortative" (nodes only connect to *other* communities).
    - **0:** Random connections.
    """
    )

    st.subheader(f"Identified {len(results.get('bridges', []))} Bridge Connections")
    with st.expander("Show/Hide Bridge Edges"):
        # Create a DataFrame for bridges
        bridge_df_data = []
        # Use the original partition for community labels
        if "partition" in results:
            partition = results["partition"]
            for u, v in results.get("bridges", []):
                bridge_df_data.append(
                    {
                        "Node 1": u,
                        "Community 1": partition.get(u, "N/A"),  # Use .get() for safety
                        "Node 2": v,
                        "Community 2": partition.get(v, "N/A"),  # Use .get() for safety
                    }
                )

        # This line will now work because pandas is imported
        st.dataframe(
            pd.DataFrame(
                bridge_df_data,
                columns=["Node 1", "Community 1", "Node 2", "Community 2"],
            )
        )

    st.header("Interactive Network Visualization")
    st.write(
        "Colors represent detected echo chambers (communities). You can drag nodes, zoom, and pan."
    )

    # Generate and display the interactive graph
    if "partition" in results:
        # This will always use the ORIGINAL partition, so colors won't change
        html_content = create_interactive_visualization(
            st.session_state.G, results["partition"]
        )
        components.html(html_content, height=710)

else:
    st.info("Load a network using the sidebar to begin the analysis.")
