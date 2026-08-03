import json
import re
from html import unescape

import requests
from bs4 import BeautifulSoup

URL = "https://www.bbcgoodfood.com/recipes/chicken-chorizo-jambalaya"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def format_duration(duration):
    """
    Convert ISO8601 duration to readable text.

    Examples:
    PT10M    -> 10 mins
    PT1H     -> 1 hr
    PT1H30M  -> 1 hr 30 mins
    PT2H     -> 2 hrs
    """

    if not duration:
        return ""

    hours = 0
    minutes = 0

    h = re.search(r"(\d+)H", duration)
    m = re.search(r"(\d+)M", duration)

    if h:
        hours = int(h.group(1))

    if m:
        minutes = int(m.group(1))

    if hours and minutes:
        return f"{hours} hr{'s' if hours > 1 else ''} {minutes} mins"

    if hours:
        return f"{hours} hr{'s' if hours > 1 else ''}"

    return f"{minutes} mins"


def fetch_recipe(url):

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:

        try:
            data = json.loads(script.string)

            if isinstance(data, dict) and data.get("@type") == "Recipe":

                recipe = {
                    "title": unescape(data.get("name", "")),
                    "description": unescape(data.get("description", "")),
                    "url": data.get("url", ""),
                    "image": data["image"][0]["url"] if data.get("image") else "",
                    "prep_time": format_duration(data.get("prepTime")),
                    "cook_time": format_duration(data.get("cookTime")),
                    "total_time": format_duration(data.get("totalTime")),
                    "serves": str(data.get("recipeYield", "")),
                    "ingredients": data.get("recipeIngredient", [])[:6],
                    "instructions": [
                        step["text"].strip()
                        for step in data.get("recipeInstructions", [])
                    ],
                    "nutrition": data.get("nutrition", {})
                }

                return recipe

        except Exception:
            pass

    return None


def main():

    recipe = fetch_recipe(URL)

    if recipe:
        print(json.dumps(recipe, indent=2))
    else:
        print("Recipe not found.")


if __name__ == "__main__":
    main()
