import os
import json
from string import punctuation

import nltk
import networkx as nx
import igraph as ig
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import leidenalg as la
from nltk.corpus import stopwords
from mycolorpy import colorlist as mcp
from networkx.algorithms.community import louvain_communities
from wordcloud import WordCloud
from PIL import Image


for file_path in ["jaccard_citation_similarities"]:#, "embedding_similarity"]:
    with open(f"./{file_path}.json", "r") as file:
        similarity_edge_list = json.loads(file.readline())   

    # Where to deposit generated network visualizations as PNGs
    PATH = f"./visualization/{file_path}/"

    if not os.path.exists(PATH):
        os.makedirs(PATH)

    G = nx.Graph()

    for n1, n2, w in similarity_edge_list:
        # Show edge only if some similarity exists
        if w > 0:
            G.add_edge(n1, n2, weight=w)

    # NOTE: Port graph to igraph since Leidenalg is not compatible with networkx==2.4
    G_igraph = ig.Graph.from_networkx(G)

    degree_dict = dict(G.degree())
    node_sizes = [degree * 2 for node, degree in degree_dict.items()]
    edge_width = [G[u][v]['weight'] * 17 for u, v in G.edges()]

    # Node positioning by layout
    layouts = {
        "": lambda _, seed=None: None, # Have something invokable that returns None to use no layout; Drawback: graphs always going to look different, since seed is thrown away
        "spring": nx.spring_layout, # Synonym name according to docs: nx.fruchterman_reingold_layout
        # "shell": nx.shell_layout, # Doesn't work well with graph
        # "spiral": nx.spiral_layout, # Doesn't work well with graph
        # "random": nx.random_layout, # Doesn't work well with graph
        # "circular": nx.circular_layout, # Doesn't work well with graph
        # "spectral": nx.spectral_layout, # Doesn't work well with graph
        # "kamada": nx.kamada_kawai_layout, # Doesn't work well with graph
        # nx.planar_layout, # G needs to be planar
        # nx.rescale_layout, # Don't work on graph
        # nx.rescale_layout_dict, # Don't work on graph
        # nx.bipartite_layout, # Missing nodes
        # nx.multipartite_layout, # Requires subset data
    }
    # igraph equivalent layouts ["circle", "dh", "drl", "fr", "fr3d", "graphopt", "grid", "kk", "kk3d", "large", "mds", "random", "random_3d", "rt", "rt_circular", "sphere"]

    # Community detection by patition algorithm
    leiden_partitions = {
        # NOTE: Why are these not being recognized?
        # la.MutableVertexPartition,
        # la.LinearResolutionParameterVertexPartition,
        "ModularityVertex": la.ModularityVertexPartition,
        "SurpriseVertex": la.SurpriseVertexPartition,
        "SignificanceVertex": la.SignificanceVertexPartition,
        "RBERVertex": la.RBERVertexPartition,
        "RBConfigurationVertex": la.RBConfigurationVertexPartition, 
        "CPMVertex": la.CPMVertexPartition
    }

    for layout_name, layout_func in layouts.items():
        for community_algorithm_name, community_algorithm_func in {"louvain": louvain_communities, "leiden": la.find_partition}.items():
                pos = layout_func(G, seed=42) # With seed to make deterministic
                
                # Lovain always uses modularity partition
                if community_algorithm_func is la.find_partition:
                    for partition_type_name, partition_type_class in leiden_partitions.items():
                        # Per Docstring:  .. warning:: This method is not suitable for weighted graphs. -> leave out weight param
                        if partition_type_class is la.SignificanceVertexPartition:
                            if len(community_algorithm_func(G_igraph, partition_type_class, seed=42)) == G.number_of_nodes():
                                continue # Disregard list where every node is a community

                            communities = community_algorithm_func(G_igraph, partition_type_class, seed=42)
                        else:
                            if len(community_algorithm_func(G_igraph, partition_type_class, seed=42)) == G.number_of_nodes():
                                continue # Disregard list where every node is a community

                            communities = community_algorithm_func(G_igraph, partition_type_class, seed=42)

                        # Convert the partition to a list of dictionaries, readable by networkx
                        # TODO: Comfirm that this really does what I expect it to
                        communities = [set({G_igraph.vs[node_id]["_nx_name"] for node_id, com_id in enumerate(communities.membership) if com_id == community_id}) for community_id, _ in enumerate(communities)]
                        node_color = [i for i, com in enumerate(communities) for node in com]
                        print(sorted([len(c) for c in communities]))

                        nx.draw(G, pos=pos, node_color=node_color, cmap='hsv', width=edge_width, node_size=8, alpha=0.5)
                        plt.savefig(f"{PATH}graph_{layout_name}_{community_algorithm_name}_{partition_type_name}.png", format="PNG")
                        plt.clf()
                else:
                    if len(community_algorithm_func(G, weight="weight", seed=42)) == G.number_of_nodes():
                        continue # Disregard list where every node is a community

                    communities = community_algorithm_func(G, weight="weight", seed=42)
                    node_color = [i for i, com in enumerate(communities) for node in com]
                    print(sorted([len(c) for c in communities]))

                    nx.draw(G, pos=pos, node_color=node_color, cmap='hsv', width=edge_width, node_size=8, alpha=0.5)
                    plt.savefig(f"{PATH}graph_{layout_name}_{community_algorithm_name}.png", format="PNG") 
                    plt.clf()  


    # VISUALIZATION OPTIONS
        # nx.draw(G, pos, with_labels=True)
        # ig.plot(G, layout=layout, vertex_label=list(range(g.vcount())))

        # Nodes
        # nx.draw(G, node_size=500, node_color='skyblue', node_shape='o')
        # ig.plot(G, vertex_size=20, vertex_color="skyblue", vertex_shape="circle")

        # Edges
        # nx.draw(G, edge_color='gray', width=2, style='dashed')
        # ig.plot(G, edge_width=2, edge_color="gray", edge_curved=True)

        # Labels
        # nx.draw_networkx_labels(G, pos, labels=nx.get_node_attributes(G, 'label'))
        # ig.plot(G, vertex_label=g.vs["name"], edge_label=g.es["weight"])

        # Subgraph / community visualization
        # communities = nx.algorithms.community.greedy_modularity_communities(G)
        # colors = ['red', 'blue', 'green']
        # for community in communities:
        #     nx.draw(G.subgraph(community), node_color=colors.pop())
        # from igraph import ClusterColoringPalette
        # clusters = G.community_multilevel()
        # palette = ClusterColoringPalette(len(clusters))
        # G.vs["color"] = [palette[cluster] for cluster in clusters.membership]
        # ig.plot(G)

    # Random Geometric Graph
    # https://hvplot.holoviz.org/user_guide/NetworkX.html#random-geometric-graph


    # Analysis of communitites

    nltk.download('stopwords')
    community_keywords = []
    wordcloud_paths = []

    hex_colors = mcp.gen_color(cmap="hsv",n=len(communities))

    # NOTE: Manual map of colors for most similar embedded communitites (4) to citation communities (8) (for presentation slides)
    # hex_colors = ["#fcf500", "#3bfff8", "#ff0000", "#ed00ff"]

    for i, community in enumerate(communities):
        unique_string = ""

        # NOTE: Only works since node label is defined as question above !
        for question in community:
            question = question.lower()
            
            for char in punctuation:
                question = question.replace(char, '')

            cachedStopWords = stopwords.words("english")

            # TODO: How can I find out these "uninteresting" words 
            for word in ["impact", "exposure", "effect", "effects", "effective", "effectiveness"]:
                cachedStopWords.append(word)
            
            unique_string += ' '.join([word for word in question.split() if word not in cachedStopWords]) + ' '

        d = {}

        for keyword in unique_string.split(" "):
            d[keyword] = d.get(keyword, 0) + 1

        ranked = sorted(d.items(), key=lambda x: x[1], reverse=True)

        # Hex to cmap
        rgb = colors.to_rgb(hex_colors[i])
        
        # Create a colormap with the specified color as the starting and ending color
        cmap = colors.LinearSegmentedColormap.from_list(
            name='custom_cmap',
            colors=[rgb, rgb],
            N=256
        )
        
        # Wordcloud per community
        wordcloud = WordCloud(width = 1000, height = 500, background_color="white", colormap=cmap).generate(unique_string)
        
        plt.figure(figsize=(15,8))
        plt.imshow(wordcloud)
        plt.axis("off")
        wordcloud_path = PATH + "wordcloud_" + str(i) + "_" + str(len(community)) +".png"
        plt.savefig(wordcloud_path, bbox_inches='tight')
        wordcloud_paths.append(wordcloud_path)

    img_size = (200, 200)  # Adjust as needed

    # NOTE: Manual grid size specification, depending on how many communities were computed (and which partition algorithm was chosen)
    if file_path == "jaccard_citation_similarities":
        X = 2  # Number of images per row/column
        Y = 4  # Number of images per row/column
    else:
        X = 2  # Number of images per row/column
        Y = 4  # Number of images per row/column

    images = []

    # Collect images of word clouds
    for path in wordcloud_paths:
        img = Image.open(path)
        img = img.resize(img_size)
        images.append(np.array(img))

    # Create grid
    grid = np.zeros((X * img_size[0], Y * img_size[1], 4), dtype=np.uint8)

    # Place images of word clouds in grid
    for i in range(X):
        for j in range(Y):
            if i*Y+j < len(images):
                grid[i*img_size[0]:(i+1)*img_size[0], j*img_size[1]:(j+1)*img_size[1], :] = images[i*Y+j]

    # Save grid to file
    grid_img = Image.fromarray(grid)
    grid_img.save(f"{PATH}/wordcloud_grid.png")
