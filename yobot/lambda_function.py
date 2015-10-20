""" Support for running in AWS Lambda, with input from API Gateway.

(You must set up Lambda+API Gateway like README suggests.)
"""
import collections
import json
import urlparse

from slack_logic import _validate_config_or_die, handle_slack_request

FORMPARAMS = 'formparams'


def lambda_handler(event, context):
    ''' Provide an event that contains the following keys:

    - formparams

    So an event will look like ...

        {
            "formparams": "token=XXXXX&team_id=T0123456&team_domain=acme&service_id=yyy&channel_id
            =zzz&channel_name=messin_with_bots&timestamp=1445211688.000031&user_id=uxxx&user_name
            =daffyduck&text=hi"
        }

    (without those line-breaks of course)

    :param event: event passed from AWS Lambda
    :type event: dict
    :param context: metadata from AWS Lambda
    :type event: dict
    '''
    print("Received event: " + json.dumps(event, indent=2))

    _validate_config_or_die()

    try:
        params_from_slack_as_lists = urlparse.parse_qs(event[FORMPARAMS])
        # For some reason these all get parsed out as 1-item lists. I guess that's how parse_qs is.
        # I think this actually is OK by the rules of URL query strings. (You could have a key
        # repeat twice and maybe that would could as 2 items in that list.)
        # Well, we expect that never to happen, so let's assert that.
        # And get all these values out of the lists, we really don't need them as lists.
        params_from_slack_request = {}
        for key, value in params_from_slack_as_lists.items():
            if isinstance(value, collections.Sequence) and len(value) == 1:
                params_from_slack_request[key] = value[0]
            else:
                raise ValueError("Error parsing out the formparams")
        print("Received param_map: " + json.dumps(params_from_slack_request, indent=2))
    except KeyError:
        raise Exception("Ahhhhh " + json.dumps(event, indent=2))  # + " and context " +
        # json.dumps(context, indent=2))

    retval = handle_slack_request(params_from_slack_request)

    return retval


if __name__ == "__main__":
    """ Manual test - to pretend you are making a request like API Gateway will make to AWS Lambda.
    """
    import slacker
    import yobot_config_and_secrets

    _validate_config_or_die()

    slack_api = slacker.Slacker(yobot_config_and_secrets.YOBOT_BOTUSER_TOKEN)
    DEBUG_USER_NAME = yobot_config_and_secrets.YOBOT_DEBUGUSER_NAME
    DEBUG_USER_NAME = DEBUG_USER_NAME.lstrip(u'@')
    users = slack_api.users.list().body['members']
    DEBUG_USER_ID = [user['id'] for user in users if user['name'] == DEBUG_USER_NAME][0]

    # TODO(hangtwenty) interpolate ALL config (including trigger_word or whatever)
    # into test sample below

    # TODO(hangtwenty) duplicate this to slack_logic.py ..?

    # if you are testing, this is just kind of "cooking the books" --
    # we are making a "request" that has the exact same token as what is configured,
    # as the authenticated token. so this will always be auth'd
    # (as long as the test token is non-zero).
    TEST_SLACK_TOKEN = yobot_config_and_secrets.YOBOT_WEBHOOK_TOKEN
    lambda_handler({
        "formparams":
            "token={token}&team_id=blah&team_domain=acme&service_id=yyy&channel_id=zzz"
            "&channel_name=messin_with_bots&timestamp=1445211688.000031&user_id={user_id}&user_name"
            "=daffyduck&text=hi&trigger_word=yobot".format(
                token=TEST_SLACK_TOKEN,user_id=DEBUG_USER_ID)
    }, None)

    try:
        # should get auth error
        lambda_handler({
            "formparams":
                "token={token}&team_id=blah&team_domain=acme&service_id=yyy&channel_id=zzz"
                "&channel_name=messin_with_bots&timestamp=1445211688.000031&user_id={user_id}&user_name"
                "=daffyduck&text=hi&trigger_word=yobot".format(
                    token="BOGUS, expect auth error",user_id=DEBUG_USER_ID)
        }, None)
        raise RuntimeError("Expected exception actually!!! Should have gotten auth error.")
    except Exception:
        pass
