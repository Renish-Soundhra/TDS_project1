from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json

URL = "https://tds.s-anand.net/#/2025-01/"

def main():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    print("Loading course page...")
    driver.get(URL)
    time.sleep(10)  # wait for JS content to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    sections = soup.find_all("div", class_="markdown-body")

    data = []
    for sec in sections:
        heading = sec.find_previous("h2")
        section_title = heading.get_text(strip=True) if heading else "No Title"
        section_body = sec.get_text(separator="\n").strip()
        data.append({
            "title": section_title,
            "body": section_body
        })

    with open("course_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("✅ course_data.json saved successfully.")

if __name__ == "__main__":
    main()
