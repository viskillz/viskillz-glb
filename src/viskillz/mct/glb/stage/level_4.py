import binascii
import struct
from typing import Union

from viskillz.mct.glb.stage.common import decode_codebook
from viskillz.mct.constants import *
from viskillz.mct.glb.constants import *


def encode(data: dict) -> bytearray:
    binary = []
    buffer_count = len(data[DATA_CB_BYTE_2])

    # shape count (1 unsigned byte)
    binary += struct.pack("B", len(data[ACCESSORS_MIN]))

    # accessor min/max values (IEEE 754)
    for key in [ACCESSORS_MIN, ACCESSORS_MAX]:
        for shape_id in data[key]:
            for value in data[key][shape_id]:
                binary += list(struct.pack("f", float(value)))

    # data
    for shape_id in data[DATA]:
        for scale_id in SCALE_IDS:
            for sequence in data[DATA][shape_id][scale_id]:
                assert len(sequence) % 2 == 0
                binary += list(struct.pack("H", len(sequence) // 2))
                binary += binascii.unhexlify(sequence)

    for buffer in data[DATA_CB_BYTE]:
        binary += list(struct.pack("H", len(buffer)))
        for entry in buffer:
            binary += binascii.unhexlify(entry)

    for i in range(buffer_count):
        buffer = data[DATA_CB_BYTE_2][i]
        binary += list(struct.pack("H", len(buffer)))
        for entry in buffer:
            assert len(entry) % 2 == 0
            binary += binascii.unhexlify(entry)

    return bytearray(binary)


def decode(group_id, binary, has_textures: bool):
    magic_1 = [4, 4, 4, 2] if has_textures else [4, 4, 2]
    magic_2 = [3, 6, 2] if has_textures else [3, 6]

    offset = 0

    count_of_shapes = struct.unpack_from("B", binary, offset)[0]
    offset += 1

    shape_ids = [f"{group_id[-2:]}{str(i).zfill(2)}" for i in range(count_of_shapes)]

    data = dict()

    def convert_if_int(value: float) -> Union[float, int]:
        return int(value) if value in {-1.0, 0.0, 1.0} else value

    # accessor min/max values (IEEE 754)
    for key in [ACCESSORS_MIN, ACCESSORS_MAX]:
        data[key] = dict()
        for shape_id in shape_ids:
            data[key][shape_id] = [convert_if_int(v) for v in struct.unpack_from("3f", binary, offset)]
            offset += 12

    # data
    data[DATA] = dict()
    for shape_id in shape_ids:
        data[DATA][shape_id] = dict()
        for scale_id in SCALE_IDS:
            data[DATA][shape_id][scale_id] = []
            for i in range(len(magic_1)):
                length = struct.unpack_from("H", binary, offset)[0]
                offset += 2
                data[DATA][shape_id][scale_id].append(
                    binascii.hexlify(binary[offset:offset + length]).decode("ascii")
                )
                offset += length

    res, offset = decode_codebook(binary, magic_1, offset)
    data[DATA_CB_BYTE] = res
    res, offset = decode_codebook(binary, magic_2, offset)
    data[DATA_CB_BYTE_2] = res

    return data
