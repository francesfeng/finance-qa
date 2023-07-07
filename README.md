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

```
   #Bear token
   os.environ['BEARER_TOKEN']

   #OpenAI API
   os.environ['OPENAI_API_KEY']
   os.environ['OPENAI_MODEL']
   

   #Pinecone vector datastore
   os.environ['PINECONE_API_KEY']
   os.environ['PINECONE_ENVIRONMENT']
   os.environ['PINECONE_INDEX']

   #Database setup (using neon.tech)
   os.environ['NEON_HOST']
   os.environ['NEON_DATABASE']
   os.environ['NEON_USER']
   os.environ['NEON_PASSWORD']
 ```

## Set up

### Database/Postgresql

```
psql 'postgresql://{username}:{password}@ep-lucky-boat-370025.eu-central-1.aws.neon.tech/neondb'
```
A detailed instructions of connecting to pgAdmin is provided [here](https://neon.tech/docs/connect/connect-postgres-gui)
### Run 
```
# clone repo
git clone https://github.com/endepth/finance-qa.git

cd finance-qa

# start virtual environment
pipenv shell --python 3.10
pipenv shell

# install requirements
pip install -r requirements.txt

# Start uvicorn server
uvicorn app.main:app

# Deploy
flyctl launch --dockerfile ./Dockerfile

```

Test the API in [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Sample questions
1. What is analysts' latest view on NEL ASA
2. What is the largest hydrogen project in United Kingdom
3. List the number of hydrogen projects per year