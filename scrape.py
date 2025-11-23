from bs4 import BeautifulSoup
from datetime import datetime
import requests
import os
import gc


def fix_url(href):
    if not href:
        return None
    if href.startswith("https://") or href.startswith("http://"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return base_url.rstrip("/") + href
    return base_url.rstrip("/") + "/" + href


def write_file(fpath, filename, quote):
    os.makedirs(fpath, exist_ok=True)
    file_path = os.path.join(fpath, filename)
    if os.path.isfile(file_path):
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(quote)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(quote)

    file_limit = 5
    files = [
        os.path.join(fpath, f)
        for f in os.listdir(fpath)
        if f.startswith("quotes_") and f.endswith(".txt")
    ]
    if len(files) > file_limit:
        files_sorted = sorted(files, key=os.path.getctime)
        old_file = files_sorted[:-file_limit]
        for file in old_file:
            try:
                os.remove(file)
            except Exception as e:
                print("Could not delete {file} -> {e}")


def find_quotes():
    tags = "tags: "
    for block in quote_block:
        quote = block.find("span", class_="text")
        author = block.find("small", class_="author")
        tag_list = block.find_all("a", class_="tag")
        for t in tag_list:
            tags += t.text + " "
        quo = quote.text + "\n-" + author.text + "\n" + tags.strip() + "\n\n"
        author_path = fr"D:\scrapedData\{author.text}"
        file_name = f"quotes_{time_now}"
        file_name = f"{file_name}.txt"
        write_file(author_path, file_name, quo)

        tags = "tags: "


# folder/file stuff
folder_path = r"D:\scrapedData"
os.makedirs(folder_path, exist_ok=True)
os.startfile(folder_path)
time_now = datetime.now().strftime("%y%m%d%H%M")
scr_website = requests.get("https://quotes.toscrape.com/")
base_url = scr_website.url
soup = BeautifulSoup(scr_website.text, "html.parser")


while True:
    if soup.find("li", class_="next"):
        quote_block = soup.find_all("div", class_="quote")
        find_quotes()
        link = fix_url(soup.find("li", class_="next").find("a").get("href").strip())
        link = requests.get(link)
        soup = BeautifulSoup(link.text, "html.parser")
    else:
        quote_block = soup.find_all("div", class_="quote")
        find_quotes()
        gc.collect()
        break
