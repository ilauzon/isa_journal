"""Houses the MdPage and HtmlPage classes."""

from dataclasses import dataclass

@dataclass
class MdPage:
    title: str
    contents: str

@dataclass
class HtmlPage:
    filename: str
    title: str
    contents: str
