from json import loads

import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import pearsonr, spearmanr


with open("./jaccard_citation_similarities.json") as file:
    jaccard_citation_similarities = loads(file.read()) 

with open("./embedded_similarities.json") as file:
    embedded_similarities = loads(file.read()) 

print([e[1] for e in embedded_similarities][:30])

# List comprehension magic: Combine tuple elements of both list to new list (Append either one of the similarities to a tuple of the other list)
combined = [(q1, q2, jac, emb) for ((q1, q2, jac), (_, _, emb)) in zip(jaccard_citation_similarities, embedded_similarities)]

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
print(f'Spearman Rank Correlation Coefficient: {spearman_corr:.3f}')

# Plot the two curves
plt.figure(figsize=(10, 6))
plt.plot(x, y1_emb, label='Jaccard similarity of citations')
plt.plot(x, y2_emb, label='Embedded similarity of researc questions (sorted)')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Curves Comparison')
plt.legend()
# plt.show()
plt.savefig(f"jaccard_against_embedded_similarity.png", format="PNG")
plt.clf()

# Plot the two curves
plt.figure(figsize=(10, 6))
plt.plot(x, y1_jac, label='Jaccard similarity of citations (sorted)')
plt.plot(x, y2_jac, label='Embedded similarity of researc questions')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Curves Comparison')
plt.legend()
# plt.show()
plt.savefig(f"embedded_against_jaccard.png", format="PNG")
plt.clf()

# # Last 50 elements (most jac similar)
# plt.figure(figsize=(10, 6))
# plt.plot(x[-50:], y1_jac[-50:], label='Jaccard similarity of citations (sorted)')
# plt.plot(x[-50:], y2_jac[-50:], label='Embedded similarity of research questions')
# plt.xlabel('X-axis')
# plt.ylabel('Y-axis')
# plt.title('Curves Comparison')
# plt.legend()
# plt.show()

# # Last 50 elements (most jac similar)
# plt.figure(figsize=(10, 6))
# plt.plot(x[-50:], y1_emb[-50:], label='Jaccard similarity of citations')
# plt.plot(x[-50:], y2_emb[-50:], label='Embedded similarity of research questions (sorted)')
# plt.xlabel('X-axis')
# plt.ylabel('Y-axis')
# plt.title('Curves Comparison')
# plt.legend()
# plt.show()



# compress emb to make it more like a line -> readable



# CORRELLATION 
    # Pearson Correlation: This measures the linear relationship between the two sets of y-values. 
    # If the coefficient is close to 1, it suggests a strong positive linear correlation; 
    # if it's close to -1, it suggests a strong negative correlation. A value near 0 suggests no linear correlation.
    # Spearman Rank Correlation: If you suspect the relationship might be monotonic but not necessarily linear, 
    # Spearman’s rank correlation can capture non-linear correlations.

    # Covariance can also give insight into whether the two variables tend to increase or decrease together. 
    # Positive covariance means they move in the same direction, while negative means they move in opposite directions.
    # Interessant ob iwan null, also nicht korrelliert.
    # + Test the statistical significance of the correlation to ensure it’s not due to random chance, 
    # especially if you’re working with small datasets. You can use a p-value to assess this.
    # ! Covariance is sensitive to scale of the data



# Ich hab eigl 2 korrellationsprobleme?
# und muss vergleichen ob die den selbsen koeffizienten bekommen??

# Similar citations should ask similar research questions

# Unbedingt nochmal doppelchecken, dass die richtigen paare verglichen werden. ROBUST (kann sein dass was vermixt wurde)


# Test for match of pairs in both files (sorting) -> all good...
# for i, _ in enumerate(embedded_similarities):
#     if i % 100 == 0:
#         print(i)
#     if embedded_similarities[i][0] != jaccard_citation_similarities[i][0] or \
#           embedded_similarities[i][1] != jaccard_citation_similarities[i][1]:
#         print("NOT THE SAME PAIR")
