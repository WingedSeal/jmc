import logging
import sys
from pathlib import Path
import jmc

logger = jmc.Logger(__name__)


def compile(config: dict) -> None:
    if config['debug_mode']:
        jmc.debug()
    config['target_file'] = Path(config['target_file'])
    config['output'] = Path(config['output'])
    with config['target_file'].open('r') as file:
        jmc_string = file.read()
    pack_global = jmc.PackGlobal(config)

    # clean_comments() MUST come before clean_whitespace
    jmc_string = jmc.utils.clean_comments(jmc_string)
    jmc_string = jmc.utils.clean_comments(jmc_string)
    jmc_string = jmc.imports.handle_imports(jmc_string, pack_global)
    jmc_string = jmc.utils.clean_whitespace(jmc_string)
    jmc_string = jmc._class.replace_class(jmc_string)
    jmc_string = jmc.if_else.capture_if_else(jmc_string, pack_global)
    jmc_string = jmc.function.capture_function(
        jmc_string, pack_global)
    pack_global.functions['__load__'] = jmc.function.Function(
        '__load__', jmc_string, pack_global)
    logger.info(pack_global)
    pack_global.compile()
