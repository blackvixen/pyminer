import html
import json
import traceback
from minecoequity.commands.commands import (
    about_command,
    accept_terms,
    add_company_dict,
    add_name,
    add_plan_dict,
    add_team_dict,
    adjust_user_balance_dict,
    adjust_user_profit_cap,
    cancel_command,
    check_com,
    check_message,
    check_name,
    check_plan,
    check_team,
    confirm_adjustment_details,
    confirm_cap_adjustment_details,
    confirm_comp_details,
    confirm_details,
    confirm_message_details,
    confirm_plan_details,
    confirm_team_details,
    connect_command,
    decline_terms,
    faq_command,
    help_command,
    home_command,
    remove_team,
    send_user_message_dict,
    services_command,
    start_mining,
    stop_mining,
    sub_plan,
    update_company_button,
    update_plan_button,
    update_plan_callback,
    update_team_button,
    view_plans,
    view_users,
    welcome_command,
    view_teams,
    view_account,
)


from warnings import filterwarnings
from telegram import Update
from telegram.ext import (
    Application,
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackContext,
)
from telegram.warnings import PTBUserWarning
from telegram.constants import ParseMode

from ..utils.load_env import DEVELOPER_CHAT_ID, TOKEN, USERNAME
from ..utils.logger import LOGGER
from ..utils.constants import help_message


filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)


def handle_response(text: str) -> str:
    processed_text = text.lower()

    if any(
        word in processed_text for word in ["assist me", "support", "commands", "help"]
    ):
        return help_message

    return text


async def handle_message(update: Update, context: CallbackContext) -> None:
    message_type: str = (
        update.message.chat.type
    )  # to determine the chat type private or group
    CHAT_ID = update.message.chat.id
    text: str = update.message.text  # message that will be processed
    LOGGER.debug(f"user: {update.message.chat.id} in {message_type}: '{text}'")

    if message_type == "private":
        response: str = handle_response(text)
        await context.bot.send_message(
            chat_id=CHAT_ID, text=response, parse_mode=ParseMode.HTML
        )
    else:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text="Sorry I can not be in a group and would do nothing for you here.",
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.

    update_str = update.to_dict() if isinstance(update, Update) else str(update)

    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


async def log_error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    This logs the error from the bot to the console

    return: error log
    """
    LOGGER.error(f"Update: {update}\n\n caused error {context.error}")


def telegram_setup() -> None:
    LOGGER.info("Initializing MinecoEquityBot")
    LOGGER.info(f"Bot Name: {USERNAME}")
    app = Application.builder().token(TOKEN).build()
    LOGGER.info("App Initialized and Ready")

    app.add_handler(CommandHandler("start", welcome_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("services", services_command))
    app.add_handler(CommandHandler("faq", faq_command))
    app.add_handler(CommandHandler("cancel", cancel_command))

    # button call back
    app.add_handler(CallbackQueryHandler(home_command, pattern=r"^home$"))
    app.add_handler(CallbackQueryHandler(start_mining, pattern=r"^start$"))
    app.add_handler(CallbackQueryHandler(stop_mining, pattern=r"^stop$"))
    app.add_handler(CallbackQueryHandler(about_command, pattern=r"^about$"))
    app.add_handler(CallbackQueryHandler(help_command, pattern=r"^help$"))
    app.add_handler(CallbackQueryHandler(services_command, pattern=r"^services$"))
    app.add_handler(CallbackQueryHandler(faq_command, pattern=r"^faq$"))
    app.add_handler(CallbackQueryHandler(connect_command, pattern=r"^connect$"))
    app.add_handler(CallbackQueryHandler(accept_terms, pattern=r"^accept_terms$"))
    app.add_handler(CallbackQueryHandler(decline_terms, pattern=r"^decline_terms$"))
    app.add_handler(CallbackQueryHandler(sub_plan, pattern=r"^subscribe_now-"))
    app.add_handler(CallbackQueryHandler(view_account, pattern=r"^view_account$"))
    app.add_handler(CallbackQueryHandler(view_plans, pattern=r"^view_plans$"))
    app.add_handler(CallbackQueryHandler(view_teams, pattern=r"^view_teams$"))
    app.add_handler(CallbackQueryHandler(view_users, pattern=r"^users$"))
    app.add_handler(CallbackQueryHandler(remove_team, pattern=r"^delete_team-"))
    app.add_handler(
        CallbackQueryHandler(update_plan_callback, pattern=r"^can_withdraw-")
    )
    app.add_handler(CallbackQueryHandler(update_plan_callback, pattern=r"^admin-"))

    # conversation handler
    NAME, CONFIRM = range(2)  # Define conversation states
    add_update_details_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_name, pattern=r"^u_profile$"),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~(filters.COMMAND), check_name)],
            CONFIRM: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND), confirm_details)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(add_update_details_handler)

    PLANDICT, PLANCONFIRM = range(2)  # Define conversation states
    add_plan_details_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_plan_dict, pattern=r"^sub$"),
            CallbackQueryHandler(update_plan_button, pattern=r"^u_plan-"),
        ],
        states={
            PLANDICT: [MessageHandler(filters.TEXT & ~(filters.COMMAND), check_plan)],
            PLANCONFIRM: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND), confirm_plan_details)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(add_plan_details_handler)

    TEAMDICT, TEAMCONFIRM = range(2)  # Define conversation states

    add_team_details_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(update_team_button, pattern=r"^update_team-"),
            CallbackQueryHandler(add_team_dict, pattern=r"^add_teams$"),
        ],
        states={
            TEAMDICT: [MessageHandler(filters.TEXT & ~(filters.COMMAND), check_team)],
            TEAMCONFIRM: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND), confirm_team_details)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(add_team_details_handler)

    COMDICT, COMCONFIRM = range(2)  # Define conversation states

    add_company_details_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(update_company_button, pattern=r"^update_company$"),
        ],
        states={
            COMDICT: [MessageHandler(filters.TEXT & ~(filters.COMMAND), check_com)],
            COMCONFIRM: [
                MessageHandler(filters.TEXT & ~(filters.COMMAND), confirm_comp_details)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(add_company_details_handler)

    MESSAGE, MCONFIRM = range(2)  # Define conversation states

    add_message_details_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(send_user_message_dict, pattern=r"^send_message"),
        ],
        states={
            MESSAGE: [MessageHandler(filters.TEXT & ~(filters.COMMAND), check_message)],
            MCONFIRM: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND), confirm_message_details
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(add_message_details_handler)

    UBALANCE = range(1)

    add_balance_adjuster_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(adjust_user_balance_dict, pattern=r"^adjust_balance-"),
        ],
        states={
            UBALANCE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND), confirm_adjustment_details
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(add_balance_adjuster_handler)

    UCAP = range(1)

    add_balance_adjuster_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(adjust_user_profit_cap, pattern=r"^set_cap-"),
        ],
        states={
            UCAP: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND), confirm_cap_adjustment_details
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    app.add_handler(add_balance_adjuster_handler)

    # handle messages
    LOGGER.info("Message handler initiated")
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # error commands
    app.add_error_handler(log_error)
    app.add_error_handler(error_handler)
    app.run_polling(allowed_updates=Update.ALL_TYPES)
