from app.client.page import DyPage
from app.client.websocket import DyWss
from loguru import logger
import os, requests, sys

def download_flv(url: str, file_path: str):
    chunk_size = 1024
    response = requests.get(url, stream=True)
    with open(file_path, 'wb') as file:
        for data in response.iter_content(chunk_size=chunk_size):
            file.write(data)
            file.flush()


    
    