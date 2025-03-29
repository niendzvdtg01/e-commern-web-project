from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class Search(FlaskForm):
    username = StringField()

def searchUser(searchtxt):
    if searchtxt != "":
        import pyodbc
        conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=LAPTOP-QTP9VMF9\\SQLEXPRESS; DATABASE=product_list; Trusted_Connection=yes;')
        cursor = conn.cursor()
        sql_command = """
        select * from product_list.dbo.product_name
        where pro_name like ?
        """
        cursor.execute(sql_command, (searchtxt))
        data = cursor.fetchall()
        return data
