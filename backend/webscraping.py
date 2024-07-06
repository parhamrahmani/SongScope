"""
backend/webscraping.py

In here we have the functions that OPENAI Assistant is expected to use!

"""

from backend import TAVILY_CLIENT

import requests
from bs4 import BeautifulSoup
import json


def tavily_search(query, limit=5):
    """
    Search for reviews and information about a song or artist on Pitchfork.com.

    :param query:  The song and artist to search for on Pitchfork.com
    :param limit: limit the number of results to return
    :return: the search results
    """
    search_result = TAVILY_CLIENT.get_search_context(
        query,
        search_depth="advanced",
        max_tokens=8000,
        include_domains=["pitchfork.com"],
        exclude_domains=["*"]
    )

    # Parse the string result into a list of dictionaries
    try:
        results = json.loads(search_result)
    except json.JSONDecodeError:
        return [{"content": search_result}]

    # Check if results is a list
    if isinstance(results, list):
        # Filter results to ensure only Pitchfork.com links are returned
        pitchfork_results = [result for result in results if
                             isinstance(result, dict) and "pitchfork.com" in result.get('url', '')]
    else:
        # If it's not a list, wrap it in a list
        pitchfork_results = [results] if isinstance(results, dict) and "pitchfork.com" in results.get('url', '') else []

    # Limit the number of results
    pitchfork_results = pitchfork_results[:limit]

    if pitchfork_results:
        return pitchfork_results
    else:
        return [{"content": "No results found on Pitchfork.com for this query."}]


def pitchfork_review(query):
    """
    Get reviews from Pitchfork for a song or the album of that song.

    :param query: The song and artist to search for.
    :return: the review results
    """
    base_url = "https://pitchfork.com/search/"
    search_url = base_url + '?query=' + '+'.join(query.split())
    response = requests.get(search_url)

    if response.status_code != 200:
        return {"error": "Failed to fetch search results"}

    soup = BeautifulSoup(response.content, 'html.parser')
    album_links = soup.find_all(class_="album-link")

    if not album_links:
        return {"error": "No reviews found"}

    # Use the first album link found
    album_link = album_links[0].get('href')
    review_url = "https://pitchfork.com" + album_link

    page = requests.get(review_url)
    if page.status_code != 200:
        return {"error": "Failed to fetch review page"}

    review_soup = BeautifulSoup(page.content, 'html.parser')

    try:
        score = float(review_soup.find(class_="score").string)
    except AttributeError:
        score = None

    review_paragraphs = review_soup.find_all('p')
    review_text = " ".join([p.text for p in review_paragraphs])

    return {
        "review_url": review_url,
        "review_text": review_text,
        "review_score": score
    }
