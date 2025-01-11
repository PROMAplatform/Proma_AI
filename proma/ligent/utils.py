from .models import room_chat_tb, character_tb, room_interview_tb
import base64
import jwt

def get_dialogue(room):
    try:
        chat_data = room_chat_tb.objects.filter(room_id=room).values()
        dialogue = ""
        if (len(chat_data) == 0):
            return ""
        for i in chat_data:
            character = character_tb.objects.get(id=i['character_id'])
            dialogue += character.name+": " + i['chat_content'] + " / "
        return dialogue
    except room_chat_tb.DoesNotExist:
        return ""

def get_history(room, character_id):
    try:
        chat_data = room_interview_tb.objects.filter(room_id=room, character=character_id).values()
        history = ""
        if (len(chat_data) == 0):
            return ""
        for i in chat_data:
            character = character_tb.objects.get(id=i['character_id'])
            history += "user: "+ i["question"] + character.name+": " + i['answer'] + " / "
        return history
    except room_chat_tb.DoesNotExist:
        return ""

def find_payload(token, key):
    if ' ' in token:
        token = token.split(' ')[1]
    payload = jwt.decode(
        token,
        base64.b64decode(key),
        algorithms=["HS512"]
    )
    return payload