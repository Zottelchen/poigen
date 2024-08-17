import concurrent.futures
import json
import os
import sys
import traceback
from argparse import ArgumentParser
from pathlib import Path

from dotenv import load_dotenv
from nbt import region

from poigen.POIDB import POIDB

load_dotenv()


def process_dimension(name, path, args, RENDER):
    print(f"Dimension {name}: {path}")
    markers = POIDB(f"{name}")

    if args.skip_entities:
        print(f"[{name}] Skipping entities.")
    else:
        handle_entities(markers, path)

    if args.skip_tile_entities:
        print(f"[{name}]Skipping tile entities.")
    else:
        handle_tile_entities(markers, path)

    if args.skip_hardcoded:
        print(f"[{name}] Skipping hardcoded entities.")
    else:
        handle_hardcoded_entities(markers, RENDER)

    if len(markers.entities) > 0:
        print(
            f"\n\n[{name}] The following entities were found:\n{markers.entities_overview}"
        )
        with open(Path(RENDER, f"{name}_found.txt"), "w") as output:
            output.write(markers.entities_overview)

    print(
        f"\n\n[{name}] The following entities were found but not have no filters designed for them:\n{markers.unmapped_overview}"
    )
    with open(Path(RENDER, f"{name}_unmapped.txt"), "w") as output:
        output.write(markers.unmapped_overview)

    print(f"\n[{name}] Writing Output.")
    markers.write_output(RENDER)
    print(f"[{name}] Done!")


def handle_entities(markers: POIDB, world_dir: Path):
    entity_files = list(world_dir.glob("entities/*.mca"))
    print(
        f"[{markers.world_name}] Starting with external entity files. Found {len(entity_files)} entity files."
    )
    if len(entity_files) == 0:
        print(f"[{markers.world_name}] There were no entity files.")
        return

    for entity_file in entity_files:
        region_file = region.RegionFile(entity_file.as_posix(), "rb")
        chunks = region_file.get_chunks()
        print(
            f"\t[{markers.world_name}] Found {len(chunks)} Chunks in Entityfile: {entity_file}"
        )
        if len(chunks) > 0:
            for chunk in chunks:
                chunk_nbt = region_file.get_nbt(chunk["x"], chunk["z"])
                if len(chunk_nbt["Entities"]) > 0:
                    print(
                        f"\t\t[{markers.world_name}] Found {len(chunk_nbt['Entities'])} Entities in Chunk {chunk['x']}, {chunk['z']}"
                    )
                    markers.add_entities_from_chunk(chunk_nbt["Entities"])


def handle_tile_entities(markers: POIDB, world_dir: Path):
    region_files = list(world_dir.glob("region/*.mca"))

    print(
        f"[{markers.world_name}] Starting with region files. Found {len(region_files)} region files."
    )
    if len(region_files) == 0:
        print(f"[{markers.world_name}] There were no region files.")
        return

    for rf in region_files:
        region_file = region.RegionFile(rf.as_posix(), "rb")
        chunks = region_file.get_chunks()
        print(
            f"\t[{markers.world_name}] Found {len(chunks)} Chunks in Regionfile: {rf}"
        )
        if len(chunks) > 0:
            for chunk in chunks:
                chunk_nbt = region_file.get_nbt(chunk["x"], chunk["z"])
                if "Level" in chunk_nbt and len(chunk_nbt["Level"]["TileEntities"]) > 0:
                    print(
                        f"\t\t[{markers.world_name}] Found {len(chunk_nbt['Level']['TileEntities'])} Entities in Chunk {chunk['x']}, {chunk['z']}"
                    )
                    markers.add_entities_from_chunk(chunk_nbt["Level"]["TileEntities"])


def handle_hardcoded_entities(markers: POIDB, RENDER):
    hardcode_file = Path(RENDER, f"hardcoded/{markers.world_name}.json")
    if not hardcode_file.is_file():
        print(f"[{markers.world_name}] No hardcoded file found at {hardcode_file}.")
        return

    with open(hardcode_file, "r") as f:
        hardcoded = json.load(f)

    markers.add_entities_from_json(hardcoded)


def main():
    parser = ArgumentParser(description="POIGen by Zottelchen")
    if os.getenv("WORLD_DIRECTORY") is None:
        parser.add_argument("world_directory", help="Directory of the Minecraft World")
    if os.getenv("RENDER_DIRECTORY") is None:
        parser.add_argument(
            "render_directory", help="Directory of the Overviewer Render"
        )
    parser.add_argument(
        "--skip_entities",
        help="Skips entities (from the entity directory) like horses, villagers, item frames, armor stands, etc.",
        type=bool,
    )
    parser.add_argument(
        "--skip_tile_entities",
        help="Skips tile entities (contained within world chunks) like chests, barrels, etc.",
        type=bool,
    )
    parser.add_argument(
        "--skip_hardcoded",
        help="Skips hardcoded entities like Towers and Towns",
        type=bool,
    )

    args = parser.parse_args()

    if os.getenv("WORLD_DIRECTORY") is None:
        WORLD = Path(args.world_directory)
    else:
        WORLD = Path(os.getenv("WORLD_DIRECTORY"))
    if os.getenv("RENDER_DIRECTORY") is None:
        RENDER = Path(args.render_directory)
    else:
        RENDER = Path(os.getenv("RENDER_DIRECTORY"))

    if not RENDER.is_dir() or not WORLD.is_dir():
        print("World or Render directory is not a folder path.")
        sys.exit(666)

    dimensions_path = WORLD / "dimensions/minecraft"
    dimensions = {}
    if dimensions_path.is_dir():
        dimensions = {
            dim.name.upper(): dim for dim in dimensions_path.iterdir() if dim.is_dir()
        }
    dimensions["OVERWORLD"] = WORLD
    if (WORLD / "DIM1").is_dir():
        dimensions["THE_END"] = WORLD / "DIM1"
    if (WORLD / "DIM-1").is_dir():
        dimensions["NETHER"] = WORLD / "DIM-1"

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_dimension, name, path, args, RENDER)
            for name, path in dimensions.items()
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing dimension: {e}: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
