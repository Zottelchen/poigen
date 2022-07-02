from html import escape
from json import loads as parsedict

from filterclass import FilterResult, EmptyFilterResult
from helpers import (
    format_coordinates,
    add_item_name,
    translate_item_id,
    format_horse,
    loop_over_generic_inventory,
    specific_item_search,
)


def signFilter(poi):
    if str(poi["id"]) in [
        "minecraft:sign",
        "minecraft:oak_sign",
        "minecraft:spruce_sign",
        "minecraft:birch_sign",
        "minecraft:jungle_sign",
        "minecraft:acacia_sign",
        "minecraft:dark_oak_sign",
        "minecraft:crimson_sign",
        "minecraft:warped_sign",
        "minecraft:oak_wall_sign",
        "minecraft:spruce_wall_sign",
        "minecraft:birch_wall_sign",
        "minecraft:jungle_wall_sign",
        "minecraft:acacia_wall_sign",
        "minecraft:dark_oak_wall_sign",
        "minecraft:crimson_wall_sign",
        "minecraft:warped_wall_sign",
    ]:
        signstring = [
            escape(parsedict(str(poi["Text1"]))["text"]),
            escape(parsedict(str(poi["Text2"]))["text"]),
            escape(parsedict(str(poi["Text3"]))["text"]),
            escape(parsedict(str(poi["Text4"]))["text"]),
        ]
        signstring = "<br>".join(signstring)
        if signstring != "<br><br><br>":
            signstring = (
                f"<b>Sign at {format_coordinates(poi['x'], poi['y'], poi['z'])}: </b><br>"
                + signstring
            )
            return FilterResult("Sign", signstring)
        else:
            return None


def generic_chest_filter(poi):
    match str(poi["id"]):
        case "minecraft:chest":
            storage_type = "Chest"
        case "minecraft:trapped_chest":
            storage_type = "Trapped Chest"
        case "minecraft:barrel":
            storage_type = "Barrel"
        case _:
            return None
    if "LootTable" in poi:
        return None
    else:
        if len(poi.get("Items", [])) > 0:
            return FilterResult(
                storage_type,
                "<br>".join(loop_over_generic_inventory(poi, storage_type)),
            )
        else:
            return None


def villagerFilter(poi):
    if str(poi["id"]) == "minecraft:villager":
        if "CustomName" in poi:
            vn = parsedict(str(poi["CustomName"]))["text"]
            villagerstring = [
                f"<b> {vn} at {format_coordinates(poi['Pos'][0], poi['Pos'][1], poi['Pos'][2])}: </b>"
            ]
            if "Offers" in poi:
                for r in poi["Offers"]["Recipes"]:
                    trade = f"{r['buy']['Count']}x {translate_item_id(r['buy']['id'])}"
                    if "buyB" in r and r["buyB"]["id"] != "minecraft:air":
                        trade = (
                            trade
                            + f" & {r['buyB']['Count']}x {translate_item_id(r['buyB']['id'])}"
                        )
                    trade = (
                        trade
                        + " &#8594;"
                        + f" {r['sell']['Count']}x {translate_item_id(r['sell']['id'])}"
                    )
                    trade = trade + add_item_name(r["sell"])
                    villagerstring.append(trade)
            return FilterResult("Villager", "<br>".join(villagerstring))


def townFilter(poi):
    if str(poi["id"]) == "Town":
        tarr = [
            f"<b>{poi['name']}</b>",
            f"{format_coordinates(poi['x'], poi['y'], poi['z'])}",
        ]
        return FilterResult(poi["name"], "<br>".join(tarr))


def towerFilter(poi):
    if str(poi["id"]) == "Tower":
        tarr = [
            f"<b>{poi['name']}</b>",
            f"{format_coordinates(poi['x'], poi['y'], poi['z'])}",
        ]
        return FilterResult(poi["name"], "<br>".join(tarr))


