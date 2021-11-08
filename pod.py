import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from request import Request
import threading

#The Pod is the unit of scaling within Kubernetes. It encapsulates the running containerized application
#name is the name of the Pod. This is the deploymentLabel with the replica number as a suffix. ie "deploymentA1"
#handlingTime is the duration taken to handle requests.
#assigned_cpu is the cost in cpu of deploying a Pod onto a Node
#available_cpu is how many cpu threads are currently available
#deploymentLabel is the label of the Deployment that the Pod is managed by
#microserviceLabel is the label of the associated microservice
#status is a string that communicates the Pod's availability. ['PENDING','RUNNING', 'TERMINATING', 'FAILED']
#crash is a threading event to interrupt request handling
#the pool is the threads that are available for request handling on the pod
#reqs are the active or queued requests
class Pod:
	def __init__(self, NAME, ASSIGNED_CPU, MSLABEL, HANDLINGTIME):
		self.podName = NAME
		self.handlingTime = HANDLINGTIME
		self.assigned_cpu = ASSIGNED_CPU
		self.available_cpu = ASSIGNED_CPU
		self.microserviceLabel = MSLABEL
		self.status = "PENDING"
		self.crash = threading.Event()
		self.pool = ThreadPoolExecutor(max_workers=ASSIGNED_CPU)
		self.requests = []

	def HandleRequest(self, REQUEST):
		def ThreadHandler():
			self.available_cpu -=1
			self.crash.wait(timeout=(REQUEST.fail.wait(timeout=self.handlingTime)))
			self.available_cpu +=1
			if self.crash.isSet():
				REQUEST.fail.set()
		if len(self.requests)>(self.assigned_cpu*self.handlingTime):
			REQUEST.fail.set()
		self.requests.append(self.pool.submit(ThreadHandler))
		activeReqs = []
		for req in self.requests:
			if not req.done():
				activeReqs.append(req)
		self.requests = activeReqs
	
	