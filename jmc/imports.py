import re
from typing import List
from . import Logger, PackGlobal
from .module import Module
import logging

logger = Logger(__name__)
IMPORT_REGEX = r'@import [\'\"](.*?)[\'\"];'


def handle_imports(string: str, pack_global: PackGlobal) -> str:
    """Create modules from "@import '<PATH>';" commands and remove the command from the string before returning"""
    logger.info("Handling imports")
    imports_match: List[re.Match] = re.finditer(
        IMPORT_REGEX, string)
    for import_match in imports_match:
        path: str = import_match.groups()[0]
        if not path.endswith('.jmc'):
            path += '.jmc'
        pack_global.imports.append(
            Module(path, pack_global))
    string = re.sub(IMPORT_REGEX, '', string)
    for module in pack_global.imports:
        string = module.context + ' ' + string
    return string
