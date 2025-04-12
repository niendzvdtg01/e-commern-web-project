from time import time
from datetime import datetime
import json, hmac, hashlib, urllib.request, urllib.parse, random

config = {
  "app_id": 2554,
  "key1": "sdngKKJmqEMzvh5QQcdD2A9XBSKUNaYn",
  "key2": "trMrHtvjo6myautxDUiAcYsVtaeQ8nhf",
  "endpoint": "https://sb-openapi.zalopay.vn/v2/create"
}
transID = random.randrange(1000000)
print(random.randrange(1000000))
order = {
  "app_id": config["app_id"],
  "app_trans_id": "{:%y%m%d}_{}".format(datetime.today(), transID), # mã giao dich có định dạng yyMMdd_xxxx
  "app_user": "user123",
  "app_time": int(round(time() * 1000)), # miliseconds
  "embed_data": json.dumps({}),
  "item": json.dumps([{}]),
  "amount": 50000,
  "description": "Payment for the order #"+str(transID),
  "bank_code": "zalopayapp"
}

# app_id|app_trans_id|app_user|amount|apptime|embed_data|item
data = "{}|{}|{}|{}|{}|{}|{}".format(order["app_id"], order["app_trans_id"], order["app_user"], 
order["amount"], order["app_time"], order["embed_data"], order["item"])

order["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

response = urllib.request.urlopen(url=config["endpoint"], data=urllib.parse.urlencode(order).encode())
result = json.loads(response.read())

for k, v in result.items():
  print("{}: {}".format(k, v))

# Merchant Server gửi request đến ZaloPay Server để lấy thông tin trạng thái thanh toán của giao dịch.
params = {
  "app_id": config["app_id"],
  "app_trans_id": "<app_trans_id>"  # Input your app_trans_id"
}

data = "{}|{}|{}".format(config["app_id"], params["app_trans_id"], config["key1"]) # app_id|app_trans_id|key1
params["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

response = urllib.request.urlopen(url=config["endpoint"], data=urllib.parse.urlencode(params).encode())
result = json.loads(response.read())

for k, v in result.items():
  print("{}: {}".format(k, v))

# Xử lý callback từ ZaloPay Server
# Merchant Server nhận callback từ ZaloPay Server để cập nhật trạng thái thanh toán cho đơn hàng.
from flask import Flask, request, json, jsonify, render_template # pip3 install Flask 
import hmac, hashlib

app = Flask(__name__)

@app.route('/create-payment', methods=['POST'])
def create_payment():
    try:
        # Get cart data from request
        cart_data = request.json
        total_amount = cart_data.get('total_amount', 0)
        items = cart_data.get('items', [])
        
        # Generate a unique transaction ID
        transID = random.randrange(1000000)
        
        # Create order data
        order = {
            "app_id": config["app_id"],
            "app_trans_id": "{:%y%m%d}_{}".format(datetime.today(), transID), # mã giao dich có định dạng yyMMdd_xxxx
            "app_user": "user123",
            "app_time": int(round(time() * 1000)), # miliseconds
            "embed_data": json.dumps({}),
            "item": json.dumps(items),
            "amount": total_amount,
            "description": "Payment for the order #"+str(transID),
            "bank_code": "zalopayapp"
        }

        # app_id|app_trans_id|app_user|amount|apptime|embed_data|item
        data = "{}|{}|{}|{}|{}|{}|{}".format(order["app_id"], order["app_trans_id"], order["app_user"], 
        order["amount"], order["app_time"], order["embed_data"], order["item"])

        order["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

        # Send request to ZaloPay
        response = urllib.request.urlopen(url=config["endpoint"], data=urllib.parse.urlencode(order).encode())
        result = json.loads(response.read())
        
        # Return the payment URL to the frontend
        if result.get('return_code') == 1:
            return jsonify({
                'success': True,
                'payment_url': result.get('order_url'),
                'app_trans_id': order["app_trans_id"]
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('return_message', 'Payment creation failed')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/callback', methods=['POST'])
def callback():
  result = {}

  try:
    cbdata = request.json
    mac = hmac.new(config['key2'].encode(), cbdata['data'].encode(), hashlib.sha256).hexdigest()

    # kiểm tra callback hợp lệ (đến từ ZaloPay server)
    if mac != cbdata['mac']:
      # callback không hợp lệ
      result['return_code'] = -1
      result['return_message'] = 'mac not equal'
    else:
      # thanh toán thành công
      # merchant cập nhật trạng thái cho đơn hàng
      dataJson = json.loads(cbdata['data'])
      print("update order's status = success where app_trans_id = " + dataJson['app_trans_id'])

      result['return_code'] = 1
      result['return_message'] = 'success'
  except Exception as e:
    result['return_code'] = 0 # ZaloPay server sẽ callback lại (tối đa 3 lần)
    result['error'] = str(e)

  # thông báo kết quả cho ZaloPay server
  return json.jsonify(result)


@app.route('/redirect-from-zalopay', methods=['GET'])
def redirect():
  data = request.args
  checksumData = "{}|{}|{}|{}|{}|{}|{}".format(data.get('appid'), data.get('apptransid'), data.get('pmcid'), data.get('bankcode'), data.get('amount'), data.get('discountamount'), data.get('status'))
  checksum = hmac.new(config['key2'].encode(), checksumData.encode(), hashlib.sha256).hexdigest()

  if checksum != data.get('checksum'):
    return "Bad Request", 400
  else:
    # kiểm tra xem đã nhận được callback hay chưa, nếu chưa thì tiến hành gọi API truy vấn trạng thái thanh toán của đơn hàng để lấy kết quả cuối cùng
    return "Ok", 200

@app.route('/payment-success', methods=['GET'])
def payment_success():
    # Get transaction ID from query parameters
    app_trans_id = request.args.get('app_trans_id')
    
    # Query payment status
    params = {
        "app_id": config["app_id"],
        "app_trans_id": app_trans_id
    }

    data = "{}|{}|{}".format(config["app_id"], params["app_trans_id"], config["key1"]) # app_id|app_trans_id|key1
    params["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

    try:
        response = urllib.request.urlopen(url="https://sb-openapi.zalopay.vn/v2/query", data=urllib.parse.urlencode(params).encode())
        result = json.loads(response.read())
        
        # Render success page with payment details
        return render_template('payment_success.html', 
                              transaction_id=app_trans_id,
                              status=result.get('status', 'unknown'),
                              amount=result.get('amount', 0))
    except Exception as e:
        return render_template('payment_error.html', error=str(e))

@app.route('/payment-error', methods=['GET'])
def payment_error():
    error_message = request.args.get('message', 'Có lỗi xảy ra trong quá trình thanh toán.')
    return render_template('payment_error.html', error=error_message)

if __name__ == '__main__':
  app.run(debug=True, port=5000)