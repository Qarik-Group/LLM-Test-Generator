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

from code_file import CodeFile
import os
from method import Method
from package import Package
from pathlib import Path
import re
from static_code_analysis import analyze
from method_signature import MethodSignature
import logging
from logging_config import configure_logging
configure_logging()


def preprocess(directory: Path) -> list[Package]:
    """Preprocesses the entire repository by creating Package objects with the parsed data from all of the files

    Args:
        directory (Path): Path to the root of the repository that is being preprocessed
        ext (str): Extension of the language being parsed (6/1/2023 - Only supports Java)

    Returns:
        list[Package]: All the parsed packages from the repository
    """
    packages = []
    package_dirs: list[Path] = find_packages(directory)
    analysis_data = analyze(directory)
    i = 0
    for package_dir in package_dirs:

        source_file_paths = find_files(package_dir, "main")
        if not source_file_paths:
            continue
        source_files = {}
        test_files = {}

        for file in source_file_paths:
            file_static_analysis = []

            if str(file.absolute()) in analysis_data:
                file_static_analysis = analysis_data[str(file.absolute())]

            code: CodeFile = parse_file(file, file_static_analysis)
            if code is None:
                continue
            source_files[str(file.absolute())] = code
        package = parse_package_value(source_file_paths[0])

        packages.append(Package(package, package_dir, source_files,
                        analysis_data, test_files))
    return packages


def parse_package_value(path: Path) -> str:
    """Parses the package from a file path

    Args:
        path (Path): path to a java source code file

    Returns:
        str: package value
    """
    package_parts = []
    path, _ = os.path.split(path)
    while True:
        path, folder = os.path.split(path)
        if folder == 'java' or folder == 'src':
            break
        package_parts.append(folder)
        if not path:
            break
    package_parts.reverse()
    package_name = '.'.join(package_parts)

    return str(package_name)


def parse_file(file: Path, static_code_analysis: list[dict]) -> CodeFile:
    """Parses a java file for useful context information, including package, imports, class comments, and methods

    Args:
        file (Path): Path of the java file

    Returns:
        CodeFile: CodeFile object with relevant parsed data, may be None if there are no methods present
    """
    with open(file, "r") as input_file:
        java_code = input_file.read()
        package = parse_package(java_code)
        class_signatures = parse_class(java_code)
        class_signatures = get_class_signature_info(class_signatures)

        imports = parse_imports(java_code)
        class_comments = parse_class_comments(java_code.splitlines())
        fields = parse_class_fields(java_code)
        methods = parse_methods(java_code, class_signatures)
        if len(methods) == 0:
            logging.warn(
                f'No methods found. Skipping {str(file.absolute().relative_to(Path("./target_repository").absolute()))}')
            return None
        return CodeFile(class_signatures, class_comments, fields, methods, file, package, imports, static_code_analysis)


def parse_class_fields(code: str) -> list[str]:
    """Parses the class fields from a file

    Args:
        code (str): code content

    Returns:
        list[str]: list of fields
    """
    field_pattern = (
        # Access modifiers
        r'((?:public\s*|protected\s*|private\s*)*'
        # modifiers
        r'(?:abstract\s*|synchronized\s*|static\s*|final\s*|transient\s*|volatile\s*)*'
        # Return type
        r'(?:void|[A-Za-z0-9<>\[\]]+) '
        # Variable name
        r'(?:[A-Za-z0-9_]+)'
        # Optional assignment value
        r'(?:\s*=\s*[A-Za-z0-9" \.]*)*;)'
    )
    enum_field_pattern = r'^\s*((?:[A-Za-z0-9])+(?:\([A-Za-z0-9-]*\))*);'
    matches = re.findall(field_pattern, code)
    enum_field_matches = re.findall(enum_field_pattern, code)
    fields = []
    for field in matches:
        fields.append(field)
    for field in enum_field_matches:
        fields.append(field)
    return fields


def get_class_signature_info(class_signatures: list[str]) -> list[dict]:
    """Parses the class signature for relevant information

    Args:
        class_signatures (list[str]): all of the signatures in a file

    Returns:
        list[dict]: Parsed signature
    """
    signatures = []
    for signature in class_signatures:
        typ = ('class'if 'class' in signature else
               'enum' if 'enum' in signature else 'interface')
        extends_pattern = r'extends\s*([A-Za-z0-9<>]*)\s*'
        implements_pattern = r'implements\s*([A-Za-z0-9<>]*)\s*'
        name_pattern = (
            # Name
            r'((?:[A-Za-z0-9<>]*))\s*'
            # Helps extract only the name
            r'(?:extends\s*[A-Za-z0-9<>]*)*\s*'
            # Helps extract only the name
            r'(?:implements\s*[A-Za-z0-9<>]*)*\s*\{')
        extends_matches = re.findall(extends_pattern, signature)
        implements_matches = re.findall(implements_pattern, signature)
        name_matches = re.findall(name_pattern, signature)
        signatureInfo = {'signature': signature, 'type': typ}
        if extends_matches:
            signatureInfo['extends'] = extends_matches
        if implements_matches:
            signatureInfo['implements'] = implements_matches
        if name_matches:
            signatureInfo['name'] = name_matches[0]
        signatures.append(signatureInfo)
    return signatures


