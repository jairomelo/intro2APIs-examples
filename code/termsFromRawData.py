import json
import pandas as pd
from itertools import combinations

def create_term_pairs(raw_terms_file: str, processed_terms_file: str) -> pd.DataFrame:
    """
    Simplified method to create term pairs from raw data already downloaded.

    Parameters:
        raw_terms_file (str): Path to the JSON file with raw terms as values and objectIDs as keys
        processed_terms_file (str): Path to the CSV file with processed terms as values and objectIDs as keys
    """
    raw_terms_df = json.load(open(raw_terms_file))

    terms_list = []

    for objectID, terms in raw_terms_df.items():
        if len(terms) > 1:
            pairs = list(combinations(terms, 2))
            for pair in pairs:
                terms_list.append({"Source": pair[0], "Target": pair[1]})
    
    if len(terms_list) > 0:
        df = pd.DataFrame(terms_list)
        if not df.empty:
            df = df.groupby(["Source", "Target"]).size().reset_index(name="Weight")
            df.to_csv(processed_terms_file, index=False)

    return df
    

if __name__ == "__main__":
    create_term_pairs(
        raw_terms_file="data/raw/raw_medieval_art_tags.json",
        processed_terms_file="data/processed/processed_medieval_art_tags_pairs.csv"
    )