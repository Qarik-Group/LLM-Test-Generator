import pathlib


class StaticAnalysisData:
    def __init__(self, file: pathlib.Path, violations: list[str]):
        self.file = file
        self.violations = violations

    def __str__(self):
        return f"{self.file} -- {len(self.violations)}"
