"""
backend/functions.py

In here we have the functions that OPENAI Assistant is expected to use!

"""

from backend import TAVILY_CLIENT

import requests
from bs4 import BeautifulSoup



def tavily_search(query):
    search_result = TAVILY_CLIENT.get_search_context(query, search_depth="advanced", max_tokens=8000)
    print(f"Tavily search result: {search_result}")  # This will show you what you're getting
    return search_result




def pitchfork_review(query):
    base_url = "https://pitchfork.com/search/?query="
    search_url = base_url + '+'.join(query.split())
    response = requests.get(search_url)
    if response.status_code != 200:
        return {"error": "Failed to fetch search results"}

    soup = BeautifulSoup(response.text, 'html.parser')
    review_links = soup.find_all('a', class_='review__link')
    if not review_links:
        return {"error": "No reviews found"}

    # Debugging: Log the found review links
    print("Found review links:", [link['href'] for link in review_links])

    # Iterate over each review link to find the correct one
    for link in review_links:
        review_url = "https://pitchfork.com" + link['href']
        review_response = requests.get(review_url)
        if review_response.status_code != 200:
            continue

        review_soup = BeautifulSoup(review_response.text, 'html.parser')
        review_text_element = review_soup.find('div', class_='review-detail__text')
        review_score_element = review_soup.find('span', class_='score')

        # Debugging: Log the review elements found
        print("Review URL:", review_url)
        print("Review Text Element:", review_text_element)
        print("Review Score Element:", review_score_element)

        if review_text_element and review_score_element:
            review_text = review_text_element.get_text(strip=True)
            review_score = review_score_element.get_text(strip=True)
            return {
                "review_url": review_url,
                "review_text": review_text,
                "review_score": review_score
            }

    return {"error": "No suitable review found"}

    return {"error": "No suitable review found"}
