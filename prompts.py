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

from package import Package
from code_file import CodeFile
from langugageLookup import language_data
from method import Method
import json
from pathlib import Path
import logging
import os
from logging_config import configure_logging
configure_logging()


def fill_out_prompts(packages: list[Package]) -> dict:
    """Fills out 1 single prompt for every method in the repository

    Args:
        packages (list[Package]): all the package data in the repository

    Returns:
        dict: all prompts with their file path as the key
    """
    clean_up()
    prompts = {}
    count = 0
    for package in packages:
        for file, code_file in package.source_code.items():
            if code_file.class_signatures[0]['type'] == 'interface':
                continue
            prompts[file] = []
            logging.info(
                f'Preparing prompts for: {str(Path(file).relative_to(Path("./target_repository/").absolute()))}')
            i = 0
            for method in code_file.methods:

                if not method.signature or not method.signature.access or 'private' == method.signature.access or method.is_constructor:
                    continue

                template_values = gather_template_values(
                    package, code_file, method)
                prompt = populate_template(template_values, i)
                prompts[file].append(prompt)
                count += 1
                i += 1
    logging.info(f'Prepared {count} prompts for repository')
    return prompts


def clean_up():
    """Remove previously generated prompts
    """
    file_list = os.listdir('final_prompts')
    if file_list:
        logging.info('Removing previously populated prompts')

    for file_name in file_list:
        file_path = os.path.join('final_prompts', file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)


def gather_template_values(package: Package, code_file: CodeFile, method: Method) -> dict:
    """Populate all of the template values for the prompt

    Args:
        language (str): language the source code is in
        package (Package): package we are processing
        code_file (CodeFile): file we are processing
        method (Method): method we are processing

    Returns:
        dict: template values for prompt
    """

    template_data = {}
    template_data['test_name'] = f'{method.parent_class["name"]}-Gen'
    template_data['package'] = code_file.package
    template_data['logging_framework'] = language_data['java']["logging"][0]
    template_data['testing_framework'] = language_data['java']["testing_frameworks"][0]['name']
    template_data['testing_framework_generic_import'] = language_data['java']["testing_frameworks"][0]['generic_import']
    template_data['static_code_analysis'] = code_file.static_code_analysis
    template_data['target_method_comment'] = method.comment
    template_data['target_method_signature'] = json.dumps(
        method.signature.to_dict())
    template_data['target_method_body'] = method.body

    template_data['class_signature'] = method.parent_class['signature']
    template_data['class_type'] = method.parent_class['type']
    template_data['class_name'] = method.parent_class['name']
    template_data['class_implements'] = ''
    template_data['class_extends'] = ''

    if 'implements' in method.parent_class:
        template_data['class_implements'] = method.parent_class['implements']
    if 'extends' in method.parent_class:
        template_data['class_extends'] = method.parent_class['extends']
    template_data['class_comments'] = code_file.class_comments

    template_data['class_imports'] = code_file.imports

    template_data['reference_package_info'] = []
    create_reference_context(package, template_data)
    template_data['code_imports'] = code_file.imports
    template_data['notes'] = ''
    template_data['class_comments'] = code_file.class_comments
    template_data['method_comments'] = [method.comment]
    return template_data


def create_reference_context(package: Package, template_data: dict):
    """Setup reference context, all other code in the same package as method that is having tests generated

    Args:
        package (Package): all the information for the package that tests are being generated for
        template_data (_type_): template to fill in
    """
    for source_code in package.source_code.values():
        info = {}
        for clas in source_code.class_signatures:
            info['class_signature'] = clas['signature']
            info['class_type'] = clas['type']
            info['class_name'] = clas['name']
            info['class_implements'] = ''
            info['class_extends'] = ''

            if 'implements' in clas:
                info['class_implements'] = clas['implements']
            if 'extends' in clas:
                info['class_extends'] = clas['extends']
            info['class_imports'] = source_code.imports
            info['class_comments'] = source_code.class_comments
            info['class_methods'] = [
                json.dumps(meth.signature.to_dict()) if meth.signature else "" for meth in source_code.methods]
        template_data['reference_package_info'].append(info)


def populate_reference_methods(methods: list[Method], template_data: dict):
    """Populate reference methods from package

    Args:
        methods (list[Method]): The methods inside of a source file
        template_data (dict):  dict of all the values we have preprocessed in a form that can be input into the template
    """
    reference_code = []

    for method in methods:
        reference_code.append(
            f'{method.signature} belongs to {method.parent_class["signature"]}')
    template_data['reference_methods'] = str(reference_code)


def populate_reference_class_signature(template_data: dict, class_signatures: list[dict]):
    """Populate reference class signatures

    Args:
        template_data (dict):  dict of all the values we have preprocessed in a form that can be input into the template
        class_signatures (list[dict]): all the signatures found in a single class
    """
    reference_sig = ''
    for value in class_signatures:
        reference_sig += f'{value["name"]} -- type: {value["type"]}'
        if 'extends' in value:
            reference_sig += " extends: " + ', '.join(value["extends"])
        if 'implements' in value:
            reference_sig += " implements: " + ', '.join(value["implements"])

        reference_sig += ','

    template_data['reference_package_info'].append(reference_sig)


def populate_template(template_data: dict, prompt_val: int) -> dict:
    """Using the template values, populate the template prompt

    Args:
        template_data (dict): dict of all the values we have preprocessed in a form that can be input into the template

    Returns:
        dict: the finished prompt
    """
    with open("template_prompts/methodprompt2.json", "r") as file:
        data = json.load(file)

        format_nested_dictionary(data["context"], template_data)
        data['context']['reference_package_info'] = []
        for reference in template_data['reference_package_info']:
            prompt_item = data['reference_package_info_item']
            template_item = {}
            for key, val in prompt_item.items():
                formatted_value = val.format(**reference)
                template_item[key] = formatted_value
            data['context']['reference_package_info'].append(template_item)
        prompt_file_path = f'final_prompts/final_prompt-{data["context"]["test_name"]}-{prompt_val}.json'
        with open(prompt_file_path, 'w') as file:
            logging.info(f'Writing final prompt to {prompt_file_path}')
            json.dump(data, file, indent=4)
        json_data = json.dumps(data['context'])
        return {'question': data['question'], 'context': json_data}


def format_nested_dictionary(template_dict: dict, value_dict: dict) -> None:
    """Format nested dictionary for prompt

    Args:
        template_dict (dict): The template to fill in
        value_dict (dict): the values to fill the template in with
    """
    for key, value in template_dict.items():
        if isinstance(value, dict):
            # Recursive call for nested dictionaries
            format_nested_dictionary(value, value_dict)
        elif isinstance(value, str):
            template = value.format(**value_dict)
            template_dict[key] = template
