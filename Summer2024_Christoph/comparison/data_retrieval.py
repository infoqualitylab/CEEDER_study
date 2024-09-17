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
    reviews = [] 

    # Extract review DOIs from CEEDER csv dump
    with open('./CEEDER_reviews_climate_collection.csv', "r", encoding="UTF-8") as csvfile:
        reader = DictReader(csvfile, delimiter=',', quotechar='"')

        for row in reader:
            try:
                review = {
                    "title": row.get("Title"),
                    "doi": row.get("Link").split(">")[1].split("<")[0], # Extract DOI from inbetween 2 HTML tags
                    "question": row.get("Review Question")
                }

                # Filter out faulty entries
                if review["doi"] not in [review["doi"] for review in reviews]: 
                    reviews.append(review)

                # CEEDER entry errors (ca. 10)
                # - Couple duplicates
                # - Couple inaccessible/missing DOIs
                # - Same review (DOI) under different titles
                #       - 125636,"A meta-analysis on the impacts of climate change on the yield of European pastures.","Dellar, M.; Topp, C. F. E.; Banos, G.; Wall, E.",2018,"Significant climatic changes are predicted across Europe, some of which are already occurring. These changes will vary dramatically across the continent, with very different conditions expected in the north than in the south. This study assesses the impacts of elevated atmospheric CO2 concentration (+C), increased air temperature (+T) and changes in water availability on pasture yield and makes region-specific predictions of future pasture conditions. The yield measure used is above ground dry weight and is evaluated across pasture and forage species from different plant functional groups. The results of the meta-analysis showed that +C will increase plant growth across Europe, with shrubs experiencing a larger increase than other functional groups, increased temperature (+T) will increase plant growth in Alpine and northern areas but will decrease it in continental Europe. Droughts will cause significant reductions in growth everywhere except for Alpine areas. The results demonstrate what can be expected from future pastures and can help European livestock farming systems to address the challenges presented by climate change.","Sustainable meat and milk production from grasslands. Proceedings of the 27th General Meeting of the European Grassland Federation, Cork, Ireland, 17-21 June 2018","<a href='https://dx.doi.org/10.1016/j.agee.2018.06.029' target='_blank'>10.1016/j.agee.2018.06.029</a>","Climate change, Meta-Analysis, Pastures, Above ground dry weight","What is the effect of elevated atmospheric carbon dioxide concentration, increased air temperature and changes in water availability on pasture yield (above ground dry weight)?",3,2,2,3,3,1,1,1,1,2,2,1,3,1,2,2,"Evidence Review"
                #       - 125772,"A meta-analysis on the effects of climate change on the yield and quality of European pastures","Dellar, M.; Topp, C. F. E.; Banos, G.; Wall, E.",2018,"As has been widely reported, climate change will be felt throughout Europe, though effects are likely to vary dramatically across European regions. While all areas are expected to experience elevated atmospheric CO2 concentrations (up arrow C) and higher temperatures (up arrow T), the north east will get considerably wetter (up arrow W) while the south much drier (down arrow W). It is likely that these changes will have an impact on pastures and consequently on grazing livestock. This study aims to evaluate the expected changes to pasture yield and quality caused by up arrow C, up arrow T, up arrow W and down arrow W across the different European regions and across different plant functional groups (PFGs). Data was collected from 143 studies giving a total of 998 observations. Mixed models were used to estimate expected changes in above ground dry weight (AGDW) and nitrogen (N) concentrations and were implemented using Markov Chain Monte Carlo simulations. The results showed an increase in AGDW under up arrow C, particularly for shrubs (+71.6%), though this is likely to be accompanied by a reduction in N concentrations (-4.8%). up arrow T will increase yields in Alpine and northern areas (+82.6%), though other regions will experience little change or else decreases. up arrow T will also reduce N concentrations, especially for shrubs (-13.6%) and forbs (-18.5%). down arrow W will decrease AGDW for all regions and PFGs, though will increase N concentrations (+11.7%). Under up arrow W there was a 33.8% increase in AGDW. While there is a need for further research to get a more complete picture of future pasture conditions, this analysis provides a general overview of expected changes and thus can help European farmers prepare to adapt their systems to meet the challenges presented by a changing climate.","Agriculture Ecosystems & Environment","<a href='https://dx.doi.org/10.1016/j.agee.2018.06.029' target='_blank'>10.1016/j.agee.2018.06.029</a>",,"What are the eﬀects of climate change on the yield and quality of European pastures?",3,1,3,3,3,1,1,1,1,2,2,1,3,3,2,2,"Evidence Review"

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
    