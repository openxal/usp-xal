from time import sleep
from random import uniform

class WaveFormParameters :
    def __init__(self) :
        self.repRate = 1.0
        self.maxCurrent = 0.0
        self.pulseDuration = 1.0
        self.waveFormLen = 1.0
        self.noiseAmp = 0.0
        self.sampRate = 1.0
        self.pulseDelay = 0.0
        
    def checkNegativity(self, variable, variableName) :
        if variable < 0 :
            return variableName + ' cannot be negative'
        else :
            return None
        
    def checkZeroEquality(self, variable, variableName) :
        if variable < 0 :
            return variableName + ' cannot be negative'
        elif variable == 0 :
            return variableName + ' cannot be equal to zero'
        else :
            return None
    
    def checkWaveFormLeng(self, waveForm, pulseDuration, pulseDelay) :
        if waveForm < pulseDuration + pulseDelay :
            return  'Wave Form Length is too small. ' + \
                    'Cannot be less than Pulse Duration plus Pulse Delay'
        else :
            return None
        
    def generateWaveForm(self) :
        t = 0
        tPoints = []
        IPoints = []
        self.noise = []
        dt = self.waveFormLen / (self.waveFormLen * self.sampRate)
        for i in range(int(self.waveFormLen * self.sampRate)) :
            tPoints.append(t)
            noiseIndex = self.noiseAmp * uniform(-1, 1)
            self.noise.append(noiseIndex)
            if  i > self.pulseDelay * self.sampRate and \
                i <= (self.pulseDelay + self.pulseDuration) * self.sampRate :
                    IPoints.append(-(self.maxCurrent + noiseIndex))
            else :
                IPoints.append(noiseIndex)
            t += dt
        return (tPoints, IPoints)
    
    def runWaveForm(self, processWaveForm) :
        while True :
            sleep(1.0 / self.repRate)
            (tPoints, IPoints) = self.generateWaveForm()
            processWaveForm(0,0,tPoints, IPoints)