# chummybot

chummybot introduces people to each other in Slack. 
It can make connections across departments or geographies in your growing organization.

# Why not [etsy/mixer][1]?

[etsy/mixer][1] is an awesome idea:

> [Mixer is] a simple web app that allows people to join a group and then get randomly paired with another member of that group. It then prompts you to meet each other for a coffee, lunch, or a drink after work.  [If you're not both in the same place,] just hop on a video chat.  This encourages people who may not work in the same place to stay in touch and find out what’s going on in each other’s day to day.  The tool keeps a history of the pairings and attempts to match you with someone unique each week; it’s possible to opt in or out of the program at any time.

I liked everything about it except that it uses email.
I can think of many coworkers who would ignore another email, but they'd be fine with a chat message.
Since I already had to write a new thing to use chat instead of email,
I decided to use 

Slack was a sensible choice for me, as my company uses Slack, and Slack has great APIs and bot support.
If you like the idea but don't use Slack, I'll bet your (modern) chat service has the same features,
so it wouldn't be hard to port chummybot!

# Differences from [etsy/mixer][1]

* Use Slack's [user list](https://api.slack.com/methods/users.list) as a directory of employees,
so there is no need to access the company's [directory service](https://en.wikipedia.org/wiki/Directory_service)
(no fun), or translate it to another format, or store that directory in a database,
or keep that second directory up to date
* PLANNED: Use a Slack channel for persistence so there is no need to set up a database
* PLANNED: It can run without you setting up a server, as an AWS Lambda job.
This was mainly because I wanted to play with AWS Lambda, but I like that this thing can be so low-maintenance!


[1]: https://codeascraft.com/2015/09/15/assisted-serendipity/
