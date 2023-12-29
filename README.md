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

```

### Deploy
```
flyctl launch --dockerfile ./Dockerfile


```
Test the API in [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Sample questions
1. What is analysts' latest view on NEL ASA
2. What is the largest hydrogen project in United Kingdom
3. List the number of hydrogen projects per year


### Sections

To run the query model 

```
query = "CEVA Logistics partners with Toyota Motor Europe to test new Hydrogen Fuel Cell Truck?"
#filter = {"type": Type.table}
q = Query(query=query, top_k=10)


# Run query against pinecone table 
res = await agent.query_text_table(q, model=PromptType.table_datastore)


# Run query against pinecone text only (including pdfs and news)
res = await agent.query_text_table(q, model=PromptType.text)
```

### Update schema

Run this following script to update the schema to the latest database structure. The updated schema will saved at 'src/connect/schemas.yaml'. When running ChatGPT, these schemas will be uploaded automatically. 
```
cd src/connect
python3 update_schema.py

```

## Local run 

```
uvicorn app.main:app    
```

# API Structure

The API response json has the following key, value fields:

- **type**: the display type of the response
   - text = "text" # streaming text from datastore
   - table = "table" # streaming table from datastore
   - data = "data" # sql data
   - chart = "chart" #
   - textdata = "textdata" # text from sql data
   - error = "error"


- **label**: "database" if the answer is from SQL, otherwise is "text"




for type "text", the response can only be the following format: 

```
{
   "type":  "text"
   "label": "text"
   "response": {
      "text":
   }
}
```

for type "table", the response can only be the following format: 

```
{
   "type":  "table"
   "label": "text"
   "response": {
      "text":
      "table": 
      "chart": "the echarts option specification in json, generated based on markdown table
   }
}
```


for type "data", the response can only be the following format: 
```
{
   "type": "data"
   "label": "database"
   "response": {
      "data":
      "chart":
   }
}
```

for type "textdata", the response can only be the following format: 

```
{
   "type":  "textdata"
   "label": "text"
   "response": {
      "text":
   }
}
```

[`API routers`](/app/README.md) 


## Roadmap

1. Provide more drill-down info when there are hyperlink on the text that leads to more detailed analysis, e.g. https://www.energy.gov/eere/fuelcells/hydrogen-and-fuel-cell-technologies-office-newsletter-july-october-2023

2. User function all to produce many filters for gogole search templates

