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
    "ASM",
]

class ASM:
    """
    ASM object for holding the generated assembly
    """
    def __init__(self):
        self.section_data: dict[str, list[str]] = {}
        self.section_bss: dict[str, list[str]] = {}
        self.section_text: dict[str, list[str]] = {}

    def add_to_section(self, section: str, label: str, code: list[str] | str):
        """
        Add code to a specific section under a named label (block).
        """
        target = {
            'data': self.section_data,
            'bss': self.section_bss,
            'text': self.section_text
        }.get(section)

        if target is None:
            raise ValueError(f"Unknown section: {section}")

        if label not in target:
            target[label] = []

        if isinstance(code, str):
            target[label].append(code)
        elif isinstance(code, list):
            for line in code:
                if len(line) == 0:
                    continue
                
                target[label].append(line)

    def get_assembly(self) -> str:
        """
        Output the final NASM code, grouped by section and label.
        """
        def format_section(section_name: str, section_dict: dict[str, list[str]]) -> str:
            if not section_dict:
                return ""
            result = f"section .{section_name}\n"
            for label, lines in section_dict.items():
                result += f"\n; -- {label} --\n"
                for line in lines:
                    result += line
            return result

        return (
            format_section("data", self.section_data) +
            format_section("bss", self.section_bss) +
            format_section("text", self.section_text)
        )