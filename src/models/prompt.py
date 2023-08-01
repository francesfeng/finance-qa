from src.models.models import PromptType

def get_prompt(model: PromptType, query: str, context: str):
    """
    Retrieve the prompt for a given model.
    """
    TABLE_DATASTORE_PROMPT = [
        {"role": "system", "content": "You are a helpful market analyst. Your goal is to answer the question strictly based on the text provided below. The answer should take into account the time sensitive topics and only provide answers based on the relevant date. However the date doesn\’t need to be part of the answer."},
        {"role": "user", "content": "The text below provides the date on which the text is based, and the actual body of the context, separated by \“——\“. "},
        {"role": "user", "content": "Keep the answer in table format."},
        {"role": "user", "content": "Think carefully, the response should be logical and make sense. You can rewrite the text, and not copy the exact wordings from the text."},
        {"role": "user", "content": f"Question: {query}"},
        {"role": "user", "content": f"Text: \"\"\"{context}\"\"\""},
    ]

    TEXT_DATASTORE_PROMPT = [
        {"role": "system", "content": "You are a helpful market analyst. Your goal is to answer questions strictly based on the context provided."},
        {"role": "user", "content": f"Question: {query}"},
        {"role": "user", "content": f"Text: \"\"\"{context}\"\"\""},
    ]


    SQL_PROMPT = [
        {"role": "system", "content": f"""You are a helpful database engineer, you have create database tables with the following schemas:\n\n{context}\n\nyou will need use some complex join SQL statement to generate a sql based on user\'s question, and return valid SQL codes only."""},
        {"role": "user", "content": "SQL should filter out Null values when comparing or sorting columns that are integer or double precision"},
        {"role": "user", "content": "Question: What is the total hydrogen capacity in UK?"},
        {"role": "user", "content": "SQL: SELECT SUM(normalised_capacity_in_kilotons_hydrogen_per_year) AS total_hydrogen_capacity_kilotons_per_year_in_uk FROM project_capacity a INNER JOIN project_location b ON a.project_id = b.project_id WHERE b.country = 'UK' OR b.country = 'United Kingdom' OR b.country = 'Great Britain' OR b.country_code = 'UK' OR b.country_code = 'GBR' OR b.country_code = 'GB'"},
        {"role": "user", "content": "Question: What are the 5 largest hydrogen projects in planning?"},
        {"role": "user", "content": "SQL: SELECT pc.project_name FROM project_capacity pc JOIN project_status ps ON pc.project_id = ps.project_id WHERE ps.date_online > NOW() AND pc.normalised_capacity_in_kilotons_hydrogen_per_year IS NOT NULL ORDER BY pc.normalised_capacity_in_kilotons_hydrogen_per_year DESC LIMIT 5"},
        {"role": "user", "content": f"Question: {query}"},
    ]


    
    if model == 'table_datastore':
        return TABLE_DATASTORE_PROMPT
    
    elif model == 'text':
        return TEXT_DATASTORE_PROMPT
    
    elif model == 'sql':
        return SQL_PROMPT
    

    else:
        raise ValueError(f"Model {model} not recognised")
    

