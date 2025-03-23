__all__ = [
    "LineModel"
]

class LineModel:
    """
    A line model
    """
    def __init__(self, content: str, line_number: int) -> None:
        self.content = content
        self.line_number = line_number
    
    def __repr__(self):
        return f"<Line: line_number={self.line_number!r}, content='{self.content!r}'>"
