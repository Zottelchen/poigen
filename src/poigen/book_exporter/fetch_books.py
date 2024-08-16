import hashlib
import os
import re
import sys
from json import loads as parsedict
from pathlib import Path

import tabulate
from dotenv import load_dotenv
from nbt import region

load_dotenv()
# CONFIG
WORLD = Path(os.getenv("WORLD_DIRECTORY"))
DELETE_AFTER = False
LOGFILE = Path("books/_LOG.txt")
LISTFILE = Path("books/_list.md")

# WORK WORK WORK
unsafe_chars_pattern = re.compile(r'[<>:"/\\|?*]')
LOGFILE = open(LOGFILE, "a", encoding="utf-8", buffering=1)


if not WORLD.is_dir():
    print("Invalid World Path")
    sys.exit()


def generate_hash(text):
    sha256_hash = hashlib.sha256(text.encode()).hexdigest()
    return sha256_hash


def fetch_text(pages):
    text = []
    for page in pages:
        text.append(str(page))
    return "\n".join(text)


def fetch_title(book_data):
    if "display" in book_data:
        if "Name" in book_data["display"]:
            if (
                book_data["display"]["Name"] is not None
                and book_data["display"]["Name"] != ""
            ):
                jsonvalues = parsedict(str(book_data["display"]["Name"]))
                if "text" in jsonvalues:
                    return jsonvalues["text"]
    title = str(book_data.get("title", "No Title"))
    if title == "":
        title = "No Title"
    return title


def booksearch(entity):
    book = None
    book_ids = ["minecraft:written_book", "minecraft:writable_book"]
    if str(entity["id"]) in [
        "minecraft:trapped_chest",
        "minecraft:chest",
        "minecraft:barrel",
    ]:
        if "LootTable" in entity:
            return None
        else:
            if len(entity.get("Items", [])) > 0:
                items = entity.get("Items", [])
                for item in items:
                    if str(item["id"]) in book_ids:
                        if "tag" in item:
                            book_data = item["tag"]
                            book = {}
                            book["x"] = entity["x"]
                            book["y"] = entity["y"]
                            book["z"] = entity["z"]
                            book["tp"] = (
                                f"/tp {entity['x']} {entity['y']} {entity['z']}"
                            )
                            book["found_in"] = entity["id"]
                            book["text"] = fetch_text(
                                book_data.get("pages", ["No Text?"])
                            )
                            book["title"] = fetch_title(book_data)
                            book["author"] = book_data.get("author", "No Author")
    elif str(entity["id"]) == "minecraft:item_frame":
        if "Item" in entity:
            if str(entity["Item"]["id"]) in book_ids:
                if "tag" in entity["Item"]:
                    book_data = entity["Item"]["tag"]
                    book = {}
                    book["x"] = entity["Pos"][0]
                    book["y"] = entity["Pos"][1]
                    book["z"] = entity["Pos"][2]
                    book["tp"] = f"/tp {book['x']} {book['y']} {book['z']}"
                    book["found_in"] = entity["id"]
                    book["text"] = fetch_text(book_data.get("pages", ["No Text?"]))
                    book["title"] = fetch_title(book_data)
                    book["author"] = book_data.get("author", "No Author")
    elif str(entity["id"]) == "minecraft:armor_stand":
        for item_slots in [entity["HandItems"], entity["ArmorItems"]]:
            for item in item_slots:
                if "id" in item and str(item["id"]) != "minecraft:air":
                    if str(item["id"]) in book_ids:
                        if "tag" in item:
                            book_data = item["tag"]
                            book = {}
                            book["x"] = entity["Pos"][0]
                            book["y"] = entity["Pos"][1]
                            book["z"] = entity["Pos"][2]
                            book["tp"] = f"/tp {book['x']} {book['y']} {book['z']}"
                            book["found_in"] = entity["id"]
                            book["text"] = fetch_text(
                                book_data.get("pages", ["No Text?"])
                            )
                            book["title"] = fetch_title(book_data)
                            book["author"] = book_data.get("author", "No Author")
    elif str(entity["id"]) == "minecraft:lectern":
        if "Book" in entity:
            if str(entity["Book"]["id"]) in book_ids:
                if "tag" in entity["Book"]:
                    book_data = entity["Book"]["tag"]
                    book = {}
                    book["x"] = entity["x"]
                    book["y"] = entity["y"]
                    book["z"] = entity["z"]
                    book["tp"] = f"/tp {entity['x']} {entity['y']} {entity['z']}"
                    book["found_in"] = entity["id"]
                    book["text"] = fetch_text(book_data.get("pages", ["No Text?"]))
                    book["title"] = fetch_title(book_data)
                    book["author"] = book_data.get("author", "No Author")
    return book


def main():
    world_files = list(WORLD.glob(pattern="**/*.mca"))
    wf_len = len(world_files)
    book_list = []
    for index, wf in enumerate(world_files):
        region_file = region.RegionFile(wf.as_posix(), "rb")
        chunks = region_file.get_chunks()
        if len(chunks) > 0:
            # print(f"{index}/{wf_len} Found {len(chunks)} Chunks in File: {wf}")
            for chunk in chunks:
                chunk_nbt = region_file.get_nbt(chunk["x"], chunk["z"])
                try:
                    tile_entities = chunk_nbt["Level"]["TileEntities"]
                except KeyError:
                    tile_entities = []
                try:
                    entities = chunk_nbt["Entities"]
                except KeyError:
                    entities = []
                if len(tile_entities) > 0 or len(entities) > 0:
                    # print(                        f"\tChunk {chunk['x']}, {chunk['z']}: TE {len(tile_entities)} | E {len(entities)}"                    )

                    # Actual Work
                    for entity_group in [tile_entities, entities]:
                        for entity in entity_group:
                            book = booksearch(entity)

                            if book:
                                book_list.append(
                                    {"title": book["title"], "tp": book["tp"]}
                                )
                                filename = re.sub(
                                    unsafe_chars_pattern, "_", str(book["title"])
                                )
                                if book["title"] == "No Title" or book["title"] == "":
                                    filename = f"No Title-{generate_hash(book['text']+book['tp'])}"
                                if Path(f"books/{filename}.md").is_file():
                                    filename = f"{filename}-{generate_hash(book['text']+book['tp'])}"
                                from_file = str(wf).replace(str(WORLD), "")
                                print(
                                    f"[{index}/{wf_len}][{from_file}][{chunk['x']},{chunk['z']}] Found Book: {book['title']}. Saving as '{filename}.md'"
                                )
                                print(
                                    f"[{index}/{wf_len}][{from_file}][{chunk['x']},{chunk['z']}] Found Book: {book['title']}. Saving as '{filename}.md'",
                                    file=LOGFILE,
                                    flush=True,
                                )
                                Path(f"books/{filename}.md").parent.mkdir(
                                    parents=True, exist_ok=True
                                )
                                with open(
                                    f"books/{filename}.md", "w", encoding="utf-8"
                                ) as fo:
                                    fo.write(
                                        f"---\ntitle: {book['title']}\nauthor: {book['author']}\nentity: {book['found_in']}\ntp: {book['tp']}\nfile: {from_file}\n---\n\n{book['text']}"
                                    )

        if DELETE_AFTER and index > 0:
            world_files[index - 1].unlink()

    with open(LISTFILE, "w", encoding="utf-8") as fo:
        fo.write(
            tabulate.tabulate(
                book_list,
                headers="keys",
                tablefmt="github",
                showindex="always",
                disable_numparse=True,
            )
        )


if __name__ == "__main__":
    main()
