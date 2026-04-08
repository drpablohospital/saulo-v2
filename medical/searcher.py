"""Medical evidence searcher for Saulo v2."""
import httpx
from typing import Dict, Any, List
import os

# PubMed API configuration
PUBMED_API_KEY = "2f199d25c5ed142f894c4f8c8b3dd9bb0d09"
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


class MedicalSearcher:
    """Search for medical evidence on PubMed."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.api_key = PUBMED_API_KEY
    
    async def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search PubMed for medical evidence."""
        
        # Add filters for critical care and exclude pediatrics
        search_term = self._build_search_query(query)
        
        try:
            # Step 1: Search
            search_params = {
                "db": "pubmed",
                "term": search_term,
                "retmax": max_results,
                "retmode": "json",
                "sort": "date",
                "api_key": self.api_key
            }
            
            search_response = await self.client.get(
                f"{PUBMED_BASE_URL}/esearch.fcgi",
                params=search_params
            )
            search_data = search_response.json()
            
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return {
                    "query": query,
                    "results": [],
                    "total": 0,
                    "message": "No se encontraron resultados en PubMed"
                }
            
            # Step 2: Fetch summaries
            summary_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "json",
                "api_key": self.api_key
            }
            
            summary_response = await self.client.get(
                f"{PUBMED_BASE_URL}/esummary.fcgi",
                params=summary_params
            )
            summary_data = summary_response.json()
            
            results = []
            for pmid in id_list:
                article = summary_data.get("result", {}).get(pmid, {})
                if article:
                    results.append(self._format_article(article))
            
            return {
                "query": query,
                "results": results,
                "total": len(results),
                "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/?term={query.replace(' ', '+')}"
            }
            
        except Exception as e:
            return {
                "query": query,
                "results": [],
                "total": 0,
                "error": str(e),
                "message": f"Error en búsqueda: {str(e)}"
            }
    
    def _build_search_query(self, query: str) -> str:
        """Build optimized PubMed query."""
        # Exclude pediatrics
        pediatric_exclusions = "NOT (pediatric OR children OR child OR infant OR neonatal OR newborn OR paediatric OR adolescent)"
        
        # Priority journals
        top_journals = [
            "New England Journal of Medicine",
            "Lancet",
            "JAMA",
            "BMJ",
            "Critical Care Medicine",
            "Intensive Care Medicine",
            "American Journal of Respiratory and Critical Care Medicine",
            "Chest",
            "Critical Care"
        ]
        
        # Build query
        base_query = f"({query}) AND ({pediatric_exclusions})"
        
        return base_query
    
    def _format_article(self, article: Dict) -> Dict[str, Any]:
        """Format article data."""
        authors = article.get("authors", [])
        author_list = [a.get("name", "") for a in authors[:3]]
        if len(authors) > 3:
            author_list.append("et al.")
        
        # Determine study type (simplified)
        title = article.get("title", "").lower()
        study_type = "Otro"
        
        if "meta-analysis" in title or "metaanálisis" in title:
            study_type = "Meta-análisis"
        elif "systematic review" in title or "revisión sistemática" in title:
            study_type = "Revisión sistemática"
        elif "randomized" in title or "trial" in title or "ensayo" in title:
            study_type = "ECA"
        elif "cohort" in title or "cohorte" in title:
            study_type = "Estudio de cohorte"
        elif "case-control" in title or "caso-control" in title:
            study_type = "Caso-control"
        
        return {
            "pmid": article.get("uid"),
            "title": article.get("title", "Sin título"),
            "authors": author_list,
            "journal": article.get("fulljournalname", article.get("source", "")),
            "year": article.get("pubdate", "")[:4] if article.get("pubdate") else "",
            "doi": article.get("elocationid", ""),
            "study_type": study_type,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{article.get('uid')}/"
        }