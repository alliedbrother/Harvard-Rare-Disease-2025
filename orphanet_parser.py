# orphanet_parser.py
import os
import json
from lxml import etree

def parse_orphanet(xml_path):
    # parse the Orphanet file and return a dict of disease -> hpo terms
    # ...
    # (Implementation from previous example)
    pass

def load_orphanet_data(json_path, xml_path):
    if not os.path.exists(json_path):
        # parse from xml
        data = parse_orphanet(xml_path)
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        return data
    else:
        with open(json_path, "r") as f:
            data = json.load(f)
        return data
