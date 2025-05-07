import json
import random
import os

import ollama
from datetime import datetime


CRITERIA = {
  "comprehensiveness": "How much detail does the answer provide to cover all the aspects and details of the question? A comprehensive answer should be thorough and complete, without being redundant or irrelevant. For example, if the question is 'What are the benefits and drawbacks of nuclear energy?', a comprehensive answer would provide both the positive and negative aspects of nuclear energy, such as its efficiency, environmental impact, safety, cost, etc. A comprehensive answer should not leave out any important points or provide irrelevant information. For example, an incomplete answer would only provide the benefits of nuclear energy without describing the drawbacks, or a redundant answer would repeat the same information multiple times.", 
  "diversity": "How varied and rich is the answer in providing different perspectives and insights on the question? A diverse answer should be multi-faceted and multi-dimensional, offering different viewpoints and angles on the question. For example, if the question is 'What are the causes and effects of climate change?', a diverse answer would provide different causes and effects of climate change, such as greenhouse gas emissions, deforestation, natural disasters, biodiversity loss, etc. A diverse answer should also provide different sources and evidence to support the answer. For example, a single-source answer would only cite one source or evidence, or a biased answer would only provide one perspective or opinion.", 
  "directness": "How specifically and clearly does the answer address the question? A direct answer should provide a clear and concise answer to the question. For example, if the question is 'What is the capital of France?', a direct answer would be 'Paris'. A direct answer should not provide any irrelevant or unnecessary information that does not answer the question. For example, an indirect answer would be 'The capital of France is located on the river Seine'.", 
  "empowerment": "How well does the answer help the reader understand and make informed judgements about the topic without being misled or making fallacious assumptions. Evaluate each answer on the quality of answer as it relates to clearly explaining and providing reasoning and sources behind the claims in the answer."
}

    
with open("C:/Users/Chris/OneDrive/Documents/ObsidianVault/prof/files/Python/llm_evaluator/data/questions.txt", mode="r", encoding="UTF-8") as file:
    questions = [i.replace("\n", "") for i in file.readlines()]

with open("C:/Users/Chris/OneDrive/Documents/ObsidianVault/prof/files/Python/llm_evaluator/regularRAG_responses.json", mode="r", encoding="UTF-8") as file:
    regularRAG_responses = json.loads(file.read())

with open("C:/Users/Chris/OneDrive/Documents/ObsidianVault/prof/files/Python/llm_evaluator/graphRAG_responses.json", mode="r", encoding="UTF-8") as file:
    grapRAG_responses = json.loads(file.read())


fieldnames = ["timestamp", "question", "regularRAG_response", "grapRAG_response", "criterion", "winner", "reasoning"]

results_dir = "./llm_judge_runs"
os.makedirs(results_dir, exist_ok=True)

# Run the evaluation 5 times
for run_number in range(5):
    print(f"\nStarting run {run_number + 1} of 5")
    
    run_results = []
    
    for i, question in enumerate(questions):
        print(f"Question {i + 1} of {len(questions)}")

        for criterion in CRITERIA:
            regularRAG_response = regularRAG_responses[question]

            # Strip query prelude of meta data 
            grapRAG_response = grapRAG_responses[question].split("SUCCESS: Global Search Response: ")[1] 

            # Randomize answer input order to mitigate llm bias sensitive to order
            responses = [
                ("regularRAG", regularRAG_response),
                ("grapRAG", grapRAG_response)
            ]
            random.shuffle(responses)
            
            # Map the randomized responses to Answer 1 and 2
            answer1_type, answer1 = responses[0]
            answer2_type, answer2 = responses[1]

            print(f"Evaluating criterion: {criterion}")

            prompt = f"""
                ---Role---

                You are a helpful assistant responsible for grading two answers to a question that are provided by two
                different people.

                ---Goal---

                Given a question and two answers (Answer 1 and Answer 2), assess which answer is better according to
                the following measure:

                {criterion}

                Your assessment should include two parts:
                - Winner: either 1 (if Answer 1 is better) and 2 (if Answer 2 is better) or 0 if they are fundamentally
                similar and the differences are immaterial.
                - Reasoning: a short explanation of why you chose the winner with respect to the measure described above.

                Format your response as a JSON object with the following structure:
                {{
                "winner": <1, 2, or 0>,
                "reasoning": "Answer 1 is better because <your reasoning>."
                }}

                ---Question---

                {question}

                ---Answer 1---

                {answer1}

                ---Answer 2---

                {answer2}

                Assess which answer is better according to the following measure:

                {criterion}

                Output:
                """
                
            response = ollama.chat(model="llama3.1", messages=[{"role": "user", "content": prompt}])
            
            try:
                response = response["message"]["content"].replace("```json", "").replace("```", "").strip()
                result = json.loads(response)
            except:
                try:
                    response = response["message"]["content"].split("Therefore, the output in JSON format is:")[1].replace("\n").strip() # hacky way if answer diverges
                    result = json.loads(response)
                except:
                    print(f"ERROR for criterion {criterion} on question {question}")
                    continue

            # Map the winner back to the correct response type
            winner = result["winner"]
            if winner == 0:  # Only remap if there is a winner
                winner_type = "tie"
            elif winner == 1:
                winner_type = answer1_type
            else:
                winner_type = answer2_type
           
            entry = {
                "run_number": run_number + 1,
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "criterion": criterion,
                "regularRAG_response": regularRAG_response,
                "grapRAG_response": grapRAG_response,
                "winner": winner_type,
                "reasoning": result["reasoning"]
            }

            run_results.append(entry)

    # Save results for this run
    output_file = os.path.join(results_dir, f"judgment_results_run_{run_number + 1}.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(run_results, f, indent=4, ensure_ascii=False)
    
    print(f"Completed run {run_number + 1}, results saved to {output_file}")

print("\nAll runs completed!")




# missing
# - average over replicated win rates ("five times per question")
#    RENAME output file and run again 5x
# - claimify...


"I am sorry but I am unable to answer this question given the provided data."
# bei 15 Fragen...



