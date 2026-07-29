import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Cid77B@99",
    database="votingsystem"
)

cursor = db.cursor(dictionary=True)