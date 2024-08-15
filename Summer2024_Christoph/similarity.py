import requests
import csv
import json

import networkx as nx
import matplotlib.pyplot as plt
import hvplot.networkx as hvnx
from networkx.algorithms.community import louvain_communities
from wordcloud import WordCloud


# 1. Data retrieval

sources = {
    "scopus": f'https://api.elsevier.com/content/article/doi/', # ... ?apiKey={API_KEY}' # + &httpAccept=text%2Fplain'
    "open_alex": f'https://api.openalex.org/works?filter=doi:', # https://github.com/ourresearch/openalex-api-tutorials/blob/main/notebooks/openalex_works/openalex_works.ipynb
    # "web_of_science": f'' 
    # https://github.com/clarivate/wos_api_usecases/blob/main/citations_from_patents/main.py
    # https://libguides.csiro.au/TDM/API/WebofScience
}

api_keys = {
    "scopus": '...', # From Ishita's git
    "open_alex": '', # It's open!
    # "web_of_science": f'' # tbd
}

# Try out different sources if review unavailabe
# for source in sources.values():
#     pass

# Structure: [{ "title": "abc", "doi": 123, "question": "abc?", "references": [ 1, 2, 3 ] }, { ... }]
review_meta_mappings = []

# Extract review DOIs from CEEDER csv dump
with open('./CEEDER_reviews_climate_collection', "r", encoding="UTF-8") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for row in reader:
        try:
            review_meta_mappings.append({
                "question": row.get("Title"),
                "doi": row.get("Link").split(">")[1].split("<")[0], # Extract DOI from inbetween 2 HTML tags
                "question": row.get("Review Question")
            })
        except:
            # No DOI
            # Strategy: ignore. Seems to only be a single review
            pass

broken_dois = []
empty_references = []

# TODO: Do this more elegantly? pop() has a lot of ugly consequences, that need to be worked around...
for review_copy in review_meta_mappings.copy(): # Iterate copy, because of pop() operation
    i = review_meta_mappings.index(review_copy) # Make i dynamic, because of changing length of list through pop() operation
    review = review_meta_mappings[i]
    doi = review["doi"]
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
        review_meta_mappings.pop(i) # Remove review with faulty meta
        continue 

    references = results[0]["referenced_works"]

    if references == []:
        empty_references.append(doi)
        review_meta_mappings.pop(i) # Remove review with faulty meta
        continue

    review["references"] = references

# TODO: To be investigated
# -> Muss ich mir mal genauer anschauen warum die kaputt sind, und ob ich da was machen kann
# ("Link ist auch nicht immer doi...")
print(broken_dois)
print(empty_references)

# 2. Data processing

similarity_edge_list = []

for i, review_A in enumerate(review_meta_mappings):
    # Optimization: Skip reflection and symmetry (self and items that have already seen each other)
    for review_B in review_meta_mappings[i+1:]:
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

# 3. Visualization

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

community_keywords = []

for community in communities:
    unique_string = ""

    # NOTE: Only works since node label is defined as question above !
    for question in community:
        # question = question.removeprefix("What is the effect of")
        # question = question.removeprefix("What are the effects of")
        # question = question.removeprefix("How effective is")
        # question = question.removeprefix("How effective are")

        import nltk
        from nltk.corpus import stopwords

        nltk.download('stopwords')
        cachedStopWords = stopwords.words("english")
        unique_string += ' '.join([word for word in question.split() if word not in cachedStopWords])

        # unique_string += question \
        #     .replace("?", "") \
        #     .replace(",", "") \
        #     .replace("(", "") \
        #     .replace(")", "") \
        #     .replace(";", "") \
        #     .replace(":", "") + " "


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



nx.draw(G, width=edge_width*100)
# nx.draw(G, node_size=node_sizes)
# nx.draw(G, width=edge_width, node_size=node_sizes)
# hvnx.draw(G, with_labels=True)

# nx.draw(G, node_color=node_color, width=edge_width, node_size=8, alpha=0.5)

# plt.show()

# hvnx.draw(G, node_color=node_color, width=edge_width, node_size=8, alpha=0.5)
plt.show()

pass


# Random Geometric Graph
# https://hvplot.holoviz.org/user_guide/NetworkX.html#random-geometric-graph

