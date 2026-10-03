"""PPT Sandbox — factory untuk membuat .pptx full-editable dari Brief YAML/JSON."""
from .builder import build_from_brief, build_from_dict

__all__ = ["build_from_brief", "build_from_dict"]
__version__ = "1.0.0"
