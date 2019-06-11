from java.awt import *
from javax.swing import *
from java.io import File
from java.util import HashMap
from WaveFormParameters import *
from ScanParameters import *
from xal.extension.widgets.plot import *
from xal.extension.widgets.swing import *
from xal.extension.emscan import Scanner
from xal.extension.emscan import ScanEvent
from xal.extension.emscan.ScanStatus import *

class WaveForm :
    def __init__(self) :
        
        
        
        self.dataPath=''     
        self.maxValue = 0.0
        self.scan = ScanParameters()
        self.waveForm = WaveFormParameters()
        self.intensityPlot = FunctionGraphsJPanel(preferredSize = (530, 240))
        self.intensityData = Data3DFactory.getData3D(1, 1, 'smooth')
        
        self.parallelogramHalf1 = BasicGraphData(graphColor = Color.WHITE)
        self.parallelogramHalf2 = BasicGraphData(graphColor = Color.WHITE)
        
        self.pauseButton = JButton('Stop', actionPerformed = self.stopRepetition)
        self.updateButton = JButton('Update', actionPerformed = self.editWaveForm)
        self.saveButton = JButton('Save', actionPerformed = self.saveWaveForm)
        self.loadButton = JButton('Load', actionPerformed = self.loadWaveForm)
        
        self.scanButton = JButton('Scan', actionPerformed = self.startScan)
        self.pauseScanButton = JButton('Pause', actionPerformed = self.pauseScan)
        self.resumeScanButton = JButton('Resume', actionPerformed = self.resumeScan)
        self.abortScanButton = JButton('Abort', actionPerformed = self.abortScan)
        
        
        
        self.integralLabel = JLabel('Integral: ' + str(self.scan.area) + ' uC')
        
        self.xTranslationLabel = JLabel('<html> x<sup>(1)</sup> = x </html>')
        self.actuatorPos1Label = JLabel('<html> x<sup>(1)</sup><sub>1</sub>: 0.0 mm </html>')
        self.actuatorPos1StepLabel = JLabel('<html> x<sup>(1)</sup><sub>Step</sub>: 0.0 mm </html>')
        self.xPrimeTranslationLabel = JLabel('<html> x<sup>(2)</sup> = x\' * L + x </html>')
        self.actuatorPos2Label = JLabel('<html> x<sup>(2)</sup><sub>1</sub>: 0.0 mm </html>')
        self.actuatorPos2StepLabel = JLabel('<html> x<sup>(2)</sup><sub>Step</sub>: 0.0 mm </html>')
        self.SPSLabel = JLabel('SPS: 0.0 mm')
        self.actuatorPosChangeLabel = JLabel('<html> dx<sup>(2)</sup>: 0.0 mm </html>')
        self.numStepsLabel = JLabel('<html> N<sup>(1)</sup><sub>Step</sub>: 0 steps </html>')
        
        self.inputPanel = JPanel(GridLayout(15, 3))
        self.simPanel  = JPanel(GridLayout(7, 3))
        self.devicePanel = JPanel(GridLayout(8, 2))
        
        self.filePanel = JPanel(BorderLayout())
        self.filePanel.add(JLabel("Datafile:"),BorderLayout.LINE_START)
        self.fileField = JTextField()
        self.fileField.setEditable(False)
        self.filePanel.add(self.fileField,BorderLayout.CENTER)
        
        self.statusPanel = JPanel(BorderLayout())
        self.statusPanel.add(JLabel("Status:"),BorderLayout.LINE_START)
        self.statusField = JTextField()
        self.statusField.setEditable(False)
        self.statusPanel.add(self.statusField,BorderLayout.CENTER)
        
        
        
        tabPanel = JTabbedPane()
