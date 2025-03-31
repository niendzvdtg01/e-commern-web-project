import pyodbc

def add_cart():
    conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=LAPTOP-QTP9VMF9\\SQLEXPRESS; DATABASE=webUsername; Trusted_Connection=yes;')
    cursor = conn.cursor()  
