import threading
import math
import sys
import os 

from java.awt import *
from javax.swing import *


#scriptpath=os.path.dirname(os.path.abspath(__file__))
#sys.path.append(scriptpath+"/../../lib/xal-shared.jar")
#sys.path.append(scriptpath+"/../../apps/emittanceanalysis.jar")


from WaveForm import *
from xal.extension.widgets.plot import *
from xal.extension.widgets.apputils import *
from xal.extension.emscan import *

WF = WaveForm()
colorGenerator = LocalColorGenerator()

waveFormPlot = FunctionGraphsJPanel(preferredSize = (530, 240))
waveFormData = BasicGraphData(graphColor = Color.BLUE)

#intensityPlot = FunctionGraphsJPanel(preferredSize = (530, 240))
#intensityData = Data3DFactory.getData3D(300, 300, 'smooth')

def waveFormGenerator() :  
    waveFormGraphPanel = JPanel(BorderLayout())
    integralPanel = JPanel(FlowLayout())
    intensityPanel = JPanel(BorderLayout())

    graphingPanel = JPanel(GridLayout(2, 1))

    graphTitlePanel = JPanel(FlowLayout())
    graphTitlePanel.add(JLabel('Wave Form Graph'))
       
    intensityTitlePanel = JPanel(FlowLayout())
    intensityTitlePanel.add(JLabel('Intensity Graph'))

    frame = JFrame('Emittance scanner', layout = BorderLayout(), 
        visible = True, defaultCloseOperation=WindowConstants.EXIT_ON_CLOSE)  
    frame.size = (950, 700)
    
    WF.mainFrame = frame

    graphingPanel.add(waveFormGraphPanel)
    graphingPanel.add(intensityPanel)
    
    
    frame.add(integralPanel, BorderLayout.PAGE_END)
    frame.add(graphingPanel, BorderLayout.CENTER)
    frame.add(WF.placeHolderPanel,BorderLayout.WEST)
    
    SimpleChartPopupMenu.addPopupMenuTo(waveFormPlot)
    SimpleChartPopupMenu.addPopupMenuTo(WF.intensityPlot)
    waveFormPlot.addGraphData(waveFormData)
    
    WF.intensityData.setSize(100, 100)
    WF.intensityData.setScreenResolution(100, 100)

    
    WF.intensityData.setColorGenerator(colorGenerator)
    WF.intensityData.setMinMaxX(-10, 10)
    WF.intensityData.setMinMaxY(-10, 10)
    
#    intensityDataPoints = WF.scan.generateIntensity()
#    for i in intensityDataPoints :
#        intensityData.setValue(i[0], i[1], i[2])
        
    WF.intensityPlot.setColorSurfaceData(WF.intensityData)
    
    WF.intensityPlot.addGraphData(WF.parallelogramHalf1)
    WF.intensityPlot.addGraphData(WF.parallelogramHalf2)

    waveFormGraphPanel.add(graphTitlePanel, BorderLayout.NORTH)
    waveFormGraphPanel.add(waveFormPlot, BorderLayout.CENTER)
    intensityPanel.add(intensityTitlePanel, BorderLayout.NORTH)
    intensityPanel.add(WF.intensityPlot, BorderLayout.CENTER)
    intensityPanel.add(integralPanel, BorderLayout.SOUTH)
        
#    integralPanel.add(WF.pauseButton)
    integralPanel.add(WF.integralLabel)
        
    for i in WF.propScan :
        WF.inputPanel.add(JLabel(i[0]))
        i[2].preferredSize = (100, i[2].preferredSize.height)
        WF.inputPanel.add(i[2])
        WF.inputPanel.add(JLabel(' ' + i[3]))
    
    for i in WF.propSim :
        WF.simPanel.add(JLabel(i[0]))
        i[2].preferredSize = (100, i[2].preferredSize.height)
        WF.simPanel.add(i[2])
        WF.simPanel.add(JLabel(' ' + i[3]))
    WF.simPanel.add(WF.pauseButton)        
        
        
    for i in WF.propDevice :
        WF.devicePanel.add(JLabel(i[0]))
        WF.devicePanel.add(i[2])
    WF.devicePanel.add(WF.scanButton)
    WF.devicePanel.add(WF.pauseScanButton)
    WF.devicePanel.add(WF.resumeScanButton)
    WF.devicePanel.add(WF.abortScanButton)
        
        

    
    WF.inputPanel.add(WF.updateButton)
    WF.inputPanel.add(WF.saveButton)
    WF.inputPanel.add(WF.loadButton)
    
    for i in WF.outPutVariables :
        WF.inputPanel.add(i)
    
    WF.inputPanel.setBorder(BorderFactory.createLineBorder(Color.black))


def processDataWaveForm(x,y, IPoints) :
    processWaveForm(x,y,[x/WF.waveForm.sampRate for x in range(1, len(IPoints)+1)],IPoints)

def processWaveForm(x,y,tPoints, IPoints) :
    
    
    if WF.scan.flag :
        waveFormData.addPoint(tPoints, IPoints)
        WF.scan.integrateWaveForm(IPoints, WF.waveForm.sampRate)
        WF.integralLabel.setText('Integral: ' + str(WF.scan.area) + ' uC')
        (x1,xp) = WF.scan.calcPhase(x,y)
        print '\n',x1,xp, WF.scan.area,'\n'
        intensityData = WF.intensityData
        (mx,my,dx,dy)= (intensityData.getMinX(),intensityData.getMinY(),intensityData.getMaxX()-intensityData.getMinX(),intensityData.getMaxY()-intensityData.getMinY())
        (nx,ny)=(intensityData.getSizeX(),intensityData.getSizeY())
        
        value = abs(WF.scan.area)
        if(value > WF.maxValue):
            WF.maxValue = value
        WF.intensityData.setValue(int((x1-mx)/dx*nx),int((xp-my)/dy*ny), abs(WF.scan.area))
        colorGenerator.setUpperLimit(WF.maxValue*1.1)
        WF.intensityPlot.refreshGraphJPanel()
        
        waveFormPlot.refreshGraphJPanel
        WF.scan.area = 0.0

    else :
        pass


def main() :
    scriptpath=os.path.dirname(os.path.abspath(__file__))+"/Config"
    if (len(sys.argv) > 1):
       	 scriptpath=sys.argv[1]+"/Config"
    else:
         print 'No arguments given'
    print "Setting config dir to "+scriptpath
    waveFormGenerator()
    WF.setDataListener(processDataWaveForm)
    WF.dataPath = scriptpath
    
#    pThread = threading.Thread(name = 'ProcessWF', 
#        target = WF.waveForm.runWaveForm(processWaveForm))
#    pThread.start()

if (__name__ == '__main__') :
    main()
