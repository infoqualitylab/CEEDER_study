from sentence_template_extraction import regex_slicing

import rdflib


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
        

