from gpt import *
from text_parser import *

if __name__ == '__main__':
    get_json_from_text(json_from_response(get_text_from_image("tests/test7.png")))
