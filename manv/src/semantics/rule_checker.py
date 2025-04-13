
# MIT License

# Copyright (c) 2025 ramsy0dev

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__all__ = [
    "RuleChecker"
]

# Base AST
from manv.src.ast.base import ASTNode

# Models
from manv.models.line_model import LineModel

class RuleChecker:
    def __init__(self) -> None:
        pass

    def check_rules(self, program: ASTNode) -> None:
        """
        Language rules
        """
        # Constant declaration
        
    def check_constant_rules(self, constant: Constant) -> tuple[bool, str]:
        """
        Check constant rules
        """
        pass

    def check_variable_rules(self, variable: Variable) -> tuple[bool, str]:
        """
        Check variable rules
        """
        pass
    
    def call_stack(self, last_line: LineModel, current_line: LineModel, next_line: LineModel) -> str:
        """
        Call stack trace.
        """
        last_line_source_code = last_line.content
        current_line_source_code = current_line.content
        next_line_source_code = next_line.content
        
        msg = (
            f"\t   {last_line.line_number} | {last_line_source_code.strip()}\n"
            f"\t-> {current_line.line_number} | {current_line_source_code.strip()}\n"
            f"\t   {next_line.line_number} | {next_line_source_code.strip()}\n"
        )

        return msg
