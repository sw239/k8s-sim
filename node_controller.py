from api_server import APIServer
import threading
import time


#NodeController is a control loop that monitors the status of WorkerNode objects in the cluster and ensures that the EndPoint objects stored in etcd are up to date.
#The NodeController will remove stale EndPoints and update to show changes in others
class NodeController:
	
	def __init__(self, APISERVER, LOOPTIME):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
	
	def __call__(self):
		print("NodeController start")
		while self.running:
			pods = []
			crashedPods = []
			with self.apiServer.etcdLock:
				for pod in self.apiServer.etcd.runningPodList:
					if pod.status == "RUNNING":
						pods.append(pod)
					elif pod.status == "TERMINATING":
						if not (all (p.done() for p in pod.requests)):
							pods.append(pod)
						else:
							pod.pool.shutdown()
					else:
						crashedPods.append(pod)
					self.apiServer.etcd.runningPodList = pods
					for pod in crashedPods:
						for endPoint in self.apiServer.etcd.endPointList:
							if endPoint.pod == pod:
								pod.status="PENDING"
								pod.crash.clear()
								self.apiServer.etcd.pendingPodList.append(pod)
								self.apiServer.RemoveEndPoint(endPoint)
								break
			time.sleep(self.time)
		print("NodeContShutdown")
