"""Module responsibile for all compiling in jmc"""
from json import JSONDecodeError, dump, dumps, loads
from shutil import rmtree
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .header import parse_header, Header
from .lexer import Lexer
from .log import Logger
from .datapack import DataPack
from .exception import JMCBuildError

if TYPE_CHECKING:
    from ..terminal import Configuration

logger = Logger(__name__)
JMC_CERT_FILE_NAME = 'jmc.txt'


def compile_jmc(config: "Configuration", debug: bool = False) -> None:
    """
    Compile the files and build the datapack

    :param config: Configuration dictionary
    :param debug: Whether to debug into log, defaults to False
    """
    logger.info("Configuration:\n" + dumps(config.toJSON(), indent=2))
    Header.clear()
    read_cert(config)
    read_header(config)
    logger.info("Parsing")
    lexer = Lexer(config)
    if debug:
        logger.info(f'Datapack :{lexer.datapack!r}')
    build(lexer.datapack, config)


def cert_config_to_string(cert_config: dict[str, str]) -> str:
    """
    Turns certificate configuration dictionary into a string for output

    :param cert_config: Certificate configuration dictionary
    :return: Converted string
    """
    return '\n'.join([f"{key}={value}" for key, value in cert_config.items()])


def string_to_cert_config(string: str) -> dict[str, str]:
    """
    Turns string into certificate configuration dictionary for further read

    :param string: String for convertion
    :return: Converted cert_config
    """
    cert_config = {}
    for line in string.split('\n'):
        if not line or line.isspace():
            continue
        key, value = line.split('=')
        cert_config[key.strip()] = value.strip()
    return cert_config


def make_cert(cert_config: dict[str, str], path: Path) -> None:
    """
    Write certificate file

    :param cert_config: Certificate configuration
    :param path: Path to write `cert_config` to
    """
    path.parent.mkdir(parents=True, exist_ok=False)
    with path.open('w+') as file:
        file.write(cert_config_to_string(cert_config))


def get_cert() -> dict[str, str]:
    """
    Make a new Certificate configuration from current DataPack class info

    :return: Certificate configuration
    """
    return {
        "LOAD": DataPack.load_name,
        "TICK": DataPack.tick_name,
        "PRIVATE": DataPack.private_name,
        "VAR": DataPack.var_name,
        "INT": DataPack.int_name
    }


def read_header(config: "Configuration",
                _test_file: str | None = None) -> bool:
    """
    Read the main header file

    :param config: JMC configuration
    :return: Whether the main header file was found
    """
    header = Header()
    header_file = Path(config.target_str[:-len(".jmc")] + ".hjmc")
    parent_target = Path(config.target_str).parent
    if header_file.is_file() or _test_file is not None:
        header.add_file_read(header_file)
        logger.info("Header file found.")
        if _test_file is None:
            with header_file.open('r', encoding="utf-8") as file:
                header_str = file.read()
        else:
            header_str = _test_file
        logger.info(f"Parsing {header_file}")
        parse_header(header_str, header_file.as_posix(), parent_target)
        return True

    logger.info("Header file not found.")
    return False


def read_cert(config: "Configuration", _test_file: str | None = None):
    """
    Read Certificate(JMC.txt)

    :param config: JMC configuration
    :raises JMCBuildError: Can't find JMC.txt
    """
    namespace_folder = Path(config.output) / 'data' / config.namespace
    cert_file = namespace_folder / JMC_CERT_FILE_NAME
    old_cert_config = get_cert()
    if namespace_folder.is_dir() or _test_file is not None:
        if not cert_file.is_file() and _test_file is None:
            raise JMCBuildError(
                f"{JMC_CERT_FILE_NAME} file not found in namespace folder.\n To prevent accidental overriding of your datapack please delete the namespace folder yourself.")
        if _test_file is None:
            with cert_file.open('r') as file:
                cert_str = file.read()
        else:
            cert_str = _test_file
        try:
            cert_config = string_to_cert_config(cert_str)
        except ValueError:
            cert_config = {}
        DataPack.load_name = cert_config.get(
            "LOAD", old_cert_config["LOAD"])
        DataPack.tick_name = cert_config.get(
            "TICK", old_cert_config["TICK"])
        DataPack.private_name = cert_config.get(
            "PRIVATE", old_cert_config["PRIVATE"])
        DataPack.var_name = cert_config.get(
            "VAR", old_cert_config["VAR"])
        DataPack.int_name = cert_config.get(
            "INT", old_cert_config["INT"])
        cert_config = get_cert()
        if _test_file is None:
            rmtree(namespace_folder.resolve().as_posix())
    else:
        cert_config = old_cert_config
    if _test_file is None:
        make_cert(cert_config, cert_file)


