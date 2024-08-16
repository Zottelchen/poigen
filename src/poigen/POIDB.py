import json
from pathlib import Path

from nbt import nbt

from poigen.filterclass import EmptyFilterResult, FilterResult
from poigen.filters import all_filters
from poigen.hardcoded import marker_groups
from poigen.helpers import get_coordinate


class POIDB:
    def __init__(self):
        self.entities = {}
        self.unmapped = {}

    @property
    def unmapped_overview(self):
        retstr = ""
        for k in self.unmapped.keys():
            retstr += f"\n\t{self.unmapped[k]}x {k}"
        return retstr

    @property
    def entities_overview(self):
        retstr = ""
        for k in self.entities.keys():
            retstr += f"\n\t{len(self.entities[k]['raw'])}x {k}"
        return retstr

    def fix_missing_entities(self):
        """Adds entities which are defined in the basemarkers.js but were not found during processing."""
        for entry in marker_groups["normalrender"]:
            if entry["groupName"] not in self.entities:
                self.entities[entry["groupName"]] = {
                    "name": entry["groupName"].replace("G_", "").replace("_", " "),
                    "created": False,
                    "raw": [],
                }

    def write_output(self, render_dir):
        with open(Path(render_dir, "markersDB.js"), "w") as output:
            output.write("var markersDB=")
            self.fix_missing_entities()
            json.dump(self.entities, output, sort_keys=True, indent=2)
            output.write(";\n")
        with open(Path(render_dir, "markers.js"), "w") as output:
            output.write("var markers=")
            json.dump(marker_groups, output, sort_keys=True, indent=2)
            output.write(";\n")
        with open(Path(render_dir, "baseMarkers.js"), "w") as output:
            output.write("overviewer.util.injectMarkerScript('markersDB.js');\n")
            output.write("overviewer.util.injectMarkerScript('markers.js');\n")
            output.write("overviewer.util.injectMarkerScript('regions.js');\n")
            output.write("overviewer.collections.haveSigns=true;\n")

    def add_entities_from_chunk(self, chunk_entities: nbt.TAG_List):
        for entity in chunk_entities:
            had_return = False
            for entity_filter in all_filters:
                returned_entity = entity_filter(entity)
                if type(returned_entity) is FilterResult:
                    had_return = True
                    # print(f"\t\t\t{returned_entity}")
                    dict_key = f'G_{returned_entity.result_type.replace(" ", "_")}'
                    if dict_key in self.entities.keys():
                        self.entities[dict_key]["raw"].append(
                            {
                                "hovertext": returned_entity.result_type,
                                "text": returned_entity.hint
                                if not None
                                else returned_entity.result_type,
                                "x": get_coordinate(entity, "x"),
                                "y": get_coordinate(entity, "y"),
                                "z": get_coordinate(entity, "z"),
                            }
                        )
                    else:
                        self.entities[dict_key] = {
                            "name": returned_entity.result_type,
                            "created": False,
                            "raw": [
                                {
                                    "hovertext": returned_entity.result_type,
                                    "text": returned_entity.hint
                                    or returned_entity.result_type,
                                    "x": get_coordinate(entity, "x"),
                                    "y": get_coordinate(entity, "y"),
                                    "z": get_coordinate(entity, "z"),
                                }
                            ],
                        }
                elif type(returned_entity) is EmptyFilterResult:
                    had_return = True
                elif (
                    returned_entity is not None
                    and type(returned_entity) is not FilterResult
                ):
                    print(
                        f"!! Weird return from filters for {entity['id']} : {returned_entity}"
                    )
            if not had_return:
                if str(entity["id"]) in self.unmapped.keys():
                    self.unmapped[str(entity["id"])] += 1
                else:
                    self.unmapped[str(entity["id"])] = 1
