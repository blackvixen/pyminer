import json
from telegram import Update, ForceReply
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler


from minecoequity.utils.load_env import DEVELOPER_CHAT_ID
from minecoequity.utils.utils import TokenDetails

from minecoequity.utils.load_data import (
    CompanyDataHandler,
    TeamsData,
    UserData,
    SubscriptionPlanData,
    SubscribedPlanData,
    TransactionsData,
    CompanyData,
)

from ..utils.logger import LOGGER
from ..utils import constants
from .buttons import (
    account_markup,
    subscribe_markup,
    subscription_markup,
    team_markup,
    update_markup,
    users_markup,
    welcome_markup,
)

userData = UserData()
# subPlanData = SubscriptionPlanData()
# subData = SubscribedPlanData()
teamsData = TeamsData()


async def welcome_command(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    chat_id = update.message.chat_id

    (
        LOGGER.info(context.args)
        if len(context.args) > 0
        else LOGGER.info("No User Arguments")
    )

    welcome_message = f"""
______________________________

<strong>Welcome Miner</strong>
______________________________

Please Accept our terms to continue using our services.
    """
    user_data = await userData.get_user_by_user_id(user_id)

    if user_data is None:
        welcome_message = f"""
<strong>Welcome Miner</strong>

To start mining, please connect to the network.
        """

    markup = await welcome_markup(user_id)

    bot_profile_photos = await context.bot.get_user_profile_photos(
        context.bot.id, limit=1
    )
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=bot_profile_photo,
        caption=welcome_message,
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )


async def home_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    chat_id = query.message.chat_id
    markup = await welcome_markup(user.id)
    welcome_message = """
<strong>Home</strong>

Make a selection and proceed with the prompts
    """
    bot_profile_photos = await context.bot.get_user_profile_photos(
        context.bot.id, limit=1
    )
    bot_profile_photo = bot_profile_photos.photos[0][0] if bot_profile_photos else None
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=bot_profile_photo,
        caption=welcome_message,
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )


