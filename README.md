# Yobot

Yobot is a chatbot that introduces people to each other. It's an easy way to make connections
in your growing organization.
 
Yobot is implemented for Slack and ready to 
deploy with AWS Lambda. Low or maintenance. Likely no cost.

Yobot is an easy way to connect people.
Now, it's nothing revolutionary. It is simple [and unoriginal][1].
But if Yobot helps a few teammates get connected, it's done its job!
The best case is that some people will connect across functions, departments, or geographies. 


# Overview

Just write `/yobot` and you get a random introduction.
When you type `/yobot` you get a private message with someone's
name, username, and an icebreaker prompt. Then you can send them a message, or not. 
Also, nobody sees that you've used Yobot. Easy, and no-pressure. There are more commands,
see below.

TODO SCREENCAST-GIF-THING. picture is worth a thousand words.
(But TEMPORARILY FORCE USER to be restricted to a volunteer who is OK with me
capturing their name and putting it on the net ...)

## Batteries included

If you're handy with Python and AWS this will take you less than an hour to set up. (You'll
just need Slack admin rights, or a Slack admin ready to grant you some integrations.)

* Implemented with Python calling Slack's excellent APIs.
* **Batteries included.**
Contains deployment script, with instructions in this README, to set up as an AWS Lambda function. 
* **No database.** Obviously easier to set up and maintain this way! But how? Well, Slack
 is the only database needed. [etsy/mixer][1] uses a database to avoid introducing people twice.
 But Yobot is designed to respond on demand. It doesn't introduce people on a schedule,
 so a repeat isn't really annoying. Put yourself in the end-user's shoes: 
 if you already know the person, you can just call `/yobot` again and get another introduction.
* **No server.**
* Take a look at AWS Lambda's pricing. Only one request is needed each time someone uses
Yobot. Since you will probably not use Yobot more than a million times in a month, it
will probably be free for you to run. Since AWS Lambda removes the need for you to maintain
a server, there is no server you need to keep running.

### Doesn't match your stack? Let's talk

**Don't want to use AWS Lambda?** It won't be hard to run Yobot the conventional way,
as a simple server (Flask would be a great choice). If you wind up writing this,
please submit a Pull Request and we'll have it out-of-the-box ;)

**Slack was a sensible choice for me,** as my company uses Slack, and Slack has excellent APIs 
and bot support. If you want an introduction-bot Slack,
I'll bet your (modern) chat service has the same API features,
so it wouldn't be hard to port Yobot :) Please let me know if you port it,
and maybe we can merge efforts and make Yobot backend-agnostic!


# Inspired by [etsy/mixer][1], but it's different

[etsy/mixer][1] is an awesome idea:

