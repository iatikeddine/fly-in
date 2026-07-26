from typing import List, Set, Dict, Any


class Parsing:
    def __init__(self) -> None:
        self.nb_drones = 0
        self.line_number: int = 0
        self.zones: Dict = {}
        self.connections: Dict = {}
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
            return to_extract
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

    def validate_zone(self, config: List[str]):
        if len(config) != 4:
            raise ValueError("Error: invalid number of arguments - "
                             f"line {self.line_number}")
        for i in range(1, 4):
            if i == 1:
                self.validate_name(config[i])
            else:
                self.validate_x_y(config[i],)
        name = config[1]
        x = int(config[2])
        y = int(config[3])
        return name, x, y

    def validate_zone_tag(self, tag: List[str], tags_data: Dict[str, Any]) -> None:
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

    def validate_connection_tag(self, tag, tags_data):
        key = tag[0]
        value = tag[1]
        if key != "max_link_capacity":
            raise ValueError(f"Error: {key} is not a valid metadata for connection"
                             f" - line {self.line_number}")
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f"Error: {value} is not a valid number"
                             f" - line {self.line_number}")
        if value < 1:
            raise ValueError(f"Error: {value} is not a postive number"
                             f" - line {self.line_number}")
        tags_data[key] = value

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
            if type == "zone":
                self.validate_zone_tag(tag, tags_data)
            else:
                self.validate_connection_tag(tag, tags_data)
        return tags_data

    def save_zone(self, name: str, x: int, y: int, tags_data: Dict, prefix: str) -> None:
        data = {"type": prefix, "x": x, "y": y, "meta_data": tags_data}
        self.zones[name] = data

    def validate_connection(self, config: List):
        path = config[0].split('-')
        if len(path) != 2:
            raise ValueError("Error: invalid name for connection"
                             f" - line {self.line_number}")
        zone_1, zone_2 = path
        if zone_1 not in self.zones:
            raise ValueError(f"Error: {zone_1} is not a valid existing zone name"
                             f" - line {self.line_number}")
        if zone_2 not in self.zones:
            raise ValueError(f"Error: {zone_2} is not a valid existing zone name"
                             f" - line {self.line_number}")
        form_1 = zone_1 + '-' + zone_2
        form_2 = zone_2 + '-' + zone_1
        if form_1 in self.connections or form_2 in self.connections:
            raise ValueError(f"Error: {form_1} is a duplicated connecttions"
                             f" - line {self.line_number}")
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
                    full_bracket = f"[{meta_data}"
                    line = line.replace(full_bracket, "").strip()
                    meta_data = meta_data.strip(']')
                    if not line:
                        raise ValueError(f"Error: invalid data - "
                                         f"line {self.line_number}")
                config: List[str] = line.split()
                prefix = config[0].strip(':')
                if prefix in ["start_hub", "end_hub", "hub"]:
                    name, x, y = self.validate_zone(config)
                    tags_data = self.validate_meta_data(meta_data, "zone")
                    self.check_zone(prefix)
                    self.save_zone(name, x, y, tags_data, prefix)
                elif prefix == "connection":
                    src_dst = self.validate_connection(config[1:])
                    tags_data = self.validate_meta_data(meta_data, "connection")
                    self.connections[src_dst] = tags_data
                else:
                    raise ValueError(f"Error: {prefix} is an invalid zone "
                                     f"type - line {self.line_number}")
            if self.start_hub_count == 0:
                raise ValueError("Error: start hub not provided"
                                    f" - line {self.line_number}")
            elif self.end_hub_count == 0:
                raise ValueError("Error: end hub not provided"
                                    f" - line {self.line_number}")
            elif self.start_hub_count > 1:
                raise ValueError("Error: duplicated start hub"
                                    f" - line {self.line_number}")
            elif self.end_hub_count > 1:
                raise ValueError("Error: duplicated end hub"
                                    f" - line {self.line_number}")


if __name__ == "__main__":
    try:
        parser = Parsing()
        parser.process_file("maps/easy/03_basic_capacity.txt")
        print(parser.zones)
        print(parser.connections)
    except Exception as e:
        print(e)