# Plans

soon enough I hope :)

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