import psycopg2

def add_cart():
    conn = psycopg2.connect("postgresql://postgres:maimoremood123@db.fxmeevciubcbiyqppdln.supabase.co:5432/postgres")
    cursor = conn.cursor()  
