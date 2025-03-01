# custom_hpo_extractor.py
import os
import logging
from hpo_extractor import load_hpo_terms, load_synonyms, extract_hpo_terms_from_text

logger = logging.getLogger(__name__)

HPO_TERMS_PATH = os.path.join("data", "hpo_term_names.txt")
HPO_SYNONYMS_PATH = os.path.join("data", "hpo_synonyms.txt")

# Load dictionaries at import time so it's done only once
try:
    hpo_dict = load_hpo_terms(HPO_TERMS_PATH)
    synonym_dict = load_synonyms(HPO_SYNONYMS_PATH)
    logger.info("Loaded HPO terms and synonyms successfully.")
except Exception as e:
    logger.exception("Failed to load HPO data.")
    # Fallback to empty dictionaries if something goes wrong
    hpo_dict = {}
    synonym_dict = {}

def run_custom_extractor(text: str) -> list:
    """
    Uses your custom HPO extraction to get HPO IDs from plain-English input.
    Returns a list of unique HPO IDs.
    """
    try:
        matches = extract_hpo_terms_from_text(text, hpo_dict, synonym_dict)
        # 'matches' is a list of (hpo_id, matched_term)
        # We only need the HPO IDs in a unique set
        hpo_ids = list({m[0] for m in matches})
        return hpo_ids
    except Exception as ex:
        logger.exception("Error extracting HPO terms using custom code.")
        return []
