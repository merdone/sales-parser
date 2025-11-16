import os
import json
from dotenv import load_dotenv
from google.cloud import vision
from google.oauth2 import service_account
import io

from utils import *


def get_text_from_image(image_path):
    key_data = load_api_key("google")

    credentials = service_account.Credentials.from_service_account_info(key_data)
    client = vision.ImageAnnotatorClient(credentials=credentials)

    with io.open(image_path, 'rb') as f:
        content = f.read()

    image_context = vision.ImageContext(
        language_hints=["pl"]
    )

    image = vision.Image(content=content)

    response = client.document_text_detection(
        image=image,
        image_context=image_context
    )
    return response


def json_from_response(response):
    document = response.full_text_annotation
    full_text = ""

    for page_idx, page in enumerate(document.pages):
        for block_idx, block in enumerate(page.blocks):
            block_text = ""
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text = "".join([symbol.text for symbol in word.symbols])
                    block_text += word_text + " "
                block_text += "\n"
            full_text += block_text

            vertices = [(v.x, v.y) for v in block.bounding_box.vertices]
            for vertex in vertices:
                full_text += str(vertex)

    return full_text
