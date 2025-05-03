```json
{
  "mcpServers": {
    "Google Search Tool": {
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
        "fastmcp",
        "run",
        "/path/real/server.py"
      ],
      "env": {
        "GOOGLE_API_KEY": "your_google_api",
        "GOOGLE_CSE_ID": "google_cse_id"
      }
    }
  }
}
```