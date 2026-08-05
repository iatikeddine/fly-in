from typing import List, Dict, Any, Tuple, Set, Union


class Parsing:
    """Parse and validate a Fly-in zone/connection map file.

    Reads data describing drone zones (``start_hub``, ``end_hub``,
    ``hub``) and the connections between them, validating syntax and
    semantics line by line and accumulating the results into
    ``self.zones`` and ``self.connections``.
    """
    def __init__(self) -> None:
        """Initialize parser state.

        Sets up empty state for parsed zones and connections, resets
        the start/end hub counters and the seen-coordinates set, and marks
        that the first line (the ``nb_drones`` header) has not yet been
        read.
        """
        self.nb_drones: int = 0
        self.line_number: int = 0
        self.zones: Dict[str, Dict[str, Any]] = {}
        self.connections: Dict[str, Union[int, None]] = {}
        self.start_hub_count: int = 0
        self.end_hub_count: int = 0
        self.coordinates: Set[Tuple[int, int]] = set()
        self.is_first_line: bool = True

    def validate_first_line(self, line: str) -> int:
        """Validate the mandatory ``nb_drones: <value>`` line.

        :param line: The raw first non-empty line of the file.
        :return: The parsed, positive number of drones.
        :raises ValueError: If the line is malformed, is not the
            ``nb_drones`` key, or its value is not a positive integer.
        """

        if ':' not in line:
            raise ValueError(
                f"Error: ivalid first line format\n"
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
        """Extract the bracketed metadata from a zone/connection line.

        :param line: The raw line.
        :return: The content of the meta data, or an empty string
            if the line has no metadata block.
        """
        reved_line: str = line[::-1]
        if not reved_line.startswith(']'):
            return ""
        if '[' not in reved_line:
            return ""
        to_extract: str = ""
        for c in reved_line:
            if c == '[':
                to_extract += '['
                break
            to_extract += c
        line = line.removesuffix(to_extract[::-1])
        if not line:
            return to_extract[::-1]
        if not line.endswith(' '):
            return ""

        return to_extract[::-1]

    def validate_name(self, name: str) -> None:
        """Validate that a zone name is well-formed and unique.

        :param name: The candidate zone name.
        :raises ValueError: If the name contains a dash or a space, or
            if it duplicates an already-registered zone name.
        """

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
        """Validate that a coordinate token is a valid integer.

        :param n: The raw coordinate string.
        :raises ValueError: If ``n`` cannot be parsed as an integer.
        """

        try:
            int(n)
        except ValueError:
            raise ValueError(
                f"Error: coordinate {n} is not a valid number\n"
                f"line {self.line_number}"
            )

    def validate_zone(self, config: List[str]) -> Tuple[str, int, int]:
        """Validate a zone declaration's fields and extract its data.

        :param config: The whitespace-split tokens of the zone line,
            expected as ``[prefix, name, x, y]``.
        :return: A ``(name, x, y)`` tuple for the validated zone.
        :raises ValueError: If the argument count is wrong, the name or
            coordinates are invalid, or the coordinates are already
            taken by another zone.
        """

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
            tags_data: Dict[str, Any]
    ) -> None:
        """Validate a single ``key=value`` zone metadata tag and store it.

        :param tag: A two-element ``[key, value]`` pair split from a
            metadata token.
        :param tags_data: The dict of already-validated tags for the
            current zone; updated in place with the new tag.
        :raises ValueError: If the key is not a recognized zone tag, or
            the value is invalid for that key (unknown zone type,
            multi-word color, or non-positive ``max_drones``).
        """

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
        if key in tags_data:
            raise ValueError(
                "Error: duplicated zone metadata\n"
                f"line {self.line_number}"
            )
        if key == "max_drones":
            tags_data[key] = converted_value
        else:
            tags_data[key] = value

    def check_zone(self, zone_type: str) -> None:
        """Marks start/end hub occurrences for later checks.

        :param zone_type: The zone prefix, e.g. "start_hub",
            "end_hub", or "hub".
        """

        if zone_type == "start_hub":
            self.start_hub_count += 1
        if zone_type == "end_hub":
            self.end_hub_count += 1

    def validate_connection_tag(
            self, tag: List[str], tags_data: Dict[str, Any]
    ) -> None:
        """Validate a single ``key=value`` connection metadata tag.

        :param tag: A two-element ``[key, value]`` pair split from a
            metadata token.
        :param tags_data: The dict of already-validated tags for the
            current connection; updated in place with the new tag.
        :raises ValueError: If the key is not ``max_link_capacity``, or
            its value is not a positive integer.
        """

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
        if key in tags_data:
            raise ValueError(
                "Error: duplicated connection metadata\n"
                f"line {self.line_number}"
            )
        tags_data[key] = converted_value

    def validate_meta_data(
            self, meta_data: str, type: str
    ) -> Dict[str, Any]:
        """Parse and validate a whitespace-separated metadata block.

        Splits the raw ``key=value`` string into
        individual tags and dispatches each to the zone or connection
        tag validator depending on ``type``.

        :param meta_data: The raw metadata string (without brackets),
            or an empty string if none was present.
        :param type: Either ``"zone"`` or ``"connection"``, selecting
            which validator handles each tag.
        :return: A dict mapping validated tag keys to their converted
            values.
        :raises ValueError: If any tag is not in ``key=value`` format,
            or fails validation in the delegated validator.
        """

        tags_data: Dict[str, Any] = {}
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
            tags_data: Dict[str, Any], prefix: str
    ) -> None:
        """Store a validated zone's data in ``self.zones``.

        :param name: The zone's unique name.
        :param x: The zone's x coordinate.
        :param y: The zone's y coordinate.
        :param tags_data: The zone's validated metadata tags.
        :param prefix: The zone's declaration type (``"start_hub"``,
            ``"end_hub"``, or ``"hub"``).
        """

        data: Dict[str, Any] = {"type": prefix, "x": x,
                                "y": y, "meta_data": tags_data}
        self.zones[name] = data

    def validate_connection(self, config: List[str]) -> str:
        """Validate a ``zoneA-zoneB`` connection pair.

        :param config: The single-element list containing the raw
            ``"zoneA-zoneB"`` token.
        :return: The canonical ``"zoneA-zoneB"`` key to store the
            connection under.
        :raises ValueError: If the token is missing or malformed, if
            it connects a zone to itself, if either zone name is
            unknown, or if the connection (in either direction) is
            already registered.
        """

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
        """Parse an entire Fly-in map file and populate the parser state.

        Reads the file line by line, skipping blanks and comments,
        validates the ``nb_drones`` header first, then dispatches each
        remaining line to zone or connection validation depending on
        its prefix. After the full file is read, checks that exactly
        one ``start_hub`` and one ``end_hub`` were declared.

        :param path: path to the map file.
        :raises ValueError: If any line fails validation, if the
            prefix is not one of ``start_hub``/``end_hub``/``hub``/
            ``connection``, or if the start/end hub counts are not
            each exactly one.
        """

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
                    line = line.removesuffix(meta_data).strip()
                    meta_data = meta_data.strip('[]')
                    if not line:
                        raise ValueError(
                            f"Error: line contains only metadata\n"
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
                    tags_data: Dict[str, Any] = self.validate_meta_data(
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
                "start hub line"
            )
        elif self.end_hub_count > 1:
            raise ValueError(
                "Error: duplicated end hub\n"
                "end hub line"
            )
        if not self.connections:
            raise ValueError(
                "Error: there is no connections between zones"
                "connection line"
            )
