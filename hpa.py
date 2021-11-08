import threading
import time
import math
from MyController import PIDController
from MyController import Supervisor
#Your Horizontal Pod Autoscaler should monitor the average resource utilization of a deployment across
#the specified time period and execute scaling actions based on this value. The period can be treated as a sliding window.
#apiServer is the apiServer
#running is the running status of the HPA
#time is the checking period for the algorithm
#deploymentLabel is the label of the associated deployment
#setPoint is the setpoint for cpu utilisation
#maxReps is the max number of pod replicas
#minReps is the minimum number of pod replicas

class HPA:
	def __init__(self, APISERVER, LOOPTIME, INFOLIST):
		self.apiServer = APISERVER
		self.running = True
		self.cindex = 0
		#self.controller = MyController(1,1,0)
		self.time = LOOPTIME
		self.microserviceLabel = INFOLIST[0]
		self.setPoint = float(INFOLIST[1])/100
		self.maxReps = 5
		self.minReps = 1
		self.errors = []
	def __call__(self):
		while self.running:
			with self.apiServer.etcdLock:
				c = PIDController(1, 1, 0)
				s = Supervisor()
				if self.cindex==15:
					s.calibrate(c, self.errors)
					self.errors = []
					self.cindex=0
				microservice = self.apiServer.GetMsByMsLabel(self.microserviceLabel)
				if microservice == None:
					self.running = False
					break
				elif self.microserviceLabel in self.apiServer.etcd.microserviceList:
					microservice.currentReplicas = 0;
					microservice.expectedReplicas = 0;
				else:
					epoints = self.apiServer.GetEndPoints()
					pods = []
					for pod in self.apiServer.GetPending():
							if pod.microserviceLabel == self.microserviceLabel:
								pods.append(pod)
					for ep in epoints:
						if ep.microserviceLabel == self.microserviceLabel:
							pods.append(self.apiServer.GetPod(ep))
					availableCPUS = 0
					for pod in pods:
						availableCPUS+=pod.available_cpu
					if len(pods) == 0:
						averageUtil = 0
					else:
						averageUtil = (microservice.cpuCost*len(pods)-availableCPUS)/(microservice.cpuCost*len(pods))
					newRepsdown = math.ceil(microservice.currentReplicas * averageUtil/(self.setPoint*0.9))
					newRepsup = math.ceil(microservice.currentReplicas * averageUtil/(self.setPoint*1.1))
					newReps = math.ceil(microservice.currentReplicas * averageUtil/self.setPoint)
					error = averageUtil-self.setPoint
					self.errors.append(error)
					u=c.work(error)
					if newRepsdown < self.minReps:
						microservice.expectedReplicas = self.minReps
					elif newRepsup > self.maxReps:
						microservice.expectedReplicas = self.maxReps
					else:
						microservice.expectedReplicas = newReps		
			time.sleep(15/self.time)
			self.cindex += 1
		print("HPA Shutdown")
