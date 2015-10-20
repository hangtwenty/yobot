# You can manually set these yourself (BUT DON'T COMMIT TO VCS).
# If you follow my suggestion, you don't set these in this file, only deploy.sh will do that.
# For development, you should just set these in `.env` or another shell script,
# or in-line each time you run the command.
# See README for additional details.
import os

YOBOT_BOTUSER_NAME = os.environ["YOBOT_BOTUSER_NAME"]
YOBOT_BOTUSER_TOKEN = os.environ["YOBOT_BOTUSER_TOKEN"]
YOBOT_WEBHOOK_TOKEN = os.environ["YOBOT_WEBHOOK_TOKEN"]
YOBOT_SLASHCOMMAND_TOKEN = os.environ["YOBOT_SLASHCOMMAND_TOKEN"]

YOBOT_BROADCASTCHANNEL_NAME = os.environ["YOBOT_BROADCASTCHANNEL_NAME"]

YOBOT_DEBUG = os.environ.get("YOBOT_DEBUG", True)
YOBOT_DEBUGUSER_NAME = os.environ.get("YOBOT_DEBUGUSER_NAME", None)