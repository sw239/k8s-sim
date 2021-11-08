#Deployment objects set the requestpath for incoming requests associated with a service.s
#deploymentLabel is the label associated with the deployment.
#msPath is the path for request handling
#msList is a list of microservices
#pendingReqs are reqests to be handled
#handledReqs are requests that are either being handled, or finished
#waiting is a flag to indicate new requests to be handled
#lock is a thread lock to protect access
#pool is a threadpool for handling requests
#orderList is the order for handling requests
import threading
import re
from concurrent.futures import ThreadPoolExecutor

class Deployment:
	def __init__(self, INFOLIST):
		self.deploymentLabel = INFOLIST[0]
		self.msPath = INFOLIST[1]
		self.msList = []
		self.pendingReqs = []
		self.handledReqs = []
		self.waiting = threading.Event()
		self.lock = threading.Lock()
		self.pool = ThreadPoolExecutor(max_workers=25)
		self.orderList = []
		self.orderList = self.msPath.split(').(')
			
		