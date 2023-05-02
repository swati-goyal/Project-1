import psycopg2
from psycopg2 import Error
import csv


file = r'./books.csv'
sql_insert = """INSERT INTO book(isbn,title,author,year) VALUES(%s, %s, %s, %s)"""

try:
    connection = psycopg2.connect(user = "newuser",
                                  password = "password",
                                  host = "localhost",
                                  port = "5432",
                                  database = "postgres")
    cursor = connection.cursor()
    with open(file,'r')as f:
        data = csv.reader(f,delimiter=',')
        next(data)
        for record in data:
            cursor.execute(sql_insert, record)
            connection.commit()

except (Exception, Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")