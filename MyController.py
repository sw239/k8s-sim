
# @author: Panos Patros
# Based on Feedback Control for Computer Systems by Philipp K. Janert (O'Reilly Media)
# COMPX529 Engineering Self-Adaptive Systems
import random
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt
import math
import pandas as pd
from sklearn.linear_model import LinearRegression
class PIDController:
	def __init__( self, kp, ki, kd):
		self.kp = kp
		self.ki = ki
		self.kd = kd
		self.totalError = 0
		self.prevError = 0
	
	def work( self, e):
		self.totalError += e
	
		up = e*self.kp
		ui = self.totalError*self.ki
		ud = (e-self.prevError)*self.kd
		
		self.prevError = e
		
		return up + ui + ud
class Supervisor:
	def __init__(self):
		self.kps = []
		self.kis = []
		self.indexes = []
		self.avgErrors = []
		self.curIndex = 0
		self.regressor = LinearRegression()
		self.initKps = [-0.04,  0.03,  0.08,  0.01, 0, -0.04, -0.03, 0.02, 0.06]
		self.initKis = [-0.05, -0.02, -0.02, -0.06, -0.1, -0.01,  0.07, 0.04, 0.04]
		self.adjustments = [x*0.01 for x in range(-10,11)]

	def calibrate(self, c, errors):
			self.indexes.append(self.curIndex)
			self.kps.append(c.kp)
			self.kis.append(c.ki)
			self.avgErrors.append(sum(errors)/len(errors))
			#Create a dataset for our regression model
			dataset = pd.DataFrame({'pValues': self.kps, 'iValues': self.kis, 'Errors': self.avgErrors})
			
			#Use some random data points to give use some alterations to base our regression on
			if len(self.initKps)>0:
				c.kp += self.initKps.pop()
				c.ki += self.initKis.pop()
			else:
				#Take our kp and ki values
				X = dataset.iloc[:, :-1].values
				Y = dataset.iloc[:, -1].values
				#assign exponential weighting
				weights = [0.9**i for i in range(len(self.kps))]
				weights.sort(reverse=True)
				weights = np.array(weights)
				#Produce our regression model
				self.regressor.fit(X,Y, sample_weight=weights)
				kp = 0
				ki = 0
				best = None
				for i in self.adjustments:
					for j in self.adjustments:
						if abs(i) + abs(j) >0.1 or c.kp+i<=0 or c.ki+j <=0:
							continue
						X_test = np.array([[c.kp+i, c.ki+j]])
						#Predict error associated with new Kp and Ki values
						Y_pred = self.regressor.predict(X_test)
						if best is None or abs(Y_pred.all())<best.all():
							best = abs(Y_pred)
							kp = i
							ki = j
				#Adjust controller values
				c.kp+=kp
				c.ki+=ki
			self.curIndex+=1
