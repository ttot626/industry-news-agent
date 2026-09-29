"""网页正文抓取工具：从搜索结果链接抓取完整正文，弥补搜索摘要的信息缺失。

搜索工具返回的通常是「标题 + 一两句摘要」，不足以支撑精确回答。本工具让
Agent 在需要时抓取原文，形成「搜索 → 抓取原文 → 综合回答」的链路。
"""

import re
from html import unescape

import httpx
from langchain_core.tools import tool

from app.core.logging import logger

# 抓取正文的最大字符数，避免一次性塞爆上下文窗口
_MAX_CONTENT_CHARS = 5000

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def _html_to_text(html: str) -> str:
    """把 HTML 转成可读纯文本（无第三方依赖的轻量实现）。

    步骤：去掉 script/style/noscript → 块级标签转行 → 去剩余标签 →
    反转义实体 → 压缩空白。

    Args:
        html: 原始 HTML 字符串。

    Returns:
        去除标签后的纯文本。
    """
    html = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?i)<(br|/p|/div|/h[1-6]|/li|/tr|/td)[^>]*>", "\n", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    text = unescape(html)
    text = re.sub(r"[ \t\r]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


@tool
async def fetch_webpage(url: str) -> str:
    """抓取指定网页的正文文本，用于在搜索结果摘要不够时阅读完整内容。

    当搜索只返回标题和简短摘要、无法据此准确回答时，用本工具抓取原文。
    返回去除了 HTML 标签的纯文本，超长内容会被截断。

    Args:
        url: 要抓取的网页完整链接（须以 http:// 或 https:// 开头）。
    """
    if not url.startswith(("http://", "https://")):
        return "错误：url 必须以 http:// 或 https:// 开头。"

    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers={"User-Agent": _USER_AGENT},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.warning("fetch_webpage_http_error", url=url, status=exc.response.status_code)
        return f"抓取失败：HTTP {exc.response.status_code}。"
    except httpx.HTTPError as exc:
        logger.warning("fetch_webpage_network_error", url=url, error=str(exc))
        return f"抓取失败：网络错误（{type(exc).__name__}）。"

    text = _html_to_text(response.text)
    if not text:
        return "抓取到的页面没有可读正文。"

    if len(text) > _MAX_CONTENT_CHARS:
        text = text[:_MAX_CONTENT_CHARS] + "\n…（内容过长已截断）"

    logger.info("fetch_webpage_success", url=url, text_chars=len(text))
    return text