async def connect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    chat_id = query.message.chat_id
    first_name = user.first_name
    last_name = user.last_name
    username = user.username
    user_id = user.id

    name = f"{first_name} {last_name}"

    user_data = {"name": name, "user_id": user_id}
    await userData.create_user(user_data)

    markup = await welcome_markup(user_id)
    await context.bot.send_message(
        chat_id=chat_id,
        reply_markup=markup,
        text=constants.about_message,
        parse_mode=ParseMode.HTML,
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    chat_id = query.message.chat_id
    markup = await welcome_markup(user.id)
    await context.bot.send_message(
        chat_id=chat_id,
        reply_markup=markup,
        text=constants.about_message,
        parse_mode=ParseMode.HTML,
    )


async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    chat_id = query.message.chat_id
    markup = await welcome_markup(user.id)
    await context.bot.send_message(
        chat_id=chat_id,
        reply_markup=markup,
        text=constants.services_message,
        parse_mode=ParseMode.HTML,
    )


async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    chat_id = query.message.chat_id
    markup = await welcome_markup(user.id)
    await context.bot.send_message(
        chat_id=chat_id,
        reply_markup=markup,
        text=constants.faq_messages,
        parse_mode=ParseMode.HTML,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    chat_id = query.message.chat_id
    markup = await welcome_markup(user.id)
    await context.bot.send_message(
        chat_id=chat_id,
        reply_markup=markup,
        text=constants.help_message,
        parse_mode=ParseMode.HTML,
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    chat_id = query.message.chat_id if query else user.id
    LOGGER.debug(f"{user.first_name} Has Canceled the conversation")
    cancel_message = "Alright Mate! I hope we can continue from where we left off."
    markup = await welcome_markup(user.id)
    await context.bot.send_message(
        chat_id=chat_id,
        reply_markup=markup,
        text=cancel_message,
        parse_mode=ParseMode.HTML,
    )
    return ConversationHandler.END


# Terms and Condition
async def accept_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    user_id = user.id

    chat_id = query.message.chat_id
    answer = await query.answer()
    LOGGER.info(answer)

    data = {"accepted_terms": 1, "verified": 1}

    user_data = await userData.update_user(user_id, data)

    markup = await welcome_markup(user_data.user_id)

    await context.bot.send_message(
        chat_id=chat_id,
        text="You have accepted our terms and condition for use",
        reply_markup=markup,
    )


async def decline_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    user_id = user.id

    chat_id = query.message.chat_id
    await query.answer()

    data = {"accepted_terms": 2, "verified": 2}

    user_data = await userData.update_user(user_id, data)

    markup = await welcome_markup(user_data.user_id)

    await context.bot.send_message(
        chat_id=chat_id,
        text="You have declined our terms and condition for use",
        reply_markup=markup,
    )


# Users
async def update_plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    qname = query.data.split("-")[0]
    user_id = query.data.split("-")[1]  # Extracting plan ID from callback data
    message_id = context.user_data.get(f"{user_id}")

    LOGGER.info(qname)
    LOGGER.info(user_id)
    u = await userData.get_user_by_id(user_id)
    if qname == "can_withdraw":
        (
            await userData.update_user(user_id, {"can_withdraw": 1})
            if u.can_withdraw == 2
            else await userData.update_user(user_id, {"can_withdraw": 2})
        )
    else:
        (
            await userData.update_user(user_id, {"is_admin": 1})
            if u.is_admin == 2
            else await userData.update_user(user_id, {"is_admin": 2})
        )

    us = await userData.get_user_by_id(user_id)

    # Construct the new message
    team_text = f"""

<strong>NAME</strong>: {us.name.title()}
<strong>USER id</strong>: {us.user_id}
<strong>WALLET</strong>: {us.eth_address}
<strong>EARNING</strong>: {round(us.earning, 6)} ETH
<strong>ADMIN</strong>:  {'💚' if us.is_admin == 1 else '🖤'}
<strong>ACCEPTED TERMS</strong>: {'💚' if us.accepted_terms == 1 else '🖤'}
<strong>CAN WITHDRAW</strong>: {'💚' if us.can_withdraw == 1 else '🖤'}

            """
    # Edit the original message with the new message
    admins = [DEVELOPER_CHAT_ID]
    if u.is_admin == 1:
        admins.append(u.user_id)

    markup = await users_markup(u.user_id)
    await context.bot.edit_message_text(
        chat_id=chat_id,
        reply_markup=markup if str(u.user_id) in admins else None,
        message_id=message_id,
        text=team_text,
        parse_mode=ParseMode.HTML,
    )


async def view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    user_id = user.id

    chat_id = query.message.chat_id
    teams = await userData.get_all_users()

    markup = await welcome_markup(user_id)

    udata = await userData.get_user_by_id(user_id)

    admins = [DEVELOPER_CHAT_ID]
    if udata.is_admin == 1:
        admins.append(udata.user_id)

    LOGGER.info(admins)
    LOGGER.info(user_id)

    if len(teams) > 0:
        for u in teams:
            team_text = f"""

<strong>NAME</strong>: {u.name.title()}
<strong>USER id</strong>: {u.user_id}
<strong>WALLET</strong>: {u.eth_address}
<strong>EARNING</strong>: {round(u.earning, 6)}
<strong>ADMIN</strong>:  {'💚' if u.is_admin == 1 else '🖤'}
<strong>ACCEPTED TERMS</strong>: {'💚' if u.accepted_terms == 1 else '🖤'}
<strong>CAN WITHDRAW</strong>: {'💚' if u.can_withdraw == 1 else '🖤'}

            """
            from telegram import InputFile

            markup = await users_markup(u.user_id)

            message = await context.bot.send_message(
                chat_id=chat_id,
                text=team_text,
                reply_markup=markup if str(user_id) in admins else None,
                parse_mode=ParseMode.HTML,
            )
            context.user_data[f"{u.user_id}"] = message.message_id
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="NO USER HAS BEEN ADDED YET",
            reply_markup=markup,
            parse_mode=ParseMode.HTML,
        )


# Our Teams
async def view_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    user_id = user.id

    chat_id = query.message.chat_id
    teams = await teamsData.get_teams()

    markup = await welcome_markup(user_id)

    udata = await userData.get_user_by_id(user_id)

    admins = [DEVELOPER_CHAT_ID]
    if udata.is_admin == 1:
        admins.append(udata.user_id)

    LOGGER.info(admins)
    LOGGER.info(user_id)

    if len(teams) > 0:
        for u in teams:
            team_text = f"""

<strong>NAME</strong>: {u.name.title()}
<strong>EMAIL</strong>: {u.email}
<strong>COUNTRY</strong>: {u.country}

            """
            from telegram import InputFile

            img = u.photo
            markup = await team_markup(u.pk)

            await context.bot.send_photo(
                chat_id=chat_id,
                photo=(
                    img if img.startswith("https://") else "https://placeholder.com/400"
                ),
                caption=team_text,
                reply_markup=markup if str(user_id) in admins else None,
                parse_mode=ParseMode.HTML,
            )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Admin has yet to upload the team data. Please check back later",
            reply_markup=markup,
        )


async def remove_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    user_id = user.id

    query.answer()
    chat_id = query.message.chat_id

    # Extract plan ID from callback data
    plan_id = query.data.split("-")[1]

    await TeamsData().delete_team(plan_id)

    # Start conversation passing the plan ID
    markup = await welcome_markup(user_id)
    await context.bot.send_message(
        chat_id=chat_id,
        text="""
Team Deleted
        """,
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )


# # plans
async def view_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    user_id = user.id

    chat_id = query.message.chat_id
    plans = await SubscriptionPlanData().get_subscriptions()

    if len(plans) > 0:
        for p in plans:
            plan_text = f"""
SUBSCRIPTION PLAN
------------------
<strong>NAME</strong>: {p.name.title()}
<strong>COST</strong>: {p.amount}
<strong>BOT MINERS</strong>: {p.tokenCount}
<strong>DURATION</strong>: {p.duration} Days
            """
            markup = await subscribe_markup(user_id, p.pk)
            await context.bot.send_message(
                chat_id=chat_id,
                text=plan_text,
                reply_markup=markup,
                parse_mode=ParseMode.HTML,
            )

    else:
        plan_text = """
SUBSCRIPTION PLANS
------------------
We are yet to add suitable plans to subscribe for your MINING journey.

Please check back in a few hours for us to populate these datas.
        """

        markup = await subscription_markup(user_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text=plan_text,
            reply_markup=markup,
            parse_mode=ParseMode.HTML,
        )


# async def view_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     user = update.effective_user
#     user_id = user.id

#     chat_id = query.message.chat_id
#     user_data = await get_user(user_id)
#     plan_text = await get_all_transactions(user_data)

#     markup = await welcome_markup(user_id)
#     await context.bot.send_message(chat_id=chat_id, text=plan_text, reply_markup=markup, parse_mode=ParseMode.HTML)


# # accounts
async def view_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    user_id = user.id

    chat_id = query.message.chat_id
    answer = await query.answer()
    LOGGER.info(answer)

    account = await userData.get_user_by_id(user_id)
    wallet = await userData.get_wallet(user_id)

    text = (
        f"""
<strong>🙍 {user_id} Account Details 🙍</strong>
_________________________

<strong>NAME</strong>: {account.name if account.name else None}

<strong>USER ID</strong>: <code>{account.user_id}</code>

<strong>BALANCE</strong>: {round(account.earning, 6)} <strong>ETH</strong>

<strong>WALLET ADDRESS</strong>: <code>{account.eth_address if account.eth_address else None}</code>

<strong>PRIVATE KEY</strong>: <code>{wallet.privateKey if wallet is not None else None}</code>

<strong>MNEMONIC PHRASE</strong>: <code>{wallet.passPhrase if wallet is not None else None}</code>

<pre><strong>NOTE</strong>: Please do not share the private key with anyone. Ensure to keep this secured and safe. Your wallet address can be imported into any other crypto wallet holder like metamask, trustwallet and many more.</pre>
    """
        if account is not None
        else f"""
<strong>🙍 {user_id} Account Details 🙍</strong>
_________________________

No Account Created Yet.
_________________________
    """
    )

    markup = await account_markup(user_id)

    await context.bot.send_message(
        chat_id=chat_id, text=text, parse_mode=ParseMode.HTML, reply_markup=markup
    )


NAME, CONFIRM = range(2)  # Define conversation states


async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = update.callback_query
    chat_id = query.message.chat_id

    await context.bot.send_message(
        chat_id=chat_id,
        text="Please type your full name:",
        reply_markup=ForceReply(
            selective=True, input_field_placeholder="Please type your full name:"
        ),
    )

    return NAME


async def check_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text

    if name != "":
        context.user_data["name"] = name
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Do you confirm your input?",
            reply_markup=ForceReply(
                selective=True, input_field_placeholder="YES or NO"
            ),
        )
        return CONFIRM
    else:
        await update.message.reply_text(
            "Invalid input. Please try again.",
            reply_markup=ForceReply(
                selective=True, input_field_placeholder="Please type your full name:"
            ),
        )
        return NAME


