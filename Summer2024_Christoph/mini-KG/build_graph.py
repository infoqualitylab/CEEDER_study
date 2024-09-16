from csv import DictReader
import json

import rdflib

from sentence_template_extraction import regex_slicing


slices = regex_slicing()
triples = []

for slice in slices:
    X, Y, Z = slice[0], slice[1], slice[2]

    # if X oder Y is compound/enumeration
    # create multiple triples

    subject = f"<http://ex.com/{X}>".replace(" ", "_").replace("'", "\'")
    predicate = f"<http://ex.com/effects>".replace(" ", "_").replace("'", "\'")
    object = f"<http://ex.com/{Y}>".replace(" ", "_").replace("'", "\'")

    triple = f"{subject} {predicate} {object}"

    # Context / Location through reification 
    if Z:
         Z = Z.replace(" ", "_").replace("'", "\'")
         triple = f"<< {triple} >> <http://ex.com/in> <http://ex.com/{Z}>"

    triples.append(triple + " . \n")


with open("./mini-KG.ttl", "w", encoding="UTF-8") as file:
    file.writelines(sorted(triples))


# TODO: Split research questions
    # Attachment to originating triple per (nested) reification?
    # Careful! There exist special cases where the and must not be split
    #    elevated_atmospheric_carbon_dioxide_concentration_and_temperature
    # Leave as is for now

# TODO: Skript to append ENVO taxonomy
#   Mark every concept that wasn't able to be mapped -> manual map to closest or leave out






# Enrichment
# with ENVO ontology as taxonomy
# .. quick and dirty w/o rdflib, just text writes; cleaner would be rdflib... get resources or similar

envo_classes = []
no_tax = []
taxonomy_triples = []

with open("C:/Users/chris/Downloads/envo.json", "r", encoding="UTF-8") as file:
        envo_classes = json.load(file)["graphs"][0]["nodes"]

# with open("C:/Users/chris/Downloads/envo-basic.tsv", "r", encoding="UTF-8") as csvfile:
#         reader = DictReader(csvfile, delimiter='\t', quotechar='"')

#         for row in reader:
#             envo_classes.append({
#                 "ID": row.get("ID"),
#                 "name": row.get("label")
#                 # "synonyms": row.get("Review Question") # TODO: Leave out for now... Very valuable, but formatting weird
#             })

for triple in triples:
    resources = triple.replace("<< ", "") \
        .replace(" >>", "") \
        .replace(" . ", "") \
        .replace("\n", "") \
        .replace("<http://ex.com/effects> ", "") \
        .replace("<http://ex.com/in> ", "") \
        .split(" ")
    
    for resource in resources:
        name = resource.replace(">", "").split("/")[-1] # Get to string name

        for cla in envo_classes:
            # if name == cla.get("name"): CSV
            if name == cla.get("lbl"):
                envo_prefix = "http://purl.obolibrary.org/obo/ENVO_"
                # class_id = cla.get("ID") CSV
                class_id = cla.get("id")

                taxonomy_triples.append(
                    f"{resource} rdf:type <{envo_prefix}{class_id}>"
                )
                # TODO: Here I'll need NER or manual work to identify parent concepts that don't simply name match

                break

        # Python for-else :)
        else: 
            no_tax.append(resource)
            


print(f"For {len(taxonomy_triples) / len(triples)}% of resources there a match in ENVO.")

with open("./mini-KG.ttl", "a", encoding="UTF-8") as file:
    file.writelines(sorted(taxonomy_triples))



# RDF lib fragments (for later)

# rdf_graph = rml_converter.convert("C:/Users/chris/Documents/ObsidianVault/prof/files/Turtle/RML_CEEDER_OR_to_RDF.ttl")

# rdf_graph.bind('rr', Namespace('http://www.w3.org/ns/r2rml#'))
# rdf_graph.bind('rml', Namespace('http://semweb.mmlab.be/ns/rml#'))
# rdf_graph.bind('ql', Namespace('http://semweb.mmlab.be/ns/ql#'))
# rdf_graph.bind('xsd', Namespace('http://www.w3.org/2001/XMLSchema#'))
# rdf_graph.bind('dcterms', Namespace('http://purl.org/dc/terms/'))
# rdf_graph.bind('fabio', Namespace('http://purl.org/spar/fabio/'))
# rdf_graph.bind('soa', Namespace('https://semopenalex.org/resource/soa:'))

# rdf_graph.serialize(destination="C:/Users/chris/Documents/ObsidianVault/prof/files/Turtle/mappedCEEDER.ttl")

#         triples = f"<http://example.com/{line[0]}> "
#         triples += "soa:hasKeyword " + f"\"{keyword.lower()}\"^^xsd:string "
            
#         if len(keywords) > 1 and keywords.index(keyword) != len(keywords) - 1: # Skip last
#             triples += ";\n\t"

#         triples += ".\n\n"
        

