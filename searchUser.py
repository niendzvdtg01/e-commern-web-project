from flask_wtf import Flaskform
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class Search(Flaskform):
    username = StringField()

def searchUser(searchtxt):
    if searchtxt != "":
        import pyodbc
        conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=LAPTOP-QTP9VMF9\\SQLEXPRESS; DATABASE=Bankrate; Trusted_Connection=yes;')
        cursor = conn.cursor()
        sql_command = """
        select * from Bankrate.dbo.bankrate
        where Bank_Name like ?
        """
        cursor.execute(sql_command, (searchtxt))
        data = cursor.fetchall()
        return data
