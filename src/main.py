import gzip
import json
import sys
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse
from urllib.request import urlopen

import ijson
from omegaconf import OmegaConf
from tqdm import tqdm

EIN_FILE_PATH = "https://antm-pt-prod-dataz-nogbd-nophi-us-east1.s3.amazonaws.com/anthem/{ein_code}.json"


def get_files_from_index(
    filename: str, location: str = "NY", first_n: int = -1
) -> Dict[str, str]:
    """
    Given a index file and a location, return a list of urls with an EIN code for reference

    args:
        filename: path to the index file
        location: location to filter by
        first_n: number of items in reporting structure to parse

    returns:
        urls_ein_index: dictionary of urls as keys and EIN codes as values
    """

    with gzip.open(filename, "rb") as file:
        # Using ijson to parse the JSON file incrementally
        objects = ijson.items(file, "reporting_structure.item")

        urls_ein_index = {}
        count = 0

        for obj in tqdm(objects, desc="Iterating index file"):
            for file in obj["in_network_files"]:
                full_url = file["location"]
                parsed_url = urlparse(full_url)

                # filter by location
                if parsed_url.path.startswith(f"/anthem/{location}"):
                    if full_url not in urls_ein_index:
                        # get plan id for reference
                        plan_id = None
                        for reporting_plan in obj["reporting_plans"]:
                            if reporting_plan["plan_id_type"] == "EIN":
                                plan_id = reporting_plan["plan_id"]
                                break
                        else:
                            print(obj["reporting_plans"])
                            print(f"Could not find EIN value for {full_url}")
                            continue
                        urls_ein_index[full_url] = plan_id

            if count == first_n:
                break
            count += 1

        return urls_ein_index


def get_inverse_urls_ein_index(urls_ein_index: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Given a dictionary of urls and EIN codes, return a dictionary where the keys are the EIN codes and the values are a list of file paths
    """
    ein_urls_index = {}
    for url, ein_value in tqdm(urls_ein_index.items(), desc="Getting inverse index"):
        if ein_value not in ein_urls_index:
            ein_urls_index[ein_value] = []
        ein_urls_index[ein_value].append(url)

    return ein_urls_index


def get_json(url: str) -> Dict[str, Any]:
    """
    Given a url, return a dictionary of the json file
    """
    with urlopen(url) as file:
        data = json.load(file)
        return data


def get_display_names(ein_urls_index: Dict) -> Dict[str, str]:
    """
    Given a list of EIN values, return a dictionary where the keys are the URLs and the values are the display names
    """
    urls_display_names = {}
    for ein_code, urls in tqdm(
        ein_urls_index.items(), desc="Gathering EIN display names"
    ):
        # get EIN json file
        file_path = EIN_FILE_PATH.format(ein_code=ein_code)
        json_file = get_json(file_path)

        # get diplay names for the urls
        in_network_files = json_file["In-Network Negotiated Rates Files"]
        for file in in_network_files:
            if file["url"] in urls:
                urls_display_names[file["url"]] = file["displayname"]

    return urls_display_names


def main():
    """
    Given a config file, return a list of urls for a given plan type and location

    args:
        sys.argv[1]: path to config file
    """
    config = OmegaConf.load(sys.argv[1])
    input_file = config.input_file
    location = config.location
    first_n = config.first_n
    plan_type = config.plan_type
    output_file = config.output_file
    verbose = config.verbose

    urls_ein_index = get_files_from_index(
        input_file, location=location, first_n=first_n
    )
    if verbose:
        print(json.dumps(urls_ein_index, indent=4))
    ein_urls_index = get_inverse_urls_ein_index(urls_ein_index)
    if verbose:
        print(json.dumps(ein_urls_index, indent=4))

    # get display names to filter by plan type
    urls_display_names = get_display_names(ein_urls_index)

    # filter by plan type
    urls_result = [
        url
        for url, display_name in urls_display_names.items()
        if f"_{plan_type}_" in display_name
    ]
    if verbose:
        print(json.dumps(urls_result, indent=4))

    # save to file
    with open(output_file, "w") as file:
        file.write("\n".join(urls_result))


if __name__ == "__main__":
    """python src/main.py configs/config.yaml"""
    main()
