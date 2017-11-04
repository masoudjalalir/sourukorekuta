#!/usr/bin/env python
"""The Main bot file."""
import logging
from time import strftime, gmtime
import config
import sys
from telegram import Bot, Update, Message, Chat
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, \
    run_async
import dbops as db
import os
import userbot

try:
    mojurasu_prod = int(os.environ['MOJURASU_PROD'])
except KeyError:
    mojurasu_prod = 0

if mojurasu_prod:
    logging.basicConfig(
            format='sourukorekuta: %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)  # Time is not needed since journalctl has that
else:
    logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO, datefmt='%H:%M:%S', stream=sys.stdout)

logger = logging.getLogger(__name__)


update_id = None
name = 'Sourukorekutā'
jname = 'ソウルコレクター'
sourukorekuta_channel_id = '-1001113142718'


# TODO Add highest consecutive messages count


def msg_type(msg: Message):
    message_type = None
    if msg.entities:
        entity = msg.entities[0].type
        if entity not in ['bold', 'italic', 'code', 'pre', 'text_link']:
            if entity != 'text_mention':
                message_type = entity
            elif entity == 'text_mention':
                message_type = 'mention'
        else:
            message_type = 'text'
    elif msg.photo:
        message_type = 'photo'
    elif msg.sticker:
        message_type = 'sticker'
    elif msg.document:
        message_type = 'document'
        filename = msg.document.file_name
        mimetype = msg.document.mime_type
        if filename == 'giphy.mp4':
            message_type = 'gif'
        elif mimetype.split('/')[0] == 'video':
            message_type = 'video'
        else:
            message_type = 'document'
    elif msg.voice:
        message_type = 'voice'
    else:
        message_type = 'text'
    return message_type


def normal_message(bot: Bot, update: Update) -> None:
    msg = update.message  # type: Message
    if update.effective_chat.type in ['group', 'supergroup']:
        msgtype = msg_type(msg)
        # msg.reply_text(msgtype)
        db.add_user(update.effective_user)
        db.addgroup(update.effective_chat)
        db.update_user(update.effective_user, update.effective_chat, msgtype)


def check_group(bot: Bot, update: Update) -> None:
    msg = update.effective_message  # type: Message
    for user in msg.new_chat_members:
        if user.id == bot.get_me().id:  # the id of the bot itself
            db.addgroup(update.effective_chat)
        else:
            db.update_user(user,
                           update.effective_chat,
                           None,
                           joindate=int(msg.date.timestamp()))


def start(bot: Bot, update: Update) -> None:
    pass


def bothelp(bot: Bot, update: Update) -> None:
    pass


def ping(bot: Bot, update: Update) -> None:
    update.message.reply_text('ポン！')
    if update.effective_chat.type != 'private':
        bot.delete_message(chat_id=update.effective_chat.id,
                           message_id=update.effective_message.message_id)


def info(bot: Bot, update: Update) -> None:
    if update.effective_chat.type != 'private':
        msg = update.message  # type: Message
        if msg.reply_to_message:
            userinfo = db.get_user(bot, msg.reply_to_message.from_user.id,
                        update.effective_chat.id)
        else:
            userinfo = db.get_user(bot, update.effective_user.id,
                                   update.effective_chat.id)

        msg_list = []
        msg_list.append(
                f"Name: {userinfo['first_name']} {userinfo['last_name']}")
        if userinfo['username'] != 'None':
            msg_list.append(
                    f"Username: {userinfo['username']}")
        if userinfo['joined'] != 'None':
            joined = strftime('%d.%m.%Y', gmtime(int(userinfo['joined'])))
            msg_list.append(
                f"Joined: {joined}")
        msg_list.append(
                f"Language: {userinfo['language_code']}")
        msg_list.append(
                f"Status: {userinfo['status']}")
        msg_list.append(
                f"UserID: {userinfo['user_id']}")
        msg_list.append(
                f"Total Messages:")
        msg_list.append(
                f"Message Types:")
        if userinfo['count_text'] != '0':
            msg_list.append(
                    f"  Texts: {userinfo['count_text']}")
        if userinfo['count_mention'] != '0':
            msg_list.append(
                    f"  Mentions: {userinfo['count_mention']}")
        if userinfo['count_hashtag'] != '0':
            msg_list.append(
                    f"  Hashtags: {userinfo['count_hashtag']}")
        if userinfo['count_bot_command'] != '0':
            msg_list.append(
                    f"  Bot Commands: {userinfo['count_bot_command']}")
        if userinfo['count_url'] != '0':
            msg_list.append(
                    f"  URLs: {userinfo['count_url']}")
        if userinfo['count_email'] != '0':
            msg_list.append(
                    f"  E-Mails: {userinfo['count_email']}")
        if userinfo['count_photo'] != '0':
            msg_list.append(
                    f"  Photos: {userinfo['count_photo']}")
        if userinfo['count_document'] != '0':
            msg_list.append(
                    f"  Documents: {userinfo['count_document']}")
        if userinfo['count_sticker'] != '0':
            msg_list.append(
                    f"  Stickers: {userinfo['count_sticker']}")
        if userinfo['count_gif'] != '0':
            msg_list.append(
                    f"  GIFs: {userinfo['count_gif']}")
        if userinfo['count_video'] != '0':
            msg_list.append(
                    f"  Video: {userinfo['count_video']}")
        if userinfo['count_voice'] != '0':
            msg_list.append(
                    f"  Voice Messages: {userinfo['count_voice']}")
        message = '\n'.join(msg_list)
        msg.reply_text(message)
        bot.delete_message(chat_id=update.effective_chat.id,
                           message_id=update.effective_message.message_id)


