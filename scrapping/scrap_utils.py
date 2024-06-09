import requests
from bs4 import BeautifulSoup
import json
import random
from time import sleep


PREFIX = "https://www.hltv.org"


def get_random_user_agent():
    return {
        "User-Agent": random.choice(
            [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            ]
        )
    }


def create_json_matches_links(match_type, filename, offset, matches_number, step=50):
    main_dict: dict[str, list[str]] = {}
    STARTING_PAGE_URL = (
        f"https://www.hltv.org/stats/matches?csVersion=CS2&matchType={match_type}"
    )
    i = 1
    for off in range(offset, offset + matches_number, step):
        url = f"{STARTING_PAGE_URL}&offset={off}"
        soup = get_page_soup(url)
        matches_links_list = get_matches_links(soup)
        main_dict[url] = matches_links_list
        print(f"Links downloaded from {url} ({i*step}/{(matches_number//50) * step})")
        i += 1

    save_to_json(main_dict, filename)


def get_matches_links(soup: BeautifulSoup) -> list[str]:
    matches = soup.find_all("td", {"class": "date-col"})
    matches_links = []
    for match in matches:
        matches_links.append(PREFIX + match.a.get("href"))

    return matches_links


def get_page_soup(url: str, max_retries=10) -> BeautifulSoup:
    sleep(random.uniform(0.4123, 1.2136778))  # avoiding being banned by server xd
    retry_count = 0
    while retry_count < max_retries:
        resp = requests.get(url, headers=get_random_user_agent())

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, features="lxml")
            return soup
        else:
            print(
                f"URL: {url}, statuscode = {resp.status_code}. Retrying ({retry_count + 1}/{max_retries})..."
            )
            retry_count += 1
            sleep(random.uniform(5, 15))

    raise Exception(f"Error fetching url: {url} after {max_retries} retries")


def save_to_json(data: dict, filename: str):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
