from collectData import get_terms_pairs

get_terms_pairs(
    collection_endpoint="https://collectionapi.metmuseum.org/public/collection/v1/objects",
    collection_params={"departmentIds": "17"},
    object_endpoint="https://collectionapi.metmuseum.org/public/collection/v1/objects",
    report=True,
    report_file="data/processed/processed_medieval_art_tags_pairs_report.txt",
    save_file="data/processed/processed_medieval_art_tags_pairs.json",
    save_csv="data/processed/processed_medieval_art_tags_pairs.csv",
    verbose=True,
    limit=30
)