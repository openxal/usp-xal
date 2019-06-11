from math import exp
from WaveFormParameters import *

class ScanParameters :
    def __init__(self) :
        self.x1 = 0.0
        self.xPrime1 = 0.0
        self.x2 = 0.0
        self.dXPrime = 0.0
        self.slope = 0.0
        self.xStep = 1.0
        self.xPrimeStep = 1.0
        self.baseLine = 1.0
        self.integStart = 0.0
        self.integEnd = 0.0
        
        self.xOne1 = '0.0'
        self.xOneStep = '0.0'
        self.xTwo1 = '0.0'
        self.xTwoStep = '0.0'
        self.sps = '0.0'
        self.dXTwo = '0.0'
        self.nOneStep = '0.0'

        self.area = 0.0
        self.flag = True
        self.actuatorLen = 946.15

    def generateIntensity(self) :
        intensityDataPoints = []
        x = -0.5
        dy = 1.0 / 300
        dx = 1.0 / 300
        for i in range(300) :
            y = -0.5
            for j in range(300) :
                k = exp(-(x ** 2 + y ** 2) / 0.25)
                intensityDataPoints.append([i, j, k])
                y += dy
            x += dx
        return intensityDataPoints

    def generateParallelogram(self) :
        parallelogramPoints = []
        theta1 = self.slope * (self.x2 - self.x1) + self.xPrime1
        theta2 = self.slope * (self.x2 - self.x1) + self.xPrime1 + self.dXPrime
        parallelogramPoints.append([self.x1, self.x1, self.x2])
        parallelogramPoints.append([self.xPrime1, self.xPrime1 + self.dXPrime, 
            theta2])
        parallelogramPoints.append([self.x1, self.x2, self.x2])
        parallelogramPoints.append([self.xPrime1, theta1, theta2])
        return parallelogramPoints

    def estimateOutput(self) :

        self.xOne1 = str(self.x1)
        self.xOneStep = str(self.xStep)
        self.xTwo1 = str(self.xPrime1/1000.0 * self.actuatorLen + self.x1)
        self.xTwoStep = str(self.xPrimeStep/1000.0 * self.actuatorLen)
        self.sps = str(self.xStep * (self.slope*self.actuatorLen/1000.0 + 1))
        self.dXTwo = str(self.dXPrime/1000.0 * self.actuatorLen )
        self.nOneStep = str(int((self.x2 - self.x1) / self.xStep))
    
    def integrateWaveForm(self, IPoints, sampRate) :
        total = 0.0
        for i in range(int(self.baseLine * sampRate)) :
            total += IPoints[i]
        avg = total / (self.baseLine * sampRate)
        for i in range(len(IPoints)) :
            IPoints[i] -= avg
        for i in range(int(self.integStart * sampRate), 
            int(self.integEnd * sampRate)) :
                self.area += IPoints[i] / sampRate
        self.area *= 10 ** -3
#        self.area = round(self.area, 4)
    def calcPhase(self,x,y):
        return (x, (y-x)/self.actuatorLen*1000.0)
