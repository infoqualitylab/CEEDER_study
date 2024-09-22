from csv import DictReader
import re


sentences = []

with open('./CEEDER_reviews_climate_collection.csv', "r", encoding="UTF-8") as csvfile:
    reader = DictReader(csvfile, delimiter=',', quotechar='"')

    for row in reader:
        sentences.append(row.get("Review Question"))


# Quick and dirty regex slicing of research questions:
def regex_slicing():
    pattern = r"What (?:are|is) the (?:effect|effects|effectiveness|impact|impacts) of (?P<X>.*?) (?:on|for) (?P<Y>.*?)(?: (?:in| at) (?P<Z>.*?))?[\?\.]" # extract X, Y, and Z
    # TODO: Handle "How effective"-phrases differently. How should triples look like?
    # Think about classes of triples: effect/impact, effectiveness, ...
    # pattern = r"How effective (?:are|is) (?P<X>.*?) (?:on|for|in|to) (?P<Y>.*?)(?: in (?P<Z>.*?))?[\?\.]" # extract X, Y, and Z

    triplets = []
    no_match = []

    for sentence in sentences:
        match = re.search(pattern, sentence)

        if match:
            X = match.group('X')
            Y = match.group('Y')
            Z = match.group('Z') if 'Z' in match.groupdict() else None
            
            triplets.append((X, Y, Z))
        else:
            no_match.append(sentence)

    print(f"Caputured {float(len(triplets)) / len(sentences)}% of sentences in pre-defined template.")

    return triplets

# What are the impacts of climate change on wheat and rice crop yield, pests, and pathogens?
# << <http://ex.com/climate_change> <http://ex.com/effects> <http://ex.com/_whe> >> <http://ex.com/in> <http://ex.com/and rice crop yield, pests, and pathogens> . 

# "Effect/Impact of X on Y in Z"

# Anomalies the REGEX can handle
# - "X1 or X2" 
# - "X (x1, x2 ...)"
# - effect/impact ON
# - effectiveness FOR
# - missing punctuation

# Anomalies the REGEX cannot handle yet...
# - "from", "under" (mostly alternative to "in Z")
# - typos: eﬀects, effcts, missing 'of'
# - [combined|individual|comparative|direct and indirect|relative] effect => annotate in triple
# - outlier
# - "X1 vs. X2"




# ------ AI / NLP ---------------------------------------------------------------

# TODO: Train custom model on CEEDER for better performance? 
#   Load English tokenizer, POS tagger, and parser
#   nlp = spacy.load("en_core_web_trf")
#    => use scientific model !
#   ClimateBERT

# from collections import defaultdict
# import spacy


# entities = {}

# for sentence in sentences:
#     doc = nlp(sentence)

#     # Skips words like soil or emissions, which is bad! Manual/custom entites are too slow and error prone...
#     # for ent in doc.ents:
#     #     ent = str(ent)

#     # NOTE: Does not get compound words !! (wich are important)
#     for token in doc:
#         if token.pos_ == "NOUN" or token.pos_ == "PROPN":

#             token.dep_

#             if entities.get(str(token)):
#                 entities[str(token)] += 1
#             else:
#                 entities[str(token)] = 1

# pass



# def extract_template(sentence):
#     doc = nlp(sentence)
#     template = []

#     for token in doc:
#         # Replace proper nouns, dates, and objects with placeholders
#         if token.ent_type_ == 'PERSON': # Compress compound words
#             if template[-1] != "<Person>":
#                 template.append("<Person>")
#         elif token.pos_ == 'NOUN':
#             if template[-1] != "<Object>": # Compress compound words
#                 template.append("<Object>")
#         elif token.pos_ == 'ADJ':
#             if template[-1] != "<Adjective>": # Compress compound words
#                 template.append("<Adjective>")
#         elif token.pos_ == 'VERB':
#             template.append(token.lemma_)  # Use verb lemma

#             # Ich brauch hier noch Adjectives !!!

#         else:
#             template.append(token.text)

#     return " ".join(template)

# # Dictionary to store sentence templates
# template_dict = defaultdict(list)

# # Extract and group templates
# for sentence in sentences:
#     template = extract_template(sentence)
#     template_dict[template].append(sentence)

# # Display the templates and their associated sentences
# for template, examples in template_dict.items():
#     print(f"Template: {template}")
#     print("Sentences:")
#     for example in examples:
#         print(f" - {example}")
#     print()





# Sollte ich stop words + What are/is etc. rauslassen? 
#   -> effect of X on Y
# Oder verliere ich da meaning?
# PRON, AUX, DET, PUNC
# Was lass ich drin was nehm ich raus...


# Might need to go in and support model with domain specific info
# common words in CEEDER manually

# I have to be able to identify specific questions in the graph
# don't want to mush together

# Ich glaube mit dem templates komm ich grad nicht weiter
# -> NER of concepts
# -> NLP of relationships + parameterization (to make unique)
# -> finalize: NLP of taxonomy (extra edges in graph) "What is being researched under this topic (parent-term)"

# Incorporate ratings? make certain paths stronger?
