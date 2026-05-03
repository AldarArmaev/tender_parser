from db import fill_db, get_db_connection
from utils import get_offers
from datetime import datetime
import pandas as pd
import glob
from config import Direction, direction_scheme


def main():
    # Подключение к БД
    conn = get_db_connection()
    if not conn:
        print("Ошибка подключения к БД")
        return

    # Обработка файлов
    files = glob.glob("files/*.xlsx")
    print(f"Найдено файлов: {len(files)}")

    for file_name in files:
        print(f"\n{file_name}")

        # Загрузка листов
        sheet1 = pd.read_excel(file_name, sheet_name=0, header=None)
        sheet2 = pd.read_excel(file_name, sheet_name=1, header=None)

        # Парсинг
        data = get_offers(sheet1, sheet2, direction_scheme,
                          ["code","title", "date", "supplier", "mail", "number", "name"])

        print(data)
        # Загрузка в БД
        #fill_db(data, file_name, conn)
        print(f"✓ Успешно загружен: {file_name}")

    conn.close()
    print("\n✅ Готово!")


if __name__ == "__main__":
    main()