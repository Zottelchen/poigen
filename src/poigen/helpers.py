from json import loads as parsedict

from poigen.filterclass import EmptyFilterResult, FilterResult
from poigen.minecraft_data import ALL_ITEMS, HORSE_VARIANTS


def add_item_name(itemdict):
    if "tag" in itemdict:
        if "display" in itemdict["tag"]:
            if "Name" in itemdict["tag"]["display"]:
                if (
                    itemdict["tag"]["display"]["Name"] is not None
                    and itemdict["tag"]["display"]["Name"] != ""
                ):
                    jsonvalues = parsedict(str(itemdict["tag"]["display"]["Name"]))
                    if "text" in jsonvalues:
                        return f" (<i>{jsonvalues['text']}</i>)"
        elif "title" in itemdict["tag"]:
            return f" (<i>{itemdict['tag']['title']}</i>)"
    return ""


def format_coordinates_str(x, y, z):
    return "{:.1f}, {:.1f}, {:.1f}".format(float(str(x)), float(str(y)), float(str(z)))


def format_coordinates(poi):
    try:
        return format_coordinates_str(poi["x"], poi["y"], poi["z"])
    except KeyError:
        return format_coordinates_str(poi["Pos"][0], poi["Pos"][1], poi["Pos"][2])


def translate_item_id(itemid: str, iconsuffix=False, iconprefix=True) -> str:
    itemid = str(itemid)
    if itemid in ALL_ITEMS:
        istr = ""
        if iconprefix:
            istr += '<img loading="lazy" src="assets/icons/{0}.png" alt="{1}" width="16" height="16"> '.format(
                itemid.split(":")[1], ALL_ITEMS[itemid]
            )
        istr += ALL_ITEMS[itemid]
        if iconsuffix:
            istr += ' <img loading="lazy" src="assets/icons/{0}.png" alt="{1}" width="16" height="16">'.format(
                itemid.split(":")[1], ALL_ITEMS[itemid]
            )
        return istr
    else:
        return str(itemid)


def translate_horse_markings(variant: int) -> str:
    # whoop whoop, doublecast. because you can't cast TAG_INT to int, but to string.
    variant = int(str(variant))
    if variant in HORSE_VARIANTS:
        return HORSE_VARIANTS[variant]
    else:
        return "Probably White"


def format_horse(name: str, poi, translate_markings=False):
    horsearr = [
        f"<b>{name}</b>{' - ' + translate_horse_markings(poi['Variant']) if translate_markings else ''}",
        "Speed: ",
        "Jump Strength: ",
        "Health: ",
    ]
    if "Attributes" in poi:
        for attr in poi["Attributes"]:
            if str(attr["Name"]) == "minecraft:generic.movement_speed":
                horsearr[1] += str(round(float(str(attr["Base"])), 3))
            elif str(attr["Name"]) == "minecraft:generic.max_health":
                horsearr[3] += (
                    f'{float(str(attr["Base"])) / 2.0} <img src="assets/icons/heart.png" alt="Hearts" width="16" height="16">'
                )
            elif str(attr["Name"]) == "minecraft:horse.jump_strength":
                horsearr[2] += str(round(float(str(attr["Base"])), 3))
            elif str(poi["id"]) == "minecraft:donkey":
                horsearr[2] += "No."

    if translate_markings:
        horsearr.append(
            '<img loading="lazy" src="assets/horses/{0}.webp" alt="{1}" width="108" height="120">'.format(
                poi["Variant"], translate_horse_markings(poi["Variant"])
            )
        )
    return horsearr


def loop_over_generic_inventory(poi, entity_name):
    items = poi.get("Items", [])

    itemstring = [
        f"<b>{entity_name} with {len(items)} items at {format_coordinates(poi)}: </b>"
    ]

    for item in items:
        istring = f"{item['Count'] if 'Count' in item else item['count']}x {translate_item_id(item['id'])}"
        istring = istring + add_item_name(item)
        itemstring.append(istring)
    return itemstring


def get_coordinate(poi, xyz: str):
    try:
        match xyz.lower():
            case "x":
                return int(float(str(poi["x"])))
            case "y":
                return int(float(str(poi["y"])))
            case "z":
                return int(float(str(poi["z"])))
    except KeyError:
        match xyz.lower():
            case "x":
                return int(float(str(poi["Pos"][0])))
            case "y":
                return int(float(str(poi["Pos"][1])))
            case "z":
                return int(float(str(poi["Pos"][2])))


