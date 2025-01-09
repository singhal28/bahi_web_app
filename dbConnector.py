import pymysql.cursors
from sqlalchemy import create_engine

class DbConnector:
    def __init__(self, db):
        connection = pymysql.connect(host = 'svc-e0349c60-67a2-4de5-b41c-459791d68310-dml.aws-virginia-8.svc.singlestore.com',
                                    user = 'admin',
                                    password = 'wEw38SrKIDB2hWbFN6bTfF66JsXVpi6S', 
                                    db = db,
                                    charset = 'utf8mb4',
                                    cursorclass = pymysql.cursors.DictCursor,
                                    autocommit = True)
        self.connection = connection


    def query_db(self, query, data=None):
        with self.connection.cursor() as cursor:
            try:
                query = cursor.mogrify(query, data)
                print("Running Query:", query)
     
                executable = cursor.execute(query, data)
                if query.lower().find("insert") >= 0:
                    # INSERT queries will return the ID NUMBER of the row inserted
                    self.connection.commit()
                    return cursor.lastrowid
                elif query.lower().find("select") >= 0:
                    # SELECT queries will return the data from the database as a LIST OF DICTIONARIES
                    result = cursor.fetchall()
                    return result
                else:
                    # UPDATE and DELETE queries will return nothing
                    self.connection.commit()
            except Exception as e:
                # if the query fails the method will return FALSE
                print("Something went wrong", e)
                return False
            finally:
                self.connection.close()


def connectToS2MS(db):
    return DbConnector(db)

def db_con(db_is):

# Connection details
    db_user = 'admin'
    db_password = 'wEw38SrKIDB2hWbFN6bTfF66JsXVpi6S'
    db_host = 'svc-e0349c60-67a2-4de5-b41c-459791d68310-dml.aws-virginia-8.svc.singlestore.com'
    db_name = db_is

# Create the database engine
    engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}')

        

    return engine

def get_connection():
    connection = pymysql.connect(host = 'svc-e0349c60-67a2-4de5-b41c-459791d68310-dml.aws-virginia-8.svc.singlestore.com',
                                    user = 'admin',
                                    password = 'wEw38SrKIDB2hWbFN6bTfF66JsXVpi6S', 
                                    db = 'db_web_app',
                                    charset = 'utf8mb4',
                                    cursorclass = pymysql.cursors.DictCursor,
                                    autocommit = True)
    return connection


