import struct
from io import BufferedReader


def read_uint32_le(reader: BufferedReader) -> int:
    """
    Reads a 32-bit unsigned integer from the reader in little-endian format.

    Args:
        reader: The BufferedReader to read from.

    Returns:
        The 32-bit unsigned integer read from the reader.
    """
    data = reader.read(4)
    assert len(data) == 4
    return int.from_bytes(data, "little", signed=False)


def read_pascal_string(reader: BufferedReader) -> bytes:
    """
    Reads a Pascal string (length-prefixed) from the reader.

    The length is read as a 32-bit unsigned little-endian integer.

    Args:
        reader: The BufferedReader to read from.

    Returns:
        The bytes of the Pascal string.
    """
    length = read_uint32_le(reader)
    string = reader.read(length)
    assert len(string) == length
    return string


def read_unicode_string(reader: BufferedReader) -> str:
    """
    Reads a Unicode string (UTF-8 encoded, length-prefixed) from the reader.

    The length is read as a 32-bit unsigned little-endian integer.

    Args:
        reader: The BufferedReader to read from.

    Returns:
        The Unicode string.
    """
    length = read_uint32_le(reader)
    data = reader.read(length)
    assert len(data) == length
    return data.decode("utf-8")


def read_float_le(reader: BufferedReader) -> float:
    """
    Reads a 32-bit floating-point number from the reader in little-endian format.

    Args:
        reader: The BufferedReader to read from.

    Returns:
        The float read from the reader.
    """
    data = reader.read(4)
    assert len(data) == 4  # struct should already error out, assert for consistency
    return struct.unpack("<f", data)[0]
