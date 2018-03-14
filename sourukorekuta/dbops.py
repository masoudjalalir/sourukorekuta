"""The Module interacting with the db."""
import userbot
import config
from telegram import Chat, Bot, ChatMember
from telegram.user import User
import psycopg2 as ps2
from psycopg2.extensions import connection as ps2conn
from psycopg2.extensions import cursor as ps2cursor

curdir = '/'.join(__file__.split('/')[:-1])


def runsql(sql: str, data: tuple = (), mogrify: bool = False) -> str:
    conn_string = f"""host='{config.db_host}'
                      dbname='{config.db_name}'
                      user='{config.db_user}' 
                      password='{config.db_password}' 
                      port='{config.db_port}'"""
    conn = ps2.connect(conn_string)  # type: ps2conn
    c = conn.cursor()  # type: ps2cursor
    if mogrify:
        return c.mogrify(sql, data)
    c.execute(sql, data)
    # result = c.mogrify(sql, data)
    try:
        result = c.fetchall()
    except ps2.ProgrammingError:
        result = None
    conn.commit()
    return result


def addgroup(chat: Chat) -> None:
    if chat.type != 'private':
        chatname = chat.title
    else:
        return
    chatid = str(chat.id).strip()

    if not runsql("SELECT id FROM sourukorekuta.groups WHERE id = %s;",
                  (chatid,)):
        channel = userbot.get_channel(chat.title)
        channel_id = channel.id  # type: int
        access_hash = channel.access_hash  # type: int
        runsql("""INSERT INTO sourukorekuta.groups (id,
                                                    name,
                                                    channel_id,
                                                    access_hash
                                                    ) VALUES (
                                                    %s,
                                                    %s,
                                                    %s,
                                                    %s);""", (
                                                    chatid,
                                                    chatname,
                                                    channel_id,
                                                    access_hash))


def update_user(user: User, chat: Chat, msgtype: str, joindate: int = 0) -> None:
    if chat.type == 'private':
        return
    userid = str(user.id).strip()
    groupid = str(chat.id).strip()

    if not runsql("""SELECT sourukorekuta.statistics.user_id,
                            sourukorekuta.statistics.group_id 
                            FROM sourukorekuta.statistics 
                            WHERE sourukorekuta.statistics.user_id = %s 
                            AND sourukorekuta.statistics.group_id = %s;
                            """, (userid, groupid)):

        runsql("""INSERT INTO sourukorekuta.statistics (user_id,
                                             group_id,
                                             count_text,
                                             count_mention,
                                             count_hashtag,
                                             count_bot_command,
                                             count_url,
                                             count_email,
                                             count_photo,
                                             count_sticker,
                                             count_gif,
                                             count_video,
                                             count_voice,
                                             joindate,
                                             count_document) VALUES ( 
                                             %s,
                                             %s,
                                              0,
                                              0,
                                              0,
                                              0,
                                              0,
                                              0,
                                              0,
                                              0,
                                              0,
                                              0,
                                              0,
                                              %s,
                                              0);""",
               (userid, groupid, joindate))
    else:
        runsql("""UPDATE sourukorekuta.statistics 
                  SET count_{} = count_{} + 1 
                  WHERE user_id = %s
                  AND group_id = %s;""".format(msgtype, msgtype),
               (userid, groupid))


def add_user(user: User) -> None:
    userid = user.id
    fname = user.first_name
    lname = user.last_name
    uname = user.username
    if not runsql("SELECT id FROM sourukorekuta.users WHERE id = '%s';",
                  (userid, )):
        runsql("""INSERT INTO sourukorekuta.users (
                                                  id,
                                                  first_name,
                                                  last_name,
                                                  username
                                                  ) VALUES (
                                                  %s,
                                                  %s,
                                                  %s,
                                                  %s);""", (
                                                  userid,
                                                  fname,
                                                  lname,
                                                  uname))


def get_active_user_ids(groupid: int) -> list:
    chatid = str(groupid).strip()
    active_members = runsql("""SELECT user_id 
                               FROM sourukorekuta.statistics 
                               WHERE group_id = %s;""", (chatid,))
    active_members = [int(user[0]) for user in active_members]
    return active_members


