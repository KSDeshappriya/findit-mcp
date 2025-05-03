import httpx
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus  # Import for URL encoding

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
    name="Google Search Tool",
    instructions="Provides a tool to search the web using Google.",
    dependencies=["httpx", "pydantic-settings", "python-dotenv"] # Added python-dotenv
)

# --- API Endpoint ---
# Use the base URL here
GOOGLE_SEARCH_BASE_URL = "https://customsearch.googleapis.com/customsearch/v1"

# --- Search Tool ---
@mcp.tool()
async def google_search(
    query: str = Field(..., description="The search query string."),
    num_results: int = Field(
        default=5, ge=1, le=10, description="Number of search results to return (1-10)."
    )
) -> list[dict[str, str]] | str:
    """
    Performs a web search using Google Programmable Search Engine by constructing the URL manually.
    Returns a list of search results, each containing a title, link, and snippet,
    or an error message string if the search fails.
    """
    # URL-encode the query parameter
    encoded_query = quote_plus(query)

    # Manually construct the full URL
    full_url = (
        f"{GOOGLE_SEARCH_BASE_URL}"
        f"?key={settings.google_api_key}"
        f"&cx={settings.google_cse_id}"
        f"&q={encoded_query}"
        f"&num={num_results}"
    )

    logger.debug(f"Constructed Google Search URL: {full_url}")

    async with httpx.AsyncClient() as client:
        try:
            # Make the GET request using the manually constructed URL
            response = await client.get(full_url, timeout=10)
            response.raise_for_status()  # Raise exception for 4xx/5xx status codes
            data = response.json()
            logger.debug(f"Search response: {data}")
            
            if "items" not in data:
                logger.info(f"No results found for query: '{query}'")
                return "No results found for your query."
                
            results = []
            for item in data["items"]:
                # Extract domain (you'll need to implement extract_domain and is_academic_source functions)
                # For now, just add placeholders
                domain = item.get("displayLink", "unknown")
                
                # Check for file format
                filetype = None
                if 'fileFormat' in item:
                    filetype = item['fileFormat']
                
                results.append({
                    "title": item.get("title", "No title"),
                    "link": item.get("link", "#"),
                    "snippet": item.get("snippet", "No snippet"),
                    "domain": domain,
                    "filetype": filetype
                })
            
            return results

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

# --- Main Execution Block ---
if __name__ == "__main__":
    print("Starting Google Search MCP server...")
    print(f"Using CSE ID: {settings.google_cse_id[:5]}...")
    mcp.run()