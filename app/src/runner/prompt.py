from typing import Dict, List, Optional
def get_prompt(model: str, query: str = None, context: str = None) -> List[Dict[str, str]]:
    """
    Retrieve the prompt for a given model.
    """

    CLASSIFICATION_RELATED_PROMPT = [
        {"role": "system", "content": "You are a helpful market research analyst. You goal is to: 1. summarise the given question into a short topic. 2. assign a \"Database\" or a \"Text\" label to the question, by judging from the context of the question. 3. Ask 6 additional related questions to the question provided, and summarise each question into a short topic"},
        {"role": "user", "content": "You assign the question \"Database\" label if the question can be answered by executing SQL query against the database, otherwise assign the \"Text\" label. If the user asks questions that can be answered based on the information contained in the following schema, it is a \"Database\" label, otherwise assign the \"Text\" label."},
        {"role": "user", "content": "From now you will respond with json list. Provide only 6 related questions. Keep the response in json format: {\“original question\”: the question provided, \“original topic\”: the summary based on the original question, \“original label\”: the \“Database\” or \“Text\” label assigned, \“related questions\”: [{\“question\”: first related question, \“topic\”: the summary based on the first related question}, {\“question\”: the second related question, \“topic\”: the summary based on the second related question}, …}."},    
        {"role": "user", "content": "You prioritise questions and topics that contains information in the schema provided above."},
        {"role": "user", "content": "Do not list topics or questions that have appeared in the prompt before."},
        {"role": "user", "content": f"Schema: \"\"\"{context}\"\"\""},
        {"role": "user", "content": f"Original question: {query}"},
    ]

    CLASSIFICATION_PROMPT = [
        {"role": "system", "content": "You are a helpful market research analyst. You goal is to: 1. summarise the given question into a short topic. 2. assign a \"Database\" or a \"Text\" label to the question, by judging from the context of the question."},
        {"role": "user", "content": "You assign the question \"Database\" label if the question can be answered by executing SQL query against the database, otherwise assign the \"Text\" label. If the user asks questions that can be answered based on the information contained in the following schema, it is a \"Database\" label, otherwise assign the \"Text\" label."},
        {"role": "user", "content": "From now you will respond with json list. Provide only 6 related questions. Keep the response in json format: {\“question\”: the question provided, \“topic\”: the summary based on the original question, \“label\”: the \“Database\” or \“Text\” label assigned}."},    
        {"role": "user", "content": f"Schema: \"\"\"{context}\"\"\""},
        {"role": "user", "content": f"Original question: {query}"},
    ]

    RELATED_PROMPT = [
        {"role": "system", "content": "You are a helpful market research analyst. You goal is to ask 6 additional related questions to the question provided, summarise each question into a short topic."},
        {"role": "user", "content": "From now you will respond with json list. Provide only 6 related questions. Keep the response in json list format: [{\“question\”: first related question, \“topic\”: the summary based on the first related question}, {\“question\”: the second related question, \“topic\”: the summary based on the second related question}, …]."},    
        {"role": "user", "content": "You prioritise questions and topics that contains information in the schema provided above."},
        {"role": "user", "content": "Do not list topics or questions that have appeared in the prompt before."},
        {"role": "user", "content": f"Schema: \"\"\"{context}\"\"\""},
        {"role": "user", "content": f"Original question: {query}"},
    ]


    TABLE_DATASTORE_PROMPT = [
        {"role": "system", "content": "You are a helpful market analyst. Your goal is to answer the question strictly based on the text provided below. The answer should take into account the time sensitive topics and only provide answers based on the relevant date. However the date doesn\’t need to be part of the answer."},
        {"role": "user", "content": "The text below provides the date on which the text is based, and the actual body of the context, separated by \“——\“. "},
        {"role": "user", "content": "Keep the answer in table format."},
        {"role": "user", "content": "Think carefully, the response should be logical and make sense. You can rewrite the text, and not copy the exact wordings from the text."},
        #{"role": "user", "content": "When you cannot derive the answer from the text provided, you can respond with one sentence: \"Sorry, seems the question is not relevant. Could you please ask a different question?\"."},
        {"role": "user", "content": f"Question: {query}"},
        {"role": "user", "content": f"Text: \"\"\"{context}\"\"\""},
    ]

    TEXT_DATASTORE_PROMPT = [
        {"role": "system", "content": "You are a helpful market analyst. Your goal is to answer questions based on the context provided."},
        #{"role": "user", "content": "When you cannot answer the question, you can respond with one sentence: \"Sorry, seems the question is not relevant. Could you please ask a different question?\"."},
        {"role": "user", "content": f"Question: {query}"},
        {"role": "user", "content": f"Text: \"\"\"{context}\"\"\""},
    ]

    COMBINED_PROMPT = [
        {"role": "system", "content": "You are a helpful market analyst. Your goal is to answer the question strictly based on the text provided below. The answer should take into account the time sensitive topics and only provide answers based on the relevant date. However the date doesn\’t need to be part of the response."},
        {"role": "user", "content": "The text below provides the date on which the text is based, and the actual body of the context, separated by \“——\“."},
        {"role": "user", "content": "The output consists two parts, 1) tables: if the context provided includes markdown tables. 2) text: to provide more detailed explanations."},
        {"role": "user", "content": "Think carefully, the response should be logical and make sense. You can rewrite the text, and not copy the exact wordings from the text."},
        {"role": "user", "content": f"Question: {query}"},
        {"role": "user", "content": f"Text: \"\"\"{context}\"\"\""},

    ]

    TABLE_TO_CHART_PROMPT = [
        {"role": "system", "content": "You are a helpful data analyst. You have two goals, first is to determine if a chart is the best representation for the data provided.  If the data contains mostly numerical value, chart is a good representation for the data provided. In this case, your second goal is to generate a valid JSON in which each element is an object for ECharts API for displaying the following data."},
        {"role": "user", "content": "The output should only have the option specification in ECharts in JSON, and do not provide any explanations. Choose the most optimal chart type and use ECharts API."},
        {"role": "user", "content": "If the data is largely comprised of text data, a chart is not needed. In this case, just respond “chart is not needed."},
        {"role": "user", "content": f"Data: \"\"\"{context}\"\"\""},
        {"role": "user", "content": "ECharts JSON: option = { "}
    ]


    SQL_PROMPT = [
        {"role": "system", "content": f"""You are a helpful database engineer. Your goal is to answer user\'s questions strictly based on the following schemas:\n\n{context}\n\nyou will need use some complex join SQL statement to generate a sql based on user\'s question, and return valid SQL codes only."""},
        {"role": "user", "content": "SQL is strictly based on the schemas provided. Do not make up tables or columns that does not exist in the schemas provided."},
        {"role": "user", "content": "When you cannot answer the question by producing valid SQL from the schemas provided, you can respond with one sentence: \"Sorry, seems the question is not relevant. Could you please ask a different question?\"."},
        {"role": "user", "content": "SQL should filter out Null values when comparing or sorting columns that are integer or double precision"},
        {"role": "user", "content": "Question: What is the total hydrogen capacity in UK?"},
        {"role": "user", "content": "SQL: SELECT SUM(normalised_capacity_in_kilotons_hydrogen_per_year) AS total_hydrogen_capacity_kilotons_per_year_in_uk FROM project_capacity a INNER JOIN project_location b ON a.project_id = b.project_id WHERE b.country = 'UK' OR b.country = 'United Kingdom' OR b.country = 'Great Britain' OR b.country_code = 'UK' OR b.country_code = 'GBR' OR b.country_code = 'GB'"},
        {"role": "user", "content": "Question: What are the 5 largest hydrogen projects in planning?"},
        {"role": "user", "content": "SQL: SELECT pc.project_name FROM project_capacity pc JOIN project_status ps ON pc.project_id = ps.project_id WHERE ps.date_online > NOW() AND pc.normalised_capacity_in_kilotons_hydrogen_per_year IS NOT NULL ORDER BY pc.normalised_capacity_in_kilotons_hydrogen_per_year DESC LIMIT 5"},
        {"role": "user", "content": f"Question: {query}"},
    ]

    SQL_TO_CHART_PROMPT = [
        {"role": "system", "content": "You are a helpful data analyst, You goal is to generate a valid JSON based on the question and the data provided in the csv format. Each element in the JSON output is an object for ECharts API to display the following table."},
        {"role": "user", "content": "The output should only have the option specification in ECharts in JSON, and do not provide any explanations. Choose the most optimal chart type and use ECharts API."},
        {"role": "user", "content": f"Question: {query}"},
        {"role": "user", "content": f"Data: \"\"\" {context} \"\"\""},
        {"role": "user", "content": "ECharts JSON: option = { "}
    ]

    DATA_TO_TEXT_PROMPT = [
        {"role": "system", "content": "You are a helpful market analyst, your goal is to answer the question based on the data provided."},
        {"role": "user", "content": f"Question: {query}"},
        {"role": "user", "content": f"Data: \"\"\"{context}\"\"\""},
    ]



    if model == 'classification_and_related':
        return CLASSIFICATION_RELATED_PROMPT
    
    elif model == 'classification':
        return CLASSIFICATION_PROMPT
    
    elif model == 'related':
        return RELATED_PROMPT
    
    elif model == 'table_datastore':
        return TABLE_DATASTORE_PROMPT
    
    elif model == 'text':
        return TEXT_DATASTORE_PROMPT
    
    elif model == 'combined':
        return COMBINED_PROMPT
    
    elif model == 'table_to_chart':
        return TABLE_TO_CHART_PROMPT
    
    elif model == 'sql':
        return SQL_PROMPT
    
    elif model == 'sql_to_chart':
        return SQL_TO_CHART_PROMPT
    
    elif model == 'data_to_text':
        return DATA_TO_TEXT_PROMPT
    

    else:
        raise ValueError(f"Model {model} not recognised")
    