def stats(bot: Bot, update: Update) -> None:
    if update.effective_chat.type != 'private':
        group = db.get_group(update.effective_chat.id)
        groupname = update.effective_chat.title

        update.message.reply_text('This Group has ' +
                                  str(group['active_members_count']) +
                                  ' active souls.')
        bot.delete_message(chat_id=update.effective_chat.id,
                           message_id=update.effective_message.message_id)


def execution_warn(bot: Bot, update: Update) -> None:
    chat = update.effective_chat  # type: Chat
    msg = update.effective_message  # type: Message

    if chat.type != 'private':
        admins = chat.get_administrators()
        admins = [admin.user.id for admin in admins]
        if update.effective_user.id in admins:
            channel = userbot.get_channel(chat.title)
            all_user_ids = userbot.get_participants_ids(channel)
            # all_user_ids = userbot.get_participants_ids(0, 0)
            active_user_ids = db.get_active_user_ids(chat.id)
            lurkers = [lurker for lurker in all_user_ids
                       if lurker not in active_user_ids]
            lurkersmsg = [f"""[{bot.get_chat_member(
                                    chat.id,
                                    l).user.first_name.replace(
                                    '[', '').replace(
                                    ']',
                                     '')}](tg://user?id={str(l)})""".strip()
                          for l in lurkers]
            # msg.reply_text(lurkers, parse_mode='Markdown')
            if not lurkersmsg:
                msg.reply_text('I detected no lurking Souls')
                bot.delete_message(chat_id=chat.id,
                                   message_id=msg.message_id)
                return
            fullmsg = 'If you are on the list below you count as a lurker and will be kicked when we decide its time to do so. There is no need to discuss if it is neccesary or not.\n\n' + ', '.join(lurkersmsg)
            msg.reply_text(fullmsg, parse_mode='Markdown')
            bot.delete_message(chat_id=chat.id,
                               message_id=msg.message_id)


@run_async
def execution(bot: Bot, update: Update) -> None:
    chat = update.effective_chat  # type: Chat
    msg = update.message  # type: Message

    if chat.type != 'private':
        admins = chat.get_administrators()
        admins = [admin.user.id for admin in admins]
        if update.effective_user.id in admins:
            channel = userbot.get_channel(chat.title)
            all_user_ids = userbot.get_participants_ids(channel)
            # all_user_ids = userbot.get_participants_ids(0, 0)
            active_user_ids = db.get_active_user_ids(chat.id)
            lurkers = [lurker for lurker in all_user_ids
                       if lurker not in active_user_ids]


            for lurker in lurkers:
                userbot.send_message_to_channel(
                        f"""Kicked {bot.get_chat_member(
                                    chat.id,
                                    lurker).user.first_name} | {str(lurker)}
                                    """
                        )
                userbot.kick_member(channel, lurker)

        bot.delete_message(chat_id=update.effective_chat.id,
                           message_id=update.effective_message.message_id)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    if mojurasu_prod:
        logger.info('Running in Production')
    else:
        logger.info('Running in Dev')
    updater = Updater(config.bottoken)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', bothelp))
    dp.add_handler(CommandHandler('ping', ping))
    dp.add_handler(CommandHandler(['joho', 'info'], info))
    dp.add_handler(CommandHandler(['tokei', 'tamashi', 'stats'], stats))
    dp.add_handler(CommandHandler(['jikkokeikoku', 'executionwarn'], execution_warn))
    dp.add_handler(CommandHandler(['jikko', 'execution'], execution))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members,
                                  check_group))
    dp.add_handler(MessageHandler(Filters.all, normal_message))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
