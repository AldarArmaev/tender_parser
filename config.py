class Direction:
    horizontal = "horizontal"
    vertical = "vertical"

direction_scheme = {
    "code":     ["код закупочной",Direction.horizontal, str],
    "title":    ["название закупочной",Direction.horizontal, str],
    "date":     ["дата начала",Direction.horizontal, str],
    "supplier": ["поставщик",Direction.vertical, list],
    "mail":     ["mail", Direction.vertical, list],
    "number":   ["тел", Direction.vertical, list],
    "name":     ["фио", Direction.vertical, list],
    "lot":      ["№ лота",Direction.vertical, list],
    "rate":     ["Ставка, руб.", Direction.vertical, list]
}

