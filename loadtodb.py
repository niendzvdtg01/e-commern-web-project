def saveto_db(name ,user, pasword):
    import pyodbc
    conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=LAPTOP-QTP9VMF9\\SQLEXPRESS; DATABASE=webUsername; Trusted_Connection=yes;')
    cursor = conn.cursor()
    sql_command = """
    INSERT INTO webUsername.dbo.userSign (clientnames, username, userpassword)
    VALUES (?, ?, ?)
    """
    cursor.execute(sql_command, (name, user, pasword))
    cursor.commit()
