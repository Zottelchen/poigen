import sys
from argparse import ArgumentParser
from pathlib import Path

from nbt import region

from POIDB import POIDB


def handle_entities(markers: POIDB, world_dir: Path):
    entity_files = list(world_dir.glob("entities/*.mca"))
    print(
        f"Starting with external entity files. Found {len(entity_files)} entity files."
    )
    if len(entity_files) == 0:
        print("There were no entity files.")
        return

    for entity_file in entity_files:
        region_file = region.RegionFile(entity_file.as_posix(), "rb")
        chunks = region_file.get_chunks()
        print(f"\tFound {len(chunks)} Chunks in Entityfile: {entity_file}")
        if len(chunks) > 0:
            for chunk in chunks:
                chunk_nbt = region_file.get_nbt(chunk["x"], chunk["z"])
                if len(chunk_nbt["Entities"]) > 0:
                    print(
                        f"\t\tFound {len(chunk_nbt['Entities'])} Entities in Chunk {chunk['x']}, {chunk['z']}"
                    )
                    markers.add_entities_from_chunk(chunk_nbt["Entities"])


def handle_tile_entities(markers: POIDB, world_dir: Path):
    region_files = list(world_dir.glob("region/*.mca"))

    print(f"Starting with region files. Found {len(region_files)} region files.")
    if len(region_files) == 0:
        print("There were no region files.")
        return

    for rf in region_files:
        region_file = region.RegionFile(rf.as_posix(), "rb")
        chunks = region_file.get_chunks()
        print(f"\tFound {len(chunks)} Chunks in Regionfile: {rf}")
        if len(chunks) > 0:
            for chunk in chunks:
                chunk_nbt = region_file.get_nbt(chunk["x"], chunk["z"])
                if len(chunk_nbt["Level"]["TileEntities"]) > 0:
                    print(
                        f"\t\tFound {len(chunk_nbt['Level']['TileEntities'])} Entities in Chunk {chunk['x']}, {chunk['z']}"
                    )
                    markers.add_entities_from_chunk(chunk_nbt["Level"]["TileEntities"])


def main():
    parser = ArgumentParser(description="POIGen by Zottelchen")
    parser.add_argument("world_directory", help="Directory of the Minecraft World")
    parser.add_argument("render_directory", help="Directory of the Overviewer Render")
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

    args = parser.parse_args()
    WORLD = Path(args.world_directory)
    RENDER = Path(args.render_directory)

    if not RENDER.is_dir() or not WORLD.is_dir():
        print("World or Render directory is not a folder path.")
        sys.exit(666)

    markers = POIDB()
    if args.skip_entities:
        print("Skipping entities.")
    else:
        handle_entities(markers, WORLD)
    if args.skip_entities:
        print("Skipping tile entities.")
    else:
        handle_tile_entities(markers, WORLD)

    print(f"\n\nThe following entities were found:\n{markers.entities_overview}")

    print(
        f"\n\nThe following entities were found but not have no filters designed for them:\n{markers.unmapped_overview}"
    )
    print("\nWriting Output.")
    markers.write_output(RENDER)
    print("Done!")


if __name__ == "__main__":
    main()