> [Mixer is] a simple web app that allows people to join a group and then get randomly paired with another member of that group. It then prompts you to meet each other for a coffee, lunch, or a drink after work.  [If you're not both in the same place,] just hop on a video chat.  This encourages people who may not work in the same place to stay in touch and find out what’s going on in each other’s day to day.  The tool keeps a history of the pairings and attempts to match you with someone unique each week; it’s possible to opt in or out of the program at any time.

I love the mixer idea, except I don't like more email.
And I don't think my coworkers want more emails either.

## Differences from [etsy/mixer][1]

The main difference from [etsy/mixer][1] is that Yobot is *serverless* and *databaseless*.
So it should be easier to set up, as well as easier to maintain.

Lastly, by using the API of your company-standard chat client (like Slack),
you can:

* Avoid sending people MORE EMAIL. Hoping people will engage readily on chat, they already "hang out" there.
* Use the [chat user list](https://api.slack.com/methods/users.list) as a directory of employees,
so there is no need to access the company's [directory service](https://en.wikipedia.org/wiki/Directory_service)
(no fun), or translate it to another format, or store that directory in a database,
or keep that second directory up to date. Of course we're coupled and limited, 
but I think I spent less time writing this code than I would have to spend, going through
IT to get access to our directory service ... not to mention how hard it would be to 
keep my replica of it up to date, etc. etc.

All that said. Big ups to Etsy Engineering and Mixer as I think it's a brilliant idea.
Clearly an inspiring one!

[1]: https://codeascraft.com/2015/09/15/assisted-serendipity/

# Setup

TODO this all needs another pass

## Configuration

### Slack side

TODO. Need to review it all and document. Screenshots would be nice.

MEMO ... don't forget step: to use the `/yobot broadcast` functionality or "post to public channel
on a schedule", Yobot MUST be MANUALLY invited (by a human) to the public channel you want her
to broadcast to.

### Yobot side

Out of the box:

    $ cp .env.example .env      # start from template
    $ vim .env                  # edit config and put your secrets in
    # source .env               # before you deploy or test.

To `source .env` every time you `cd` into this directory,
[use autoenv](https://github.com/kennethreitz/autoenv) (or [autoenv-zsh](https://github.com/kennethreitz/autoenv)).

Full details ... Take a look at `yobot_config_and_secrets.py` and `.env.example.` The idea is:

* `yobot_config_and_secrets.py` just gets its values from environment variables.
This makes it easy to work with locally, without committing secrets to VCS.
* There are several easy ways to manage these environment variables. Pick your fancy:
    * You make a script that sets the variables, and source it before testing or deploying.
      *Don't commit this to git.*
    * Pass them as arguments. i.e. `YOBOT_BOTUSER_TOKEN=blah YOBOT_BLAH=foobar ./scripts/deploy.sh`
    * Define them in a `~/.bashrc`.
    * If you don't want environment variables at all, just modify your local
        `yobot_config_and_secrets.py` directly and hardcode the values. *Don't commit this to git.*

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

## Some clean up

* *replace deploy.sh* with [kappa](https://github.com/garnaat/kappa) Lambda
deployment/configuration tool

## More commands!

* `/yobot help` -- print (basic help).
 As I add other commands, this will also contain the "advanced help" with ALL COMMANDS listed. 
* `/yobot broadcast` -- paste (basic help) text in `#general`. <-- DONE, but ...
    * TODO: need to make the CHANNEL for this CONFIGURABLE.
        SLASH_COMMAND_NAME, BOT_USER_NAME; WEBHOOK_UPON_MENTION_ENABLE ...i.e.     
    * TODO--Tutorial secition--best used to run on a schedule,
    such as every Friday at 11AM. (Give people time to make a quick plan for their lunchtime
    on the "casual" day.) SO ADD TUTORIAL ABOUT RUNNING _THIS_ COMMAND WITH LAMBDA,
    on schedule ...  WHICH will ALSO require some work on API gateway side and/or
    the input accepted by Yobot ...
* *filter people* with commands.
    * `/yobot #channel`. Meet people with a certain interest or on a certain team.
    Best use case for MY organization: I'm remote. So doing `/yobot #remote` until I've met
    everyone remote, would be cool. Also, I'm in America; I'd love to do `/yobot #london` 
    to meet a couple people from Across the Pond ;). Again... you COULD go look at USER LIST
    and select people out, but I'm finding people like the element of chance.
    * `/yobot timezone EST` to filter to a certain timezone. Helpful if you want to meet
    people on the same clock as you, in a distributed team ...
* `/yobot @fbar` will direct messages @foo to say hi on your behalf.
This is for shy people :) It will message that user as yobot and say,
"Hi, I'm yobot. I introduce people to each other. @calling_user (real_name) wants to chat.
If you've got a moment, you should say hi!".
    * It would also be cool if you could just tell yobot "OK, sounds good, send them a message"
        Any variation of `/yobot ok..` or `/yobot hi...` or `/yobot message...`
        (as in `/yobot message them`) were accepted to mean this. And this would be triggered.
        Implementation: Yobot looks back at im.history (with the calling-user) to grab last @handle
        it mentioned to calling-user.
* Ensure bot name configurable. (Any user-facing text that currently says "Yobot" should be
changed to interpolate a variable. That variable should come from config. This _might_
already be true, but needs another pass of validation at least.)

## Leaderboards 

It would also be nice to have a little bit of statefulness, but I still want to avoid having a
database. I don't care about making it remember everything: I've brainstormed a lot about that,
and I don't think it's particularly useful. (Repeats are just fine.) However a short-term memory
would be good, and for that purpose, **Yobot could store a short term record in direct messages
with itself.** (Yep, that works actually.) Technical limitations include 
Bot Users not being allowed to upload files or create "posts";
the 10,000-message-limit for free-tier Slack teams;
character limit for messages (4,000 characters).
But I think it'd be just fine to log each (caller, introduced-to) to this private channel.
Then when `/yobot broadcast` happens, maybe it also mentions that X people have "recently"
used `/yobot` and the top Y users "recently" are blah&blah&blah. Where "recently"
means "within the last month OR as far back as I can remember"
