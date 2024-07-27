from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import ChatOpenAI
from langchain_community.document_loaders import OnlinePDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader

def gemini_answer(prompt, ques, pdf):
    # llm = ChatGoogleGenerativeAI(model="gemini-pro")
    llm = ChatOpenAI(temperature=2.0,  # 창의성 (0.0 ~ 2.0)
                     max_tokens=2048,  # 최대 토큰수
                     model_name='gpt-4o',  # 모델명
                     )
    retriever = gemini_pdf(pdf)

    if retriever is None:
        user_prompt = ChatPromptTemplate.from_template(prompt + "<Question>:{question}")
        chain = (
            user_prompt
            | llm
            | StrOutputParser()
        )
    else:
        user_prompt = ChatPromptTemplate.from_template("{context}" + prompt + "<Question>:{question}")
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | user_prompt
            | llm
            | StrOutputParser()
        )
    return (chain.invoke(ques))

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

def gemini_pdf(pdf):
    if pdf is "":
        return None
    # loader = OnlinePDFLoader(pdf)
    loader = PyPDFLoader(pdf)
    document = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=256, chunk_overlap=50)
    texts = text_splitter.split_documents(document)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  # gemini의 임베딩 모델
    docsearch = Chroma.from_documents(texts, embeddings)
    retriever = docsearch.as_retriever()
    return retriever

def dgu_chatbot(question):
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    retriever = gemini_pdf("https://secure-project-dev-image.s3.ap-northeast-2.amazonaws.com/secure-project-using-image/computer.pdf")
    user_prompt = ChatPromptTemplate.from_template("{context} 너는 동국대학교 컴퓨터공학과 챗봇이야. 이 pdf에 근거해서 친절하게 대답해줘. <Question>:{question}")
    chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | user_prompt
            | llm
            | StrOutputParser()
    )
    return (chain.invoke(question))