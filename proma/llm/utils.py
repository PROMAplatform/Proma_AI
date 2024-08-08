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
from .template import history_template
from langchain_teddynote.models import MultiModal

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\su\AppData\Local\tesseract.exe'

def gemini_answer(prompt, messageQuestion, messageFile, history):
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    # llm = ChatOpenAI(temperature=0.0,  # 창의성 (0.0 ~ 2.0)
    #                  max_tokens=2048,  # 최대 토큰수
    #                  model_name='gpt-4o',  # 모델명
    #                  )
    retriever = gemini_pdf(messageFile)
    if history == "":
        tmp_history = ""
    else:
        tmp_history = history_template + history
    if retriever is None:
        user_prompt = ChatPromptTemplate.from_template(tmp_history + prompt + "{question}")
        chain = (
            user_prompt
            | llm
            | StrOutputParser()
        )
    else:
        user_prompt = ChatPromptTemplate.from_template(tmp_history + "{context}" + prompt + "{question}")
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | user_prompt
            | llm
            | StrOutputParser()
        )
    return (chain.invoke(messageQuestion))

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

def gemini_pdf(pdf):
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
            {"type": "text", "text": tmp_history + messageQuestion},
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
        tmp_history = history_template + history
    multimodal_gemini = MultiModal(
        llm, system_prompt=tmp_history+prompt, user_prompt=messageQuestion
    )
    answer = multimodal_gemini.stream(messageFile)
    ret = ''
    for i in answer:
        ret += i.content
    return ret

def get_history(room):
    chat_data = message_tb.objects.filter(chatroom_id=room).values()
    history = ""
    if (len(chat_data) == 0):
        return ""
    for i in chat_data:
        history += '[human]:' + i['message_question'] + ' / [system]:' + i['message_answer'] + ' / '

    return history