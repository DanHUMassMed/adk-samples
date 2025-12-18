from typing import List, Optional, Dict, Any
from connector import SearXNGConnector
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("searxng_search")


@mcp.tool()
async def search(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Search the web using SearXNG.

    Args:
        query: Search query string
        results: Number of results to return (default: 10)
    """
    connector = SearXNGConnector()
    results = await connector.search(query=query, max_results=max_results)
    return results


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
    
