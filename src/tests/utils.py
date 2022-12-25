def string_to_tree_dict(string: str) -> dict[str, str]:
    """
    Parse multiline string to dictionary of file name and file content

    :param string: Multiline String
    :return: Dictionary of file name and file content

    .. example::
    >>> string_to_tree_dict(\"\"\"
    > FILE_NAME_1
    FILE_CONTENT_1_1
    FILE_CONTENT_1_2
    > FILE_NAME_2
    FILE_CONTENT_2_1
    FILE_CONTENT_2_2
    \"\"\")
    {"FILE_NAME_1":"FILE_CONTENT_1_1\\nFILE_CONTENT_1_2",
    "FILE_NAME_2":"FILE_CONTENT_2_1\\nFILE_CONTENT_2_2"}
    """
    lines = string.split("\n")
    if lines[0] and not lines[0].isspace():
        raise ValueError(
            "String given is doesn't start with empty lines")
    if lines[-1] and not lines[-1].isspace():
        raise ValueError(
            "String given is doesn't end with empty lines")

    del lines[0]
    del lines[-1]

    result: dict[str, str] = {}
    key: None | str = None
    value: None | str = None

    for line in lines:
        if line.startswith("> "):

            if value is None and key is None:
                key = line[2:]  # len("> ") = 2
            elif value is None and key is not None:
                raise ValueError(
                    "File name is given without file content")
            elif value is not None and key is None:
                raise NotImplementedError("This case shouldn't be possible")
            elif value is not None and key is not None:
                result[key] = value
                value = None
                key = line[2:]  # len("> ") = 2

            continue

        if key is None:
            raise ValueError(
                "File content is given without file name")

        if value is None:
            value = line
        else:
            value += "\n" + line

    if value is None:
        raise ValueError(
            "File name is given without file content")
    if key is not None:
        result[key] = value

    return result
