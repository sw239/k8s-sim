import threading
from request import Request
from dep_controller import DepController
from api_server import APIServer
from node_controller import NodeController
from graphInfo import DeploymentGraphInfo, MicroserviceGraphInfo, NodeGraphInfo
from scheduler import Scheduler
import matplotlib.pyplot as plt
from hpa import HPA
from load_balancer import LoadBalancer
import time



#This is the simulation frontend that will interact with your APIServer to change cluster configurations and handle requests
#All building files are guidelines, and you are welcome to change them as much as desired so long as the required functionality is still implemented.

_nodeCtlLoop = 1
_depCtlLoop = 1
_scheduleCtlLoop =1
_hpaCtlLoop = 2

kind = ''
apiServer = APIServer()
depController = DepController(apiServer, _depCtlLoop)
nodeController = NodeController(apiServer, _nodeCtlLoop)
scheduler = Scheduler(apiServer, _scheduleCtlLoop)
depControllerThread = threading.Thread(target=depController)
nodeControllerThread = threading.Thread(target=nodeController)
schedulerThread = threading.Thread(target = scheduler)
print("Threads Starting")
nodeControllerThread.start()
depControllerThread.start()
schedulerThread.start()
print("ReadingFile")
#Graphing info
nodeGraphing = []
deploymentGraphing = []
steps = []
curStep = 0
#Simulation information
loadBalancers = []
hpas = []
supervisors = []
hpaThreads = []
loadBalancerThreads = []
supervisorThreads = []
count = 0
instructions = open("instructions.txt", "r")
commands = instructions.readlines()
for i in range (0,3):
	deploymentGraphing.append(DeploymentGraphInfo())
for i in range(0,8):
	nodeGraphing.append(NodeGraphInfo())
for command in commands:
	cmdAttributes = command.split()
	with apiServer.etcdLock:
		if cmdAttributes[0] == 'CreateMS':
			apiServer.CreateMicroserviceTemplate(cmdAttributes[1:])
		if cmdAttributes[0] == 'Deploy':
			print(command)
			apiServer.CreateDeployment(cmdAttributes[1:])
			deployment = apiServer.GetDepByLabel(cmdAttributes[1])
			loadbalancer = LoadBalancer(kind, apiServer, deployment)
			lbThread = threading.Thread(target=loadbalancer)
			lbThread.start()
			loadBalancers.append(loadbalancer)
			loadBalancerThreads.append(lbThread)
			graphedDeploy= next(dep for dep in deploymentGraphing if dep.deploymentLabel == '')
			graphedDeploy.deploymentLabel = deployment.deploymentLabel
			for i in range (0, curStep):
				graphedDeploy.requests[0].append(0)
				graphedDeploy.requests[1].append(0)
			for ms in deployment.msList:
				graphedMS = MicroserviceGraphInfo(ms)
				for i in range (0,curStep):
					graphedMS.activeList.append(0)
					graphedMS.pendingList.append(0)
					graphedMS.crashedList.append(0)
					graphedMS.expectedList.append(0)
					graphedMS.utilList.append(0)
					graphedMS.setpointList.append(0)
				graphedDeploy.microservices.append(graphedMS)

		elif cmdAttributes[0] == 'AddNode':
			apiServer.CreateWorker(cmdAttributes[1:])
			graphedNode= next(node for node in nodeGraphing if node.label == '')
			graphedNode.label = cmdAttributes[1]
		elif cmdAttributes[0] == 'DeleteDeployment':
			#We have to makesure that our load balancer will end gracefully here
			for loadbalancer in loadBalancers:
				if loadbalancer.deployment.deploymentLabel == cmdAttributes[1]:
					loadbalancer.running = False
			apiServer.RemoveDeployment(cmdAttributes[1:])
		elif cmdAttributes[0] == 'DeleteMicroservice':
			apiServer.RemoveMicroservice(cmdAttributes[1:])
			#Graceful ending of HPAs
			for hpa in hpas:
				if hpa.microserviceLabel == cmdAttributes[1]:
					hpa.running = False
		elif cmdAttributes[0] == 'ReqIn':
			apiServer.PushReq(cmdAttributes[1:])
		elif cmdAttributes[0] == 'CreateHPA':
			hpa = HPA(apiServer, _hpaCtlLoop, cmdAttributes[1:])
			hpaThread = threading.Thread(target=hpa)
			hpaThread.start()
			hpas.append(hpa)
			hpaThreads.append(hpaThread)
		elif cmdAttributes[0] == 'CrashPod':
			apiServer.CrashPod(cmdAttributes[1:])
	#The instructions will sleep after each round of requests. The following code stores values for graphing
	if cmdAttributes[0] == 'Sleep':
		count+=1
		time.sleep(int(cmdAttributes[1]))
	
	for graphedNode in nodeGraphing:
		for node in apiServer.etcd.nodeList:
			if node.label == graphedNode.label:
				graphedNode.cpuList.append(node.available_cpu)
		if graphedNode.label == '':
			graphedNode.cpuList.append(0)
	for graphedDep in deploymentGraphing:
		for dep in apiServer.etcd.deploymentList:
			if dep.deploymentLabel == graphedDep.deploymentLabel:
				failReqs = list(filter(lambda x: x.fail.isSet(), dep.handledReqs))
				graphedDep.requests[0].append(len(dep.handledReqs)-len(failReqs))
				graphedDep.requests[1].append(len(failReqs))
				for ms in dep.msList:
					curMS = apiServer.GetMsByMsLabel(ms)
					graphedMS = next(graphingMS for graphingMS in graphedDep.microservices if graphingMS.label == ms)
					graphedMS.expectedList.append(curMS.expectedReplicas)
					pendingPods = list(filter(lambda x: x.microserviceLabel == ms, apiServer.etcd.pendingPodList))
					activePods = len(apiServer.GetEndPointsByMSLabel(ms))
					failedPods = list(filter(lambda x: x.microserviceLabel == ms, filter(lambda x: x.status == "FAILED", apiServer.etcd.runningPodList)))
					graphedMS.pendingList.append(len(pendingPods))
					graphedMS.activeList.append((activePods))
					graphedMS.crashedList.append(len(failedPods))
	curStep+=1
	steps.append(curStep)
time.sleep(30)
print("Shutting down threads")
depController.running = False
scheduler.running = False
nodeController.running = False
apiServer.requestWaiting.set()
for lbthread in loadBalancerThreads:
	lbthread.join()
for hpathread in hpaThreads:
	hpathread	.join()
depControllerThread.join()
schedulerThread.join()
nodeControllerThread.join()
for node in nodeGraphing:
	plt.plot(steps, node.cpuList, label = "available cpu")
	plt.title("Available CPU for "+node.label)
	plt.legend()
	plt.savefig(node.label+".png")
	plt.show()
	
for dep in deploymentGraphing:
	plt.plot(steps, dep.requests[0], label="Handled Requests")
	plt.plot(steps, dep.requests[1], label="Failed Requests")
	plt.title("Requests for "+dep.deploymentLabel)
	plt.legend()
	plt.savefig(dep.deploymentLabel+".png")
	plt.show()
	
	for ms in dep.microservices:
		plt.plot(steps, ms.activeList, label = "Active pods")
		plt.plot(steps, ms.crashedList, label = "Failed pods")
		plt.plot(steps, ms.pendingList, label = "Pending pods")
		plt.plot(steps, ms.expectedList, label = "Expected pods")
		plt.title("Pods for"+ms.label)
		plt.legend()
		plt.savefig(ms.label+".png")
		plt.show()

		