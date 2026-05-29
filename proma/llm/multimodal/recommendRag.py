from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain_core.documents import Document

from secondary.models import block_history_log_pca_tb
from .evalues3 import evaluate_rag_simple_bert
from .evalus import evaluate_rag_performance
from ..evalues2 import evaluate_rag_simple
from ..template import  recommend_default_template, recommend_korean_template
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from datetime import datetime


def llm_answer_block_history_rag(prompt_method, prompt_category, language, user_inputs):
    llm = ChatOpenAI(temperature=0.0,
                     max_tokens=2048,
                     model_name='gpt-4o',
                     )

    start_time = datetime.now()

    query_fields = {
        k: v for k, v in user_inputs.items()
        if k not in ['type', 'category'] and v.strip()
    }


    fields_list = get_o_fields_list(block_history_log_pca_tb)
    queryset = block_history_log_pca_tb.objects.values(*fields_list)
    history = [{"type": f"{key}:{value}"} for row in queryset for key, value in row.items()]

    # for row in queryset:
    #     for key, value in row.items():
    #         history.append({"type": f"{key}: {value}"})

    # 3. 벡터스토어 생성 (필드별 데이터 포함)
    documents = [Document(page_content=item["type"]) for item in history]
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)
    context_docs_by_field = {}
    context_docs = []

    for field, value in query_fields.items():
        field_query = f"{field}:{value}"
        seen_contents = set()
        unique_docs = []
        k = 10  # 초기 검색 개수
        max_attempts = 7  # 최대 시도 횟수

        for attempt in range(max_attempts):
            # 이미 검색한 문서들을 제외하고 추가로 검색
            print(field_query)
            docs = vectorstore.similarity_search(field_query, k=k)

            new_unique_found = False
            for doc in docs:
                if doc.page_content not in seen_contents:
                    unique_docs.append(doc)
                    seen_contents.add(doc.page_content)
                    context_docs.append(doc)
                    new_unique_found = True

                    # 목표 개수에 도달하면 중단
                    if len(unique_docs) == 5:
                        break

            # 목표 개수에 도달했거나 더 이상 새로운 문서가 없으면 중단
            if len(unique_docs) == 5 or not new_unique_found:
                break

            # 다음 시도에서는 더 많은 문서를 요청
            k += 10

        context_docs_by_field[field] = unique_docs

    # # 기존 검색 결과
   #  context_docs = []
   #  for field, value in query_fields.items():
   #      field_query = f"{field}:{value}"
   #      docs = vectorstore.similarity_search(field_query, k=5)
   #      context_docs.extend(docs)
   #
   #  # query_fields 값과 일치하는 문서 제외
   #  filtered_context_docs = []
   #  for doc in context_docs:
   #      exclude = False
   #      for field, value in query_fields.items():
   #          if field in doc and doc[field] == value:
   #              exclude = True
   #              break
   #      if not exclude:
   #          filtered_context_docs.append(doc)
   #
   #  print(filtered_context_docs)
   #  print(context_docs)
   #  print("asdfkasdljflaskdfjas")
    print(context_docs)
    print("\n" + "🔍 벡터 검색 결과 평가 시작" + "\n")
    evaluation_results = evaluate_rag_simple_bert(query_fields, context_docs)

    # retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    # retrieved_docs = retriever.get_relevant_documents("교수")
    # retrieved_contents = [doc.page_content for doc in retrieved_docs]
    # print(retrieved_contents)

    # 타이머
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    print(f"[process_user_record] 총 소요 시간: {elapsed:.3f}초")

    memory = ConversationBufferMemory()
    # for item in context_docs:
    #     memory.save_context({"type": item["type"]}, {"outputs": ""})

    for item in context_docs:
        # 예시: Document 객체의 주요 텍스트와 type 메타데이터 추출
        text = item.page_content if hasattr(item, "page_content") else str(item)
        doc_type = item.metadata.get("type", "unknown") if hasattr(item, "metadata") else "unknown"
        memory.save_context({"type": doc_type}, {"outputs": text})

    # memory에서 저장한 내용 불러오기
    # ConversationBufferMemory는 get_buffer()로 전체 히스토리를 문자열로 반환
    history = memory.load_memory_variables({})["history"]


    # chain에 넘길 때 context 대신 chat_history 사용

    if(language == "en"):
        system_message = SystemMessage(content=recommend_default_template)
    else:
        system_message = SystemMessage(content=recommend_default_template)



    human_message = HumanMessagePromptTemplate.from_template(
        "history: {chat_history} context: {context} <question>: {input}")

    user_prompt = ChatPromptTemplate(messages=[system_message, human_message])

    # retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

    combine_docs_chain = create_stuff_documents_chain(llm, user_prompt)


    # return (combine_docs_chain.invoke({
    #     "input": f"prompt_method: {prompt_method}, prompt_category: {prompt_category}",
    #     "context": context_docs,
    #     "chat_history": []
    # }))

    return combine_docs_chain.invoke({
        "input": f"prompt_method: {prompt_method}, prompt_category: {prompt_category}",
        "context": context_docs,  # context에 memory에서 불러온 히스토리 전달
        "chat_history": []  # 별도 히스토리 필요시 추가
    })

    # messageQuestion = "prompt_method는 " + prompt_method +" 이고 prompt_category는 " + prompt_category + "야"
    # return (retrieval_chain.invoke({"input": messageQuestion, "chat_history": []}))["answer"]

def get_o_fields_list(model_class):
    """
    Django 모델에서 'o_'로 시작하는 필드 이름만 리스트로 추출합니다.
    """
    return [field.name for field in model_class._meta.get_fields()
            if hasattr(field, 'name') and field.name.startswith('o_')]


