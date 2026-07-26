from typing import List, Set, Dict, Any


class Parsing:
    def __init__(self) -> None:
        self.line_number: int = 0
        self.zones: Dict = {}
        self.connections: Set = set()
        self.start_hub_count: int = 0
        self.end_hub_count: int = 0
        self.is_first_line: bool = True

    def validate_first_line(self, line: str) -> int:
        if ':' not in line:
            raise ValueError(f"Error: line does not contain ':' "
                             f"- line {self.line_number} ")
        splited_line: List[str] = line.split(':', maxsplit=1)
        if splited_line[0] != splited_line[0].strip():
            raise ValueError("Error: key contains white space at the end - "
                             f"line: {self.line_number} ")
        if splited_line[0] != 'nb_drones':
            raise ValueError("Error: line does not start with 'nb_drones' "
                             f"- line: {self.line_number}")
        try:
            value: int = int(splited_line[1])
        except ValueError:
            raise ValueError("Error: value of number of nb_drones "
                             f"is not a valid number - line: {self.line_number}")
        if value < 1:
            raise ValueError(f"Error: number of drones is not positive - "
                             f"line {self.line_number}")
        return value

    def extract_meta_data(self, line: str) -> str:
        splited_line: List[str] = line.split('[')
        if len(splited_line) > 1:
            to_extract: str = splited_line[len(splited_line) - 1]
            return to_extract.strip('[]')
        return ""

    def validate_name(self, name: str) -> None:
        if '-' in name:
            raise ValueError("Error: zone name contains a dash'"
                             f" - line {self.line_number}")
        if ' ' in name:
            raise ValueError("Error: zone name contains a space"
                             f" - line {self.line_number}")
        if name in self.zones:
            raise ValueError("Error: duplicated zone name - line"
                             f"{self.line_number}")

    def validate_x_y(self, n: str) -> None:
        try:
            int(n)
        except ValueError:
            raise ValueError(f"Error: coordinated {n} is not a valid "
                             f"number - line {self.line_number}")

    def validate_zone(self, zone_args: List[str]):
        if len(zone_args) != 4:
            raise ValueError("Error: invalid number of arguments - "
                             f"line {self.line_number}")
        for i in range(1, 4):
            if i == 1:
                self.validate_name(zone_args[i])
            else:
                self.validate_x_y(zone_args[i],)
        name = zone_args[1]
        x = int(zone_args[2])
        y = int(zone_args[3])
        return name, x, y

    def validate_tag(self, tag: List[str], tags_data: Dict[str, Any]) -> None:
        key = tag[0]
        value = tag[1]
        if key not in ["zone", "color", "max_drones"]:
            raise ValueError(f"Error: invalid tag key {key}"
                             f" - line {self.line_number}")
        valid_zones = ["normal", "blocked", "restricted", "priority"]
        if key == "zone" and value not in valid_zones:
            raise ValueError(f"Error: {value} is not a valid zone"
                             f" - line {self.line_number}")
        elif key == "color" and len(value.split()) != 1:
            raise ValueError(f"Error: {value} is not valid"
                             f" - line {self.line_number}")
        elif key == "max_drones":
            try:
                value = int(value)
            except ValueError:
                raise ValueError(f"Error: {value} is not a valid number"
                                 f" - line {self.line_number}")
            if value < 1:
                raise ValueError(f"Error: {value} is not a positive "
                                 f"number - line {self.line_number}")
        tags_data[key] = value

    def check_zone(self, zone_type: str) -> None:
        if zone_type == "start_hub":
            self.start_hub_count += 1
        if zone_type == "end_hub":
            self.end_hub_count += 1

    def validate_meta_data(self, meta_data: str, type: str):
        tags_data = {}
        if not meta_data:
            return tags_data
        tags: List[str] = meta_data.split()
        for tag in tags:
            tag = tag.split('=')
            if len(tag) != 2:
                raise ValueError("Error: invalid meta data - line "
                                 f"{self.line_number}")
            self.validate_tag(tag, tags_data)
        return tags_data

    def save_zone(self, name: str, x: int, y: int, tags_data: Dict, prefix: str) -> None:
        data = {"type": prefix, "x": x, "y": y, "meta_data": tags_data}
        self.zones[name] = data

    def process_file(self, path: str) -> None:
        with open(path, "r") as f:
            for line in f:
                self.line_number += 1
                line = line.strip()
                if not line or line[0] == '#':
                    continue
                if '#' in line:
                    line = line.split('#')[0]
                if self.is_first_line:
                    self.validate_first_line(line)
                    self.is_first_line = False
                    continue
                meta_data: str = self.extract_meta_data(line)
                if meta_data:
                    line = line.replace(meta_data, "")
                    if not line:
                        raise ValueError(f"Error: invalid data - "
                                         f"line {self.line_number}")
                rest: List[str] = line.split()
                prefix = rest[0]
                if prefix in ["start_hub", "end_hub", "hub"]:
                    name, x, y = self.validate_zone(rest)
                    tags_data = self.validate_meta_data(meta_data, "zone")
                    self.check_zone(prefix)
                    self.save_zone(name, x, y, tags_data, prefix)
                elif prefix == "connection":
                    pass
                else:
                    raise ValueError(f"Error: {prefix} is an invalid zone "
                                     f"type - line {self.line_number}")
