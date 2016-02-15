class Command:

	""" 
	Command { [
		index, 
		current_waypoint,
		coordinate_frame, 
		command_id, 
		var1 - Hold time in decimal seconds. (ignored by fixed wing, time to stay at MISSION for rotary wing),
		var2 - Acceptance radius in meters (if the sphere with this radius is hit, the MISSION counts as reached),
		var3 - 0 to pass through the WP, if > 0 radius in meters to pass by WP. Positive value for clockwise orbit, negative value for counter-clockwise orbit (allows trajectory control),
		var4 - Desired yaw angle at MISSION (rotary wing),
		latitude, 
		longitude, 
		altitude, 
		auto_continue 
	] }
	
	"""

	NUM_ATTRIBUTES = 11

	def __init__(self, command_id, latitude, longitude, altitude):
		self.attributes = [0, 0, command_id, 0, 0, 0, 0, latitude, longitude, altitude, 1]

class MissionGenerator:

	"""
	Utility class for creation of the mission .waypoints file.
	"""

	def __init__(self):
		self.commands = []

	def add_command(self, command, index=None):
		if index is None:
			self.commands.append(command)
		elif index >= 0 and index <= len(self.commands):
			self.commands.insert(index, command)
		else:
			print 'Out of bounds on call to add_command'

	def del_command(self, index=None):
		if index is None:
			del self.commands[len(self.commands) - 1]
		elif index >= 0 and index < len(self.commands):
			del self.commands[index]
		else:
			print 'Out of bounds on call to del_command'

	def export_to_file(self, file_name):
		output = 'QGC WPL 110\n'
		for i in range(0, len(self.commands)):
			output += '%s\t' % i
			for j in range(0, Command.NUM_ATTRIBUTES):
				output += '%s\t' % self.commands[i].attributes[j]
			output += '\n'
		file_out = open(file_name, 'w')
		file_out.write(output)
		file_out.close()