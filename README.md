# Finance QA

Connecting ChatGPT to Pinecone vector store and PostgreSQL database, so that you can ask questions about hydrogen. You will get an answer in text, data or chart, depending on how ChatGPT routes the question.

At the moment, we have 4 tables available in SQL database, which are project_capacity, project_status, project_location, and project_technology. Any questions about hydrogen projects' capacity, status, location and technology will be routed to SQL database. Any other questions will be routed to Pinecone datastore for text answers.
</br>
</br>

### The workflow of interacting with SQL database is following:

1. Depending on the context of the question, ChatGPT will ask database server for the schema of selected tables which contains the answers
2. From the schema given, ChatGPT generate SQL query
3. Server run the SQL query and reply with the data in csv stream.
4. Dependings on the data given, if it is a sinple row of data, ChatGPT will answer in natural language. If more than one row, ChatGPT will further generate python charting code based on the data structure.
   </br>
   </br>

### The workflow of interacting with Pinecone is following:

1. The prerequisite of using Pinecone datastore is that index has been created, and all relevant text data is vectorised, and its embedding is stored in Pinecone datastore already.
2. Using ada-text-embedding-02 model, create embedding of the question/Query
3. Pinecone retrieve the top 10 most relevant records to the query by cosine similarities (context)
4. Feed both the question and the top10 relevant records into prompt, and retrieve answers from ChatGPT (in-context learning)
   </br>
   </br>

### Following environment variables need to set:

- os.environ['OPENAI_API_KEY']
- os.environ['PINECONE_API_KEY']
- os.environ['PINECONE_ENVIRONMENT']
- os.environ['PINECONE_INDEX']
- os.environ['PG_HOST']
- os.environ['PG_DATABASE']
- os.environ['PG_USER']
- os.environ['PG_PASSWORD']
  <br>
  <br>

## Run

```
python terminal.py
```
