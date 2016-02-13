class Vertex:

	""" 
	Vertex {
		index, 
		latitude, 
		longitude, 
		altitude,  
	}
	
	"""

	def __init__(self):
		self.attributes = []

class PolygonParser:

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
				count = 0
				for val in line:
					try:
						val = float(val)
						vertex.attributes.insert(count, val)
						count = count + 1
					except:
						continue
				self.vertices.append(vertex)
			else:
				break
		file_in.close()

if __name__ == '__main__':
	p = PolygonParser()
	p.parse('isep.txt')