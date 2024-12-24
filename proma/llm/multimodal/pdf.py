from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain.memory import ConversationBufferMemory
from ..template import default_template
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

def llm_answer_his_pdf(prompt, messageQuestion, messageFile, history):
    '''
    파일 기반 답변 생성 함수
    입력:
        - prompt: 사용자가 입력한 프롬프트의 내용, (string)
        - messageQuestion: 사용자가 입력한 질문의 내용, (string)
        - messageFile: 사용자가 입력한 파일의 경로, (string)
        - history: 사용자와 대회한 기록, (tuple)
    반환:
        - 생성한 답변(string)
    '''
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
    system_message = SystemMessage(content=default_template + prompt)
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
    loader = PyPDFLoader(pdf)       # pdf 파일 로드
    document = loader.load()        # 내용 추출
    text_splitter = CharacterTextSplitter(chunk_size=256, chunk_overlap=50)     # 데이터를 chunk사이즈로 분할
    texts = text_splitter.split_documents(document)
    embeddings = OpenAIEmbeddings()             # 임베딩
    docsearch = Chroma.from_documents(texts, embeddings)    # 벡터 스토어(chroma)에 저장
    retriever = docsearch.as_retriever()        # retriever 형태로 가져옴
    return retriever
