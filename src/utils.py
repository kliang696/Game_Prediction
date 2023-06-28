import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from google.cloud import secretmanager
from google.cloud import storage
from pathlib import Path
from config import BASE_URL, MATCH_API_BASE_URL, SUMMONERS_BASE_URL, SUMMONERS_TIER_URL
from google.cloud import bigquery

def upload_to_bigquery(
        project_id,
        dataset_id,
        table_id,
        source_uri,
        partition_column,
        partition_date
    ):

    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)
    client.create_dataset(dataset_ref, exists_ok=True)

    table_ref = dataset_ref.table(table_id + "$" + partition_date)

    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        source_format=bigquery.SourceFormat.CSV,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=partition_column,
        ),
    )
    load_job = client.load_table_from_uri(
        source_uri, table_ref, job_config=job_config
    )
    load_job.result()
    print("Loaded {} rows into {}:{}.".format(load_job.output_rows, dataset_id, table_id))


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

    if not urls:
       return []
    
    text_contents = []

    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            span_elements = soup.select('tbody tr td:not([class]) span')
            text_contents.extend(span.text for span in span_elements)
        except Exception as e:
            logging.error(f"Error getting player IDs: {e}")

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
        except Exception as e:
            logging.error(f"Error getting player info: {e}")

    return puuid_list

def get_match_ids(api_key, puuids):
    """Returns a list of unique match IDs for the given PUUIDs."""
    match_id_list = []

    for puuid in puuids:
        get_match = f"{MATCH_API_BASE_URL}by-puuid/{puuid}/ids?type=ranked&start=0&count=3&api_key={api_key}"  # noqa: E501
        try:
            match_info = requests.get(get_match).json()
            if match_info:
                match_id_list.extend(match_info)
        except Exception as e:
            logging.error(f"Error getting match info: {e}")
    return list(set(match_id_list))

def get_game_info(api_key, match_ids, max_games=10):
    """Returns a DataFrame containing game information for the given match IDs."""
    game_info = []

    for match_id in match_ids[:max_games]:
        game_info_url = f"{MATCH_API_BASE_URL}{match_id}?api_key={api_key}"
        try:
            participants = requests.get(game_info_url).json()
            participants = participants["info"]["participants"]
            game_info.append(pd.DataFrame.from_dict(participants))
        except Exception as e:
            logging.error(f"Error getting game info: {e}")
    
    if not game_info:
        return pd.DataFrame()
    return pd.concat(game_info)


def get_tier_rank_info(api_key, game_info_df):
  """Returns a DataFrame containing player rank&Tier&LP information for the given summonerId."""

  if game_info_df.empty:
    return pd.DataFrame()
  
  tier_rank_info_list = []
  for summoner_Id in game_info_df['summonerId'].unique():
    summoner_url= f"{SUMMONERS_TIER_URL}{summoner_Id}?api_key={api_key}"
    get_player_info = requests.get(summoner_url).json()
    tier_rank_info_list.append(get_player_info)
  
  """Only Keep the information with queueType=RANKED_SOLO_5x5 in tier_rank_info_list"""
  filtered_list = []
  #for i in tier_rank_info_list:
   # for j in i:
    #  if j['queueType'] == 'RANKED_SOLO_5x5':
     #   filtered_list.append(j)
  return pd.DataFrame(filtered_list)

def upload_to_cloud_storage(bucket_name: str, file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} does not exist")
    if not file_path.is_file():
        raise FileNotFoundError(f"{file_path} is not a file")
    
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    if not bucket.exists():
        bucket.create()
    
    blob = bucket.blob(file_path.name)
    blob.upload_from_filename(file_path)
