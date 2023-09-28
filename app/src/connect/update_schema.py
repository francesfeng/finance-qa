import yaml
from connect.db import Database
import os

def main():
    db = Database()
    schemas = db.get_schemas()
    schemas_short = db.get_schemas_short()


    schemas_dict = {
        "schema": schemas,
        "schema_short": schemas_short
    }

    path = './connect/schemas.yaml'
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'w') as file:
        yaml.dump(schemas_dict, file)

if __name__ == "__main__":
    main()
