from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# research_questions = [
#     "How does climate change impact biodiversity?", 
#     "How does climate change impact fauna?", 
#     "How is fauna impacted by the change in climate?", 
#     "What is the weather going to be like tomorrow?"
# ]
#
# [1.0000002  0.8714391  0.832276   0.25206238]
# [0.8714391  1.0000002  0.96776915 0.27055174]
# [0.832276   0.96776915 0.9999999  0.27489406]
# [0.25206238 0.27055174 0.27489406 1.        ]
# -> Looks plausible! Every question compared to itself is effectively valued 1 (Matrix diagonal)
#    2,3 which ar paraphrased also close to 1 
#    1-3 only vary in a single word also close to 1
#    4 smallest similarity since it's unrelated
#   => Worth investigating more complex (nuanced) questions
#    

from pathlib import Path
from json import loads

from data_retrieval import get_review_meta_data


if not Path("./reviews_with_meta_data.json").is_file():
    get_review_meta_data() 

with open("./reviews_with_meta_data.json") as file:
    reviews_with_meta_data = loads(file.read()) # 340 reviews; 16 with either broken DOIs or empty references


research_questions = [review["question"] for review in reviews_with_meta_data]

model_all = SentenceTransformer('all-MiniLM-L6-v2')
embeddings_all = model_all.encode(research_questions)
similarity_matrix_all = cosine_similarity(embeddings_all)


similarity_pairs = []

# Reconstruct pairs by going over indices, not the cleanest...
for i1, review in enumerate(similarity_matrix_all):
    for i2, sim in enumerate(review):
        # Prevent identicals
        if i1 != i2:
            similarity_pairs.append((research_questions[i1], research_questions[i2], sim))

most_similar = sorted(similarity_pairs, key=lambda x: -x[2])
most_similar = most_similar[::2] # Discard every other pair as redundant inverse
print()

# (
#     'What is the impact of nitrogen addition on soil methane in uplands and wetlands ?', 
#     'What is the impact of nitrogen addition on methane uptake in upland soils?', 
#     0.9374442
# )
