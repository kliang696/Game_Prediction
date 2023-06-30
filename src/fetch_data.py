import logging
import os
import pathlib
from pathlib import Path
from datetime import datetime
import time


from config import PROJECT_ID, SECRET_ID
from utils import (
    get_api_key_from_secret_manager,
    get_leaderboard_urls,
    get_player_ids,
    get_puuids,
    get_match_ids,
    get_game_info,
    get_tier_rank_info,
    upload_to_cloud_storage,
    upload_to_bigquery
)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    api_key = os.getenv("RIOT_API_KEY", None)

    if not api_key:
        logger.info("API key not found in environment variables."
                    "Fetching from Secret Manager...")
        api_key = get_api_key_from_secret_manager(PROJECT_ID, SECRET_ID)

    logger.info("Fetching data...")
    logger.info("Getting leaderboard URLs...")
    urls = get_leaderboard_urls(max_pages=1)
    logger.info("Getting player IDs...")
    player_ids = get_player_ids(urls)
    logger.info("Getting PUUIDs...")
    puuids = get_puuids(api_key, player_ids)
    logger.info("Getting match IDs...")
    match_ids = get_match_ids(api_key, puuids)
    logger.info("Getting game info...")
    game_info_df = get_game_info(api_key, match_ids)
    logger.info("Getting player rank info...")
    time.sleep(90)

    now = datetime(2023, 6, 30) # datetime.now()
    
    rank_info_df = get_tier_rank_info(api_key, game_info_df)
    rank_info_df['Date'] = now.strftime('%Y-%m-%d')
    rank_info_df=rank_info_df[["Date","summonerName","summonerId","tier","rank","leaguePoints"]]
    logger.info("Saving data...")
    out_dir = pathlib.Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    game_info_df['Date'] = now.strftime('%Y-%m-%d')
    game_info_df=game_info_df[['Date',"summonerName","championName","individualPosition","goldEarned","kills","deaths","assists","item0","item1","item2","item3","item4","item5","item6","perks","win"]]
    game_info_df.to_csv("out/game_info.csv", index=False)

    rank_info_df.to_csv("out/rank_info.csv", index=False)
    logger.info("Upload data to google cloud storage...")
    upload_to_cloud_storage("daily-game-stats", Path("out/game_info.csv"))
    upload_to_cloud_storage("daily-game-stats", Path("out/rank_info.csv"))

    
    logger.info("Upload data to Big Query...")
    upload_to_bigquery(
        project_id=PROJECT_ID,
        dataset_id="daily_game_stats",
        table_id="game_info_part1",
        source_uri="gs://daily-game-stats/game_info.csv",
        partition_column="Date",
        partition_date=now.strftime("%Y%m%d")
    )
    upload_to_bigquery(
        project_id=PROJECT_ID,
        dataset_id="daily_game_stats",
        table_id="rank_info_part1",
        source_uri="gs://daily-game-stats/rank_info.csv",
        partition_column="Date",
        partition_date=now.strftime("%Y%m%d")
    )
    
    
    logger.info("Done!")
