from models.decorators import retry_api_request
import requests

@retry_api_request(max_retries=3, delay_seconds=2)
def contact_api_server(payload, url_page):
    """Encapsulates the API request logic with retries."""
    url = f"https://voxmate.longrunner.co.uk/{url_page}"
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()  # Triggers HTTPError for bad status
    return response.json()
