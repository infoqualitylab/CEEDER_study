import requests
import json
from csv import DictReader


broken_dois = []
empty_references = []
empty_funders = []
reviews_with_meta_data = []


def get_references(doi):
    response = requests.get(f'https://api.openalex.org/works?filter=doi:{doi}')

    if response.status_code != 200:
        print(f"Error: Failed to retrieve full text. Status code: {response.status_code}")

    data = response.json()

    if not data.get("results") or data["results"] == []:
        broken_dois.append(doi)
        return None 

    references = data["results"][0]["referenced_works"]

    if references == []:
        empty_references.append(doi)
        return None

    return references


def get_funders(doi):
    response = requests.get(f'https://api.crossref.org/works/{doi}')

    if response.status_code != 200:
        print(f"Error: Failed to retrieve full text. Status code: {response.status_code}")

    data = response.json().get("message", None)

    if not data:
        broken_dois.append(doi)
        return []

    funders = data.get("funder", None)
        
    if not funders:
        empty_funders.append(doi)
        return []
    
    funders_with_meta_data = []
    
    for funder in funders:
        if not funder.get("DOI", None):
            funders_with_meta_data.append(funder) # Append to list, handle funders w/o meta in visualization
            continue

        response = requests.get(f'https://data.crossref.org/fundingdata/funder/{funder["DOI"]}')
        
        if response.status_code != 200:
            print(f"Error: Failed to retrieve full text. Status code: {response.status_code}")

        data = response.json()

        if not data:
            continue

        funder["region"] = data["region"]
        funder["fundingBodyType"] = data["fundingBodyType"]
        funders_with_meta_data.append(funder)

    return funders_with_meta_data


def get_review_meta_data():
    # Structure:
    # [{ 
    #   "title": "abc", 
    #   "doi": 123, 
    #   "question": "abc?",
    #   "references": [ 1, 2, ... ] }, 
    #   "funders": [ 1, 2, ... ] }, 
    #   { ... }
    # }]
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

    for review in reviews: 
        doi = review["doi"]

        references = get_references(doi) 
        if not references: continue # Skip on broken DOI (unrecognized by OpenAlex) or empty references

        funders = get_funders(doi)
        # Don't skip on broken doi (at crossref API)
        
        reviews_with_meta_data.append({
            "title": review.get("title"),
            "doi": review.get("doi"),
            "question": review.get("question"),
            "references": references,
            "funders": funders
        })

    # TODO: To be investigated
    # -> Muss ich mir mal genauer anschauen warum die kaputt sind, und ob ich da was machen kann
    # ("Link ist auch nicht immer doi...")
    # print(broken_dois)
    # print(empty_references)

    with open("./reviews_with_meta_data.json", "w") as file:
        file.write(json.dumps(reviews_with_meta_data))
    