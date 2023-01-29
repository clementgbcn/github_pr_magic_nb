import configparser
import logging
import os

from github_pr_magic_nb.ConfigConstants import LOGGER_SECTION, FILE_PATH_KEY
from github_pr_magic_nb.PRChecker import PRChecker


if __name__ == "__main__":
    # Load config
    configParser = configparser.ConfigParser()
    configParser.read("config.ini")

    # Setup logger
    # Gets or creates a logger
    logger = logging.getLogger("github_pr_magic_nb")
    logger.setLevel(logging.INFO)

    # define file handler and set formatter
    file_handler = logging.FileHandler(
        os.path.abspath(
            os.path.expanduser(
                os.path.expandvars(configParser[LOGGER_SECTION][FILE_PATH_KEY])
            )
        )
    )
    formatter = logging.Formatter(
        "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
    )
    file_handler.setFormatter(formatter)

    # add file handler to logger
    logger.addHandler(file_handler)

    # Launch Analysis
    pr_checker = PRChecker(configParser)
    pr_checker.analyse_repositories()
    logger.info("End of Analysis\n{}\n".format("#" * 50))
