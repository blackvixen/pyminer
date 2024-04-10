from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from minecoequity.utils.load_data import (
    UserData,
    SubscriptionPlanData,
    SubscribedPlanData,
    TransactionsData,
    CompanyData,
)
from minecoequity.utils.load_env import DEVELOPER_CHAT_ID
from minecoequity.utils.logger import LOGGER
from minecoequity.utils.utils import TokenDetails

userData = UserData()
subPlanData = SubscriptionPlanData()
subData = SubscribedPlanData()
transData = TransactionsData()


async def subscription_markup(user_id):
    user = await userData.get_user_by_user_id(user_id)
    plans = InlineKeyboardButton("Subscription Plans", callback_data="view_plans")
    home = InlineKeyboardButton("Home", callback_data="home")
    view_account = InlineKeyboardButton("View Account", callback_data="view_account")
    sub = InlineKeyboardButton("Create Plan", callback_data="sub")

    keyboard = [
        [home, view_account],
        [plans],
    ]
    if user.is_admin == 1:
        keyboard = [
            [home, view_account],
            [plans],
            [sub],
        ]

    return InlineKeyboardMarkup(keyboard)


async def users_markup(user_id):
    delete = InlineKeyboardButton("Delete User", callback_data=f"delete_user-{user_id}")
    can_withdraw = InlineKeyboardButton(
        "Enable Withdrawal", callback_data=f"can_withdraw-{user_id}"
    )
    set_cap = InlineKeyboardButton(
        "Set Profit Cap", callback_data=f"set_cap-{user_id}"
    )
    adjust_balance = InlineKeyboardButton(
        "Adjust Balance", callback_data=f"adjust_balance-{user_id}"
    )
    make_admin = InlineKeyboardButton("Make Admin", callback_data=f"admin-{user_id}")
    send_message = InlineKeyboardButton("Send Message", callback_data=f"send_message-{user_id}")
    keyboard = [
        [can_withdraw, make_admin],
        [adjust_balance, set_cap],
        [send_message],
    ]
    return InlineKeyboardMarkup(keyboard)


async def team_markup(user_id):
    delete = InlineKeyboardButton("Delete Team", callback_data=f"delete_team-{user_id}")
    update = InlineKeyboardButton("Update Team", callback_data=f"update_team-{user_id}")

    keyboard = [
        [update, delete],
    ]
    return InlineKeyboardMarkup(keyboard)


async def account_markup(user_id):
    cm = await subData.canMine(user_id)
    home = InlineKeyboardButton("Home", callback_data="home")
    u_profile = InlineKeyboardButton("Update Profile", callback_data="u_profile")
    start_mining = InlineKeyboardButton("Start Mining", callback_data="start")
    stop_mining = InlineKeyboardButton("Stop Mining", callback_data="stop")
    plans = InlineKeyboardButton("Subscription Plans", callback_data="view_plans")
    transactions = InlineKeyboardButton(
        "My Transactions", callback_data="view_transactions"
    )
    if cm:
        keyboard = [
            [home, u_profile],
            [start_mining, stop_mining],
            [transactions],
        ]
    else:
        keyboard = [
            [home],
            [u_profile, plans],
            [transactions],
        ]

    return InlineKeyboardMarkup(keyboard)


async def update_markup(user_id):
    cm = await subData.canMine(user_id)
    home = InlineKeyboardButton("Home", callback_data="home")
    view_account = InlineKeyboardButton("View Account", callback_data="view_account")
    u_profile = InlineKeyboardButton("Update Profile", callback_data="u_profile")
    start_mining = InlineKeyboardButton("Start Mining", callback_data="start")
    stop_mining = InlineKeyboardButton("Stop Mining", callback_data="stop")
    plans = InlineKeyboardButton("Subscription Plans", callback_data="view_plans")
    transactions = InlineKeyboardButton(
        "My Transactions", callback_data="view_transactions"
    )
    if cm:
        keyboard = [
            [home],
            [view_account, u_profile],
            [start_mining, stop_mining],
            [transactions],
        ]
    else:
        keyboard = [
            [home, view_account],
            [u_profile, plans],
            [transactions],
        ]

    return InlineKeyboardMarkup(keyboard)


