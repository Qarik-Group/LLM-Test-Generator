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

import argparse
import logging
import os
from pathlib import Path
from preprocess import preprocess
from prompts import fill_out_prompts
import llm
from git_clone import clone_or_update_repository
from postprocess import postprocess
from logging_config import configure_logging
configure_logging()


def setup() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='Test Generation',
        description='Generate Tests using a LLM')
    parser.add_argument('repo_url',
                        help='Url to repository')
    parser.add_argument('--module', nargs='?', help='Specific Module')

    return parser.parse_args()


def run():
    args = None
    try:
        args = setup()
    except NotADirectoryError as e:
        logging.error("{} not a directory".format(e))
        return

    repo_path = clone_or_update_repository(args.repo_url)
    if args.module:
        repo_path = repo_path/args.module
    pre_processed_packages = preprocess(repo_path)
    filled_out_prompts = fill_out_prompts(pre_processed_packages)
    results = llm.generate_tests(filled_out_prompts)
    postprocess(results)


def dir_path(string) -> Path:
    if os.path.isdir(string):
        return Path(string)
    else:
        raise NotADirectoryError(string)


if __name__ == '__main__':
    run()
