from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from pathlib import Path
from json import dumps, loads

from data_retrieval import get_review_meta_data


# If file of metadata doesn't already exist, create it
if not Path("./reviews_with_meta_data.json").is_file():
    get_review_meta_data() 

with open("./reviews_with_meta_data.json") as file:
    reviews_with_meta_data = loads(file.read()) 

research_questions = [review["question"] for review in reviews_with_meta_data]

model_all = SentenceTransformer('all-MiniLM-L6-v2') # TODO: use ClimateBERT
embeddings_all = model_all.encode(research_questions)
similarity_matrix_all = cosine_similarity(embeddings_all)

similarity_pairs = []
similarity_pairs_all = []

# Reconstruct pairs by going over indices, not the cleanest...
for i1, review in enumerate(similarity_matrix_all):
    # Skip/discard reflexive pair and one of the two summetrical pairs (redundant)
    for i2, sim in enumerate(review[i1 + 1:]): # NOTE: This expects some sorting; if its not there this will lose information !
        similarity_pairs_all.append((research_questions[i1], research_questions[i2 + i1 + 1], sim.item()))

most_similar = sorted(similarity_pairs_all, key=lambda x: -x[2]) 

with open("./embedding_similarity.json", "w") as file:
        file.write(dumps(similarity_pairs_all))
