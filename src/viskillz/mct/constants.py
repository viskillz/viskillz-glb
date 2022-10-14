GROUP_IDS = [f"Classic.{str(i).zfill(2)}" for i in range(1, 26) if i not in {2, 4, 8, 25}]
PLANE_IDS = [str(i).zfill(2) for i in range(1, 32)]
SCALE_IDS = ["000", "001", "010", "100", "011", "101", "110"]
ROTATION_VECTORS = [
    [0, 0, 0], [0, 0, 90], [0, 0, 180], [0, 0, 270], [0, 90, 0], [0, 90, 90],
    [0, 90, 180], [0, 90, 270], [0, 180, 0], [0, 180, 90], [0, 180, 180], [0, 180, 270],
    [0, 270, 0], [0, 270, 90], [0, 270, 180], [0, 270, 270], [90, 0, 0], [90, 0, 90],
    [90, 0, 180], [90, 0, 270], [90, 180, 0], [90, 180, 90], [90, 180, 180], [90, 180, 270]
]
ROTATION_IDS = [f"{rotation[0] // 90}{rotation[1] // 90}{rotation[2] // 90}" for rotation in ROTATION_VECTORS]
SHAPE_COUNTS = [10, 10, 8, 8, 10, 10, 10, 11, 10, 8, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
SHAPE_IDS = {GROUP_IDS[i]: [f"{GROUP_IDS[i]}{str(j).zfill(2)}"
                            for j in range(SHAPE_COUNTS[i])] for i in range(len(GROUP_IDS))}

