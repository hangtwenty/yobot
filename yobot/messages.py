# -*- coding: utf-8 -*-
""" User-facing messages. Used by main logic to - with elements of chance.

You should feel free to modify these in place to suit you or your team's fancy.
If you really want to enhance the code to read from a config file, you could,
and pull requests are welcome :)
"""
import random

# TODO(hangtwenty) move messages into static files, maybe internationalization-ready
GREETINGS = [
    u"Howdy!",
    u"Hey there!",
    u"Hey!",
    u"Hey champ."
]
THINGS_TO_DO = [
    # TODO(hangtwenty) replace all emojis with :blah: equivalents (?) but that's chat-provider specific...
    # Slack does this automatically but it would be easier to read to just use that here too.
    u'Grab coffee ☕️',
    u'Maybe you should grab coffee ☕️',
    u'Maybe you should get coffee ☕️',
    u'Tea time?',
    u'Maybe you should have some coffee or tea.',
    u'Maybe you should grab a drink 🍻',
    u'Hungry? Grab lunch! 🍜',
    u"Grab lunch why don't you? 🍟",
    u'Maybe you should grab a snack 🍉',
    u"Why don't you grab a snack 🍩",
]
THINGS_TO_DO_REMOTE = [
    u"chat",
    u"hop on a quick video chat",
]
PROMPTS = [
    'Ask them what do they do at work.',
    'I wonder what they do for fun ...',
    'Ask them what they do for fun.',
    'Ask them what gets them excited lately.',
    'Ask them what they think about their work.',
    'Ask them if something is bugging them.',
    'Ask them how their day is going.',
    'Tell a joke.',
]
EMOJI_MSG = [
    # TODO(hangtwenty) replace all emojis with :blah: equivalents.
    # Slack does this automatically but it would be easier to read to just use that here too.
    u"👏",  # clapping hands
    u"👋",  # waving hand sign
    u"👍",  # thumbs up
    u"🏄",  # surfer.
    u"👌"  # ok hand
]


def generate_random_introduction_text(
        introduce_readable_name,
        introduce_username,
        introducing_to_oneself=False):
    """

    :param introduce_readable_name: the "readable" name of the person to introduce.
        there's a an order of precedence for determining this, but that's slack_logic's business.
        Here we just know where to put it, in the message template.
    :param introduce_username: the username (the thing you can mention like, @username)
        of the person to introduce.
    :param introducing_to_oneself: Flag; if true, activates alternate "easter egg" message.
    :return:
    """
    if introducing_to_oneself:
        # Easter egg in the VERY RARE chance that you get introduced to yourself.
        # TODO(hangtwenty) link the text "You're Great" to that shark "faces are full of protein"
        # meme cos that'd be pretty funny. Need to host it somewhere safe and persistent though.

        msg = u"*{greeting}* Have you met *{introduce_name}*?" \
              u"\nWait a second. That name seems awfully familiar." \
              u"\nRight! It's you! " \
              u"\nLook at you. You're great. http://hollyfeld.org/supergreat.jpg" \
              u"\n:dog: _Call me again for another random introduction._".format(
            greeting=random.choice(GREETINGS),
            introduce_name=introduce_readable_name,
        )
    else:
        msg = u"*{greeting}* Have you met *{introduce_name}*?\n\n" \
              u"{thing_to_do} {prompt}\n" \
              u"If you're not in the same place, just {thing_to_do_remote}{punctuation}\n\n" \
              u"*Type _/msg {introduce_username}_* " \
              u"to message {introduce_name} now. {emoji_msg}\n".format(
            greeting=random.choice(GREETINGS),
            introduce_name=introduce_readable_name,
            thing_to_do=random.choice(THINGS_TO_DO),
            thing_to_do_remote=random.choice(THINGS_TO_DO_REMOTE),
            punctuation=random.choice(['!', '.']),
            emoji_msg=random.choice(['', random.choice(EMOJI_MSG)]),
            prompt=random.choice(['', random.choice(PROMPTS)]),
        )
    return msg


def get_introduction_message():
    return (
        "*Hello!* I'm yobot. I introduce people to each other. :smiley: \n\n"
        "Want to try? *Type _/yobot_ anywhere in Slack.* "
        "Nobody else will see that you've typed /yobot, the command goes straight to me. "
        "It's silent. "
        "I'll choose another person who has Slack, randomly. "
        "Then I'll send *you* a private message with their name. "
        "I'll give you an idea to break the ice. :coffee: :beers: :computer: "
        "It's just for you, and there's no pressure to follow up. \n\n"
        "Try it! *Type _/yobot_ and meet someone new.*\n")