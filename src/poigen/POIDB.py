import json
from pathlib import Path

from nbt import nbt

from poigen.filterclass import EmptyFilterResult, FilterResult
from poigen.filters import all_filters
from poigen.helpers import get_coordinates


class POIDB:
    def __init__(self, world_name: str):
        self.entities = {}
        self.unmapped = {}
        self.world_name = world_name
        self._counter = 0

    @property
    def counter(self):
        self._counter += 1
        return self._counter

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
            retstr += f"\n\t{len(self.entities[k]['markers'])}x {k}"
        return retstr

    def write_output(self, render_dir):
        with open(Path(render_dir, f"{self.world_name}_markers.json"), "w") as output:
            json.dump(self.entities, output, sort_keys=True, indent=2)

    def add_entities_from_chunk(self, chunk_entities: nbt.TAG_List):
        for entity in chunk_entities:
            had_return = False
            for entity_filter in all_filters:
                returned_entity = entity_filter(entity)
                if type(returned_entity) is FilterResult:
                    had_return = True
                    # print(f"\t\t\t{returned_entity}")
                    dict_key = (
                        f'{returned_entity.result_type.replace(" ", "_")}-marker-set'
                    )

                    marker_uuid = f"{returned_entity.result_type}-{self.counter}"
                    new_marker = {
                        "type": "poi",
                        "position": get_coordinates(entity),
                        "label": returned_entity.result_type,
                        # optional:
                        "icon": f"assets/marker/{returned_entity.result_type.lower().replace(" ","_")}.png",
                        # other stuff we could add: anchor, sorting, listed, classes (css), min-distance, max-distance
                    }
                    if returned_entity.hint is not None:
                        new_marker["detail"] = returned_entity.hint

                    if dict_key in self.entities.keys():
                        self.entities[dict_key]["markers"][marker_uuid] = new_marker
                    else:
                        self.entities[dict_key] = {
                            "label": returned_entity.result_type,
                            "toggleable": True,
                            "default-hidden": True,
                            "sorting": 10,
                            "markers": {marker_uuid: new_marker},
                        }
                elif type(returned_entity) is EmptyFilterResult:
                    had_return = True
                elif (
                    returned_entity is not None
                    and type(returned_entity) is not FilterResult
                ):
                    print(
                        f"!! {self.world_name} Weird return from filters for {entity['id']} : {returned_entity}"
                    )
            if not had_return:
                if str(entity["id"]) in self.unmapped.keys():
                    self.unmapped[str(entity["id"])] += 1
                else:
                    self.unmapped[str(entity["id"])] = 1

    def add_entities_from_json(self, json_data):
        print(f"[{self.world_name}] Adding entities from JSON")
        for entity_type in json_data:
            print(
                f"[{self.world_name}] Adding {len(json_data[entity_type])} entities of type {entity_type} from JSON"
            )
            dict_key = f'{entity_type.replace(" ", "_")}-marker-set'
            for entity in json_data[entity_type]:
                marker_uuid = f"{entity_type}-{entity}-{self.counter}"
                new_marker = {
                    "type": "poi",
                    "position": json_data[entity_type][entity],
                    "label": entity,
                    # optional:
                    "icon": f"assets/marker/{entity_type.lower().replace(" ","_")}.png",
                    # other stuff we could add: anchor, sorting, listed, classes (css), min-distance, max-distance
                }
                if dict_key in self.entities.keys():
                    self.entities[dict_key]["markers"][marker_uuid] = new_marker
                else:
                    self.entities[dict_key] = {
                        "label": entity_type,
                        "toggleable": True,
                        "default-hidden": True,
                        "sorting": 0,
                        "markers": {marker_uuid: new_marker},
                    }
