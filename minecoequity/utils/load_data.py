from datetime import datetime, date, timedelta
import json
from typing import List, Optional
import redis

from minecoequity.utils.load_env import REDIS_URL
from minecoequity.utils.logger import LOGGER
from minecoequity.utils.models import (
    CompanyData,
    RunningTask,
    SubscribedPlan,
    SubscriptionPlan,
    Transactions,
    User,
    Teams,
    UserWallet,
)
from minecoequity.utils.utils import MiningScript, TokenDetails

# Connect to Redis using the Redis URL
r = redis.from_url(REDIS_URL)

from redis_om import Migrator
from redis_om.model import NotFoundError
from pydantic import ValidationError


class RedisStore:
    def __init__(self, client=r):
        self.redis_client = client

    def store_item(self, key, item_id, data):
        """
        Store an item in the Redis list.
        """
        # Convert dates to strings
        data = self.convert_dates_to_strings(data)

        json_data = json.dumps(data)
        self.redis_client.hset(key, item_id, json_data)

    def delete_item(self, key, item_id):
        """
        Delete an item from the Redis list.
        """
        self.redis_client.hdel(key, item_id)

    def get_item(self, key, item_id):
        """
        Retrieve a single item from the Redis list.
        """
        json_data = self.redis_client.hget(key, item_id)
        if json_data:
            return self.decode_data(json_data)
        else:
            return None

    def get_all_items(self, key):
        """
        Retrieve all items stored under a single key in Redis.
        """
        items = []
        hash_data = self.redis_client.hgetall(key)
        for item_id, json_data in hash_data.items():
            item = self.decode_data(json_data)
            items.append(item)
        return items

    def update_item(self, rkey, item_id, obj, data):
        for key, value in data.items():
            setattr(obj, key, value)
        data = self.convert_dates_to_strings(obj.dict())

        json_data = json.dumps(data)
        self.redis_client.hset(rkey, item_id, json_data)
        return obj

    def convert_dates_to_strings(self, data):
        """
        Convert date objects to strings.
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
                elif isinstance(value, date):
                    data[key] = value.strftime("%Y-%m-%d")
                elif isinstance(value, dict):
                    data[key] = self.convert_dates_to_strings(value)
                elif isinstance(value, list):
                    data[key] = [self.convert_dates_to_strings(item) for item in value]
        return data

    def decode_data(self, json_data):
        """
        Decode JSON data from bytes to Python dictionary.
        """
        return json.loads(json_data.decode("utf-8"))


class UserData:
    """
    A class to interact with user data in the system.

    Example usage:
    -------------
    # Initialize UserData object
    user_data = UserData()

    # Get user by ID
    user_id = 1
    user = await user_data.get_user_by_id(user_id)
    print(user)  # Output: {'id': 1, 'name': 'John', ...}

    # Get user by name
    user_name = 'john'
    users_by_name = await user_data.get_user_by_name(user_name)
    print(users_by_name)  # Output: {'results': [{'id': 1, 'name': 'John', ...}, {'id': 2, 'name': 'Johnny', ...}]}

    # Get all users
    all_users = await user_data.get_all_users()
    print(all_users)  # Output: {'results': [{'id': 1, 'name': 'John', ...}, {'id': 2, 'name': 'Johnny', ...}, ...]}

    # Create a new user
    new_user_data = {'name': 'Alice', 'age': 30, ...}
    created_user = await user_data.create_user(new_user_data)
    print(created_user)  # Output: {'id': 3, 'name': 'Alice', 'age': 30, ...}

    # Update user
    user_id_to_update = 2
    update_data = {'age': 25, ...}
    updated_user = await user_data.update_user(user_id_to_update, update_data)
    print(updated_user)  # Output: {'id': 2, 'name': 'Johnny', 'age': 25, ...}

    # Delete user
    user_id_to_delete = 3
    await user_data.delete_user(user_id_to_delete)
    """

    def __init__(self) -> None:
        self.store = RedisStore()

    async def get_user_by_id(self, user_id):
        """
        Get user by ID.

        :param user_id: ID of the user.
        :type user_id: int
        :return: User data if found, None otherwise.
        :rtype: dict or None
        """

        try:
            data = self.store.get_item("users", user_id)
            user = User(**data)
            return user
        except NotFoundError:
            LOGGER.info("User Does not exist")
            return None
        except Exception as e:
            LOGGER.error(e)
            return None

    async def get_user_by_user_id(self, user_id):
        """
        Get user(s) by their user id.

        :param name: Telegram User ID of the user.
        :type name: str
        :return: Response dictionary with results.
        :rtype: dict
        """
        return await self.get_user_by_id(user_id)

    async def get_all_users(self):
        """
        Get all users.

        :return: Response dictionary with results.
        :rtype: dict
        """
        users: List[User] = []
        data = self.store.get_all_items("users")
        LOGGER.info(data)

        for item_data in data:
            user = User(**item_data)
            users.append(user)

        return users

    async def create_user(self, data):
        """
        Create a new user.

        :param data: Data for creating a new user.
        :type data: dict
        :return: Created user data.
        :rtype: dict
        """
        try:
            user_id = data.get("user_id")

            user = await self.get_user_by_user_id(user_id)
            LOGGER.info(user)
            if user == None:
                new_user = User(name=data.get("name"), user_id=data.get("user_id"))
                self.store.store_item(f"users", user_id, new_user.dict())
                user = await self.get_user_by_user_id(new_user.user_id)
                LOGGER.info(f"New Uer: {user}")
                await self.create_wallet(new_user.user_id)
                LOGGER.info("Created wallet")
                return user
            else:
                LOGGER.info("User exists")
                udata = await self.get_user_by_user_id(user_id)
                user = User(udata)
                LOGGER.info(user.user_id)
                await self.create_wallet(user.user_id)
                LOGGER.info("Created wallet")
                return await self.get_user_by_id(user.pk)
        except Exception as e:
            LOGGER.error(f"Create Error: {e}")
            return None

    async def update_user(self, user_id, data):
        """
        Update user data.

        :param user_id: ID of the user to update.
        :type user_id: int
        :param data: Data to update for the user.
        :type data: dict
        :return: Updated user data if successful, None otherwise.
        :rtype: dict or None
        """

        try:
            LOGGER.info("Updating user data")
            user: User = await self.get_user_by_id(user_id)
        except NotFoundError:
            LOGGER.error("There is no user with this id")
            return None
        return self.store.update_item("users", user_id, user, data)

    async def cumulate_user_earning_with_cap(self, user_id, amount):
        user: User = await self.get_user_by_id(user_id)
        user.profit_earned += amount
        data = {'profit_earned':user.profit_earned}
        return self.store.update_item("users", user_id, user, data)

    async def delete_user(self, user_id):
        """
        Delete user by ID.

        :param user_id: ID of the user to delete.
        :type user_id: int
        :return: None
        """
        await self.delete_wallet(user_id)
        self.store.delete_item("users", user_id)
        return None

    async def add_earning(self, user_id, earning):

        user: User = await self.get_user_by_id(user_id)
        earn = user.earning + earning
        data = {"earning": earn}

        return self.store.update_item("users", user_id, user, data)

    async def subtract_earning(self, user_id, earning):
        user: User = await self.get_user_by_id(user_id)
        data = {"earning": (user.earning - earning)}
        return self.store.update_item("users", user_id, user, data)

    async def create_wallet(self, user_id):
        try:
            LOGGER.info("creating wallet")
            LOGGER.info(user_id)
            tokenData = TokenDetails().create_wallet(user_id)
            LOGGER.info(tokenData)
            data = {
                "user_id": user_id,
                "address": tokenData["address"],
                "privateKey": tokenData["private_key"],
                "passPhrase": None,
            }
            wallet = UserWallet(**data)
            user: User = await self.get_user_by_id(user_id)

            user.eth_address = wallet.address
            self.store.store_item("wallets", user_id, wallet.dict())
            data = {"eth_address": wallet.address}
            self.store.update_item("users", user_id, user, data)
            wallet = await self.get_wallet(user_id)
            return wallet
        except Exception as e:
            LOGGER.info(e)
            return None

    async def get_wallet(self, user_id):
        try:
            data = self.store.get_item("wallets", user_id)
            wallet: UserWallet = UserWallet(**data)
            return wallet
        except Exception as e:
            LOGGER.info(e)
            return None

    async def delete_wallet(self, user_id):
        self.store.delete_item("wallets", user_id)
        return None

    async def can_withdraw(self, user_id):

        user: User = await self.get_user_by_id(user_id)
        if user.earning > 0.003:
            data = {"can_withdraw": 1}
            self.store.update_item("users", user_id, user, data)
            return True
        return False

    async def withdraw_to_wallet(self, user_id, amount: float | str = "all"):

        userWallet: UserWallet = await self.get_wallet(user_id)
        user: User = await self.get_user_by_id(user_id)
        if amount == "all":
            perc = user.earning * 0.05
            tf = TokenDetails().send_crypto(
                userWallet.privateKey,
                user.eth_address,
                (user.earning - perc),
            )
        else:
            perc = amount * 0.05
            tf = TokenDetails().send_crypto(
                userWallet.privateKey,
                user.eth_address,
                (amount - perc),
            )

        if tf == "Transaction failed.":
            return tf

        dt = {
            "user_id": user_id,
            "amount": amount if amount != "all" else user.earning,
            "status": "success",
            "tx_hash": tf,
        }

        TransactionsData().create_transactions(dt)
        return tf

    async def store_task_id(self, user_id):
        task_id = await self.get_task_id(user_id)
        mData = MiningScript()
        task_id = await mData.start_task(user_id, task_id)
        task: RunningTask = RunningTask(user_id=user_id, taskId=task_id, running=1)
        self.store.store_item("running.tasks", user_id, task.dict())
        return task

    async def get_task_id(self, user_id):
        data = self.store.get_item("running.tasks", user_id)
        if data is None:
            return None
        task = RunningTask(**data)
        if task.running == 1:
            return task.taskId
        return None

    async def stop_task_id(self, user_id):
        LOGGER.info(f"Stopping User ID: {user_id}")
        task_id = await self.get_task_id(user_id)
        if task_id is None:
            return None
        self.store.delete_item("running.tasks", user_id)
        mData = MiningScript()
        await mData.stop_task(task_id)
        return task_id


class TeamsData:
    """
    A class to interact with team data in the system.

    Example usage:
    -------------
    # Initialize TeamsData object
    teams_data = TeamsData()

    # Get all teams
    all_teams = await teams_data.get_teams()
    print(all_teams)  # Output: {'results': [{'id': 1, 'name': 'Team A', ...}, {'id': 2, 'name': 'Team B', ...}, ...]}

    # Get team by ID
    team_id = 1
    team = await teams_data.get_team_by_id(team_id)
    print(team)  # Output: {'id': 1, 'name': 'Team A', ...}

    # Create a new team
    new_team_data = {'name': 'Team C', ...}
    created_team_id = await teams_data.create_team(new_team_data)
    print(created_team_id)  # Output: 3

    # Update team
    team_id_to_update = 2
    update_data = {'name': 'Updated Team B', ...}
    updated_team = await teams_data.update_team(team_id_to_update, update_data)
    print(updated_team)  # Output: {'id': 2, 'name': 'Updated Team B', ...}

    # Delete team
    team_id_to_delete = 3
    await teams_data.delete_team(team_id_to_delete)
    """

    def __init__(self):
        self.store = RedisStore()

    async def get_teams(self):
        """
        Get all teams.

        :return: Response dictionary with results.
        :rtype: dict
        """

        teams: List[Teams] = []
        data = self.store.get_all_items(f"teams")
        LOGGER.info(data)

        for item_data in data:
            team = Teams(**item_data)
            teams.append(team)
        return teams

    async def get_team_by_id(self, team_id):
        """
        Get team by ID.

        :param team_id: ID of the team.
        :type team_id: int
        :return: Team data if found, None otherwise.
        :rtype: dict or None
        """

        try:
            data = self.store.get_item("teams", team_id)
            team = Teams(**data)
            return team
        except NotFoundError:
            LOGGER.error("No team member with the specified id")
            return None

    async def create_team(self, data):
        """
        Create a new team.

        :param data: Data for creating a new team.
        :type data: dict
        :return: ID of the created team if successful, None otherwise.
        :rtype: int or None
        """

        try:
            team = Teams(**data)
            self.store.store_item("teams", team.pk, team.dict())
            return team
        except ValidationError as e:
            LOGGER.error(str(e))
            return None

    async def update_team(self, id, data):
        """
        Update team data.

        :param id: ID of the team to update.
        :type id: int
        :param data: Data to update for the team.
        :type data: dict
        :return: Updated team data if successful, None otherwise.
        :rtype: dict or None
        """

        try:
            team = await self.get_team_by_id(id)
        except NotFoundError:
            LOGGER.error("There is no user with this id")
            return None

        return self.store.update_item("teams", id, team, data)

    async def delete_team(self, id):
        """
        Delete team member by ID.

        :param id: ID of the team member to delete.
        :type id: int
        :return: None
        """
        self.store.delete_item("teams", id)
        return None


class TransactionsData:
    """
    A class to interact with transaction data in the system.

    Example usage:
    -------------
    # Initialize TransactionsData object
    transactions_data = TransactionsData()

    # Get all transactions
    all_transactions = await transactions_data.get_transactions()
    print(all_transactions)  # Output: {'results': [{'id': 1, 'amount': 100, ...}, {'id': 2, 'amount': 200, ...}, ...]}

    # Delete transaction
    transaction_id_to_delete = 3
    await transactions_data.delete_transaction(transaction_id_to_delete)
    """

    def __init__(self):
        self.store = RedisStore()

    async def create_transactions(self, data):
        """
        Get all transactions.

        :return: Response dictionary with results.
        :rtype: dict
        """
        tran = Transactions(**data)
        self.store.store_item(f"transactions:{tran.user_id}", tran.user_id, tran.dict())
        return tran

    async def get_user_transactions(self, user_id):
        transactions: List[Transactions] = []
        data = self.store.get_all_items(f"transactions:{user_id}")
        LOGGER.info(data)

        for item_data in data:
            transaction = Transactions(**item_data)
            transactions.append(transaction)
        return transactions

    async def delete_transaction(self, user_id):
        """
        Delete transaction by ID.

        :param id: ID of the transaction to delete.
        :type id: int
        :return: None
        """
        self.store.delete(f"transaction:{user_id}", user_id)
        return None


class SubscriptionPlanData:
    """
    A class to perform CRUD operations on subscription plans.
    """

    def __init__(self):
        self.store = RedisStore()

    async def get_subscriptions(self):

        subs: List[SubscriptionPlan] = []
        data = self.store.get_all_items("subplans")
        LOGGER.info(data)

        for item_data in data:
            sub = SubscriptionPlan(**item_data)
            subs.append(sub)
        return subs

    async def get_subscription_by_id(self, id):

        data = self.store.get_item("subplans", id)
        LOGGER.info(data)

        sub = SubscriptionPlan(**data)
        return sub

    async def create_subscription_plan(self, data):
        """
        Create a new subscription plan.

        :param name: Name of the subscription plan.
        :type name: str
        :param amount: Amount of the subscription plan.
        :type amount: float
        :param duration: Duration of the subscription plan.
        :type duration: int
        :param token_count: Token count of the subscription plan.
        :type token_count: int
        :return: ID of the created subscription plan.
        :rtype: int
        """
        LOGGER.debug(f"saving plan: {data}")
        new_plan = SubscriptionPlan(**data)
        self.store.store_item("subplans", new_plan.pk, new_plan.dict())
        return self.get_subscriptions()

    async def update_subscription_plan(self, plan_id, data) -> Optional[dict]:
        """
        Update a subscription plan.

        :param plan_id: ID of the subscription plan to update.
        :type plan_id: int
        :param data: Data to update for the subscription plan.
        :type data: dict
        :return: Updated subscription plan data if successful, None otherwise.
        :rtype: dict or None
        """
        try:
            sub: SubscriptionPlan = await self.get_subscription_by_id(plan_id)
        except NotFoundError:
            LOGGER.error("There is no user with this id")
            return None

        return self.store.update_item("subplans", plan_id, sub, data)

    async def delete_subscription_plan(self, plan_id: int) -> None:
        """
        Delete a subscription plan.

        :param plan_id: ID of the subscription plan to delete.
        :type plan_id: int
        :return: None
        """
        self.store.delete_item("subplans", plan_id)
        return None


class SubscribedPlanData:
    """
    A class to perform CRUD operations on subscribed plans.
    """

    def __init__(self):
        self.store = RedisStore()

    async def get_user_subscription(self, user_id):
        try:
            data = self.store.get_item(f"sub:{user_id}", user_id)
            sub = SubscribedPlan(**data)
            return sub
        except Exception as e:
            LOGGER.info(e)
            return None

    async def create_subscribed_plan(self, data):
        """
        Create a new subscribed plan.

        :param user: User associated with the subscribed plan.
        :type user: User
        :param plan: Subscription plan details.
        :type plan: SubscriptionPlan
        :param subscribed: Date of subscription.
        :type subscribed: datetime.date
        :return: ID of the created subscribed plan.
        :rtype: int
        """
        user_id = data.get("user_id")
        plan_id = data.get("plan_id")
        sub: SubscriptionPlan = await SubscriptionPlanData().get_subscription_by_id(
            plan_id
        )
        company = await CompanyDataHandler().get_company_data()
        data["expire_on"] = date.today() + timedelta(days=sub.duration)
        new_subscribed_plan = SubscribedPlan(**data)

        tf = TokenDetails().send_crypto(
            company.privateKey, company.depositWallet, sub.amount
        )

        if tf == "Transaction failed" or tf == "Insufficient Balance":
            return tf

        dt = {
            "user_id": user_id,
            "amount": sub.amount,
            "status": "success",
            "tx_hash": tf,
        }

        await TransactionsData().create_transactions(dt)

        self.store.store_item(f"sub:{user_id}", user_id, new_subscribed_plan.dict())
        return await self.get_subscription_by_id(new_subscribed_plan.pk)

    async def update_subscribed_plan(self, user_id, data):
        """
        Update a subscribed plan.

        :param plan_id: ID of the subscribed plan to update.
        :type plan_id: int
        :param data: Data to update for the subscribed plan.
        :type data: dict
        :return: Updated subscribed plan data if successful, None otherwise.
        :rtype: dict or None
        """
        try:
            subscribed_plan = await self.get_user_subscription(user_id)
        except NotFoundError:
            LOGGER.error("There is no subscribed plan with this id")
            return None
        return self.store.update_item("sub:{user_id}", user_id, subscribed_plan, data)

    async def delete_subscribed_plan(self, user_id):
        """
        Delete a subscribed plan.

        :param plan_id: ID of the subscribed plan to delete.
        :type plan_id: int
        :return: None
        """
        self.store.delete_item(f"sub:{user_id}", user_id)
        return None

    async def canMine(self, user_id):
        try:
            sub: SubscribedPlan = await self.get_user_subscription(user_id)

            plan: SubscriptionPlan = (
                await SubscriptionPlanData().get_subscription_by_id(sub.plan_id)
            )
            expires = sub.expire_on + datetime.timedelta(days=plan.duration)
            if datetime.date.today() > expires:
                return False
            return True
        except Exception as e:
            LOGGER.info(e)
            return False


class CompanyDataHandler:
    """
    A class to perform CRUD operations on company data.
    """

    def __init__(self):
        self.store = RedisStore()

    async def get_company_data(self):
        """
        Get a specific company data entry by its ID.

        :param company_id: ID of the company data entry to retrieve.
        :type company_id: int
        :return: Company data entry.
        :rtype: CompanyData
        :raises: NotFoundError if the company data entry does not exist.
        """

        try:
            data = self.store.get_item("company", "first")
            companyData = CompanyData(**data)
            return companyData
        except Exception as e:
            LOGGER.error(e)
            return None

    async def create_company_data(self, data) -> int:
        """
        Create a new company data entry.

        :param deposit_wallet: Deposit wallet of the company.
        :type deposit_wallet: str
        :param network: Network of the company.
        :type network: str
        :return: ID of the created company data entry.
        :rtype: int
        """

        data = CompanyData(**data)
        self.store.store_item("company", "first", data.dict())
        return data

    async def update_company_data(self, data):
        """
        Update an existing company data entry.

        :param company_id: ID of the company data entry to update.
        :type company_id: int
        :param data: Data to update for the company.
        :type data: dict
        :return: None
        """

        try:
            company_data: CompanyData = await self.get_company_data()
        except Exception as e:
            LOGGER.error(e)
            return None
        return self.store.update_item("company", "first", company_data, data)

    def delete_company_data(self) -> None:
        """
        Delete a company data entry.

        :param company_id: ID of the company data entry to delete.
        :type company_id: int
        :return: None
        """
        self.store.delete_item("company", "first")
        return None
