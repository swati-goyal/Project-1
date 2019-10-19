import psycopg2
from psycopg2 import Error
import csv


file = r'/Users/swati/Web-Programming/project1/books.csv'
sql_insert = """INSERT INTO book(isbn,title,author,year) VALUES(%s, %s, %s, %s)"""

try:
    connection = psycopg2.connect(user = "erpjbubameieud",
                                  password = "3647f8b223a70ff28483a6637a32245644df263cb8c24a93ac478ac949d63771",
                                  host = "ec2-54-243-193-59.compute-1.amazonaws.com",
                                  port = "5432",
                                  database = "d9ffrbpg4is8tk")
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