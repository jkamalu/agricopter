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