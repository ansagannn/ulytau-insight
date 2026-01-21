
import requests

url = "https://t.me/s/ztb_qaz"
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    # Save first 50kb to a file to inspect structure
    with open("telegram_dump.html", "w", encoding="utf-8") as f:
        f.write(response.text[:50000])
    print("Dumped telegram html.")
except Exception as e:
    print(e)
