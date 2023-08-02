import psycopg2
from psycopg2 import sql
import sqlalchemy
import os
from io import StringIO
import csv

host = os.environ['NEON_HOST']
database = os.environ['NEON_DATABASE']
user = os.environ['NEON_USER']
password = os.environ['NEON_PASSWORD']

assert host is not None
assert database is not None
assert user is not None
assert password is not None

class Database:

    def __init__(self):
        try:
            self.conn = psycopg2.connect(host=host, database=database, user=user, password=password)
            print("database successfully connected")
        except Exception as e:
            raise f"Error connecting to database: {e}"
        

    def close(self):
        self.conn.close()

    def execute_query(self, query:str, output_headers = True):
        """
        Execute a query and return the result
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()

            # The output is a csv string format
            if output_headers == True:
                headers = [column[0] for column in cursor.description]
                output = StringIO()
                csv_writer = csv.writer(output)
                csv_writer.writerow(headers)
                csv_writer.writerows(result)
                return output.getvalue()  
             
            # The output is a list of tuples, without headers
            else:          
                return result
        except Exception as e:
            raise f"Error executing query: {e}"
        

    def get_table_names(self):
        """
        Get all table names from the database
        """
        tables_names = []
        query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA= 'public'"
        tables =  self.execute_query(query, output_headers=False)
        tables = [i[0] for i in tables]
        return tables
    

    def get_table_columns(self, table_name):
        """
        Get all columns from a table
        """
        query = f"""SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME IN ('{table_name}')"""
        return self.execute_query(query, output_headers=False)
    
    
    def get_values(self, table_name, column_name, data_type):
        """
        Get all values from a column
        distinct values if data type is character varying
        """
        query = ''
        if not column_name.endswith('_id'):
            if column_name != 'project_name' and column_name != 'announced_capacity':
                
                # Return distincting values for character varying columns
                if data_type == 'character varying':
                    query = f"SELECT STRING_AGG(DISTINCT({column_name}),', ') FROM {table_name}"
                    return self.execute_query(query, output_headers=False)
                
        else:
            return None

        
    
    def get_schemas(self):
        """
        Get all schemas from the database
        """
        schemas = ['Table, Column, DataType, Possible Values']
        tables = self.get_table_names()
        for t in tables:
            columns = self.get_table_columns(t)
            for c in columns:
                values = self.get_values(c[0], c[1], c[2])
                if values is not None:
                    schemas.append(', '.join(c) + ', ' + values[0][0])
                else:
                    schemas.append(', '.join(c))

        return '\n'.join(schemas)
    

    def get_schemas_short(self):
        """
        Get all table_names (column1, column2, column3...) in this format
        Used for classification
        """
        tables = self.get_table_names()
        schemas = []
        for t in tables:
            columns = self.execute_query(f"SELECT STRING_AGG(COLUMN_NAME, ', ') FROM  INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME IN ('{t}')", output_headers=False)
            schema = f"{t} ({columns[0][0]})"
            schemas.append(schema)
        return '\n'.join(schemas)