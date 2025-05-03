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

Here are some example prompts for test this MCP Server:

1. **Research-Based Prompt:**
   - "Find recent studies on the effects of remote work on employee productivity and summarize the key findings."

2. **How-To Guide Prompt:**
   - "Search for step-by-step guides on how to start a vegetable garden and create a comprehensive guide based on the best practices found."

3. **Comparison Prompt:**
   - "Look for articles comparing electric cars and traditional gasoline cars, and generate a summary highlighting the pros and cons of each."

4. **Trend Analysis Prompt:**
   - "Search for the latest trends in digital marketing for 2025 and create a report on the top five strategies businesses are using."

5. **Travel Planning Prompt:**
   - "Find the best travel destinations for solo travelers in 2025 and write a travel itinerary for a week-long trip."

6. **Product Review Prompt:**
   - "Search for reviews of the latest smartphone models released this year and generate a comparison chart of their features and prices."

7. **Historical Context Prompt:**
   - "Look for information on the causes and effects of the Industrial Revolution and create a timeline of key events."

8. **Health and Wellness Prompt:**
   - "Search for the benefits of mindfulness meditation and write an article outlining how to get started with mindfulness practices."

9. **Recipe Development Prompt:**
   - "Find popular recipes for vegan desserts and create a new recipe that combines elements from the top three."

10. **Event Coverage Prompt:**
    - "Search for news articles covering the latest tech conference and summarize the major announcements and innovations presented."
