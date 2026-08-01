from typing import List, Dict, Any, Tuple, Set, Union


class Parsing:
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.line_number: int = 0
        self.zones: Dict[str, Dict[str, Any]] = {}
        self.connections: Dict[str, Union[int, None]] = {}
        self.start_hub_count: int = 0
        self.end_hub_count: int = 0
        self.coordinates: Set[Tuple[int, int]] = set()
        self.is_first_line: bool = True

    def validate_first_line(self, line: str) -> int:
        if ':' not in line:
            raise ValueError(
                f"Error: line does not contain ':'\n"
                f"line {self.line_number} "
            )

        splited_line: List[str] = line.split(':', maxsplit=1)
        if splited_line[0] != splited_line[0].strip():
            raise ValueError(
                "Error: key contains white space at the end\n"
                f"line: {self.line_number} "
            )
        if splited_line[0] != 'nb_drones':
            raise ValueError(
                "Error: line does not start with 'nb_drones'\n"
                f"line: {self.line_number}"
            )
        try:
            value: int = int(splited_line[1])
        except ValueError:
            raise ValueError(
                "Error: nb_drones is not a valid number\n"
                f"line: {self.line_number}"
            )
        if value < 1:
            raise ValueError(
                f"Error: number of drones is not positive\n"
                f"line {self.line_number}"
            )

        return value

    def extract_meta_data(self, line: str) -> str:
        splited_line: List[str] = line.split('[')
        if len(splited_line) > 1:
            to_extract: str = splited_line[len(splited_line) - 1]
            return to_extract

        return ""

    def validate_name(self, name: str) -> None:
        if '-' in name:
            raise ValueError(
                "Error: zone name contains an invalid dash\n"
                f"line {self.line_number}"
            )
        if ' ' in name:
            raise ValueError(
                "Error: zone name contains an invalid space\n"
                f"line {self.line_number}"
            )
        if name in self.zones:
            raise ValueError(
                "Error: duplicated zone name not allowed\n"
                f"line {self.line_number}"
            )

    def validate_x_y(self, n: str) -> None:
        try:
            int(n)
        except ValueError:
            raise ValueError(
                f"Error: coordinate {n} is not a valid number\n"
                f"line {self.line_number}"
            )

    def validate_zone(self, config: List[str]) -> Tuple[str, int, int]:
        if len(config) != 4:
            raise ValueError(
                "Error: invalid number of arguments for zone\n"
                f"line {self.line_number}"
            )
        for i in range(1, 4):
            if i == 1:
                self.validate_name(config[i])
            else:
                self.validate_x_y(config[i])

        name: str = config[1]
        x: int = int(config[2])
        y: int = int(config[3])
        if (x, y) in self.coordinates:
            raise ValueError(
                "Error: zone coordinates should be unique\n"
                f"line {self.line_number}"
            )
        self.coordinates.add((x, y))

        return name, x, y

    def validate_zone_tag(
            self, tag: List[str],
            tags_data: Dict
    ) -> None:
        key: str = tag[0]
        value: str = tag[1]
        if key not in ["zone", "color", "max_drones"]:
            raise ValueError(
                f"Error: invalid meta data key {key}\n"
                f"line {self.line_number}"
            )
        v_zones: List[str] = ["normal", "blocked", "restricted", "priority"]
        if key == "zone" and value not in v_zones:
            raise ValueError(
                f"Error: {value} is not a valid zone\n"
                f"line {self.line_number}"
            )
        elif key == "color" and len(value.split()) != 1:
            raise ValueError(
                f"Error: color should be one word only\n"
                f"line {self.line_number}"
            )
        elif key == "max_drones":
            try:
                converted_value: int = int(value)
            except ValueError:
                raise ValueError(
                    f"Error: {value} is not a valid number\n"
                    f"line {self.line_number}"
                )
            if converted_value < 1:
                raise ValueError(
                    f"Error: {converted_value} is not a positive number\n"
                    f"line {self.line_number}"
                )
        if key == "max_drones":
            tags_data[key] = converted_value
        else:
            tags_data[key] = value

    def check_zone(self, zone_type: str) -> None:
        if zone_type == "start_hub":
            self.start_hub_count += 1
        if zone_type == "end_hub":
            self.end_hub_count += 1

    def validate_connection_tag(
            self, tag: List[str], tags_data: Dict
    ) -> None:
        key: str = tag[0]
        value: str = tag[1]
        if key != "max_link_capacity":
            raise ValueError(
                f"Error: {key} is not a valid metadata for connection\n"
                f"line {self.line_number}"
            )
        try:
            converted_value: int = int(value)
        except ValueError:
            raise ValueError(
                f"Error: {value} is not a valid number\n"
                f"line {self.line_number}"
            )
        if converted_value < 1:
            raise ValueError(
                f"Error: {converted_value} is not a positive number\n"
                f"line {self.line_number}"
            )
        tags_data[key] = converted_value

    def validate_meta_data(
            self, meta_data: str, type: str
    ) -> Dict:
        tags_data: Dict = {}
        if not meta_data:
            return tags_data
        tags: List[str] = meta_data.split()
        for tag in tags:
            splited_tag: List[str] = tag.split('=')
            if len(splited_tag) != 2:
                raise ValueError(
                    "Error: invalid meta data format\n"
                    f"line {self.line_number}"
                )
            if type == "zone":
                self.validate_zone_tag(splited_tag, tags_data)
            else:
                self.validate_connection_tag(splited_tag, tags_data)
        return tags_data

    def save_zone(
            self, name: str, x: int, y: int,
            tags_data: Dict, prefix: str
    ) -> None:

        data: Dict[str, Any] = {"type": prefix, "x": x,
                                "y": y, "meta_data": tags_data}
        self.zones[name] = data

    def validate_connection(self, config: List[str]) -> str:
        if not config or len(config) != 1:
            raise ValueError(
                "Error: invalid connection data\n"
                f"line {self.line_number}"
            )
        path: List[str] = config[0].split('-')
        if len(path) != 2:
            raise ValueError(
                "Error: invalid connection pair format 'zoneA-zoneB'\n"
                f"line {self.line_number}"
            )
        zone_1: str = path[0]
        zone_2: str = path[1]
        if zone_1 == zone_2:
            raise ValueError(
                "Error: self connections are not allowed\n"
                f"line {self.line_number}"
            )
        if zone_1 not in self.zones:
            raise ValueError(
                f"Error: {zone_1} is not a valid existing zone name\n"
                f"line {self.line_number}"
            )
        if zone_2 not in self.zones:
            raise ValueError(
                f"Error: {zone_2} is not a valid existing zone name\n"
                f"line {self.line_number}"
            )
        form_1: str = f"{zone_1}-{zone_2}"
        form_2: str = f"{zone_2}-{zone_1}"
        if form_1 in self.connections or form_2 in self.connections:
            raise ValueError(
                f"Error: {form_1} is a duplicated connections\n"
                f"line {self.line_number}"
            )
        return form_1

    def process_file(self, path: str) -> None:
        with open(path, "r") as f:
            for line in f:
                self.line_number += 1
                line = line.strip()
                if not line or line[0] == '#':
                    continue
                if '#' in line:
                    line = line.split('#')[0].strip()
                if self.is_first_line:
                    self.nb_drones = self.validate_first_line(line)
                    self.is_first_line = False
                    continue
                meta_data: str = self.extract_meta_data(line)
                if meta_data:
                    full_bracket: str = f"[{meta_data}"
                    line = line.replace(full_bracket, "").strip()
                    meta_data = meta_data.strip(']')
                    if not line:
                        raise ValueError(
                            f"Error: invalid data\n"
                            f"line {self.line_number}"
                        )
                config: List[str] = line.split()
                if not config[0].endswith(':'):
                    raise ValueError(
                        "Error: invalid prefix does not contain ':'\n"
                        f"line {self.line_number}"
                    )
                prefix: str = config[0].strip(':')
                if prefix in ["start_hub", "end_hub", "hub"]:
                    name, x, y = self.validate_zone(config)
                    tags_data: Dict = self.validate_meta_data(
                        meta_data, "zone")
                    self.check_zone(prefix)
                    self.save_zone(name, x, y, tags_data, prefix)
                elif prefix == "connection":
                    src_dst: str = self.validate_connection(config[1:])
                    tags_data = self.validate_meta_data(
                        meta_data, "connection"
                    )
                    if not tags_data:
                        self.connections[src_dst] = None
                    else:
                        self.connections[src_dst] = tags_data[
                            "max_link_capacity"
                        ]
                else:
                    raise ValueError(
                        f"Error: {prefix} is an invalid zone type\n"
                        f"line {self.line_number}"
                    )
        if self.start_hub_count == 0:
            raise ValueError(
                "Error: start hub not provided\n"
                "start hub line"
            )
        elif self.end_hub_count == 0:
            raise ValueError(
                "Error: end hub not provided\n"
                "end hub line"
            )
        elif self.start_hub_count > 1:
            raise ValueError(
                "Error: duplicated start hub\n"
                f"line {self.line_number}"
            )
        elif self.end_hub_count > 1:
            raise ValueError(
                "Error: duplicated end hub\n"
                f"line {self.line_number}"
            )
