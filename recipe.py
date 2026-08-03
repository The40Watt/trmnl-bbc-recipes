import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.bbcgoodfood.com/recipes/chicken-chorizo-jambalaya"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

scripts = soup.find_all("script", type="application/ld+json")

for script in scripts:
    try:
        data = json.loads(script.string)

        if isinstance(data, dict) and data.get("@type") == "Recipe":
            print(json.dumps(data, indent=2))
            break

    except Exception:
        pass
