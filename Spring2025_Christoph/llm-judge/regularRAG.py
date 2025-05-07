from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss  # Alternative: chromadb
import ollama

import os
import json
import numpy as np


responses = {}

with open("C:/Users/Chris/OneDrive/Documents/ObsidianVault/prof/files/Python/llm_evaluator/data/questions.txt", mode="r", encoding="UTF-8") as file:
    questions = [i.replace("\n", "") for i in file.readlines()]

# 1. Chunk documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_chunks = []
path_to_abstracts = "C:/Users/Chris/OneDrive/Documents/ObsidianVault/prof/files/Python/llm_evaluator/input_abstracts/"

for path in os.listdir(path_to_abstracts):
    with open(path_to_abstracts + path, "r", encoding="utf-8") as file:
        text = file.read()
    chunks = text_splitter.split_text(text)
    all_chunks.extend(chunks)

# 2. Embed chunks using ollama
embeddings = []

for chunk in all_chunks:
    embedding = ollama.embeddings(model='nomic-embed-text', prompt=chunk)
    embeddings.append(np.array(embedding['embedding']))

# Convert list of embeddings into a NumPy array
embeddings = np.array(embeddings)

# 3. Store in vector index (FAISS)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

for i, question in enumerate(questions):
    print(i)
    print(question)
    # 4. Answer question with top-k retrieval
    k = 5

    # Embed query using ollama
    embedded_query = ollama.embeddings(model='nomic-embed-text', prompt=question)
    query_vec = np.array(embedded_query['embedding']).reshape(1, -1)

    # Retrieve top-k most similar chunks
    D, I = index.search(query_vec, k)

    # Concatenate the top-k chunks and send to LLM for the final answer
    context_data = "id|text\n\n" + "\n\n".join(f"{i}|{all_chunks[i]}" for i in I[0])

    # https://github.com/microsoft/graphrag/blob/56a865bff0cac9fbbc24f343cf52d0a1850abba6/graphrag/cli/query.py
    response_type = "Free form text describing the response type and format, can be anything, e.g. Multiple Paragraphs, Single Paragraph, Single Sentence, List of 3-7 Points, Single Page, Multi-Page Report. Default: Multiple Paragraphs"

    graphRAG_inspired_system_prompt = f"""
        ---Role---

        You are a helpful assistant responding to questions about data in the reports provided.

        ---Goal---

        Generate a response of the target length and format that responds to the user’s question, summarize all relevant information in the input reports appropriate for the response length and format, and incorporate any relevant general knowledge.

        If you don't know the answer, just say so. Do not make anything up.

        The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".

        Points supported by data should list the relevant reports as references as follows:

        "This is an example sentence supported by data references [Data: Reports (report ids)]"

        Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.

        For example:

        "Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (2, 7, 64, 46, 34, +more)]. He is also CEO of company X [Data: Reports (1, 3)]"

        where 1, 2, 3, 7, 34, 46, and 64 represent the id (not the index) of the relevant data report in the provided reports.

        Do not include information where the supporting evidence for it is not provided.


        ---Target response length and format--

        {response_type}

        ---Reports--

        {context_data}
        """
        # At the beginning of your response, generate an integer score between 0-100 that indicates how **helpful** is this response in answering the user’s question. Return the score in this format: <ANSWER_HELPFULNESS> score.value </ANSWER_HELPFULNESS>.


    # 2 prompts, one system to set rules then user query
    # https://github.com/microsoft/graphrag/blob/ddc6541ab6e0483d4f23de14579034fa1c4056d4/graphrag/query/structured_search/global_search/search.py
    messages = [
        {
            'role': 'system',
            'content': graphRAG_inspired_system_prompt,
        },
        {
            'role': 'user',
            'content': question,
        },
    ]

    # Get response from the model
    response = ollama.chat(model="mistral-nemo", messages=messages)

    # Return the final answer
    responses[question] = response["message"]["content"]


with open("./regularRAG_responses.json", "w", encoding="utf-8") as f:
    json.dump(responses, f, indent=4)


# --- SAVE TO FILE ---
# with open('./data/regular_RAG_answers.json', "x", encoding="utf-8") as f:
#     json.dump(results, f, indent=2)




# service_context = ServiceContext.from_defaults(
#     llm = Ollama(model="mistral-nemo"),
#     embed_model = SentenceTransformer("nomic-ai/nomic-embed-text-v1")
# )

# --- LOAD DOCUMENTS ---
# documents = SimpleDirectoryReader("C:/Users/Chris/OneDrive/Documents/ObsidianVault/prof/files/Python/llm_evaluator/input_abstracts/").load_data()
# index = VectorStoreIndex.from_documents(documents, service_context=service_context)
# query_engine = index.as_query_engine(similarity_top_k=5)






# Note: Extracted with Cursor App (may be unreliable)


# context_data = {
#     # Community Reports DataFrame
#     "reports": pd.DataFrame({
#         "id": ["1", "2", "3"],
#         "title": ["Report A", "Report B", "Report C"],
#         "summary": ["Summary of A", "Summary of B", "Summary of C"],
#         "rank": [1, 2, 3],
#         "occurrence": [0.5, 0.3, 0.2]
#     }),
    
#     # Entities DataFrame
#     "entities": pd.DataFrame({
#         "id": ["1", "2", "3"],
#         "entity": ["Entity A", "Entity B", "Entity C"],
#         "rank": [1, 2, 3],
#         "number_of_relationships": [5, 3, 2]
#     }),
    
#     # Relationships DataFrame
#     "relationships": pd.DataFrame({
#         "id": ["1", "2", "3"],
#         "source": ["Entity A", "Entity B", "Entity C"],
#         "target": ["Entity B", "Entity C", "Entity A"],
#         "description": ["relates to", "connected to", "associated with"],
#         "weight": [0.8, 0.6, 0.4]
#     }),
    
#     # Covariates DataFrame (if any)
#     "covariates": pd.DataFrame({
#         "id": ["1", "2", "3"],
#         "entity": ["Entity A", "Entity B", "Entity C"],
#         "value": ["value1", "value2", "value3"]
#     })
# }


# Community Reports (from build_community_context):
#  - Contains information about community reports
#  - Columns include: id, title, summary/content, rank, occurrence weight
#  - Used for global context understanding
#  - Entities (from build_entity_context):
#  - Contains information about entities
#  - Columns include: id, entity name, rank, number of relationships
#  - Represents the main objects in the system
# Relationships (from build_relationship_context):
#  - Contains information about relationships between entities
#  - Columns include: id, source, target, description, weight
#  - Shows how entities are connected
# Covariates (from build_covariates_context):
#  - Contains additional attributes for entities
#  - Columns include: id, entity, and various attribute columns
#  - Provides supplementary information

# -----Reports-----
# id|title|summary|rank|occurrence
# 1|Report Title 1|Summary text 1|0.8|0.5
# 2|Report Title 2|Summary text 2|0.6|0.3



