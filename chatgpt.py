import os
import openai
import logging
import json
from datastore import DataStore


class ChatGPT:

    startMessageStack = [
        {"role": "system", "content": "You act as the middleman between USER and a DATABASE. Your main goal is to answer questions based on data in a SQL Server database (SERVER). You do this by executing valid queries against the database and interpreting the results to anser the questions from the USER."},
        {"role": "user", "content": "From now you will only ever respond with JSON. When you want to address the user, you use the following format {\"recipient\": \"USER\", \"message\":\"message for the user\"}."},
        {"role": "assistant", "content": "{\"recipient\": \"USER\", \"message\":\"I understand.\"}."},
        {"role": "user", "content": "You can address the SQL Server by using the SERVER recipient. When calling the server, you must also specify an action. The action can be QUERY when you want to QUERY the database, or SCHEMA when you need SCHEMA information for a comma separated list of tables. The format you will use for requesting schema information is as follows {\"recipient\":\"SERVER\", \"action\":\"SCHEMA\", \"message\":\"project_status, project_technology\"}. The format you will use for executing a query is as follows: {\"recipient\":\"SERVER\", \"action\":\"QUERY\", \"message\":\"SELECT SUM(normalised_capacity_in_megawatt_electrolyser) FROM project_capacity;\"}"},
        # At some point the list of tables should become dynamic. Todo: Figure out how the flows can be dynamic, perhaps some sort of config.
        {"role": "user", "content": "THe following tables are available in the database: project_status, project_location, project_technology, project_capacity. You will always first request the SCHEMA for a table before using the table in a QUERY."},
        # Newly added message, in the event when the query is invalid.
        {"role": "user", "content": "When there is an issue with the query, the server doesn't need to respond with an error message. You can try to fix the query and try to provide the new query in json format."},
        {"role": "user", "content": "Let's start! What is the total hydrogen capacity in UK?"},
        {"role": "assistant", "content": "{\"recipient\":\"SERVER\", \"action\":\"SCHEMA\", \"message\":\"project_capacity, project_location\"}"},
        {"role": "user", "content": "Table, Column, DataType, Is_Nullable\nproject_capacity, project_id, integer, NO\nproject_capacity, project_name, character varying, NO\nproject_capacity, announced_capacity, character varying, YES\nproject_capacity, normalised_capacity_in_megawatt_electrolyser, double precision, YES\nproject_capacity, normalised_capacity_in_normal_cubit_meter_hydrogen_per_hour, double precision, YES\nproject_capacity, normalised_capacity_in_kilotons_hydrogen_per_year, double precision, YES\nproject_capacity, normalised_capacity_in_tones_co2_captured_per_year, double precision, YES\nproject_capacity, iea_zero_carbon_estimated_normalized_capacity_nm3_h2_per_hour, double precision, YES\nproject_location, project_location_id, integer, NO\nproject_location, project_id, integer, NO\nproject_location, project_name, character varying, NO\nproject_location, country_code, character varying, YES\nproject_location, country, character varying, YES"},
        {"role": "assistant", "content": "{\"recipient\":\"SERVER\", \"action\":\"QUERY\", \"message\":\"SELECT SUM(normalised_capacity_in_kilotons_hydrogen_per_year) AS total_hydrogen_capacity_kilotons_per_year_in_uk FROM project_capacity a INNER JOIN project_location b ON a.project_id = b.project_id WHERE b.country = 'UK' OR b.country = 'United Kingdom' OR b.country = 'Great Britain' OR b.country_code = 'UK' OR b.country_code = 'GBR' OR b.country_code = 'GB';\"}"},      
        {"role": "user", "content": "total_hydrogen_capacity_kilotons_per_year_in_uk\n5174.7"},
        {"role": "assistant", "content": "{\"recipient\": \"USER\", \"message\":\"5174.7 kilotons per year hydrogen capacity in UK.\"}."},
        {"role": "user", "content": "excellent, thank you! Now the next question. How much is the total capacity in Germany?"},
        {"role": "assistant", "content": "{\"recipient\":\"SERVER\", \"action\":\"QUERY\", \"message\":\"SELECT SUM(normalised_capacity_in_kilotons_hydrogen_per_year) AS total_hydrogen_capacity_kilotons_per_year_in_germany FROM project_capacity a INNER JOIN project_location b ON a.project_id = b.project_id WHERE b.country = 'Germany' OR b.country_code = 'DE' OR b.country_code = 'DEU';\"}"},
        {"role": "user", "content": "total_hydrogen_capacity_kilotons_per_year_in_germany\n3402.8"},
        {"role": "assistant", "content": "{\"recipient\": \"USER\", \"message\":\"3402.8 kilotons per year hydrogen capacity in Germany.\"}."},
        {"role": "user", "content": "great, thank you! Now the next question. How much megawatt electrolyser equivalent hydrogen capacity built in China?"},
        # The below messages will be generated by ChatGPT based on the above. Still keeping them in to reinforce the idea, not sure if useful(?).
        {"role": "assistant", "content": "{\"recipient\":\"SERVER\", \"action\":\"QUERY\", \"message\":\"SELECT SUM(normalised_capacity_in_megawatt_electrolyser) AS total_hydrogen_capacity_megawatt_electrolyser_in_china FROM project_capacity a INNER JOIN project_location b ON a.project_id = b.project_id WHERE b.country = 'China' OR b.country_code = 'CN' OR b.country_code = 'CHN';\"}", "role": "assistant"},
        {"role": "user", "content": "total_hydrogen_capacity_megawatt_electrolyser_in_china\n13523.105920978001"},
        {"role": "assistant", "content": "{\"recipient\": \"USER\", \"message\":\"13523.105920978001 megawatt electrolyser equivalent of hydrogen capacity in China.\"}."}, 
        {"role": "user", "content": "What are the 5 largest hydrogen projects in planning?"},
        {"role": "assistant", "content": "{\"recipient\":\"SERVER\", \"action\":\"SCHEMA\", \"message\":\"project_status, project_capacity\"}"},
        {"role": "user", "content": "Table, Column, DataType, Is_Nullable\nproject_status, project_id, integer, NO\nproject_status, project_name, character varying, NO\nproject_status, date_online, date, YES\nproject_status, decomission_date, date, YES\nproject_status, status, character varying, YES\nproject_capacity, project_id, integer, NO\nproject_capacity, project_name, character varying, NO\nproject_capacity, announced_capacity, character varying, YES\nproject_capacity, normalised_capacity_in_megawatt_electrolyser, double precision, YES\nproject_capacity, normalised_capacity_in_normal_cubit_meter_hydrogen_per_hour, double precision, YES\nproject_capacity, normalised_capacity_in_kilotons_hydrogen_per_year, double precision, YES\nproject_capacity, normalised_capacity_in_tones_co2_captured_per_year, double precision, YES\nproject_capacity, iea_zero_carbon_estimated_normalized_capacity_nm3_h2_per_hour, double precision, YES"}, 
        {"role": "assistant", "content": "{\"recipient\":\"SERVER\", \"action\":\"QUERY\", \"message\":\"SELECT pc.project_name FROM project_capacity pc JOIN project_status ps ON pc.project_id = ps.project_id WHERE ps.date_online > NOW() AND pc.normalised_capacity_in_kilotons_hydrogen_per_year IS NOT NULL ORDER BY pc.normalised_capacity_in_kilotons_hydrogen_per_year DESC LIMIT 5;"},
        {"role": "user", "content": "project_name\nHyDeal Ambition\nH21 North of England\nAsian Renewable Energy Hub\nOman green H2 project, phase 2\nBaicheng, Jilin wind-solar project"},
        {"role": "assistant", "content": "{\"recipient\": \"USER\", \"message\":\"The 5 largest hydrogen projects in planning are HyDeal Ambition, H21 North of England, Asian Renewable Energy Hub, Oman green H2 project, phase 2, Baicheng, Jilin wind-solar project.\"}."}
    ]

    startChartingMessageStack =[
        {"role": "system", "content": "You are a helpful assistant. Your main goal is to decide the best type of graph and provide python code to draw the graph based on the input data. you do this by executing valid python code against the input data."},
        {"role": "user", "content": "A sample of the input data is provided as csv string, and the actual data is saved with the path 'data/data.csv'. You construct the input data using pd.read_csv('data/data.csv'). Your preferred charting library is pandas plot"},
        {"role": "user", "content": "From now you will only ever respond with JSON. When you respond the user, you use the following format {\"code\": \" ```import matplotlib.pyplot as plt\n#code to draw the graph\n``` \", \"explanation\": \"the explanation of the graph.\"}."},
        {"role": "user", "content": "The code has to take into account the input data types and the optimal display of the graphs. Convert datetime or timestamp data to the shortest format. The explanation tells the main trend or the abnormalities shown in the graph. Your preferred graphing library is pandas plot library."},
        {"role": "user", "content": "When there is an error in the code, you don\'t need to respond with an explanation, nor apology. You will fix the code and keep the output in json format."},
        #{"role": "user", "content": "Let's start. Input data: year,total_projects_planned_per_year\r\n1900,2\r\n1975,2\r\n2000,8\r\n2001,2\r\n2003,7\r\n2004,6\r\n2005,5\r\n2006,3\r\n2007,7\r\n2008,8\r\n2009,10\r\n2010,8\r\n2011,16\r\n2012,12\r\n2013,21\r\n2014,11\r\n2015,21\r\n2016,16\r\n2017,13\r\n2018,30\r\n2019,34\r\n2020,29\r\n2021,71\r\n2022,75\r\n2023,69\r\n"},
        #{"role": "assistant", "content": "{\"code\": \" ```import matplotlib.pyplot as plt\n\nyears = [1900,1975,2000,2001,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]\nnum_projects = [2,2,8,2,7,6,5,3,7,8,10,8,16,12,21,11,21,16,13,30,34,29,71,75,69]\nplt.plot(years, num_projects)\nplt.xlabel('Year')\nplt.ylabel('Number of Projects Planned')\nplt.title('Total Projects Planned per Year')\nplt.show()\n``` \", \"explanation\": \"The graph shows the number of projects planned over the years. The number of projects remained almost constant till 2010 and then experienced a sharp increase from 2011 until 2023 with a large peak in 2021 and 2022.\"}"},
        {"role": "user", "content": "Input data: country,year,total_hydrogen_capacity_kilotons_per_year\r\nFrance,2000,0.0\r\nUnited Kingdom,2004,0.0\r\nUnited Kingdom,2005,0.0\r\nUnited Kingdom,2008,0.0\r\nFrance,2009,0.0\r\nUnited Kingdom,2010,0.0\r\nUnited Kingdom,2011,0.0\r\n"},
        {"role": "assistant", "content": "{\"code\": \"```import matplotlib.pyplot as plt\nimport pandas as pd\n\ndata=pd.read_csv('data/data.csv')\n\nfrance_df = df[df['country'] == 'France']\nuk_df = df[df['country'] == 'United Kingdom']\n\nplt.plot(france_df['year'], france_df['total_hydrogen_capacity_kilotons_per_year'], label='France')\nplt.plot(uk_df['year'], uk_df['total_hydrogen_capacity_kilotons_per_year'], label='United Kingdom')\n\nplt.xlabel('Year')\nplt.ylabel('Total Hydrogen Capacity (kilotons per year)')\nplt.title('Total Hydrogen Capacity per Year by Country')\nplt.legend()\n\nplt.show()\n\n```\", \"explanation\": \"The graph compares the hydrogen capacity planning between France and the United Kingdom. France invested heavily in hydrogen capacity planning with a peak in 2015 and significant investments continuing even in 2023. On the other hand, the United Kingdom has invested much less with only a small peak in 2021 and 2023.\"}"},
        {"role": "user", "content": "Input data: country,total_hydrogen_capacity_kilotons_per_year\r\nSpain,13037.4\r\nAustralia,11993.4\r\nFrance,11818.5\r\nNetherlands,5556.0\r\nKazakhstan,5198.0\r\nMauritania,5197.6\r\nUnited Kingdom,5174.7\r\nGermany,3402.8\r\n"},
    ]

    startLabelMessageStack = [
        {"role": "system", "content": "You are a helpful assistant. Your main goal is to assign a \"Database\" or a \"Text\" label to the question, by judging from the context of the question."},
        {"role": "user", "content": "From now you will only respond with \"Database\" or \"Text\"."},
        {"role": "user", "content": "You assign the question \"Database\" label if the question can be answered by executing SQL query against the database, otherwise assign the \"Text\" label."},
        {"role": "user", "content": "If the user asks questions relating to hydrogen projects\' capacity, size, location, status, the go-live date, or the usage of technology, it is a \"Database\" label, otherwise assign the \"Text\" label"},
        {"role": "user", "content": "Question: What is Austria\'s hydrogen strategy?\nLabel: Text\n\nQuestion: Which country has the largest hydrogen project?\nLabel: Database\n\n"}
    ]

    startTextSearchStack = [
        {"role": "system", "content": "You are a helpful assistant. Your goal is to answer questions strictly based on the context provided."},
    ]

    startRelatedTopicsStack = [
        {"role": "system", "content": "You are a helpful assistant. You goal is to list topics that are related to the question provided, and ask the question about that topic. Keep the topics simple and direct."},
        {"role": "user", "content": "From now you will respond with json list. When asked to give 5 more examples, keep the response in json list."},
        {"role": "user", "content": "You prioritise topics that relates to hydrogen projects\' location, capacity, size, technology, status or live date."},
        {"role": "user", "content": "Do not list topics or questions that have appeared in the prompt before."},
        #{"role": "user", "content": "Question: what is Austria\'s hydrogen strategy?\n\n1: Topic: Austria\'s total planned hydrogen capacity\nQuestion: What is Austria\'s total planned hydrogen capacity?\n\n2.Topic: The largest hydrogen project in Austria\nQuestion: What is the largest hydrogen project in Austria?\n\n3.Topic: hydrogen project online by years in Austria\nQuestion: How many hydrogen projects are coming online each year in Austria?\n\n4.Topic: Status of Austria\'s hydrogen strategy\nQuestion: What is the current status of Austria\'s hydrogen strategy implementation?\n\n5.Topic: Notable collaborations in the largest Austria\'s hydrogen project\nQuestion: Are there any notable collaborations or partnerships involved in the development of the largest hydrogen project in Austria?\n\n"},
        {"role": "user", "content": "Question: what is Austria\'s hydrogen strategy?\n\n{\"1\": {\"Topic\": \"Austria\'s total planned hydrogen capacity\", \"Question\": \"What is Austria\'s total planned hydrogen capacity?\"}, \"2\": {\"Topic\": \"The largest hydrogen project in Austria\", \"Question\": \"What is the largest hydrogen project in Austria?\"}, \"3\": {\"Topic\": \"hydrogen project online by years in Austria\", \"Question\": \"How many hydrogen projects are coming online each year in Austria?\"}, \"4\": {\"Topic\": \"Status of Austria\'s hydrogen strategy\", \"Question\": \"What is the current status of Austria\'s hydrogen strategy implementation?\"}, \"5\": {\"Topic\": \"Notable collaborations in the largest Austria\'s hydrogen project\", \"Question\": \"Are there any notable collaborations or partnerships involved in the development of the largest hydrogen project in Austria?\"}}"},
    
    ]


    def __init__(self, openai_api_key, datastore_api_key, datastore_env, datastore_index, api_org = "", model = "gpt-3.5-turbo", top_k=10):
        if api_org:
            openai.api_key
        openai.api_key = openai_api_key
        self.model = model
        self.messages_query = self.startMessageStack.copy()
        self.messages_chart = self.startChartingMessageStack.copy()
        self.messages_label = self.startLabelMessageStack.copy()
        self.messages_text = self.startTextSearchStack.copy()
        self.messages_topics = self.startRelatedTopicsStack.copy()

        self.datastore = DataStore(datastore_api_key, datastore_env, datastore_index, top_k)


    def generate_sql(self, message, sender):
        logging.debug('Mesages sent to OpenAI:')
        logging.debug(message)
        if (sender):
            message = json.dumps({'message':message, 'sender':sender})
        self.messages_query.append({"role": "user", "content": message})
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages_query
        )
        response = completion.choices[0].message.content 
        logging.debug('Response from OpenAI:')
        logging.debug(response)
        self.messages_query.append({"role": "assistant", "content": response})
        return response

    def reset(self):
        self.messages_query = self.startMessageStack.copy()
        self.messages_chart = self.startChartingMessageStack.copy()
        self.messages_label = self.startLabelMessageStack.copy()
        self.messages_text = self.startTextSearchStack.copy()
        self.messages_topics = self.startRelatedTopicsStack.copy()
        print('model was reset to intial state')

    def generate_chart(self, message):

        self.messages_chart.append(message)
        
        logging.debug('Charting Mesages sent to OpenAI:')
        logging.debug(message)

        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages_chart
        )
        response = completion.choices[0].message.content 

        # replace \n with \\n, so that the output response can be parsed as json
        response = response.replace("\n", "\\n")
  
        logging.debug('Response from OpenAI:')
        logging.debug(response)

        return response

    def generate_label(self, message):
        self.messages_label.append({"role": "user", "content": f"Questions:{message}\nLabel:"})
        logging.debug('Label message to OpenAI')
        logging.debug(message)

        while True:
            completion = openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages_label
            )
            response = completion.choices[0].message.content 

            logging.debug('Reponse Label from OpenAI')
            logging.debug(response)

            if response == 'Text' or response == 'Database':
                self.messages_label.append({"role": "assistant", "content": response})
                return response
            
            # resend request if the response is not one of the two labels
            self.messages_label.append({"role": "user", "content": "Respond with \"Text\" or \"Database\"."})


    

    def summarise_text(self, message):
        logging.debug('Text question to OpenAI')
        logging.debug(message)

        # create embeddings of the question
        response = openai.Embedding.create(
            input=message,
            model="text-embedding-ada-002"
            )
        embeddings = response['data'][0]['embedding']

        # obtain top_k semantic search result based on the question's embedding
        context = self.datastore.query(embeddings)

        logging.debug('Pinecone results')
        logging.debug(context)

        # construct prompt
        message_template = self.messages_text.copy()
        message_template.append({"role": "user", "content": f"Based on the context below, please answer the questions: {message}\n\nContext:{context}\n\n"})
 
        # chain or memorise questions and response, but not the context       
        self.messages_text.append({"role": "user", "content": message})

        completion = openai.ChatCompletion.create(
            model = self.model,
            messages = message_template
        )

        response = completion.choices[0].message.content 
        logging.debug('Response Semantic search from OpenAI')
        logging.debug(response)

        self.messages_text.append({"role": "system", "content": response})

        return response
    

    def generate_topics(self, message):
        logging.debug('Original question submitted')
        logging.debug(message)

        self.messages_topics.append({"role":"user", "content": f"Question: {message}"})
        return self.__send_topics_message()

    def generate_more_topics(self, qty = 5):
        logging.debug('Generate more topics and questions')

        self.messages_topics.append({"role": "user", "content": f"Please give {qty} more topics and questions based on the previous question. Keep the output JSON only."})
        return self.__send_topics_message()


    def __send_topics_message(self):
        completion = openai.ChatCompletion.create(
            model = self.model,
            messages = self.messages_topics
        )

        response = completion.choices[0].message.content 
        logging.debug('Topics response from OpenAI')
        logging.debug(response)

        # return json loads reponse, if errors, ask Chat to re-generate output in json format
        try: 
            response_json = json.loads(response)
            self.messages_topics.append({"role": "assistant", "content": response})
            return response_json
        
        except ValueError:
            self.messages_topics.append({"role": "user", "content": "Please repeat the response but use valid JSON only."})
            self.__send_topics_message()
        


    