async def confirm_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    confirmation = update.message.text
    LOGGER.info(confirmation)
    chat_id = update.message.chat_id
    LOGGER.info(chat_id)
    user = update.effective_user
    user_id = str(user.id)

    if confirmation.lower() in ["yes", "y", "confirm", "ok"]:
        markup = await update_markup(user_id)
        try:
            data = {"name": context.user_data.get("name")}
            await userData.update_user(user_id, data)
            await update.message.reply_text(
                f"Name updated successfully!", reply_markup=markup
            )
        except Exception as e:
            await update.message.reply_text(
                f"Failed to update user informations: {str(e)}", reply_markup=markup
            )
            return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Incorrect User Details. Retrying",
            reply_markup=ForceReply(
                selective=True, input_field_placeholder="Please type your full name:"
            ),
        )
        return NAME
    return ConversationHandler.END


async def sub_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    # Extract plan ID from callback data
    plan_id = query.data.split("-")[1]

    LOGGER.info(f"Plan: {plan_id}, User: {user.id}")

    # Start conversation passing the plan ID
    data = {"user_id": user.id, "plan_id": plan_id}
    sub = await SubscribedPlanData().create_subscribed_plan(data)
    markup = await subscription_markup(user.id)
    if sub == "Transaction failed" or sub == "Insufficient Balance":
        await context.bot.send_message(
            chat_id=chat_id,
            text=sub,
            reply_markup=markup,
            parse_mode=ParseMode.HTML,
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"""
Subscription Paid
-----------------
<a href="{sub}">View Etherscan</a>
            """,
            reply_markup=markup,
            parse_mode=ParseMode.HTML,
        )


