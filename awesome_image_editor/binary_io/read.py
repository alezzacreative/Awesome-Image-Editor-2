import struct
from io import BufferedReader


def read_uint32_le(reader: BufferedReader):
    data = reader.read(4)
    assert len(data) == 4
    return int.from_bytes(data, "little", signed=False)


def read_pascal_string(reader: BufferedReader):
    length = read_uint32_le(reader)
    string = reader.read(length)
    assert len(string) == length
    return string


def read_unicode_string(reader: BufferedReader):
    length = read_uint32_le(reader)
    data = reader.read(length)
    assert len(data) == length
    return data.decode("utf-8")


def read_float_le(reader: BufferedReader):
    data = reader.read(4)
    assert len(data) == 4  # struct should already error out, assert for consistency
    return struct.unpack("<f", data)[0]
