# yobot

yobot introduces people to each other in Slack. 
It can make connections across departments or geographies in your growing organization.

# Screenshots

TODO

# Inspired by [etsy/mixer][1], but it's different

[etsy/mixer][1] is an awesome idea:

> [Mixer is] a simple web app that allows people to join a group and then get randomly paired with another member of that group. It then prompts you to meet each other for a coffee, lunch, or a drink after work.  [If you're not both in the same place,] just hop on a video chat.  This encourages people who may not work in the same place to stay in touch and find out what’s going on in each other’s day to day.  The tool keeps a history of the pairings and attempts to match you with someone unique each week; it’s possible to opt in or out of the program at any time.

I love the mixer idea, except I don't like more email.
And I don't think my coworkers want more emails either.

Slack was a sensible choice for me, as my company uses Slack, and Slack has great APIs and bot support.
If you like the idea but don't use Slack, I'll bet your (modern) chat service has the same features,
so it wouldn't be hard to port yobot :)

## Differences from [etsy/mixer][1]

The main difference is that it's *serverless* and *databaseless*. There's one-time set up and that's
it. So it's extremely low maintenance if you follow the recommended setup.

* *Serverless*. No long-running server needed. I'm running it as an AWS Lambda job and I'll show you how 
 to set it up yourself. It can run without you setting up a server, as an AWS Lambda job.
This was mainly because I wanted to play with AWS Lambda, but I like that this thing can be so low-maintenance!
* Use Slack's [user list](https://api.slack.com/methods/users.list) as a directory of employees,
so there is no need to access the company's [directory service](https://en.wikipedia.org/wiki/Directory_service)
(no fun), or translate it to another format, or store that directory in a database,
or keep that second directory up to date. None of that. Just Slack.
* *No database.* No need to set up a database. 
(Repeats are not so annoying in yobot as they would be in etsy/mixer.
This is because yobot responds on demand instead of introducing people on a schedule.
So if you get a repeat, just call `/yobot` again.)


[1]: https://codeascraft.com/2015/09/15/assisted-serendipity/


# Setup

TODO this all needs another pass

## Configuration

### Slack side

TODO. Need to review it all and document. Screenshots would be nice.

MEMO ... don't forget step: to use the `/yobot broadcast` functionality or "post to public channel
on a schedule", yobot MUST be MANUALLY invited (by a human) to the public channel you want her
to broadcast to.

### Yobot side

Take a look at `yobot_config_and_secrets.py` and `.env.example.` The idea is:

* `yobot_config_and_secrets.py` just gets its values from environment variables.
This makes it easy to work with locally, without committing secrets to VCS.
* There are several easy ways to manage these environment variables. Pick your fancy:
    * You make a script that sets the variables, and source it before testing or deploying.
      *Don't commit this to git.*
        * I recommend you do `cp .env.example .env` to make your own, then activate it
        by doing `source .env` or [using autoenv](https://github.com/kennethreitz/autoenv) (or [autoenv-zsh](https://github.com/kennethreitz/autoenv))
        ... this is very convenient :) The `.gitignore` ignores the `.env` file.
    * Pass them as arguments. i.e. `YOBOT_BOTUSER_TOKEN=blah YOBOT_BLAH=foobar ./scripts/deploy.sh`
    * Define them in a `~/.bashrc`.
    * If you don't want environment variables at all, just modify your local
        `yobot_config_and_secrets.py` directly and hardcode the values. *Don't commit this to git.*

(Seem weird?
If you think it's weird to put this config in a Python file, please open an Issue or submit a PR.
I did this for maximum flexibility, while also being clean/simple for AWS Lambda deployment.

## Test it out locally

Right now the best way is:

    $ python ./yobot/lambda_function.py

## Deployment

### Serverless, with AWS Lambda (batteries included!)

Here are detailed instructions - but don't be intimidated, *it's easy*.

The idea is that you put Yobot in AWS Lambda behind an API Gateway. (TODO add links to normal
documentation, as well as link to that helpful Fugue blog post.)

#### Prereqs:

1. An AWS account (TODO add link.)
2. Permissions to configure your AWS Account to add 1 AWS Lambda function and 1 AWS API Gateway.
3. The AWS CLI, up to date. (TODO add link.)

#### Manual, one-time setup with AWS Lambda

TODO add step by step guide with screenshots.

(PR welcome if someone wants to automate this.)

#### Deployment script

If you followed "Configuration" then this is all it takes:

    $ source .env 
    $ ./scripts/deploy.sh

`deploy.sh` is mostly just [standard steps to deploy Python code and a virtualenv to AWS Lambda](http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html)
Plus a little bit to do with config.

There's just one part some people might see as weird. The script will
take the required environment variables (`YOBOT_BOTUSER_TOKEN` etc.) -- the same ones you set
before, in "Configuration" section -- and **hardcode them into the deployment package.**
Specifically, it'll make the zip, then overwrite `yobot_config_and_secrets.py`
with values from environment variables.

Again, the simplest way to do something different is to **directly modify the code.**
Just modify `deploy.sh` to suit your needs, getting config & secrets from wherever you'd prefer.
If you've already hardcoded config & secrets into `yobot_config_and_secrets.py`,
then you could just delete this bit from `deploy.sh`

### Without AWS Lambda (batteries not included, but it'll be easy)

You could run this like a normal long-running bot process. It won't be hard.
Put it behind a web server that can take requests from Slack.
Make your server take a request from Slack. You are only responsible
for processing Slack's incoming POST request and converting it to a dictionary of parameters.
Then you pass that dictionary of parameters to the `handle_slack_request` 
function in `slack_logic.py`. It'll take it all from there.

# Plans

## Tests

Needs unit tests not just manual tests.

## More commands!

* `/yobot broadcast` -- paste (basic help) text in `#general`. (Channel should be configurable.)
best used to run on a schedule (that's easy with Lambda), such as every Friday at 11AM.
with introduction text. Should have a little config: 
SLASH_COMMAND_NAME, BOT_USER_NAME; WEBHOOK_UPON_MENTION_ENABLE ...i.e. 
    > "Hi, I'm yobot. :smiley: I introduce people to each other.
    
    > Type `/yobot` and hit enter. (You can run this command anywhere in Slack..
    > You can also just say "yobot" :wink:)
    > I'll pick someone randomly. Then I'll send you a message prompting you to introduce yourself.
    > For more info type `/yobot help`.
    > Try it! Type `/yobot` and meet someone new." 
    
* `/yobot help` -- print (basic help) AND advanced help with ALL commands listed.
* `/yobot @fbar` will direct messages @foo to say hi on your behalf.
This is for shy people :) It will message that user as yobot and say,
"Hi, I'm yobot. I introduce people to each other. @calling_user (real_name) wants to chat.
If you've got a moment, you should say hi!".
    * It would also be cool if you could just tell yobot "OK, sounds good, send them a message"
        Any variation of `/yobot ok..` or `/yobot hi...` or `/yobot message...`
        (as in `/yobot message them`) were accepted to mean this. And this would be triggered.
        Implementation: yobot looks back at im.history (with the calling-user) to grab last @handle
        it mentioned to calling-user.
* Ensure bot name configurable. (Any user-facing text that currently says "yobot" should be
changed to interpolate a variable. That variable should come from config. This _might_
already be true, but needs another pass of validation at least.)

## Leaderboards 

It would also be nice to have a little bit of statefulness, but I still want to avoid having a
database. I don't care about making it remember everything: I've brainstormed a lot about that,
and I don't think it's particularly useful. (Repeats are just fine.) However a short-term memory
would be good, and for that purpose, **yobot could store a short term record in direct messages
with itself.** (Yep, that works actually.) Technical limitations include 
Bot Users not being allowed to upload files or create "posts";
the 10,000-message-limit for free-tier Slack teams;
character limit for messages (4,000 characters).
But I think it'd be just fine to log each (caller, introduced-to) to this private channel.
Then when `/yobot broadcast` happens, maybe it also mentions that X people have "recently"
used `/yobot` and the top Y users "recently" are blah&blah&blah. Where "recently"
means "within the last month OR as far back as I can remember"

## Some clean up

* Should change `deploy.sh` so that it packages the whole `yobot` module so that the imports
can be more like absolute imports. (`from yobot.messages import` ...)
