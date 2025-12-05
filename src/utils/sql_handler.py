import re
from services import LLM_connector


def extract_sql_response(text):
    """
    Extracts the longest SQL SELECT statement from the provided text.
    Args:
        text (str): The text containing SQL statements. 
        
        Returns:
        str: The longest SQL SELECT statement found in the text.
    """
    select_statements = re.findall(r'\bselect\b.*?(?:;|\Z)', text, flags=re.IGNORECASE | re.DOTALL)
    
    cleaned_statements = [re.sub(r'\s+', ' ', stmt.replace('\n', ' ')).strip() for stmt in select_statements]
    
    longest_statement = max(cleaned_statements, key=len) if cleaned_statements else None
    
    if longest_statement and not longest_statement.endswith(';'):
        longest_statement += ';'
    
    return longest_statement

def execute_query(query):
    conn = LLM_connector.AzureSQLConnection.get_instance()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        conn.rollback()
        print(f"Error executing query: {e}")
        return None
