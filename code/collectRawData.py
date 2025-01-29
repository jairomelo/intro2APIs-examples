from collectData import get_terms_from_collection

get_terms_from_collection(
        collection_endpoint="https://collectionapi.metmuseum.org/public/collection/v1/objects",
        collection_params={"departmentIds": "17"},
        object_endpoint="https://collectionapi.metmuseum.org/public/collection/v1/objects",
        report=True,
        report_file="data/raw/raw_medieval_art_tags_report.txt",
        save_file="data/raw/raw_medieval_art_tags.json",
        verbose=True
    )