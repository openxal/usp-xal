# The controller and auxilary classes for the main loop over MEBT, DTL, and CCL cavities

import sys
import math
import types
import time
import random

from java.lang import *
from javax.swing import *
from javax.swing import JTable
from java.awt import Color, BorderLayout, GridLayout, FlowLayout
from java.awt import Dimension
from java.awt.event import WindowAdapter
from java.beans import PropertyChangeListener
from java.awt.event import ActionListener
from java.util import ArrayList
from javax.swing.table import AbstractTableModel, TableModel
from javax.swing.event import TableModelEvent, TableModelListener, ListSelectionListener
from java.text import SimpleDateFormat,NumberFormat,DecimalFormat

from xal.ca import ChannelFactory

from xal.smf.data import XMLDataManager
from xal.smf import AcceleratorSeqCombo

from xal.smf.impl import Marker, Quadrupole, RfGap, BPM
from xal.smf.impl.qualify import AndTypeQualifier, OrTypeQualifier

from xal.extension.widgets.plot import BasicGraphData, FunctionGraphsJPanel, GraphDataOperations
from xal.extension.widgets.swing import DoubleInputTextField 
from xal.tools.text import ScientificNumberFormat


from abstract_cavity_controller_lib import Scan_Progress_Bar

false= Boolean("false").booleanValue()
true= Boolean("true").booleanValue()
null = None

#------------------------------------------------------------------------
#           DTL Acceptance Scan Cavity Controller
#------------------------------------------------------------------------
class DTL_Acc_Scan_Cavity_Controller:
	def __init__(self,dtl_acceptance_scans_controller,cav_wrapper,fc_name):
		#---- main_loop_controller - main controller for PASTA scans
		#---- it keeps referencies to cotrollers for each cavity		
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller	
		self.is_initialized = false
		self.cav_wrapper = cav_wrapper
		self.main_panel = JPanel(BorderLayout())
		self.pattern_panel = JPanel(BorderLayout())
		#-----------------------------------------
		self.scan_progress_bar = Scan_Progress_Bar()
		#-----------------------------------------
		self.cav_scan_cotroller_main_panel = Cavity_Scan_Controller_Main_Panel(self.dtl_acceptance_scans_controller,self)
		self.main_panel.add(self.cav_scan_cotroller_main_panel,BorderLayout.CENTER)
		#-----------------------------------------
		self.fc_name = fc_name
		self.fc_actuator_pv = null
		self.fc_actuator_in_pv = null
		self.fc_actuator_out_pv = null
		self.fc_signal_pv = null
		#------------------------------------------------
		
	def isInitialized(self):
		return self.is_initialized 
		
	def getFC_Name(self):
		return self.fc_name
		
	def connectPVs(self):
		#print "debug connection start cav="+self.cav_wrapper.alias
		prefix = "DTL_Diag:"
		if(self.fc_name == "FC104"): prefix = "CCL_Diag:"
		self.fc_actuator_pv = ChannelFactory.defaultFactory().getChannel(prefix+self.fc_name+":Actuator")
		if(not self.fc_actuator_pv.connectAndWait(0.5)): return false
		self.fc_signal_pv = ChannelFactory.defaultFactory().getChannel(prefix+self.fc_name+":Fast:QGt")
		if(not self.fc_signal_pv.connectAndWait(0.5)): return false
		self.fc_actuator_in_pv = ChannelFactory.defaultFactory().getChannel(prefix+self.fc_name+":Actuator_In")
		if(not self.fc_actuator_in_pv.connectAndWait(0.5)): return false
		self.fc_actuator_out_pv = ChannelFactory.defaultFactory().getChannel(prefix+self.fc_name+":Actuator_Out")	
		if(not self.fc_actuator_out_pv.connectAndWait(0.5)): return false
		#----------------------------
		self.cav_wrapper.connectPVs()
		#----------------------------
		return true
	
	def init(self):
		if(not self.connectPVs()):
			prefix = "DTL_Diag:"
			if(self.fc_name == "FC104"): prefix = "CCL_Diag:"			
			messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
			messageTextField.setText("Cannot Initialize. Cannot connect FC PVs for FC="+prefix+self.fc_name)
			return
		self.cav_wrapper.init()
		#----- set up amplitude scan params
		if(self.cav_scan_cotroller_main_panel.max_cav_amp_text.getValue() == 0.):
			self.cav_scan_cotroller_main_panel.max_cav_amp_text.setValue(self.cav_wrapper.initAmp*1.03)
			self.cav_scan_cotroller_main_panel.min_cav_amp_text.setValue(self.cav_wrapper.initAmp*0.97)
			self.cav_scan_cotroller_main_panel.cav_amp_points_text.setValue(3.)
		self.is_initialized = true
		
	def getMainPanel(self):
		return self.main_panel
		
	def getPatternPanel(self):
		return self.pattern_panel
		
	def moveActuator(self, pos = +1):
		if(self. fc_actuator_pv== null):
			prefix = "DTL_Diag:"
			if(self.fc_name == "FC104"): prefix = "CCL_Diag:"			
			messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
			messageTextField.setText("Cannot move FC. Cannot connect FC PVs for FC="+prefix+self.fc_name)			
			return false
		self.fc_actuator_pv.putVal(pos)
		return true
		
	def isActuatorIn(self):
		if(self.fc_actuator_in_pv == null): return false
		if(self.fc_actuator_in_pv.getValInt() == 1): return true
		return false
		
	def isActuatorOut(self):
		if(self.fc_actuator_in_pv == null): return false
		if(self.fc_actuator_out_pv.getValInt() == 1): return true
		return false

	def getFC_Charge(self):
		if(self.fc_signal_pv == null): return 0.
		return self.fc_signal_pv.getValDbl()
		
	def getCavPhase(self):
		return self.cav_wrapper.getLivePhase()
		
	def getCavAmp(self):
		return self.cav_wrapper.getLiveAmp()
		
	def getMaxTimeCount(self):
		time_scan = self.cav_scan_cotroller_main_panel.getTimeScanEstimation()
		return time_scan
		
	def initProgressBar(self):
		self.scan_progress_bar.init()
		
	def runSetUpAlgorithm(self):
		print "debug runSetUpAlgorithm for "+self.cav_wrapper.alias
		return (true," success ")

