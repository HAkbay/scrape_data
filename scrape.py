from bs4 import BeautifulSoup
from datetime import datetime
import subprocess
import requests
import platform
import random
import time
import os
import gc


def sleep():
    time.sleep(random.uniform(2.0, 5.0))


def open_folder(path):
    system = platform.system()
    if system == "Windows":  # if system is windows
        os.startfile(path)
    elif system == "Darwin":  # if system is mac
        subprocess.Popen(["open", path])
    else:  # if system is linux
        subprocess.Popen(["xdg-open", path])


def fix_url(href):  # this project does not need this function, but it can be very useful.
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
                print(f"Could not delete {file} -> {e}")


def find_quotes():
    tags = "tags: "
    for block in quote_block:
        quote = block.find("span", class_="text")
        author = block.find("small", class_="author")
        tag_list = block.find_all("a", class_="tag")
        for t in tag_list:
            tags += t.text + " "
        quo = quote.text + "\n-" + author.text + "\n" + tags.strip() + "\n\n"
        author_path = os.path.join(folder_path, f"{author.text}")
        file_name = f"quotes_{time_now}.txt"
        write_file(author_path, file_name, quo)
        tags = "tags: "


# folder/file stuff
home_dir = os.path.expanduser("~")
folder_path = os.path.join(home_dir, "Scraped Data", "QuotesToScrape")
os.makedirs(folder_path, exist_ok=True)
open_folder(folder_path)
time_now = datetime.now().strftime("%y%m%d%H%M%S")
scr_website = requests.get("https://quotes.toscrape.com/")
base_url = scr_website.url
soup = BeautifulSoup(scr_website.text, "html.parser")


while True:
    if soup.find("li", class_="next"):
        quote_block = soup.find_all("div", class_="quote")
        find_quotes()
        sleep()
        link = fix_url(soup.find("li", class_="next").find("a").get("href").strip())
        link = requests.get(link)
        soup = BeautifulSoup(link.text, "html.parser")
    else:
        quote_block = soup.find_all("div", class_="quote")
        find_quotes()
        gc.collect()
        print("Done scraping!")
        break
