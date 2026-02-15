import psycopg2
import json

from app.services.utils import convert_from_text_to_grams

from app.loader import load_database


class Database:
    def __init__(self) -> None:
        cfg = load_database()
        self.connection = psycopg2.connect(
            host=cfg["host"],
            dbname=cfg["dbname"],
            user=cfg["user"],
            password=cfg["password"],
            port=cfg["port"]
        )
        self.create_tables()

    def create_tables(self) -> None:
        with self.connection.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS chains (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
            """)
            cur.execute("INSERT INTO chains (name) VALUES ('biedronka') ON CONFLICT (name) DO NOTHING;")

            cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL
            );
            """)
            initial_categories = [
                "słodycze i przekąski",
                "mięso i wędliny",
                "nabiał i jajka",
                "ryby i owoce morza",
                "pieczywo i wypieki",
                "napoje",
                "mrożonki",
                "produkty suche",
                "produkty śniadaniowe",
                "gotowe dania",
                "inne"
            ]
            for category in initial_categories:
                cur.execute("INSERT INTO categories (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", (category,))

            cur.execute("""
            CREATE TABLE IF NOT EXISTS promotion_types (
                id SERIAL PRIMARY KEY,
                code VARCHAR(100) UNIQUE NOT NULL,
                display_name VARCHAR(100),
                sort_order INT DEFAULT 0
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS promotions (
                id SERIAL PRIMARY KEY,
                chain_id INT REFERENCES chains(id),
                category_id INT REFERENCES categories(id),
                promotion_type_id INT REFERENCES promotion_types(id),
                
                product_name TEXT NOT NULL,
                weight_text VARCHAR(50),
                weight_grams INT,

                new_price NUMERIC(10, 2),
                old_price NUMERIC(10, 2),
                new_price_per_kg NUMERIC(10, 2),
                old_price_per_kg NUMERIC(10, 2),

                start_date DATE,
                end_date DATE,

                status VARCHAR(20) DEFAULT 'active', -- active, upcoming, expired
                promotion_label_raw TEXT,

                image_path TEXT,
                source_image_path TEXT,
                coordinates JSONB,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,


                UNIQUE (product_name, start_date, end_date, chain_id)
            );
            """)
        self.connection.commit()

    def get_chain_id(self, chain_name: str) -> int:
        if not chain_name:
            raise ValueError("Chain name cannot be empty")

        chain_name = chain_name.lower().strip()
        with self.connection.cursor() as cur:
            cur.execute("SELECT id FROM chains WHERE name = %s", (chain_name,))
            chain_id = cur.fetchone()
            if chain_id:
                return chain_id[0]
            else:
                raise ValueError(f"Shop '{chain_name}' is not found in database")

    def get_or_create_promotion_type_id(self, raw_label: str | None) -> int:
        if not raw_label or not raw_label.strip():
            return None
        raw_label = raw_label.strip()

        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT id FROM promotion_types WHERE code = %s",
                (raw_label,)
            )
            promotion_type_id = cur.fetchone()
            if promotion_type_id:
                return promotion_type_id[0]

            cur.execute(
                """
                INSERT INTO promotion_types (code, display_name, sort_order)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (raw_label, raw_label, 0),
            )
            promotion_type_new_id = cur.fetchone()[0]

            # self.connection.commit()
            return promotion_type_new_id

    def get_or_create_category_id(self, category_name: str | None) -> int:
        if not category_name:
            category_name = "inne"

        category_name = category_name.lower().strip().strip(".")

        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT id FROM categories WHERE name = %s",
                (category_name,)
            )
            category_id = cur.fetchone()
            if category_id:
                return category_id[0]

            cur.execute(
                "INSERT INTO categories (name) VALUES (%s) RETURNING id",
                (category_name,)
            )
            new_category_id = cur.fetchone()[0]

            # self.connection.commit()
            return new_category_id

    def update_promotion_statuses(self) -> None:
        with self.connection.cursor() as cur:
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
        self.connection.commit()

    def save_promotions_bulk(self, pages_data: list[dict], store_name: str) -> None:
        chain_id = self.get_chain_id(store_name)

        with self.connection.cursor() as cur:
            for page in pages_data:
                for promo in page.get("promotions", []):
                    try:
                        cur.execute("SAVEPOINT sp_promo")
                        product_name = promo.get("product_name")
                        weight_text = promo.get("weight")
                        weight_grams = convert_from_text_to_grams(promo.get("weight"))
                        start_date = promo.get("start_date")
                        end_date = promo.get("end_date")
                        new_price = promo.get("new_price")
                        old_price = promo.get("old_price")
                        new_price_per_kg = promo.get("new_price_per_kg")
                        old_price_per_kg = promo.get("old_price_per_kg")
                        promotion_label_raw = promo.get("promotion")
                        category_raw = promo.get("category")
                        coordinates_json = json.dumps(promo.get("mask", []))
                        crop_path = promo.get("crop_path")
                        source_image = promo.get("source_image")

                        promotion_type_id = self.get_or_create_promotion_type_id(promotion_label_raw)
                        category_id = self.get_or_create_category_id(category_raw)

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
                                chain_id,
                                coordinates,
                                image_path,
                                source_image_path
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                                chain_id,
                                coordinates_json,
                                crop_path,
                                source_image
                            )
                        )
                        cur.execute("RELEASE SAVEPOINT sp_promo")
                    except Exception as e:
                        cur.execute("ROLLBACK TO SAVEPOINT sp_promo")

        self.connection.commit()

    def get_all_promotions(self, limit: int = 100) -> list[dict]:
        with self.connection.cursor() as cur:
            cur.execute("""
                SELECT 
                    p.product_name,
                    p.new_price,
                    p.old_price,
                    p.new_price_per_kg,
                    
                    c.name as category_name,
                    
                    p.start_date,
                    p.end_date,
                    
                    p.image_path,
                    p.source_image_path,
                    p.coordinates,
                    
                    pt.code as promotion_code
                    
                FROM promotions p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN promotion_types pt ON p.promotion_type_id = pt.id
                WHERE p.end_date >= CURRENT_DATE
                ORDER BY p.start_date DESC
                LIMIT %s;
            """, (limit, ))

            rows = cur.fetchall()

            results = []
            col_names = [desc[0] for desc in cur.description]

            for row in rows:
                results.append(dict(zip(col_names, row)))

        return results

    def get_all_promotions_by_category(self, category: str, limit: int = 100) -> list[dict]:
        with self.connection.cursor() as cur:
            cur.execute("""
                SELECT 
                    p.product_name,
                    p.new_price,
                    p.old_price,
                    p.new_price_per_kg,

                    c.name as category_name,

                    p.start_date,
                    p.end_date,

                    p.image_path,
                    p.source_image_path,
                    p.coordinates,

                    pt.code as promotion_code

                FROM promotions p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN promotion_types pt ON p.promotion_type_id = pt.id
                WHERE p.end_date >= CURRENT_DATE AND c.name = %s
                ORDER BY p.start_date DESC
                LIMIT %s;
            """, (category, limit, ))

            rows = cur.fetchall()

            results = []
            col_names = [desc[0] for desc in cur.description]

            for row in rows:
                results.append(dict(zip(col_names, row)))

        return results

    def close(self):
        if self.connection:
            self.connection.close()
