from bs4 import BeautifulSoup
from scrap_utils import *
import json
import re
import pandas as pd
import io
import argparse
import time


def get_match_data(url: str) -> dict:
    match_id = get_match_id(url)

    soup = get_page_soup(url)
    data = extract_base_match_data(soup)

    data["id"] = match_id
    
    A_rank, B_rank = get_teams_rankings(soup)
    data["A_rank"] = A_rank
    data["B_rank"] = B_rank
    return data


def extract_base_match_data(soup: BeautifulSoup):
    info_box = soup.find("div", {"class": "match-info-box"})
    strings = list(info_box.stripped_strings)
    match_map = strings[3]
    team_A = strings[4]
    team_A_score = int(strings[5])
    team_B = strings[6]
    team_B_score = int(strings[7])

    A_stats, B_stats = get_match_table(soup, team_A, team_B)

    return {
        "map": match_map,
        "team_A": team_A,
        "team_A_score": team_A_score,
        "team_B": team_B,
        "team_B_score": team_B_score,
        "A_stats": A_stats.to_dict(orient="list"),
        "B_stats": B_stats.to_dict(orient="list"),
    }


def get_teams_rankings(soup: BeautifulSoup) -> tuple[int, int]:
    link = soup.find("a", {"class": "match-page-link button"})
    url = PREFIX + link.get("href")

    soup = get_page_soup(url)
    rankings = soup.find_all("div", {"class": "teamRanking"})
    pattern = r"World rank: #(\d+)"
    ranks = [-1, -1]
    for i, rank in enumerate(rankings):
        match = re.match(pattern, rank.text)
        if match:
            ranks[i] = int(match.groups()[0])

    return ranks[0], ranks[1]


def convert_to_decimal(value_str):
    return float(value_str.strip("%"))


def extract_kills_and_hs(value_str):
    parts = value_str.split(" (")
    return int(parts[0]), int(parts[1].strip(")"))


def get_match_table(
    soup: BeautifulSoup, team_A, team_B
) -> tuple[pd.DataFrame, pd.DataFrame]:
    stats = {team_A: None, team_B: None}
    tables = soup.findAll("table", {"class": "stats-table totalstats"})
    for table, team in zip(tables, (team_A, team_B)):
        dataframe = pd.read_html(io.StringIO(str(table)))[0]
        kills_hs = dataframe["K (hs)"].apply(extract_kills_and_hs)
        assists = dataframe["A (f)"].apply(extract_kills_and_hs)
        kast = dataframe["KAST"].apply(convert_to_decimal)
        dataframe["K (hs)"] = [kills[0] for kills in kills_hs.values]
        dataframe["HS"] = [hs[1] for hs in kills_hs.values]
        dataframe["A (f)"] = [assists[0] for assists in assists.values]
        dataframe["KAST"] = [kast for kast in kast.values]
        dataframe = dataframe.rename(columns={"K (hs)": "K", "A (f)": "A"})
        stats[team] = dataframe.drop(columns=[team, "K-D Diff"])

    return stats[team_A], stats[team_B]


def get_match_id(url: str) -> int:
    pattern = r".+/mapstatsid/(\d+)"

    match = re.match(pattern, url)

    if match:
        return match.groups()[0]
    else:
        raise Exception("Id not found!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", "-p", required=True, help="Filename to save data")
    parser.add_argument("--filename", "-f", required=True, help="File with json data")
    args = parser.parse_args()
    start = time.time()
    try:
        counter = 0
        res = []
        with open(args.filename, "r") as file:
            matches: dict = json.loads(file.read())
            for link, matches_list in matches.items():
                for match in matches_list:
                    res.append(get_match_data(match))
                    counter += 1
                    print(f"Matches downloaded: {counter}")

        save_to_json(res, args.path)
        end = time.time()
        print(
            f"It took: {end - start} seconds\nPer 1 match: {(end-start)/counter} seconds"
        )
    except (KeyboardInterrupt, Exception) as error:
        save_to_json(res, args.path)
        print(error)
        print(link, match, sep="\n")
