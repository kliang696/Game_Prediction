import requests
import pandas as pd
from bs4 import BeautifulSoup
from google.cloud import secretmanager
from config import BASE_URL, MATCH_API_BASE_URL, SUMMONERS_BASE_URL

def get_api_key_from_secret_manager(project_id, secret_id, version_id="latest"):
    """Returns the API key from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def get_leaderboard_urls(max_pages=6):
    """Returns a list of leaderboard URLs."""
    return [BASE_URL + str(i) for i in range(max_pages)]

def get_player_ids(urls):
    """Returns a list of unique player IDs from the given URLs."""
    text_contents = []

    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        span_elements = soup.select('tbody tr td:not([class]) span')
        text_contents.extend(span.text for span in span_elements)

    return list(set(text_contents))

def get_puuids(api_key, ids):
    """Returns a list of PUUIDs for the given player IDs."""
    puuid_list = []

    for player_id in ids:
        try:
            summoner_url = f"{SUMMONERS_BASE_URL}{player_id}?api_key={api_key}"
            get_player_info = requests.get(summoner_url).json()
            puuid = get_player_info['puuid']
            puuid_list.append(puuid)
        except KeyError:
            continue

    return puuid_list

def get_match_ids(api_key, puuids):
    """Returns a list of unique match IDs for the given PUUIDs."""
    match_id_list = []

    for puuid in puuids:
        get_match = f"{MATCH_API_BASE_URL}by-puuid/{puuid}/ids?type=ranked&start=0&count=3&api_key={api_key}"  # noqa: E501
        match_info = requests.get(get_match).json()
        match_id_list.extend(match_info)

    return list(set(match_id_list))

def get_game_info(api_key, match_ids):
    """Returns a DataFrame containing game information for the given match IDs."""
    game_info = []

    for match_id in match_ids[:10]:
        game_info_url = f"{MATCH_API_BASE_URL}{match_id}?api_key={api_key}"
        participants = requests.get(game_info_url).json()
        participants = participants["info"]["participants"]
        game_info.append(pd.DataFrame.from_dict(participants))

    return pd.concat(game_info)