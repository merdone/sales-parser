from gpt import json_from_image_interface
from crop_image import crop_products
from database import get_connection, add_to_table, update_promotion_statuses

if __name__ == '__main__':
    prompt_path = "prompts/prompt_combo.txt"
    image_path = "kukich_41.png"
    system_prompt = prompt_path.read_text(encoding="utf-8")
    json_from_image_interface(image_path, "KUKICH", system_prompt)

    json_path = "KUKICH.json"
    out_dir = "crops"

    crop_products(image_path, json_path, out_dir)

    # json_from_image_interface("kukich_41.png", "promo1")

    # connection = get_connection()
    # add_to_table('promo1.json', connection)
    # update_promotion_statuses(connection)
    # connection.close()
