"""LangGraph tools for enhanced language model capabilities.

This package contains custom tools that can be used with LangGraph to extend
the capabilities of language models. Currently includes tools for web search
and other external integrations.
"""

from langchain_core.tools.base import BaseTool

from .ask_human import ask_human
from .duckduckgo_search import duckduckgo_search_tool
from .fetch_webpage import fetch_webpage

tools: list[BaseTool] = [duckduckgo_search_tool, fetch_webpage, ask_human]
