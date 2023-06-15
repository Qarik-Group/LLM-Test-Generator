import textwrap


class Method:
    def __init__(self, signature: str, body: str, comment: str, parent_class: str, is_constructor: bool) -> None:
        self.signature = signature
        self.body = body
        self.comment = comment
        self.parent_class = parent_class
        self.is_constructor = is_constructor

    def __str__(self) -> str:
        body_indent = ""
        if self.body:
            body_indent = textwrap.indent(self.body, '\t')
        comment_indent = ""
        if self.comment:
            comment_indent = textwrap.indent(self.comment, '\t')
        return f"{comment_indent}\n\t{self.signature}\n{body_indent}"
