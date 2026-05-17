# Litmol

Litmol is a molecular search program. Currently, it contains the PubChemClient class, which wraps the [PUG REST API of PubChem](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest#section=Structure-Search-Operations) for structure searches. PubChemClient contains two core functions: `search_similar` and `search_substructure`. 

## Installation
Use the package installer pip to install Litmol. 
```bash
pip install git+https://github.com/ansonzhang2009/litmol.git
```

## Jupyter Notebook Demo
A Jupyter Notebook demonstration can be found at [`demo.ipynb`](https://github.com/AnsonZhang2009/litmol/blob/main/playground/demo.ipynb). 
