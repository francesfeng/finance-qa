import csv
import logging
import psycopg2
from psycopg2 import sql
import sqlalchemy

from io import StringIO
import os
import shutil

class GoogleCloudSQL:

    FILE_PATH = 'data/data.csv'

    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def connect(self):
        try:
            self.conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
            return True
        except Exception as e:
            return str(e)

    def close(self):
        self.conn.close()

    def execute_query(self, query):
        print(f'\033[94mExecuting Query:{query}\033[0m')
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            if len(result) == 0:
                result = "0 rows returned"
                logging.debug('Query Executing with no results')
                logging.debug(result)
                print(f'\033[96m{result}\033[0m')
                return result

            headers = [column[0] for column in cursor.description]
            output = StringIO()
            csv_writer = csv.writer(output)
            csv_writer.writerow(headers)
            csv_writer.writerows(result)
            result = output.getvalue()

            # save the data from query execution to a csv file
            if os.path.isfile(self.FILE_PATH):
                os.remove(self.FILE_PATH)
            with open(self.FILE_PATH, 'w') as f:
                output.seek(0)
                shutil.copyfileobj(output, f)
            
            logging.debug('Query Executing with results')
            logging.debug(result)

            print(f'\033[96m{result}\033[0m')

            # return the query result in csv string format
            return result
        except Exception as e:
            return str(e)

    def process_table_string(self, input_str):
        items = input_str.split(',')
        items = [item.split('.')[-1] for item in items]
        formatted_str = "', '".join(items)
        result = f"'{formatted_str}'"
        return result

    def execute_schema(self, table_list):
        queryPart = self.process_table_string(table_list)
        # table_catalog, or table_schema, which one to use to group tables details?
        #return f"SELECT CONCAT(TABLE_SCHEMA, '.', TABLE_NAME, ', ', COLUMN_NAME, ', ', DATA_TYPE) AS 'Table, Column, DataType, Is_Nullable' FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME IN ({queryPart})"
        query = f"""SELECT CONCAT(TABLE_NAME, ', ', COLUMN_NAME, ', ', DATA_TYPE, ', ', IS_NULLABLE) AS "Table, Column, DataType, Is_Nullable" FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME IN ({queryPart})"""
        return self.execute_query(query)
    
    def __save_data_to_csv(self, data):
        # Save data from the query execution to csv file

        if os.path.isfile(self.FILE_PATH):
            os.remove(self.FILE_PATH)
        with open(self.FILE_PATH, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(data)