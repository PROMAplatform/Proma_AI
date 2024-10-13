from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain.memory import ConversationBufferMemory
from ..template import implicit_template
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

def llm_answer_his_pdf(prompt, messageQuestion, messageFile, history):
    llm = ChatOpenAI(temperature=0.0,  # 창의성 (0.0 ~ 2.0)
                     max_tokens=2048,  # 최대 토큰수
                     model_name='gpt-4o',  # 모델명
                     )
    retriever = pdf_loader(messageFile)
    memory = ConversationBufferMemory()
    for i in history:
        memory.save_context(
            {"input": i["input"]},
            {"outputs": i["outputs"]}
        )
    system_message = SystemMessage(content=implicit_template + prompt)
    human_message = HumanMessagePromptTemplate.from_template("history: {chat_history} context: {context} <question>: {input}")
    user_prompt = ChatPromptTemplate(messages=[system_message, human_message])
    combine_docs_chain = create_stuff_documents_chain(
        llm=llm, prompt=user_prompt,
    )
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    return (retrieval_chain.invoke({"input": messageQuestion, "chat_history": memory}))["answer"]

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
