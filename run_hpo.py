# run_hpo.py

from hpo_extractor import load_hpo_terms, load_synonyms, extract_hpo_terms_from_text

# File paths for HPO data
HPO_FILE = "data/hpo_term_names.txt"
SYNONYM_FILE = "data/hpo_synonyms.txt"

# Load HPO terms and synonyms
hpo_dict = load_hpo_terms(HPO_FILE)
synonym_dict = load_synonyms(SYNONYM_FILE)

# Provide text directly as input
clinical_text = "Severe Headache and seizure, and stomach ache along side nerve pain"

# Extract HPO terms
hpo_matches = extract_hpo_terms_from_text(clinical_text, hpo_dict, synonym_dict)

# Display results
print("\nExtracted HPO Terms:")
for hpo_id, name in hpo_matches:
    print(f"{hpo_id} - {name}")