def get_lurker_ids(groupid: int) -> list:
    chatid = str(groupid).strip()
    lurkers = runsql("""SELECT user_id
                              FROM sourukorekuta.statistics 
                              WHERE group_id = %s
                              AND count_text = 0
                              OR count_mention = 0
                              OR count_hashtag = 0
                              OR count_bot_command = 0
                              OR count_url = 0
                              OR count_email = 0
                              OR count_photo = 0
                              OR count_sticker = 0
                              OR count_gif = 0
                              OR count_video = 0
                              OR count_voice = 0
                              OR count_document = 0;""", (chatid, ))[0][0]
    lurkers = [user[0] for user in lurkers]
    return lurkers


def get_user(bot: Bot, userid: int, groupid: int) -> dict:
    chatid = str(groupid).strip()
    userrow = runsql("""SELECT * FROM sourukorekuta.statistics 
                        WHERE user_id = %s AND group_id = %s""",
                        (str(userid), chatid))[0]
    user = bot.get_chat_member(userrow[1], userrow[0])  # type: ChatMember
    userdict = {
        'first_name': str(user.user.first_name),
        'last_name': str(user.user.last_name),
        'username': str(user.user.username),
        'language_code': str(user.user.language_code),
        'status': str(user.status),
        'user_id': str(userrow[0]),
        'group_id': str(userrow[1]),
        'count_text': str(userrow[2]),
        'count_mention': str(userrow[3]),
        'count_hashtag': str(userrow[4]),
        'count_bot_command': str(userrow[5]),
        'count_url': str(userrow[6]),
        'count_email': str(userrow[7]),
        'count_photo': str(userrow[8]),
        'count_sticker': str(userrow[9]),
        'count_gif': str(userrow[10]),
        'count_video': str(userrow[11]),
        'count_voice': str(userrow[12]),
        'joined': str(userrow[13]),
        'count_document': str(userrow[14])
        }
    return userdict


def get_group(groupid: int) -> dict:
    chatid = str(groupid).strip()
    grouptuple = runsql("""SELECT * FROM sourukorekuta.groups 
                           WHERE id = %s""", (chatid, ))[0]
    active_members = runsql("""SELECT count(user_id) 
                              FROM sourukorekuta.statistics 
                              WHERE group_id = %s
                              AND count_text > 0
                              OR count_mention > 0
                              OR count_hashtag > 0
                              OR count_bot_command > 0
                              OR count_url > 0
                              OR count_email > 0
                              OR count_photo > 0
                              OR count_sticker > 0
                              OR count_gif > 0
                              OR count_video > 0
                              OR count_voice > 0
                              OR count_document > 0;""", (chatid, ))[0][0]

    lurkers = runsql("""SELECT count(user_id) 
                              FROM sourukorekuta.statistics 
                              WHERE group_id = %s
                              AND count_text = 0
                              OR count_mention = 0
                              OR count_hashtag = 0
                              OR count_bot_command = 0
                              OR count_url = 0
                              OR count_email = 0
                              OR count_photo = 0
                              OR count_sticker = 0
                              OR count_gif = 0
                              OR count_video = 0
                              OR count_voice = 0
                              OR count_document = 0;""", (chatid, ))[0][0]
    group = {'chatid': grouptuple[0],
             'title': grouptuple[1],
             'channel_id': grouptuple[2],
             'access_hash': grouptuple[3],
             'active_members_count': active_members,
             'lurkers': lurkers}
    return group


def whitelist_user(userid: int, groupid: int, remove: bool = False) -> None:
    if not remove:
        if not runsql("""SELECT * FROM sourukorekuta.whitelist 
                         WHERE user_id = %s AND chat_id = %s;""",
                      (str(userid), str(groupid))):
            runsql("""INSERT INTO sourukorekuta.whitelist(user_id, chat_id) VALUES (%s, %s)""", (str(userid), str(groupid)))
        else:
            return
    elif remove:
        if runsql(
                """SELECT * FROM sourukorekuta.whitelist 
                   WHERE user_id = %s AND chat_id = %s;""",
                (str(userid), str(groupid))):
            runsql(
                    """DELETE FROM sourukorekuta.whitelist 
                       WHERE user_id = %s AND chat_id = %s;""",
                    (str(userid), str(groupid)))


def get_whitelisted_users(groupid: int) -> list:
    chatid = str(groupid).strip()
    whitelisted_members = runsql("""SELECT user_id 
                               FROM sourukorekuta.whitelist 
                               WHERE chat_id = %s;""", (str(groupid),))
    whitelisted_members = [int(user[0]) for user in whitelisted_members]
    return whitelisted_members
