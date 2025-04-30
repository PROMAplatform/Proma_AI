from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain.memory import ConversationBufferMemory
from sympy.physics.units import temperature
from langchain_core.documents import Document
from secondary.models import block_history_log_pca_tb
from ..models import block_history_tb
from ..template import default_template, recommend_default_template, recommend_korean_template
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

def llm_answer_block_history_rag(prompt_method, prompt_category, language, history):
    llm = ChatOpenAI(temperature=0.0,
                     max_tokens=2048,
                     model_name='gpt-4o',
                     )
    documents = [Document(page_content=item["type"]) for item in history]
    # 2. 벡터스토어 및 retriever 생성
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)
    retriever = vectorstore.as_retriever()
    #memory = ConversationBufferMemory(input_key="type", memory_key="history")
    memory = ConversationBufferMemory()
    for item in history:
        memory.save_context({"type": item["type"]}, {"outputs": ""})
    if(language == "en"):
        system_message = SystemMessage(content=recommend_default_template)
    else:
        system_message = SystemMessage(content=recommend_default_template + recommend_korean_template)

    human_message = HumanMessagePromptTemplate.from_template(
        "history: {chat_history} context: {context} <question>: {input}")
    print(retriever)
    #human_message = HumanMessagePromptTemplate.from_template("current content: {history}, <question>:{input}")
    user_prompt = ChatPromptTemplate(messages=[system_message, human_message])
    combine_docs_chain = create_stuff_documents_chain(
        llm=llm, prompt=user_prompt,
    )
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    messageQuestion = "prompt_method는 " + prompt_method +" 이고 prompt_category는 " + prompt_category + "야"
    return (retrieval_chain.invoke({"input": messageQuestion, "chat_history": memory}))["answer"]



def get_o_fields_list(model_class):
    """
    Django 모델에서 'o_'로 시작하는 필드 이름만 리스트로 추출합니다.
    """
    return [field.name for field in model_class._meta.get_fields()
            if hasattr(field, 'name') and field.name.startswith('o_')]