def parse_class(code: str) -> list[str]:
    """Retrieves the package string at the beginning of the file

    Args:
        code (str): the full text of a java code document

    Returns:
        str: The package declaration, may be empty string
    """
    class_pattern = (
        # Access modifers
        r"((?:public\s*|protected\s*|private\s*)*"
        # class keywork and name
        r"(?:class|enum|interface)\s*(?:[A-Za-z0-9<>]*)\s*"
        # optional extends and name
        r"(?:extends\s*[A-Za-z0-9<>]*)*\s*"
        # optional implements and name
        r"(?:implements\s*[A-Za-z0-9<>]*)*\s*\{)")
    matches = re.findall(class_pattern, code)
    classes = []
    for cls in matches:
        classes.append(cls)
    return classes


def parse_package(code: str) -> str:
    """Retrieves the package string at the beginning of the file

    Args:
        code (str): the full text of a java code document

    Returns:
        str: The package declaration, may be empty string
    """
    package_pattern = r"(package\s+.*;)"
    match = re.findall(package_pattern, code)
    if match:
        return match[0]
    return ""


def parse_imports(code: str) -> list[str]:
    """Retrieves all the imports in a in a file

    Args:
        code (str): the full text of a java code document

    Returns:
        list[str]: All of the imports found, may be empty
    """
    imports = []
    import_pattern = r"(import\s+.*;)"
    matches = re.findall(import_pattern, code)
    for imp in matches:
        imports.append(imp)
    return imports


def parse_methods(code: str, class_signatures: list[dict]) -> list[Method]:
    """Retrieves all the methods in a file, parsing by method comments, method signatures, and method body

    Args:
        code (str): the full text of a java code document

    Returns:
        list[Method]: A list of Methods found in the file, may be empty
    """
    methods = []

    method_signature_pattern = (r'\b(?!\s*if|\s*new|\s*else|\s*while|\s*catch|\s*return|\s*switch|\s*synchronized\b)((?:public\s*|protected\s*)*(?:static\s*|final\s*|native\s*|synchronized\s*|abstract\s*|default\s*|transient\s*)*(?:void\s|[A-Za-z0-9<>\[\]\?, \.]+\s*)(?:\w+\s*)(?:\([A-Za-z0-9 ,<>\?\[\]]*\))(?: throws \w+|))(?:\s*[{;])(?:\n*\s*)'
                                )

    matches = re.findall(method_signature_pattern, code)
    for signature in matches:
        body = get_next_method_body(code, code.index(
            signature)+len(signature))
        if body == "":
            continue
        parent_class = get_parent_class(
            code, code.index(signature)-1, class_signatures)
        if not_method(signature, code, parent_class):
            continue
        method_comment = get_comment_before(
            code, code.index(signature)-1)

        constructor = is_constructor(signature)
        signature_obj = parse_method_signature(signature)

        methods.append(Method(signature_obj, body, method_comment,
                       parent_class, constructor))

    return methods


def parse_method_signature(signature: str) -> MethodSignature:
    """Parse out the components of a java method signature

    Args:
        signature (str): String version of the signature

    Returns:
        MethodSignature: A fully parsed signature object
    """
    signature_parts_pattern = (r'^(public\s|private\s|protected\s)*'
                               r'(static\s)*(synchronized\s)*'
                               r'(void\s|[A-Za-z0-9<>]*\s)*'
                               r'([A-Za-z0-9]*)'
                               r'\(([A-Za-z0-9 <>,\[\]]*)\)')
    match = re.search(signature_parts_pattern, signature)
    if match:
        access = match.group(1) if match.group(1) else ''
        static = match.group(2) if match.group(2) else ''
        synchronized = match.group(3) if match.group(3) else ''
        ret_val = match.group(4) if match.group(4) else ''
        name = match.group(5) if match.group(5) else ''
        parameters = (match.group(6) if match.group(6) else '').split(',')
        return MethodSignature(access, [static, synchronized], ret_val, name, parameters, [])
    return None


