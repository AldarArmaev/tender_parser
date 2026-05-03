import unittest
import pandas as pd
from src.utils import remove_symbols, get_coordinates
from src.config import Direction, direction_scheme

class TestUtils(unittest.TestCase):

    def test_remove_symbols_text(self):
        result = remove_symbols("текст\xa0с пробелом\nновая")
        self.assertEqual(result, "текст с пробелом новая")

    def test_remove_symbols_number(self):
        result = remove_symbols(123.45)
        self.assertEqual(result, "123.45")

    def test_get_coordinates_found(self):
        df = pd.DataFrame([["код процедуры", "ZK-001"]])
        trigger_word = direction_scheme['code']
        coords = get_coordinates(df, trigger_word)
        self.assertIsNotNone(coords)
        self.assertEqual(coords, (0, 0))

    def test_get_coordinates_not_found(self):
        df = pd.DataFrame([["другое", "значение"]])
        trigger_word = direction_scheme['unknown']
        coords = get_coordinates(df, trigger_word)
        self.assertIsNone(coords)


if __name__ == "__main__":
    unittest.main()