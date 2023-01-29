import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from github_pr_magic_nb.ConfigConstants import SLACK_SECTION, TOKEN_KEY, CHANNEL_KEY


class SlackBot:
    def __init__(self, config):
        self.client = WebClient(token=config[SLACK_SECTION][TOKEN_KEY])
        self.slack_channel = config[SLACK_SECTION][CHANNEL_KEY]

    def send_message(self, message):
        try:
            response = self.client.chat_postMessage(
                channel=self.slack_channel, text=message
            )
        except SlackApiError as e:
            logging.error(e)
        logging.info(response)
