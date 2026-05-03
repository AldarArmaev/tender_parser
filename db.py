import psycopg2
from dotenv import load_dotenv
import os
from psycopg2 import OperationalError



def get_db_connection():
    load_dotenv()
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except OperationalError as e:
        print(f"Ошибка подключения: {e}")
        return None


def fill_db(data: dict, file_name: str, conn):
    cursor = conn.cursor()
    try:
        # Вставка procurement
        cursor.execute("""
            INSERT INTO procurements (procedure_code, title, start_date, file_name)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (data['code'], data.get('title'), data['date'], file_name))
        procurement_id = cursor.fetchone()[0]

        # Вставка suppliers (если есть)
        supplier_ids = {}
        for i, sup in enumerate(data.get('supplier', [])):
            cursor.execute("""
                INSERT INTO suppliers (name, email, phone, full_name)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
            """, (
                sup,
                data['mail'][i] if data.get('mail') else None,
                data['number'][i] if data.get('number') else None,
                data['name'][i] if data.get('name') else None
            ))
            row = cursor.fetchone()
            if row:
                supplier_ids[sup] = row[0]
            else:
                # если уже существует — получим id
                cursor.execute("SELECT id FROM suppliers WHERE name = %s", (sup,))
                supplier_ids[sup] = cursor.fetchone()[0]

        # Вставка lots и offers
        for lot_num, bids in data.get('rate', {}).items():
            # найти наименование лота
            lot_idx = list(data['rate'].keys()).index(lot_num)
            lot_name = data['name_of_lot'][lot_idx] if lot_idx < len(data.get('name_of_lot', [])) else None

            cursor.execute("""
                INSERT INTO lots (procurement_id, lot_number, lot_name)
                VALUES (%s, %s, %s) RETURNING id
            """, (procurement_id, int(lot_num), lot_name))
            lot_id = cursor.fetchone()[0]

            for supplier_name, (bid, red, red_pct) in bids.items():
                if supplier_name in supplier_ids:
                    cursor.execute("""
                        INSERT INTO offers (lot_id, supplier_id, bid_amount, reduction_amount, reduction_percentage)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (lot_id, supplier_ids[supplier_name], bid, red, red_pct))

        conn.commit()
        print(f"  ✓ Загружено в БД: {file_name}")

    except Exception as e:
        conn.rollback()
        print(f"  ✗ Ошибка при загрузке {file_name}: {e}")
    finally:
        cursor.close()