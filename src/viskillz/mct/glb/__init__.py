import json
import os.path
import sys
from datetime import datetime

from viskillz.common.file import init_dir, list_files
from viskillz.common.log import StageLogger
from wakepy import keepawake

from viskillz.mct.glb.constants import *
from viskillz.mct.glb.model import GLB
from viskillz.mct.glb.stage import level_4, level_3, level_2, level_1
from viskillz.mct.glb.stage.level_0 import create_common

DIST = "dist"
GROUPS = "groups"
SRC = "src"
TYPE = "type"


def decode(path_input: str, path_output: str, group_id: str, level: int, indent: int = 0) -> dict:
    with open(os.path.join(path_input, "global.json")) as file:
        common_data = json.load(file)

    if level == 4:
        with open(os.path.join(path_input, f"{group_id}.bin"), "rb") as file:
            group_data = level_4.decode(group_id, bytearray(file.read()), len(common_data[BUFFER_VIEWS]) == 4)
        level -= 1
    else:
        with open(os.path.join(path_input, f"{group_id}.json")) as file:
            group_data = json.load(file)

    # TODO array like the encode
    if level == 3:
        group_data = level_3.decode(group_data)
        level -= 1
    if level == 2:
        group_data = level_2.decode(group_data)
        level -= 1

    return level_1.decode(group_id, group_data, common_data, path_output, indent)


def encode(path_input: str, path_output: str, group_id: str, level: int) -> dict:
    log = StageLogger(lambda x: x)

    shape_count = 8 if group_id[-2:] in {"05", "06", "13"} else 11 if group_id[-2:] in {"11"} else 10

    stages = [None, level_2, level_3, level_4]

    log.start("level-1")
    data = level_1.encode(os.path.join(path_input, group_id), shape_count)

    for i in range(1, level):
        log.start(f"level-{i + 1}")
        data = stages[i].encode(data)

    log = log.finish()
    if level == 4:
        with open(os.path.join(path_output, f"{group_id}.bin"), "wb") as file:
            file.write(data)
    else:
        with open(os.path.join(path_output, f"{group_id}.json"), "w") as file:
            json.dump(
                data,
                file, ensure_ascii=True, sort_keys=True, separators=(',', ':')
            )

    return log


def texture(path_input: str, path_output: str, indent: int = 0) -> dict[dict[str, float]]:
    log = StageLogger(lambda x: x.split(".")[1], indent)
    for file_name in list_files(path_input, "glb"):
        log.start(file_name)
        GLB(os.path.join(path_input, file_name)) \
            .remove_textures() \
            .write(os.path.join(path_output, file_name))
    return log.finish()


def material(path_input: str, path_output: str, indent: int = 0) -> dict[dict[str, float]]:
    log = StageLogger(lambda x: x.split(".")[1], indent)
    for file_name in list_files(path_input, "glb"):
        log.start(file_name)
        gltf = GLB(os.path.join(path_input, file_name))
        gltf.doc[MATERIALS] = MATERIAL_VALUE
        gltf.doc[MESHES][1][PRIMITIVES][0][MATERIAL] = 1
        gltf.write(os.path.join(path_output, file_name))
    return log.finish()


def clean(path_input: str, path_output: str, indent: int = 0) -> dict[dict[str, float]]:
    log = StageLogger(lambda x: x.split(".")[1], indent)
    for file_name in list_files(path_input, "glb"):
        log.start(file_name)
        GLB(os.path.join(path_input, file_name)) \
            .remove_meta() \
            .write(os.path.join(path_output, file_name))
    return log.finish()


def validate(path_left: str, path_right: str, group_id: int, epsilon: float, indent: int = 0) -> dict[dict[str, float]]:
    file_names = [list_files(rf"{folder}\Classic.{str(group_id).zfill(2)}", "glb", True) for folder in
                  [path_left, path_right]]

    log = StageLogger(lambda x: os.path.split(x)[-1].split(".")[1], indent)
    for i in range(len(file_names[0])):
        log.start(file_names[0][i])

        assets = GLB(file_names[0][i]), GLB(file_names[1][i])
        GLB.equal(assets[0], assets[1], epsilon)

    return log.finish()


