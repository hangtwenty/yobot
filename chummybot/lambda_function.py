#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Translates from AWS Lambda event to Slack call.
"""
import json
import os
import pprint
import re

from funcy import merge
import slacker

HOST = 'slack.com'
BASE_URL = '/api/'

SLACK_API_ARGUMENTS_DEFAULT = {
    'channel': '#chummybot',
    'as_user': 'chummybot',
}

RE_FIRST_CAP = re.compile('(.)([A-Z][a-z]+)')
RE_ALL_CAP = re.compile('([a-z0-9])([A-Z])')

slack = slacker.Slacker(os.environ["CHUMMYBOT_API_TOKEN"])


def snake_case(s):
    """ Convert CamelCase to snake_case. `slacker` library wants snake_case.

    from http://stackoverflow.com/a/1176023/884640
    """
    s2 = RE_FIRST_CAP.sub(r'\1_\2', s)
    return RE_ALL_CAP.sub(r'\1_\2', s2).lower()


def lambda_handler(event, context):
    '''Provide an event that contains the following keys:

      - slack_api_method: a Slack API method (a URL on Slack API), see `call_slack` for more info
      - slack_api_arguments: arguments for Slack API Method, see `call_slack` for more info
        these will be merged with (and override) arguments.

    :param event: event passed from AWS Lambda
    :type event: dict
    :param context: metadata from AWS Lambda
    :type event: dict
    '''
    print("Received event: " + json.dumps(event, indent=2))

    api_method_path = event['slack_api_method']  # i.e. "chat.postMessage"
    api_arguments = merge(SLACK_API_ARGUMENTS_DEFAULT, event['slack_api_arguments'])

    # TODO(hangtwenty) schema for another field, "chummybot_arguments" ...?
    # i.e. memory_channel

    # this block "resolves" the string of the Slack API method,
    # to a callable on the `slack` instance. i.e. for chat.postMessage, do
    # >>> fun = slack | getattr('chat') | getattr('post_message')
    # >>> fun(<the arguments for that API method>)
    api_method_path_components = api_method_path.split('.')
    fun = slack
    for component_name in api_method_path_components:  # i.e. first "chat" then "postMessage"
        component_name = snake_case(component_name)
        fun = getattr(fun, component_name)

    api_response = fun(**api_arguments)

    print("Received response from Slack: " + pprint.pformat(api_response, indent=2))
    return api_response

def always_failed_handler(event, context):
    raise Exception('I failed!')


if __name__ == "__main__":
    # for manual testing on my laptop

    import os

    my_event = {
        "slack_api_method": "chat.postMessage",
        "slack_api_arguments": {
            "channel": "#friendlybotisfriendly",
            "as_user": "friendlybot",
            "text": "Hello from a Python script"
        }
    }
    response = lambda_handler(my_event, {})
