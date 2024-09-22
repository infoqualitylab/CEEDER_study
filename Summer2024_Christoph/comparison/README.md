# CEEDER exploration

This repository contains a set of Python scripts to retrieve and explore the a set of evidence reviews from the CEEDER database through computation of similarity metrics and visualizations.

## Installation

```shell
# Create a virtual environment (optional)
python3 -m venv CEEDER_exploration

# Activate virtual environment (optional)
CEEDER_exploration\bin\activate.bat

# Install dependencies
pip install -r requirements.txt
```

## Scripts

### data_retrieval.py

Makes calls to OpenAlex API, Crossref API and Crossref funder registry to retrieve selected metadata of a publication.

Input
- Internet connection (availability of crossref API, crossref funding registry and OpenAlex API)
- CSV file in same directory with the following headers: "Title", "Link" and "Review Question" (Link must be a DOI)

Output
- JSON file of metadata as list of dicts with the following structure
```JSON
{
    "title": "...",
    "doi": "...",
    "question": "...",
    "references": ["...", ...],
    "funders": {"name": "...", "region": "...", "fundingBodyType": "..."}
}
```
For the climate change collection of CEEDER metadata of 337 reviews is retrieved
19 reivews have either a broken DOI, empty references or are a duplicate

### jaccard_similarity.py

Computes the Jaccard similarity of both lists of references for each unique pair in a set of reviews (with metadata). 

Input
- `reviews_with_meta_data.json` of data_retrieval.py; calls module to create file if not exists

Output
- JSON file of unique pairs of reviews (as review question Strings) and their respective Jaccard similarity value of their references

### embedded_similarity.py

Computes the Cosine similarity between both embedded review question for each unique pair in a set of reviews (with metadata). 
The review questions are embedded with SBERT (all-MiniLM-L6-v2).

Input
- `reviews_with_meta_data.json` of data_retrieval.py; calls module to create file if not exists

Output
- JSON file of unique pairs of reviews (as review question Strings) and their respective Cosine similarity value of their embedded review questions

### visualize_communities.py

For each similarity list seperately, detects communitites of reviews and generates word clouds (seperately, and in a grid) and network graphs for in a ./visualizations subfolder.

The communities are detected multiple times for different detection algorithms in Louvain and Leiden and their partition algorithms.
The word clouds are of the words in the review questions Strings in a community, without stop words like 'What' or 'the' and a list of custom words that are part of almost every question like 'impact' or 'effect'.
The graphs nodes are the reviews, the weighed edges connecting them are the similarity values.

Input
- `jaccard_citation_similarities.json` of jaccard_similarity.py
- `embedding_similarity.json` of embedding_similarity.py

Output
- PNG files of visualizations for different community detection configurations and layouts

### compare_similarities.py

Computes covariance, Pearson correlation coefficient and Spearman's rank correlation and plots curves of both similarities sorted each.

Input
- `jaccard_citation_similarities.json` of jaccard_similarity.py
- `embedding_similarity.json` of embedding_similarity.py

Output
- PNG files of two value-distribution plots 

### visualize_funders.py

[Not part of METSTI extended abstract (or future work)]
Creates sunburst chart of funder data of all publications in input JSON. From type of funding body as inner most ring to region to name of funder as outer most ring.

Input
- `reviews_with_meta_data.json` of data_retrieval.py; calls module to create file if not exists

Output
- PNG files of two value-distribution plots 


### CEEDER entry errors
- Duplicates
- Inaccessible/missing DOIs
- Idential reviews (DOIs) with different titles
    - 125636,"A meta-analysis on the impacts of climate change on the yield of European pastures.","<a href='https://dx.doi.org/10.1016/j.agee.2018.06.029' target='_blank'>10.1016/j.agee.2018.06.029</a>"
    - 125772,"A meta-analysis on the effects of climate change on the yield and quality of European pastures","<a href='https://dx.doi.org/10.1016/j.agee.2018.06.029' target='_blank'>10.1016/j.agee.2018.06.029</a>"
