# 一个简单的刷题网站
main.py构建了一个根据给定格式的题库的刷题网站。初次使用需要将main.py中  
``` python
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
            st.session_state.questionNum = getQuestionNum(
                st.session_state.questionsCount - 1
            )
        questionPage(questionDatas)

```  
的questionsPath字段改成你自己的题库路径，题库格式参照`questions.json`，该代码仅实现了单选题，多选题和判断题的随机取题并展示。
