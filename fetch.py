from bs4 import BeautifulSoup
import os
import json
import re


def fetchQUuetion(file):
    res = []
    soup = BeautifulSoup(file, "html.parser")
    questionBlocks = soup.find_all("div", class_="zm_ask")
    answers = soup.find_all("div", class_=re.compile(r"^zr_bg"))
    for questionBlock, answer in zip(questionBlocks, answers):
        if "第一空" in answer.get_text():
            continue
        resAnswer = answer.find("p", class_="fr").get_text(strip=True)
        resAnswer = resAnswer.split("正确答案：", 1)[1].strip()
        options = []
        question = ""
        type = ""
        questionText = questionBlock.get_text(strip=False, separator="\n")
        lines = [line.strip() for line in questionText.split("\n") if line.strip()]
        question = lines[1]
        if re.fullmatch(r"[A-Za-z]+", resAnswer):
            if len(resAnswer) == 1:
                type = "singleSelect"
            else:
                type = "multipleSelect"
                resAnswer = list(resAnswer)
            options = lines[3::2]
        else:
            type = "trueOrFalse"
        res.append(
            {
                "num": 0,
                "question": question,
                "options": options,
                "answer": resAnswer,
                "type": type,
                "explanation": "",
            }
        )
    return res


folderPath = "mao"
res = []

# 获取所有 .html 文件列表
all_files = [f for f in os.listdir(folderPath) if os.path.splitext(f)[1] == ".html"]
total_files = len(all_files)

print(f"🔍 开始处理题目数据，共 {total_files} 个 HTML 文件...\n")

for idx, filename in enumerate(all_files, start=1):
    file_path = os.path.join(folderPath, filename)

    print(f"✅ 正在处理第 {idx}/{total_files} 个文件：{filename}")

    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    questions = fetchQUuetion(html_content)
    res.extend(questions)

print(f"\n🎉 完成！共提取 {len(res)} 道题目。")

with open("mao/maoQuestions.json", "w", encoding="utf-8") as f:
    json.dump(res, f, indent=4, ensure_ascii=False)

print(f"💾 数据已保存至：xi/xiQuestions.json")
