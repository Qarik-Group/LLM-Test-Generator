from package import Package
from code_file import CodeFile
from langugageLookup import language_data
from method import Method
import json


def fill_out_prompts(packages: list[Package], ext: str) -> dict:
    """Fills out 1 single prompt for every method in the repository

    Args:
        packages (list[Package]): all the package data in the repository
        ext (str): language

    Returns:
        dict: all prompts with their file path as the key
    """
    prompts = {}
    for package in packages:
        for file, code_file in package.source_code.items():
            prompts[file] = []
            for method in code_file.methods:
                if 'static' in method.signature or 'private' in method.signature or method.is_constructor:
                    continue
                template_values = gather_template_values(
                    ext, package, code_file, method,)
                prompt = populate_template(template_values)
                prompts[file].append(prompt)
    print(f'Prepped {len(prompts)} prompts')
    return prompts


def gather_template_values(language: str, package: Package, code_file: CodeFile, method: Method) -> dict:
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
    template_data['language'] = language
    template_data['testing_framework'] = language_data[language]["testing_frameworks"][0]['name']
    template_data['testing_framework_generic_import'] = language_data[language]["testing_frameworks"][0]['generic_import']
    template_data['logging_framework'] = language_data[language]["logging"][0]
    template_data['static_code_analysis'] = code_file.static_code_analysis
    template_data['source_code'] = str(method)
    template_data['reference_package_info'] = []
    for source_code in package.source_code.values():
        populate_reference_class_signature(
            template_data, source_code.class_signatures)
        method = populate_reference_methods(source_code.methods)
    template_data['source_code_implements'] = ''
    template_data['source_code_extends'] = ''
    template_data['source_code_fields'] = code_file.fields
    if 'implements' in code_file.class_signatures[0]:
        template_data['source_code_implements'] = code_file.class_signatures[0]['implements']
    if 'extends' in code_file.class_signatures[0]:
        template_data['source_code_extends'] = code_file.class_signatures[0]['extends']

    template_data['code_imports'] = code_file.imports
    template_data['notes'] = ''
    template_data['class_comments'] = code_file.class_comments
    template_data['package'] = package.package_path
    template_data['method_comments'] = [method.comment]
    return template_data


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


def populate_template(template_data: dict) -> dict:
    """Using the template values, populate the template prompt

    Args:
        template_data (dict): dict of all the values we have preprocessed in a form that can be input into the template

    Returns:
        dict: the finished prompt
    """
    with open("template_prompts/methodprompt.json", "r") as file:
        data = json.load(file)
        context = ''
        for item in data["context"]:
            title = str(item).replace('_', ' ')
            context += f'{title}: {data["context"][item].format(**template_data)} \n'
        question = data["question"].format(**template_data)
        context = context.replace('static code analysis: []', '')
        context = context.replace('method comments: ['']', '')

        return {'question': question, 'context': context}
