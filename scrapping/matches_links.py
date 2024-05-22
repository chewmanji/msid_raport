from scrap_utils import *
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", "-p", required=True, help="Filename to save data")
    parser.add_argument(
        "--type",
        "-t",
        default='Lan',
        choices=["Lan", "Online"],
        help="Type of matches",
    )
    parser.add_argument("--offset", "-o", default=0, type=int, help="Starts dowloading from a given number.")
    parser.add_argument("--number", "-n", default=1000, type=int, help="Number of matches to download. Should be multiple of 50")

    args = parser.parse_args()
    create_json_matches_links(args.type, args.path, args.offset, args.number)