#------------------------------------------------------------------------
#           Auxiliary classes
#-----------------------------------------------------------------------
class Acc_Scans_Loop_Run_State:
	""" Describes the acceptance scans loop state """
	def __init__(self):
		self.isRunning  = false
		self.shouldStop = false
	
class Acceptance_Scans_Loop_Runner(Runnable):
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.cav_active_ind = -1

	def run(self):
		self.dtl_acceptance_scans_controller.loop_run_state.isRunning = true
		self.dtl_acceptance_scans_controller.loop_run_state.shouldStop = false
		self.cav_active_ind = -1
		self.runMainLoop()
		self.dtl_acceptance_scans_controller.loop_run_state.isRunning = false
		self.dtl_acceptance_scans_controller.loop_run_state.shouldStop = false		
		self.dtl_acceptance_scans_controller.cav_table.getModel().fireTableDataChanged()
		if(self.cav_active_ind >= 0):
			self.dtl_acceptance_scans_controller.cav_table.setRowSelectionInterval(self.cav_active_ind,self.cav_active_ind)

	def runMainLoop(self):
		res = self.dtl_acceptance_scans_controller.connectAllPVs()
		if(not res):
			return
		status_text = self.dtl_acceptance_scans_controller.start_stop_panel.status_text
		status_text.setText("running")
		messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
		messageTextField.setText("")
		#---------start deal with selected cavities
		cav_selected_inds = self.dtl_acceptance_scans_controller.cav_table.getSelectedRows()
		if(len(cav_selected_inds) < 1 or cav_selected_inds[0] < 0):
			messageTextField.setText("Select one or more cavities to start SetUp!")	
			status_text.setText("Not running.")
			return
		# these are the table indexes
		cav_wrapper = null
		start_ind = cav_selected_inds[0]
		last_ind = cav_selected_inds[len(cav_selected_inds)-1]	
		self.dtl_acceptance_scans_controller.acc_scan_loop_timer.init(start_ind,last_ind)
		self.dtl_acceptance_scans_controller.acc_scan_loop_timer.startMonitor()
		start_cav_name = self.dtl_acceptance_scans_controller.cav_wrappers[start_ind].alias
		stop_cav_name = self.dtl_acceptance_scans_controller.cav_wrappers[last_ind].alias
		txt_status = "From "+ start_cav_name+" to "+stop_cav_name+". Cav="
		self.cav_active_ind = -1
		force_stop = false
		for cav_ind in range(start_ind,last_ind+1):
			self.cav_active_ind = cav_ind
			if(self.dtl_acceptance_scans_controller.loop_run_state.shouldStop):
				force_stop = true
				break
			cav_wrapper = self.dtl_acceptance_scans_controller.cav_wrappers[cav_ind]
			cav_acc_scan_controller = self.dtl_acceptance_scans_controller.cav_acc_scan_controllers[cav_ind]
			status_text.setText(txt_status+cav_wrapper.alias+" scan is running!")
			self.dtl_acceptance_scans_controller.cav_table.setRowSelectionInterval(cav_ind,cav_ind)
			#--------------------------------------------------------
			#????
			cav_acc_scan_controller.initProgressBar()
			(res,txt) = cav_acc_scan_controller.runSetUpAlgorithm()
			if(res):
				if(not self.dtl_acceptance_scans_controller.skipAnalysis_RadioButton.isSelected()):
					if(self.dtl_acceptance_scans_controller.start_stop_panel.keepPhases_RadioButton.isSelected()):
						cav_wrapper.setLivePhase(cav_wrapper.initPhase)
					else:
						cav_wrapper.setLivePhase(cav_wrapper.newPhase)
					if(self.dtl_acceptance_scans_controller.start_stop_panel.keepAmps_RadioButton.isSelected()):
						cav_wrapper.setLiveAmp(cav_wrapper.initAmp)
					else:
						cav_wrapper.setLiveAmp(cav_wrapper.newAmp)
			else:
				cav_wrapper.setLivePhase(cav_wrapper.initPhase)
				cav_wrapper.setLiveAmp(cav_wrapper.initAmp)
			cav_acc_scan_controller.initProgressBar()
			#--------------------------------------------------------	
			if(not res):
				messageTextField.setText(txt)
				status_text.setText("Not running.")
				return
			if(self.dtl_acceptance_scans_controller.loop_run_state.shouldStop):
				force_stop = true
				break
			self.dtl_acceptance_scans_controller.cav_table.getModel().fireTableDataChanged()
		cav_wrapper = self.dtl_acceptance_scans_controller.cav_wrappers[self.cav_active_ind]
		if(force_stop):
			messageTextField.setText("The setup stopped by user's request! Cavity="+cav_wrapper.alias)
		else:
			messageTextField.setText("The setup finished at cavity="+cav_wrapper.alias+"!")
		status_text.setText("Not running.")
		return		

