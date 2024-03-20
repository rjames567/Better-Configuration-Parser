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

    def read(self, filename):
        with open(filename, 'r') as f:
            self._heirachy = [i for i in f.readlines()]

        self._remove_comments()
        self._flatten_split_lines()
        self._split_variables()

    def _remove_blank_lines(self):
        self._heirachy = [i.rstrip(" ").lstrip(" ").lstrip("\t") for i in self._heirachy if i != '' and i != "\n"]

    def _remove_comments(self):
        block_comment = False
        for i, k in enumerate(self._heirachy):
            if block_comment:
                block_comment_end = k.find("*/")
                if block_comment_end != -1:
                    self._heirachy[i] = k[block_comment_end + 2:]
                    block_comment = False
                else:
                    self._heirachy[i] = ""
            else:
                block_comment_start = k.find("/*")
                if block_comment_start != -1:
                    block_comment_end = k.find("*/")
                    if block_comment_end != -1:
                        self._heirachy[i] = k[:block_comment_start] + k[block_comment_end + 2:]
                    else:
                        block_comment = True
                        self._heirachy[i] = k[:block_comment_start]
                else:
                    comment_index = k.find("//")
                    if comment_index != -1:
                        string_start, string_end = min(k.find('"'), k.find("'")), max(k.rfind('"'), k.rfind("'"))
                        if not string_start <= comment_index <= string_end:
                            self._heirachy[i] = k[:comment_index]
        self._remove_blank_lines()

    def _flatten_split_lines(self):
        add = False
        add_index = 0
        multiline_string = False
        for i, k in enumerate(self._heirachy):
            if add:
                temp = k.rstrip("\n")
                if i + 1 < len(self._heirachy):
                    if self._heirachy[i + 1][:3] in self._multiline_openings.values() or not multiline_string:
                        add_string = k.rstrip("\n")
                    else:
                        add_string = k
                else:
                    add_string = k
                self._heirachy[i] = ""
                if temp[-1] in self._multiline_openings.values() or temp[-3:] in self._multiline_openings.values():
                    add = False
                    multiline_string = False
                    add_string = k.rstrip("\n")
                self._heirachy[add_index] += add_string
            else:
                elems = k.split("=")
                if len(elems) == 2:
                    var = elems[1].lstrip(" ")
                    opening = None
                    if var[0] in self._multiline_openings.keys():
                        opening = var[0]
                        self._heirachy[i] = self._heirachy[i].rstrip("\n")
                    elif var[:3] in self._multiline_openings.keys():
                        opening = var[:3]
                        multiline_string = True
                        self._heirachy[i] = self._heirachy[i].rstrip("\n")
                    if opening:
                        location = var.find(self._multiline_openings[opening])
                        if location <= 0:
                            add = True
                            add_index = i
        self._remove_blank_lines()
        self._remove_trailing_whitespace()

    def _remove_trailing_whitespace(self):
        self._heirachy = [i.rstrip("\n").rstrip(" ") for i in self._heirachy]

    def _split_variables(self):
        self._processed_heirachy = [i.split("=") for i in self._heirachy]
        self._processed_heirachy = [tuple(k.lstrip(" ").rstrip(" ") for k in i) for i in self._processed_heirachy]


configuration = ConfigParser()
configuration.read("basic-configuration-example.conf")
