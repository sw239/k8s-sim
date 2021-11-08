#Microservice objects describe pod information
#Microservice templates are created, from which microservice objects are created and associated with deployments.
#microserviceLabel is the identifying label of the microservice
#deploymentLabel is the label of the associated deployment. When intially created as a template, this is empty.
#currentReplicas are the current number of pod replicas for the microservice and deployment
#expectedReplics is the expected number of pod replicas
#handlingTime is the duration taken to handle requests
#cpuCost is the cost of deploying a microservice pod onto a node
import threading

class Microservice:
	def __init__(self, INFOLIST):
		self.microserviceLabel = INFOLIST[0]
		self.deploymentLabel = ''
		self.currentReplicas = 0
		self.expectedReplicas = 1
		self.handlingTime = int(INFOLIST[2])
		self.cpuCost = int(INFOLIST[1])
