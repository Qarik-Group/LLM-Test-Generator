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
from pathlib import Path
import logging
from logging_config import configure_logging
configure_logging()


def postprocess(results: dict):
    """Process the results from the LLM. Clean up text, save to file

    Args:
        results (dict): the results from the LLM
    """
    count = 0
    for path, result in results.items():
        content = remove_excess_text(result)
        content = rename_test(path.stem, content)
        count += count_tests(content)
        try:
            save(path, content)
        except Exception as e:
            logging.warning(f'Failed saving file: {e}')
            continue
    logging.info(f'Generated a total of {count} tests')


def count_tests(content: str) -> int:
    """Count number of tests generated for file

    Args:
        content (str): contents of tes file

    Returns:
        int: number of tests found
    """
    return content.count('@Test')


def save(path: str, content: str):
    """Save the contents to the test directory of the respective module

    Args:
        path (str): path of the new test
        content (str): content to save
    """
    logging.info(
        f'Writing tests to {str(Path(path).relative_to(Path("./target_repository/").absolute()))}')
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as file:
        file.write(content)


def rename_test(name: str, content: str) -> str:
    """Rename the test class to the file name

    Args:
        name (str): name to use
        content (str): content of the new test file

    Returns:
        str: edited content
    """
    class_name_start = content.index("class") + len("class")
    class_name_end = content.index("{", class_name_start)

    content = content[:class_name_start] + \
        ' '+name + content[class_name_end:]
    return content


def remove_excess_text(content: str) -> str:
    """Remove non-code responses, and code section indicators

    Args:
        content (str): test file content

    Returns:
        str: cleaned up text
    """
    llm_comments_start = content.index("```java") + len("```java")
    content = content[llm_comments_start:]
    content = content.replace('```', '')
    return content
