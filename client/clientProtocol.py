def build_command(command, params):
    """Build a command string using an opcode and parameters.

    Joins parameters with '@#' delimiter and prepends the command opcode.

    :param command: The opcode for the command.
    :param params: List of parameters for the command.
    :return: Formatted command string.
    """
    return str(command) + "@#".join(params)


def unpack(data):
    """Unpack a command string into opcode and parameters.

    Splits the command string by '@#' to extract parameters.

    :param data: Command string to unpack.
    :return: Tuple of (opcode, parameters list).
    """
    opcode = data[0]
    params = data[1:].split("@#")
    return opcode, params
