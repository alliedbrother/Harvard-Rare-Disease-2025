# orphanet_parser.py

import os
import json
from lxml import etree # type: ignore

def parse_orphanet(xml_path):
    """
    Parses an Orphanet XML file (e.g., en_product6.xml) to extract
    disease → HPO annotations.
    
    Returns a dictionary in the format:
    {
      "ORPHA:XXXX | DiseaseName": {
        "hpo_terms": ["HP:000XXXX", "HP:000YYYY", ...],
        "frequencies": {
          "HP:000XXXX": "Occasional",
          "HP:000YYYY": "Very frequent",
          ...
        }
      },
      ...
    }
    """
    # 1. Parse the XML
    tree = etree.parse(xml_path)
    root = tree.getroot()
    
    # The XML uses a particular namespace for Orphadata
    # This namespace can vary if Orphanet changes their schema, so adjust if needed
    ns = {"o": "http://www.orpha.net/od/Orphadata"}
    
    # 2. Initialize a dictionary to hold all disease info
    disease_dict = {}
    
    # 3. Retrieve all <Disorder> elements
    #    The path is typically 'o:DisorderList/o:Disorder' in en_product6.xml
    disorders = root.xpath("o:DisorderList/o:Disorder", namespaces=ns)
    
    for disorder in disorders:
        # a) Get the ORPHA number
        orpha_number_el = disorder.find("o:OrphaNumber", ns)
        if orpha_number_el is not None:
            orpha_number = orpha_number_el.text
        else:
            # If missing, skip or handle
            continue
        
        # b) Get the disorder name
        name_el = disorder.find("o:Name", ns)
        if name_el is not None:
            disease_name = name_el.text
        else:
            disease_name = f"ORPHA:{orpha_number}"
        
        # We'll create a key that includes both the ORPHA number and the name
        disease_key = f"ORPHA:{orpha_number} | {disease_name}"
        
        # c) Prepare lists/dicts for HPO data
        hpo_terms = []
        frequencies = {}  # map HPO ID -> frequency label (e.g., "Very frequent")
        
        # d) Find HPO associations in sub-elements
        assoc_list_path = "o:HPODisorderAssociationList/o:HPODisorderAssociation"
        associations = disorder.xpath(assoc_list_path, namespaces=ns)
        
        for assoc in associations:
            # Each association might have <HPO><HPOId>, <HPOFrequency><Name>, etc.
            hpo_el = assoc.find("o:HPO", ns)
            if hpo_el is not None:
                hpo_id_el = hpo_el.find("o:HPOId", ns)
                if hpo_id_el is not None:
                    hpo_id = hpo_id_el.text  # e.g., "HP:0001156"
                    # Add this to our list of HPO terms
                    hpo_terms.append(hpo_id)
                    
                    # Frequency info
                    freq_el = assoc.find("o:HPOFrequency", ns)
                    if freq_el is not None:
                        freq_name_el = freq_el.find("o:Name", ns)
                        if freq_name_el is not None:
                            freq_label = freq_name_el.text  # e.g., "Very frequent", "Occasional", etc.
                            frequencies[hpo_id] = freq_label
        
        # e) Remove duplicates by converting to a set, then back to list
        unique_hpo_terms = list(set(hpo_terms))
        
        # f) Store everything in the dictionary
        disease_dict[disease_key] = {
            "hpo_terms": unique_hpo_terms,
            "frequencies": frequencies
        }
    
    return disease_dict


def load_orphanet_data(json_path, xml_path):
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError:
            print("WARNING: disease_data.json is invalid. Re-parsing Orphanet XML.")
            # Re-parse from XML if JSON is corrupt
            data = parse_orphanet(xml_path)
            with open(json_path, "w") as f:
                json.dump(data, f, indent=2)
            return data
    else:
        data = parse_orphanet(xml_path)
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        return data



if __name__ == "__main__":
    # Example usage:
    xml_file = os.path.join("data", "en_product6.xml")
    json_file = os.path.join("data", "disease_data.json")
    
    # Parse Orphanet data (if disease_data.json doesn't exist yet, it will be created)
    orphanet_data = load_orphanet_data(json_file, xml_file)
    print(f"Loaded Orphanet data for {len(orphanet_data)} diseases.")
    
    # Print a small sample
    sample_keys = list(orphanet_data.keys())[:5]
    for k in sample_keys:
        print(k, orphanet_data[k])
