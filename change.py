import json

index_map = {"A": 0, "B": 1, "C": 2, "D": 3}

with open("mao/maoQuestions.json", "r", encoding="utf-8") as f:
    datas = json.load(f)

for question in datas:
    if question["options"] == []:
        continue
    question["answer"] = [
        question["options"][index_map[ans]] for ans in question["answer"]
    ]

with open("mao/maoQuestionsModified.json", "w", encoding="utf-8") as f:
    json.dump(datas, f, ensure_ascii=False, indent=2)
