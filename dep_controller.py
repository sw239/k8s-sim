from api_server import APIServer
import threading
import time


#DepController is a control loop that creates and terminates Pod objects based on
#the expected number of replicas.
class DepController:
	def __init__(self, APISERVER, LOOPTIME):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
	
	def __call__(self):
		print("depController start")
		while self.running:
			microservices= []
			with self.apiServer.etcdLock:
				for microservice in self.apiServer.etcd.microserviceList:
					while microservice.currentReplicas < microservice.expectedReplicas:
						self.apiServer.CreatePod(microservice)
						microservice.currentReplicas +=1
					#endPoints = self.apiServer.GetEndPointsByLabel(microservice.deploymentLabel, microservice.microserviceLabel)
					endPoints = self.apiServer.GetEndPointsByMSLabel(microservice.microserviceLabel)
					#Remove any pending pods before terminating running ones
					for pod in self.apiServer.etcd.pendingPodList:
						if pod.microserviceLabel == microservice.microserviceLabel:
							if microservice.currentReplicas > microservice.expectedReplicas:
								self.apiServer.etcd.pendingPodList.remove(pod)
								microservice.currentReplicas-=1
					for endPoint in endPoints:
						#Terminate running pods if required
						if microservice.currentReplicas > microservice.expectedReplicas:
							self.apiServer.TerminatePod(endPoint)
							microservice.currentReplicas-=1
					#if microservice.expectedReplicas > 0:
					microservices.append(microservice)
				self.apiServer.etcd.microserviceList = microservices
			time.sleep(self.time)
		print("DepContShutdown")
