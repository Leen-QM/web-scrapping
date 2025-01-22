import csv

def is_it_a_nationality(filename, query):
    """
    Check if the provided query is a nationality (male or female) and return the country.

    Args:
        filename (str): The name of the CSV file.
        query (str): The query to check (case-insensitive).

    Returns:
        str: The country if the query is a nationality, otherwise 'False'.
    """
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if (query.lower() in row['Demonym (Male)'].lower() or
                query.lower() in row['Demonym (Female)'].lower()):
                return row['Country']
    return False
