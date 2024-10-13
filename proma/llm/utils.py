from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import (
    ConversationChain,
    ConversationalRetrievalChain,
    StuffDocumentsChain,
    create_retrieval_chain,
    LLMChain,
)
from langchain.memory import ConversationBufferMemory
import base64
from .models import message_tb
from .template import history_template, implicit_template, preview_template
from langchain_teddynote.models import MultiModal
import jwt

def llm_answer(prompt, messageQuestion, history):
    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
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
    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
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
    return conversation.invoke(messageQuestion)

def llm_pdf(prompt, messageQuestion, messageFile, history):
    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
    llm = ChatOpenAI(temperature=0.0,  # 창의성 (0.0 ~ 2.0)
                     max_tokens=2048,  # 최대 토큰수
                     model_name='gpt-4o',  # 모델명
                     )
    retriever = pdf_loader(messageFile)
    # if history == "":
    #     tmp_history = ""
    # else:
    #     tmp_history = history + history_template
    # user_prompt = ChatPromptTemplate.from_template(implicit_template + tmp_history + "{context}" + "<prompt>:[" + prompt + "] <question>:")
    memory = ConversationBufferMemory(memory_key='chat_history')
    for i in history:
        memory.save_context(
            {"input": i["input"]},
            {"outputs": i["outputs"]}
        )
    system_message = SystemMessage(content=implicit_template + prompt)
    human_message = HumanMessagePromptTemplate.from_template("current content: {chat_history}, context: {context} <question>: {input}")
    user_prompt = ChatPromptTemplate(messages=[system_message, human_message])
    question_generator_chain = LLMChain(
        llm=llm,
        prompt=user_prompt,
    )
    # combine_docs_chain = create_stuff_documents_chain(llm, user_prompt)

    combine_docs_chain = StuffDocumentsChain(
        llm_chain=question_generator_chain,
        document_variable_name="context",
        memory=memory,
    )
    retrieval_docs = (lambda x: x["input"]) | retriever
    retrieval_chain = (
        RunnablePassthrough.assign(
            context=retrieval_docs.with_config(run_name="retrieve_documents"),
        ).assign(answer=combine_docs_chain)
    ).with_config(run_name="retrieval_chain")
    # retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    # chain = ConversationalRetrievalChain(
    #     # {"context": retriever},
    #     combine_docs_chain=combine_docs_chain,
    #     question_generator=question_generator_chain,
    #     retriever=retriever,
    #     memory=memory
    # )
    # chain = (
    #         {"context": retriever, "question": RunnablePassthrough(), "history": memory.load_memory_variables({})}
    #         | user_prompt
    #         | llm
    # )
    return (retrieval_chain.invoke({"input": messageQuestion}))

def llm_preview(cate, desc):
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
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_documents(texts, embeddings)
    retriever = docsearch.as_retriever()
    return retriever

def llm_img(prompt, messageQuestion, messageFile, history):
    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
    llm = ChatOpenAI(temperature=0,  # 창의성 (0.0 ~ 2.0)
                     max_tokens=2048,  # 최대 토큰수
                     model_name='gpt-4o',  # 모델명
                     )
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
        return ""

def get_history_tuple(room):
    try:
        chat_data = message_tb.objects.filter(chatroom_id=room).values()
        history = []
        if (len(chat_data) == 0):
            return ""
        for i in chat_data:
            history.append({"input": i['message_question'], "outputs": i['message_answer']})
            # history.append({"output": i['message_answer']})
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