class MethodSignature:
    def __init__(self, access: str, modifiers: list[str], ret_val: str, name: str, parameters: list[str], exceptions: list[str]) -> None:
        self.access = access
        self.modifiers = modifiers
        self.ret_val = ret_val
        self.name = name
        self.exceptions = exceptions
        self.parameters = parameters

    def to_dict(self):
        return {"access": self.access,
                "modifiers": self.modifiers,
                "ret_val": self.ret_val,
                "name": self.name,
                "parameters": self.parameters}

    def __str__(self) -> str:
        return f'{self.access} {[modifier for modifier in self.modifiers]} {self.ret_val} {self.name}({[parameter for parameter in self.parameters]})'
