from code_file import CodeFile
import json
from method import Method
from package import Package
from pathlib import Path
import re
from static_analysis_data import StaticAnalysisData


def preprocess(directory: Path, ext: str) -> list[Package]:
    """Preprocesses the entire repository by creating Package objects with the parsed data from all of the files

    Args:
        directory (Path): Path to the root of the repository that is being preprocessed
        ext (str): Extension of the language being parsed (6/1/2023 - Only supports Java)

    Returns:
        list[Package]: All the parsed packages from the repository
    """
    packages = []
    package_dirs: list[Path] = find_packages(directory)
    for package in package_dirs:

        source_file_paths = find_files(package, "main", ext)
        test_file_paths = find_files(package, "test", ext)
        source_files = {}
        test_files = {}
        analysis_data = run_static_code_analysis(package)

        for file in source_file_paths:
            code: CodeFile = parse_file(file)
            if code is None:
                continue
            source_files[str(file.absolute())] = code
        for file in test_file_paths:
            code: CodeFile = parse_file(file)
            if code is None:
                continue
            test_files[str(file.absolute())] = code
            print(code.imports)

        packages.append(Package(package, source_files,
                        analysis_data, test_files))
    return packages


def parse_file(file: Path) -> CodeFile:
    """Parses a java file for useful context information, including package, imports, class comments, and methods

    Args:
        file (Path): Path of the java file

    Returns:
        CodeFile: CodeFile object with relevant parsed data, may be None if there are no methods present
    """
    with open(file, "r") as input_file:
        java_code = input_file.read()
        package = get_package(java_code)
        imports = get_imports(java_code)
        class_comments = get_class_comments(java_code.splitlines())
        methods = get_methods(java_code)
        if len(methods) == 0:
            return None
        return CodeFile(class_comments, methods, file, package, imports)


def get_package(code: str) -> str:
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


def get_imports(code: str) -> list[str]:
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


def get_methods(code: str) -> list[Method]:
    """Retrieves all the methods in a file, parsing by method comments, method signatures, and method body

    Args:
        code (str): the full text of a java code document

    Returns:
        list[Method]: A list of Methods found in the file, may be empty
    """
    methods = []
    method_signature_pattern = (
        # don't match keywords
        r"\b(?!\s*if|\s*new|\s*else|\s*while|\s*catch|\s*return|\s*switch|\s*synchronized\b)"
        # match access modifiers
        r"((?:public\s*|private\s*|protected\s*)*"
        # match modifiers
        r"(?:static\s*|final\s*|native\s*|synchronized\s*|abstract\s*|default\s*|transient\s*)*"
        # match return type
        r"(?:void\s|[A-Za-z0-9<>\[\]\?, \.]+\s*)"
        # match method name
        r"(?:\w+\s*)"
        # match method parameters
        r"(?:\([A-Za-z0-9 ,<>\?]*\))"
        # match exception throws
        r"(?: throws \w+|))"
        # match curly brackets and new lines
        r"(?:\s*{)(?:\n*\s*)")

    matches = re.findall(method_signature_pattern, code)
    for signature in matches:
        body = get_next_method(code, code.index(signature)+len(signature)+1)
        method_comment = get_comment_before(code, code.index(signature)-1)
        if body == "":
            continue
        methods.append(Method(signature, body, method_comment))
    return methods


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


def get_next_method(code: str, index: int) -> str:
    """Retrieves the next method, starting at the index given

    Args:
        code (str): the full text of a java document
        index (int): index of where to start looking for the next method

    Returns:
        str: _description_
    """
    if code[index] != "{":
        print("Expected a '{' " + f"but got '{code[index]}'")
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


def get_class_comments(code: str) -> list[str]:
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


def find_files(package: Path, sub_dir: str, ext: str) -> list[Path]:
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
        if item.is_file() and "."+ext in str(item.name):
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


def run_static_code_analysis(package: Path) -> dict:
    """Run the PMD static code analysis cli tool, and return the results

    Args:
        package (Path): Path to the package to run the analysis on

    Returns:
        dict: Key - Path to file, Value - StaticAnalysisData where we have the path, and the violations
    """
    output_file = package.joinpath('output.json')
    staticAnalysisData = {}
    with open(output_file) as file:
        data = json.load(file)
        for file in data["files"]:
            staticAnalysisData[file["filename"]] = StaticAnalysisData(
                file["filename"], file["violations"])
    return staticAnalysisData
    # All of this was pregenerated to save time
    # command = [
    #     '/Users/jake/Applications/pmd-bin-7.0.0-rc2/bin/pmd', 'check',
    #     '-D', package.absolute(),
    #     '-R', 'rulesets/java/quickstart.xml',
    #     '-f', 'json'
    # ]

    # output_file = package.joinpath('output.json')

    # with open(output_file, 'w') as f:
    #     process = subprocess.Popen(command, stdout=f, stderr=subprocess.PIPE)
    #     _, stderr = process.communicate()

    #     if process.returncode == 0:
    #         print('Command executed successfully.')
    #     else:
    #         print(f'Command failed with return code {process.returncode}.')
    #         print('Error output:')
    #         print(stderr.decode('utf-8'))
    #     pass
