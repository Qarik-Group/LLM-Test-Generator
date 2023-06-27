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


def clone_or_update_repository(repo_url) -> Path:
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    repo_path = os.path.join(TARGET_DIRECTORY, repo_name)
    logging.info(f'Preparing to clone {repo_url}')
    # Check if the repository directory exists
    if os.path.exists(repo_path):
        # Check if it's a Git repository
        if not os.path.isdir(os.path.join(repo_path, '.git')):
            logging.error(f"Error: {repo_path} is not a Git repository")
            exit(1)
        # Check if it's the same repository
        repo = Repo(repo_path)
        remote_url = repo.remotes.origin.url
        if remote_url == repo_url:
            logging.info(
                f"The repository {repo_url} is already cloned in {repo_path}. Continuing...")
            return Path(repo_path)

        else:
            logging.error(
                f"Error: {repo_path} exists but points to a different repository")
            exit(1)
    else:
        # Clone the repository
        Repo.clone_from(repo_url, repo_path)
        logging.info(f"Successfully cloned {repo_url} into {repo_path}")
        return Path(repo_path)
