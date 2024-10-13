import base64
import requests
import os
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from ..template import implicit_template, image_template, image_desc_template

def encode_image_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        image_content = response.content
        if url.lower().endswith((".jpg", ".jpeg")):
            mime_type = "image/jpeg"
        elif url.lower().endswith(".png"):
            mime_type = "image/png"
        else:
            mime_type = "image/unknown"
        return f"data:{mime_type};base64,{base64.b64encode(image_content).decode('utf-8')}"
    else:
        raise Exception("Failed to download image")


# 이미지를 base64로 인코딩하는 함수 (파일)
def encode_image_from_file(file_path):
    with open(file_path, "rb") as image_file:
        image_content = image_file.read()
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        elif file_ext == ".png":
            mime_type = "image/png"
        else:
            mime_type = "image/unknown"
        return f"data:{mime_type};base64,{base64.b64encode(image_content).decode('utf-8')}"


# 이미지 경로에 따라 적절한 함수를 호출하는 함수
def encode_image(image_path):
    if image_path.startswith("http://") or image_path.startswith("https://"):
        return encode_image_from_url(image_path)
    else:
        return encode_image_from_file(image_path)

def create_messages(
        image_url, system_prompt=None, user_prompt=None,
):
    encoded_image = encode_image(image_url)
    # 인코딩된 이미지를 사용하여 다른 처리를 수행할 수 있습니다.
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"{encoded_image}"},
                },
            ],
        },
    ]
    return messages

def llm_answer_his_img(prompt, messageQuestion, history, imageFile):
    llm = ChatOpenAI(temperature=0.0,  # 창의성 (0.0 ~ 2.0)
                     max_tokens=2048,  # 최대 토큰수
                     model_name='gpt-4o',  # 모델명
                     )
    memory = ConversationBufferMemory()
    for i in history:
        memory.save_context({"input": i["input"]},
                            {"outputs": i["outputs"]})

    message = create_messages(imageFile, image_desc_template, "please describe this image")
    image_description = llm.invoke(message).content
    system_message = SystemMessage(content=implicit_template + prompt)
    human_message = HumanMessagePromptTemplate.from_template(image_template + image_description + "current content: {history}, <question>:{input}")
    user_prompt = ChatPromptTemplate(messages=[system_message, human_message])

    conversation = ConversationChain(
        prompt=user_prompt,
        llm=llm,
        memory=memory,
    )
    return (conversation.invoke(messageQuestion))["response"]