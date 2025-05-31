import io
import struct

from awesome_image_editor.binary_io.read import (
    read_uint32_le,
    read_pascal_string,
    read_unicode_string,
    read_float_le,
)

# Tests for read_uint32_le
def test_read_uint32_le_simple():
    value = 12345
    data = value.to_bytes(4, 'little', signed=False)
    reader = io.BytesIO(data)
    assert read_uint32_le(reader) == value

def test_read_uint32_le_max_value():
    value = 2**32 - 1
    data = value.to_bytes(4, 'little', signed=False)
    reader = io.BytesIO(data)
    assert read_uint32_le(reader) == value

def test_read_uint32_le_zero():
    value = 0
    data = value.to_bytes(4, 'little', signed=False)
    reader = io.BytesIO(data)
    assert read_uint32_le(reader) == value

# Tests for read_pascal_string
def test_read_pascal_string_simple():
    string_data = b"Hello Pascal"
    length_data = len(string_data).to_bytes(4, 'little', signed=False)
    reader = io.BytesIO(length_data + string_data)
    assert read_pascal_string(reader) == string_data

def test_read_pascal_string_empty():
    string_data = b""
    length_data = len(string_data).to_bytes(4, 'little', signed=False)
    reader = io.BytesIO(length_data + string_data)
    assert read_pascal_string(reader) == string_data

# Tests for read_unicode_string
def test_read_unicode_string_simple():
    string_data_utf8 = "Hello Unicode".encode('utf-8')
    length_data = len(string_data_utf8).to_bytes(4, 'little', signed=False)
    reader = io.BytesIO(length_data + string_data_utf8)
    assert read_unicode_string(reader) == "Hello Unicode"

def test_read_unicode_string_non_ascii():
    string_data_utf8 = "你好世界".encode('utf-8')
    length_data = len(string_data_utf8).to_bytes(4, 'little', signed=False)
    reader = io.BytesIO(length_data + string_data_utf8)
    assert read_unicode_string(reader) == "你好世界"

def test_read_unicode_string_empty():
    string_data_utf8 = "".encode('utf-8')
    length_data = len(string_data_utf8).to_bytes(4, 'little', signed=False)
    reader = io.BytesIO(length_data + string_data_utf8)
    assert read_unicode_string(reader) == ""

# Tests for read_float_le
def test_read_float_le_positive():
    value = 3.14
    data = struct.pack("<f", value)
    reader = io.BytesIO(data)
    assert abs(read_float_le(reader) - value) < 1e-6 # Compare with tolerance for float

def test_read_float_le_negative():
    value = -2.71
    data = struct.pack("<f", value)
    reader = io.BytesIO(data)
    assert abs(read_float_le(reader) - value) < 1e-6

def test_read_float_le_zero():
    value = 0.0
    data = struct.pack("<f", value)
    reader = io.BytesIO(data)
    assert abs(read_float_le(reader) - value) < 1e-6
