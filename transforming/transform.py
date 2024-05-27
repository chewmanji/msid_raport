from pathlib import Path
import re
import json
from statistics import mean


def save_to_json(data: list, filename: str):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def read_json(filepath: Path) -> list:
    with open(filepath, "r") as file:
        data = json.load(file)
        return data


def remove_unranked_matches(matches: list):
    """
    Remove match if any of team was unranked (rank = -1) at the moment of match
    Saved: 1282 | Removed: 422
    Saved: 941 | Removed: 59
    Saved: 897 | Removed: 103
    Saved: 905 | Removed: 95
    Saved: 509 | Removed: 43
    Saved: 797 | Removed: 203
    Saved: 666 | Removed: 334
    Saved: 931 | Removed: 69
    Saved: 924 | Removed: 76
    """
    saved = []
    for match in matches:
        if not (match["A_rank"] == -1 or match["B_rank"] == -1):
            saved.append(match)

    return saved


def id_to_int(matches: list):
    for match in matches:
        match["id"] = int(match["id"])


def calculate_avg_values(matches: list[dict]):

    res = []
    for game in matches:
        new_entry = {k: v for k, v in game.items() if type(v) is not dict}
        try:
            for k, value in game.items():
                if type(value) is dict:
                    avg_values = {
                        f"AVG_{key}": mean(stat) for key, stat in value.items()
                    }
                    new_entry[k] = avg_values
        except Exception:
            matches.remove(game)

        res.append(new_entry)
    return res


if __name__ == "__main__":
    data_folder = Path("D:\\AI_the_beginning\\raport\\data")
    filename_pattern = r".+_matches\d+_data.json"
    result = []
    for path in data_folder.iterdir():
        regex_match = re.match(filename_pattern, path.name)
        if regex_match:
            matches = read_json(path)
            saved = remove_unranked_matches(matches)
            id_to_int(matches)
            result.extend(calculate_avg_values(matches))

    save_to_json(result, "main_data.json")
