# phrank_pipeline.py
import os
from phrank import Phrank

class PhrankPipeline:
    def __init__(self, hpo_file, disease_data):
        """
        disease_data: dict of disease_key -> { 'hpo_terms': [...], 'frequencies': {...} }
        """
        self.phrank = Phrank(hpo_file=hpo_file)
        
        # Convert disease_data into the format Phrank needs
        self.disease_to_phenotypes = {
            disease_key: info["hpo_terms"] for disease_key, info in disease_data.items()
        }
        self.phrank.load_knowledge_base(self.disease_to_phenotypes)

    def rank_diseases(self, patient_hpo_list, threshold=0.2):
        """
        Returns a sorted list of (disease_key, score) and a boolean: is_below_threshold
        """
        results = []
        for disease_key, hpo_list in self.disease_to_phenotypes.items():
            score = self.phrank.score_phenotype_sets(patient_hpo_list, hpo_list)
            results.append((disease_key, score))

        # Sort descending
        results.sort(key=lambda x: x[1], reverse=True)

        if not results:
            # If no diseases at all, treat as rare
            return results, True

        # If top disease is below threshold, consider it "rare/novel"
        top_score = results[0][1]
        return results, (top_score < threshold)
