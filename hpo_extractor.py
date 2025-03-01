# hpo_extractor.py

def load_hpo_terms(file_path):
    """
    Reads hpo_term_names.txt and returns a dictionary mapping phenotype names to HPO IDs.
    """
    hpo_dict = {}  # { "phenotype name": "HP:0001234" }
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split("\t")  # Format: HP:0001234<TAB>Phenotype Name
            if len(parts) == 2:
                hpo_dict[parts[1].lower()] = parts[0]
    return hpo_dict


def load_synonyms(file_path):
    """
    Reads hpo_synonyms.txt and returns a dictionary mapping synonyms to HPO IDs.
    """
    synonym_dict = {}  # { "synonym": "HP:0001234" }
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split("\t")  # Format: Synonym<TAB>HPO_ID
            if len(parts) == 2:
                synonym_dict[parts[0].lower()] = parts[1]
    return synonym_dict


def extract_hpo_terms_from_text(text, hpo_dict, synonym_dict):
    """
    Extracts HPO terms from a given clinical text.
    """
    text = text.lower()
    matched_terms = []

    # Direct phenotype name matches
    for term in hpo_dict:
        if term in text:
            matched_terms.append((hpo_dict[term], term))  # (HPO_ID, Term)

    # Synonym matches
    for synonym in synonym_dict:
        if synonym in text:
            matched_terms.append((synonym_dict[synonym], synonym))  # (HPO_ID, Synonym)

    return matched_terms