def is_constructor(signature: str) -> bool:
    """Simple check if the signature is a constructor

    Args:
        signature (str): the signature we are checking

    Returns:
        bool: result if it is a constructor
    """
    constructor_pattern = r"^\s*((?:public\s*|protected\s*|)(?:[A-Za-z0-9<>])+\s*(?:\([A-Za-z0-9 ,<>\?]*\)))"
    matches = re.findall(constructor_pattern, signature)
    if matches:
        return True
    return False


def not_method(signature: str, code: str, class_signatures: dict) -> bool:
    """Helper method to identify if the signature is a method, or a method call

    Args:
        signature (str): string signature to check
        code (str): code to get context from
        class_signature (dict): all classes found inside code file

    Returns:
        bool: result of if it is a proper method or not
    """
    if not signature or not class_signatures:
        return True
    if class_signatures['type'] == 'interface':
        return False
    next = code.index(signature)+len(signature)
    for c in code[next:]:
        if c == ';':
            return True
        if c == '{':
            return False
    return False


def get_parent_class(code: str, index: int, class_signatures: list[str]) -> str:
    """Reverse searches from index of start of method till it finds a class signature

    Args:
        code (str): source code contents
        index (int): start of the method
        class_signatures (list[str]): all class signatures found in the file

    Returns:
        str: class signature found
    """
    if len(class_signatures) == 1:
        return class_signatures[0]
    for i in range(index, -1, -1):
        if code[i:i+5] == 'class':
            for signature in class_signatures:
                lower = (i-10 if i-10 >= 0 else 0)
                upper = (i+200 if i+200 < len(code) else len(code))
                if signature['signature'] in code[lower:upper]:
                    return signature


def get_comment_before(code: str, index: int) -> str:
    """Retrieves the comment right before the method signature

    Args:
        code (str): the full text of a java document
        index (int): the index right before the start of the method signature

    Returns:
        str: either the comment before, or empty string
    """
    comment = ""
    sampling = False
    for i in range(index, -1, -1):
        if code[i] == '/' and code[i-1] == '*':
            sampling = True
        if sampling:
            comment += code[i]
        if code[i] == '*' and code[i-1] == '*' and code[i-2] == '/':
            comment += "*/"
            sampling = False
            break
        if code[i] == '*' and code[i-1] == '/':
            comment += "/"
            sampling = False
            break
        if not sampling and (code[i] == '}' or code[i] == '{'):
            break

    return comment[::-1]


def find_opening_bracket(code: str, starting_index: int) -> int:
    """Find the next opening bracket - iterates forward from the starting index until '{' is found

    Args:
        code (str): the code that is being iterated through
        starting_index (int): we we start the iteration

    Returns:
        int: index of where we are starting the search
    """
    found = starting_index
    for c in code[starting_index:]:
        found += 1
        if c == '{':
            return found
    return starting_index


def get_next_method_body(code: str, index: int) -> str:
    """Retrieves the next method body, starting at the index given

    Args:
        code (str): the full text of a java document
        index (int): index of where to start looking for the next method

    Returns:
        str: The content of the method body
    """
    index = find_opening_bracket(code, index)
    if code[index] != "{":
        logging.error("Tried to find a method, but none was found")
        return
    curly_stack = []
    body = ""
    for c in code[index:]:
        if c == "{":
            curly_stack.append("{")
        elif c == "}":
            curly_stack.pop()
        body += c
        if len(curly_stack) == 0:
            break
    return body


def parse_class_comments(code: str) -> list[str]:
    """Gets the class comments, matching the '/**' for the start, and '*/' for the end

    Args:
        code (str): the full text of a java document

    Returns:
        list[str]: List of class comments, may be empty
    """
    sampling = False
    current_comment = ""
    comments = []
    for line in code:
        if "class" in line:
            break
        if "/**" in line:
            sampling = True
        if sampling:
            current_comment += line
        if "*/" in line and sampling:
            sampling = False
            comments.append(current_comment)
            current_comment = ""

    return comments


def find_files(package: Path, sub_dir: str) -> list[Path]:
    """Finds all files in a package with a speicifc extension

    Args:
        package (Path): The path to the package we are searching in
        sub_dir (str): The sub directory of 'src' in the package
        ext (str): The extension of the files we are searching for

    Returns:
        list[Path]: The files found, may be empty
    """
    files = []
    for item in package.joinpath(sub_dir).glob('**/*'):
        if item.is_file() and ".java" in str(item.name) and not 'package-info.java' in str(item.name):
            files.append(item)
    return files


def find_packages(repository_root: Path) -> list[Path]:
    """Find the packages in the repository where 'src' is the current directory

    Args:
        repository_root (Path): Root of the project

    Returns:
        list[Path]: List of paths to each package
    """
    packages = []
    for item in repository_root.glob('**/*'):
        if item.is_dir() and "src" in str(item.name):
            packages.append(item)
    return packages
