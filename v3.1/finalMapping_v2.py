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
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Ensure required columns exist in the CSV file
            if 'Demonym (Male)' not in reader.fieldnames or 'Demonym (Female)' not in reader.fieldnames:
                return "Error: Missing required columns in CSV file."
            
            for row in reader:
                # Check if the query matches either male or female demonym
                if (query.lower() in row['Demonym (Male)'].lower() or 
                    query.lower() in row['Demonym (Female)'].lower()):
                    return row['Country']
          
    except FileNotFoundError:
        return f"Error: The file '{filename}' was not found."
    except Exception as e:
        return f"Error: {str(e)}"

