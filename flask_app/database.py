from time import sleep, time
from threading import Thread
from flask_app.config import *
import os
import pymysql.cursors

class database:

    def __init__(self):
        self.connections = {} 
        self.dict_connection = None       

    def connection_is_alive(self, connection):
        try:
            while True:
                start_time = self.connections.get(connection)

                if start_time is not None:
                    now_time = time()
                    if now_time - start_time >= 60:
                        self.connections.pop(connection)
                        connection.close()
                        return
                    sleep(60 - (now_time - start_time)+ 1)
                else:
                    sleep(1)
        except Exception as e:
            print("Exception in Thread of connection", e)
            self.connections.pop(connection)
            connection.close()

    def get_connection(self):
        while True:
            try:
                if self.connections:
                    con = list(self.connections.keys())
                    connection = con.pop()
                    self.connections.pop(connection)
                    return connection
                else:
                    # Connection to the database
                    database_endpoint = {
                        "host": os.getenv("HOST"),
                        "port": int(os.getenv("PORT")),
                        "database":os.getenv("DATABASE"),
                        "user":os.getenv("USER_NAME"),
                        "password":os.getenv("PASSWORD"),
                        'autocommit':True
                    }
                    database_endpoint['cursorclass']= pymysql.cursors.DictCursor
                    connection = pymysql.connect(**database_endpoint)
                    Thread(target = self.connection_is_alive, args=(connection,)).start()

                    return connection
            except Exception as e:
                print("Connection Error : ", e)
                sleep(1)

    def execute_query(self, query):
        connection = self.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(query)
            data = cursor.fetchall()
        
        except Exception as e:
            data = None
            print("Exception while executing", e)

        self.connections[connection] = time()
        return data

connection = database()