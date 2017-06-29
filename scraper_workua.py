import time
import re
import random
import requests
import bs4


DOMAIN_NAME = "https://www.work.ua"
START_URL = DOMAIN_NAME + "/jobs/"
START_PAGE = {
    "page": 1,
}

BROWSER_HEADERS = headers = requests.utils.default_headers()
BROWSER_HEADERS.update({
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0'
})


def check_vacancy_url(url: str) -> bool:
    regex = re.compile(r"/jobs/\d+")
    return bool(regex.match(url))


def get_job_id(url: str) -> int:
    regex = re.compile(r"/jobs/(\d+)")
    job_id = regex.findall(url)
    return int(job_id[0])


def find_pages_amount(url: str) -> int or None:
    regex = re.compile(r"/jobs/\?page=(\d+)")
    page = regex.findall(url)
    if page:
        return int(page[0])


def get_pages(soup_object) -> int:
    pages = 0
    for a in soup_object.find_all("a", href=True):
        page = find_pages_amount(a.get("href"))
        if page and page > pages:
            pages = page
    return pages


def get_description(href: str) -> str:
    work_url = DOMAIN_NAME + href
    html = requests.get(
        work_url,
        headers=BROWSER_HEADERS
    ).text
    soup = bs4.BeautifulSoup(html, "html.parser")
    try:
        description = soup.find('div', {'class': 'overflow wordwrap'}).text
    except AttributeError:
        print("No description")
        with open('work_ua_error.txt', 'w+') as file:
            file.write(str(work_url) + " - No description" + "\n")
        return "No description"
    return description.replace(u'\xa0', u' ')


def random_sleep(s=1, e=3):
    time.sleep(random.randint(s, e))


def parse_page(soup) -> dict:
    result = []
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        title = a.get("title")
        if check_vacancy_url(href) and title:
            result.append({
                "description": get_description(href),
                "href": href,
                "title": title,
                "id": get_job_id(href),
                })
    return result


def main():
    print("Parsing STARTED!")
    html = requests.get(
        START_URL,
        params=START_PAGE,
        headers=BROWSER_HEADERS
    ).text
    soup = bs4.BeautifulSoup(html, "html.parser")
    pages = get_pages(soup)
    with open('work_ua2.txt', 'w+') as file:
        for page_num in range(2687, pages+1):
            print("{} of {} pages parsed".format(page_num, pages))
            payload = {
                "page": page_num,
            }
            html = requests.get(
                START_URL,
                params=payload,
                headers=BROWSER_HEADERS
            ).text
            soup = bs4.BeautifulSoup(html, "html.parser")
            for r in parse_page(soup):
                file.write(str(r) + "\n")
    print("Parsing ENDED!")
    return True


def test():
    print("Parsing STARTED!")
    html = requests.get(
        START_URL,
        params=START_PAGE,
        headers=BROWSER_HEADERS
    ).text
    soup = bs4.BeautifulSoup(html, "html.parser")
    pages = get_pages(soup)
    all_list = []
    with open('work_ua.txt', 'w+') as file:
        for page_num in range(1, 2):
            print("{} of {} pages parsed".format(page_num, pages))
            payload = {
                "page": page_num,
            }
            html = requests.get(
                START_URL,
                params=payload,
                headers=BROWSER_HEADERS
            ).text
            soup = bs4.BeautifulSoup(html, "html.parser")
            for r in parse_page(soup):
                all_list.append(r)
                file.write(str(r) + "\n")
            random_sleep()
    print("Parsing ENDED!")
    return True


if __name__ == "__main__":
    main()
    # test()