PLANDICT, PLANCONFIRM = range(2)  # Define conversation states


async def update_plan_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    # Extract plan ID from callback data
    plan_id = query.data.split("-")[1]

    # Start conversation passing the plan ID
    context.user_data["plan_id"] = plan_id
    await context.bot.send_message(
        chat_id=chat_id,
        text="""
Please add the details like this:

<code>{
    "name": "Diamond Plan",
    "amount": 0.0002,
    "duration": 30,
    "tokenCount":2
}</code>

Ensure it follows the exact same format.

<code>The amount is in a unified token value ETH, the duration is in days, while the tokenCount denotes the amount of bots to run for a single user</code>
        """,
        reply_markup=ForceReply(
            selective=True, input_field_placeholder="Follow the sample"
        ),
        parse_mode=ParseMode.HTML,
    )

    return PLANDICT


async def add_plan_dict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = update.callback_query
    chat_id = query.message.chat_id

    await context.bot.send_message(
        chat_id=chat_id,
        text="""
Please add the details like this:

<code>{
    "name": "Diamond Plan",
    "amount": 0.0002,
    "duration": 30,
    "tokenCount":2
}</code>

Ensure it follows the exact same format.

<code>The amount is in a unified token value ETH, the duration is in days, while the tokenCount denotes the amount of bots to run for a single user</code>
        """,
        reply_markup=ForceReply(
            selective=True, input_field_placeholder="Follow the sample"
        ),
        parse_mode=ParseMode.HTML,
    )

    return PLANDICT


async def check_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan = update.message.text
    LOGGER.info(plan)

    if plan != "":
        context.user_data["plan"] = plan
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Do you confirm your input?",
            reply_markup=ForceReply(
                selective=True, input_field_placeholder="YES or NO"
            ),
        )
        return PLANCONFIRM
    else:
        await update.message.reply_text(
            "Invalid input. Please try again.",
            reply_markup=ForceReply(
                selective=True, input_field_placeholder="Draft the details out"
            ),
        )
        return PLANDICT


