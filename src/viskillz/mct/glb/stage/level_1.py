import binascii
import os
from copy import deepcopy
from os.path import join as os_path_join

from viskillz.common.file import init_dir
from viskillz.common.log import StageLogger
from viskillz.mct.constants import *
from viskillz.mct.glb.constants import *
from viskillz.mct.glb.model import GLB

PREFIX = "Classic"


def encode(
        path_input: str,
        shape_count: int = 10):

    data = {
        ACCESSORS: dict(),
        ACCESSORS_MIN: dict(),
        ACCESSORS_MAX: dict(),
        DATA: dict()
    }

    for full_shape_id in SHAPE_IDS[os.path.split(path_input)[-1]]:
        shape_id = full_shape_id.split(".")[-1]
        for result in [data[ACCESSORS], data[DATA]]:
            result[shape_id] = dict()

        for scale_id in SCALE_IDS:
            file_name = f"{full_shape_id}.{scale_id}.000.01.glb"
            gltf = GLB(os.path.join(path_input, file_name)) \
                .remove_meta()

            accessor_count = len(gltf.doc[ACCESSORS])

            if scale_id == "000":
                data[ACCESSORS_MIN][shape_id] = gltf.doc[ACCESSORS][accessor_count // 2][MIN]
                data[ACCESSORS_MAX][shape_id] = gltf.doc[ACCESSORS][accessor_count // 2][MAX]

            data[ACCESSORS][shape_id][scale_id] = [
                accessor[COUNT] for accessor in gltf.doc[ACCESSORS][accessor_count // 2:]
            ]
            data[DATA][shape_id][scale_id] = binascii.hexlify(gltf.data[1984 if accessor_count == 8 else 1536:]) \
                .decode("ascii")

    return data


def decode(
        group_id: str,
        group_data: dict,
        common_data: dict,
        path_out: str,
        indent: int = 0) -> dict:

    # create directory for group
    path_out_full = os_path_join(path_out, group_id)
    init_dir(path_out_full)

    logger = StageLogger(lambda x: x, indent)

    has_textures = len(common_data[BUFFER_VIEWS]) == 4
    buffer_count = 4 if has_textures else 3

    skeleton = {
        ASSET: common_data[ASSET],
        SCENE: common_data[SCENE],
        SCENES: common_data[SCENES],
        NODES: [],
        MATERIALS: common_data[MATERIALS],
        MESHES: common_data[MESHES]
    }

    for shape_id in group_data[ACCESSORS]:
        logger.start(shape_id)
        for scale_id in group_data[ACCESSORS][shape_id]:
            for plane_id in PLANE_IDS:
                for rotation_id in ROTATION_IDS:
                    doc = deepcopy(skeleton)

                    # plane data
                    plane_data = deepcopy(common_data[PLANES][plane_id])
                    plane_data[MESH] = 0
                    doc[NODES].append(dict(sorted(plane_data.items(), key=lambda x: ORDER_NODE.index(x[0]))))

                    # rotation data
                    shape_data = deepcopy(deepcopy(common_data[ROTATIONS][rotation_id]))
                    shape_data[MESH] = 1
                    doc[NODES].append(dict(sorted(shape_data.items(), key=lambda x: ORDER_NODE.index(x[0]))))

                    # accessors
                    base_plane_ids = [1, 10, 16, 20]
                    base_plane_id = str(max([v for v in base_plane_ids if v <= int(plane_id)])).zfill(2)
                    doc[ACCESSORS] = deepcopy(common_data[ACCESSORS][base_plane_id])

                    for i in range(buffer_count):
                        doc[ACCESSORS][i + buffer_count][COUNT] = group_data[ACCESSORS][shape_id][scale_id][i]

                    for key in [MIN, MAX]:
                        doc[ACCESSORS][buffer_count][key] = []
                        for i in range(3):
                            if scale_id[[0, 2, 1][i]] == "1":
                                doc[ACCESSORS][buffer_count][key].append(
                                    group_data[f"accessors-{key}"][shape_id][i] * 0.7)
                            else:
                                doc[ACCESSORS][buffer_count][key].append(group_data[f"accessors-{key}"][shape_id][i])

                    for i in range(buffer_count * 2):
                        doc[ACCESSORS][i][BUFFER_VIEW] = i
                        doc[ACCESSORS][i] = dict(sorted(
                            doc[ACCESSORS][i].items(),
                            key=lambda x: ORDER_ACCESSOR.index(x[0])
                        ))

                    magic_1, magic_2 = ([3, 3, 2, 1], [4, 4, 4, 2]) if has_textures else ([3, 3, 1], [4, 4, 2])

                    # buffers
                    doc[BUFFER_VIEWS] = []
                    offset = 0
                    for i in range(buffer_count * 2):
                        byte_length = common_data[BUFFER_VIEWS][i] \
                            if i < buffer_count \
                            else doc[ACCESSORS][i][COUNT] * magic_1[i - buffer_count] * magic_2[i - buffer_count]
                        doc[BUFFER_VIEWS].append({
                            BUFFER: 0,
                            BYTE_LENGTH: byte_length,
                            BYTE_OFFSET: offset
                        })
                        offset += byte_length

                    doc[BUFFERS] = [{
                        BYTE_LENGTH: sum([buffer[BYTE_LENGTH] for buffer in doc[BUFFER_VIEWS]])
                    }]

                    # data chunk
                    binary = common_data[DATA][base_plane_id] + group_data[DATA][shape_id][scale_id]

                    # serialize
                    glb = GLB.of(doc, binary)
                    glb.write(os_path_join(
                        path_out_full,
                        f"{PREFIX}.{shape_id}.{scale_id}.{rotation_id}.{plane_id}.glb"
                    ))
    return logger.finish()
