import pandas as pd
import numpy as np
from config import Direction, direction_scheme


def get_coordinates(file: pd.DataFrame, trigger_word: str) -> (int, int):
    mask = file.map(lambda x: trigger_word.lower() in str(x).lower())
    indices = np.where(mask)
    if len(indices[0]) == 0:
        return None
    x, y = indices[0][0], indices[1][0]
    return (x, y)


def remove_symbols(words: pd.Series) -> pd.Series:
    return words.astype(str).str.replace('\xa0', ' ', regex=False).str.replace('\n', ' ', regex=False).str.strip()


def get_general_data(file: pd.DataFrame, direction_scheme: dict, scheme_word: str) -> pd.Series:
    list_of_scheme = direction_scheme.get(scheme_word)
    if list_of_scheme == None:
        return None
    trigger_word, direction, expected_type = list_of_scheme
    coordinates = get_coordinates(file, trigger_word)
    if coordinates == None:
        return None
    x, y = coordinates
    if direction == Direction.horizontal:
        if expected_type == str:
            return remove_symbols(pd.Series([file.iloc[x, y+ 1:].dropna()][0]))
        else:
            return remove_symbols(file.iloc[x, :].dropna())

    if direction == Direction.vertical:
        if expected_type == str:
            return remove_symbols(pd.Series([file.iloc[x + 1, y].dropna()][0]))
        else:
            return remove_symbols(file.iloc[x + 1:, y].dropna())


def get_supplier_rate(file: pd.DataFrame, direction_scheme: dict, suppliers: list, scheme_lot_rate: list) -> dict:
    scheme_lot, scheme_rate = scheme_lot_rate
    series_of_lots = get_general_data(file, direction_scheme, scheme_lot)

    if series_of_lots is None or series_of_lots.empty:
        return None

    series_of_lots = series_of_lots[pd.to_numeric(series_of_lots, errors='coerce').notna()]

    result = {lot: {} for lot in series_of_lots}
    rate_word = direction_scheme[scheme_rate][0]

    mask = file.map(lambda x: rate_word in str(x))
    coords_v = np.where(mask)

    for i, column_idx in enumerate(coords_v[1]):
        row_idx = coords_v[0][0]
        potential_name = file.iloc[row_idx - 1, column_idx]

        matched = None
        clean_potential = str(potential_name).strip() if pd.notna(potential_name) else ''
        for sup in suppliers:
            if clean_potential == str(sup).strip():
                matched = sup
                break
        if matched is not None:
            name_of_supplier = matched
        else:
            if len(coords_v[1]) == len(suppliers):
                name_of_supplier = suppliers[i]
            else:
                name_of_supplier = clean_potential if clean_potential else f"unknown_{i}"

        for tab in range(len(series_of_lots)):
            index_of_lot = series_of_lots.index[tab]
            lot_label = series_of_lots[index_of_lot]

            rate = file.iloc[index_of_lot, column_idx]
            drop_rub = file.iloc[index_of_lot, column_idx + 1]
            drop_pct = file.iloc[index_of_lot, column_idx + 2]

            if not pd.isna(rate):
                result[lot_label][name_of_supplier.strip()] = [rate, drop_rub, drop_pct]

    final_result = {}
    for lot_label, lot_data in result.items():
        if lot_data:
            final_result[lot_label] = lot_data

    return final_result


def get_names_of_lots(file: pd.DataFrame, direction_scheme: dict, scheme_lot_word) -> list[str, ...]:
    trigger_word = direction_scheme.get(scheme_lot_word)[0]

    series_of_lots = get_general_data(file, direction_scheme, scheme_lot_word)
    coordinates = get_coordinates(file, trigger_word)
    if series_of_lots is None or coordinates is None:
        return None
    x, y = coordinates
    names = []
    for tab in range(len(series_of_lots)):

        index_of_lot = series_of_lots.index[tab]
        value = file.iloc[index_of_lot, y + 1]
        if pd.notna(value) and str(series_of_lots[index_of_lot]).isdigit():
            names.append(value)
        # print(index_of_lot, value ,series_of_lots)
    return names


def get_offers(file_sheet_0: pd.DataFrame, file_sheet_1: pd.DataFrame, direction_scheme: dict,
               list_of_words: list) -> dict:
    parsed_data = {}
    for word in list_of_words:
        result = get_general_data(file_sheet_0, direction_scheme, word)
        if isinstance(result, pd.Series):
            parsed_data[word] = result.tolist()
        else:
            parsed_data[word] = result
    name_of_lot = get_names_of_lots(file_sheet_1, direction_scheme, "lot")
    rates = get_supplier_rate(file_sheet_1, direction_scheme, parsed_data['supplier'], ["lot", "rate"])
    parsed_data['rate'] = rates
    parsed_data['name_of_lot'] = name_of_lot
    return parsed_data

