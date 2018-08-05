import sqlite3

def connection():
    con=sqlite3.connect("dab.db")
    c=con.cursor()

    return c,con