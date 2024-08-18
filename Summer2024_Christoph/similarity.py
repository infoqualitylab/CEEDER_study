from string import punctuation
from pathlib import Path
from json import loads

from data_retrieval import get_review_meta_data

import nltk
from nltk.corpus import stopwords
import networkx as nx
import matplotlib.pyplot as plt
import hvplot.networkx as hvnx
from networkx.algorithms.community import louvain_communities
from wordcloud import WordCloud


if not Path("./review_with_references.json").is_file():
    get_review_meta_data()

with open("./review_with_references.json") as file:
    review_with_references = loads(file.read())

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

for n1, n2, w in similarity_edge_list:
    # Show edge only if some similarity exists
    if w > 0:
        G.add_edge(n1["question"], n2["question"], weight=w)

degree_dict = dict(G.degree())
node_sizes = [degree * 2 for node, degree in degree_dict.items()]
edge_width = [G[u][v]['weight'] * 10 for u, v in G.edges()]
communities = louvain_communities(G)
communities1 = louvain_communities(G, weight=None)
communities2 = louvain_communities(G, weight="weight")
node_color = [i for i, comm in enumerate(communities) for node in comm]

# Analysis of communitites

nltk.download('stopwords')
community_keywords = []

for community in communities:
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

    print(ranked)

    # Wordcloud per community
    wordcloud = WordCloud(width = 1000, height = 500).generate(unique_string)
    plt.figure(figsize=(15,8))
    plt.imshow(wordcloud)
    plt.axis("off")
    # plt.savefig("your_file_name"+".png", bbox_inches='tight')
    plt.show()
    plt.close()

# Was ist falsch mit der wordcloud: carbon viel oefter als organic (auch andere woerter dazwischen)
# aber beide am groessten dargestellt
# oder "soil organic" ??
# oder "rate?What"

# nx.draw(G, width=edge_width*100)
# nx.draw(G, node_size=node_sizes)
# nx.draw(G, width=edge_width, node_size=node_sizes)
# hvnx.draw(G, with_labels=True)

# nx.draw(G, node_color=node_color, width=edge_width, node_size=8, alpha=0.5)

# plt.show()

# hvnx.draw(G, node_color=node_color, width=edge_width, node_size=8, alpha=0.5)
# plt.show()

# Random Geometric Graph
# https://hvplot.holoviz.org/user_guide/NetworkX.html#random-geometric-graph

