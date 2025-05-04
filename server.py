import httpx
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus  # Import for URL encoding
from typing import List, Optional, Literal
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup

from fastmcp import FastMCP
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__) # Use FastMCP's logger

# --- Configuration ---
class SearchSettings(BaseSettings):
    """Loads settings from environment variables or .env file."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    google_api_key: str = Field(..., description="Google API Key for Custom Search")
    google_cse_id: str = Field(..., description="Programmable Search Engine ID (cx)")

settings = SearchSettings() # type: ignore

# --- MCP Server Setup ---
mcp = FastMCP(
    name="FindIt",
    instructions="Provides tools to search the web using Google and extract content (web scrap) from web pages.",
    dependencies=["httpx", "pydantic-settings", "python-dotenv", "beautifulsoup4"]
)

# --- API Endpoint ---
# Use the base URL here
GOOGLE_SEARCH_BASE_URL = "https://customsearch.googleapis.com/customsearch/v1"

# --- Search Tool ---
@mcp.tool()
async def findIt_google(
    query: str = Field(..., description="The search query string."),
    search_depth: Optional[Literal["basic", "advanced"]] = Field(
        default="basic", description="The depth of the search. 'basic' is faster, 'advanced' is more comprehensive."
    ),
    time_range: Optional[Literal["day", "week", "month", "year"]] = Field(
        default=None, description="Limit results to the specified time range."
    ),
    max_results: int = Field(
        default=5, ge=1, le=10, description="Number of search results to return (1-10)."
    ),
    include_domains: Optional[List[str]] = Field(
        default=None, description="List of domains to specifically include in the search results."
    ),
    exclude_domains: Optional[List[str]] = Field(
        default=None, description="List of domains to specifically exclude from the search results."
    ),
    include_raw_content: bool = Field(
        default=False, description="Include the cleaned and parsed content from top results."
    )
) -> dict | str:
    """
    Performs a web search using Google Programmable Search Engine with enhanced parameters.
    Returns search results with metadata and optionally raw content from top results.
    """
    # URL-encode the query parameter
    encoded_query = quote_plus(query)

    # Build site filtering if specified
    site_filter = ""
    if include_domains:
        site_filter = " OR ".join([f"site:{domain}" for domain in include_domains])
        if site_filter:
            query = f"{query} ({site_filter})"
            encoded_query = quote_plus(query)
    
    # Build exclusion filters
    exclusion_filter = ""
    if exclude_domains:
        exclusion_filter = " ".join([f"-site:{domain}" for domain in exclude_domains])
        if exclusion_filter:
            query = f"{query} {exclusion_filter}"
            encoded_query = quote_plus(query)

    # Add time-based filtering
    date_restrict = ""
    if time_range:
        if time_range == "day":
            date_restrict = "d1"
        elif time_range == "week":
            date_restrict = "w1"
        elif time_range == "month":
            date_restrict = "m1"
        elif time_range == "year":
            date_restrict = "y1"

    # Manually construct the full URL
    full_url = (
        f"{GOOGLE_SEARCH_BASE_URL}"
        f"?key={settings.google_api_key}"
        f"&cx={settings.google_cse_id}"
        f"&q={encoded_query}"
        f"&num={max_results}"
    )
    
    if date_restrict:
        full_url += f"&dateRestrict={date_restrict}"
    
    # Adjust parameters based on search depth
    if search_depth == "advanced":
        full_url += "&safe=off&filter=0"  # Less filtering for comprehensive results

    logger.debug(f"Constructed Google Search URL: {full_url}")

    async with httpx.AsyncClient() as client:
        try:
            # Make the GET request using the manually constructed URL
            response = await client.get(full_url, timeout=15)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Search response received with {len(data.get('items', []))} items")
            
            if "items" not in data:
                logger.info(f"No results found for query: '{query}'")
                return "No results found for your query."
                
            results = []
            for item in data["items"]:
                domain = item.get("displayLink", "unknown")
                
                result_data = {
                    "title": item.get("title", "No title"),
                    "link": item.get("link", "#"),
                    "snippet": item.get("snippet", "No snippet"),
                    "domain": domain,
                    "filetype": item.get('fileFormat', None)
                }
                
                # If requested, extract raw content for top results (limited to first few to avoid slow responses)
                if include_raw_content and len(results) < 3:  # Limit to first 3 to avoid timeouts
                    try:
                        content_response = await client.get(item.get("link"), timeout=10, follow_redirects=True)
                        if content_response.status_code == 200:
                            soup = BeautifulSoup(content_response.text, 'html.parser')
                            # Extract text and remove extra whitespace
                            text = soup.get_text(separator=' ', strip=True)
                            # Normalize whitespace
                            text = re.sub(r'\s+', ' ', text).strip()
                            # Limit text length
                            result_data["raw_content"] = text[:5000] + ("..." if len(text) > 5000 else "")
                    except Exception as e:
                        logger.warning(f"Failed to extract content from {item.get('link')}: {e}")
                        result_data["raw_content"] = "Content extraction failed."
                
                results.append(result_data)
            
            search_result = {
                "query": query,
                "search_depth": search_depth,
                "time_range": time_range,
                "total_results": len(results),
                "results": results
            }
            
            if "searchInformation" in data:
                search_result["estimated_total_results"] = data["searchInformation"].get("totalResults", "unknown")
                search_result["search_time"] = data["searchInformation"].get("searchTime", 0)
            
            return search_result

        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP Error: {e.response.status_code}"
            try:
                error_content = e.response.json()
                error_detail += f" - {error_content.get('error', {}).get('message', e.response.text)}"
            except Exception:
                error_detail += f" - {e.response.text}"
            logger.error(f"Google Search API error: {error_detail} for URL: {full_url}")
            return f"Search failed: {error_detail}"
        except httpx.RequestError as e:
            logger.error(f"Google Search request failed: {e} for URL: {full_url}")
            return f"Search failed: Could not connect to Google Search API ({e.__class__.__name__})."
        except Exception as e:
            logger.error(f"An unexpected error occurred during search: {e}", exc_info=True)
            return f"Search failed: An unexpected error occurred ({e.__class__.__name__})."

@mcp.tool()
async def findIt_scrap(
    urls: List[str] = Field(..., description="List of URLs to extract content from."),
    extract_depth: Literal["basic", "advanced"] = Field(
        default="basic", description="Depth of extraction - basic extracts main content, advanced attempts to get more detailed content."
    ),
    include_images: bool = Field(
        default=False, description="Include a list of images extracted from the URLs in the response."
    )
) -> dict | str:
    """
    Extracts and processes content from specified URLs, supporting in-depth content analysis
    and optional image extraction. Perfect for research and content gathering tasks.
    """
    results = []
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for url in urls:
            try:
                logger.info(f"Extracting content from: {url}")
                response = await client.get(url, timeout=20)
                response.raise_for_status()
                
                # Process the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Basic extraction (text content)
                page_title = soup.title.string if soup.title else "No title found"
                
                # Process main content based on common content containers
                article_tags = soup.find_all(['article', 'main', 'div.content', 'div.post', 'div.article'])
                
                # Default to body if no specific content containers found
                if not article_tags and extract_depth == "advanced":
                    article_tags = [soup.body]
                
                # Extract text
                if article_tags:
                    # Take the largest content container
                    largest_tag = max(article_tags, key=lambda tag: len(str(tag)))
                    content = largest_tag.get_text(separator=' ', strip=True)
                else:
                    # Fallback: get text from body, removing scripts and styles
                    for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                        script.extract()
                    content = soup.body.get_text(separator=' ', strip=True) if soup.body else "No content found"
                
                # Clean up whitespace
                content = re.sub(r'\s+', ' ', content).strip()
                
                # Basic page data
                result = {
                    "url": url,
                    "title": page_title,
                    "content": content[:10000] + ("..." if len(content) > 10000 else ""),
                    "content_type": response.headers.get("content-type", "unknown"),
                    "extraction_depth": extract_depth,
                }
                
                # Extract images if requested
                if include_images:
                    images = []
                    for img in soup.find_all('img'):
                        src = img.get('src')
                        alt = img.get('alt', '')
                        
                        # Skip tiny images, icons, etc.
                        if src and not src.endswith(('ico', 'icon')):
                            # Convert relative URLs to absolute
                            if src.startswith('/'):
                                from urllib.parse import urlparse
                                base_url = "{0.scheme}://{0.netloc}".format(urlparse(url))
                                src = base_url + src
                            
                            images.append({
                                "url": src,
                                "alt_text": alt
                            })
                    
                    # Limit to most relevant images
                    result["images"] = images[:10]
                
                results.append(result)
                
            except httpx.HTTPStatusError as e:
                results.append({
                    "url": url,
                    "error": f"HTTP Error: {e.response.status_code}",
                    "message": "Failed to access the URL"
                })
            except httpx.RequestError as e:
                results.append({
                    "url": url,
                    "error": f"Request Error: {str(e)}",
                    "message": "Network or connection error"
                })
            except Exception as e:
                logger.error(f"Error extracting content from {url}: {e}", exc_info=True)
                results.append({
                    "url": url,
                    "error": f"Extraction Error: {str(e)}",
                    "message": "Failed to process content"
                })
    
    return {
        "extraction_results": results,
        "urls_processed": len(urls),
        "successful_extractions": sum(1 for r in results if "error" not in r)
    }

# --- Main Execution Block ---
if __name__ == "__main__":
    print("Starting Advanced Web Search MCP server...")
    print(f"Using CSE ID: {settings.google_cse_id[:5]}...")
    mcp.run()