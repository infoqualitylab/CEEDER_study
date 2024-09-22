from json import loads

import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import pearsonr, spearmanr


with open("./jaccard_citation_similarities.json") as file:
    jaccard_citation_similarities = loads(file.read()) 

with open("./embedding_similarities.json") as file:
    embedding_similarities = loads(file.read()) 

print([e[1] for e in embedding_similarities][:30])

# List comprehension magic: Combine tuple elements of both list to new list (Append either one of the similarities to a tuple of the other list)
combined = [(q1, q2, jac, emb) for ((q1, q2, jac), (_, _, emb)) in zip(jaccard_citation_similarities, embedding_similarities)]

combined_sort_emb = sorted(combined, key=lambda x: x[2])
combined_sort_jac = sorted(combined, key=lambda x: x[3])

x = np.array([i for i, _ in enumerate(combined_sort_emb)])
y1_emb = np.array([tup[2] for tup in combined_sort_emb])
y1_jac = np.array([tup[2] for tup in combined_sort_jac])
y2_emb = np.array([tup[3] for tup in combined_sort_emb])
y2_jac = np.array([tup[3] for tup in combined_sort_jac])

# Should be the same for both sorts !
cov_matrix = np.cov(y1_emb, y2_emb); covariance = cov_matrix[0, 1]
pearson_corr, _ = pearsonr(y1_emb, y2_emb)
spearman_corr, _ = spearmanr(y1_emb, y2_emb) # capturing non-linear correlation

print(f'Covariance: {covariance:.3f}')
print(f'Pearson Correlation Coefficient: {pearson_corr:.3f}')
print(f'Spearman\'s Rank Correlation: {spearman_corr:.3f}')

# Plot the two curves
plt.figure(figsize=(10, 6))
plt.plot(x, y1_emb, label='Jaccard similarity of citations')
plt.plot(x, y2_emb, label='Embedding similarity of research questions (sorted)')
plt.xlabel('Review-pair')
plt.ylabel('Similarity')
plt.title('Curves Comparison')
plt.legend()
# plt.show()
plt.savefig(f"jaccard_against_embedding_similarity.png", format="PNG")
plt.clf()

# Plot the two curves
plt.figure(figsize=(10, 6))
plt.plot(x, y1_jac, label='Jaccard similarity of citations (sorted)')
plt.plot(x, y2_jac, label='Embedding similarity of research questions')
plt.xlabel('Review-pair')
plt.ylabel('Similarity')
plt.title('Curves Comparison')
plt.legend()
# plt.show()
plt.savefig(f"embedding_against_jaccard.png", format="PNG")
plt.clf()
