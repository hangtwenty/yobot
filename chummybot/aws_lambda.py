#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Translates from AWS Lambda event to Slack call.
"""
import httplib
import json
import pprint
import urllib

HOST = 'slack.com'
BASE_URL = '/api/'

SLACK_API_ARGUMENTS_DEFAULT = {
    'channel': '#chummybot',
    'as_user': 'chummybot',
}


def call_slack(slack_api_method, slack_api_arguments):
    """ Call any Slack slack_api_method with these slack_api_arguments

    Implementation must use httplib because we are sticking to Standard Library.
    (For the sake of portability and AWS Lambda.)

    :param slack_api_method: Corresponds to an Slack API Method from the subset of API Methods that
        Bot Users are allowed to call: https://api.slack.com/bot-users
    :type slack_api_method: str
    :param slack_api_arguments: API Method arguments!
        No really, this can be anything under "Arguments"
        in the documentation for a given API method.
        i.e. https://api.slack.com/methods/chat.postMessage
        These are merged with (and override) some defaults.
    :return: Response body from request to Slack, unmodified
    :rtype: httplib.HTTPResponse
    """
    slack_api_method = slack_api_method.strip('/')
    working_arguments = SLACK_API_ARGUMENTS_DEFAULT.copy()
    working_arguments.update(slack_api_arguments.copy())
    slack_api_arguments = working_arguments
    query_params_str = urllib.urlencode(slack_api_arguments)
    assert u"#" not in query_params_str, "Expected '#' to be escaped to '%23'"
    conn = httplib.HTTPSConnection(HOST)
    relative_url = BASE_URL + slack_api_method + "?" + query_params_str
    print "About to request, " + relative_url
    conn.request('GET', relative_url)
    http_response = conn.getresponse()
    return json.load(http_response)


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

    api_method = event['slack_api_method']
    api_arguments = event['slack_api_arguments']

    # TODO(hangtwenty) schema for another field, "chummybot_arguments" ...?
    # i.e. memory_channel

    api_response = call_slack(api_method, api_arguments)

    print("Received response from Slack: " + pprint.pformat(api_response, indent=2))
    return api_response

if __name__ == "__main__":
    # for manual testing on my laptop

    import os
    my_event = {
        "slack_api_method": "chat.postMessage",
        "slack_api_arguments": {
            "token" : os.environ["CHUMMYBOT_API_TOKEN"],
            "channel": "#friendlybotisfriendly",
            "as_user": "friendlybot",
            "text": "Hello from a Python script"
        }
    }
    # response = lambda_handler(my_event, {})

    import requests
    requests.post(
        os.environ['CHUMMYBOT_API_GATEWAY_URL'])


