import psycopg2
import json

from utils import load_database, convert_from_text_to_grams


def get_connection():
    cfg = load_database()
    return psycopg2.connect(
        host=cfg["host"],
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
        port=cfg["port"]
    )


def update_promotion_statuses(conn):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE promotions
            SET status = 'expired'
            WHERE end_date < CURRENT_DATE
            AND status <> 'expired';
        """)

        cur.execute("""
            UPDATE promotions
            SET status = 'active'
            WHERE start_date <= CURRENT_DATE
            AND end_date >= CURRENT_DATE
            AND status <> 'active';
        """)

        cur.execute("""
            UPDATE promotions
            SET status = 'upcoming'
            WHERE start_date > CURRENT_DATE
            AND status <> 'upcoming';
        """)
    conn.commit()


def get_or_create_promotion_type_id(conn, raw_label: str | None):
    # 1. Пустая строка или None → считаем, что типа промо нет
    if not raw_label:
        return None

    # на всякий случай убираем пробелы по краям
    raw_label = raw_label.strip()
    if not raw_label:
        return None

    with conn.cursor() as cur:
        # 2. Ищем уже существующий тип
        cur.execute(
            "SELECT id FROM promotion_types WHERE code = %s",
            (raw_label,)
        )
        row = cur.fetchone()
        if row:
            return row[0]

        # 3. Не нашли — создаём новый
        cur.execute(
            """
            INSERT INTO promotion_types (code, display_name, sort_order)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (raw_label, raw_label, 0),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id



def get_category_id(conn, category_name: str | None):
    if not category_name:
        return None

    category_name = category_name.strip()
    if not category_name:
        return None

    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM categories WHERE name = %s",
            (category_name,)
        )
        row = cur.fetchone()
        if row:
            return row[0]

        cur.execute(
            "INSERT INTO categories (name) VALUES (%s) RETURNING id",
            (category_name,)
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id



def add_to_table(json_name, conn):
    with open(json_name, 'r', encoding='utf-8') as json1_file:
        json1_data = json.load(json1_file)

    for promo in json1_data["promotions"]:
        try:
            product_name = promo["product_name"]
            weight_text = promo["weight"]
            weight_grams = convert_from_text_to_grams(promo["weight"])
            start_date = promo["start_date"]
            end_date = promo["end_date"]
            new_price = promo["new_price"]
            old_price = promo["old_price"]
            new_price_per_kg = promo["new_price_per_kg"]
            old_price_per_kg = promo["old_price_per_kg"]
            promotion_label_raw = promo["promotion"]
            category_raw = promo["category"]

            promotion_type_id = get_or_create_promotion_type_id(conn, promotion_label_raw)
            category_id = get_category_id(conn, category_raw)
            chain_id = 1

            with conn.cursor() as cur:
                cur.execute("""
                            INSERT INTO promotions (
                                product_name,
                                weight_text,
                                weight_grams,
                                start_date,
                                end_date,
                                new_price,
                                old_price,
                                new_price_per_kg,
                                old_price_per_kg,
                                promotion_type_id,
                                promotion_label_raw,
                                category_id,
                                chain_id
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (product_name, start_date, end_date, chain_id) DO NOTHING;
                        """, (
                    product_name,
                    weight_text,
                    weight_grams,
                    start_date,
                    end_date,
                    new_price,
                    old_price,
                    new_price_per_kg,
                    old_price_per_kg,
                    promotion_type_id,
                    promotion_label_raw,
                    category_id,
                    chain_id
                ))
        except Exception as e:
            print("\n=== ERROR WHILE IMPORTING PROMO ===")
            print("json file     :", json_name)
            print("product_name  :", promo.get("product_name"))
            print("promotion     :", repr(promo.get("promotion")))
            print("category      :", repr(promo.get("category")))
            print("error type    :", type(e).__name__)
            print("error message :", e)
            # чтобы не глотать ошибку — пробрасываем дальше
            raise

    conn.commit()