def get_coordinates(poi):
    return {
        "x": get_coordinate(poi, "x"),
        "y": get_coordinate(poi, "y"),
        "z": get_coordinate(poi, "z"),
    }


def specific_item_search(poi, searched_item_ids: list, item_name: str):
    if str(poi["id"]) in [
        "minecraft:trapped_chest",
        "minecraft:chest",
        "minecraft:barrel",
        "minecraft:dropper",
        "minecraft:dispenser",
        "minecraft:furnace",
        "minecraft:brewing_stand",
        "minecraft:hopper",
        "minecraft:shulker_box",
        "minecraft:chest_minecart",
        "minecraft:hopper_minecart",
    ]:
        if "LootTable" in poi:
            return EmptyFilterResult()
        else:
            if len(poi.get("Items", [])) > 0:
                item_found = False
                items = poi.get("Items", [])
                itemstring = [
                    f"<b>{item_name} found at {format_coordinates(poi)}: </b>"
                ]
                for item in items:
                    if str(item["id"]) in searched_item_ids:
                        item_found = True
                        istring = f"{item['Count']}x {translate_item_id(item['id'])}"
                        istring = istring + add_item_name(item)
                        itemstring.append(istring)
                        if searched_item_ids == ["minecraft:enchanted_book"]:
                            try:
                                for ench in item["tag"]["StoredEnchantments"]:
                                    itemstring.append(
                                        f" - lvl{ench['lvl']} {ench['id']}"
                                    )
                            except KeyError:
                                itemstring.append("NO ENCHANTMENTS FOUND ?")
                                print("NO ENCHANT:", item)
                if item_found:
                    return FilterResult(item_name, "<br>".join(itemstring))
            else:
                return EmptyFilterResult()
    elif str(poi["id"]) == "minecraft:item_frame":
        if "Item" in poi:
            if str(poi["Item"]["id"]) in searched_item_ids:
                itemstring = [
                    f"<b>{item_name} found in Item Frame at {format_coordinates(poi)}: </b>",
                    translate_item_id(poi["Item"]["id"]) + add_item_name(poi["Item"]),
                ]
                if searched_item_ids == ["minecraft:enchanted_book"]:
                    try:
                        for ench in poi["Item"]["tag"]["StoredEnchantments"]:
                            itemstring.append(f" - lvl{ench['lvl']} {ench['id']}")
                            print("NO ENCHANT:", poi["Item"])
                    except KeyError:
                        itemstring.append("NO ENCHANTMENTS FOUND ?")
                return FilterResult(item_name, "<br>".join(itemstring))
    elif str(poi["id"]) == "minecraft:armor_stand":
        has_items = False
        itemstring = [
            f"<b>Book found in Armor Stand at {format_coordinates(poi)}: </b>"
        ]
        for item in poi["HandItems"]:
            has_items, itemstring = search_in_armor_stand(
                has_items, item, itemstring, searched_item_ids
            )
        for item in poi["ArmorItems"]:
            has_items, itemstring = search_in_armor_stand(
                has_items, item, itemstring, searched_item_ids
            )
        if has_items:
            return FilterResult(item_name, "<br>".join(itemstring))
    elif str(poi["id"]) == "minecraft:lectern":
        if "Book" in poi:
            if str(poi["Book"]["id"]) in searched_item_ids:
                istring = f"{1}x {translate_item_id(poi['Book']['id'])}"
                istring += add_item_name(poi["Book"])

                if searched_item_ids == ["minecraft:enchanted_book"]:
                    try:
                        for ench in poi["Book"]["tag"]["StoredEnchantments"]:
                            istring += f"\n - lvl{ench['lvl']} {ench['id']}"
                    except KeyError:
                        istring += "NO ENCHANTMENTS FOUND ?"
                        print("NO ENCHANT:", poi["Book"])
                return FilterResult(
                    item_name,
                    f"<b>{item_name} found in Lectern at {format_coordinates(poi)}:</b><br>{istring}",
                )


def search_in_armor_stand(has_items, item, itemstring, searched_item_ids):
    if "id" in item and str(item["id"]) != "minecraft:air":
        if str(item["id"]) in searched_item_ids:
            has_items = True
            itemstring.append(translate_item_id(item["id"]) + add_item_name(item))
            if searched_item_ids == ["minecraft:enchanted_book"]:
                try:
                    for ench in item["tag"]["StoredEnchantments"]:
                        itemstring.append(f" - lvl{ench['lvl']} {ench['id']}")
                except KeyError:
                    itemstring.append("NO ENCHANTMENTS FOUND ?")
                    print("NO ENCHANT:", item)
    return has_items, itemstring
