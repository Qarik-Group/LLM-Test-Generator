# Copyright 2023 Qarik Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from git import Repo
from pathlib import Path
from logging_config import configure_logging
import logging
TARGET_DIRECTORY = 'target_repository'
configure_logging()


def clone_or_update_repository(repo_url: str) -> Path:
    """Clone/update the git repository you added to the command

    Args:
        repo_url (str): URL to the git repo

    Returns:
        Path: Path to the repository that was cloned/updated
    """
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    repo_path = os.path.join(TARGET_DIRECTORY, repo_name)
    logging.info(f'Preparing to clone {repo_url}')
    # Check if the repository directory exists
    if os.path.exists(repo_path):
        return check_if_cloned(repo_url, repo_path)

    # Clone the repository
    Repo.clone_from(repo_url, repo_path)
    logging.info(f"Successfully cloned {repo_url} into {repo_path}")
    return Path(repo_path)


def check_if_cloned(repo_url: str, repo_path: str) -> Path:
    """Checks if the repository is cloned locally, and returns a relative path to it

    Args:
        repo_url (str): git repo remote cloning url
        repo_path (str): path to local repository

    Returns:
        Path: Path to local repository
    """
    check_if_git_repo(repo_path)

    # Check if it's the same repository
    remote_url = Repo(repo_path).remotes.origin.url
    if remote_url != repo_url:
        logging.error(
            f"Error: {repo_path} exists but points to a different repository")
        exit(1)
    logging.info(
        f"The repository {repo_url} is already cloned in {repo_path}. Continuing...")
    return Path(repo_path)


def check_if_git_repo(repo_path: str):
    """Check if the repo we are looking at locally is a git repository

    Args:
        repo_path (str): path to local repository
    """
    if not os.path.isdir(os.path.join(repo_path, '.git')):
        logging.error(f"Error: {repo_path} is not a Git repository")
        exit(1)
