from method import Method
from pathlib import Path


class CodeFile:
    def __init__(self, class_comments: list[str], methods: list[Method], path: Path, package: str, imports: list[str]) -> None:
        self.class_comments = class_comments
        self.methods = methods
        self.path = path
        self.package = package
        self.imports = imports

    def test_name(self) -> str:
        return self.path.with_stem(self.path.stem + "Test").name
