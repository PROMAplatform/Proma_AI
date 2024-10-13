from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import base64
from .models import message_tb
from .template import history_template, implicit_template, preview_template
import jwt

def llm_answer(prompt, messageQuestion, history):
    llm = ChatOpenAI(temperature=0.0,  # 창의성 (0.0 ~ 2.0)
                     max_tokens=2048,  # 최대 토큰수
                     model_name='gpt-4o',  # 모델명
                     )
    if history == "":
        tmp_history = ""
    else:
        tmp_history = history + history_template
    user_prompt = ChatPromptTemplate.from_template(implicit_template + tmp_history + "<prompt>:[" + prompt + "] <question>: {question}  ")
    chain = (
        user_prompt
        | llm
        | StrOutputParser()
    )
    return (chain.invoke(messageQuestion))

def llm_answer_his(prompt, messageQuestion, history):
    llm = ChatOpenAI(temperature=0.0,  # 창의성 (0.0 ~ 2.0)
                     max_tokens=2048,  # 최대 토큰수
                     model_name='gpt-4o',  # 모델명
                     )
    memory = ConversationBufferMemory()
    for i in history:
        memory.save_context({"input": i["input"]},
                            {"outputs": i["outputs"]})
    system_message = SystemMessage(content=implicit_template + prompt)
    human_message = HumanMessagePromptTemplate.from_template("current content: {history}, <question>:{input}")
    user_prompt = ChatPromptTemplate(messages=[system_message, human_message])
    conversation = ConversationChain(
        prompt=user_prompt,
        llm=llm,
        memory=memory,
    )
    return conversation.invoke(messageQuestion)["response"]

def get_history_tuple(room):
    try:
        chat_data = message_tb.objects.filter(chatroom_id=room).values()
        history = []
        if (len(chat_data) == 0):
            return ""
        for i in chat_data:
            history.append({"input": i['message_question'], "outputs": i['message_answer']})
        return history
    except message_tb.DoesNotExist:
        return []

def find_payload(token, key):
    if ' ' in token:
        token = token.split(' ')[1]
    payload = jwt.decode(
        token,
        base64.b64decode(key),
        algorithms=["HS256"]
    )
    return payload

def fallback_response(lang):
    if lang == "ko":
        return "죄송합니다. 다시 질문해주시기 바랍니다."
    if lang == "en":
        return "I'm sorry, but could you please ask that again?"
    return "fallback"