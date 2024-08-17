import os
import sys
from pathlib import Path

import minecraftmap
from dotenv import load_dotenv

load_dotenv()

WORLD = Path(os.getenv("WORLD_DIRECTORY") + "/data")

if not WORLD.is_dir():
    print("Invalid World Path")
    sys.exit()


def main():
    world_files = list(WORLD.glob(pattern="**/map_*.dat"))
    if len(world_files) == 0:
        print("There were no map files.")
        return
    print(f"Found {len(world_files)} map files.")
    Path.mkdir(Path("./maps"), exist_ok=True, parents=True)
    Path("./maps/ALL-FAILED.txt").unlink(missing_ok=True)
    for map_file in world_files:
        print(os.path.basename(map_file))
        map_id = int(os.path.basename(map_file).split("_")[1].split(".")[0])
        try:
            m = minecraftmap.Map(map_file, eco=False)
            m.saveimagepng("./maps/" + os.path.basename(map_file).replace('.dat','') + ".png")
        except IndexError:
            print(f"\tFAILED - /give @s minecraft:filled_map{{map:{map_id}}}")
            with open("./maps/ALL-FAILED.txt", "a") as f:
                f.write(f"/give @s minecraft:filled_map{{map:{map_id}}}\n")


if __name__ == "__main__":
    main()
