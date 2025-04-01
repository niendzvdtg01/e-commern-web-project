def checkuser(user, pasword):
    result = False
    import pyodbc
    conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=LAPTOP-QTP9VMF9\\SQLEXPRESS; DATABASE=webUsername; Trusted_Connection=yes;')
    cursor = conn.cursor()
    sql_command = """
    select * from webUsername.dbo.userSign
    where username = ? and userpassword = ?
    """
    cursor.execute(sql_command, (user, pasword))
    data = cursor.fetchall()
    if len(data) > 0:
        result = True
    return result
