import textwrap

from viskillz.mct.glb.stage.common import create_codebook
from viskillz.mct.glb.constants import *


def encode(common_data: dict) -> dict:
    buffer_count = common_data[DATA][list(common_data[DATA].keys())[0]]
    buffer_count = len(buffer_count[list(buffer_count.keys())[0]])

    vec_wrap = [6, 12, 4] if buffer_count == 4 else [6, 12]
    vec_fill = [4, 4, 2] if buffer_count == 4 else [4, 4]

    common_data[DATA_CB_BYTE_2] = create_codebook(
        common_data, buffer_count - 1, vec_wrap, vec_fill, lambda d, sh, sc: d[DATA][sh][sc]
    )

    return common_data


def decode(root: dict) -> dict:
    assert DATA_CB_BYTE_2 in root

    magic = [4, 4, 2, 4] if len(root[DATA_CB_BYTE]) == 4 else [4, 4, 4]

    data = root[DATA]
    for shape_id in data:
        for scale_id in data[shape_id]:
            for i in range(len(magic) - 1):
                codebook = root[DATA_CB_BYTE_2][i]
                data[shape_id][scale_id][i] = "".join(
                    [codebook[int(val, base=16)] for val in textwrap.wrap(data[shape_id][scale_id][i], magic[i])]
                )

    del root[DATA_CB_BYTE_2]
    return root