def read_func_tag(path: Path, config: "Configuration") -> dict[str, Any]:
    """
    Read minecraft function tag file

    :param path: Path to minecraft function tag file
    :param config: JMC configuration
    :raises JMCBuildError: MalformedJsonException
    :raises JMCBuildError: Can't find `values` key in json
    :return: Content of function tag file in dictionary
    """
    if path.is_file():
        with path.open('r') as file:
            content = file.read()
        try:
            json: dict[str, Any] = loads(content)
            json["values"] = [
                value for value in json["values"] if not value.startswith(config.namespace + ':')]
        except JSONDecodeError as error:
            raise JMCBuildError(
                f"MalformedJsonException: Cannot parse {path.resolve().as_posix()}. Deleting the file to reset.") from error
        except KeyError as error:
            raise JMCBuildError(
                f'"values" key not found in {path.resolve().as_posix()}. Deleting the file to reset.') from error
    else:
        json = {"values": []}
    return json


def post_process(string: str) -> str:
    """
    Post processing of .mcfunction files

    - Add credits at the end of every .mcfunction file

    :param string: File content
    :return: Processed file content
    """
    header = Header()
    if not header.credits:
        return string

    string += "\n" * 2
    for line in header.credits:
        string += f"\n# {line}" if line else "\n#"
    return string


def build(datapack: DataPack, config: "Configuration",
          _is_virtual: bool = False) -> dict[str, str] | None:
    """
    Build and write files for minecraft datapack

    :param datapack: DataPack object
    :param config: JMC configuration
    :param _is_virtual: Whether to make a dictionary of output result instead of writing to files
    :returns: Dictionary of file path and file content if _is_virtual is True
    """
    output: dict[str, Any] = {}

    logger.debug(f"Building (_is_virtual={_is_virtual})")
    datapack.build()
    output_folder = Path(config.output)
    namespace_folder = output_folder / 'data' / config.namespace
    functions_tags_folder = output_folder / \
        'data' / 'minecraft' / 'tags' / 'functions'

    if not _is_virtual:
        functions_tags_folder.mkdir(exist_ok=True, parents=True)
    load_tag = functions_tags_folder / 'load.json'
    tick_tag = functions_tags_folder / 'tick.json'

    load_json = {"values": []} if _is_virtual else read_func_tag(
        load_tag, config)
    tick_json = {"values": []} if _is_virtual else read_func_tag(
        tick_tag, config)

    load_json["values"].append(f'{config.namespace}:{DataPack.load_name}')
    if _is_virtual:
        output[load_tag.as_posix()] = dumps(load_json, indent=2)
    else:
        with load_tag.open('w+') as file:
            dump(load_json, file, indent=2)

    if DataPack.tick_name in datapack.functions and datapack.functions[DataPack.tick_name]:
        tick_json["values"].append(
            f'{config.namespace}:{DataPack.tick_name}')
        if _is_virtual:
            output[tick_tag.as_posix()] = dumps(tick_json, indent=2)
        else:
            with tick_tag.open('w+') as file:
                dump(tick_json, file, indent=2)

    for func_path, func in datapack.functions.items():
        path = namespace_folder / 'functions' / (func_path + '.mcfunction')
        content = post_process(func.content)
        if content:
            if _is_virtual:
                output[path.as_posix()] = content
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('w+') as file:
                    file.write(content)

    for json_path, json in datapack.jsons.items():
        # if json_path.startswith("minecraft/"):
        #     path = namespace_folder / (json_path + '.json')
        # else:
        #     # len("minecraft/") = 10
        #     path = output_folder / 'data' / 'minecraft' / (json_path[10:] + '.json')
        path = namespace_folder / (json_path + '.json')
        if json:
            if _is_virtual:
                output[path.as_posix()] = dumps(json, indent=2)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('w+') as file:
                    dump(json, file, indent=2)
    if _is_virtual:
        return output

    with (output_folder / 'pack.mcmeta').open('w+') as file:
        dump({
            "pack": {
                "pack_format": int(config.pack_format),
                "description": config.description
            }
        }, file, indent=2)
    return None
