import shutil
import requests
import json
import uuid
import random
from langchain_community.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage
import static.data as data
import streamlit as st


def get_message_by_gigachain(session_messages: dict, message: str):
    chat = GigaChat(credentials=st.secrets["CREDENTIALS"], verify_ssl_certs=False)

    pipeline = [SystemMessage(content=data.bots_plot)]

    for cur in session_messages[:-2]:
        if cur["role"] == "user":
            pipeline.append(HumanMessage(content=cur["content"]))
    pipeline.append(HumanMessage(content=message))

    return chat(pipeline).content


def get_access_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload='scope=GIGACHAT_API_PERS'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': str(uuid.UUID(int=random.getrandbits(128), version=4)),
    'Authorization': 'Basic ' + st.secrets["CREDENTIALS"]
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()

    return response_json["access_token"]


def get_payload_headers(message: str):
    access_token = get_access_token()

    payload = json.dumps({
    "model": "GigaChat", 
    "stream": False, 
    "update_interval": 0, 
    "function_call": "auto",
    "messages": [
            {
                "role": "system", 
                "content": data.image_plot + message
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': "Bearer " + access_token
    }
    
    return payload, headers


def save_genrated_image(img_uuid):
    access_token = get_access_token()

    url = f"https://gigachat.devices.sberbank.ru/api/v1/files/{img_uuid}/content"
    headers = {
        'Accept': 'application/jpg',
        'Authorization': 'Bearer ' + access_token
    }

    response = requests.request("GET", url, headers=headers, stream=True)
    image_number = data.get_count_in_folder("static/images/generated/") + 1
    path_to_img = f'static/images/generated/img{image_number}.jpg'
    with open(path_to_img, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

    return path_to_img


def get_image_by_gigachain(message: str):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    payload, headers = get_payload_headers(message)

    response = requests.request("POST", url, headers=headers, data=payload)
    return_json = response.json()

    content = return_json["choices"][0]["message"]["content"]

    img_uuid = content.split('src="')[1].split('" fuse=')[0]

    path_to_img = save_genrated_image(img_uuid)
    res_title = return_json["choices"][0]["message"]["data_for_context"][2]["content"]
    return res_title, path_to_img