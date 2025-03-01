from clinphen import clinphen  

# Example clinical note  
text = "The patient exhibits progressive muscle weakness and difficulty swallowing."  

# Extract phenotype terms  
phenotypes = clinphen.get_phenotypes(text)  

# Output results  
for pheno in phenotypes:
    print(f"HPO Term: {pheno['hpo_term']} - {pheno['name']}")
