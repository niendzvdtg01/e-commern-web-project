from flask import jsonify
import psycopg2

def searchUser(searchtxt):
    if not searchtxt:  # Nếu không có input, trả về danh sách rỗng
        return jsonify([])

    try:
        conn = psycopg2.connect("postgresql://postgres:maimoremood123@db.fxmeevciubcbiyqppdln.supabase.co:5432/postgres")
        cursor = conn.cursor()

        sql_command = """
        SELECT * FROM product
        WHERE name LIKE %s
        """
        cursor.execute(sql_command, ('%' + searchtxt + '%',))
        rows = cursor.fetchall()
        conn.close()

        return jsonify([list(row) for row in rows])  # Trả về JSON danh sách

    except Exception as e:
        return jsonify({"error": str(e)})  # Debug lỗi nếu có