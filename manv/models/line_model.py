__all__ = [
    "LineModel"
]

class LineModel: ...

class LineModel:
    """
    A line model
    """
    content: str
    line_number: int
    last_line: LineModel | None
    next_line: LineModel | None

    def __init__(self, content: str, line_number: int, last_line: LineModel | None = None, next_line: LineModel | None = None) -> None:
        self.content = content
        self.line_number = line_number
        self.last_line = last_line
        self.next_line = next_line
    
    def __repr__(self):
        return f"LineModel(line_number={self.line_number!r}, content={self.content!r})"
