import csv
import logging
import os
from os import path

from github import Github

from github_pr_magic_nb.ConfigConstants import (
    GITHUB_SECTION,
    REPOSITORIES_KEY,
    REPOSITORIES_SPLIT_TOKEN,
    ORG_KEY,
    TOKEN_KEY,
    FILE_PATH_KEY,
    SAVE_SECTION,
    USERS_SECTION,
)
from github_pr_magic_nb.MagicChecker import Rarity
from github_pr_magic_nb.Repository import Repository
from github_pr_magic_nb.SlackBot import SlackBot

HIGH_THRESHOLD = 10
LOW_THRESHOLD = 100
MAX_PREVIOUS_TO_CHECK = 1000

logger = logging.getLogger("github_pr_magic_nb")


class PRChecker:
    def __init__(self, config):
        self.repositories = {}
        for repo in config[GITHUB_SECTION][REPOSITORIES_KEY].split(
            REPOSITORIES_SPLIT_TOKEN
        ):
            self.repositories[repo] = Repository(config[GITHUB_SECTION][ORG_KEY], repo)
        self.github = Github(config[GITHUB_SECTION][TOKEN_KEY])
        self.save_file_path = os.path.abspath(
            os.path.expanduser(os.path.expandvars(config[SAVE_SECTION][FILE_PATH_KEY]))
        )
        self.load_last_run()
        self.slack_bot = SlackBot(config)
        self.users = {
            user: config[USERS_SECTION][user] for user in config[USERS_SECTION]
        }

    def load_last_run(self):
        if not path.exists(self.save_file_path):
            logger.warning("No backup {} - Skipping import".format(self.save_file_path))
            return
        with open(self.save_file_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                self.repositories[row[0]].last_pr_check = int(row[1])

    def save_run(self):
        with open(self.save_file_path, "w") as f:
            writer = csv.writer(f)
            for repo in self.repositories.values():
                writer.writerow([repo.name, repo.last_pr_check])

    def analyse_repositories(self):
        for repo in self.repositories.values():
            current_value = (
                self.github.get_repo(repo.get_url()).get_pulls(state="all")[0].number
            )
            logger.info("Current value for {} is {}".format(repo.name, current_value))
            self.check_previous_pr(current_value, repo)
            self.check_next_pr(current_value, repo)
            repo.last_pr_check = current_value
        self.save_run()

    def check_previous_pr(self, current_value, repo):
        last_pr_to_check = repo.last_pr_check
        if current_value - repo.last_pr_check > MAX_PREVIOUS_TO_CHECK:
            last_pr_to_check = current_value + 1 - MAX_PREVIOUS_TO_CHECK
            logger.warning(
                "Too many PR too check in comparison to last time from={} to={}, reducing check "
                "from={} to={}".format(
                    repo.last_pr_check,
                    current_value,
                    last_pr_to_check,
                    current_value,
                )
            )
        res = Rarity.check_rarity_value_range(last_pr_to_check, current_value + 1)
        for pr_number, pr_rarity in res.items():
            pr_with_magic_nb = self.github.get_repo(repo.get_url()).get_pull(pr_number)
            if pr_with_magic_nb.user.login in self.users:
                prefix = "<@{}>".format(self.users[pr_with_magic_nb.user.login])
            else:
                prefix = "<{}|{}>".format(
                    pr_with_magic_nb.user.html_url,
                    pr_with_magic_nb.user.name
                    if pr_with_magic_nb.user.name
                    else pr_with_magic_nb.user.login,
                )
            message = "{}\n:tada: {} opened in repository {} the PR <{}|#{} {}>".format(
                pr_rarity.get_str_repr(),
                prefix,
                repo.name,
                pr_with_magic_nb.html_url,
                pr_number,
                pr_with_magic_nb.title,
            )
            self.slack_bot.send_message(message)

    def check_next_pr(self, current_value, repo):
        # Check Next
        last_pr_to_check = max(repo.last_pr_check + HIGH_THRESHOLD, current_value)
        next_rarity_level = Rarity.check_rarity_value_range(last_pr_to_check, current_value + HIGH_THRESHOLD)
        is_high = False
        if next_rarity_level:
            is_high = True
        else:
            last_pr_to_check = max(repo.last_pr_check + LOW_THRESHOLD, current_value)
            next_rarity_level = Rarity.check_rarity_value_range(
                last_pr_to_check, current_value + LOW_THRESHOLD
            )
        if next_rarity_level:
            for pr_number, pr_rarity in next_rarity_level.items():
                message = "{}\n:{}: Repository {} current PR number {} is close to a rare number: {} (less than {})".format(
                    pr_rarity.get_str_repr(),
                    "so_close" if is_high else "warning",
                    repo.name,
                    current_value,
                    pr_number,
                    HIGH_THRESHOLD if is_high else LOW_THRESHOLD,
                )
                self.slack_bot.send_message(message)
