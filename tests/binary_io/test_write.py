import io
import struct

from awesome_image_editor.binary_io.write import (
    write_uint32_le,
    write_float_le,
    write_pascal_string,
    write_unicode_string,
)

# Tests for write_uint32_le
def test_write_uint32_le_simple():
    writer = io.BytesIO()
    value = 67890
    write_uint32_le(value, writer)
    expected_bytes = value.to_bytes(4, 'little', signed=False)
    assert writer.getvalue() == expected_bytes

def test_write_uint32_le_max_value():
    writer = io.BytesIO()
    value = 2**32 - 1
    write_uint32_le(value, writer)
    expected_bytes = value.to_bytes(4, 'little', signed=False)
    assert writer.getvalue() == expected_bytes

def test_write_uint32_le_zero():
    writer = io.BytesIO()
    value = 0
    write_uint32_le(value, writer)
    expected_bytes = value.to_bytes(4, 'little', signed=False)
    assert writer.getvalue() == expected_bytes

# Tests for write_float_le
def test_write_float_le_positive():
    writer = io.BytesIO()
    value = 1.618
    write_float_le(value, writer)
    expected_bytes = struct.pack("<f", value)
    assert writer.getvalue() == expected_bytes

def test_write_float_le_negative():
    writer = io.BytesIO()
    value = -0.577
    write_float_le(value, writer)
    expected_bytes = struct.pack("<f", value)
    assert writer.getvalue() == expected_bytes

def test_write_float_le_zero():
    writer = io.BytesIO()
    value = 0.0
    write_float_le(value, writer)
    expected_bytes = struct.pack("<f", value)
    assert writer.getvalue() == expected_bytes

# Tests for write_pascal_string
def test_write_pascal_string_simple():
    writer = io.BytesIO()
    string_data = b"hello"
    write_pascal_string(string_data, writer)
    expected_length_bytes = len(string_data).to_bytes(4, 'little', signed=False)
    assert writer.getvalue() == expected_length_bytes + string_data

def test_write_pascal_string_empty():
    writer = io.BytesIO()
    string_data = b""
    write_pascal_string(string_data, writer)
    expected_length_bytes = len(string_data).to_bytes(4, 'little', signed=False)
    assert writer.getvalue() == expected_length_bytes + string_data

# Tests for write_unicode_string
def test_write_unicode_string_simple():
    writer = io.BytesIO()
    unicode_string = "world"
    write_unicode_string(unicode_string, writer)
    encoded_string = unicode_string.encode('utf-8')
    expected_length_bytes = len(encoded_string).to_bytes(4, 'little', signed=False)
    assert writer.getvalue() == expected_length_bytes + encoded_string

def test_write_unicode_string_non_ascii():
    writer = io.BytesIO()
    unicode_string = "Äpfel"
    write_unicode_string(unicode_string, writer)
    encoded_string = unicode_string.encode('utf-8')
    expected_length_bytes = len(encoded_string).to_bytes(4, 'little', signed=False)
    assert writer.getvalue() == expected_length_bytes + encoded_string

def test_write_unicode_string_empty():
    writer = io.BytesIO()
    unicode_string = ""
    write_unicode_string(unicode_string, writer)
    encoded_string = unicode_string.encode('utf-8')
    expected_length_bytes = len(encoded_string).to_bytes(4, 'little', signed=False)
    assert writer.getvalue() == expected_length_bytes + encoded_string
