ACCESSORS = "accessors"
ACCESSORS_MIN = "accessors-min"
ACCESSORS_MAX = "accessors-max"
ASSET = "asset"
ATTRIBUTES = "attributes"
BIN = "BIN"
BUFFER = "buffer"
BUFFER_VIEW = "bufferView"
BUFFER_VIEWS = "bufferViews"
BUFFERS = "buffers"
BYTE_LENGTH = "byteLength"
BYTE_OFFSET = "byteOffset"
COMPONENT_TYPE = "componentType"
COUNT = "count"
DATA = "data"
DATA_CB_BYTE = "data-cb-byte"
DATA_CB_BYTE_2 = "data-cb-byte-2"
GENERATOR = "generator"
INDICES = "indices"
JSON = "JSON"
MIN = "min"
MATERIAL = "material"
MATERIALS = "materials"
MAX = "max"
MESH = "mesh"
MESHES = "meshes"
NAME = "name"
NODES = "nodes"
PLANES = "planes"
PRIMITIVES = "primitives"
ROTATION = "rotation"
ROTATIONS = "rotations"
SCALE = "scale"
SCENE = "scene"
SCENES = "scenes"
TRANSLATION = "translation"
TYPE = "type"

ORDER_NODE = [MESH, ROTATION, SCALE, TRANSLATION]
ORDER_ACCESSOR = [BUFFER_VIEW, COMPONENT_TYPE, COUNT, MAX, MIN, TYPE]
ORDER_BUFFER_VIEW = [BUFFER, BYTE_LENGTH, BYTE_OFFSET]

MATERIAL_VALUE = [
    {
        "name": "black",
        "pbrMetallicRoughness": {
            "baseColorFactor": [0, 0, 0, 1],
            "roughnessFactor": 0.5
        }
    },
    {
        "name": "white",
        "pbrMetallicRoughness": {
            "baseColorFactor": [0.8, 0.8, 0.8, 1],
            "metallicFactor": 0.5,
            "roughnessFactor": 0.3
        }
    }
]
