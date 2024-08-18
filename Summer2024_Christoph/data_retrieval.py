import requests
import json
from csv import DictReader

def get_review_meta_data():
    # Structure: [{ "title": "abc", "doi": 123, "question": "abc?", "references": [ 1, 2, 3 ] }, { ... }]
    reviews = [] # TODO: Rename. Not really a mapping. Outermost data structure is a list...

    # Extract review DOIs from CEEDER csv dump
    with open('./CEEDER_reviews_climate_collection.csv', "r", encoding="UTF-8") as csvfile:
        reader = DictReader(csvfile, delimiter=',', quotechar='"')

        for row in reader:
            try:
                reviews.append({
                    "title": row.get("Title"),
                    "doi": row.get("Link").split(">")[1].split("<")[0], # Extract DOI from inbetween 2 HTML tags
                    "question": row.get("Review Question")
                })
            except:
                # No DOI
                # Strategy: ignore. Seems to only be a single review
                pass

    broken_dois = []
    empty_references = []
    review_with_references = []

    for review in reviews: 
        doi = review["doi"]
        response = requests.get(f'https://api.openalex.org/works?filter=doi:{doi}')

        if response.status_code != 200:
            print(f"Error: Failed to retrieve full text. Status code: {response.status_code}")

        response_text = json.loads(response.text)

        if not response_text.get("results") or response_text["results"] == []:
            broken_dois.append(doi)
            continue 

        references = response_text["results"][0]["referenced_works"]

        if references == []:
            empty_references.append(doi)
            continue

        review_with_references.append({
            "title": review.get("title"),
            "doi": review.get("doi"),
            "question": review.get("question"),
            "references": references
        })

    # TODO: To be investigated
    # -> Muss ich mir mal genauer anschauen warum die kaputt sind, und ob ich da was machen kann
    # ("Link ist auch nicht immer doi...")
    print(broken_dois)
    print(empty_references)

    with open("./review_with_references.json", "w") as file:
        file.write(json.dumps(review_with_references))
