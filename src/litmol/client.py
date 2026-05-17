import requests
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional


class PubChemClient:
    """Client for PubChem PUG REST structure search operations."""

    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def _search_cids(self, search_type: str, smiles: str, **params) -> List[int]:
        encoded_smiles = quote(smiles, safe="")
        url = f"{self.BASE_URL}/compound/{search_type}/smiles/{encoded_smiles}/cids/JSON"
        response = self.session.get(url, params=params, timeout=self.timeout)

        if response.status_code == 404:
            return []

        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            return []

        id_list = data.get("IdentifierList", {})
        cids = id_list.get("CID", [])
        if isinstance(cids, int):
            cids = [cids]
        return cids

    def _cids_to_smiles(self, cids: List[int]) -> List[str]:
        if not cids:
            return []
        cid_str = ",".join(map(str, cids))
        url = f"{self.BASE_URL}/compound/cid/{cid_str}/property/IsomericSMILES/JSON"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            return []

        props = data.get("PropertyTable", {}).get("Properties", [])
        cid_to_smiles = {p["CID"]: p["SMILES"] for p in props}
        return [cid_to_smiles.get(cid, "") for cid in cids]

    def search_similar(
        self, smiles: str, threshold: int = 90, max_records: int = 100
    ) -> List[str]:
        params = {"Threshold": threshold, "MaxRecords": max_records}
        cids = self._search_cids("fastsimilarity_2d", smiles, **params)
        return self._cids_to_smiles(cids)

    def search_substructure(
        self, smiles: str, max_records: int = 100, **kwargs
    ) -> List[str]:
        params = {"MaxRecords": max_records, **kwargs}
        cids = self._search_cids("fastsubstructure", smiles, **params)
        return self._cids_to_smiles(cids)

    def search_similar_batch(
        self,
        smiles_list: List[str],
        threshold: int = 90,
        max_records: int = 100,
        max_workers: int = 5,
    ) -> Dict[str, List[str]]:
        results: Dict[str, List[str]] = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.search_similar, s, threshold, max_records): s
                for s in smiles_list
            }
            for future in as_completed(futures):
                s = futures[future]
                try:
                    results[s] = future.result()
                except Exception:
                    results[s] = []
        return results

    def search_substructure_batch(
        self,
        smiles_list: List[str],
        max_records: int = 100,
        max_workers: int = 5,
        **kwargs,
    ) -> Dict[str, List[str]]:
        results: Dict[str, List[str]] = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.search_substructure, s, max_records, **kwargs): s
                for s in smiles_list
            }
            for future in as_completed(futures):
                s = futures[future]
                try:
                    results[s] = future.result()
                except Exception:
                    results[s] = []
        return results

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