#        tabPanel.addTab("Simulation",self.simPanel)
        tabPanel.addTab("Device",self.devicePanel)
                 
        self.placeHolderPanel = JPanel()
        self.placeHolderPanel.setLayout(BoxLayout(self.placeHolderPanel, BoxLayout.PAGE_AXIS))
        self.placeHolderPanel.add(self.inputPanel)
        self.placeHolderPanel.add(tabPanel)
        self.placeHolderPanel.add(self.filePanel)
        self.placeHolderPanel.add(self.statusPanel)
        

        self.placeHolderPanel.add(Box.Filler(Dimension(0,0), Dimension(0,1000), Dimension(0,1000)));
        
        
        self.repRateField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.maxCurrentField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.pulseDurationField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.waveFormLenField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.noiseAmpField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.sampRateField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.pulseDelayField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.x1Field = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.xPrime1Field = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.x2Field = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.dXPrimeField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.slopeField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.xStepField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.xPrimeStepField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.baseLineField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.integStartField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        self.integEndField = DoubleInputTextField('0.0', horizontalAlignment = SwingConstants.RIGHT)
        
        
        self.slitHarpField = DoubleInputTextField('946.15', horizontalAlignment = SwingConstants.RIGHT)
        self.slitField = JTextField(10, horizontalAlignment = SwingConstants.RIGHT)
        self.harpField = JTextField(10, horizontalAlignment = SwingConstants.RIGHT)
        self.slitRbField = JTextField(10, horizontalAlignment = SwingConstants.RIGHT)
        self.harpRbField = JTextField(10, horizontalAlignment = SwingConstants.RIGHT)
        self.signalField = JTextField(10, horizontalAlignment = SwingConstants.RIGHT)
        
        
        self.propScan = [   ['Repetition Rate: ', 'repRate', self.repRateField, 'Hz', self.waveForm.repRate],                             
                            ['<html> x<sub>1</sub>: </html>', 'x1', self.x1Field, 'mm', self.scan.x1],
                            ['<html> x\'<sub>1</sub>: </html>', 'xPrime1', self.xPrime1Field, 'mrad', self.scan.xPrime1],
                            ['<html> x<sub>2</sub>: </html>', 'x2', self.x2Field, 'mm', self.scan.x2],
                            ['dx\': ', 'dXPrime', self.dXPrimeField, 'mrad', self.scan.dXPrime],
                            ['Slope: ', 'slope', self.slopeField, 'rad/m', self.scan.slope],
                            ['<html> x<sub>Step</sub>: </html>', 'positionStep', self.xStepField, 'mm', self.scan.xStep],
                            ['<html> x\'<sub>Step</sub>: </html>', 'angleStep', self.xPrimeStepField, 'mrad', self.scan.xPrimeStep],
                            ['Base Line: ', 'baseLine', self.baseLineField, 'us', self.scan.baseLine],
                            ['Integration Start: ', 'integStart', self.integStartField, 'us', self.scan.integStart], 
                            ['Integration End: ', 'integEnd', self.integEndField, 'us', self.scan.integEnd]
        ]
        
        self.propSim = [   
                            ['Maximum Current: ', 'maxCurrent', self.maxCurrentField, 'mAmp', self.waveForm.maxCurrent], 
                            ['Pulse Duration: ', 'pulseDuration', self.pulseDurationField, 'us', self.waveForm.pulseDuration], 
                            ['Wave Form Length: ', 'waveFormLen', self.waveFormLenField, 'us', self.waveForm.waveFormLen], 
                            ['Noise Amplitude: ', 'noiseAmp', self.noiseAmpField, 'mAmp', self.waveForm.noiseAmp], 
                            ['Sample Rate: ', 'sampRate', self.sampRateField, 'samp/us', self.waveForm.sampRate], 
                            ['Pulse Delay: ', 'pulseDelay', self.pulseDelayField, 'us', self.waveForm.pulseDelay]
                            
        ]
        
        self.propDevice = [ 
                            ['Slit Harp Distance (mm): ', 'SlitHarp', self.slitHarpField, True],
                            ['Upstream Actuator: ', 'Slit', self.slitField, False], 
                            ['Downstream Actuator:', 'Harp', self.harpField, False], 
                            ['Upstream synced rb: ', 'SlitRb', self.slitRbField,False], 
                            ['Downstream synced rb: ', 'HarpRb', self.harpRbField,False], 
                            ['Signal: ', 'Signal', self.signalField, False] 
                            
                            
        ]
        
        self.propMisc = [   ['DataPath',''],
                            ['SystemType','BTF']
        ]
               
        self.zeroEquality = [   [self.repRateField, 'Repetition Rate'], 
                                [self.pulseDurationField, 'Pulse Duration'], 
                                [self.waveFormLenField, 'Wave Form Length'], 
                                [self.sampRateField, 'Sample Rate'],
                                [self.xStepField, 'Position Actuator Step'],
                                [self.xPrimeStepField, 'Angle Actuator Step']
        ]
        self.negativity = [ [self.maxCurrentField, 'Maximum Current'], 
                            [self.pulseDelayField, 'Base Line'],
                            [self.dXPrimeField, 'Change in Angle']
                            
        ]
        self.outPutVariables = [self.xTranslationLabel, self.actuatorPos1Label, 
            self.actuatorPos1StepLabel, self.xPrimeTranslationLabel, 
            self.actuatorPos2Label, self.actuatorPos2StepLabel, self.SPSLabel, 
            self.actuatorPosChangeLabel, self.numStepsLabel]
            
        self.updateScanStatus(ScanEvent(ABORT))
    
    def stopRepetition(self, e) :
        if self.scan.flag :
            self.scan.flag = False
            self.pauseButton.setText('Resume')
        else :
            self.scan.flag = True
            self.pauseButton.setText('Stop')

    def editWaveForm(self, e) :
        errMsg = None
        for i in self.zeroEquality :
            if errMsg == None :
                errMsg = self.waveForm.checkZeroEquality(i[0].value, i[1])
            else :
                break
        if errMsg == None :
            for i in self.negativity :
                if errMsg == None :
                    errMsg = self.waveForm.checkNegativity(i[0].value, i[1])
                else :
                    break
        if errMsg == None :
            errMsg = self.waveForm.checkWaveFormLeng(self.waveFormLenField.value, 
                self.pulseDurationField.value, self.pulseDelayField.value)
        if errMsg == None :
            self.waveForm.repRate = self.repRateField.value
            self.waveForm.maxCurrent = self.maxCurrentField.value
            self.waveForm.pulseDuration = self.pulseDurationField.value
            self.waveForm.waveFormLen = self.waveFormLenField.value
            self.waveForm.noiseAmp = self.noiseAmpField.value
            self.waveForm.sampRate = self.sampRateField.value
            self.waveForm.pulseDelay = self.pulseDelayField.value
            
            self.scan.x1 = self.x1Field.value
            self.scan.xPrime1 = self.xPrime1Field.value
            self.scan.x2 = self.x2Field.value
            self.scan.dXPrime = self.dXPrimeField.value
            self.scan.slope = self.slopeField.value
            self.scan.xStep = self.xStepField.value
            self.scan.xPrimeStep = self.xPrimeStepField.value
            self.scan.baseLine = self.baseLineField.value
            self.scan.integStart = self.integStartField.value
            self.scan.integEnd = self.integEndField.value
            
            self.scan.actuatorLen = self.slitHarpField.value
            
            pPoints = self.scan.generateParallelogram()
            self.parallelogramHalf1.addPoint(pPoints[0], pPoints[1])
            self.parallelogramHalf2.addPoint(pPoints[2], pPoints[3])
            
            self.xvals = pPoints[0]+pPoints[2]
            self.yvals = pPoints[1]+pPoints[3]
            
            self.intensityPlot.refreshGraphJPanel()
            
            self.scan.estimateOutput()
            self.actuatorPos1Label.setText('<html> x<sup>(1)</sup><sub>1</sub>: ' + self.scan.xOne1 + ' mm </html>')
            self.actuatorPos1StepLabel.setText('<html> x<sup>(1)</sup><sub>Step</sub>: ' + self.scan.xOneStep + ' mm </html>')
            self.actuatorPos2Label.setText('<html> x<sup>(2)</sup><sub>1</sub>: ' + self.scan.xTwo1 + ' mm </html>')
            self.actuatorPos2StepLabel.setText('<html> x<sup><(2)</sup><sub>Step</sub>: ' + self.scan.xTwoStep + ' mm </html>')
            self.SPSLabel.setText('SPS: ' + self.scan.sps + ' mm')
            self.actuatorPosChangeLabel.setText('<html> dx<sup>(2)</sup>: ' + self.scan.dXTwo + ' mm </html>')
            self.numStepsLabel.setText('<html> N<sup>(1)</sup><sub>Step</sub>: ' + self.scan.nOneStep + '</html>')
        else :
            errFrame = JFrame('ERROR')
            errFrame.size = (550, 75)
            errFrame.setLayout(FlowLayout())
            errFrame.add(JLabel(errMsg))
            errFrame.setVisible(1)
        self.updateScanStatus(ScanEvent(IDLE))
        

        
    def saveWaveForm(self, e) :
        chooseFile = JFileChooser()
	chooseFile.setCurrentDirectory(File(self.dataPath))
        ret = chooseFile.showDialog(None, 'Save')
        if ret == JFileChooser.APPROVE_OPTION :
            filename = chooseFile.getSelectedFile().getCanonicalPath()
            title = chooseFile.getSelectedFile().getName()
            self.mainFrame.setTitle("Emittance scanner: " +title)
            with open(filename, 'w') as f :
                self.savePropV(self.propSim,f)
                self.savePropT(self.propDevice,f)
                self.savePropV(self.propScan,f)
                self.savePropS(self.propMisc,f)
                
                f.close()
                
    def savePropV(self, prop, f):
        for i in prop :
            f.write(i[1] + ' ' + str(i[2].value) + ' ' + i[3] + '\n')
    
    def savePropT(self, prop, f):
        for i in prop :
            f.write(i[1] + ' ' + str(i[2].text) + '\n')
    def savePropS(self, prop, f):
        for i in prop :
            f.write(i[0] + ' ' + i[1] + '\n')            
            
    def loadWaveForm(self, e) :
        chooseFile = JFileChooser()
	print self.dataPath
	chooseFile.setCurrentDirectory(File(self.dataPath))
        ret = chooseFile.showDialog(None, 'Load')
        if ret == JFileChooser.APPROVE_OPTION :
            filename = chooseFile.getSelectedFile().getCanonicalPath()
            title = chooseFile.getSelectedFile().getName()
            self.mainFrame.setTitle("Emittance scanner: " +title)
            with open(filename, 'r') as f :
                for line in f :
                    dataLine = line.split(' ')
                    self.readLineV(self.propScan,dataLine)
                    self.readLineV(self.propSim,dataLine)
                    self.readLineT(self.propDevice,dataLine)
                    self.readLineS(self.propMisc,dataLine)
                f.close()
                
    def readLineV(self,prop,line):
        for i in prop :
            if line[0] == i[1] :
                i[2].setValue(float(line[1]))
            else : 
                continue
                
    def readLineT(self,prop,line):
        for i in prop :
            if line[0] == i[1] :
                if i[3]:
                    i[2].setValue(float(line[1]))
                else:
                    i[2].setText(' '.join(map(lambda x: x.strip(),filter(lambda x: len(x)!=0,line[1:]))))
            else : 
                continue
  
    def readLineS(self,prop,line):
        for i in prop :
            if line[0] == i[0] :
               i[1]=line[1].strip()
            else : 
                continue
                 
    
    def setDataListener(self,l):
        self.dataListener = l
                
                
    def startScan(self,e):
        print "Starting scan"
        self.maxValue=0.0
        self.intensityData.setMinMaxX(1.1*min(self.xvals)-2, 1.1*max(self.xvals)+2)
        self.intensityData.setMinMaxY(1.1*min(self.yvals)-2, 1.1*max(self.yvals)+2)
        self.intensityData.setZero()

        self.intensityPlot.refreshGraphJPanel()
        paramMap = HashMap()
        for i in self.propDevice :
            paramMap[i[1]]=i[2].text
        
        paramMap['SlitInitial']=self.scan.xOne1

        #the harp initial position has max x' and first swipe will go backwards
        paramMap['HarpInitial']=str(float(self.scan.xTwo1)+float(self.scan.dXTwo))
        paramMap['SlitStepSize']=self.scan.xOneStep
        paramMap['HarpStepSlitSize']=self.scan.sps
        paramMap['HarpSpan']=self.scan.dXTwo
        paramMap['HarpStepSize']=self.scan.xTwoStep
        paramMap['RepRate']=str(self.waveForm.repRate)
        paramMap['SlitSteps']=self.scan.nOneStep
        paramMap['Speed']='2.5'
        paramMap['StopTimeout']='120000'
	paramMap['SystemType']=self.propMisc[1][1]
        paramMap['DataPath']=self.propMisc[0][1]
        
        signal = paramMap.remove('Signal')
        i=1
        for s in signal.split(',') :
            paramMap['Signal'+str(i)]=s.strip()
            i=i+1
        
        
        scanner = Scanner(self.updateScanStatus,self.dataListener)
        scanner.runAsync(paramMap)
        scanner.setPaused(False)
        self.scanner = scanner
        
        print str(paramMap)
    
    def pauseScan(self,e):        
        self.scanner.setPaused(True)
    def resumeScan(self,e):        
        self.scanner.setPaused(False)
    def abortScan(self,e):        
        self.scanner.abort()    
        
    def updateScanStatus(self,event):
        status = event.getStatus()
        if (status == PROGRESS):
            self.scanButton.setEnabled(False)
            self.pauseScanButton.setEnabled(True)
            self.resumeScanButton.setEnabled(False)
            self.abortScanButton.setEnabled(True)
            self.statusField.setText(str(status)+" "+event.getArg())
        elif (status == START):
            self.fileField.setText(event.getArg())   
            self.statusField.setText(str(status))
        elif(status == PAUSED):
            self.scanButton.setEnabled(False)
            self.pauseScanButton.setEnabled(False)
            self.resumeScanButton.setEnabled(True)
            self.abortScanButton.setEnabled(True)
            self.statusField.setText(str(status))
        elif(status == ABORT):
            self.scanButton.setEnabled(False)
            self.pauseScanButton.setEnabled(False)
            self.resumeScanButton.setEnabled(False)
            self.abortScanButton.setEnabled(False)
            self.statusField.setText(str(status))
        elif(status == IDLE):
            self.scanButton.setEnabled(True)
            self.pauseScanButton.setEnabled(True)
            self.resumeScanButton.setEnabled(True)
            self.abortScanButton.setEnabled(True)
            self.statusField.setText(str(status))
            
        print str(status)
