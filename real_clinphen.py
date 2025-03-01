# real_clinphen.py
import subprocess
import tempfile
import logging

logger = logging.getLogger(__name__)

def run_clinphen(text: str):
    """
    Calls the ClinPhen CLI to extract HPO terms from plain text.
    Returns a list of HPO term IDs.
    """
    # If text is very large, handle carefully. We'll do a naive approach here.
    # This function can raise an exception if ClinPhen is not installed or fails.

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_in:
        tmp_in_name = tmp_in.name
        tmp_in.write(text)

    tmp_out_name = tmp_in_name + "_out.txt"

    try:
        cmd = f"clinphen -f {tmp_in_name} -o {tmp_out_name}"
        subprocess.run(cmd, shell=True, check=True)

        # Read output
        with open(tmp_out_name, "r") as f:
            lines = f.readlines()

        hpo_terms = []
        for line in lines:
            line = line.strip()
            if line.startswith("HP:"):
                hpo_terms.append(line)

        return list(set(hpo_terms))

    except subprocess.CalledProcessError as e:
        logger.error(f"ClinPhen command failed: {e}")
        return []
    except Exception as ex:
        logger.exception("Error running ClinPhen.")
        return []