async def confirm_plan_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    confirmation = update.message.text
    LOGGER.info(confirmation)
    chat_id = update.message.chat_id
    LOGGER.info(chat_id)
    user = update.effective_user
    user_id = str(user.id)

    if confirmation.lower() in ["yes", "y", "confirm", "ok"]:
        markup = await subscription_markup(user_id)
        try:
            data = json.loads(context.user_data.get("plan"))
            LOGGER.debug(data)
            if context.user_data.get("plan_id"):
                plan_id = context.user_data.get("plan_id")
                await SubscriptionPlanData().update_subscription_plan(plan_id, data)
            else:
                await SubscriptionPlanData().create_subscription_plan(data)
            await update.message.reply_text(
                f"Plan Created successfully!", reply_markup=markup
            )
            context.user_data.clear()
        except Exception as e:
            await update.message.reply_text(
                f"Failed to create plan detail: {str(e)}", reply_markup=markup
            )
    else:
        await update.message.reply_text(
            "Incorrect Plan Details. Retrying",
            reply_markup=ForceReply(
                selective=True,
                input_field_placeholder="Please retype the plan dictionary:",
            ),
        )
        return PLANDICT
    return ConversationHandler.END


COMDICT, COMCONFIRM = range(2)  # Define conversation states


async def update_company_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    # Start conversation passing the plan ID
    context.user_data["plan_id"] = "first"
    await context.bot.send_message(
        chat_id=chat_id,
        text="""
Please add the details like this:

<code>{
    "privateKey": "WalletPrivateKey",
    "passPhrase": "pass phrase if any",
    "depositWallet": "0xwalletaddress",
    "network": "MainNet"
}</code>

Ensure it follows the exact same format.

<pre>The amount is in a unified token value ETH, the network must be the main network, while the passphrase and private key are necessary for attaching your wallet address. You must have a private key or passphrase but note the passphrase is optional</pre>
        """,
        reply_markup=ForceReply(
            selective=True, input_field_placeholder="Follow the sample"
        ),
        parse_mode=ParseMode.HTML,
    )

    return COMDICT


async def add_company_dict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = update.callback_query
    chat_id = query.message.chat_id

    await context.bot.send_message(
        chat_id=chat_id,
        text="""
Please add the details like this:

<code>{
    "privateKey": "WalletPrivateKey",
    "passPhrase": "pass phrase if any",
    "depositWallet": "0xwalletaddress",
    "network": "MainNet"
}</code>

Ensure it follows the exact same format.

<code>The amount is in a unified token value ETH, the network must be the main network, while the passphrase and private key are necessary for attaching your wallet address. You must have a private key or passphrase but note the passphrase is optional</code>
        """,
        reply_markup=ForceReply(
            selective=True, input_field_placeholder="Follow the sample"
        ),
        parse_mode=ParseMode.HTML,
    )

    return COMDICT


async def check_com(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan = update.message.text
    LOGGER.info(plan)

    if plan != "":
        context.user_data["plan"] = plan
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Do you confirm your input?",
            reply_markup=ForceReply(
                selective=True, input_field_placeholder="YES or NO"
            ),
        )
        return COMCONFIRM
    else:
        await update.message.reply_text(
            "Invalid input. Please try again.",
            reply_markup=ForceReply(
                selective=True, input_field_placeholder="Draft the details out"
            ),
        )
        return COMDICT


async def confirm_comp_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    confirmation = update.message.text
    LOGGER.info(confirmation)
    chat_id = update.message.chat_id
    LOGGER.info(chat_id)
    user = update.effective_user
    user_id = str(user.id)

    if confirmation.lower() in ["yes", "y", "confirm", "ok"]:
        markup = await welcome_markup(user_id)
        try:
            data = json.loads(context.user_data.get("plan"))
            LOGGER.debug(data)
            # if context.user_data.get("plan_id"):
            #     plan_id = context.user_data.get("plan_id")
            #     await CompanyDataHandler().update_company_data(data)
            # else:
            await CompanyDataHandler().create_company_data(data)
            await update.message.reply_text(
                f"Company Details Created successfully!", reply_markup=markup
            )
            context.user_data.clear()
        except Exception as e:
            await update.message.reply_text(
                f"Failed to create plan detail: {str(e)}", reply_markup=markup
            )
            return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Incorrect Company Details. Retrying",
            reply_markup=ForceReply(
                selective=True,
                input_field_placeholder="Please retype the company dictionary:",
            ),
        )
        return COMDICT
    return ConversationHandler.END


