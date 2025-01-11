from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from .template import citizen_template, liar_template, citizen_qa_template, liar_qa_template
from langchain_core.output_parsers import StrOutputParser
import time

class Agent:
    def __init__(self, personality, agent_name, category, word, explain_sen, is_liar):
        self.personality = personality
        self.agent_name = agent_name
        self.category = category
        self.word = word
        self.explain_sen = explain_sen
        self.history = ""
        self.is_liar = is_liar
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

    def introduce(self, dialogue):
        if self.is_liar == True:
            prompt = PromptTemplate.from_template(liar_template)
            chain = prompt | self.llm
            msg = chain.invoke({"dialogue": dialogue, "category": self.category})
        else:
            prompt = PromptTemplate.from_template(citizen_template)
            conversation_chain = prompt | self.llm
            # print(prompt)
            msg = conversation_chain.invoke(
                {"category": self.category, "personal": str(self.personality), "word": self.word,
                "dialogue": dialogue, "explain_sen": self.explain_sen})

        return msg.content

    def interview(self, question, dialogue, history):
        if self.is_liar == True:
            prompt = PromptTemplate.from_template(liar_qa_template)
            chain = prompt | self.llm
            msg = chain.invoke({
                "dialogue": dialogue,
                "category": self.category,
                "question": question,
                "agent_name": self.agent_name,
                "history": history
            })
        else:
            prompt = PromptTemplate.from_template(citizen_qa_template)
            conversation_chain = prompt | self.llm
            msg = conversation_chain.invoke({
                "category": self.category,
                "personal": str(self.personality),
                "word": self.word,
                "dialogue": dialogue,
                "question": question,
                "agent_name": self.agent_name,
                "history": history
            })
        return msg.content
