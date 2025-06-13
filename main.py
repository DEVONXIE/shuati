import json
import streamlit as st
import os
import random
from streamlit_option_menu import option_menu
import time


selected = option_menu(
    menu_title=None,  # 不显示标题
    options=["习概", "毛概"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important"},
        "nav-link": {"font-weight": "bold", "padding": "10px 20px"},
    },
)


def getQUestionBank():
    if st.session_state.selected_bank == "习概":
        return "xiQuestions"
    else:
        return "maoQuestions"


def saveUsrData():
    with open(f"{st.session_state.usrId}.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.usrData, f, indent=4, ensure_ascii=False)


def ini_data(usrId, nickName):

    info = {
        "nickName": nickName,
        "xiSolvedNum": 0,
        "maoSolvedNum": 0,
        "solvedNum": 0,
        "xiQuestions": [
            {
                "id": i,
                "correctCount": 0,
                "wrongCount": 0,
                "totalAttempts": 0,
                "consecutiveCorrect": 0,
                "lastCorrectAttempt": 0,
            }
            for i in range(1337)  # 题号从 1 到 1000
        ],
        "maoQuestions": [
            {
                "id": i,
                "correctCount": 0,
                "wrongCount": 0,
                "totalAttempts": 0,
                "consecutiveCorrect": 0,
                "lastCorrectAttempt": 0,
            }
            for i in range(1156)  # 题号从 1 到 1000
        ],
    }
    with open(f"{usrId}.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4, ensure_ascii=False)


def creatQuetion(quetion, options, answer):
    if options is None:
        data = {
            "num": 0,
            "question": quetion,
            "options": None,
            "answer": answer,
            "type": "trueOrFalse",
            "explanation": "",
        }
    else:
        if len(answer) == 1:
            data = {
                "num": 0,
                "question": quetion,
                "options": options,
                "answer": answer,
                "type": "singleSelect",
                "explanation": "",
            }
        else:
            data = {
                "num": 0,
                "question": quetion,
                "options": options,
                "answer": answer,
                "type": "multipleSelect",
                "explanation": "",
            }
    with open("questions.json", "r", encoding="utf-8") as f:
        datas = json.load(f)
    datas.append(data)


def addNumber():
    with open("questions.json", "r", encoding="utf-8") as f:
        datas = json.load(f)
    cnt = 1
    for data in datas:
        data["num"] = cnt
        cnt = cnt + 1


def fetchQuestions(file):
    return


def computeScore(q):
    cc = q["consecutiveCorrect"]
    correct = q["correctCount"]
    wrong = q["wrongCount"]

    # 已学会的题（连对 ≥ 3）完全不出现
    if cc >= 3:
        return float("-inf")

    # 巩固：连对=2 且已经很久没出现
    if (cc == 1 or cc == 2) and (
        st.session_state.currentAttempt - q["lastCorrectAttempt"] >= 20
    ):
        return 999  # 最高优先级巩固

    # 新题（没做过）
    if correct == 0 and wrong == 0:
        return 50

    # 错题优先：错多的更靠前
    return max(wrong * 100 - correct * 50, 10)


def selectQuestion(question_data):
    weighted = []

    for q in question_data:
        score = computeScore(q)
        if score == float("-inf"):
            continue  # 已掌握的不选
        weighted.append((q["id"], score))

    if not weighted:
        return None

    # 拆开 id 和权重
    ids, weights = zip(*weighted)
    return random.choices(ids, weights=weights, k=1)[0]


def judge(chosenAnswer, correctAnswer, question):

    if st.session_state.status:
        if st.button("确定"):
            st.session_state.currentAttempt += 1
            st.session_state.status = False
            if chosenAnswer == correctAnswer:
                st.session_state.isCorrect = True
                if st.session_state.selected_bank == "习概":
                    st.session_state.usrData["xiQuestions"][
                        st.session_state.questionNum
                    ]["consecutiveCorrect"] += 1
                    st.session_state.usrData["xiQuestions"][
                        st.session_state.questionNum
                    ]["correctCount"] += 1
                    st.session_state.usrData["xiQuestions"][
                        st.session_state.questionNum
                    ]["lastCorrectAttempt"] = st.session_state.currentAttempt
                elif st.session_state.selected_bank == "毛概":
                    st.session_state.usrData["maoQuestions"][
                        st.session_state.questionNum
                    ]["consecutiveCorrect"] += 1
                    st.session_state.usrData["maoQuestions"][
                        st.session_state.questionNum
                    ]["correctCount"] += 1
                    st.session_state.usrData["maoQuestions"][
                        st.session_state.questionNum
                    ]["lastCorrectAttempt"] = st.session_state.currentAttempt
            else:
                st.session_state.isCorrect = False
                if st.session_state.selected_bank == "习概":
                    st.session_state.usrData["xiQuestions"][
                        st.session_state.questionNum
                    ]["consecutiveCorrect"] = 0
                    st.session_state.usrData["xiQuestions"][
                        st.session_state.questionNum
                    ]["wrongCount"] += 1
                elif st.session_state.selected_bank == "毛概":
                    st.session_state.usrData["maoQuestions"][
                        st.session_state.questionNum
                    ]["consecutiveCorrect"] = 0
                    st.session_state.usrData["maoQuestions"][
                        st.session_state.questionNum
                    ]["wrongCount"] += 1
            if (
                st.session_state.usrData[getQUestionBank()][
                    st.session_state.questionNum
                ]["consecutiveCorrect"]
                == 3
            ):
                if st.session_state.selected_bank == "习概":
                    st.session_state.usrData["xiSolvedNum"] += 1
                else:
                    st.session_state.usrData["maoSolvedNum"] += 1
            st.session_state.usrData["solvedNum"] += 1
            st.session_state.usrData[getQUestionBank()][st.session_state.questionNum][
                "totalAttempts"
            ] += 1

            saveUsrData()
            st.rerun()
    else:
        bt = st.button("下一题")
        if st.session_state.isCorrect:
            st.success("✅恭喜你做对啦", icon="🌟")
        else:
            st.error(f'😭答案错误  正确答案:{question["answer"]}')
        if bt:
            st.session_state.status = True
            st.session_state.questionNum = selectQuestion(
                st.session_state.usrData[getQUestionBank()]
            )
            st.rerun()


def questionPage(questions):
    questionType = questions[st.session_state.questionNum]["type"]
    if questionType == "trueOrFalse":
        questionType = "判断题"
    elif questionType == "singleSelect":
        questionType = "单选题"
    else:
        questionType = "多选题"
    st.markdown(
        f"""
        <div style="border: 1px solid ; border-radius: 8px; padding: 16px;">
            <p>昵称：{st.session_state.usrData["nickName"]}</p>
            <p>已刷题目数量：{st.session_state.usrData["solvedNum"]}</p>
            <p>已解决习概题目数量（每题连续做对三次算一题）：{st.session_state.usrData["xiSolvedNum"]}</p>
            <p>已解决毛概题目数量（每题连续做对三次算一题）：{st.session_state.usrData["maoSolvedNum"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.selected_bank == "习概":
        status_text = st.write(
            f"已做 {st.session_state.usrData['xiSolvedNum'] } / {len(questions)} 题"
        )
        progress = st.progress(st.session_state.usrData["xiSolvedNum"] / len(questions))
    elif st.session_state.selected_bank == "毛概":
        status_text = st.write(
            f"已做 {st.session_state.usrData['maoSolvedNum'] } / {len(questions)} 题"
        )
        progress = st.progress(
            st.session_state.usrData["maoSolvedNum"] / len(questions)
        )
    if st.session_state.questionNum not in st.session_state.usrData[getQUestionBank()]:
        correctCnt = 0
    else:
        correctCnt = st.session_state.usrData[getQUestionBank()][
            st.session_state.questionNum
        ]
    if questions[st.session_state.questionNum]["type"] == "trueOrFalse":
        st.markdown(
            f"""
            <div style="border: 1px solid ; border-radius: 8px; padding: 16px;">
                <p >{questionType}</p>
                <p >{st.session_state.questionNum + 1}({correctCnt}/3). {questions[st.session_state.questionNum]["question"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        answer = st.radio(label="1", options=("对", "错"), label_visibility="hidden")
        judge(
            answer,
            questions[st.session_state.questionNum]["answer"],
            questions[st.session_state.questionNum],
        )

    elif questions[st.session_state.questionNum]["type"] == "singleSelect":
        st.markdown(
            f"""
            <div style="border: 1px solid ; border-radius: 8px; padding: 16px;">
                <p >{questionType}</p>
                <p >{st.session_state.questionNum + 1}({correctCnt}/3). {questions[st.session_state.questionNum]["question"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        options = questions[st.session_state.questionNum]["options"]
        answer = st.radio(
            label="1",
            options=(
                f"A:{options[0]}",
                f"B:{options[1]}",
                f"C:{options[2]}",
                f"D:{options[3]}",
            ),
            label_visibility="hidden",
        )
        judge(
            answer[0],
            questions[st.session_state.questionNum]["answer"],
            questions[st.session_state.questionNum],
        )

    elif questions[st.session_state.questionNum]["type"] == "multipleSelect":
        st.markdown(
            f"""
            <div style="border: 1px solid ; border-radius: 8px; padding: 16px;">
                <p >{questionType}</p>
                <p >{st.session_state.questionNum + 1}({correctCnt}/3). {questions[st.session_state.questionNum]["question"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        options = questions[st.session_state.questionNum]["options"]
        answers = []
        for i in range(4):
            if st.checkbox(f"{chr(65 + i)}:{options[i]}", value=False):
                answers.append(f"{chr(65 + i)}")
        judge(
            answers,
            questions[st.session_state.questionNum]["answer"],
            questions[st.session_state.questionNum],
        )


def loginPage():
    st.title("用户登录")

    with st.form("login_form"):
        usr_id = st.text_input("请输入用户名 (usrId)", max_chars=16)
        nick_name = st.text_input("请输入昵称 (nickName)")
        submit = st.form_submit_button("登录")

        if submit:
            if not usr_id:
                st.error("用户名不能为空")
            else:
                user_data = loadUsrData(usr_id)

                if user_data is None:
                    # 用户不存在，自动创建账户
                    ini_data(usr_id, nick_name)
                    st.success(f"新账户已创建：{usr_id}")
                    st.session_state.usrId = usr_id
                    st.session_state.nickName = nick_name
                    st.session_state.is_login = True
                    time.sleep(0.5)
                    st.rerun()

                else:
                    # 用户存在，检查 nickName 是否匹配
                    if user_data.get("nickName") == nick_name:
                        st.success(f"欢迎回来，{nick_name}！")
                        st.session_state.usrId = usr_id
                        st.session_state.nickName = nick_name
                        st.session_state.is_login = True
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("昵称不匹配，请重试。")


def loadUsrData(usrId):
    if os.path.exists(f"{usrId}.json"):
        with open(f"{usrId}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None


if "questionsCount" not in st.session_state:
    st.session_state.questionsCount = 0
if "usrId" not in st.session_state:
    st.session_state.usrId = None
if "usrName" not in st.session_state:
    st.session_state.usrName = None
if "usrData" not in st.session_state:
    st.session_state.usrData = {}
if "status" not in st.session_state:
    st.session_state.status = True
if "isCorrect" not in st.session_state:
    st.session_state.isCorrect = False
if "currentAttempt" not in st.session_state:
    st.session_state.currentAttempt = 0
if "selected_bank" not in st.session_state:
    st.session_state.selected_bank = "习概"
if selected != st.session_state.selected_bank:
    st.session_state.selected_bank = selected
    st.session_state.questionNum = selectQuestion(
        st.session_state.usrData[getQUestionBank()]
    )
    st.session_state.status = True
    st.session_state.history_results = []
    st.rerun()


if __name__ == "__main__":
    if "is_login" not in st.session_state:
        loginPage()
    elif st.session_state.is_login == True:

        questionsPath = ""
        if st.session_state.selected_bank == "习概":
            questionsPath = "xi/xiQuestions.json"
        elif st.session_state.selected_bank == "毛概":
            questionsPath = "mao/maoQuestions.json"
        with open(questionsPath, "r", encoding="utf-8") as f:
            questionDatas = json.load(f)
        if st.session_state.usrData == {}:
            st.session_state.usrData = loadUsrData(st.session_state.usrId)
        st.session_state.questionsCount = len(questionDatas)
        if "questionNum" not in st.session_state:
            st.session_state.questionNum = selectQuestion(
                st.session_state.usrData[getQUestionBank()]
            )
        # st.write(st.session_state.questionNum)
        # st.write(st.session_state.usrData["xiQuestions"][st.session_state.questionNum])
        questionPage(questionDatas)
