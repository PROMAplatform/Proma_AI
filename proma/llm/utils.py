from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
import base64
import pytesseract
from .models import message_tb
from .template import history_template, implicit_template, preview_template
from langchain_teddynote.models import MultiModal
import jwt
from config.settings.base import JWT_SECRET_KEY

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\su\AppData\Local\tesseract.exe'

def gemini_answer(prompt, messageQuestion, history):
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    # llm = ChatOpenAI(temperature=0.0,  # 창의성 (0.0 ~ 2.0)
    #                  max_tokens=2048,  # 최대 토큰수
    #                  model_name='gpt-4o',  # 모델명
    #                  )
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

def gemini_pdf(prompt, messageQuestion, messageFile, history):
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    retriever = pdf_loader(messageFile)
    if history == "":
        tmp_history = ""
    else:
        tmp_history = history + history_template
    user_prompt = ChatPromptTemplate.from_template(implicit_template + tmp_history + "{context}" + "<prompt>:[" + prompt + "] <question>:")
    chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | user_prompt
            | llm
            | StrOutputParser()
    )
    return (chain.invoke(messageQuestion))

def gemini_preview(cate, desc):
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    result = ""
    prompt_2 = ChatPromptTemplate.from_template("template[" + preview_template + '] to fit this template CATEGORY[{cate}] / DESCRIPTION[{desc}] Please put these content.')
    chain = (
            prompt_2
            | llm
            | StrOutputParser()
    )
    for i in range(len(cate)):
        # result.append(chain.invoke({"input": word[i], "sen": sen[i]}))
        result += chain.invoke({"cate": cate[i], "desc": desc[i]})
        result += "\n"
    # result += chain.invoke("A Few Details for More Successful Prompt Engineering")
    return result

def pdf_loader(pdf):
    if pdf is "":
        return None
    loader = PyPDFLoader(pdf)
    document = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=256, chunk_overlap=50)
    texts = text_splitter.split_documents(document)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  # gemini의 임베딩 모델
    docsearch = Chroma.from_documents(texts, embeddings)
    retriever = docsearch.as_retriever()
    return retriever

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        img = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:image/jpeg;base64,{img}"

def chat_img(prompt, messageQuestion, messageFile, history):
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    # llm = ChatOpenAI(temperature=0,  # 창의성 (0.0 ~ 2.0)
    #                  max_tokens=2048,  # 최대 토큰수
    #                  model_name='gpt-4o',  # 모델명
    #                  )
    if messageFile:
        image_url = messageFile
    else:
        base64_image = encode_image(messageFile)
        image_url = f"{base64_image}"
    system_message = SystemMessage(
        content=prompt
    )
    if history == "":
        tmp_history = ""
    else:
        tmp_history = history_template + history
    vision_message = HumanMessage(
        content=[
            {"type": "text", "text": implicit_template + tmp_history + "<prompt>:[" + prompt + "] <question>: "+messageQuestion},
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                    "detail": "auto",
                },
            },
        ]
    )
    output = llm.invoke([system_message, vision_message])
    return output.content


def gemini_img(prompt, messageQuestion, messageFile, history):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
    if history == "":
        tmp_history = ""
    else:
        tmp_history = history + history_template
    multimodal_gemini = MultiModal(
        llm, system_prompt=implicit_template + tmp_history + prompt, user_prompt=messageQuestion
    )
    answer = multimodal_gemini.stream(messageFile)
    ret = ''
    for i in answer:
        ret += i.content
    return ret

def get_history(room):
    try:
        chat_data = message_tb.objects.filter(chatroom_id=room).values()
        history = ""
        if (len(chat_data) == 0):
            return ""
        for i in chat_data:
            history += '[human]:' + i['message_question'] + ' / [system]:' + i['message_answer'] + ' / '
        return history
    except message_tb.DoesNotExist:
        return "error"

def find_id(token):
    token = token.split(' ')[1]
    payload = jwt.decode(
        token,
        base64.b64decode(JWT_SECRET_KEY),
        algorithms=["HS256"]
    )
    return payload['id']

def fallback_response(lang):
    if lang == "ko":
        return "죄송합니다. 다시 질문해주시기 바랍니다."
    if lang == "en":
        return "I'm sorry, but could you please ask that again?"
    return "fallback"