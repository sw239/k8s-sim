#The WorkerNode is the object to which pods can be scheduled
#label is the label of the Node
#assigned_cpu is the amount of cpu assigned to the node
#available_cpu is the amount of assigned_cpu not currently in use
#status communicates the Node's availability. ['UP', 'CRASHED', 'TERMINATING', 'TERMINATED']

class WorkerNode:


	def __init__(self, INFOLIST):
		self.label = INFOLIST[0]
		self.assigned_cpu = int(INFOLIST[1])
		self.available_cpu = int(INFOLIST[1])
		self.status = 'UP'
