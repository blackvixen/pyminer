import datetime
from typing import Optional

from pydantic import EmailStr

from redis_om import Field, HashModel, Migrator


class Customer(HashModel):
    first_name: str
    last_name: str = Field(index=True)
    email: str
    join_date: datetime.date
    age: int = Field(index=True)
    bio: Optional[str]


andrew = Customer(
    first_name="Andrew",
    last_name="Brookins",
    email="brookins@example.com",
    join_date=datetime.date.today(),
    age=38,
)

andrew.save()


# Now, if we use this model with a Redis deployment that has the
# Redis Stack installed, we can run queries like the following.

# Before running queries, we need to run migrations to set up the
# indexes that Redis OM will use. You can also use the `migrate`
# CLI tool for this!
# Migrator().run()


# Find all customers with the last name "Brookins"
Customer.find(Customer.last_name == "Brookins").all()

# Find all customers that do NOT have the last name "Brookins"
Customer.find(Customer.last_name != "Brookins").all()

# Find all customers whose last name is "Brookins" OR whose age is
# 100 AND whose last name is "Smith"
Customer.find((Customer.last_name == "Brookins") | (Customer.age == 100) & (Customer.last_name == "Smith")).all()
