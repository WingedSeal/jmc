import logging
import sys
from pathlib import Path
import jmc

logger = jmc.Logger(__name__, logging.DEBUG)


def main():

    target_file = Path(sys.argv[1])
    with target_file.open() as file:
        jmc_string = jmc.utils.clean_whitespace(file.read())
    load_json = jmc.LoadJson()
    jmcfunctions, jmc_string = jmc.function.capture_function(
        jmc_string, load_json)
    logger.debug(f"""Leftover jmc_string (first 100 char):
    {jmc_string[:100]}
    . . .""")

    logger.info(load_json)


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
