
import requests
import csv
import json

import networkx as nx
from networkx.algorithms.community import louvain_communities
import matplotlib.pyplot as plt

import hvplot.networkx as hvnx

import networkx as nx
import holoviews as hv


TEST_DOI = '10.1111/geb.13597' # Meta-Analysis on Land use...
API_KEY = '11852fb061166663a048c15071f4d873'

# 1. Data retrieval

sources = {
    "scopus": f'https://api.elsevier.com/content/article/doi/', # ... ?apiKey={API_KEY}' # + &httpAccept=text%2Fplain'
    "open_alex": f'https://api.openalex.org/works?filter=doi:', # https://github.com/ourresearch/openalex-api-tutorials/blob/main/notebooks/openalex_works/openalex_works.ipynb
    # "web_of_science": f'' 
    # https://github.com/clarivate/wos_api_usecases/blob/main/citations_from_patents/main.py
    # https://libguides.csiro.au/TDM/API/WebofScience
}

api_keys = {
    "scopus": '11852fb061166663a048c15071f4d873', # From Ishita's git
    "open_alex": '', # It's open!
    # "web_of_science": f'' # tbd
}

# Try out different sources if review unavailabe
# for source in sources.values():
#     pass

review_dois = []

# Extract review DOIs from CEEDER csv dump
with open('C:/Users/chris/Documents/ObsidianVault/prof/files//csv/CEEDER_OR_all.csv', "r", encoding="UTF-8") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for row in reader:
        # Extract DOI from inbetween 2 HTML tags
        try:
            review_dois.append(row.get("Link").split(">")[1].split("<")[0])
        except:
            # No DOI
            # Strategy: ignore. Seems to only be a single review
            pass

review_citation_list_mapping = {}
broken_dois = []
empty_references = []

for doi in review_dois:
    response = requests.get(f'https://api.openalex.org/works?filter=doi:{doi}')

    if response.status_code == 200:
        content_type = response.headers['Content-Type']
    else:
        print(f"Error: Failed to retrieve full text. Status code: {response.status_code}")
        
    # Embed citation wenns sein muss, kann auch mit komplettem query string arbeiten...
    # For now work with 

    results = json.loads(response.text)["results"]

    if results == []:
        broken_dois.append(doi)
        continue 

    references = results[0]["referenced_works"]

    if references == []:
        empty_references.append(doi)
        continue

    review_citation_list_mapping[doi] = references

# TODO: To be investigated
# -> Muss ich mir mal genauer anschauen warum die kaputt sind, und ob ich da was machen kann
# ("Link ist auch nicht immer doi...")
print(broken_dois)
print(empty_references)

# 2. Data processing

similarity_edge_list = []

for review_A, references_A in review_citation_list_mapping.items():
    # TODO: Optimize runtime and prevent duplicates by starting nested for loop at index + 1
    # https://stackoverflow.com/questions/14538885/how-to-get-the-index-with-the-key-in-a-dictionary
    for review_B, references_B in review_citation_list_mapping.items():
        if review_A is review_B:
            continue

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

# 3. Visualization

# https://networkx.org/documentation/stable/reference/readwrite/edgelist.html

# hvplot oder so fuer dense graphs

G = nx.Graph()

for n1, n2, w in similarity_edge_list:
    # Show edge only if some similarity exists
    if w > .001:
        G.add_edge(n1, n2, weight=w)

degree_dict = dict(G.degree())
node_sizes = [degree * 2 for node, degree in degree_dict.items()]
edge_width = [G[u][v]['weight'] * 10 for u, v in G.edges()]
communities = louvain_communities(G)
node_color = [i for i, comm in enumerate(communities) for node in comm]

# nx.draw(G, width=edge_width*100)
# nx.draw(G, node_size=node_sizes)
# nx.draw(G, width=edge_width, node_size=node_sizes)
# hvnx.draw(G, with_labels=True)

nx.draw(G, node_color=node_color, width=edge_width, node_size=8, alpha=0.5)

plt.show()

# G = nx.petersen_graph()

# spring = hvnx.draw(G, with_labels=True)
# shell = hvnx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')

# spring + shell

pass


# Random Geometric Graph
# https://hvplot.holoviz.org/user_guide/NetworkX.html#random-geometric-graph

