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


def cert_config_to_string(cert_config: dict[str, str]) -> str:
    return '\n'.join([f"{key}={value}" for key, value in cert_config.items()])


def string_to_cert_config(string: str) -> dict[str, str]:
    cert_config = dict()
    for line in string.split('\n'):
        key, value = line.split('=')
        cert_config[key.strip()] = value.strip()
    return cert_config


def make_cert(cert_config: dict[str, str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=False)
    with path.open('w+') as file:
        file.write(cert_config_to_string(cert_config))


def get_cert() -> dict:
    return {
        "LOAD": DataPack.LOAD_NAME,
        "TICK": DataPack.TICK_NAME,
        "PRIVATE": DataPack.PRIVATE_NAME,
        "VAR": DataPack.VAR_NAME,
        "INT": DataPack.INT_NAME
    }


def read_cert(config: dict[str, str]):
    namespace_folder = Path(config["output"])/config["namespace"]
    cert_file = namespace_folder/JMC_CERT_FILE_NAME
    old_cert_config = get_cert()
    if namespace_folder.is_dir():
        if not cert_file.is_file():
            raise JMCError(
                f"{JMC_CERT_FILE_NAME} file not found in namespace folder.\n To prevent accidental overriding of your datapack please delete the namespace folder yourself.")

        with cert_file.open('r') as file:
            cert_str = file.read()
            try:
                cert_config = string_to_cert_config(cert_str)
            except ValueError:
                cert_config = dict()
            DataPack.LOAD_NAME = cert_config.get(
                "LOAD", old_cert_config["LOAD"])
            DataPack.TICK_NAME = cert_config.get(
                "TICK", old_cert_config["TICK"])
            DataPack.PRIVATE_NAME = cert_config.get(
                "PRIVATE", old_cert_config["PRIVATE"])
            DataPack.VAR_NAME = cert_config.get(
                "VAR", old_cert_config["VAR"])
            DataPack.INT_NAME = cert_config.get(
                "INT", old_cert_config["INT"])
            cert_config = get_cert()
        rmtree(namespace_folder.resolve().as_posix())
    else:
        cert_config = old_cert_config
    make_cert(cert_config, cert_file)


def build(datapack: DataPack, config: dict[str, str]):
    logger.debug("Building")
    datapack.build()
    namespace_folder = Path(config["output"])/config["namespace"]
    for func_path, func in datapack.functions.items():
        path = namespace_folder/(func_path+'.mcfunction')
        path.parent.mkdir(parents=True, exist_ok=True)
        content = func.content
        if content:
            with path.open('w+') as file:
                file.write(func.content)

    for json_path, json in datapack.jsons.items():
        path = namespace_folder/(json_path+'.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        if json:
            with path.open('w+') as file:
                file.write(dumps(json, indent=2))
