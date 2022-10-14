import textwrap

from viskillz.mct.glb.stage.common import create_codebook
from viskillz.mct.glb.constants import *


def encode(common_data: dict) -> dict:
    buffer_count = common_data[ACCESSORS][list(common_data[ACCESSORS].keys())[0]]
    buffer_count = len(buffer_count[list(buffer_count.keys())[0]])

    vec_wrap, vec_fill = ([8, 8, 8, 4], [2, 4, 2, 2]) \
        if buffer_count == 4 \
        else ([8, 8, 4], [2, 4, 2])

    def value_to_slices(value, accessors):
        accessors = [
            0,
            accessors[0] * 3 * 4 * 2,
            accessors[1] * 3 * 4 * 2,
            accessors[2] * 2 * 4 * 2,
            accessors[3] * 2 * 2
        ] if len(accessors) == 4 \
            else [
            0,
            accessors[0] * 3 * 4 * 2,
            accessors[1] * 3 * 4 * 2,
            accessors[2] * 2 * 2
        ]

        for i in range(1, len(accessors)):
            accessors[i] += accessors[i - 1]

        return [value[accessors[i]:accessors[i + 1]] for i in range(len(accessors) - 1)]

    common_data[DATA_CB_BYTE] = create_codebook(common_data, buffer_count, vec_wrap, vec_fill,
                                                lambda data, shape_id, scale_id: value_to_slices(
                                                    data[DATA][shape_id][scale_id],
                                                    data[ACCESSORS][shape_id][scale_id]
                                                ))

    del common_data[ACCESSORS]

    return common_data


def decode(common_data: dict) -> dict:
    assert DATA_CB_BYTE in common_data and DATA_CB_BYTE_2 not in common_data

    magic, accessor_divisors = ([2, 4, 2, 2], [12, 12, 8, 2]) \
        if len(common_data[DATA_CB_BYTE]) == 4 \
        else ([2, 4, 2], [12, 12, 2])

    data = common_data[DATA]
    common_data[ACCESSORS] = dict()

    for shape_id in data:
        common_data[ACCESSORS][shape_id] = dict()
        for scale_id in data[shape_id]:
            common_data[ACCESSORS][shape_id][scale_id] = []
            for i in range(len(magic)):
                cookbook = common_data[DATA_CB_BYTE][i]
                data[shape_id][scale_id][i] = "".join(
                    [cookbook[int(val, base=16)] for val in textwrap.wrap(data[shape_id][scale_id][i], magic[i])]
                )
                common_data[ACCESSORS][shape_id][scale_id].append(
                    len(data[shape_id][scale_id][i]) // 2 // accessor_divisors[i]
                )
            data[shape_id][scale_id] = "".join(data[shape_id][scale_id])

    del common_data[DATA_CB_BYTE]
    return common_data
