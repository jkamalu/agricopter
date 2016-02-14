from shapely.geometry import Polygon

def parse(file_name):
	# list to build coordinates of polygon during creation
	coords = []
	file_in = open(file_name, 'r')
	file_in.readline()
	while True:
		line = file_in.readline()
		if line:
			# list to build coordinate of point during creation
			coord = []
			line = line.split('|')
			index = True
			for val in line:
				try:
					val = float(val)
					if index:
						index = False
						continue
					coord.append(val)
				except:
					continue
			coords.append(coord)
		else:
			break
	file_in.close()
	return Polygon(coords)

if __name__ == '__main__':
	print parse('isep.txt')