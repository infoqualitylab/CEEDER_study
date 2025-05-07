import subprocess
import json


with open("C:/Users/Chris/OneDrive/Documents/ObsidianVault/prof/files/Python/llm_evaluator/data/questions.txt", mode="r", encoding="UTF-8") as file:
    questions = [i.replace("\n", "") for i in file.readlines()]

responses = {}

for i, question in enumerate(questions):
    print(i)
    print(question)
    command = [
        "py", "-m", "graphrag.query",
        "--root", "C:/Users/Chris/OneDrive/Documents/graphrag-local-ollama/ragtest",
        "--method", "global",
        question
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    
    responses[question] = result.stdout.strip()

with open("./graphRAG_responses.json", "w", encoding="utf-8") as f:
    json.dump(responses, f, indent=4)
