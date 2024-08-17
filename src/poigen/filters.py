from html import escape
from json import loads as parsedict

from poigen.filterclass import EmptyFilterResult, FilterResult
from poigen.helpers import (
    add_item_name,
    format_coordinates,
    format_horse,
    loop_over_generic_inventory,
    specific_item_search,
    translate_item_id,
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
            signstring = f"<b>Sign at {format_coordinates(poi)}: </b><br>" + signstring
            return FilterResult("Sign", signstring)
        else:
            return EmptyFilterResult()


def generic_chest_filter(poi):
    match str(poi["id"]):
        case "minecraft:chest":
            storage_type = "Chest"
        case "minecraft:trapped_chest":
            storage_type = "Trapped Chest"
        case "minecraft:barrel":
            storage_type = "Barrel"
        case "minecraft:shulker_box":
            storage_type = "Shulker Box"
        case "minecraft:dispenser":
            storage_type = "Dispenser"
        case "minecraft:dropper":
            storage_type = "Dropper"
        case "minecraft:hopper":
            storage_type = "Hopper"
        case "minecraft:chest_minecart":
            storage_type = "Chest Minecart"
        case "minecraft:hopper_minecart":
            storage_type = "Hopper Minecart"
        case _:
            return None
    if "LootTable" in poi:
        return EmptyFilterResult()
    else:
        if len(poi.get("Items", [])) > 0:
            return FilterResult(
                storage_type,
                "<br>".join(loop_over_generic_inventory(poi, storage_type)),
            )
        else:
            return EmptyFilterResult()


def villagerFilter(poi):
    if str(poi["id"]) == "minecraft:villager":
        if "CustomName" in poi:
            vn = parsedict(str(poi["CustomName"]))["text"]
            villagerstring = [f"<b> {vn} at {format_coordinates(poi)}: </b>"]
            if "Offers" in poi:
                for r in poi["Offers"]["Recipes"]:
                    trade = f"{r['buy']['Count']}x {translate_item_id(r['buy']['id'])}"
                    if "buyB" in r and str(r["buyB"]["id"]) != "minecraft:air":
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
            f"{format_coordinates(poi)}",
        ]
        return FilterResult(poi["name"], "<br>".join(tarr))


def towerFilter(poi):
    if str(poi["id"]) == "Tower":
        tarr = [
            f"<b>{poi['name']}</b>",
            f"{format_coordinates(poi)}",
        ]
        return FilterResult(poi["name"], "<br>".join(tarr))


def generic_entity_filter(poi):
    id_to_result = {
        "minecraft:axolotl": "Axolotl",
        "minecraft:beacon": "Beacon",
        "minecraft:bee": "Bee",
        "minecraft:beehive": "Bee Hive",
        "minecraft:blaze": "Blaze",
        "minecraft:brewing_stand": "Brewing Stand",
        "minecraft:cat": "Cat",
        "minecraft:chicken": "Chicken",
        "minecraft:conduit": "Conduit",
        "minecraft:cow": "Cow",
        "minecraft:dolphin": "Dolphin",
        "minecraft:drowned": "Drowned",
        "minecraft:elder_guardian": "Elder Guardian",
        "minecraft:enchanting_table": "Enchanting Table",
        "minecraft:end_crystal": "End Crystal",
        "minecraft:ender_chest": "Ender Chest",
        "minecraft:evoker": "Evoker",
        "minecraft:fox": "Fox",
        "minecraft:glow_squid": "Glow Squid",
        "minecraft:goat": "Goat",
        "minecraft:guardian": "Guardian",
        "minecraft:illusioner": "Illusioner",
        "minecraft:iron_golem": "Iron Golem",
        "minecraft:llama": "Llama",
        "minecraft:mooshroom": "Mooshroom",
        "minecraft:ocelot": "Ocelot",
        "minecraft:panda": "Panda",
        "minecraft:parrot": "Parrot",
        "minecraft:pig": "Pig",
        "minecraft:piglin": "Piglin",
        "minecraft:piglin_brute": "Piglin Brute",
        "minecraft:pillager": "Pillager",
        "minecraft:polar_bear": "Polar Bear",
        "minecraft:rabbit": "Rabbit",
        "minecraft:sheep": "Sheep",
        "minecraft:skull": "Skull",  # todo: move to special filter displaying skin?
        "minecraft:slime": "Slime",
        "minecraft:strider": "Strider",
        "minecraft:tnt_minecart": "TNT Minecart",
        "minecraft:trident": "Trident (Entity)",
        "minecraft:turtle": "Turtle",
        "minecraft:vindicator": "Vindicator",
        "minecraft:wandering_trader": "Wandering Trader",
        "minecraft:witch": "Witch",
        "minecraft:wither_skeleton": "Wither Skeleton",
        "minecraft:wither_skull": "Wither Skull",
        "minecraft:wolf": "Wolf",
        "minecraft:zombie_horse": "Zombie Horse",
        "minecraft:zombie_villager": "Zombie Villager",
    }

    entity_id = str(poi["id"])
    if entity_id in id_to_result:
        return FilterResult(id_to_result[entity_id])

    if entity_id == "minecraft:horse":
        return FilterResult(
            "Horse",
            "<br>".join(format_horse("Horse", poi, translate_markings=True)),
        )
    elif entity_id == "minecraft:donkey":
        return FilterResult("Donkey", "<br>".join(format_horse("Donkey", poi)))
    elif entity_id == "minecraft:mule":
        return FilterResult("Mule", "<br>".join(format_horse("Mule", poi)))


def booksFilter(poi):
    return specific_item_search(
        poi, ["minecraft:written_book", "minecraft:writable_book"], "Book"
    )


def itemframeFilter(poi):
    if str(poi["id"]) == "minecraft:item_frame":
        if "Item" in poi:
            itemstring = [
                f"<b>Item Frame found at {format_coordinates(poi)}: </b>",
                translate_item_id(poi["Item"]["id"]) + add_item_name(poi["Item"]),
            ]
            return FilterResult("Item Frame", "<br>".join(itemstring))


def armorstandFilter(poi):
    if str(poi["id"]) == "minecraft:armor_stand":
        has_items = False
        itemstring = [f"<b>Armor Stand at {format_coordinates(poi)}: </b>"]
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
                f"<b>Item found in Lectern at {format_coordinates(poi)}:</b><br>{istring}",
            )
        else:
            return EmptyFilterResult()


def spawnerFilter(poi):
    if str(poi["id"]) == "minecraft:mob_spawner":
        if "SpawnPotentials" in poi:
            if len(poi["SpawnPotentials"]) > 0:
                itemstring = [f"<b>Spawner found at {format_coordinates(poi)}: </b>"]
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
