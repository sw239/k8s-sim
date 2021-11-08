#EndPoint objects associate a Pod with a Deployment and a Node.
#pod is the associated Pod.
#deploymentLabel is the label of the Deployment.
#microserviceLabel is the label of the microservices
#node is the associated Node

class EndPoint:

	def __init__(self, POD, MSLABEL, NODE,):
		self.pod = POD
		self.microserviceLabel = MSLABEL
		self.node = NODE