class Accpts_Scan_Timer_Runner(Runnable):
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller 
		self.time_step = 1.0

	def run(self):
		while(1 < 2):
			time.sleep(self.time_step)
			if(not self.dtl_acceptance_scans_controller.loop_run_state.isRunning):
				self.dtl_acceptance_scans_controller.acc_scan_loop_timer.time_estimate_text.setText("")
				return
			self.dtl_acceptance_scans_controller.acc_scan_loop_timer.updateProgress()

class Acc_Scan_Loop_Timer:
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller 
		self.time_estimate_text = 	JTextField(30)
		self.time_estimate_label = JLabel("Time:",JLabel.RIGHT)
		self.total_time = 0.
		self.run_time = 0.
		self.start_time = 0.
		
	def init(self,start_ind,last_ind):
		self.total_time = 0.
		for cav_ind in range(start_ind,last_ind+1):
			cav_acc_scan_controller = self.dtl_acceptance_scans_controller.cav_acc_scan_controllers[cav_ind]
			self.total_time += cav_acc_scan_controller.getMaxTimeCount()
		self.start_time = time.time()
		self.time_estimate_text.setText("")
	
	def updateProgress(self):
		self.run_time = time.time() - self.start_time
		txt = ""
		if(self.run_time < self.total_time):
			txt = self.timeToString(self.run_time)
			txt += " =out of= "+self.timeToString(self.total_time)
		else:
			txt = "Overtime:"+self.timeToString(self.run_time-self.total_time)
			txt += " =out of= "+self.timeToString(self.total_time)
		self.time_estimate_text.setText(txt)
		
	def timeToString(self,tm):
		time_sec = int(tm % 60)
		time_min = int(tm/60.)
		return " %3d min  %2d sec "%(time_min,time_sec)		
		
	def startMonitor(self):
		runner = Accpts_Scan_Timer_Runner(self.dtl_acceptance_scans_controller)
		thr = Thread(runner)
		thr.start()				


#------------------------------------------------------------------------
#           Auxiliary panels
#------------------------------------------------------------------------

