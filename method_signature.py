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
