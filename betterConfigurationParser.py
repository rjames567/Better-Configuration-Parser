class ConfigParser:
	def __init__(self):
		pass

	def read(self, filename):
		with open(filename, 'r') as f:
			self._heirachy =  [i.rstrip("\n") for i in f.readlines()]

		self._remove_comments()

	def _remove_blank_lines(self):
		self._heirachy = [i.rstrip(" ").lstrip(" ").lstrip("\t") for i in self._heirachy if i != '']
			
	def _remove_comments(self):
		for i, k in enumerate(self._heirachy):
			comment_index = k.find("//")
			if comment_index != -1:
				string_start, string_end = min(k.find('"'), k.find("'")), max(k.rfind('"'), k.rfind("'"))
				if not string_start <= comment_index <= string_end:
					self._heirachy[i] = k[:comment_index]
		self._remove_blank_lines()

configuration = ConfigParser()
configuration.read("basic-configuration-example.conf")
