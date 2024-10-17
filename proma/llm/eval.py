from .template import (
    eval_coh_template,
    eval_con_template,
    eval_flu_template,
    eval_rel_template,
    eval_comment_template,
)

from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from .models import message_tb

def prompt_eval(prompt, chat_data):
    llm = ChatOpenAI(temperature=0.0,  # 창의성 (0.0 ~ 2.0)
                     max_tokens=2048,  # 최대 토큰수
                     model_name='gpt-4o',  # 모델명
                     )
    eval_prompt = [eval_coh_template, eval_con_template, eval_flu_template, eval_rel_template]
    score = [[], [], [], []]
    for i in range(len(chat_data)):
        for j in range(4):
            chain_prompt = PromptTemplate.from_template(eval_prompt[j])
            chain = (
                    chain_prompt
                    | llm
                    | StrOutputParser()
            )
            score[j].append(int(chain.invoke({
                "input": "please evaluation this prompt",
                "Prompt": prompt,
                "User Question": chat_data[i]["input"],
                "Output": chat_data[i]["output"],
            })))
    return {
        "Coherence": sum(score[0]) / len(score[0]),
        "Consistency": sum(score[1]) / len(score[1]),
        "Fluency": sum(score[2]) / len(score[2]),
        "Relevance": sum(score[3]) / len(score[3]),
    }

def eval_comment(prompt, score):
    llm = ChatOpenAI(
        temperature=0.0,  # 창의성 (0.0 ~ 2.0)
        max_tokens=4096,  # 최대 토큰수
        model_name='gpt-4o',  # 모델명
    )
    chain_prompt = PromptTemplate.from_template(eval_comment_template)
    chain = (
            chain_prompt
            | llm
            | StrOutputParser()
    )
    comment = chain.invoke({
        "prompt": prompt,
        "Coherence": score["Coherence"],
        "Consistency": score["Consistency"],
        "Fluency": score["Fluency"],
        "Relevance": score["Relevance"],
    })
    return comment


def get_chat_data(promptId):
    chat_data = message_tb.objects.filter(prompt_id=promptId).values()
    values = []
    for i in chat_data:
        if (len(values) > 7):
            return values
        if(len(i["message_answer"]) > 100):
            values.append({"input": i['message_question'], "output": i['message_answer']})
    return values