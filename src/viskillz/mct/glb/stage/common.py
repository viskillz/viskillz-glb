import binascii
import struct
import textwrap
from typing import Callable

from viskillz.mct.glb.constants import *


def create_codebook(
        common_data: dict,
        count: int,
        vec_wrap: list[int],
        vec_fill: list[int],
        slices_function: Callable[[dict, str, str], list[str]]) -> list[list[str]]:

    values = [set() for _ in range(count)]
    data = common_data[DATA]
    for shape_id in data:
        for scale_id in data[shape_id]:
            slices = slices_function(common_data, shape_id, scale_id)
            for i in range(len(values)):
                for part in textwrap.wrap(slices[i], vec_wrap[i]):
                    values[i].add(part)

    dictionaries = [dict() for _ in range(len(values))]
    values = [list(sorted(list(value))) for value in values]
    for i in range(len(values)):
        for j in range(len(values[i])):
            dictionaries[i][values[i][j]] = hex(j)[2:].zfill(vec_fill[i])

    for shape_id in data:
        for scale_id in data[shape_id]:
            slices = slices_function(common_data, shape_id, scale_id)
            data[shape_id][scale_id] = [
                "".join([dictionaries[i][part] for part in textwrap.wrap(slices[i], vec_wrap[i])])
                if i < len(vec_wrap)
                else slices[i] for i in range(len(slices))]

    return values


def decode_codebook(binary: bytearray, magic: list[int], offset: int) -> tuple[list[list[str]], int]:
    result = []
    for i in range(len(magic)):
        length = struct.unpack_from("H", binary, offset)[0]
        offset += 2

        result.append([])

        for _ in range(length):
            result[i].append(
                binascii.hexlify(binary[offset:offset + magic[i]]).decode("ascii")
            )
            offset += magic[i]

    return result, offset
