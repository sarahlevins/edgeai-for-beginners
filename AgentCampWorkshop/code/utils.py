import textwrap

import requests
import os
import json

from typing import Annotated
from pydantic import Field


async def stream_response(stream, width=80):
    """Stream a response with word-wrapped output, capturing reasoning and text.

    Args:
        stream: An async iterable of chunks with .contents (e.g. from agent.run(query, stream=True)).
        width: Line width for wrapping (default 80).

    Returns:
        A tuple of (reasoning, text) strings.
    """
    all_reasoning = []
    all_text = []
    line_len = 0

    def print_wrapped(token):
        nonlocal line_len
        for char in token:
            if char == "\n":
                print("", flush=True)
                line_len = 0
            else:
                if line_len >= width and char == " ":
                    print("", flush=True)
                    line_len = 0
                else:
                    print(char, end="", flush=True)
                    line_len += 1

    last_chunk = None
    async for chunk in stream:
        last_chunk = chunk
        for content in chunk.contents:
            if content.type == "text_reasoning":
                token = content.text or ""
                all_reasoning.append(token)
                print_wrapped(token)
            elif content.type == "text":
                token = content.text or ""
                all_text.append(token)
                print_wrapped(token)

    reasoning = "".join(all_reasoning)
    text = "".join(all_text)

    print("\n\n=== FINAL REASONING ===")
    if reasoning:
        print(textwrap.fill(reasoning, width=width))
    else:
        print("(No reasoning)")

    print("\n=== FINAL TEXT ===")
    if text:
        print(text)
    else:
        print("(No text)")

    # Return the stream itself (may have .response or other final state)
    return stream

def web_search(
    query: Annotated[str, Field(description="Search query")],
) -> str:
    """Perform web search using Ollama API."""

    api_key = os.getenv("OLLAMA_API_KEY")
    if not api_key:
        return "Error: OLLAMA_API_KEY environment variable not set"

    url = "https://ollama.com/api/web_search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "query": query
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        raw = json.loads(response.text)
        # Take top 3 results with just title and content snippet
        top_results = [
            {"title": r.get("title", ""), "content": r.get("content", "")[:4000]}
            for r in raw.get("results", [])[:3]
        ]
        result = json.dumps(top_results, indent=2)
        print(result.length)
        return result
    except requests.exceptions.RequestException as e:
        return f"Error fetching web content: {str(e)}"