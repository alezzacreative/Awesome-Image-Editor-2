import struct
from io import BufferedWriter


def write_uint32_le(value: int, writer: BufferedWriter):
    data = value.to_bytes(4, "little", signed=False)
    writer.write(data)


def write_float_le(value: float, writer: BufferedWriter):
    writer.write(struct.pack("<f", value))


def write_pascal_string(string: bytes, writer: BufferedWriter):
    write_uint32_le(len(string), writer)
    writer.write(string)


def write_unicode_string(string: str, writer: BufferedWriter):
    data = string.encode("utf-8")
    write_uint32_le(len(data), writer)
    writer.write(data)