class Cavity_Scan_Controller_Main_Panel(JPanel):
	def __init__(self,dtl_acceptance_scans_controller,dtl_acc_scan_cavity_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller		
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		self.dtl_acc_scan_cavity_controller = dtl_acc_scan_cavity_controller
		self.setLayout(BorderLayout())
		self.setBorder(BorderFactory.createEtchedBorder())
		etched_border = BorderFactory.createEtchedBorder()
		#----------------------------------------------------
		scan_params_panel_1 = JPanel(FlowLayout(FlowLayout.LEFT,3,1))
		scan_params_panel_1.setBorder(BorderFactory.createEtchedBorder())
		scan_params_panel_1.setBorder(BorderFactory.createTitledBorder(etched_border,"Cavity Amplitude Scan Parameters"))
		scan_params_panel_2 = JPanel(FlowLayout(FlowLayout.LEFT,3,1))
		scan_params_panel_2.setBorder(BorderFactory.createTitledBorder(etched_border,"Cavity Phase Scan Parameters"))
		scan_params_panel_3 = JPanel(FlowLayout(FlowLayout.LEFT,3,1))
		scan_params_panel_3.setBorder(BorderFactory.createTitledBorder(etched_border,"Cavity Live Parameters"))	
		self.scan_cav_amplitude_button = JRadioButton("Scan Ampl.")
		scan_params_panel_1.add(self.scan_cav_amplitude_button)
		#------------------------------------------------------------
		min_cav_amp_label = JLabel(" Min=",JLabel.RIGHT)
		max_cav_amp_label = JLabel(" Max=",JLabel.RIGHT)
		cav_amp_points_label = JLabel(" Points=",JLabel.RIGHT)
		time_amp_scan_label = JLabel(" Ampl. Change Time[sec]=",JLabel.RIGHT)
		self.min_cav_amp_text = DoubleInputTextField(0.,DecimalFormat("#.####"),5)
		self.max_cav_amp_text = DoubleInputTextField(0.,DecimalFormat("#.####"),5)
		self.cav_amp_points_text = DoubleInputTextField(3,DecimalFormat("##"),3)
		self.time_amp_scan_text = DoubleInputTextField(20.,DecimalFormat("###"),3)
		scan_params_panel_1.add(min_cav_amp_label)
		scan_params_panel_1.add(self.min_cav_amp_text)
		scan_params_panel_1.add(max_cav_amp_label)
		scan_params_panel_1.add(self.max_cav_amp_text)
		scan_params_panel_1.add(cav_amp_points_label)
		scan_params_panel_1.add(self.cav_amp_points_text)
		scan_params_panel_1.add(time_amp_scan_label)
		scan_params_panel_1.add(self.time_amp_scan_text)
		#----------------------------------------------
		phase_step_label = JLabel("Step[deg]=",JLabel.RIGHT)
		phase_min_label = JLabel(" Min[deg]=",JLabel.RIGHT)
		phase_max_label = JLabel(" Max[deg]=",JLabel.RIGHT)
		phase_scan_time_step_label = JLabel(" Time/Step[sec]=",JLabel.RIGHT)
		self.phase_step_text = DoubleInputTextField(3.,DecimalFormat("##.##"),5)
		self.phase_min_text = DoubleInputTextField(-180.,DecimalFormat("####.#"),6)
		self.phase_max_text = DoubleInputTextField(180.,DecimalFormat("####.#"),6)
		self.phase_scan_time_step_text = DoubleInputTextField(1.5,DecimalFormat("##.#"),4)
		scan_params_panel_2.add(phase_step_label)
		scan_params_panel_2.add(self.phase_step_text)
		scan_params_panel_2.add(phase_min_label)
		scan_params_panel_2.add(self.phase_min_text)
		scan_params_panel_2.add(phase_max_label)
		scan_params_panel_2.add(self.phase_max_text)
		scan_params_panel_2.add(phase_scan_time_step_label)
		scan_params_panel_2.add(self.phase_scan_time_step_text)
		#----------------------------------------------
		cav_ampl_live_label = JLabel("Cavity Ampl.=",JLabel.RIGHT)
		cav_phase_live_label = JLabel(" Phase[deg]=",JLabel.RIGHT)
		self.cav_ampl_live_text = DoubleInputTextField(0.,DecimalFormat("#.###"),5)
		self.cav_phase_live_text = DoubleInputTextField(0.,DecimalFormat("####.##"),7)
		scan_params_panel_3.add(cav_ampl_live_label)
		scan_params_panel_3.add(self.cav_ampl_live_text)
		scan_params_panel_3.add(cav_phase_live_label)
		scan_params_panel_3.add(self.cav_phase_live_text)
		#-----------------------------------------------
		cntrl_upper_panel = JPanel(GridLayout(3,1,1,1))	
		cntrl_upper_panel.add(scan_params_panel_1)
		cntrl_upper_panel.add(scan_params_panel_2)
		cntrl_upper_panel.add(scan_params_panel_3)
		#----------------------------------------------
		scan_res_panel = JPanel(BorderLayout())
		#----------------------------------------------
		left_scan_res_panel_0 = JPanel(BorderLayout())
		scan_progress_panel = self.dtl_acc_scan_cavity_controller.scan_progress_bar.scan_progress_panel
		left_scan_res_panel_0.add(scan_progress_panel,BorderLayout.CENTER)
		#---------------------------------------------
		left_scan_res_panel_1 = JPanel(FlowLayout(FlowLayout.LEFT,3,1))
		make_analysis_button = JButton("Make Analysis")
		make_analysis_button.addActionListener(Make_Analysis_Of_Scan_Button_Listener(self.dtl_acceptance_scans_controller,self.dtl_acc_scan_cavity_controller))
		set_new_phase_button = JButton("Set New Phase to EPICS")
		set_new_phase_button.addActionListener(Set_New_Phase_Button_Listener(self.dtl_acceptance_scans_controller,self.dtl_acc_scan_cavity_controller))	
		left_scan_res_panel_1.add(make_analysis_button)
		left_scan_res_panel_1.add(set_new_phase_button)
		#----------------------------------------------
		left_scan_res_panel_2 = JPanel(FlowLayout(FlowLayout.LEFT,3,1))	
		new_cav_phase_label = JLabel("New Phase[deg]=",JLabel.RIGHT)
		self.new_cav_phase_text = DoubleInputTextField(0.,DecimalFormat("####.##"),7)
		left_scan_res_panel_2.add(new_cav_phase_label)
		left_scan_res_panel_2.add(self.new_cav_phase_text)
		#----------------------------------------------
		left_scan_res_panel_3 = JPanel(FlowLayout(FlowLayout.LEFT,3,1))
		shift_scan_button = JButton("Shift Scan by +10 deg")
		shift_scan_button.addActionListener(Shift_Scan_Button_Listener(self.dtl_acceptance_scans_controller,self.dtl_acc_scan_cavity_controller))
		make_pattern_button = JButton("Make a Pattern")
		make_pattern_button.addActionListener(Make_Pattern_Button_Listener(self.dtl_acceptance_scans_controller,self.dtl_acc_scan_cavity_controller))	
		left_scan_res_panel_3.add(shift_scan_button)
		left_scan_res_panel_3.add(make_pattern_button)
		#----------------------------------------------
		left_scan_res_panel_4 = JPanel(FlowLayout(FlowLayout.LEFT,3,1))	
		acc_scan_width_label = JLabel("Acc. Scan Width[deg]=",JLabel.RIGHT)
		self.acc_scan_width_text = DoubleInputTextField(0.,DecimalFormat("####.##"),7)
		left_scan_res_panel_4.add(acc_scan_width_label)
		left_scan_res_panel_4.add(self.acc_scan_width_text)
		#----------------------------------------------
		left_scan_res_panel_5 = JPanel(FlowLayout(FlowLayout.LEFT,3,1))	
		new_cav_amp_label = JLabel("New Cav. Amplitude  =",JLabel.RIGHT)
		self.new_cav_amp_text = DoubleInputTextField(0.,DecimalFormat("#.####"),7)
		left_scan_res_panel_5.add(new_cav_amp_label)
		left_scan_res_panel_5.add(self.new_cav_amp_text)	
		#----------------------------------------------
		scan_res_grid_panel = JPanel(GridLayout(6,1,1,1))
		scan_res_grid_panel.add(left_scan_res_panel_0)
		scan_res_grid_panel.add(left_scan_res_panel_1)
		scan_res_grid_panel.add(left_scan_res_panel_2)
		scan_res_grid_panel.add(left_scan_res_panel_3)
		scan_res_grid_panel.add(left_scan_res_panel_4)
		scan_res_grid_panel.add(left_scan_res_panel_5)
		scan_res_panel.add(scan_res_grid_panel,BorderLayout.NORTH)
		#----------------------------------------------
		self.scan_data_graph = Acceptance_Graphs_Panel_Holder(self.dtl_acceptance_scans_controller)
		self.add(cntrl_upper_panel,BorderLayout.NORTH)	
		self.add(self.scan_data_graph.getGraphsPanel(),BorderLayout.CENTER)
		self.add(scan_res_panel,BorderLayout.WEST)
		
	def getTimeScanEstimation(self):
		nAmpPoints = 1.
		time_amp_change = 0.
		if(self.scan_cav_amplitude_button.isSelected()):
			nAmpPoints = self.cav_amp_points_text.getValue()
			time_amp_change = nAmpPoints*self.time_amp_scan_text.getValue()
		nPhasePoints = (self.phase_max_text.getValue() - self.phase_min_text.getValue())/self.phase_step_text.getValue()
		time_scan = nAmpPoints*nPhasePoints*self.phase_scan_time_step_text.getValue() + time_amp_change
		return time_scan
		

class Acceptance_Graphs_Panel_Holder():
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		#----------------------------------------
		etched_border = BorderFactory.createEtchedBorder()
		self.gp_acc_scan = FunctionGraphsJPanel()
		self.gp_scan_width = FunctionGraphsJPanel()
		#------------------------------------------
		self.gp_acc_scan.setLegendButtonVisible(true)
		self.gp_scan_width.setLegendButtonVisible(true)
		#------------------------------------------	
		self.gp_acc_scan.setChooseModeButtonVisible(true)
		self.gp_scan_width.setChooseModeButtonVisible(true)
		#------------------------------------------
		self.gp_acc_scan.setName("Acceptance Scan: FC vs. RF Phase")
		self.gp_scan_width.setName("Acc. Width vs. RF Ampl")
		self.gp_acc_scan.setAxisNames("Cav Phase, [deg]","FC Q, [a.u.]")
		self.gp_scan_width.setAxisNames("RF Amplitude, [a.u]","Acceptance Width, [deg]")
		self.gp_acc_scan.setBorder(etched_border)
		self.gp_scan_width.setBorder(etched_border)
		#---------------------------------------------
		self.graphs_panel = JTabbedPane()
		self.graphs_panel.add("Acceptance Scan Data",self.gp_acc_scan)
		self.graphs_panel.add("Acc. Width",self.gp_scan_width)
		
	def getGraphsPanel(self):
		return self.graphs_panel
		
	def refreshGraphs(self):
		self.gp_acc_scan.refreshGraphJPanel()
		self.gp_scan_width.refreshGraphJPanel()

class Start_Stop_Panel(JPanel):
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller		
		self.setLayout(GridLayout(3,1,1,1))
		self.setBorder(BorderFactory.createEtchedBorder())
		#-----------------------------------------------------------
		start_selected_button = JButton("Start Scan for Selected Cavs")
		start_selected_button.addActionListener(Start_Scan_Selected_Cavs_Button_Listener(self.dtl_acceptance_scans_controller))		
		stop_button = JButton("Stop")
		stop_button.addActionListener(Stop_Scan_Button_Listener(self.dtl_acceptance_scans_controller))	
		send_amp_phase_to_EPICS_button = JButton("Send New Amp&Phase to EPICS for Selected Cavs")
		send_amp_phase_to_EPICS_button.addActionListener(Send_Amp_Phase_to_EPICS_Button_Listener(self.dtl_acceptance_scans_controller))	
		restore_amp_phase_to_EPICS_button = JButton("Restore Init Amp&Phase to EPICS for Selected Cavs")
		restore_amp_phase_to_EPICS_button.addActionListener(Restore_Amp_Phase_of_Selected_Cavs_to_EPICS_Button_Listener(self.dtl_acceptance_scans_controller))			
		self.keepPhases_RadioButton = JRadioButton("Keep Cavities Phases")
		self.keepAmps_RadioButton = JRadioButton("Keep Cavities Amplitudes")
		self.skipAnalysis_RadioButton = JRadioButton("Skip Analysis")
		#-----------------------------------------------------------
		self.status_text = JTextField(30)
		self.status_text.setForeground(Color.red)
		self.status_text.setText("Not running.")
		status_text_label = JLabel("Loop status:",JLabel.RIGHT)
		status_panel_tmp0 = JPanel(GridLayout(2,1,1,1))
		status_panel_tmp0.add(status_text_label)
		status_panel_tmp0.add(self.dtl_acceptance_scans_controller.acc_scan_loop_timer.time_estimate_label)
		status_panel_tmp1 = JPanel(GridLayout(2,1,1,1))
		status_panel_tmp1.add(self.status_text)
		status_panel_tmp1.add(self.dtl_acceptance_scans_controller.acc_scan_loop_timer.time_estimate_text)
		status_panel = JPanel(BorderLayout())
		status_panel.add(status_panel_tmp0,BorderLayout.WEST)
		status_panel.add(status_panel_tmp1,BorderLayout.CENTER)
		status_panel.setBorder(BorderFactory.createEtchedBorder())
		#------------------------------------------------
		buttons_panel0 = JPanel(FlowLayout(FlowLayout.LEFT,3,1))
		buttons_panel0.add(start_selected_button)
		buttons_panel0.add(stop_button)
		buttons_panel1 = JPanel(FlowLayout(FlowLayout.LEFT,3,1))
		buttons_panel1.add(self.skipAnalysis_RadioButton)
		buttons_panel1.add(self.keepPhases_RadioButton)
		buttons_panel1.add(self.keepAmps_RadioButton)
		buttons_panel = JPanel(GridLayout(2,1,1,1))
		buttons_panel.add(buttons_panel0)
		buttons_panel.add(buttons_panel1)
		#---------------------------------------
		bottom_buttons_panel0 = JPanel(FlowLayout(FlowLayout.LEFT,3,1))
		bottom_buttons_panel0.add(send_amp_phase_to_EPICS_button)
		bottom_buttons_panel1 = JPanel(FlowLayout(FlowLayout.LEFT,3,1))
		bottom_buttons_panel1.add(restore_amp_phase_to_EPICS_button)
		bottom_buttons_panel = JPanel(GridLayout(2,1,1,1))
		bottom_buttons_panel.add(bottom_buttons_panel0)
		bottom_buttons_panel.add(bottom_buttons_panel1)
		#---------------------------------------
		self.add(buttons_panel)	
		self.add(status_panel)
		self.add(bottom_buttons_panel)

#------------------------------------------------
#  JTable models
#------------------------------------------------

class Cavities_Table_Model(AbstractTableModel):
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		self.columnNames = ["Cavity",]
		self.columnNames += ["<html>&phi;<SUB>design</SUB>[deg]<html>",]
		self.columnNames += ["<html>A<SUB>init</SUB>[a.u.]<html>",]
		self.columnNames += ["<html>&phi;<SUB>init</SUB>[deg]<html>",]
		self.columnNames += ["<html>A<SUB>new</SUB>[a.u.]<html>",]
		self.columnNames += ["<html>&phi;<SUB>new</SUB>[deg]<html>",]
		self.columnNames += ["<html>FC<SUB>in</SUB><html>",]
		self.string_class = String().getClass()
		self.boolean_class = Boolean(true).getClass()
		
	def getColumnCount(self):
		return len(self.columnNames)
		
	def getRowCount(self):
		#---- it will be DTL 1-6
		return len(self.dtl_acceptance_scans_controller.cav_wrappers)

	def getColumnName(self,col):
		return self.columnNames[col]
		
	def getValueAt(self,row,col):
		cav_wrapper = self.dtl_acceptance_scans_controller.cav_wrappers[row]
		cav_acc_scan_cotroller = self.dtl_acceptance_scans_controller.cav_acc_scan_controllers[row]
		if(col == 0): return cav_wrapper.alias
		if(col == 1): return "%5.1f"%cav_wrapper.design_phase
		if(col == 2): return "%5.3f"%cav_wrapper.initAmp
		if(col == 3): return "%5.1f"%cav_wrapper.initPhase
		if(col == 4): return "%5.3f"%cav_wrapper.newAmp	
		if(col == 5): return "%5.1f"%cav_wrapper.newPhase
		if(col == 6): return cav_acc_scan_cotroller.isActuatorIn()
		return ""
				
	def getColumnClass(self,col):
		if(col == 6): return self.boolean_class
		return self.string_class		
	
	def isCellEditable(self,row,col):
		return false
			
	def setValueAt(self, value, row, col):
		cav_wrapper = self.dtl_acceptance_scans_controller.cav_wrappers[row]


#------------------------------------------------------------------------
#           Listeners
#------------------------------------------------------------------------
class Cavs_Table_Selection_Listener(ListSelectionListener):
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller	

	def valueChanged(self,listSelectionEvent):
		if(listSelectionEvent.getValueIsAdjusting()): return
		listSelectionModel = listSelectionEvent.getSource()
		index = listSelectionModel.getMinSelectionIndex()	
		cav_acc_scan_controller = self.dtl_acceptance_scans_controller.cav_acc_scan_controllers[index]
		tabbedPane = self.dtl_acceptance_scans_controller.tabbedPane		
		tabbedPane.setComponentAt(0,cav_acc_scan_controller.getMainPanel())
		tabbedPane.setComponentAt(1,cav_acc_scan_controller.getPatternPanel())
		tabbedPane.setSelectedIndex(0)
		tabbedPane.setTitleAt(0,cav_acc_scan_controller.cav_wrapper.alias)
		tabbedPane.setTitleAt(1,"Acceptance Scan Pattern")

class Init_Selected_Cavs_Button_Listener(ActionListener):
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		
	def actionPerformed(self,actionEvent):
		messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
		messageTextField.setText("")
		cav_selected_inds = self.dtl_acceptance_scans_controller.cav_table.getSelectedRows()
		if(len(cav_selected_inds) < 1 or cav_selected_inds[0] < 0):
			messageTextField.setText("Select one or more cavities to initialize!")	
			return
		ind_start = cav_selected_inds[0]
		ind_stop =  cav_selected_inds[len(cav_selected_inds)-1]
		self.dtl_acceptance_scans_controller.initAllCavControllers(ind_start,ind_stop)
		self.dtl_acceptance_scans_controller.cav_table.getModel().fireTableDataChanged()
		self.dtl_acceptance_scans_controller.cav_table.setRowSelectionInterval(ind_start,ind_stop)
		
class FC_In_Selected_Cavs_Button_Listener	(ActionListener):
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		
	def actionPerformed(self,actionEvent):
		messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
		messageTextField.setText("")
		cav_selected_inds = self.dtl_acceptance_scans_controller.cav_table.getSelectedRows()
		if(len(cav_selected_inds) < 1 or cav_selected_inds[0] < 0):
			messageTextField.setText("Select one or more cavities to put FC in!")	
			return
		ind_start = cav_selected_inds[0]
		ind_stop =  cav_selected_inds[len(cav_selected_inds)-1]
		for ind in range(ind_start,ind_stop+1):
			cav_acc_scan_controller = self.dtl_acceptance_scans_controller.cav_acc_scan_controllers[ind]
			if(not cav_acc_scan_controller.moveActuator(+1)): break
		time.sleep(1.5)
		self.dtl_acceptance_scans_controller.cav_table.getModel().fireTableDataChanged()
		
class FC_Out_Selected_Cavs_Button_Listener(ActionListener):
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		
	def actionPerformed(self,actionEvent):
		messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
		messageTextField.setText("")
		cav_selected_inds = self.dtl_acceptance_scans_controller.cav_table.getSelectedRows()
		if(len(cav_selected_inds) < 1 or cav_selected_inds[0] < 0):
			messageTextField.setText("Select one or more cavities to move FC out!")	
			return
		ind_start = cav_selected_inds[0]
		ind_stop =  cav_selected_inds[len(cav_selected_inds)-1]
		for ind in range(ind_start,ind_stop+1):
			cav_acc_scan_controller = self.dtl_acceptance_scans_controller.cav_acc_scan_controllers[ind]
			if(not cav_acc_scan_controller.moveActuator(+1)): break
		time.sleep(1.5)
		self.dtl_acceptance_scans_controller.cav_table.getModel().fireTableDataChanged()		
	
class Start_Scan_Selected_Cavs_Button_Listener(ActionListener):
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		
	def actionPerformed(self,actionEvent):
		messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
		messageTextField.setText("")
		if(self.dtl_acceptance_scans_controller.loop_run_state.isRunning):
			messageTextField.setText("The Acceptance Scans Loop is running already!")
			return
		runner = Acceptance_Scans_Loop_Runner(self.dtl_acceptance_scans_controller)
		thr = Thread(runner)
		thr.start()			
		
class Stop_Scan_Button_Listener(ActionListener):
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		
	def actionPerformed(self,actionEvent):
		messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
		messageTextField.setText("")
		if(not self.dtl_acceptance_scans_controller.loop_run_state.isRunning):
			messageTextField.setText("The Acceptance Scans Loop is not running!")
			return
		self.dtl_acceptance_scans_controller.loop_run_state.shouldStop = true		


class Send_Amp_Phase_to_EPICS_Button_Listener(ActionListener):
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		
	def actionPerformed(self,actionEvent):
		messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
		messageTextField.setText("")

class Restore_Amp_Phase_of_Selected_Cavs_to_EPICS_Button_Listener(ActionListener):
	def __init__(self,dtl_acceptance_scans_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		
	def actionPerformed(self,actionEvent):
		messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
		messageTextField.setText("")

class Make_Analysis_Of_Scan_Button_Listener(ActionListener):
	def __init__(self,dtl_acceptance_scans_controller,dtl_acc_scan_cavity_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		self.dtl_acc_scan_cavity_controller = dtl_acc_scan_cavity_controller
		
	def actionPerformed(self,actionEvent):
		messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
		messageTextField.setText("")

class Set_New_Phase_Button_Listener(ActionListener):
	def __init__(self,dtl_acceptance_scans_controller,dtl_acc_scan_cavity_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		self.dtl_acc_scan_cavity_controller = dtl_acc_scan_cavity_controller
		
	def actionPerformed(self,actionEvent):
		messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
		messageTextField.setText("")
		
class Shift_Scan_Button_Listener(ActionListener):
	def __init__(self,dtl_acceptance_scans_controller,dtl_acc_scan_cavity_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		self.dtl_acc_scan_cavity_controller = dtl_acc_scan_cavity_controller
		
	def actionPerformed(self,actionEvent):
		messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
		messageTextField.setText("")

class Make_Pattern_Button_Listener(ActionListener):
	def __init__(self,dtl_acceptance_scans_controller,dtl_acc_scan_cavity_controller):
		self.dtl_acceptance_scans_controller = dtl_acceptance_scans_controller
		self.main_loop_controller = self.dtl_acceptance_scans_controller.main_loop_controller
		self.dtl_acc_scan_cavity_controller = dtl_acc_scan_cavity_controller
		
	def actionPerformed(self,actionEvent):
		messageTextField = self.dtl_acceptance_scans_controller.getMessageTextField()
		messageTextField.setText("")

#------------------------------------------------------------------------
#           Controllers
#------------------------------------------------------------------------
class DTL_Acceptance_Scans_Controller:
	def __init__(self,top_document,accl):
		#--- top_document is a parent document for all controllers
		self.top_document = top_document
		self.main_loop_controller = self.top_document.main_loop_controller
		self.main_panel = JPanel(BorderLayout())
		#----etched border
		etched_border = BorderFactory.createEtchedBorder()
		#---------------------------------------------
		#---- Cavities' Controllers - only DTLs
		self.cav_acc_scan_controllers = []
		self.cav_wrappers = self.main_loop_controller.cav_wrappers[4:10]
		self.cav_acc_scan_controllers.append(DTL_Acc_Scan_Cavity_Controller(self,self.cav_wrappers[0],"FC160"))
		self.cav_acc_scan_controllers.append(DTL_Acc_Scan_Cavity_Controller(self,self.cav_wrappers[1],"FC248"))
		self.cav_acc_scan_controllers.append(DTL_Acc_Scan_Cavity_Controller(self,self.cav_wrappers[2],"FC334"))
		self.cav_acc_scan_controllers.append(DTL_Acc_Scan_Cavity_Controller(self,self.cav_wrappers[3],"FC428"))
		self.cav_acc_scan_controllers.append(DTL_Acc_Scan_Cavity_Controller(self,self.cav_wrappers[4],"FC524"))
		self.cav_acc_scan_controllers.append(DTL_Acc_Scan_Cavity_Controller(self,self.cav_wrappers[5],"FC104"))
		#----acceptance scans loop timer
		self.acc_scan_loop_timer = Acc_Scan_Loop_Timer(self)			
		#----------------------------------------------   
		self.tabbedPane = JTabbedPane()		
		self.tabbedPane.add("Cavity",JPanel(BorderLayout()))	
		self.tabbedPane.add("Pattern",JPanel(BorderLayout()))
		#--------------------------------------------------------
		self.cav_table = JTable(Cavities_Table_Model(self))
		self.cav_table.setSelectionMode(ListSelectionModel.SINGLE_INTERVAL_SELECTION)
		self.cav_table.setFillsViewportHeight(true)
		self.cav_table.setPreferredScrollableViewportSize(Dimension(500,120))
		self.cav_table.getSelectionModel().addListSelectionListener(Cavs_Table_Selection_Listener(self))
		scrl_cav_panel = JScrollPane(self.cav_table)
		#-------------------------------------------------------
		scrl_cav_panel.setBorder(BorderFactory.createTitledBorder(etched_border,"Cavities' Parameters"))
		init_buttons_panel = JPanel(FlowLayout(FlowLayout.LEFT,5,2))
		#---- initialization buttons
		init_selected_cavs_button = JButton("Init Selected Cavs")
		init_selected_cavs_button.addActionListener(Init_Selected_Cavs_Button_Listener(self))
		fc_in_selected_cavs_button = JButton("FC In for Selected Cavs")
		fc_in_selected_cavs_button.addActionListener(FC_In_Selected_Cavs_Button_Listener(self))	
		fc_out_selected_cavs_button = JButton("FC Out for Selected Cavs")
		fc_out_selected_cavs_button.addActionListener(FC_Out_Selected_Cavs_Button_Listener(self))
		init_buttons_panel.add(init_selected_cavs_button)
		init_buttons_panel.add(fc_in_selected_cavs_button)
		init_buttons_panel.add(fc_out_selected_cavs_button)
		#---- start stop buttons panel
		self.start_stop_panel = Start_Stop_Panel(self)
		#-------------------------------------------------
		tmp0_panel = JPanel(BorderLayout())
		tmp0_panel.add(init_buttons_panel,BorderLayout.NORTH)
		tmp0_panel.add(scrl_cav_panel,BorderLayout.CENTER)
		tmp0_panel.add(self.start_stop_panel,BorderLayout.SOUTH)
		tmp1_panel = JPanel(BorderLayout())
		tmp1_panel.add(tmp0_panel,BorderLayout.NORTH)
		#-------------------------------------------------
		left_panel = JPanel(BorderLayout())
		left_panel.add(tmp1_panel,BorderLayout.WEST)
		#--------------------------------------------------
		self.main_panel.add(left_panel,BorderLayout.WEST)
		self.main_panel.add(self.tabbedPane,BorderLayout.CENTER)
		#----------- loop state
		self.loop_run_state = Acc_Scans_Loop_Run_State()	
		#---- non GUI controllers
		
		
	def connectAllPVs(self):
		for cav_acc_scan_controller in self.cav_acc_scan_controllers:
			try:
				cav_acc_scan_controller.connectPVs()
			except:
				self.getMessageTextField().setText("Cannot connect PVs for cavity="+cav_acc_scan_controller.cav_wrapper.alias)
				return false
		return true
		
	def initAllCavControllers(self, ind_start = -1, ind_stop = -1):
		res = self.connectAllPVs()
		if(not res):
			return false
		if(ind_start < 0):
			ind_start = 0
			ind_stop = len(self.cav_acc_scan_controllers) - 1
		for cav_acc_scan_controller in self.cav_acc_scan_controllers[ind_start:ind_stop+1]:
			try:
				cav_acc_scan_controller.init()
			except:
				self.getMessageTextField().setText("Cannot read cavity's PVs! Cavity="+cav_acc_scan_controller.cav_wrapper.alias)
				return	false
		return true		

	def getMainPanel(self):
		return self.main_panel
		
	def getMessageTextField(self):
		return self.top_document.getMessageTextField()
		
	def writeDataToXML(self,root_da):
		dtl_scans_loop_cntrl_da = root_da.createChild("DTL_ACCPT_SCANS_CONTROLLER")

	def readDataFromXML(self,root_da):		
		dtl_scans_loop_cntrl_da = root_da.childAdaptor("DTL_ACCPT_SCANS_CONTROLLER")
		if(dtl_scans_loop_cntrl_da == null): return



