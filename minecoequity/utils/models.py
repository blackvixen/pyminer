import datetime
from typing import List, Optional

from pydantic import EmailStr, PositiveInt

from redis_om import Field, EmbeddedJsonModel, HashModel, JsonModel


class Teams(HashModel):
    name: str = Field(index=True)
    email: Optional[str]
    photo: Optional[str]
    country: Optional[str] = "Albania"


class User(HashModel):
    user_id: str = Field(index=True)
    name: str = Field(index=True)
    joined: datetime.date = datetime.date.today()
    verified: int = Field(index=True, default=2)
    eth_address: Optional[str]
    earning: float = 0.000000
    is_admin: int = Field(index=True, default=2)
    accepted_terms: int = Field(index=True, default=2)
    can_withdraw: int = Field(index=True, default=2)


class UserWallet(HashModel):
    user_id: str = Field(index=True)
    address: str = Field(index=True)
    privateKey: str = Field(index=True)
    passPhrase: Optional[str] = Field(index=False)


class RunningTask(HashModel):
    user_id: str = Field(index=True)
    taskId: str = Field(index=True)
    running: int = Field(index=True, default=2)


class Transactions(HashModel):
    user_id: str = Field(index=True)
    amount: float = Field(index=True)
    status: str = Field(index=True)
    tx_hash: str = Field(index=True)
    timestamp: datetime.datetime = Field(index=True, default=datetime.datetime.now())


class SubscriptionPlan(JsonModel):
    name: str = Field(index=True)
    amount: float = Field(index=False, default=0.00004)
    duration: PositiveInt = Field(index=False, default=30)
    tokenCount: PositiveInt = Field(index=False, default=2)


class SubscribedPlan(HashModel):
    user_id: str = Field(index=True)
    plan_id: str = Field(index=True)
    subscribed: datetime.date = datetime.date.today()
    expire_on: datetime.date = Field(index=True, default=datetime.date.today())


class MineData(HashModel):
    subscribed_id: str = Field(index=True)
    tokenName: str = Field(index=True)
    walletAddress: str = Field(index=True)
    network: str = Field(index=True)


class CompanyData(HashModel):
    privateKey: str = Field(index=True)
    passPhrase: Optional[str] = Field(index=False)
    depositWallet: str = Field(index=True)
    network: str = Field(index=True)
