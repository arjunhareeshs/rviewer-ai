import asyncio
import hashlib
import logging
import diskcache as dc
from urllib.parse import urlparse
from typing import Dict, List, Any
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

# Use a local disk cache with a 7-day TTL
cache = dc.Cache("app/data/roadmap_link_cache")
CACHE_TTL = 7 * 24 * 60 * 60  # 7 days in seconds

DOMAIN_PRIORITY = {
    "geeksforgeeks.org":  10,
    "freecodecamp.org":   10,
    "youtube.com":         9,
    "coursera.org":        9,
    "kaggle.com":          8,
    "nptel.ac.in":         8,
    "github.com":          7,
    "medium.com":          6,
    "dev.to":              5,
    "udemy.com":           5,
    "leetcode.com":        8,
    "hackerrank.com":      7,
}

def extract_domain(url: str) -> str:
    try:
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except:
        return ""

def score_result(hit: dict, node_label: str) -> float:
    domain = extract_domain(hit["url"])
    domain_score = DOMAIN_PRIORITY.get(domain, 3)
    
    label_words = set(node_label.lower().split())
    title_words = set(hit["title"].lower().split())
    
    if not label_words:
        return domain_score * 0.6
        
    relevance = len(label_words & title_words) / len(label_words)
    return domain_score * 0.6 + relevance * 10 * 0.4

async def fetch_links_for_node(node_label: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Fetches links using duckduckgo_search across multiple platforms concurrently.
    """
    cache_key = hashlib.md5(node_label.encode()).hexdigest()
    cached = cache.get(cache_key)
    if cached:
        return cached

    queries = {
        "article":  f"{node_label} tutorial site:geeksforgeeks.org OR site:medium.com",
        "video":    f"{node_label} tutorial site:youtube.com",
        "course":   f"{node_label} course site:coursera.org OR site:udemy.com",
        "practice": f"{node_label} site:kaggle.com OR site:leetcode.com",
        "docs":     f"{node_label} official documentation",
        "github":   f"{node_label} example site:github.com",
    }

    results = {}
    
    # Run queries in an executor to avoid blocking the async event loop with DDGS sync calls
    # Wait, duckduckgo_search has AsyncDDGS, let's see if we can use it, or just use DDGS in a thread.
    # DDGS is natively synchronous but often thread-safe enough, or we can use AsyncDDGS if available.
    # We will just run it in a threadpool to be safe.
    
    def run_queries():
        local_results = {}
        try:
            with DDGS() as ddgs:
                for resource_type, query in queries.items():
                    try:
                        # Fetch up to 3 results per type
                        hits = list(ddgs.text(query, max_results=3))
                        if hits:
                            scored_hits = []
                            for h in hits:
                                score = score_result(h, node_label)
                                scored_hits.append({
                                    "title": h.get("title", ""),
                                    "url":   h.get("href", ""),
                                    "snippet": h.get("body", ""),
                                    "score": score
                                })
                            
                            # Sort by score descending and take top 2
                            scored_hits.sort(key=lambda x: x["score"], reverse=True)
                            local_results[resource_type] = [
                                {"title": h["title"], "url": h["url"], "snippet": h["snippet"]}
                                for h in scored_hits[:2]
                            ]
                    except Exception as e:
                        logger.warning(f"Error fetching links for query '{query}': {e}")
                        continue
        except Exception as e:
             logger.error(f"DDGS error: {e}")
        return local_results

    loop = asyncio.get_running_loop()
    results = await loop.run_in_executor(None, run_queries)

    # Cache the results
    cache.set(cache_key, results, expire=CACHE_TTL)
    
    return results

async def attach_links_to_roadmap(roadmap: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes a generated roadmap JSON and attaches live learning links to every node in parallel.
    """
    tasks = []
    node_index = []

    for track in roadmap.get("tracks", []):
        for node in track.get("nodes", []):
            label = node.get("label", "")
            if label:
                tasks.append(fetch_links_for_node(label))
                node_index.append((track["track_id"], node["id"]))

    if not tasks:
        return roadmap

    # Run all node fetches in parallel
    all_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Attach back to the roadmap
    for (track_id, node_id), links in zip(node_index, all_results):
        if isinstance(links, Exception):
            logger.error(f"Failed to fetch links for node {node_id}: {links}")
            links = {}
            
        for track in roadmap.get("tracks", []):
            if track["track_id"] == track_id:
                for node in track.get("nodes", []):
                    if node["id"] == node_id:
                        node["resources"] = links

    return roadmap