def generic_entity_filter(poi):
    match str(poi["id"]):
        case "minecraft:pig":
            return FilterResult("Pig")
        case "minecraft:sheep":
            return FilterResult("Sheep")
        case "minecraft:cow":
            return FilterResult("Cow")
        case "minecraft:chicken":
            return FilterResult("Chicken")
        case "minecraft:mooshroom":
            return FilterResult("Mooshroom")
        case "minecraft:wolf":
            return FilterResult("Wolf")
        case "minecraft:ocelot":
            return FilterResult("Ocelot")
        case "minecraft:cat":
            return FilterResult("Cat")
        case "minecraft:horse":
            return FilterResult(
                "Horse",
                "<br>".join(format_horse("Horse", poi, translate_markings=True)),
            )
        case "minecraft:donkey":
            return FilterResult("Donkey", "<br>".join(format_horse("Donkey", poi)))
        case "minecraft:elder_guardian":
            return FilterResult("Elder Guardian")
        case "minecraft:llama":
            return FilterResult("Llama")
        case "minecraft:rabbit":
            return FilterResult("Rabbit")
        case "minecraft:panda":
            return FilterResult("Panda")
        case "minecraft:polar_bear":
            return FilterResult("Polar Bear")
        case "minecraft:turtle":
            return FilterResult("Turtle")
        case "minecraft:parrot":
            return FilterResult("Parrot")
        case "minecraft:fox":
            return FilterResult("Fox")
        case "minecraft:drowned":
            return FilterResult("Drowned")
        case "minecraft:bee":
            return FilterResult("Bee")


def booksFilter(poi):
    return specific_item_search(
        poi, ["minecraft:written_book", "minecraft:writable_book"], "Book"
    )


def itemframeFilter(poi):
    if str(poi["id"]) == "minecraft:item_frame":
        if "Item" in poi:
            itemstring = [
                f"<b>Item Frame found at {format_coordinates(poi['Pos'][0], poi['Pos'][1], poi['Pos'][2])}: </b>",
                translate_item_id(poi["Item"]["id"]) + add_item_name(poi["Item"]),
            ]
            return FilterResult("Item Frame", "<br>".join(itemstring))


def armorstandFilter(poi):
    if str(poi["id"]) == "minecraft:armor_stand":
        has_items = False
        itemstring = [
            f"<b>Armor Stand at {format_coordinates(poi['Pos'][0], poi['Pos'][1], poi['Pos'][2])}: </b>"
        ]
        for item in poi["HandItems"]:
            if "id" in item and item["id"] != "minecraft:air":
                has_items = True
                itemstring.append(translate_item_id(item["id"]) + add_item_name(item))
        for item in poi["ArmorItems"]:
            if "id" in item and item["id"] != "minecraft:air":
                has_items = True
                itemstring.append(translate_item_id(item["id"]) + add_item_name(item))
        if has_items:
            return FilterResult("Armor Stand", "<br>".join(itemstring))


def mapsFilter(poi):
    return specific_item_search(poi, ["minecraft:filled_map"], "Map")


def enchantedbooksFilter(poi):
    return specific_item_search(poi, ["minecraft:enchanted_book"], "Enchanted Book")


def lecternFilter(poi):
    if str(poi["id"]) == "minecraft:lectern":
        if "Book" in poi:
            istring = f"{1}x {translate_item_id(poi['Book']['id'])}"
            istring = istring + add_item_name(poi["Book"])
            return FilterResult(
                "Lectern",
                f"<b>Item found in Lectern at {format_coordinates(poi['x'], poi['y'], poi['z'])}:</b><br>{istring}",
            )
        else:
            return EmptyFilterResult()


def spawnerFilter(poi):
    if str(poi["id"]) == "minecraft:mob_spawner":
        if "SpawnPotentials" in poi:
            if len(poi["SpawnPotentials"]) > 0:
                itemstring = [
                    f"<b>Spawner found at {format_coordinates(poi['x'], poi['y'], poi['z'])}: </b>"
                ]
                try:
                    for mob in poi["SpawnPotentials"]:
                        if "Entity" in mob:
                            itemstring.append(" - " + str(mob["Entity"]["id"]))
                    return FilterResult("Spawner", "<br>".join(itemstring))
                except:
                    print("Something odd with Spawner:", poi)


all_filters = [
    signFilter,
    generic_chest_filter,  # contains the code for chests, trapped chests & barrels
    # towerFilter,  # static Towns (currently not implemented)
    # townFilter,  # static Towers (currently not implemented)
    armorstandFilter,
    booksFilter,  # finds written books in all sorts of containers
    enchantedbooksFilter,  # finds enchanted books in all sorts of containers
    generic_entity_filter,  # contains a lot of useful minecraft entities, that do NOT need any more information processing (other than their location)
    itemframeFilter,
    lecternFilter,
    mapsFilter,  # finds maps in all sorts of containers
    spawnerFilter,
    villagerFilter,  # only lists villagers with names
]