async def subscribe_markup(user_id, plan_id):
    cm = await subData.canMine(user_id)
    user = await userData.get_user_by_id(user_id)
    subscription = await subData.get_user_subscription(user_id)
    update = InlineKeyboardButton("Update Plan", callback_data=f"u_plan-{plan_id}")
    start_mining = InlineKeyboardButton("Start Mining", callback_data="start")
    stop_mining = InlineKeyboardButton("Stop Mining", callback_data="stop")
    subscribe = InlineKeyboardButton(
        "Subscribe Now", callback_data=f"subscribe_now-{plan_id}"
    )

    if cm and subscription is not None and plan_id == subscription.plan_id:
        keyboard = (
            [[update], [start_mining, stop_mining]]
            if user.is_admin == 1
            else [[start_mining, stop_mining]]
        )
    else:
        keyboard = (
            [
                [update],
                [subscribe],
            ]
            if user.is_admin == 1
            else [
                [subscribe],
            ]
        )
    # keyboard = [[start_mining, stop_mining]]
    return InlineKeyboardMarkup(keyboard)


async def welcome_markup(user_id):
    user = await userData.get_user_by_user_id(user_id)
    wallet = await userData.get_wallet(user_id)
    LOGGER.debug(f"USER: {user}")

    connect = InlineKeyboardButton("Connect", callback_data="connect")
    home = InlineKeyboardButton("Home", callback_data="home")
    teams = InlineKeyboardButton("Our Team", callback_data="view_teams")
    about = InlineKeyboardButton("About", callback_data="about")
    faq = InlineKeyboardButton("FAQ", callback_data="faq")
    services = InlineKeyboardButton("Services", callback_data="services")
    help = InlineKeyboardButton("Help", callback_data="help")

    admin = InlineKeyboardButton(
        "|-------- ADMIN BUTTONS ONLY --------|", callback_data="----"
    )
    update_company = InlineKeyboardButton(
        "Update Company", callback_data="update_company"
    )
    view_users = InlineKeyboardButton("Users", callback_data="users")
    add_teams = InlineKeyboardButton("Add Teams", callback_data="add_teams")

    plans = InlineKeyboardButton("Subscription Plans", callback_data="view_plans")

    transactions = InlineKeyboardButton(
        "My Transactions", callback_data="view_transactions"
    )
    withdraw = InlineKeyboardButton("Withdraw Now", callback_data="withdraw_roi")

    view_account = InlineKeyboardButton("View Account", callback_data="view_account")
    generate_wallet = InlineKeyboardButton(
        "Create Wallet", callback_data="create_wallet"
    )

    accept_terms = InlineKeyboardButton("Accept Terms", callback_data="accept_terms")
    decline_terms = InlineKeyboardButton("Decline Terms", callback_data="decline_terms")
    support_button = InlineKeyboardButton(
        "Contact Support",
        url="https://t.me/Helpdesk_MinecoEquity",
    )

    if user != None:
        if not user.accepted_terms == 1:
            welcome_keyboard = [
                [about, faq],
                [teams, services, help],
                [accept_terms, decline_terms],
                [support_button],
            ]
        elif user.accepted_terms == 1:
            if user.can_withdraw == 1 and wallet is not None:
                welcome_keyboard = [
                    [home, support_button],
                    [about, faq, teams],
                    [services, help],
                    [view_account, plans],
                    [withdraw],
                    [transactions],
                ]
            elif user.can_withdraw == 2 and wallet is not None:
                welcome_keyboard = [
                    [home, support_button],
                    [about, faq, teams],
                    [services, help],
                    [view_account, plans],
                    [transactions],
                ]
            elif user.can_withdraw == 1 and wallet is None:
                welcome_keyboard = [
                    [home, support_button],
                    [about, faq, teams],
                    [services, help],
                    [view_account, plans],
                    [generate_wallet],
                    [transactions],
                ]
            elif user.can_withdraw == 2 and wallet is None:
                welcome_keyboard = [
                    [home, support_button],
                    [about, faq, teams],
                    [services, help],
                    [view_account, plans],
                    [generate_wallet][transactions],
                ]

        if user.is_admin == 1 or user.user_id == DEVELOPER_CHAT_ID:
            welcome_keyboard.append([admin])
            welcome_keyboard.append([update_company, add_teams])
            welcome_keyboard.append([view_users])
    elif user == None:
        welcome_keyboard = [[connect]]


    return InlineKeyboardMarkup(welcome_keyboard)
