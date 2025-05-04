# FindIt - Advanced Web Search MCP

A powerful web search and content extraction tool that provides comprehensive, real-time results using Google's search engine. Returns relevant web content with customizable parameters for result count, content type, time range, and domain filtering. Ideal for gathering current information, news, and detailed web content analysis.

## Installation

### Prerequisites

- Python 3.8 or higher
- `uv` package manager

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/KSDeshappriya/findit-mcp.git
   cd findit-mcp
   ```

2. Install dependencies using `uv`:
   ```bash
   uv pip install fastmcp httpx pydantic-settings python-dotenv beautifulsoup4
   ```

3. Set up Google API credentials:
   - Create a [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
   - Obtain your Google API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Set the environment variables or update the configuration file with your credentials:
     ```cmd
     GOOGLE_API_KEY=your_google_api_key
     GOOGLE_CSE_ID=your_custom_search_engine_id
     ```

4. Configure your MCP client to use FindIt as specified in the Configuration section.


## Configuration

```json
{
  "mcpServers": {
    "FindIt": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "fastmcp",
        "--with",
        "httpx",
        "--with",
        "pydantic-settings",
        "--with",
        "python-dotenv",
        "--with",
        "beautifulsoup4",
        "fastmcp",
        "run",
        "/path/to/server.py"
      ],
      "env": {
        "GOOGLE_API_KEY": "your_google_api",
        "GOOGLE_CSE_ID": "google_cse_id"
      }
    }
  }
}
```

## Tools

### findIt_google

Performs a web search using Google Programmable Search Engine with enhanced parameters.

**Parameters:**
- `query*`: Search query string
- `search_depth`: The depth of the search - 'basic' (faster) or 'advanced' (more comprehensive)
- `time_range`: Limit results to a specific time frame ('day', 'week', 'month', 'year')
- `max_results`: The maximum number of search results to return (1-10)
- `include_domains`: List of domains to specifically include in the search results
- `exclude_domains`: List of domains to specifically exclude from the search results
- `include_raw_content`: Include the cleaned and parsed content from top results (limited to first 3 results)

### findIt_scrap

Extracts and processes content from specified URLs, supporting in-depth content analysis.

**Parameters:**
- `urls*`: List of URLs to extract content from
- `extract_depth`: Depth of extraction - 'basic' or 'advanced'
- `include_images`: Include a list of images extracted from the URLs in the response (limited to 10 per URL)

## Example Prompts

1. **Research with Domain Filtering:**
   - "Search for recent studies on climate change from .edu and .gov domains only and summarize the key findings."

2. **Content Extraction:**
   - "Extract the full content from these three articles about artificial intelligence ethics and create a comparative analysis."

3. **Targeted Research with Time Constraints:**
   - "Find news articles about renewable energy innovations from the past month and extract the most significant breakthroughs."

4. **Competitive Analysis:**
   - "Search for information about Tesla's latest electric vehicles and extract detailed specifications from their official website."

5. **Academic Research:**
   - "Find scientific papers on mRNA vaccines published in the last year, excluding results from news sites."

6. **Technical Documentation:**
   - "Extract the installation instructions from the official documentation pages for TensorFlow, PyTorch, and Keras."

7. **Market Analysis:**
   - "Search for recent financial reports about the semiconductor industry from the past week and extract key market trends."

8. **Image Collection:**
   - "Find websites about sustainable architecture and extract all relevant images with their descriptions."

9. **Product Comparison:**
   - "Search for detailed reviews of the latest MacBook Pro and extract specifications and performance benchmarks."

10. **News Analysis:**
    - "Find articles about the recent tech layoffs from major news sources published this month and extract the main facts."

##### **Bonus Prompt**
   > "Large Concept Model (LCM) : A giant step towards AGI" generate report about that using web search and web scrap


## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0) - see the [LICENSE](https://creativecommons.org/licenses/by-nc/4.0/) file for details.