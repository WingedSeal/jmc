from json import dumps
from shutil import rmtree
from pathlib import Path

from .lexer import Lexer
from .log import Logger
from .datapack import DataPack
from .exception import JMCError


logger = Logger(__name__)
JMC_CERT_FILE_NAME = 'jmc.txt'


def compile(config: dict[str, str], debug: bool = False) -> None:
    logger.info("Configuration:\n"+dumps(config, indent=2))
    read_cert(config)
    logger.info("Parsing")
    lexer = Lexer(config)
    if debug:
        logger.info(f'Datapack :{lexer.datapack!r}')
    build(lexer.datapack, config)


def read_cert(config: dict[str, str]):
    old_cert_config = f"""LOAD={DataPack.LOAD_NAME}
TICK={DataPack.TICK_NAME}
PRIVATE={DataPack.PRIVATE_NAME}"""

    namespace_folder = Path(config["output"])/config["namespace"]
    jmc_cert = namespace_folder/JMC_CERT_FILE_NAME
    if namespace_folder.is_dir():
        if not jmc_cert.is_file():
            raise JMCError(
                f"{JMC_CERT_FILE_NAME} file not found in namespace folder.\n To prevent accidental overriding of your datapack please delete the namespace folder yourself.")

        with jmc_cert.open('r') as file:
            jmc_cert_str = file.read()
            try:
                cert_config = dict()
                for line in jmc_cert_str.split('\n'):
                    key, value = line.split('=')
                    cert_config[key.strip()] = value.strip()
                DataPack.LOAD_NAME = cert_config["LOAD"]
                DataPack.TICK_NAME = cert_config["TICK"]
                DataPack.PRIVATE_NAME = cert_config["PRIVATE"]
            except ValueError:
                logger.warning(f"Fail to parse {JMC_CERT_FILE_NAME}")
                with jmc_cert.open('w+') as file:
                    file.write(old_cert_config)
                cert_config = dict()
                for line in old_cert_config.split('\n'):
                    key, value = line.split('=')
                    cert_config[key.strip()] = value.strip()
                DataPack.LOAD_NAME = cert_config["LOAD"]
                DataPack.TICK_NAME = cert_config["TICK"]
                DataPack.PRIVATE_NAME = cert_config["PRIVATE"]

    else:
        namespace_folder.mkdir(exist_ok=True)
        with jmc_cert.open('w+') as file:
            file.write(old_cert_config)


def build(datapack: DataPack, config: dict[str, str]):
    logger.debug("Building")
