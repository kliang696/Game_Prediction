import logging
import os
import pathlib

from config import PROJECT_ID, SECRET_ID
from utils import (
    get_api_key_from_secret_manager,
    get_leaderboard_urls,
    get_player_ids,
    get_puuids,
    get_match_ids,
    get_game_info,
    get_tier_rank_info
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
    rank_info_df = get_tier_rank_info(api_key, game_info_df)
    logger.info("Saving data...")
    out_dir = pathlib.Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)
    game_info_df.to_csv("out/game_info.csv", index=False)
    rank_info_df.to_csv("out/rank_info.csv", index=False)
    logger.info("Done!")