TEAMDICT, TEAMCONFIRM = range(2)  # Define conversation states


async def update_team_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    # Start conversation passing the plan ID
    plan_id = query.data.split("-")[1]

    # Start conversation passing the plan ID
    context.user_data["plan_id"] = plan_id
    await context.bot.send_message(
        chat_id=chat_id,
        text="""
Please add the details like this:

<code>{
    "name": "John Doe",
    "email": "fridaymail@mail.com",
    "photo": "https://placeholder.co/400",
    "country": "Milan"
}</code>

Ensure it follows the exact same format.

<code>The email address must be valid, and the image must be a link of an image</code>
        """,
        reply_markup=ForceReply(
            selective=True, input_field_placeholder="Follow the sample"
        ),
        parse_mode=ParseMode.HTML,
    )

    return COMDICT


async def add_team_dict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = update.callback_query
    chat_id = query.message.chat_id

    await context.bot.send_message(
        chat_id=chat_id,
        text="""
Please add the details like this:

<code>{
    "name": "John Doe",
    "email": "fridaymail@mail.com",
    "photo": "https://placeholder.co/400",
    "country": "Milan"
}</code>

Ensure it follows the exact same format.

<code>The email address must be valid, and the image must be a link of an image</code>
        """,
        reply_markup=ForceReply(
            selective=True, input_field_placeholder="Follow the sample"
        ),
        parse_mode=ParseMode.HTML,
    )

    return TEAMDICT


async def check_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan = update.message.text
    LOGGER.info(plan)

    if plan != "":
        context.user_data["plan"] = plan
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Do you confirm your input?",
            reply_markup=ForceReply(
                selective=True, input_field_placeholder="YES or NO"
            ),
        )
        return TEAMCONFIRM
    else:
        await update.message.reply_text(
            "Invalid input. Please try again.",
            reply_markup=ForceReply(
                selective=True, input_field_placeholder="Draft the details out"
            ),
        )
        return TEAMDICT


async def confirm_team_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    confirmation = update.message.text
    LOGGER.info(confirmation)
    chat_id = update.message.chat_id
    LOGGER.info(chat_id)
    user = update.effective_user
    user_id = str(user.id)

    if confirmation.lower() in ["yes", "y", "confirm", "ok"]:
        markup = await welcome_markup(user_id)
        try:
            data = json.loads(context.user_data.get("plan"))
            LOGGER.debug(data)
            if context.user_data.get("plan_id"):
                plan_id = context.user_data.get("plan_id")
                await TeamsData().update_team(plan_id, data)
            else:
                await TeamsData().create_team(data)
            await update.message.reply_text(
                f"Team Details Created successfully!", reply_markup=markup
            )
            context.user_data.clear()
        except Exception as e:
            await update.message.reply_text(
                f"Failed to create team detail: {str(e)}", reply_markup=markup
            )
            return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Incorrect Team Details. Retrying",
            reply_markup=ForceReply(
                selective=True,
                input_field_placeholder="Please retype the team dictionary:",
            ),
        )
        return TEAMDICT
    return ConversationHandler.END


MESSAGE, MCONFIRM = range(2)  # Define conversation states


async def send_user_message_dict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = query.data.split("-")[1]
    context.user_data['user_id'] = user_id

    await context.bot.send_message(
        chat_id=chat_id,
        text="""
Please add the message like this:

<pre>
Whatever you wish to message the user
</pre>

Ensure it follows the exact same format.
        """,
        reply_markup=ForceReply(
            selective=True, input_field_placeholder="Follow the sample"
        ),
        parse_mode=ParseMode.HTML,
    )

    return MESSAGE


async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan = update.message.text
    LOGGER.info(plan)

    if plan != "":
        context.user_data['plan'] = plan
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Do you confirm your input?",
            reply_markup=ForceReply(
                selective=True, input_field_placeholder="YES or NO"
            ),
        )
    else:
        await update.message.reply_text(
            "Invalid input. Please try again.",
            reply_markup=ForceReply(
                selective=True, input_field_placeholder="Draft the details out"
            ),
        )
        return MESSAGE
    return MCONFIRM


