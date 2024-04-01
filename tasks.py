import random
import time
from celery import Celery
from minecoequity.utils.load_env import REDIS_URL, TOKEN
from telegram import Bot
from asgiref.sync import async_to_sync
from minecoequity.utils.logger import LOGGER


app = Celery("tasks", broker=f"{REDIS_URL}")


async def run_mining(user_id, task_id, tries=0):
    from minecoequity.utils.utils import MiningScript
    from minecoequity.utils.load_data import UserData

    """
    Celery task to start mining for a user.

    Args:
        user_id (str): The user ID to start mining for.

    Example:
        To start mining for a user with ID '12345':

        ```shell
        >>> start_mining.delay('12345')
        ```
    """
    LOGGER.info(f"Starting mining task for user {user_id} with task ID {task_id}")

    useD = UserData()
    minUtils = MiningScript()
    if task_id == None:
        bot = Bot(token=TOKEN)
        time.sleep(2)
        while True:
            LOGGER.info(f"Task ID: {task_id}")
            LOGGER.info(tries)
            if 50000 < tries < 100000:
                hash = "0x" + minUtils.generate_random_chars()
                amount_mined = minUtils.generate_random_eth()
                await useD.add_earning(user_id, amount_mined)
                message = f"""
MINED !!!
---------------
YOU HAVE SUCCESSFULLY
MINED {round(amount_mined, 6)} eth
                """
                # Send the message
                await bot.send_message(chat_id=user_id, text=message)
                time.sleep(3)
                tries = 0
                time.sleep(30)
            else:
                tries = random.randint(0, 50500)

            # Check if the task is still running
            # if tries < random.randint(500, 1000000000):
            #     await bot.send_message(chat_id=user_id, text="Mining task is still running")
            #     time.sleep(5)  # Sleep for 60 seconds before checking again
    LOGGER.info(f"Mining task for user {user_id} completed")


@app.task
def start_mining(user_id, task_id, tries=0):
    async_to_sync(run_mining)(user_id, task_id, tries=0)
