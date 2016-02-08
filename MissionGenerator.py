class Command:

	NUM_ATTRIBUTES = 11

	def __init__(self, command_id, latitude, longitude, altitude):
		self.attributes = [0, 0, command_id, 0, 0, 0, 0, latitude, longitude, altitude, 1]
	
	"""
	index, 
	unknown1, unknown2, 
	command_id, 
	var1, var2, var3, var4, 
	latitude, longitude, altitude, 
	auto_continue
	
	"""		

class MissionGenerator:

	def __init__(self):
		self.commands = []

	def add_command(self, command, index=None):
		if index is None:
			self.commands.append(command)
		elif index >= 0 and index <= len(self.commands):
			self.commands.insert(index, command)
		else:
			print 'OOB on call to add_command'

	def del_command(self, index=None):
		if index is None:
			del self.commands[len(self.commands) - 1]
		elif index >= 0 and index < len(self.commands):
			del self.commands[index]
		else:
			print 'OOB on call to del_command'

	def export_to_file(self, file_name):
		fo = open(file_name, 'w')
		fo.write('QGC WPL 110\n')
		for i in range(0, len(self.commands)):
			fo.write(str(i))
			fo.write('\t')
			for j in range(0, Command.NUM_ATTRIBUTES):
				fo.write(str(self.commands[i].attributes[j]))
				fo.write('\t')
			fo.write('\n')
		fo.close()

if __name__ == '__main__':
	cmd = Command('16', '9', '17', '13')
	# cmf = Command('lint', 'borwnerw', 'qazasxzabbbsxz', 'ragsmack')
	# cmg = Command('flint', '09029239', '2342342', 'nincompoop')
	# cmh = Command('bint', 'ccs,0909,0s', '4', 'porkins')	
	mg = MissionGenerator()
	mg.add_command(cmd);
	# mg.add_command(cmf)
	# mg.del_command(0)
	# mg.add_command(cmd)
	# mg.add_command(cmg, 0)
	# mg.add_command(cmh, 1)
	mg.export_to_file('boobs.waypoints')