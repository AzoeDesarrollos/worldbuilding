import csv


class MyCSV(csv.excel):
    delimiter = ';'


def read_csv(ruta):
    """Lee archivos CSV y los devuelve como una lista."""

    table = []
    with open(ruta, encoding='windows-1252') as file:
        data = csv.reader(file, dialect=MyCSV)
        for row in data:
            for i, value in enumerate(row[1:], 1):
                row[i] = float(row[i])
            table.append(row)

    return table