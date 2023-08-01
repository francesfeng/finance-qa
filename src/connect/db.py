import psycopg2
from psycopg2 import sql
import sqlalchemy
import os

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

    def execute_query(self, query):
        """
        Execute a query and return the result
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            raise f"Error executing query: {e}"
        

    def get_table_names(self):
        """
        Get all table names from the database
        """
        tables_names = []
        query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA= 'public'"
        tables =  self.execute_query(query)
        tables = [i[0] for i in tables]
        return tables
    

    def get_table_columns(self, table_name):
        """
        Get all columns from a table
        """
        query = f"""SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME IN ('{table_name}')"""
        return self.execute_query(query)
    
    
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
                    return self.execute_query(query)
                
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