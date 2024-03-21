import enum


class _StringTypes(enum.Enum):
    RAW = enum.auto()
    STRING = enum.auto()


class ConfigParser:
    def __init__(self):
        # Key is the opening, and the value is the closing
        self._multiline_openings = {
            '"""': '"""',
            "'''": "'''",
            "[": "]",
            "{": "}",
            "(": ")"
        }

        self._escape_code_string_lookup = {
            "\\n": "\n",
            "\\t": "\t",
            "\\r": "\r"
        }

    def read(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            self._read_hierarchy = [i for i in f]

        self._remove_comments()
        self._flatten_split_lines()
        self._remove_escape_code()

        self._split_variables()

    @classmethod
    def _check_string(cls, var):
        if (var[:3] == "'''" and var[-3:] == "'''") or (var[0] == "'" and var[-1] == "'"):
            return _StringTypes.RAW
        elif (var[:3] == '"""' and var[-3:] == '"""') or (var[0] == '"' and var[-1] == '"'):
            return _StringTypes.STRING
        else:
            return False

    def _remove_escape_code(self):
        for i, k in zip(self._escape_code_string_lookup.keys(), self._escape_code_string_lookup.values()):
            for j, l in enumerate(self._read_hierarchy):
                if ConfigParser._check_string(l.split("=")[1].strip()) == _StringTypes.STRING:
                    self._read_hierarchy[j] = self._read_hierarchy[j].replace(i, k)

    def _remove_blank_lines(self):
        self._read_hierarchy = [i.rstrip(" ") for i in self._read_hierarchy if i != '' and i != "\n"]

    def _remove_comments(self):
        block_comment = False
        for i, k in enumerate(self._read_hierarchy):
            if block_comment:
                block_comment_end = k.find("*/")
                if block_comment_end != -1:
                    self._read_hierarchy[i] = k[block_comment_end + 2:]
                    block_comment = False
                else:
                    self._read_hierarchy[i] = ""
            else:
                block_comment_start = k.find("/*")
                if block_comment_start != -1:
                    block_comment_end = k.find("*/")
                    if block_comment_end != -1:
                        self._read_hierarchy[i] = k[:block_comment_start] + k[block_comment_end + 2:]
                    else:
                        block_comment = True
                        self._read_hierarchy[i] = k[:block_comment_start]
                else:
                    comment_index = k.find("//")
                    if comment_index != -1:
                        string_start, string_end = min(k.find('"'), k.find("'")), max(k.rfind('"'), k.rfind("'"))
                        if not string_start <= comment_index <= string_end:
                            self._read_hierarchy[i] = k[:comment_index]
        self._remove_blank_lines()

    def _flatten_split_lines(self):
        add = False
        add_index = 0
        multiline_string = False
        remove_whitespace = False
        remove_whitespace_change = False
        for i, k in enumerate(self._read_hierarchy):
            temp = k.rstrip("\n")
            if i < len(self._read_hierarchy):
                if (temp.rstrip("\\")[-3:] in self._multiline_openings.keys() or multiline_string) and temp[-1] == "\\":
                    remove_whitespace = True
                    remove_whitespace_change = True
                    k = temp.lstrip()[:-1]
            if add:
                if remove_whitespace and not remove_whitespace_change:
                    k = temp.lstrip()
                    if temp[-1] != "\\":
                        remove_whitespace = False
                    else:
                        k = k[:-1]  # Otherwise removes last of the 3 quotation marks
                if i + 1 < len(self._read_hierarchy):
                    if self._read_hierarchy[i + 1][-3:] in self._multiline_openings.values() or not multiline_string:
                        add_string = k.rstrip("\n")
                    else:
                        add_string = k
                else:
                    add_string = k
                if temp[-1] in self._multiline_openings.values() or temp[-3:] in self._multiline_openings.values():
                    add = False
                    multiline_string = False
                    add_string = k.rstrip("\n")
                self._read_hierarchy[add_index] += add_string
                self._read_hierarchy[i] = ""
            else:
                elems = k.split("=")
                if len(elems) == 2:
                    var = elems[1].lstrip(" ")
                    opening = None
                    line = self._read_hierarchy[i].rstrip("\n")
                    if remove_whitespace and remove_whitespace_change:
                        line = line[:-1]
                    if var[0] in self._multiline_openings.keys():
                        opening = var[0]
                        self._read_hierarchy[i] = line
                    elif var.rstrip("\\")[:3] in self._multiline_openings.keys():
                        opening = var.rstrip("/")[:3]
                        multiline_string = True
                        self._read_hierarchy[i] = line
                    if opening:
                        location = var.find(self._multiline_openings[opening])
                        if location <= 0:
                            add = True
                            add_index = i
            remove_whitespace_change = False
        self._remove_blank_lines()
        self._remove_trailing_whitespace()

    def _remove_trailing_whitespace(self):
        self._read_hierarchy = [i.rstrip("\n").rstrip(" ") for i in self._read_hierarchy]

    def _split_variables(self):
        temp = [i.split("=") for i in self._read_hierarchy]
        temp = [tuple(k.lstrip(" ").rstrip(" ") for k in i) for i in temp]
        self._hierarchy = dict()
        for var, val in temp:
            if (var[0] == var[-1] == "'" or
                    var[0] == var[-1] == "'"):
                var = var[1:-1]
            self._hierarchy[var] = val

    def output_configuration(self):
        for i, k in zip(self._hierarchy, self._hierarchy.values()):
            print(f"{i}: {k}")


configuration = ConfigParser()
configuration.read("basic-configuration-example.conf")

configuration.output_configuration()
