from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import ChatOpenAI

def gemini_answer(prompt, ques):
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    user_prompt = ChatPromptTemplate.from_template(prompt+"{input}")
    chain = (
        user_prompt
        | llm
        | StrOutputParser()
    )
    return (chain.invoke({"input":ques}))

def gemini_preview(sen, word):
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    result = ""
    for i in range(len(word)):
        prompt_2 = ChatPromptTemplate.from_template('"{input}" 이 명사를 "{sen}"이 문장의 __부분에 맞춤법을 맞춰서 넣어줘. 명사와 종결 어미는 수정하지마. 결과 문장만 깔끔하게 보여줘. 이 문장들을 너가 잘 이해할 수 있게 프롬프트처럼 최종 수정된 문장만 보여줘.')
        chain = (
                prompt_2
                | llm
                | StrOutputParser()
        )
        #result.append(chain.invoke({"input": word[i], "sen": sen[i]}))
        result += chain.invoke({"input": word[i], "sen": sen[i]})
        result += " "
    return result

def openai_preview(sen, word):
    llm = ChatOpenAI(temperature=0,  # 창의성 (0.0 ~ 2.0)
                     max_tokens=2048,  # 최대 토큰수
                     model_name='gpt-4o',  # 모델명
                     )
    result = ""
    for i in range(len(word)):
        prompt_2 = ChatPromptTemplate.from_template('"{input}" 이 명사를 "{sen}"이 문장의 __부분에 맞춤법을 맞춰서 넣어줘. 명사와 종결 어미는 수정하지마. 결과 문자열에서 프롬프트 내용은 빼고 결과 문장만 깔끔하게 보여줘. 이 문장들을 너가 잘 이해할 수 있게 프롬프트처럼 최종 수정된 문장만 보여줘.')
        chain = (
                prompt_2
                | llm
                | StrOutputParser()
        )
        # result.append(chain.invoke({"input": word[i], "sen": sen[i]}))
        result += chain.invoke({"input": word[i], "sen": sen[i]})
        result += " "
    return result