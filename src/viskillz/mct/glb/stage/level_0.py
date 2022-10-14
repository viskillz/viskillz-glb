import binascii
import os

from viskillz.mct.constants import *
from viskillz.mct.glb.constants import *
from viskillz.mct.glb.model import GLB


def create_common(path_input: str, group_id: str) -> dict:
    result = {
        PLANES: dict(),
        ROTATIONS: dict(),
        DATA: dict(),
        ACCESSORS: dict()
    }

    shape_id = f"{group_id}00"
    path_input = os.path.join(path_input, shape_id[:-2])

    for plane_id in PLANE_IDS:
        gltf = GLB(os.path.join(path_input, f"{shape_id}.000.000.{plane_id}.glb")) \
            .remove_meta()

        # store plane data
        result[PLANES][plane_id] = gltf.doc[NODES][0]
        del result[PLANES][plane_id][MESH]

        accessor_count = len(gltf.doc[ACCESSORS])

        # collect binary data and accessors of each unique plane
        if plane_id in {"01", "10", "16", "20"}:
            result[DATA][plane_id] = binascii.hexlify(gltf.data[:1984 if accessor_count == 8 else 1536]) \
                .decode("ascii")

            result[ACCESSORS][plane_id] = gltf.doc[ACCESSORS]
            for accessor in result[ACCESSORS][plane_id]:
                del accessor[BUFFER_VIEW]
            for i in range(accessor_count // 2, accessor_count):
                del result[ACCESSORS][plane_id][i][COUNT]
                if i == accessor_count // 2:
                    del result[ACCESSORS][plane_id][i][MIN]
                    del result[ACCESSORS][plane_id][i][MAX]

        # collect identical attributes from the first asset
        if plane_id == "01":
            for key in [ASSET, SCENE, SCENES, MATERIALS, MESHES]:
                result[key] = gltf.doc[key]
            result[BUFFER_VIEWS] = [view[BYTE_LENGTH] for view in gltf.doc[BUFFER_VIEWS][:accessor_count // 2]]

    # store rotation data
    for rotation_id in ROTATION_IDS:
        gltf = GLB(os.path.join(path_input, f"{shape_id}.000.{rotation_id}.01.glb"))
        gltf.remove_meta()

        result[ROTATIONS][rotation_id] = gltf.doc[NODES][1]
        del result[ROTATIONS][rotation_id][MESH]

    return result
