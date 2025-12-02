from gpt import json_from_image_interface
from database import get_connection, add_to_table, update_promotion_statuses

if __name__ == '__main__':
    json_from_image_interface("kukich_41.png", "promo1")

    # connection = get_connection()
    # add_to_table('promo1.json', connection)
    # update_promotion_statuses(connection)
    # connection.close()
