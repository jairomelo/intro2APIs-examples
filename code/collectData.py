from datetime import datetime, timedelta
from collections import deque
import httpx
import time
import json
from itertools import combinations
import pandas as pd
import os

class RateLimiter:
    def __init__(self, calls_per_second: float = 2.0):
        """
        Parameters:
            calls_per_second (float): Number of API calls allowed per second.
        """
        self.calls_per_second = calls_per_second
        self.minimum_interval = timedelta(seconds=1 / calls_per_second)
        self.calls_made = deque()

    def wait_if_necessary(self):
        """
        Wait to avoid making too many calls too quickly.
        """
        now = datetime.now()

        while self.calls_made and now - self.calls_made[0] > timedelta(seconds=1):
            self.calls_made.popleft()

        if len(self.calls_made) >= self.calls_per_second:
            sleep_time = (self.calls_made[0] + timedelta(seconds=1) - now).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.calls_made.append(now)


def validate_paths(filepaths: list[str]) -> None:
    """
    Validate filepaths.
    """
    for filepath in filepaths:
        get_dir_abspath = os.path.dirname(os.path.abspath(filepath))
        if not os.path.exists(get_dir_abspath):
            user_validation = input(f"Directory {get_dir_abspath} does not exist. Create it? (y/n)")
            if user_validation.lower() == "y":
                os.makedirs(get_dir_abspath, exist_ok=True)
            else:
                raise FileNotFoundError(f"Directory {get_dir_abspath} does not exist.")

def get_api_data(endpoint: str, params: dict | None = None) -> dict:
    """
    Get data from the API.

    Parameters:
        endpoint (str): The endpoint to get data from.
        params (dict, optional): The parameters to pass to the endpoint.

    Returns:
        dict: The data from the API in JSON format.

    Raises:
        Exception: If the HTTP request fails or JSON decoding fails.
    """
    params = params or {}
    
    try:
        response = httpx.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP request failed: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to decode JSON response: {e}")

    
def get_terms_from_endpoint(endpoint: str, objectID: str, return_full_list: bool = False) -> list[str]:
    """
    Get terms from an endpoint.

    Parameters:
        endpoint (str): Base endpoint URL
        objectID (str): Object ID to append to endpoint
        return_full_list (bool): If True, returns full list of terms; if False, returns pairs

    Returns:
        list[str] | list[dict[str, str]]: List of terms or list of term pairs
    """
    try:
        endpoint = f"{endpoint}/{objectID}"
        data = get_api_data(endpoint)
        data = data["tags"]
        terms = [tag["term"] for tag in data]

        if return_full_list:
            return terms
        elif len(terms) > 1:
            pairs = list(combinations(terms, 2))
            return [{"Source": pair[0], "Target": pair[1]} for pair in pairs]
        
    except KeyError as ke:
        print(f"KeyError for objectID {objectID}: {ke}") 
        raise
    except TypeError as te:
        print(f"TypeError for objectID {objectID}: {te}")
        raise


def process_object_terms(object_endpoint: str, objectID: str, return_full_list: bool, verbose: bool) -> tuple[list, bool]:
    """
    Process terms for a single object.
    
    Returns:
        tuple[list, bool]: List of terms and whether processing was successful
    """
    try:
        object_terms = get_terms_from_endpoint(
            object_endpoint, 
            str(objectID), 
            return_full_list
        )
        
        if object_terms:
            if verbose:
                print(f"{objectID} terms: {object_terms}")
            return object_terms, True
        return [], False
    except Exception as e:
        if verbose:
            print(f"Failed to process objectID {objectID}: {e}")
        return [], False
    

def save_results(terms: list, 
                save_csv: str | None, 
                save_file: str | None,
                report: bool,
                report_file: str,
                total_objects: int,
                none_count: int,
                return_full_list: bool) -> None:
    """Save results to CSV, JSON, and/or report file"""
    if save_csv and not return_full_list:
        df = pd.DataFrame(terms)
        if not df.empty:
            df = df.groupby(["Source", "Target"]).size().reset_index(name="Weight")
            df.to_csv(save_csv, index=False)

    if save_file:
        with open(save_file, "w") as f:
            json.dump(terms, f)

    if report:
        report_text = (
            f"Total objects: {total_objects}\n"
            f"Total terms: {len(terms)}\n"
            f"Failed requests: {none_count}"
        )
        with open(report_file, "w") as f:
            f.write(report_text)


def get_object_ids(collection_endpoint: str, 
                  collection_params: dict | None, 
                  limit: int | None) -> list:
    """Get and process object IDs from collection endpoint"""
    collection_params = collection_params or {}
    objectIDs = get_api_data(collection_endpoint, collection_params).get("objectIDs", [])
    
    if limit:
        objectIDs = objectIDs[:limit]
    
    return objectIDs


def get_terms_from_collection(
        collection_endpoint: str, 
        collection_params: dict | None = None, 
        object_endpoint: str | None = None,
        report: bool = False, 
        report_file: str = "report.txt", 
        save_file: str | None = None,
        save_csv: str | None = None,
        verbose: bool = False,
        limit: int | None = None) -> tuple[list[str | dict[str, str]], int]:
    """
    Get terms from a collection.
    """

    validate_paths([save_file, save_csv, report_file])
    if not object_endpoint:
        raise ValueError("object_endpoint must be provided")
    
    rate_limiter = RateLimiter(calls_per_second=2.0)
    objectIDs = get_object_ids(collection_endpoint, collection_params, limit)

    if not objectIDs:
        return [], 0
    
    terms_dict = {}
    none_count = 0

    for objectID in objectIDs:
        rate_limiter.wait_if_necessary()
        object_terms, success = process_object_terms(
            object_endpoint, objectID, return_full_list=True, verbose=verbose
        )

        if success:
            terms_dict[objectID] = object_terms
        else:
            none_count += 1

    save_results(
        terms_dict, save_csv, save_file, report, report_file,
        len(objectIDs), none_count, return_full_list=True
    )

    return terms_dict, none_count

def get_terms_pairs(
        collection_endpoint: str, 
        collection_params: dict | None = None, 
        object_endpoint: str | None = None,
        report: bool = False, 
        report_file: str = "report.txt", 
        save_file: str | None = None,
        save_csv: str | None = None,
        verbose: bool = False,
        return_full_list: bool = False,
        limit: int | None = None) -> tuple[list[str | dict[str, str]], int]:
    """
    Get terms from the API.
    """
    validate_paths([save_file, save_csv, report_file])

    if not object_endpoint:
        raise ValueError("object_endpoint must be provided")
    
    rate_limiter = RateLimiter(calls_per_second=2.0)
    objectIDs = get_object_ids(collection_endpoint, collection_params, limit)
    
    if not objectIDs:
        return [], 0
    
    terms = []
    none_count = 0

    for objectID in objectIDs:
        rate_limiter.wait_if_necessary()
        object_terms, success = process_object_terms(
            object_endpoint, objectID, return_full_list, verbose
        )
        if success:
            terms.extend(object_terms)
        else:
            none_count += 1

    save_results(
        terms, save_csv, save_file, report, report_file,
        len(objectIDs), none_count, return_full_list
    )

    return terms, none_count

if __name__ == "__main__":
    pass