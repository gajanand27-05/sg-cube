import requests
import sqlite3

print("---API TEST---")
try:
    print("\n[1] Testing Admin Flow")
    res = requests.post('http://localhost:5000/api/auth_step', json={'email':'admin@sgcube.local'})
    print('Auth Step (Admin):', res.json())
    
    res3 = requests.post('http://localhost:5000/api/login', json={'email':'admin@sgcube.local','password':'admin'})
    print('Login Response (Admin):', res3.json())

    print("\n[2] Testing Normal User Flow")
    res_user = requests.post('http://localhost:5000/api/auth_step', json={'email':'user@sgcube.local'})
    print('Auth Step (User):', res_user.json())
    
    # Get code from DB
    conn = sqlite3.connect('C:/SG/backend/users.db')
    c = conn.cursor()
    c.execute("SELECT verification_code FROM users WHERE email='user@sgcube.local'")
    code = c.fetchone()[0]
    print(f'Retrieved Verification Code: {code}')
    
    res2 = requests.post('http://localhost:5000/api/verify', json={'email':'user@sgcube.local','code':code})
    print('Verify Response (User):', res2.json())

except Exception as e:
    print('Error during test:', e)
