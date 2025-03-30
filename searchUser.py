from flask import jsonify
import pyodbc

def searchUser(searchtxt):
    if not searchtxt:  # Nếu không có input, trả về danh sách rỗng
        return jsonify([])

    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server}; SERVER=LAPTOP-QTP9VMF9\\SQLEXPRESS; DATABASE=product_list; Trusted_Connection=yes;'
        )
        cursor = conn.cursor()

        sql_command = """
        SELECT * FROM product_list.dbo.product_name
        WHERE pro_name LIKE ?
        """
        cursor.execute(sql_command, ('%' + searchtxt + '%',))
        rows = cursor.fetchall()
        conn.close()

        return jsonify([list(row) for row in rows])  # Trả về JSON danh sách

    except Exception as e:
        return jsonify({"error": str(e)})  # Debug lỗi nếu có

