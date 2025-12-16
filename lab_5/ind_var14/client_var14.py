import json
import requests
from cryptography.fernet import Fernet

def make_request():
    # Load encryption key (same as server uses)
    try:
        key = open('encryption_key.txt', 'rb').read()
        cipher = Fernet(key)
        # Prepare data to send (as JSON array)
        plaintext_data = [3, 1, 4, 1, 5, 9, 2, 6]  # Можно менять на любые данные
        # Convert to JSON string before encrypting
        json_data = json.dumps(plaintext_data)
        encrypted_data = cipher.encrypt(json_data.encode()).decode()
    except FileNotFoundError:
        print("Error: encryption_key.txt not found. Please generate it first.")
        return
    except Exception as e:
        print(f"Error preparing data: {e}")
        return

    # Prepare request payload
    data = {
        "certificate": open('client_cert.pem', 'r').read(),
        "data": encrypted_data,
        "sort_order": "desc"  # или "asc"
    }

    # Note: Coordinator runs on HTTP (port 8000), so we don't need SSL for coordinator connection
    # SSL/TLS is used between coordinator and backend servers
    try:
        # Make the HTTP request to coordinator
        response = requests.post('http://localhost:8000/api/data', json=data)

        if response.status_code == 200:
            result = response.json()
            print(f"[Client1] Success:")
            print(f"  Original: {result.get('original_data')}")
            print(f"  Sorted ({result.get('sort_order')}): {result.get('sorted_data')}")
        else:
            print(f"[Client1] Error: {response.status_code} - {response.text}")

    except requests.exceptions.SSLError as ssl_error:
        print(f"[Client1] SSL error: {ssl_error}")
    except requests.exceptions.RequestException as req_error:
        print(f"[Client1] Request error: {req_error}")
    except Exception as e:
        print(f"[Client1] Unexpected error: {e}")
