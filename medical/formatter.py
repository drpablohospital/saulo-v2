"""Medical evidence formatter for Langosta-style summaries."""
from typing import Dict, Any, List


class MedicalFormatter:
    """Format medical evidence in Langosta style."""
    
    async def format_summary(self, search_results: Dict[str, Any]) -> str:
        """Format search results as Langosta-style summary."""
        
        results = search_results.get("results", [])
        total = search_results.get("total", 0)
        
        if not results:
            return f"""🔍 **Resumen de Evidencia Médica**

**Consulta:** {search_results.get('query', 'Desconocida')}

⚠️ **No se encontraron resultados** en PubMed para esta búsqueda.

**Sugerencias:**
- Prueba con términos más generales
- Verifica la ortografía de los medicamentos o condiciones
- Usa términos en inglés si es necesario

---
*Fuente: PubMed | Generado por Saulo v2*"""
        
        summary = f"""🔍 **Resumen de Evidencia Médica**

**Consulta:** {search_results.get('query', 'Desconocida')}
**Resultados:** {total} artículos encontrados

---

"""
        
        # Group by study type priority
        priority_order = ["Meta-análisis", "Revisión sistemática", "ECA", "Estudio de cohorte", "Caso-control", "Otro"]
        grouped = {t: [] for t in priority_order}
        
        for article in results:
            study_type = article.get("study_type", "Otro")
            if study_type in grouped:
                grouped[study_type].append(article)
        
        # Add top results by priority
        for study_type in priority_order:
            articles = grouped[study_type]
            if articles:
                summary += f"**{study_type}** ({len(articles)} artículos)\n\n"
                
                for i, article in enumerate(articles[:3], 1):  # Top 3 per type
                    summary += self._format_article_summary(article, i)
                    summary += "\n"
        
        summary += f"""
---

**Notas:**
- ✅ Prioridad: Meta-análisis > ECA > Estudios observacionales
- 🔗 Ver todos: {search_results.get('pubmed_url', 'https://pubmed.ncbi.nlm.nih.gov')}

*Fuente: PubMed (últimos 30 días, excluye pediatría) | Generado por Saulo v2*"""
        
        return summary
    
    def _format_article_summary(self, article: Dict, index: int) -> str:
        """Format single article summary."""
        return f"""{index}. **{article.get('title', 'Sin título')}**
   📚 *{article.get('journal', 'Revista desconocida')}* ({article.get('year', 'N/A')})
   👤 {', '.join(article.get('authors', ['Autores no disponibles'])[:2])}
   🔗 [{article.get('pmid', 'N/A')}]({article.get('url', '')})"""


class LangostaMedClient:
    """Client to access Langosta-Med summaries."""
    
    def __init__(self):
        self.workspace_path = "C:/Users/xiute/.openclaw/workspace/langosta/agents/med-pub-monitor/data"
    
    async def get_latest_summaries(self, limit: int = 5) -> List[Dict]:
        """Get latest Langosta-Med summaries."""
        import os
        import json
        from pathlib import Path
        
        summaries = []
        daily_path = Path(self.workspace_path) / "daily"
        
        if not daily_path.exists():
            return []
        
        # Get most recent files
        files = sorted(
            [f for f in daily_path.glob("*.json")],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        for file in files[:limit]:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    summaries.append({
                        "timestamp": data.get("timestamp", ""),
                        "articles_count": len(data.get("articles", [])),
                        "articles": data.get("articles", [])[:3]  # Top 3
                    })
            except:
                continue
        
        return summaries
    
    async def format_for_display(self, summaries: List[Dict]) -> str:
        """Format summaries for Saulo display."""
        if not summaries:
            return "📚 No hay resúmenes recientes de Langosta-Med."
        
        text = "🦞 **Resúmenes Langosta-Med (4 horas)**\n\n"
        
        for summary in summaries[:3]:  # Last 3 updates
            text += f"**Actualización:** {summary.get('timestamp', 'Desconocida')}\n"
            text += f"**Artículos:** {summary.get('articles_count', 0)}\n\n"
            
            for article in summary.get("articles", [])[:3]:
                text += f"• {article.get('title', 'Sin título')}\n"
                text += f"  {article.get('journal', '')} | {article.get('study_type', '')}\n\n"
            
            text += "---\n\n"
        
        return text