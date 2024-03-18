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
			self._heirachy =  [i.rstrip("\n") for i in f.readlines()]

		self._remove_comments()
		self._flatten_split_lines()

	def _remove_blank_lines(self):
		self._heirachy = [i.rstrip(" ").lstrip(" ").lstrip("\t") for i in self._heirachy if i != '']
			
	def _remove_comments(self):
		block_comment = False
		for i, k in enumerate(self._heirachy):
			if block_comment:
				block_comment_end = k.find("*/")
				if block_comment_end != -1:
					self._heirachy[i] = k[block_comment_end+2:]
					block_comment = False
				else:
					self._heirachy[i] = ""
			else:
				block_comment_start = k.find("/*")
				if block_comment_start != -1:
					block_comment_end = k.find("*/")
					if block_comment_end != -1:
						self._heirachy[i] = k[:block_comment_start] + k[block_comment_end+2:]
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
		for i, k in enumerate(self._heirachy):
			if add:
				self._heirachy[add_index] += k
				self._heirachy[i] = ""
				if k[-1] in self._multiline_openings.values() or k[-3:] in self._multiline_openings.values():
					add = False
			else:
				elems = k.split("=")
				if len(elems):
					var = elems[1].lstrip(" ")
					opening = None
					if var[0] in self._multiline_openings.keys():
						opening = var[0]
					elif var[:3] in self._multiline_openings.keys():
						opening = var[:3]
					if opening:
						location = var.find(self._multiline_openings[opening])
						if location <= 0:
							add = True
							add_index = i
		self._remove_blank_lines()

configuration = ConfigParser()
configuration.read("basic-configuration-example.conf")
