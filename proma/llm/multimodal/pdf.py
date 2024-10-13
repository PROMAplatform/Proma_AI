import base64
import requests
import os
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain.memory import ConversationBufferMemory, VectorStoreRetrieverMemory
from ..template import implicit_template
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import (
    ConversationChain,
    ConversationalRetrievalChain,
    StuffDocumentsChain,
    create_retrieval_chain,
    LLMChain,
)

def llm_answer_his_pdf(prompt, messageQuestion, messageFile, history):
    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
    llm = ChatOpenAI(temperature=0.0,  # 창의성 (0.0 ~ 2.0)
                     max_tokens=2048,  # 최대 토큰수
                     model_name='gpt-4o',  # 모델명
                     )
    retriever = pdf_loader(messageFile)
    memory = VectorStoreRetrieverMemory(memory_key='chat_history', retriever=retriever)
    for i in history:
        memory.save_context(
            {"input": i["input"]},
            {"outputs": i["outputs"]}
        )
    system_message = SystemMessage(content=implicit_template + prompt)
    human_message = HumanMessagePromptTemplate.from_template("current content: {chat_history}, context: {context} <question>: {question}")
    user_prompt = ChatPromptTemplate(messages=[system_message, human_message])
    question_generator_chain = LLMChain(
        llm=llm,
        prompt=user_prompt,
    )
    # combine_docs_chain = create_stuff_documents_chain(llm, user_prompt)

    combine_docs_chain = StuffDocumentsChain(
        llm_chain=question_generator_chain,
        document_variable_name="context",
        # memory=memory,
    )
    # retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    chain = ConversationalRetrievalChain(
        combine_docs_chain=combine_docs_chain,
        question_generator=question_generator_chain,
        retriever=retriever,
        memory=memory,
        get_chat_history=lambda h: h,
    )
    # chain = (
    #         {"context": retriever, "question": RunnablePassthrough(), "history": memory.load_memory_variables({})}
    #         | user_prompt
    #         | llm
    # )
    return (chain.invoke(messageQuestion))

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