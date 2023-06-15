import argparse
import logging
import os
from pathlib import Path
from preprocess import preprocess
from prompts import fill_out_prompts
import llm

from postprocess import postprocess


def setup() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='Test Generation',
        description='Generate Tests using a LLM')
    parser.add_argument('project_path', type=dir_path,
                        help='Path to project')
    parser.add_argument('ext', type=str,
                        help='File extension for src code')
    parser.add_argument('LLM', type=str, nargs='?',
                        help='Which LLM to use')

    return parser.parse_args()


def run():
    args = None
    try:
        args = setup()
    except NotADirectoryError as e:
        logging.error("{} not a directory".format(e))
        return
    pre_processed_packages = preprocess(args.project_path, args.ext)
    filled_out_prompts = fill_out_prompts(
        pre_processed_packages, args.ext)
    llm.generate_tests(filled_out_prompts)
    postprocess()
    pass


def dir_path(string) -> Path:
    if os.path.isdir(string):
        return Path(string)
    else:
        raise NotADirectoryError(string)


if __name__ == '__main__':
    run()
