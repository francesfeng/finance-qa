def get_text_retrieval_function_call():
    tools = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_context_from_datastore",
            "description": "Retrieve context from vector datastore based on the query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type":"string",
                        "description": "The query to retrieve context, .e.g. UK hydrogen policies, Tailwind for hydrogen projects, etc."
                    },
                    "start_date": {
                        "type": "string",
                        "description": "The date from which the context is retrieved. When user asks for latest, assuming it is today\'s date, minus 3 months."
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The date to which the context is retrieved. Today is 2023-12-04"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_context_from_google_search",
            "description": "Generate 3 google search queries, to retrieve context from google search based on the search queries",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type":"string",
                        "description": "Write 3 google search queries to search online that form an objective opinion of user\'s query. The format is: \"query1, query2, query3\". e.g. \"UK hydrogen strategy, UK hydrogen targets, UK hydrogen strategy update\"."
                    },
                    "date_period": {
                        "type": "string",
                        "description": "The date period for which the context is retrieved, e.g. d1, d2, d3 for last 1, 2, or 3 days; w1, w2,... for last 1 or 2 weeks; m1, m2, m3 for last 1, 2 or 3 months; y1, y2... for last 1 or 2 years. When user asks for latest, assuming it is the last 3 months, m3. One quarter is m3. two quarters is m6. 3 quarters is m9."
                    }
                }
            }
        }
    },    
    ]
    return tools

