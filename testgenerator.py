import argparse
import logging
import os
from pathlib import Path
import preprocess as prep
import prompts

import postprocess as postp

def setup() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
                    prog='Test Generation',
                    description='Generate Tests using a LLM')
    parser.add_argument('project_path', type=dir_path,
                    help='Path to project')
    parser.add_argument('ext', type=str,
                    help='File extension for src code')
    parser.add_argument('LLM', type=str,nargs='?',
                    help='Which LLM to use')

    return parser.parse_args()


def run():
    args = None
    try:
        args = setup()
    except NotADirectoryError as e:
        logging.error("{} not a directory".format(e))
        return
    pre_processed_packages=prep.preprocess(args.project_path,args.ext)
    filled_out_prompts=prompts.fill_out_prompts(pre_processed_packages,args.ext)
    # preprocess - run static code analysis, aggregate file information
    # loop over aggregate file information
    #   - get prompt per file - needs context information, static code analysis info,
    #   - send info to LLM and get response
    #   - post-process - strip any leading and end remarks from response, save tests to a file - needs to be the correct location and name based on the current file we are processing
    postp.postprocess()
    pass

def dir_path(string) -> Path:
    if os.path.isdir(string):
        return Path(string)
    else:
        raise NotADirectoryError(string)


if __name__ == '__main__':
    run()
