from string import punctuation
from pathlib import Path
from json import loads

from data_retrieval import get_review_meta_data

import nltk
from nltk.corpus import stopwords
import networkx as nx
import igraph as ig
import matplotlib.pyplot as plt
# import hvplot.networkx as hvnx
from networkx.algorithms.community import louvain_communities
from wordcloud import WordCloud
import numpy as np
from PIL import Image
import leidenalg as la


if not Path("./review_with_references.json").is_file():
    get_review_meta_data() 

with open("./review_with_references.json") as file:
    review_with_references = loads(file.read()) # 340 reviews; 16 with either broken DOIs or empty references

similarity_edge_list = []

for i, review_A in enumerate(review_with_references):
    # Optimization: Skip reflection and symmetry (self and items that have already seen each other)
    for review_B in review_with_references[i+1:]:
        references_A = review_A["references"]
        references_B = review_B["references"]
        
        # Jaccard-Formula
        intersection = len(list(set(references_A).intersection(references_B)))
        union = (len(set(references_A)) + len(set(references_B))) - intersection
        
        # Compute similarity metric
        similarity = float(intersection) / union

        similarity_edge_list.append(
            (
                review_A, # Node A
                review_B, # Node B
                similarity # Weight
            )
        )

print(f"Mean similarity over greater 0: {sum(edge[2] for edge in similarity_edge_list if edge[2] > 0) / len([edge for edge in similarity_edge_list if edge[2] > 0])}")
print(f"Mean similarity over all: {sum(edge[2] for edge in similarity_edge_list) / len([edge for edge in similarity_edge_list])}")

G = nx.Graph()
similarity_edge_list = sorted(similarity_edge_list, key=lambda x: x[0]["doi"]) # sort by doi to make sure input for graph drawing always looks the same (deterministic)

for n1, n2, w in similarity_edge_list:
    # Show edge only if some similarity exists
    if w > 0:
        G.add_edge(n1["question"], n2["question"], weight=w)

# NOTE: Port graph to igraph since Leidenalg is not compatible with networkx==2.4
G_igraph = ig.Graph.from_networkx(G)

degree_dict = dict(G.degree())
node_sizes = [degree * 2 for node, degree in degree_dict.items()]
edge_width = [G[u][v]['weight'] * 17 for u, v in G.edges()]

# Node positions
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
    # functions = [function1, function2, function3]
    # for func in functions:
    #     func()
    # 'igraph': ["circle", "dh", "drl", "fr", "fr3d", "graphopt", "grid", "kk", "kk3d", "large", "mds", "random", "random_3d", "rt", "rt_circular", "sphere", ],
    # pos = nx.fruchterman_reingold_layout(G)
    # nx.draw(G, pos=pos)
}

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

PATH = "C:/Users/chris/Documents/ObsidianVault/prof/files/PNG/graphs/"


for layout_name, layout_func in layouts.items():
    for community_algorithm_name, community_algorithm_func in {"louvain": louvain_communities, "leiden": la.find_partition}.items():
            pos = layout_func(G, seed=42) # With seed to make deterministic
            
            # Lovain always uses modularity partition
            if community_algorithm_func is la.find_partition:
                for partition_type_name, partition_type_class in leiden_partitions.items():
                    # Per Docstring:  .. warning:: This method is not suitable for weighted graphs.
                    if partition_type_class is la.SignificanceVertexPartition:
                        communities = community_algorithm_func(G_igraph, partition_type_class)
                    else:
                        communities = community_algorithm_func(G_igraph, partition_type_class, weights="weight")

                    # Convert the partition to a list of dictionaries, readable by networkx
                    # TODO: Comfirm that this really does what I expect it to
                    communities = [set({G_igraph.vs[node_id]["_nx_name"] for node_id, com_id in enumerate(communities.membership) if com_id == community_id}) for community_id, _ in enumerate(communities)]
                    node_color = [i for i, com in enumerate(communities) for node in com]

                    nx.draw(G, pos=pos, node_color=node_color, width=edge_width, node_size=8, alpha=0.5)
                    plt.savefig(f"{PATH}graph_{layout_name}_{community_algorithm_name}_{partition_type_name}.png", format="PNG")
                    plt.clf()
            else:
                communities = community_algorithm_func(G, weight="weight")
                node_color = [i for i, com in enumerate(communities) for node in com]

                nx.draw(G, pos=pos, node_color=node_color, width=edge_width, node_size=8, alpha=0.5)
                plt.savefig(f"{PATH}graph_{layout_name}_{community_algorithm_name}.png", format="PNG") # bbox_inches='tight'
                plt.clf()
                # hvnx.draw(G, node_color=node_color, width=edge_width, node_size=8, alpha=0.5, with_labels=True)

# igraph
# # colors = [plt.cm.rainbow(mem / float(max(communities_with_weighting.membership))) for mem in communities_with_weighting.membership]
# G.vs['color'] = colors
# layout = G.layout("dh")
# ig.plot(G, layout=layout, edge_width=edge_width, vertex_size=8, target='graph.png')
# Save
# ig.plot(G, f"{path}graph{}{}.png")
            

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

# Interactive
# hvplot
# cytoscape?

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

# Save
# plt.savefig("graph.png", format="PNG")
# ig.plot(G, "graph.png")
# C:\Users\chris\Documents\ObsidianVault\prof\files\PNG\graphs

# Random Geometric Graph
# https://hvplot.holoviz.org/user_guide/NetworkX.html#random-geometric-graph


# Analysis of communitites

nltk.download('stopwords')
community_keywords = []
wordcloud_paths = []

for i, community in enumerate(communities):
    unique_string = ""

    # NOTE: Only works since node label is defined as question above !
    for question in community:
        question = question.lower()
        
        for char in punctuation:
            question = question.replace(char, '')
    
        # TODO: Further word simplification
        # - singular and plural
        # - word stem verbs

        cachedStopWords = stopwords.words("english")

        # TODO: How can I find out these "uninteresting" words 
        for word in ["impact", "exposure", "effect", "effects", "effective", "effectiveness"]:
            cachedStopWords.append(word)
        
        unique_string += ' '.join([word for word in question.split() if word not in cachedStopWords]) + ' '

    d = {}
    for keyword in unique_string.split(" "):
        d[keyword] = d.get(keyword, 0) + 1

    ranked = sorted(d.items(), key=lambda x: x[1], reverse=True)

    # print(ranked)

    # Wordcloud per community
    wordcloud = WordCloud(width = 1000, height = 500).generate(unique_string)
    plt.figure(figsize=(15,8))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig("wordcloud_" + str(i) +".png", bbox_inches='tight')
    wordcloud_paths.append("wordcloud_" + str(i) +".png")
    # plt.show()
    # plt.close()

img_size = (200, 200)  # Adjust as needed
X = 2  # Number of images per row/column
Y = 4  # Number of images per row/column

images = []

for path in wordcloud_paths:
    img = Image.open(path)
    img = img.resize(img_size)
    images.append(np.array(img))

# Create grid
grid = np.zeros((X * img_size[0], Y * img_size[1], 4), dtype=np.uint8)

for i in range(X):
    for j in range(Y):
          grid[i*img_size[0]:(i+1)*img_size[0], j*img_size[1]:(j+1)*img_size[1], :] = images[i*Y+j]

grid_img = Image.fromarray(grid)
grid_img.save("./wordcloud_grid.png")


# TODO
# - set seed
# - consesus clustering
