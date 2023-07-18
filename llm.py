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

from vertexai.preview.language_models import ChatModel
import json
from pathlib import Path
import logging
from logging_config import configure_logging
configure_logging()

parameters = {
    # Temperature controls the degree of randomness in token selection.
    "temperature": .8,
    # Token limit determines the maximum amount of text output.
    "max_output_tokens": 1024,
    # Tokens are selected from most probable to least until the sum of their probabilities equals the top_p value.
    "top_p": 0.4,
    # A top_k of 1 means the selected token is the most probable among all tokens.
    "top_k": 15,
}

chat_model = ChatModel.from_pretrained("chat-bison@001")


def generate_tests(prompts: dict) -> dict:

    final_results = {}
    for path, prompt_list in prompts.items():
        results = []
        name = f'{Path(path).stem}GenTest'
        name = name.replace('.', '_')
        logging.info(
            f'Starting to generate test(s) for {str(Path(path).relative_to(Path("./target_repository/").absolute()))}')
        for prompt in prompt_list:

            context = json.loads(prompt['context'])
            chat = chat_model.start_chat(
                context=json.dumps(context)
            )
            response = ''
            try:
                response = chat.send_message(
                    prompt['question'], **parameters)
            except Exception as e:
                logging.warning(f'Error when connecting to the LLM: {e}')
                continue

            results.append(response.text)
        logging.info(
            f'Finished generating test(s) for {str(Path(path).relative_to(Path("./target_repository/").absolute()))}')
        prepare_final_results(name, path, results, final_results)
    return final_results


def prepare_final_results(name: str, path: str, results: list[str], final_results: dict) -> dict:
    """Combine results into one file, and make the path the correct place

    Args:
        name (str): name of the test
        results (list[str]): results from the LLM
        final_results (dict): collection of all the results

    Raises:
        e: Exception from the LLM when combining the tests

    Returns:
        dict: all the results
    """
    res = ''
    path = path.replace('main', 'test')

    path = Path(path)

    test_path = path.with_name(name).with_suffix('.java')

    if len(results) > 1:
        logging.info(
            f'Multiple tests found for {str(Path(test_path).relative_to(Path("./target_repository/").absolute()))}, combining into 1 test file')

        try:
            res = combine_tests(results)
        except Exception as e:
            logging.error(f'Failed combining tests: {e}')
            raise e

        final_results[test_path] = res
    elif results:

        res = results[0]
        final_results[test_path] = results[0]
    return final_results


def combine_tests(results: list[str]) -> str:
    """Combine relavant tests

    Args:
        results (list[str]): Tests to combine

    Returns:
        str: combined tests
    """
    chat = chat_model.start_chat(
        context=", ".join(results)
    )
    return chat.send_message(
        f'Combine the following tests into one java test file. Add in any imports for core java code lists, queues, maps, etc that are missing', **parameters).text
