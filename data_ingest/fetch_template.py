import json
import requests
import datetime
import os

# load endpoints
with open(os.path.join(os.path.dirname(__file__), '../config/config.json')) as f:
    ENDPOINTS = json.load(f)

def fetch_and_save(name: str):
    url = ENDPOINTS[name]
    resp = requests.get(url)
    resp.raise_for_status()

    # choose extension by content-type
    ctype = resp.headers.get('Content-Type','')
    ext = 'json' if 'application/json' in ctype else 'csv'

    timestamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    folder = os.path.join(os.path.dirname(__file__), '../raw')
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{name}-{timestamp}.{ext}")

    with open(path, 'w', encoding='utf-8') as out:
        if ext == 'json':
            json.dump(resp.json(), out, ensure_ascii=False, indent=2)
        else:
            out.write(resp.text)

    print(f"[{name}] saved to {path}")

if __name__ == '__main__':
    # example: fetch all three
    for key in ENDPOINTS:
        fetch_and_save(key)

