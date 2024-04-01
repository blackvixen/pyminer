from decimal import Decimal
import random
import string

from celery.result import AsyncResult
# from celery.app.control import Control

from coinbase.rest import RESTClient as Client

from web3 import Web3

# from web3.middleware import geth_poa_middleware
# from web3.gas_strategies.rpc import rpc_gas_price_strategy
from web3.exceptions import ProviderConnectionError
from eth_account import Account
import secrets

# from web3.auto import w3

from tasks import start_mining
from minecoequity.utils.logger import LOGGER

from .load_env import COINBASE_API, COINBASE_SK, INFURA_HTTP_URL

client = Client(api_key=COINBASE_API, api_secret=COINBASE_SK)


class TokenDetails:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(f"{INFURA_HTTP_URL}"))
        if not self.w3.is_connected():
            LOGGER.info("Connection Error")
            return None
        pk = secrets.token_hex(32)
        LOGGER.info(f"0x{pk}")
        self.privateKey = f"0x{pk}"

    def get_price(self, symbol: str) -> Decimal:
        req = client.get_buy_price(currency=f"{symbol.upper}-USD")
        price = req["amount"]
        return Decimal(price)

    def validate_token(self, address: str) -> bool:
        return self.w3.is_checksum_address(address)

    def create_wallet(self, password: str):
        LOGGER.info("Generating wallet...")
        account = Account.from_key(self.privateKey)
        LOGGER.info(Account.encrypt(account.key.hex(), password))
        return {
            "private_key": account.key.hex(),
            "address": account.address,
        }

    def import_wallet(self, private_key: str, password: str) -> str:
        decrypted_key = Account.decrypt(private_key, password)
        account = self.w3.eth.account.from_key(decrypted_key)
        return account.address

    def get_balance(self, address: str) -> Decimal:
        balance = self.w3.eth.get_balance(address)
        return self.w3.from_wei(balance, "ether")

    def send_token(
        self,
        abi,
        contract_address: str,
        sender_private_key: str,
        recipient_address: str,
        amount_ether: float,
    ):
        sender_account = self.w3.eth.account.from_key(sender_private_key)
        nonce = self.w3.eth.get_transaction_count(sender_account.address)

        contract = self.w3.eth.contract(contract_address, abi)
        token_amount = self.w3.to_wei(amount_ether, "ether")

        # Get and determine gas parameters
        latest_block = self.web3.eth.get_block("latest")
        base_fee_per_gas = (
            latest_block.baseFeePerGas
        )  # Base fee in the latest block (in wei)
        max_priority_fee_per_gas = self.web3.to_wei(
            1, "gwei"
        )  # Priority fee to include the transaction in the block
        max_fee_per_gas = (
            5 * base_fee_per_gas
        ) + max_priority_fee_per_gas  # Maximum amount you’re willing to pay

        tx = {
            "nonce": nonce,
            "gas": 2100000,
            "maxFeePerGas": max_fee_per_gas,
            "maxPriorityFeePerGas": max_priority_fee_per_gas,
            "chainId": 1,
            # "gasPrice": self.w3.to_wei("50", "gwei"),
        }

        transaction = contract.functions.transfer(
            recipient_address,
            token_amount,
        ).build_transaction(tx)

        signed_tx = self.w3.eth.account.sign_transaction(
            transaction, sender_account.key
        )
        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if tx_receipt.status:
                LOGGER.info("Transaction successful!")
                LOGGER.info("Transaction hash:", tx_hash.hex())
                LOGGER.info(
                    f"Explorer link: https://sepolia.etherscan.io/tx/{tx_hash.hex()}"
                )
                return f"https://sepolia.etherscan.io/tx/{tx_hash.hex()}"
            else:
                LOGGER.info("Transaction failed")
                return "Transaction failed"
        except Exception as e:
            LOGGER.info(e)
            if 'insufficient funds for gas' in e:
                return "Insufficient Balance"
            return "Transaction failed"

    def send_crypto(
        self, sender_private_key: str, recipient_address: str, amount_ether: Decimal
    ) -> str:
        sender_account = self.w3.eth.account.from_key(sender_private_key)
        nonce = self.w3.eth.get_transaction_count(sender_account.address)

        # Get and determine gas parameters
        latest_block = self.w3.eth.get_block("latest")
        base_fee_per_gas = (
            latest_block.baseFeePerGas
        )  # Base fee in the latest block (in wei)
        max_priority_fee_per_gas = self.w3.to_wei(
            1, "gwei"
        )  # Priority fee to include the transaction in the block
        max_fee_per_gas = (
            5 * base_fee_per_gas
        ) + max_priority_fee_per_gas  # Maximum amount you’re willing to pay

        tx = {
            "nonce": nonce,
            "to": recipient_address,
            "value": self.w3.to_wei(amount_ether, "ether"),
            "gas": 21000,
            "maxFeePerGas": max_fee_per_gas,
            "maxPriorityFeePerGas": max_priority_fee_per_gas,
            "chainId": 1,
            # "gasPrice": self.w3.to_wei("50", "gwei"),
        }
        signed_tx = self.w3.eth.account.sign_transaction(tx, sender_account.key)
        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if tx_receipt.status:
                LOGGER.info("Transaction successful!")
                LOGGER.info("Transaction hash:", tx_hash.hex())
                LOGGER.info(f"Explorer link: https://etherscan.io/tx/{tx_hash.hex()}")
                return f"https://etherscan.io/tx/{tx_hash.hex()}"
            else:
                LOGGER.info("Transaction failed")
                return "Transaction failed"
        except Exception as e:
            LOGGER.info(e)
            if 'insufficient funds for gas' in str(e):
                return "Insufficient Balance"
            return "Transaction failed"


class MiningScript:
    def __init__(self, *args, **kwargs):
        pass

    async def start_task(self, user_id, task_id):
        task_id = start_mining.delay(user_id, task_id).id
        return task_id

    async def stop_task(self, thread_id):
        # control = Control()
        LOGGER.info(f"Revoking Celery task: {thread_id}")

        # Revoke the task by task ID
        # control.revoke(thread_id, terminate=True)
        result = AsyncResult(thread_id)
        LOGGER.info(f"Stopped Task: {result.id}")
        if result.state == "PENDING":
            # Task hasn't started yet
            result.revoke()
        elif result.state == "STARTED":
            # Task is running, try to terminate it gracefully
            result.revoke(terminate=True)

    def generate_random_time(self):
        random_int = random.randint(2, 33)
        return random_int

    def generate_random_eth(self):
        # Define the range in wei
        min_wei = int(0.0002 * 10**18)  # 0.0002 ETH in wei
        max_wei = int(0.0045 * 10**18)  # 0.0045 ETH in wei

        # Generate a random number within the range
        random_wei = random.randint(min_wei, max_wei)

        # Convert the random wei value back to ETH
        random_eth = random_wei / 10**18

        return random_eth

    def generate_random_chars(
        self, size=40, chars=string.ascii_uppercase + string.digits
    ):
        return "".join(random.choice(chars) for _ in range(size))
