import json
from app.src.chatgpt import ChatGPT
from app.src.google_sql_connector import GoogleCloudSQL
import configparser
import os
import csv
import sys

# Read the config file
# config = configparser.ConfigParser()
# config.read("config.ini")

# # Access the config values
# #driver = config.get("database", "driver")
# host = config.get("database", "host")
# database = config.get("database", "database")
# user = config.get("database", "user")
# password = config.get("database", "password")
# #encrypt = config.get("database", "encrypt")
# openai_api_key = config.get("openai", "api_key")
# openai_org = ''
# openai_model = config.get("openai", "model")


class Controller:

    FILE_PATH = 'data/data.csv'

    def __init__(self):
        # initialise all the things
        
        self.chatModel = ChatGPT(os.environ['OPENAI_API_KEY'], 
                                 os.environ['PINECONE_API_KEY'], 
                                 os.environ['PINECONE_ENVIRONMENT'],
                                 os.environ['PINECONE_INDEX']
                                 )
        self.google_sql = GoogleCloudSQL(os.environ['NEON_HOST'], 
                                         os.environ['NEON_DATABASE'],
                                         os.environ['NEON_USER'],
                                         os.environ['NEON_PASSWORD'])
        self.google_sql.connect()

    def run(self, message):
        label = self.chatModel.generate_label(message)
        match label:
            case "Text":
                response = self.chatModel.summarise_text(message)
                return {'type': 'summary', 'response': response}
            case "Database":
                response_json = self.run_query(message, 'USER')
                match response_json["recipient"]:
                    case "USER":
                        response = response_json["message"]
                        return {'type': 'sentence', 'response': response}
                    case "DATA":
                        response_code = self.run_chart()

                        if 'error' in response_code:
                            return {'type': 'error', 'response': response_code['error'] }
                        else:
                            return {'type': 'chart', 'response': response_code}

                    case _:
                        return {'type': 'error', 'response': response_json['error']}
            case _:
                return {'type': 'error', 'response': 'errors in categorise the question'}

    def run_topics(self, message):
        # calling ChatModel to generate related topics
        return self.chatModel.generate_topics(message)
    
    def run_more_topics(self):
        return self.chatModel.generate_more_topics()
    
    
    def run_query(self, message, sender, counter=0):
        
        # get query from chatModel. Request for json output format when failed to json.loads. Max 3 attemps
        if (counter > 3):
            return {"error": "Too many requests"}
        responseString = self.chatModel.generate_sql(message, sender)
        try:
            response = json.loads(responseString[:-1] if responseString.endswith('.') else responseString)
        except ValueError:
            return self.run_query("Please repeat that answer but use valid JSON only.", "SYSTEM", counter + 1)
        
        # Once pass json.loads, parsing the recipient and action
        match response["recipient"]:
            case "USER": 
                return response  # return format:{'recipient': 'USER', 'message': xxx}
            # further parsing action
            case "SERVER":
                match response["action"]:
                    case "QUERY":
                        result = self.google_sql.execute_query(response["message"])

                        # if output data is more than 2 row (including header), generate chart
                        result_arr = result.strip().split('\n')  # if not remove empty space, will result a empty row

                        if len(result_arr) > 2:
                            return {'recipient': 'DATA', 'message':'The path of the file saved'}
                        
                        # if output data is 1 row, generate text answer
                        else:
                            return self.run_query(result, None, counter + 1)
                        
                    case "SCHEMA":
                        result = self.google_sql.execute_schema(response["message"])
                        return self.run_query(result, None, counter + 1)
                    case _:
                        return {'recipient': 'ERROR', 'message': 'invalid database action'}
            case _:
                return {'recipient': 'ERROR', 'message': 'invalid database recipient'}


    def reset(self):
        self.chatModel.reset()

    def run_chart(self, counter = 0):
        # load sample data from csv file, to generate code for charting
        input_data = self.load_input_data()
        input_message = {"role": "user", "content": "Input data: " + input_data}
                            
        # if the code from the response has execution errors, re-send request
        while True:
            if (counter > 3):
                return {"error": "too many requests to generate chart"}
                                
            response_chart_string = self.chatModel.generate_chart(input_message)

            # clean response text and extract code
            response_chart = json.loads(response_chart_string.replace('```',''))  # removing ```, otherwise cannot json.loads. and remove blocking function plt.show()`
           
            # response_chart = json.loads(response_chart_string.replace('```','').replace('plt.show()',''))  # removing ```, otherwise cannot json.loads. and remove blocking function plt.show()`
            chart_code = response_chart["code"]
                                
            # return code if the charting code generated by Chat Model is valid
            if self.__is_valid_python(chart_code):
                return response_chart
                                
            # if not valid, append the error message, and send to Chat Model to regenerate code
            else:
                err_string = 'There are errors in the code, Please try again'
                #err_string = type(err).__name__ + ': ' + str(err) + '. Please try again.'
                input_message = {"role": "user", "content": err_string}
                counter += 1
                print(err_string)


    def load_input_data(self):
        # Load a sample of input data to string, which will be used to generate code for charting
        data =[]
        data_string = ''
        if os.path.isfile(self.FILE_PATH):
            with open(self.FILE_PATH, 'r') as f:
                input = csv.reader(f)

                # construct each row of data into a string, deliminated by ','    
                for row in input:
                    data.append(','.join(row))

            # join the first 10 rows of data into a string, deliminated by '\n'
            data_string = '\r\n'.join(data[:10])

        return data_string
    

    def __is_valid_python(self, code):
        # execute the code string to check if it is valid
        try:
            exec(code)
        except BaseException:
            return False
        return True 
    
