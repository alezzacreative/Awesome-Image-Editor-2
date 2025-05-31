import struct
from io import BufferedWriter


def write_uint32_le(value: int, writer: BufferedWriter) -> None:
    """
    Writes a 32-bit unsigned integer to the writer in little-endian format.

    Args:
        value: The 32-bit unsigned integer to write.
        writer: The BufferedWriter to write to.
    """
    data = value.to_bytes(4, "little", signed=False)
    writer.write(data)


def write_float_le(value: float, writer: BufferedWriter) -> None:
    """
    Writes a 32-bit floating-point number to the writer in little-endian format.

    Args:
        value: The float to write.
        writer: The BufferedWriter to write to.
    """
    writer.write(struct.pack("<f", value))


def write_pascal_string(string: bytes, writer: BufferedWriter) -> None:
    """
    Writes a Pascal string (length-prefixed) to the writer.

    The length is written as a 32-bit unsigned little-endian integer.

    Args:
        string: The bytes of the Pascal string to write.
        writer: The BufferedWriter to write to.
    """
    write_uint32_le(len(string), writer)
    writer.write(string)


def write_unicode_string(string: str, writer: BufferedWriter) -> None:
    """
    Writes a Unicode string (UTF-8 encoded, length-prefixed) to the writer.

    The length is written as a 32-bit unsigned little-endian integer.

    Args:
        string: The Unicode string to write.
        writer: The BufferedWriter to write to.
    """
    data = string.encode("utf-8")
    write_uint32_le(len(data), writer)
    writer.write(data)
