def unpack(data):
    """Unpack a command string into opcode and parameters.

    Extracts the opcode and splits parameters by '@#' delimiter if present.

    :param data: Command string to unpack.
    :return: Tuple of (opcode, parameters list).
    """
    opcode = data[:2]
    params = []
    if len(data) > 2:
        params = data[2:].split("@#")

    for i, v in enumerate(params):
        if "#@" in v:
            params[i] = v.split("#@")

    return opcode, params


print(unpack("19"))