async def confirm_message_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    confirmation = update.message.text
    chat_id = update.message.chat_id
    user = update.effective_user
    user_id = str(user.id)
    uid = context.user_data.get("user_id")

    mdict = context.user_data.get("plan")

    if confirmation.lower() in ["yes", "y", "confirm", "ok"]:
        markup = await welcome_markup(user_id)
        try:
            message = mdict
            LOGGER.debug(message)
            await context.bot.send_message(
                chat_id=uid, text=message, reply_markup=None, parse_mode=ParseMode.HTML
            )
        except Exception as e:
            LOGGER.debug(e)
            await update.message.reply_text(
                f"Failed to send message: {str(e)}", reply_markup=markup
            )
            return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Incorrect essage format. Retrying",
            reply_markup=ForceReply(
                selective=True,
                input_field_placeholder="Please retype the message dictionary:",
            ),
        )
        return MESSAGE
    return ConversationHandler.END


UBALANCE = range(1)

async def adjust_user_balance_dict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = query.data.split("-")[1]
    context.user_data['user_id'] = user_id

    await context.bot.send_message(
        chat_id=chat_id,
        text="""
How much do you want to add:
        """,
        reply_markup=ForceReply(
            selective=True, input_field_placeholder="just type the amount"
        ),
        parse_mode=ParseMode.HTML,
    )

    return UBALANCE

async def confirm_adjustment_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = float(update.message.text)
    chat_id = update.message.chat_id
    user = update.effective_user
    user_id = str(user.id)
    uid = context.user_data.get("user_id")
    data = {'earning': amount}
    await userData.update_user(uid, data)

    if amount:
        markup = await account_markup(user_id)
        try:
            message = "Successfully adjusted their amount"
            LOGGER.debug(message)
            await context.bot.send_message(
                chat_id=user_id, text=message, reply_markup=markup, parse_mode=ParseMode.HTML
            )
        except Exception as e:
            LOGGER.debug(e)
            await update.message.reply_text(
                f"Failed to adjust balance: {str(e)}", reply_markup=markup
            )
            return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Incorrect format. Retrying",
            reply_markup=ForceReply(
                selective=True,
                input_field_placeholder="Please retype the action again:",
            ),
        )
        return ConversationHandler.END


UCAP = range(1)

async def adjust_user_profit_cap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = query.data.split("-")[1]
    context.user_data['user_id'] = user_id

    await context.bot.send_message(
        chat_id=chat_id,
        text="""
How much should they make only:
        """,
        reply_markup=ForceReply(
            selective=True, input_field_placeholder="just type the amount"
        ),
        parse_mode=ParseMode.HTML,
    )

    return UBALANCE

async def confirm_cap_adjustment_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = float(update.message.text)
    chat_id = update.message.chat_id
    user = update.effective_user
    user_id = str(user.id)
    uid = context.user_data.get("user_id")

    await userData.update_user(uid, {'profit_cap': amount})

    if amount:
        markup = await account_markup(user_id)
        try:
            message = "Successfully adjusted their profit cap"
            LOGGER.debug(message)
            await context.bot.send_message(
                chat_id=user_id, text=message, reply_markup=markup, parse_mode=ParseMode.HTML
            )
        except Exception as e:
            LOGGER.debug(e)
            await update.message.reply_text(
                f"Failed to adjust profit cap: {str(e)}", reply_markup=markup
            )
            return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Incorrect format. Retrying",
            reply_markup=ForceReply(
                selective=True,
                input_field_placeholder="Please retype the action again:",
            ),
        )
        return ConversationHandler.END




async def start_mining(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    user_id = user.id

    chat_id = query.message.chat_id

    await userData.store_task_id(user_id)

    markup = await welcome_markup(user_id)

    await context.bot.send_message(
        chat_id=chat_id,
        text="Mining script is now activated and running in the background. Periodical alerts will be sent here to you.",
        reply_markup=markup,
    )


async def stop_mining(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    user_id = user.id

    chat_id = query.message.chat_id

    task_id = await userData.get_task_id(user_id)

    markup = await welcome_markup(user_id)
    if task_id is not None:
        await userData.stop_task_id(user_id)

        await context.bot.send_message(
            chat_id=chat_id,
            text="Mining script Has been stopped.",
            reply_markup=markup,
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="You do not have an active mining script running. Please start one immediately.",
            reply_markup=markup,
        )