def main() -> None:
    with open(sys.argv[1]) as file:
        conf = json.load(file)

    path_base = conf["working-directory"]
    stage_id = 0
    global_log = {}

    start_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    name_dir = os.path.dirname(sys.argv[1])
    name_conf = os.path.split(sys.argv[1])[-1].split(".")[0]

    for act_stage in conf["goals"]:
        print(f"#{stage_id} / {len(conf['goals'])}", act_stage[TYPE])
        if act_stage[TYPE] in {"material", "clean", "texture"}:
            function = {
                "material": material,
                "clean": clean,
                "texture": texture
            }[act_stage[TYPE]]

            global_log[f"{str(stage_id).zfill(2)}-{act_stage[TYPE]}"] = dict()
            for group_id in act_stage[GROUPS]:
                formatted_group_id = f"Classic.{str(group_id).zfill(2)}"
                print("-", formatted_group_id)
                path_input = os.path.join(path_base, act_stage[SRC], formatted_group_id)
                path_output = os.path.join(path_base, act_stage[DIST], formatted_group_id)
                init_dir(path_output)
                global_log[f"{str(stage_id).zfill(2)}-{act_stage[TYPE]}"][group_id] = function(
                    path_input,
                    path_output,
                    indent=1
                )

        if act_stage[TYPE] == "encode":
            path_input = os.path.join(path_base, act_stage[SRC])
            path_output = os.path.join(path_base, act_stage[DIST])
            init_dir(path_output)

            global_log[f"{str(stage_id).zfill(2)}-{act_stage[TYPE]}"] = dict()

            formatted_group_id = f"Classic.{str(act_stage[GROUPS][0]).zfill(2)}"
            log = StageLogger(lambda x: x)
            log.start("global")
            common = create_common(path_input, formatted_group_id)
            global_log[f"{str(stage_id).zfill(2)}-{act_stage[TYPE]}"]["global"] = log.finish()["global"]
            with open(os.path.join(path_output, "global.json"), "w") as file:
                json.dump(
                    common,
                    file,
                    ensure_ascii=True, separators=(',', ':'))

            for group_id in act_stage[GROUPS]:
                formatted_group_id = f"Classic.{str(group_id).zfill(2)}"
                print("-", formatted_group_id)
                global_log[f"{str(stage_id).zfill(2)}-{act_stage[TYPE]}"][group_id] = encode(
                    os.path.join(path_base, act_stage[SRC]),
                    os.path.join(path_base, act_stage[DIST]),
                    formatted_group_id,
                    act_stage["level"]
                )
        if act_stage[TYPE] == "decode":
            global_log[f"{str(stage_id).zfill(2)}-{act_stage['type']}"] = dict()
            for group_id in act_stage[GROUPS]:
                formatted_group_id = f"Classic.{str(group_id).zfill(2)}"
                path_input = os.path.join(path_base, act_stage[SRC])
                path_output = os.path.join(path_base, act_stage[DIST])
                print("-", formatted_group_id)
                global_log[f"{str(stage_id).zfill(2)}-{act_stage[TYPE]}"][group_id] = decode(
                    path_input,
                    path_output,
                    formatted_group_id,
                    act_stage["level"],
                    indent=1
                )
        if act_stage[TYPE] == "validate":
            global_log[f"{str(stage_id).zfill(2)}-{act_stage[TYPE]}"] = dict()
            for group_id in act_stage[GROUPS]:
                formatted_group_id = f"Classic.{str(group_id).zfill(2)}"
                print("-", formatted_group_id)
                global_log[f"{str(stage_id).zfill(2)}-{act_stage[TYPE]}"][group_id] = validate(
                    os.path.join(path_base, act_stage[SRC]),
                    os.path.join(path_base, act_stage[DIST]),
                    group_id,
                    act_stage["epsilon"],
                    indent=1
                )
        stage_id += 1

        with open(os.path.join(name_dir, f"log-{name_conf}-{start_time}.json"), "w") as file:
            json.dump(global_log, file, indent=2)


def run() -> None:
    with keepawake(keep_screen_awake=True):
        main()
