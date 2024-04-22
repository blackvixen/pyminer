from pathlib import Path
from typing import Final
from decouple import config

from minecoequity.utils.logger import LOGGER

env = config

TOKEN: Final = env('TOKEN')
REDIS_URL: Final = env('REDIS_URL', default="redis://:6a30851e71dc192e854a841bab63053a4297fb31c6569a1f11c76d0f7fd0c865@dokku-redis-mincorequit-rd:6379")
USERNAME: Final = env('USERNAME')
DEVELOPER_CHAT_ID: Final = env('DEVELOPER_CHAT_ID')
COINBASE_API: Final = env('COINBASE_API')
COINBASE_SK: Final = env('COINBASE_SK')
INFURA_HTTP_URL: Final = env('INFURA_HTTP_URL')
INFURA_WS_URL: Final = env('INFURA_WS_URL')
