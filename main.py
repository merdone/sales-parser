from dotenv import load_dotenv

from gpt import get_json_from_text, get_json_from_image
from text_parser import get_text_from_image, json_from_response
from utils import write_to_file

load_dotenv()

if __name__ == '__main__':
    ocr_text = get_text_from_image("tests/test7.png")
    json_resp = json_from_response(ocr_text)
    promotions = get_json_from_text(json_resp)
    write_to_file(promotions)

