#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Business logic - gets requestin from Slack, does stuff, sends requests back to Slack.

Notes for developers who want to add or change functionality: You're in the right module.
    * If you were to run this behind a server (Flask would work well) instead of behind AWS Lambda,
    it would be quite easy. Make your server take a request from Slack. You are responsible
    all the way up to parsing Slack's request parameters so they are a tidy dict.
    This module - handle_slack_request, specifically - will take it from there.
    * If you were to port to another messaging client, this is the "guts" that you would port.
"""
import json
import random

from funcy import memoize, retry
import slacker

from messages import generate_random_introduction_text
import yobot_config_and_secrets



# Since we expect users to freely modify the yobot_config_and_secrets file, let's eagerly
# affirm that these attributes are set.
# also aliasing them because "YOBOT_" namespacing not needed in the code...

BOT_USER_NAME = yobot_config_and_secrets.YOBOT_BOTUSER_NAME
BOT_USER_TOKEN = yobot_config_and_secrets.YOBOT_BOTUSER_TOKEN
SLACK_WEBHOOK_TOKEN = yobot_config_and_secrets.YOBOT_WEBHOOK_TOKEN
SLACK_SLASHCOMMAND_TOKEN = yobot_config_and_secrets.YOBOT_SLASHCOMMAND_TOKEN
BROADCAST_CHANNEL_NAME = yobot_config_and_secrets.YOBOT_BROADCASTCHANNEL_NAME
DEBUG = yobot_config_and_secrets.YOBOT_DEBUG
if unicode(DEBUG).lower() == "false":
    DEBUG = False

WEBHOOK = 'webhook'
SLASHCOMMAND = 'slash_command'
AUTH_TOKENS_EXPECTED_BY_REQUEST_TYPE = {
    WEBHOOK: SLACK_WEBHOOK_TOKEN,
    SLASHCOMMAND: SLACK_SLASHCOMMAND_TOKEN
}

SENSITIVE_TOKENS_TO_SANITIZE = (SLACK_SLASHCOMMAND_TOKEN, BOT_USER_TOKEN, SLACK_WEBHOOK_TOKEN)

COMMAND_BROADCAST = "broadcast"

SLACK_CALL_EXPECTED_KEYS_COMMON = [
    'token',
    'team_id',
    'team_domain',
    'channel_id',
    'channel_name',
    'user_id',
    'user_name',
    # 'timestamp',
    # 'text',

    # btw - does not include 'command' or 'trigger_word' because those are exclusive to
    # Slash Command or Webhook request APIs specifically.
]

FIELDNAME_USER_ID = 'id'
FIELDNAME_USER_NAME = 'name'

NULLHANDLE = "nullhandle"


@memoize
def get_slack_api():
    slack_api = slacker.Slacker(BOT_USER_TOKEN)
    return slack_api


# @retry(3)
def handle_slack_request(params_from_slack_request):
    """ Main entry point. Validate input, authenticate caller, route to handler.
    :param params_from_slack_request:
    :return: can be a few kinds of output; this CAN be returned to Slack and shown to end-user
        so do NOT put any sensitive stuff in it ;)
    """
    _validate_config_or_die()
    validate_input_from_slack_or_die(params_from_slack_request)
    get_slack_request_type_and_authenticate(params_from_slack_request)

    slack_request_type = get_slack_request_type(params_from_slack_request)
    text_that_could_contain_command = ""
    if slack_request_type == SLASHCOMMAND:
        text_that_could_contain_command += " " + params_from_slack_request.get(u'command')
    text_that_could_contain_command += " " + params_from_slack_request.get(u'text', u'<None>')

    if COMMAND_BROADCAST in text_that_could_contain_command:
        # TODO(hangtwenty) refactor to function; move message to messages.py ?
        slack_api = get_slack_api()
        broadcast_channel_name = BROADCAST_CHANNEL_NAME  # .replace("#", "%23")
        msg = (
            "*Hello!* I'm yobot. I introduce people to each other. :smiley: \n\n"
            "Want to try? *Type _/yobot_ anywhere in Slack.* "
            "Nobody else will see that you've typed /yobot, the command goes straight to me. "
            "It's silent. "
            "I'll choose another person who has Slack, randomly. "
            "Then I'll send *you* a private message with their name. "
            "I'll give you an idea to break the ice. :coffee: :beers: :computer: "
            "It's just for you, and there's no pressure to follow up. \n\n"
            "Try it! *Type _/yobot_ and meet someone new.*\n")
        try:
            slack_api.chat.post_message(
                broadcast_channel_name,
                msg,
                as_user=BOT_USER_NAME,
            )
        except Exception as e:
            raise Exception(
                e.message + " ... broadcast_channel_name = {}".format(broadcast_channel_name))
        return_value_for_caller = u"yobot introduced herself to {}".format(broadcast_channel_name)
    else:
        # default command.
        return_value_for_caller = random_introduction(params_from_slack_request)

    # in all cases ... if the incoming request was actually a Webhook, we don't really
    # want to return ANY "output" (weird stuff happens if we do return output,
    # like just 1 letter output, and output in a PUBLIC message to caller channel... not sure why)
    if get_slack_request_type(params_from_slack_request) == WEBHOOK:
        return_value_for_caller = True

    return return_value_for_caller


def random_introduction(params_from_slack_request):
    """ Handle the plain `/yobot` case where someone wants a random introduction/prompt.
    """
    slack_api = get_slack_api()

    user_id_who_called_yobot = params_from_slack_request['user_id']
    if not user_id_who_called_yobot:
        raise ValueError("Can't message you: no user_id specified.")

    users_list_response = slack_api.users.list()
    users = users_list_response.body['members']
    user_to_introduce = choose_a_user(users)
    introduce_username = user_to_introduce.get(FIELDNAME_USER_NAME, None)
    # TODO(hangwenty) case where user will be introduced to themself is not handled yet.
    # should be handled. With a funny easter egg.
    introduce_readable_name = _get_readable_name(user_to_introduce)
    if not introduce_readable_name:
        raise ValueError("Somehow the user I chose has NO real_name, username, or email. "
                         "This should never happen but it did.")

    msg = generate_random_introduction_text(
        introduce_readable_name,
        introduce_username,
        introducing_to_oneself=user_id_who_called_yobot == user_to_introduce[FIELDNAME_USER_ID])

    if DEBUG:
        debug_msg = _get_debug_message(params_from_slack_request)
        msg = debug_msg + msg

    # ensure-open a direct-message channel with the user who called, then message them
    channel_im_with_caller = \
        slack_api.im.open(user=user_id_who_called_yobot).body['channel']['id']
    slack_api.chat.post_message(
        channel_im_with_caller,
        msg,
        as_user=BOT_USER_NAME,
    )
    return_msg_for_slash_command = \
        u"{as_user} just sent you a private message. Take a look.".format(
            as_user=BOT_USER_NAME, introduce_username=introduce_username)
    return return_msg_for_slash_command


class UserNotGoodToMessageException(ValueError):
    """ Raised when a user isn't good to message, for our purposes.
    """


@retry(10, errors=UserNotGoodToMessageException)
def choose_a_user(users):
    """ Chose a user from list (pseudo)randomly. Raise exception if deleted or has no username.

    @retry decorator means normally exception won't reach end-user; we'll keep choosing up to
    N times until we find a good one.

    :param users: list of user-type JSON objects from Slack api (like users.list API method)
    :return: a single user-type JSON object
    """
    introduce_user = random.choice(users)

    _debug_user_string = u"This user (id={} and email={}) ".format(
        introduce_user.get(FIELDNAME_USER_ID, None),
        introduce_user.get('email', None))

    if introduce_user[FIELDNAME_USER_NAME] == NULLHANDLE:
        # This can happen, it's seemingly when someone registered sorta but didn't finish.
        raise UserNotGoodToMessageException(
            u"{} has a null username ({!r}).".format(_debug_user_string, NULLHANDLE))

    if introduce_user['deleted']:
        raise UserNotGoodToMessageException("{} has been deleted.".format(_debug_user_string))

    return introduce_user


def _get_readable_name(user):
    """ Try to get a name besides the @handle, hopefully readable (like their real name).

    Falls back to other things, because if they don't have a real name listed,

    :param user: the user-type JSON object from Slack API.
    :return:
    """
    username = user[FIELDNAME_USER_NAME]
    profile = user['profile']
    real_name = profile.get('real_name', None)
    email = profile.get('email', None)
    skype = profile.get('skype', None)
    if skype:
        leftward_arrow_emoji = u"⬅️"
        skype = u"{} ({} Skype username)".format(skype, leftward_arrow_emoji)
    introduce_readable_name = real_name or email or skype or username
    return introduce_readable_name


@memoize
def _validate_config_or_die():
    """ Die if any essential configuration is not set. (If it's None or 0.)
    :raise: ValueError
    """
    if not BOT_USER_TOKEN:
        raise ValueError("Need a token for the bot user in order to make API calls to Slack.")
    if not BOT_USER_NAME:
        raise ValueError("You should set a bot username.")
    if not SLACK_WEBHOOK_TOKEN and not SLACK_SLASHCOMMAND_TOKEN:
        # TODO(hangtwenty) clean up this verbose error message; move this "dev-only" suggestion
        # to README.
        raise ValueError("Need at least one of the two from-Slack auth tokens to be configured, "
                         "in order to _authenticate the caller. ")
    return True


def _authenticate(slack_request_type, token):
    """ Authenticate an incoming `token` against a privileged token.

    Tokens allowed are set by configuration.

    :param token: The `token` parameter from the incoming request. This must equal
        one of the two configured tokens for "Outgoing Webhook" or "Slash Command"
    :raise: ValueError
    """
    authed = False

    if slack_request_type == WEBHOOK:
        if SLACK_SLASHCOMMAND_TOKEN:
            expected_token = AUTH_TOKENS_EXPECTED_BY_REQUEST_TYPE[WEBHOOK]
            if expected_token and token == expected_token:
                authed = True

    elif slack_request_type == SLASHCOMMAND:
        expected_token = AUTH_TOKENS_EXPECTED_BY_REQUEST_TYPE[SLASHCOMMAND]
        if expected_token and token == expected_token:
            authed = True

    if not authed:
        raise ValueError("Forbidden.")

    return authed


def get_slack_request_type(params_from_slack):
    """ Supported requests from Slack are "Slash Command" and "Outgoing Webhook" . Which is this?
    :param params_from_slack:
    :return:
    """
    if 'command' in params_from_slack:
        return SLASHCOMMAND
    elif 'trigger_word' in params_from_slack:
        return WEBHOOK
    else:
        raise ValueError("Invalid call (params did not not match Slack API).")


def get_slack_request_type_and_authenticate(params_from_slack):
    request_type = get_slack_request_type(params_from_slack)
    _authenticate(request_type, params_from_slack['token'])


def validate_input_from_slack_or_die(params_from_slack):
    """ Just because it seems "right," fully validate the request params from Slack expected.

    Because input validation is a good idea ... validate the param keys in the Slack call.
    - https://api.slack.com/getting-started
    - https://api.slack.com/outgoing-webhooks
    - https://api.slack.com/slash-commands

    :param params_from_slack: Parsed parameters POST'd by Slack. These will be the same
        params whether the POST comes from an "Outgoing Webhook" or a "Slash Command" integration.
    :raise: ValueError
    """
    for key in SLACK_CALL_EXPECTED_KEYS_COMMON:
        if key not in params_from_slack:
            raise ValueError(
                "Invalid call (params did not not match Slack API). Expected key {!r} to be in "
                "params incoming from Slack call.".format(key))


def _get_debug_message(params_from_slack):
    """
    :param params_from_slack: params from slack. (FORMPARAMS field.) What Slack POSTs.
    :return: Event, formatted nicely for adding into Slack message,
        also with any known-sensitive auth tokens removed
    """
    dumped = json.dumps(params_from_slack, indent=2)
    sanitized = _sanitize(dumped)
    debug_msg = u"```\n[DEBUG]\nparams_from_slack = {}\n```\n".format(sanitized)
    return debug_msg


def _sanitize(output_that_end_user_might_see):
    for sensitive_string in SENSITIVE_TOKENS_TO_SANITIZE:
        output_that_end_user_might_see = output_that_end_user_might_see.replace(sensitive_string,
            '<redacted>')

    # double check...
    for sensitive_string in SENSITIVE_TOKENS_TO_SANITIZE:
        assert not sensitive_string in output_that_end_user_might_see

    return output_that_end_user_might_see
