from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import base64
from .models import message_tb, block_history_tb
from .template import default_template, recommend_default_template
import jwt

def llm_answer_his(prompt, messageQuestion, history):
    '''
    기본 답변 생성 함수
    입력:
        - prompt: 사용자가 입력한 프롬프트의 내용, (string)
        - messageQuestion: 사용자가 입력한 질문의 내용, (string)
        - history: 사용자와 대회한 기록, (tuple)
    반환:
        - 생성한 답변(string)
    '''
    llm = ChatOpenAI(temperature=0.0,  # 창의성 (0.0 ~ 2.0)
                     max_tokens=2048,  # 최대 토큰수
                     model_name='gpt-4o',  # 모델명
                     )
    memory = ConversationBufferMemory()
    for i in history:
        memory.save_context({"input": i["input"]},
                            {"outputs": i["outputs"]})      # history to memory
    system_message = SystemMessage(content=default_template + prompt)  # default prompt template + user's prompt
    human_message = HumanMessagePromptTemplate.from_template("current content: {history}, <question>:{input}")
    user_prompt = ChatPromptTemplate(messages=[system_message, human_message])
    conversation = ConversationChain(
        prompt=user_prompt,
        llm=llm,
        memory=memory,
    )
    return conversation.invoke(messageQuestion)["response"]

def llm_answer_block_history(prompt_method, prompt_category, history):
    llm = ChatOpenAI(temperature=0.0,
                     max_tokens=2048,
                     model_name='gpt-4o-mini',
                     )
    #memory = ConversationBufferMemory(input_key="type", memory_key="history")
    memory = ConversationBufferMemory()
    for item in history:
        memory.save_context({"type": item["type"]}, {"outputs": ""})
    system_message = SystemMessage(content=recommend_default_template)
    human_message = HumanMessagePromptTemplate.from_template("current content: {history}, <question>:{input}")
    user_prompt = ChatPromptTemplate(messages=[system_message, human_message])
    conversation = ConversationChain(
        prompt=user_prompt,
        llm=llm,
        memory=memory,
    )
    return conversation.invoke("prompt_method는 " + prompt_method +" 이고 prompt_category는 " + prompt_category + "야 " )["response"]

def llm_one_answer(prompt, messageQuestion):
    llm = ChatOpenAI(temperature=0.0,  # 창의성 (0.0 ~ 2.0)
                     max_tokens=2048,  # 최대 토큰수
                     model_name='gpt-4o',  # 모델명
                     )
    memory = ConversationBufferMemory()
    system_message = SystemMessage(content=default_template + prompt)
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

def get_block_history_tuple(user, promptMethod, promptCateory):
    try:
        block_history_data = block_history_tb.objects.filter(user=user, prompt_category=promptCateory).values()
        block_history = []
        if (len(block_history_data) == 0):
            return ""
        for i in block_history_data:
            block_history.append({"type": i['history']})
        return block_history
    except block_history_tb.DoesNotExist:
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