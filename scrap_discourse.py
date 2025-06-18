from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import requests

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_URL = f"{BASE_URL}/c/courses/tds-kb/34"

def get_topic_links():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--remote-debugging-pipe")  # add this
    driver = webdriver.Chrome(options=options)

    # Load homepage first (important)
    driver.get("https://discourse.onlinedegree.iitm.ac.in")

    # Inject login cookie manually
    driver.add_cookie({
        'name': '_t',
        'value': 'ow7DDDGdohjJ2y5W4LHJzsQXVQITXD%2FN6JsUi4QWA4Rdl97ueVdYQKNRXfdY5PnChuZ%2BtgxUCzPHZyXqorwLwO5ZvSKJmx0O6rRA2R84JTCVSluTHyqwCRLuPCN7J%2BqpZy26XYGQZ24QQyS3uNAlNHQX10OUl0j0P9Mvr9UPHF1hrEab1424QRxLwumdta79Rpu9hrtzECP6fL4ErcrtjH79uPApGOUZf80YrmNP0P5ZkV0Gocy1DI7iYBCzm90ef4hfuF0HJVck6RA84SHaW8Ys%2F%2BodtU7ycUA40WlAXGvc7sM38%2Bn63FHK1hoGAnwy--qy%2Fj8wlahUoi1Rtg--Xrejz4%2Bl0UGtVHyPhTtr8g%3D%3D',
        'domain': 'discourse.onlinedegree.iitm.ac.in',
        'path': '/',
    })


    print("Loading category page...")
    driver.get(CATEGORY_URL)
    time.sleep(10)  # give JS time to run

    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = []
    for a_tag in soup.select("a.title"):
        href = a_tag.get("href")
        if href and href.startswith("/t/"):
            full_url = BASE_URL + href.split("?")[0]
            if full_url not in links:
                links.append(full_url)

    driver.quit()
    return links


def get_topic_content(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    post_divs = soup.select("div.cooked")
    content = " ".join(div.get_text(separator=" ", strip=True) for div in post_divs)
    return {"url": url, "content": content}

def main():
    links = get_topic_links()
    print(f"Found {len(links)} links")

    all_posts = []

    for url in links:
        print(f"Scraping: {url}")
        try:
            headers = {"Cookie": "ow7DDDGdohjJ2y5W4LHJzsQXVQITXD%2FN6JsUi4QWA4Rdl97ueVdYQKNRXfdY5PnChuZ%2BtgxUCzPHZyXqorwLwO5ZvSKJmx0O6rRA2R84JTCVSluTHyqwCRLuPCN7J%2BqpZy26XYGQZ24QQyS3uNAlNHQX10OUl0j0P9Mvr9UPHF1hrEab1424QRxLwumdta79Rpu9hrtzECP6fL4ErcrtjH79uPApGOUZf80YrmNP0P5ZkV0Gocy1DI7iYBCzm90ef4hfuF0HJVck6RA84SHaW8Ys%2F%2BodtU7ycUA40WlAXGvc7sM38%2Bn63FHK1hoGAnwy--qy%2Fj8wlahUoi1Rtg--Xrejz4%2Bl0UGtVHyPhTtr8g%3D%3D"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.string.strip() if soup.title else "No Title"
            body_div = soup.find("div", {"class": "cooked"})
            body = body_div.get_text(separator="\n").strip() if body_div else "No Body"

            all_posts.append({
                "url": url,
                "title": title,
                "body": body
            })

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    # Save all posts to JSON file
    with open("discourse_data.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=4)
