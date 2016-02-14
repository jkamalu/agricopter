class Vertex:

	""" 
	Vertex { [
		index, 
		latitude, 
		longitude, 
		altitude,  
	] }
	
	"""

	def __init__(self):
		self.attributes = []

class PolygonParser:

	"""
	Utility class to generate original polygon from input file.
	"""

	def __init__(self):
		self.vertices = []

	def parse(self, file_name):
		file_in = open(file_name, 'r')
		file_in.readline()
		while True:
			line = file_in.readline()
			if line:
				line = line.split('|')
				vertex = Vertex()
				for val in line:
					try:
						val = float(val)
						vertex.attributes.append(count)
					except:
						continue
				self.vertices.append(vertex)
			else:
				break
		file_in.close()

	def get_polygon(self):
		return self.vertices

if __name__ == '__main__':
	p = PolygonParser()
	p.parse('isep.txt')
	print p.get_polygon()