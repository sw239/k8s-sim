#Deployment objects set the configuration and expected number of Pod objects
#deploymentLabel is the label associated with the deployment.
#currentReplicas is the number of pods currently running that are associated with 
#the Deployment.
#expectedReplicas is the setpoint for the number of pods.
#cpuCost is the amount of cpu that a pod must be assigned.
import threading

class DeploymentGraphInfo:
	def __init__(self):
		self.deploymentLabel = ''
		self.requests = [[],[]]
		self.microservices = []
	
class MicroserviceGraphInfo:
	def __init__(self, LABEL):
		self.label = LABEL
		self.activeList = []
		self.pendingList = []
		self.crashedList = []
		self.expectedList = []
		self.utilList = []
		self.setpointList = []
			
class NodeGraphInfo:
	def __init__(self):
		self.label = ''
		self.cpuList = []
		self.activePodList = []
		self.pendingPodList = []
		self.crashedPodList = []