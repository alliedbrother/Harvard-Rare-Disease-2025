import os

structure = {
    "genomic-diagnostics-app": {
        ".": ["app.py", "models.py", "phrank_pipeline.py", "orphanet_parser.py", "real_clinphen.py", "requirements.txt"],
        "logs": {
            ".": ["app.log"]
        },
        "data": {
            ".": ["en_product6.xml", "hp.obo", "disease_data.json"]
        },
        "templates": {
            ".": ["base.html", "index.html", "login.html", "register.html", "results.html", "history.html"]
        },
        "static": {
            ".": ["style.css"]
        }
    }
}

def create_structure(base_path, structure):
    """
    Recursively creates the specified directory structure with files.
    """
    for folder, content in structure.items():
        path = os.path.join(base_path, folder)
        os.makedirs(path, exist_ok=True)  # Create the folder if it doesn't exist
        
        if isinstance(content, dict):  # If content is a dictionary, process nested structures
            create_structure(path, content)
        elif isinstance(content, list):  # If content is a list, create files
            for file in content:
                with open(os.path.join(path, file), "w") as f:
                    f.write("")  # Create an empty file

# Execute the function to create the structure in the current directory
create_structure(".", structure)

print("Project structure created successfully!")
