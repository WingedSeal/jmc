import logging
import sys
from pathlib import Path
import jmc

logger = jmc.Logger(__name__, logging.DEBUG)


def main():

    target_file = Path(sys.argv[1])
    with target_file.open() as file:
        jmc_string = file.read()
    pack_global = jmc.PackGlobal(target_file)

    jmc_string = jmc.utils.clean_whitespace(jmc_string)
    jmc_string = jmc.utils.clean_comments(jmc_string)
    jmc_string = jmc.imports.handle_imports(jmc_string, pack_global)
    jmc_string = jmc.utils.custom_syntax(jmc_string, pack_global)
    jmcfunctions, jmc_string = jmc.function.capture_function(
        jmc_string, pack_global)
    jmc_string = jmc.function.replace_function_call(jmc_string, pack_global)

    logger.debug(f"""Leftover jmc_string:
    {jmc_string[:300]}
    . . .""")

    jmc_load = [jmc.command.Command(command, pack_global) for command in jmc_string.split(
        '; ') if command]
    nl = '\n'

    logger.debug(
        f"jmc_load.mcfunction (Commands): {nl.join([str(command) for command in jmc_load])}")
    logger.info(pack_global)


if __name__ == '__main__':
    logger.info("""
----------
compile.py
----------""")
    if len(sys.argv) == 2 and sys.argv[1].endswith('.jmc'):
        main()
        logger.debug(f'sys.argv = {sys.argv}')
    else:
        print('Invalid arguments, the proper usage is "python compile.py <FILE_NAME>.jmc"')
        logger.info(f'sys.argv = {sys.argv}')
