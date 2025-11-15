from .prompt_template import SQL_RETRIEVER_TEMPLATE, FINAL_ANSWER


def sql_retriever_template(related_table, related_question, question):
    """
    Generate the SQL retriever prompt template.

    Args:
        related_table (dict): A dictionary of related table names and their descriptions.
        related_question (dict): A dictionary of related questions and their SQL queries.
        question (str): The user's question.

    Returns:
        str: The formatted SQL retriever prompt.
    """
    
    formatted_table = "\n".join([f"Schema name: {k}\n{v}" for k, v in related_table.items()])
    formatted_question = "\n".join([f"Question: {k}\nAI generated: {n}" for k, n in related_question.items()])
    
    return SQL_RETRIEVER_TEMPLATE.format(related_table=formatted_table, related_question=formatted_question, question=question)

def final_answer_template(question, answer):
    """
    Generate the final answer prompt template.

    Args:
        question (str): The user's question.
        answer (str): The generated answer.

    Returns:
        str: The formatted final answer prompt.
    """
    return FINAL_ANSWER.format(question=question, answer = answer)