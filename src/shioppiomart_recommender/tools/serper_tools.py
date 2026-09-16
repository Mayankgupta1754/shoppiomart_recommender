from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from shioppiomart_recommender.tools.http import serper_post


class SerperSearchInput(BaseModel):
    query: str = Field(..., description="Google search query, e.g. trending wireless earbuds India today")


class SerperSearchTool(BaseTool):
    name: str = "serper_web_search"
    description: str = (
        "Search the live web via Serper. Use for trending products, bestsellers, "
        "news, and marketplace roundups. Returns titles, snippets, and links. "
        "Call this once at a time, never in parallel with shopping search."
    )
    args_schema: Type[BaseModel] = SerperSearchInput

    def _run(self, query: str) -> str:
        try:
            data = serper_post(
                "search",
                {"q": query, "num": 10, "gl": "in", "hl": "en", "location": "India"},
            )
        except Exception as exc:
            return f"SEARCH_FAILED: {exc}"
        lines: list[str] = []
        for item in (data.get("organic") or [])[:10]:
            lines.append(
                f"- {item.get('title')}\n  {item.get('snippet')}\n  {item.get('link')}"
            )
        return "\n".join(lines) or "No web results"


class SerperShoppingInput(BaseModel):
    query: str = Field(..., description="Product category to search on Google Shopping India")


class SerperShoppingTool(BaseTool):
    name: str = "serper_shopping_search"
    description: str = (
        "Search Google Shopping India via Serper. Returns product titles, prices, "
        "marketplaces, ratings, and review counts. Call once, then wait before web search."
    )
    args_schema: Type[BaseModel] = SerperShoppingInput

    def _run(self, query: str) -> str:
        try:
            data = serper_post(
                "shopping",
                {"q": query, "num": 20, "gl": "in", "hl": "en", "location": "India"},
            )
        except Exception as exc:
            return f"SHOPPING_FAILED: {exc}"
        lines: list[str] = []
        for item in (data.get("shopping") or [])[:20]:
            lines.append(
                f"- {item.get('title')} | {item.get('price')} | {item.get('source')} | "
                f"{item.get('rating')}★ ({item.get('ratingCount')} reviews)"
            )
        return "\n".join(lines) or "No shopping results"
