import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx



# Definisi struktur Node untuk Binary Tree
class Node:
    def __init__(self, value):
        self.data = value
        self.left = None
        self.right = None

# Fungsi untuk membangun Binary Search Tree yang seimbang
def build_balanced_bst(sorted_codes):
    if not sorted_codes:
        return None
    mid_index = len(sorted_codes) // 2
    root = Node(sorted_codes[mid_index])
    root.left = build_balanced_bst(sorted_codes[:mid_index])
    root.right = build_balanced_bst(sorted_codes[mid_index+1:])
    return root

# Fungsi untuk mendapatkan graph dan posisi untuk visualisasi
def get_graph_and_positions(node, graph=None, pos=None, x=0, y=0, layer_width=3.0):
    if graph is None: graph = nx.DiGraph()
    if pos is None: pos = {}
    if node is not None:
        graph.add_node(node.data)
        pos[node.data] = (x, y)
        if node.left:
            graph.add_edge(node.data, node.left.data)
            get_graph_and_positions(node.left, graph, pos, x - layer_width/2, y - 1, layer_width/2)
        if node.right:
            graph.add_edge(node.data, node.right.data)
            get_graph_and_positions(node.right, graph, pos, x + layer_width/2, y - 1, layer_width/2)
    return graph, pos

# Fungsi untuk memvisualisasikan tree dengan jalur yang disorot
def visualize_tree_st(graph, pos, path=None, title=""):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Atur warna default
    node_colors = ['lightblue'] * graph.number_of_nodes()
    edge_colors = ['black'] * graph.number_of_edges()
    
    # Jika ada jalur, sorot node dan edge
    if path:
        path_edges = list(zip(path, path[1:]))
        node_list = list(graph.nodes())
        for i, node_name in enumerate(node_list):
            if node_name in path:
                node_colors[i] = 'lightgreen' # Warna hijau muda untuk node
        
        edge_list = list(graph.edges())
        for i, edge in enumerate(edge_list):
            if edge in path_edges or (edge[1], edge[0]) in path_edges:
                edge_colors[i] = 'black' # Warna hitam untuk edge

    nx.draw(graph, pos, ax=ax, with_labels=True, node_size=2500, node_color=node_colors,
            font_size=10, font_weight='bold', edge_color=edge_colors, arrows=False)
    ax.set_title(title)
    st.pyplot(fig)

# Traversal: In-order (kiri, root, kanan)
def inorder_traversal(node, result_list):
    if node:
        inorder_traversal(node.left, result_list)
        result_list.append(node.data)
        inorder_traversal(node.right, result_list)

# Fungsi pencarian yang mengembalikan jalur
def get_search_path(node, target_code):
    path = []
    current_node = node
    while current_node is not None:
        path.append(current_node.data)
        if target_code == current_node.data:
            return path # Ditemukan
        elif target_code < current_node.data:
            current_node = current_node.left
        else:
            current_node = current_node.right
    return None # Tidak ditemukan

# --- Aplikasi Streamlit ---

def main():
    st.set_page_config(page_title="Visualisasi Tree", page_icon="✈️")

    st.title("✈️ Visualisasi Interaktif Binary Search Tree")
    st.write("Aplikasi ini membangun dan memvisualisasikan Binary Search Tree dari data jadwal penerbangan.")

    st.sidebar.header("⚙️ Kontrol Aplikasi")
    uploaded_file = st.sidebar.file_uploader("📁 Unggah file Jadwal_Penerbangan.csv", type=["csv"])
    
    # --- PENAMBAHAN KODE DI SINI ---
    # Menambahkan tombol untuk mengunduh file CSV contoh
    # Pastikan file 'Jadwal_Penerbangan.csv' ada di direktori yang sama dengan skrip ini
    try:
        with open("Jadwal_Penerbangan.csv", "rb") as file:
            st.sidebar.download_button(
                label="📥 Unduh Contoh CSV",
                data=file,
                file_name="Jadwal_Penerbangan.csv",
                mime="text/csv"
            )
    except FileNotFoundError:
        st.sidebar.error("File 'Jadwal_Penerbangan.csv' tidak ditemukan untuk diunduh.")
    # --- AKHIR PENAMBAHAN KODE ---

    if uploaded_file is not None:
        # Muat data dan bangun tree
        df = pd.read_csv(uploaded_file)
        flight_codes = df['Kode'].tolist()
        unique_sorted_codes = sorted(list(set(flight_codes)))
        
        # Opsi untuk memilih jumlah data
        num_data = st.slider("Pilih jumlah data untuk membangun tree:", 5, 50, 10)
        codes_for_tree = unique_sorted_codes[:num_data]
        
        root = build_balanced_bst(codes_for_tree)
        G, pos = get_graph_and_positions(root)
        
        st.header("1. 🌳 Struktur Awal Tree")
        st.write(f"Berikut adalah {len(codes_for_tree)} kode penerbangan pertama yang digunakan untuk membangun tree:")
        st.write(codes_for_tree)
        if st.button("Tampilkan Tree Awal"):
            visualize_tree_st(G, pos, title="Struktur Awal Binary Tree")
            
        st.header("2. 👣 Traversal In-order")
        if st.button("Jalankan In-order Traversal"):
            inorder_result = []
            inorder_traversal(root, inorder_result)
            st.write("Hasil In-order Traversal (data terurut):")
            st.write(inorder_result)
            visualize_tree_st(G, pos, path=inorder_result, title="Visualisasi Jalur In-order Traversal")

        st.header("3. 🔍 Pencarian Kode Penerbangan")
        search_code = st.text_input("Masukkan kode penerbangan untuk dicari", placeholder="Contoh: GA039")
        if st.button("Cari Kode"):
            if search_code:
                search_path_result = get_search_path(root, search_code)
                if search_path_result:
                    st.success(f"✅ Kode '{search_code}' ditemukan!")
                    st.write("Jalur dari root: " + " -> ".join(search_path_result))
                    visualize_tree_st(G, pos, path=search_path_result, title=f"Jalur Pencarian Menuju '{search_code}'")
                else:
                    st.error(f"❌ Kode '{search_code}' tidak ditemukan.")
            else:
                st.warning("⚠️ Silakan masukkan kode penerbangan untuk dicari.")

    else:
        st.info("ℹ️ Silakan unggah file CSV di sidebar untuk memulai, atau unduh file contoh jika Anda belum memilikinya.")

if __name__ == '__main__':
    main()