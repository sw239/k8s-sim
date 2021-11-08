"""
This tracefile generator is to be used in conjunction with Assignment 2 of CompX529.
It takes a student ID value and an integer seed, from which it generates a tracefile for use
with a simulated Kubernetes cluster
"""
import math
import random
from matplotlib import pyplot as plt

def detMS(msList):
	selMS = []
	retMS = []
	operators = ['+', '.']
	MSString = "("
	if len(msList)>1:
		op = random.choice(operators)
		numMS = random.randint(2,5)
		if numMS > len(msList):
			numMS = len(msList)
		while len(selMS)<numMS:
			selMS.append(msList[0])
			msList.pop(0)
		for i in range(0, numMS):
			MSString+=selMS[i]
			if i < numMS-1:
				MSString+=op
			else:
				MSString+=")"
		retMS.append(MSString)
		if len(msList)>0:
			retMS+=detMS(msList)
		return(retMS)
	return msList
		
def joinMS(msList):
	operators = ['+', '.']
	retMS = ""
	if len(msList)>1:
		for i in range(0, len(msList)):
			op = random.choice(operators)
			retMS+=msList[i]
			if i < len(msList)-1:
				retMS+=op
		return retMS
	return msList[0]


try:
	idVal = int(input("Enter your student ID: "))*3
	seed = int(input("Enter seed: "))
	if seed > 3 or seed < 1:
		print ("please use seed of 1, 2, or 3")
		quit()
except:
	print("Please enter as integer")
	quit()

nodes = []
deployments = []
microservices = []
hpas = []
nodeMax = 8
depMax =  3
msMax = 6
msLab = 65
depA = 65
depB = 65
commandCount = 300
separator = " "
expRounds = []
expProg = []
xVals = []
f = open("instructions.txt", "w")
for x in range (1, commandCount+1): #Generates a set number of commands
	commands = [] #Establishes the list of possible commands for this step
	random.seed(idVal+x)
	if len(nodes) == 0:
		cpus = random.randint(15,20)
		node = "".join(["Node_",str(len(nodes)+1)])
		command = separator.join(["AddNode", node, str(cpus)])
		nodes.append(node)
		f.write(command+"\n") #Node creation will always be the first command
		continue
	elif len(nodes) < nodeMax:#If we have at least one node but can still have more
		commands.append("AddNode")
	if len(microservices) < msMax:
		commands.append("CreateMS")
	if ((len(deployments) < depMax)&(len(microservices)>2)): #If we can deploy to the cluster
		if depA < 90:
			commands.append("Deploy")
	if len(deployments) >0:#If we have deployments
		commands.append("ReqIn")
		if random.randint(1,10)%3 == 0:
			commands.append("CrashPod")
	if len(hpas)< len(microservices):
		commands.append("CreateHPA")
	choice = random.choice(commands) #Select a command from the pool of available options
	if choice == "AddNode":
		cpus = random.randint(15,20)
		node = "".join(["Node_",str(len(nodes)+1)])
		command = separator.join([choice, node, str(cpus)])
		f.write(command+"\n")
		nodes.append(node)
	if choice == "Deploy":
		msList = []
		msStr = ""
		reqPath = ""
		operators = ["+", "."]
		nMS = random.randint(1, 5)
		if nMS > len(microservices):
			nMS = len(microservices)
		while len(msList)<nMS: #Select microservices to be used by deployment
			msChoice = (random.choice(microservices))
			if not msChoice in msList:
				msList.append(msChoice)
		tmpMS = detMS(msList)
		msStr = joinMS(tmpMS)#Determine action pathway
		depLabel = "".join(map(chr,[depA, depB]))
		if depB < 90:
			depB +=1
		else:
			depA +=1
			depB = 65
		deployment = "".join(["Deployment_",depLabel])
		command = separator.join([choice, deployment, msStr])
		f.write(command+"\n")
		deployments.append(deployment)
		if len(expRounds)<len(deployments):
			expRounds.append(1)
			expProg.append(1)
	if choice == "CreateMS":
		cpus = random.randint(1,3)
		reqDur = random.randint(3, 9)
		ms = "Microservice_" + chr(msLab)
		microservices.append(ms)
		msLab+=1
		command = separator.join([choice, ms, str(cpus), str(reqDur)])
		f.write(command+"\n")
	if choice == "CrashPod":
		deployment = random.choice(deployments)
		command = separator.join([choice, deployment])
		f.write(command+"\n")
	if choice == "ReqIn":
		newSeed = idVal
		for deployment in deployments:
			index = deployments.index(deployment)
			random.seed(newSeed*expRounds[index])
			command = separator.join([choice, str(x), deployment])
			if seed == 1:#Generates a load that ramps up to steady level before dropping
				maxTime = random.randint(20,40)
				curMinPeriod = random.randint(1, 5)
				if expProg[index] == maxTime:
					expRounds[index] +=1
					expProg[index] = 1
				if expProg[index] > curMinPeriod:
					reqPeriod = curMinPeriod		
				else:
					reqPeriod = 2*curMinPeriod - expProg[index]

			elif seed == 2:#Produces a load in with increasing frequency determined by composite sine function
				reqPeriod = int(math.ceil((math.sin(x/random.uniform(10,30)))**2+(math.sin(x/random.uniform(5,20)))**2)+(commandCount-x)/10)
			elif seed == 3:#Produces a load in with decreasing frequency determined by composite sine function
				reqPeriod = int(math.ceil((math.sin(x/random.uniform(10,30)**2))+(math.sin(x/random.uniform(5,20)**2)))+(x)/10)
			expProg[index]+=1
			if reqPeriod < 0:
					reqPeriod = reqPeriod*-1
			if expProg[index]%reqPeriod == 0:
					f.write(command+"\n")
			newSeed+=1

	if choice == "CreateHPA":
		setPoint = random.randint(60,90)
		for ms in microservices:
			if not ms in hpas:
				command = separator.join([choice, ms, str(setPoint)])
				hpas.append(ms)
				f.write(command+"\n")
				break
			
	f.write("Sleep 1\n")
	
for deployment in deployments:
	f.write ("DeleteDeployment "+deployment+"\n")
for ms in microservices:
	f.write ("DeleteMicroservice "+ms+"\n")