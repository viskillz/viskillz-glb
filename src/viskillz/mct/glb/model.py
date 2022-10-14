from __future__ import annotations

import json
import os
import struct
from dataclasses import dataclass
from typing import Union

from viskillz.mct.glb.constants import *


@dataclass
class GLB:
    """
    A class that represents and manipulates GLB assets.
    """
    doc: dict
    data: bytearray

    magic: str = "glTF"
    version: int = 2

    @staticmethod
    def of(doc: dict[str, any], data: str) -> GLB:
        """
        Creates an instance with the given JSON and BIN chunks.
        :param doc: the dictionary of the JSON chunk
        :param data: the hex value of the data chunk
        :return: the document
        """
        file = GLB()
        file.doc = doc
        file.data = bytearray.fromhex(data)
        return file

    def __init__(self: GLB, path: str = None) -> None:
        if path:
            with open(os.path.join(path), "rb") as file:
                data = bytearray(file.read())

            def bytes_to_int(value: bytearray, offset: int = 0) -> int:
                return struct.unpack_from("H", value, offset)[0]

            def bytes_to_str(value: bytearray, offset: int = 0, count: int = 1) -> str:
                return struct.unpack_from(f"{count}s", value, offset)[0].decode(encoding="ascii")

            self.magic = bytes_to_str(data, 0, 4)
            self.version = bytes_to_int(data, 4)
            self.length = bytes_to_int(data, 8)

            act = 12
            # read json chunk
            json_length = bytes_to_int(data, act)
            act += 8  # JSON
            self.doc = json.loads(bytes_to_str(data, act, json_length))
            act += json_length

            act += (4 - (act % 4)) % 4

            # read binary chunk
            binary_length = bytes_to_int(data, act)
            act += 8
            self.data = data[act:act + binary_length]
            act += binary_length

    def remove_meta(self: GLB) -> GLB:
        """
        Removes unnecessary metadata.
        :return: self
        """
        if GENERATOR in self.doc[ASSET]:
            del self.doc[ASSET][GENERATOR]
        for prop_name in [SCENES, NODES, MATERIALS, MESHES]:
            for element in self.doc[prop_name]:
                if NAME in element:
                    del element[NAME]
        return self

    def remove_textures(self: GLB) -> GLB:
        assert "TEXCOORD_0" in self.doc[MESHES][0][PRIMITIVES][0][ATTRIBUTES], "No texture to remove"

        buffer_views = self.doc[BUFFER_VIEWS]

        self.data = \
            self.data[:buffer_views[2][BYTE_OFFSET]] + \
            self.data[buffer_views[3][BYTE_OFFSET]:buffer_views[6][BYTE_OFFSET]] + \
            self.data[buffer_views[7][BYTE_OFFSET]:]

        # modify meshes
        del self.doc[MESHES][0][PRIMITIVES][0][ATTRIBUTES]["TEXCOORD_0"]
        del self.doc[MESHES][1][PRIMITIVES][0][ATTRIBUTES]["TEXCOORD_0"]
        self.doc[MESHES][0][PRIMITIVES][0][INDICES] -= 1

        self.doc[MESHES][1][PRIMITIVES][0][INDICES] -= 2
        self.doc[MESHES][1][PRIMITIVES][0][ATTRIBUTES]["POSITION"] -= 1
        self.doc[MESHES][1][PRIMITIVES][0][ATTRIBUTES]["NORMAL"] -= 1

        # modify bufferViews and buffers
        length_2 = self.doc[BUFFER_VIEWS][2][BYTE_LENGTH]
        length_6 = self.doc[BUFFER_VIEWS][6][BYTE_LENGTH]

        for i in [3, 4, 5, 7]:
            self.doc[ACCESSORS][i][BUFFER_VIEW] -= 1
            self.doc[BUFFER_VIEWS][i][BYTE_OFFSET] -= length_2

        self.doc[ACCESSORS][7][BUFFER_VIEW] -= 1
        self.doc[BUFFER_VIEWS][7][BYTE_OFFSET] -= length_6

        for index in [6, 2]:
            del self.doc[ACCESSORS][index]
            del self.doc[BUFFER_VIEWS][index]

        self.doc[BUFFERS][0][BYTE_LENGTH] -= length_2 + length_6

        return self

    @staticmethod
    def __get_slices_full(value: bytearray, accessors: list[int]) -> list[bytearray]:
        accessors = [
            0,
            accessors[0] * 3 * 4,
            accessors[1] * 3 * 4,
            accessors[2] * 2 * 4,
            accessors[3] * 2,
            accessors[4] * 3 * 4,
            accessors[5] * 3 * 4,
            accessors[6] * 2 * 4,
            accessors[7] * 2
        ] if len(accessors) == 8 \
            else [
            0,
            accessors[0] * 3 * 4,
            accessors[1] * 3 * 4,
            accessors[2] * 2,
            accessors[3] * 3 * 4,
            accessors[4] * 3 * 4,
            accessors[5] * 2
        ]

        for i in range(1, len(accessors)):
            accessors[i] += accessors[i - 1]

        return [value[accessors[i]:accessors[i + 1]] for i in range(len(accessors) - 1)]

    @staticmethod
    def equal(left: GLB, right: GLB, epsilon: float) -> bool:
        def check_types(
                left_value: Union[int, float, str, dict, list],
                right_value: Union[int, float, str, dict, list]) -> bool:
            value_type = type(left_value)
            assert value_type == type(right_value), (value_type, right_value)
            if value_type == float:
                assert abs(left_value - right_value) <= epsilon, (
                    abs(left_value - right_value), left_value, right_value)
            elif value_type in {int, str}:
                assert left_value == right_value
            elif value_type == dict:
                assert left_value.keys() == right_value.keys(), "\n".join(
                    [str(left_value.keys()), str(right_value.keys())])
                for k in left_value.keys():
                    check_types(left_value[k], right_value[k])
            elif value_type == list:
                assert len(left_value) == len(right_value)
                for i in range(len(left_value)):
                    assert check_types(left_value[i], right_value[i])
            return True

        assert check_types(left.doc, right.doc)

        accessor_counts = [a[COUNT] for a in left.doc[ACCESSORS]]
        slices_left = left.__get_slices_full(left.data, accessor_counts)
        slices_right = right.__get_slices_full(right.data, accessor_counts)

        def check_slices(slice_indices: list[int], value_type: type) -> bool:
            length = 4 if value_type == float else 2
            type_format = "f" if value_type == float else "H"

            for slice_index in slice_indices:
                for offset in range(0, len(slices_left[slice_index]), length):
                    value_left = struct.unpack(type_format, bytes(slices_left[0][offset:offset + length]))[0]
                    value_right = struct.unpack(type_format, bytes(slices_right[0][offset:offset + length]))[0]
                    if value_type == float:
                        assert (abs(value_left - value_right) <= epsilon, abs(value_left - value_right)) \
                            if value_type == float \
                            else value_left == value_right
                return True

        assert check_slices([0, 1, 3, 4] if len(accessor_counts) == 6 else [0, 1, 2, 4, 5, 6], float)
        assert check_slices([2] if len(accessor_counts) == 6 else [3, 7], int)
        return True

    def __to_bytes(self) -> bytearray:
        def int_to_bytes(value: int) -> bytearray:
            return bytearray(value.to_bytes(4, byteorder="little"))

        def str_to_bytes(value: str) -> bytearray:
            return bytearray(value, encoding="ascii")

        def padding(value: bytearray, extra: int) -> bytearray:
            return bytearray([extra for _ in range((4 - (len(value) % 4)) % 4)])

        data = str_to_bytes(self.magic)
        data += int_to_bytes(self.version)
        data += int_to_bytes(0)

        json_chars = str_to_bytes(json.dumps(self.doc, ensure_ascii=True, separators=(',', ':')))
        json_chars += padding(json_chars, 32)

        data += int_to_bytes(len(json_chars))
        data += str_to_bytes(JSON)
        data += json_chars

        data += int_to_bytes(len(self.data))
        data += str_to_bytes(BIN) + bytearray([0])
        data += self.data
        data += padding(data, 0)
        data[8:12] = int_to_bytes(len(data))

        return data

    def write(self: GLB, file_name: str) -> None:
        """
        Writes the asset to the given file.
        :param file_name:  the name of the file
        :return: nothing
        """
        with open(file_name, "wb") as file:
            file.write(self.__to_bytes())
