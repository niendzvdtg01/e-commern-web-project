from dotenv import load_dotenv
from flask import jsonify
import os
from supabase import create_client
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)
response = (supabase.table("products")
            .select("*")
            .execute())

print("✅ Dữ liệu Supabase trả về:", response)
# Kiểm tra lỗi từ Supabase