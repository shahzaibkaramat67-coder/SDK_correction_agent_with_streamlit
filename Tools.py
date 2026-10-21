from bs4 import BeautifulSoup
import requests
from ddgs import DDGS
import json

# from Tools import tool

BAD_DOMAINS = ["linkedin.com", "facebook.com", "instagram.com"]


# --------------------
# FETCH PAGE
# --------------------
def Fetch_page(url: str, emit) -> str:
    try:
        emit("FETCH", f"Fetching URL: {url}")
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        emit("FETCH", "Parsing content...")
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove noise: scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        emit("FETCH", f"Extracted {len(text)} characters")
        return text[:8000]  # cap to avoid overflowing model context

    except Exception as e:
        emit("FETCH", f"Failed to fetch {url}: {e}")
        return ""


# --------------------
# SEARCH
# --------------------
def search(query: str, emit) -> list:
    emit("SEARCH", f"Searching for: {query}")
    content = []
    seen_urls = set()

    with DDGS() as ddgs:
        for doc in ddgs.text(query, max_results=5, timeout=10):
            title = doc["title"]
            url = doc["href"]
            snippet = doc["body"]

            if any(domain in url for domain in BAD_DOMAINS):
                emit("SEARCH", f"Skipping blocked domain: {url}")
                continue
            if url in seen_urls:
                continue

            emit("SEARCH", f"Fetching content: {doc['title']}")
            seen_urls.add(url)
            content.append({"url": url, "title": title, "snippet": snippet})
    return content

# --------------------
# RESEARCH
# --------------------
def research(query: str, sources: list, emit) -> str:
    emit("RESEARCH", f"Starting research: {query}")
    research_result = []
    seen_urls = set()

    if not sources:
        emit("RESEARCH", "No sources found.")
        return "No sources for research found."
    total = len(sources)

    for message in sources:
        if message["role"] != "tool":
            continue
        content = message["content"]
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                continue
        result = content["Tool_Result"]
        for i, item in enumerate(result):
            url = item["url"]
            if not url or url in seen_urls:
                emit("RESEARCH", f"Duplicate skipped: {url}")
                continue
            seen_urls.add(url)
            web_data = Fetch_page(url, emit=emit)
            if not web_data:
                continue

            emit("RESEARCH", f"[{i+1}/{total}] Processing: {item['title']}")

            research_result.append(f"""
Query: {query}
Title: {item["title"]}
URL: {url}

Content:
{web_data}

----------------------------------------
""")

    emit("RESEARCH", "Research completed")
    return "\n".join(research_result)
