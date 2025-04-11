from flask import jsonify
import os
from supabase import create_client
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Lấy thông tin kết nối từ biến môi trường
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Kiểm tra nếu thiếu thông tin kết nối
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Thiếu SUPABASE_URL hoặc SUPABASE_KEY trong môi trường!")

# Khởi tạo client Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Hàm tìm kiếm sản phẩm
def searchUser(searchtxt):
    if not searchtxt:
        return jsonify({"error": "Chưa nhập từ khóa tìm kiếm."}), 400

    try:
        print(f"🔍 Đang tìm kiếm: {searchtxt}")  # Debug đầu vào

        # Truy vấn Supabase
        response = (
            supabase.table("products")
            .select("*")
            .ilike("product_name", f"%{searchtxt}%")  # Tìm kiếm không phân biệt hoa thường
            .execute()
        )

        # Debug phản hồi từ Supabase
        print(f"✅ Raw response: {response}")  

        # Supabase trả về một object APIResponse, cần lấy `.data`
        data = response.data  # Thay vì dùng `.get("data")`

        if not data:
            print("❌ Không tìm thấy dữ liệu")
            return jsonify([])

        print(f"✅ Dữ liệu tìm thấy: {data}")
        return jsonify(data)

    except Exception as e:
        print(f"🔥 Lỗi hệ thống: {e}")  # Debug lỗi vào terminal
        return jsonify({"error": "Lỗi máy chủ, vui lòng thử lại sau."}), 500