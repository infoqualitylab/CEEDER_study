from pathlib import Path
from json import dumps, loads

from data_retrieval import get_review_meta_data


# If file of metadata doesn't already exist, create it
if not Path("./reviews_with_meta_data.json").is_file():
    get_review_meta_data() 

with open("./reviews_with_meta_data.json") as file:
    reviews_with_meta_data = loads(file.read()) 

# Citation ranking of studies
ranking = {}

for review in reviews_with_meta_data:
    for study in review["references"]:
        if ranking.get(study):
            ranking[study] += 1
        else:
            ranking[study] = 1

# Top 5 most influental/cited studies
print(list(dict(sorted(ranking.items(), key=lambda item: -item[1])).items())[:5])

similarity_edge_list = []

for i, review_A in enumerate(reviews_with_meta_data):
    # [i+1:] Optimization: Skip reflection and symmetry (self and items that have already seen each other)
    for review_B in reviews_with_meta_data[i+1:]:
        references_A = review_A["references"]
        references_B = review_B["references"]
        
        # Jaccard similarity formula
        intersection = len(list(set(references_A).intersection(references_B)))
        union = (len(set(references_A)) + len(set(references_B))) - intersection
        similarity = float(intersection) / union
        
        similarity_edge_list.append(
            (
                review_A, # Node A
                review_B, # Node B
                similarity # Weight
            )
        )

similarity_edge_list = sorted(similarity_edge_list, key=lambda x: x[0]["doi"]) # Sort by DOI to make sure input for graph drawing always looks the same (deterministic)

# Write to file of each tuple in the similarity edge list the two review questions and similarity value
with open("./jaccard_citation_similarities.json", "w") as file:
    file.write(dumps([(entry[0]["question"], entry[1]["question"], entry[2]) for entry in similarity_edge_list]))

print(f"Mean similarity over greater 0: {sum(edge[2] for edge in similarity_edge_list if edge[2] > 0) / len([edge for edge in similarity_edge_list if edge[2] > 0])}")
print(f"Mean similarity over all: {sum(edge[2] for edge in similarity_edge_list) / len([edge for edge in similarity_edge_list])}")
