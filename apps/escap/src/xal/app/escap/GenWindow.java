/*
 * GenWindow.java
 *
 * Created on 06/16/2003 by cp3
 *
 */
 
package xal.app.escap;

import java.math.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.event.*;
import java.util.*;
import java.io.*;
import java.lang.*;
import java.text.NumberFormat;
import xal.extension.widgets.swing.*;
import xal.extension.application.*;
import java.net.URL;
import xal.tools.apputils.EdgeLayout;
/**
 * GenWindow is a subclass of XalWindow used in the ring optics application.  
 * This class implement a subclass of XalWindow to server as the 
 * main window of a document.  The window contains only view definitions and 
 * no model references.  It defines how the window looks and how to represent 
 * the document in graphical form.
 *
 * @author  cp3
 */

public class GenWindow extends XalWindow {

    private static final long serialVersionUID = 1L;
    
    private JPanel mainPanel;
 
    //  private Container mainPanel;

    /** Creates a new instance of MainWindow */
    public GenWindow(XalDocument aDocument) {
        super(aDocument);
	mainPanel = new JPanel();
	mainPanel.setVisible(true);
	BorderLayout layout = new BorderLayout();
	mainPanel.setLayout(layout);
	mainPanel.setPreferredSize(new Dimension(1200, 750));
	
	makeContent();
    }
    
    /**
     * Create the main window subviews.
     */
    protected void makeContent() {
	
	JTabbedPane tabbedPane = new JTabbedPane(JTabbedPane.TOP);

	JPanel scannerpanel = new JPanel(){
        private static final long serialVersionUID = 1L;
    };
	JPanel profilepanel = new JPanel(){
        private static final long serialVersionUID = 1L;
    };
	ScannerFace scannerface = new ScannerFace();
        ProfileFace profileface = new ProfileFace();
	
	scannerpanel.add(scannerface);
	profilepanel.add(profileface);
	tabbedPane.add("Raw Image Display", scannerpanel);
	tabbedPane.add("Profile Display", profilepanel);
        
	mainPanel = new JPanel();
	mainPanel.setVisible(true);
	mainPanel.setPreferredSize(new Dimension(1200, 750));
	mainPanel.setLayout(new BoxLayout(mainPanel, BoxLayout.Y_AXIS));
	//mainPanel.add(dataface);
	mainPanel.add(tabbedPane);
	//mainPanel.add(acclplotface);
	this.getContentPane().add(mainPanel);
	
	pack();
	
    }   

}

























