def bbbbFilter(poi):  # badly bugged blue books
    if poi["id"] in [
        "Trapped Chest",
        "minecraft:trapped_chest",
        "Chest",
        "minecraft:chest",
        "Barrel",
        "minecraft:barrel",
    ]:
        if "LootTable" in poi:
            return None
        else:
            if len(poi.get("Items", [])) > 0:
                book_found = False
                items = poi.get("Items", [])
                itemstring = [
                    "<b>Badly Bugged Blue Book found at {0}: </b>".format(
                        formatCoordinates(poi["x"], poi["y"], poi["z"])
                    )
                ]
                for item in items:
                    if item["id"] == "minecraft:enchanted_book":
                        if "tag" in item:
                            if "Enchantments" in item["tag"]:
                                book_found = True
                                istring = "{0}x {1}".format(
                                    item["Count"], translateItemId(item["id"])
                                )
                                istring = istring + addItemName(item)
                                itemstring.append(istring)
                                for ench in item["tag"]["Enchantments"]:
                                    itemstring.append(
                                        " - lvl{0} {1}".format(ench["lvl"], ench["id"])
                                    )
                        else:
                            book_found = True
                            itemstring.append("NO TAG?!")
                if book_found:
                    return ("Badly Bugged Blue Book", "<br>".join(itemstring))
            else:
                return None
    elif poi["id"] == "Item Frame" or poi["id"] == "minecraft:item_frame":
        if "Item" in poi:
            if poi["Item"]["id"] == "minecraft:enchanted_book":
                if "tag" in item:
                    if "Enchantments" in poi["Item"]["tag"]:
                        itemstring = [
                            "<b>Badly Bugged Blue Book found in Item Frame at {0}: </b>".format(
                                formatCoordinates(poi["Pos"][0], poi["Pos"][1], poi["Pos"][2])
                            )
                        ]
                        itemstring.append(
                            translateItemId(poi["Item"]["id"]) + addItemName(poi["Item"])
                        )
                        for ench in poi["Item"]["tag"]["Enchantments"]:
                            itemstring.append(" - lvl{0} {1}".format(ench["lvl"], ench["id"]))
                        return ("Badly Bugged Blue Book", "<br>".join(itemstring))
                else:
                    itemstring.append("NO TAG?!")
                    return ("Badly Bugged Blue Book", "<br>".join(itemstring))
    elif poi["id"] == "Armor Stand" or poi["id"] == "minecraft:armor_stand":
        has_items = False
        itemstring = [
            "<b>Badly Bugged Blue Book found in Armor Stand at {0}: </b>".format(
                formatCoordinates(poi["Pos"][0], poi["Pos"][1], poi["Pos"][2])
            )
        ]
        for item in poi["HandItems"]:
            if "id" in item and item["id"] != "minecraft:air":
                if item["id"] == "minecraft:enchanted_book":
                    if "tag" in item:
                        if "Enchantments" in item["tag"]:
                            has_items = True
                            itemstring.append(translateItemId(item["id"]) + addItemName(item))
                            for ench in item["tag"]["Enchantments"]:
                                itemstring.append(" - lvl{0} {1}".format(ench["lvl"], ench["id"]))
                    else:
                        has_items = True
                        itemstring.append("NO TAG?!")
        for item in poi["ArmorItems"]:
            if "id" in item and item["id"] != "minecraft:air":
                if item["id"] == "minecraft:enchanted_book":
                    if "tag" in item:
                        if "Enchantments" in item["tag"]:
                            has_items = True
                            itemstring.append(translateItemId(item["id"]) + addItemName(item))
                            for ench in item["tag"]["Enchantments"]:
                                itemstring.append(" - lvl{0} {1}".format(ench["lvl"], ench["id"]))
                    else:
                        has_items = True
                        itemstring.append("NO TAG?!")
        if has_items:
            return ("Badly Bugged Blue Book", "<br>".join(itemstring))


def dolphinFilter(poi):
    if poi["id"] == "Dolphin" or poi["id"] == "minecraft:dolphin":
        return "Dolphin"


def guardianFilter(poi):
    if poi["id"] == "Guardian" or poi["id"] == "minecraft:guardian":
        return "Guardian"
