//
//  CAServer.java
//  xal
//
//  Created by Tom Pelaia on 4/28/2009.
//  Copyright 2009 Oak Ridge National Lab. All rights reserved.
//

package xal.app.virtualaccelerator;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import xal.ca.Channel;
import xal.ca.IServerChannel;
import xal.smf.AcceleratorNode;
import xal.smf.AcceleratorSeq;
import xal.smf.TimingCenter;
import xal.smf.impl.BLM;
import xal.smf.impl.BPM;
import xal.smf.impl.Bend;
import xal.smf.impl.CurrentMonitor;
import xal.smf.impl.Electromagnet;
import xal.smf.impl.ExtractionKicker;
import xal.smf.impl.HDipoleCorr;
import xal.smf.impl.MagnetMainSupply;
import xal.smf.impl.MagnetTrimSupply;
import xal.smf.impl.ProfileMonitor;
import xal.smf.impl.Quadrupole;
import xal.smf.impl.RfCavity;
import xal.smf.impl.Sextupole;
import xal.smf.impl.Solenoid;
import xal.smf.impl.TrimmedQuadrupole;
import xal.smf.impl.VDipoleCorr;
import xal.smf.impl.WireScanner;
import xal.smf.impl.qualify.AndTypeQualifier;
import xal.smf.impl.qualify.KindQualifier;
import xal.smf.impl.qualify.NotTypeQualifier;
import xal.smf.impl.qualify.QualifierFactory;
import xal.smf.impl.qualify.TypeQualifier;


/**
 * Server channel access
 * 
 * @version 0.2 13 Jul 2015
 * @author unkwnon
 * @author Blaz Kranjc <blaz.kranjc@cosylab.com>
 */
public class VAServer {	
	/** The sequence for which to server channels */
	final private AcceleratorSeq SEQUENCE;
	
	
	final protected static int DEFAULT_ARRAY_SIZE = 1024;
	/**
	 * Constructor
	 * @param sequence The sequence for which to serve channels
	 */
	public VAServer( final AcceleratorSeq sequence ) throws Exception {
		SEQUENCE = sequence;
		
		/** register channels for the sequence's nodes */
		registerNodeChannels();
	}
	
	
	/** dispose of the context */
	public void destroy() throws Exception {
	    //Nothing to do here.
	}
	
	
	/**
	 * Write the PCAS input file for the list of PVs in the usual nodes
	 * @param writer The writer to which to output the PCAS file
	 */
	private void registerNodeChannels() throws Exception {
		registerNodeChannels( Quadrupole.s_strType, null, AndTypeQualifier.qualifierWithQualifiers( new KindQualifier( Quadrupole.s_strType ), new NotTypeQualifier( TrimmedQuadrupole.s_strType ) ) );		// untrimmed quads
		registerNodeChannels( TrimmedQuadrupole.s_strType );
		registerNodeChannels( Bend.s_strType );
		registerNodeChannels( Sextupole.s_strType );
		registerNodeChannels( HDipoleCorr.s_strType );
		registerNodeChannels( VDipoleCorr.s_strType );
		registerNodeChannels( ExtractionKicker.s_strType );
		registerNodeChannels( RfCavity.s_strType );
		registerNodeChannels( CurrentMonitor.s_strType );
		registerNodeChannels( BPM.s_strType );
		registerNodeChannels( BLM.s_strType );
		registerNodeChannels( Solenoid.s_strType );  
    // need to distinguish profile monitors from wire scanners which share the same type but have different soft types
		//registerNodeChannels( ProfileMonitor.s_strType, ProfileMonitor.SOFTWARE_TYPE, AndTypeQualifier.qualifierWithQualifiers( new KindQualifier( ProfileMonitor.s_strType ), QualifierFactory.getSoftTypeQualifier( ProfileMonitor.SOFTWARE_TYPE ) ) );
		registerNodeChannels( WireScanner.s_strType);
        
		registerTimingSignals();
	}
	
	
	/**
	 * Write to the PCAS input file the list of PVs for the specified node type.
	 * @param type node type for which to register channels
	 */
	private void registerNodeChannels( final String type ) throws IOException {
		registerNodeChannels( type, null, new KindQualifier( type ) );
	}
	
	
	/**
	 * Write to the PCAS input file the list of PVs for the specified node type.
	 * @param type node type for which to register channels
	 * @param nodeFilter a qualifier to filter which nodes to process
	 */
	private void registerNodeChannels( final String type, final String softType, final TypeQualifier nodeFilter ) throws IOException {
		final NodeSignalProcessor processor = NodeSignalProcessor.getInstance( type, softType );
		final List<SignalEntry> signals = new ArrayList<SignalEntry>();
		final TypeQualifier qualifier = QualifierFactory.qualifierForQualifiers( true, nodeFilter );
		final List<AcceleratorNode> nodes = SEQUENCE.getAllInclusiveNodesWithQualifier( qualifier );
		
        //System.out.println( "\n\ntype: " + type );
		for ( AcceleratorNode node : nodes ) {
            System.out.println( "\nnode: " + node.getId() + ", type: " + type + ", soft type: " + node.getSoftType() + ", status: " + node.getStatus() );
			final Collection<String> handles = processor.getHandlesToProcess( node );
            System.out.println( "handles: " + handles );
            for ( final String handle : handles ) {
				System.out.println( "Getting channel for handle: " + handle );
				final Channel channel = node.findChannel( handle );
				//System.out.println( "Channel with signal: " + channel.channelName() + " and validity: " + channel.isValid() );
				if ( channel != null && channel.isValid() ) {
					final String signal = channel.channelName();
					System.out.println( "Registering channel: " + signal + " for handle: " + handle );
					final SignalEntry entry = new SignalEntry( signal, handle );
					if ( !signals.contains( entry ) ) {
						signals.add( entry );
						if (channel instanceof IServerChannel)
							processor.appendLimits( entry, (IServerChannel)channel);
					}
				} else {
					System.err.println( "Warning! No valid channel for handle: " + handle );
				}
			}
		}
	}
	
	
	/**
	 * Write to the PCAS input file the list of timing signals.
	 */
	protected void registerTimingSignals() throws IOException {
		final TimingCenterProcessor processor = new TimingCenterProcessor();
		final List<SignalEntry> signals = new ArrayList<SignalEntry>();
		final TimingCenter timingCenter = SEQUENCE.getAccelerator().getTimingCenter();
		
		if ( timingCenter == null )  return;
		final Collection<String> handles = processor.getHandlesToProcess( timingCenter );
		
        for ( final String handle : handles ) {
			final Channel channel = timingCenter.getChannel( handle );
			if ( channel != null ) {
				final String signal = channel.channelName();
				final SignalEntry entry = new SignalEntry( signal, handle );
				if ( !signals.contains( entry ) ) {
					signals.add( entry );
					if (channel instanceof IServerChannel)
						processor.appendLimits( entry, (IServerChannel)channel);
				}
			}
		}
	}
}



/** Default processor for a signal */
abstract class SignalProcessor {
	protected abstract void appendLimits( final SignalEntry entry, final IServerChannel pv );
	
	
	protected void setLimits( final IServerChannel pv, final double lowerLimit, final double upperLimit ) {
		pv.setLowerDispLimit( lowerLimit );
		pv.setUpperDispLimit( upperLimit );
		
		pv.setLowerAlarmLimit( lowerLimit );
		pv.setUpperAlarmLimit( upperLimit );
		
		pv.setLowerCtrlLimit( lowerLimit );
		pv.setUpperCtrlLimit( upperLimit );
		
		pv.setLowerWarningLimit( lowerLimit );
		pv.setUpperWarningLimit( upperLimit );
	}
}



/**
 * Signal processor class for nodes.
 */
class NodeSignalProcessor extends SignalProcessor {
	/**
	 * Get the appropriate processor instance for the specified node type
	 * @param type The type of node for which to process the signals
	 * @return An instance of SignalProcessor or a subclass appropriate for the node type
	 */
	static public NodeSignalProcessor getInstance( final String type, final String softType ) {
		if ( type == Quadrupole.s_strType || type == Bend.s_strType || type == Solenoid.s_strType )  return new UnipolarEMProcessor();
		else if ( type == TrimmedQuadrupole.s_strType )  return new TrimmedQuadrupoleProcessor();
		else if ( type == BPM.s_strType )  return new BPMProcessor();
		else if ( type == VDipoleCorr.s_strType || type == HDipoleCorr.s_strType )  return new DipoleCorrectorProcessor();
		else if ( type == Sextupole.s_strType )  return new SextupoleProcessor();
		//else if ( type == ProfileMonitor.s_strType && softType == ProfileMonitor.SOFTWARE_TYPE )  return new ProfileMonitorProcessor();
 		else if ( type == WireScanner.s_strType )  return new WireScannerProcessor();
		else return new NodeSignalProcessor();
	}
	
	
	/**
	 * Get the handles we wish to process for a node.  By default we process all of a node's handles.  Subclasses may wish to override this method to return only a subset of handles.
	 * @param node The node whose handles we wish to get
	 * @return the collection of the node's handles we wish to process
	 */
	public Collection<String> getHandlesToProcess( final AcceleratorNode node ) {
		return node.getHandles();
	}


	@Override
	protected void appendLimits(SignalEntry entry, IServerChannel pv) {		
	}
}



/** Implement the processor for the ProfileMonitor.  This class returns only the X and Y sigma M handles. */
class ProfileMonitorProcessor extends NodeSignalProcessor {
	final static private Collection<String> HANDLES;
	
	// static initializer
	static {
		HANDLES = new ArrayList<String>();
		HANDLES.add( ProfileMonitor.H_SIGMA_M_HANDLE );
		HANDLES.add( ProfileMonitor.V_SIGMA_M_HANDLE );
	}
	
	
	/**
	 * Get the handles we wish to process for a node.  This processor overrides this method to return only the handles of interest for the node.
	 * @return the collection of the node's handles we wish to process
	 */
	public Collection<String> getHandlesToProcess( final AcceleratorNode node ) {
		return HANDLES;
	}	
}



/** Implement the processor for the WireScanner. */
class WireScannerProcessor extends NodeSignalProcessor {
	final static private Collection<String> HANDLES;
	
	// static initializer
	static {
		HANDLES = new ArrayList<String>();
    HANDLES.add( WireScanner.HORIZONTAL_SIGMA_GAUSS_HANDLE );
		HANDLES.add( WireScanner.VERTICAL_SIGMA_GAUSS_HANDLE );
	}
	
	
	/**
	 * Get the handles we wish to process for a node.  This processor overrides this method to return only the handles of interest for the node.
	 * @return the collection of the node's handles we wish to process
	 */
	public Collection<String> getHandlesToProcess( final AcceleratorNode node ) {
		return HANDLES;
	}	
}


/** Implement the processor for the WireScanner2. */
class WireScanner2Processor extends NodeSignalProcessor {
    final static private Collection<String> HANDLES;
    
    // static initializer
    static {
        HANDLES = new ArrayList<String>();
        // TODO: add wirescanner 2 handles
//        HANDLES.add( WireScanner2.HORIZONTAL_SIGMA_GAUSS_HANDLE );
//        HANDLES.add( WireScanner2.VERTICAL_SIGMA_GAUSS_HANDLE );
    }
    
    
    /**
     * Get the handles we wish to process for a node.  This processor overrides this method to return only the handles of interest for the node.
     * @return the collection of the node's handles we wish to process
     */
    public Collection<String> getHandlesToProcess( final AcceleratorNode node ) {
        return HANDLES;
    }   
}


/** Signal processor appropriate for processing sextupole electro magnets */
class SextupoleProcessor extends NodeSignalProcessor {
	static final private Set<String> LIMIT_HANDLES;
	
	
	//Static initializer for setting constant values
	static {		
		LIMIT_HANDLES = new HashSet<String>();
		LIMIT_HANDLES.add( Electromagnet.FIELD_RB_HANDLE );
		LIMIT_HANDLES.add( MagnetMainSupply.FIELD_SET_HANDLE );
		LIMIT_HANDLES.add( MagnetMainSupply.FIELD_RB_HANDLE );
	}
	
	
	protected void appendLimits( final SignalEntry entry, final IServerChannel pv ) {
		if ( LIMIT_HANDLES.contains( entry.getHandle() ) ) {
			setLimits( pv, -10.0, 10.0 );
		}
	}
}



/** Signal processor appropriate for processing unipolar electro magnets */
class UnipolarEMProcessor extends NodeSignalProcessor {
	static final private Set<String> LIMIT_HANDLES;
	
	
	//Static initializer for setting constant values
	static {		
		LIMIT_HANDLES = new HashSet<String>();
		LIMIT_HANDLES.add( Electromagnet.FIELD_RB_HANDLE );
		LIMIT_HANDLES.add( MagnetMainSupply.FIELD_SET_HANDLE );
		LIMIT_HANDLES.add( MagnetMainSupply.FIELD_RB_HANDLE );
		LIMIT_HANDLES.add( MagnetMainSupply.FIELD_BOOK_HANDLE );
	}
	
	@Override
	protected void appendLimits( final SignalEntry entry, final IServerChannel pv ) {
		if ( LIMIT_HANDLES.contains( entry.getHandle() ) ) {
			setLimits( pv, 0.0, 50.0 );
		}
	}
}



/** Signal processor appropriate for processing trimmed quadrupoles */
class TrimmedQuadrupoleProcessor extends NodeSignalProcessor {
	static final private Set<String> MAIN_LIMIT_HANDLES;
	static final private Set<String> TRIM_LIMIT_HANDLES;
	
	
	// Static initializer for setting constant values
	static {		
		MAIN_LIMIT_HANDLES = new HashSet<String>();
		MAIN_LIMIT_HANDLES.add( Electromagnet.FIELD_RB_HANDLE );
		MAIN_LIMIT_HANDLES.add( MagnetMainSupply.FIELD_SET_HANDLE );
		MAIN_LIMIT_HANDLES.add( MagnetMainSupply.FIELD_RB_HANDLE );
		MAIN_LIMIT_HANDLES.add( MagnetMainSupply.FIELD_BOOK_HANDLE );
		
		TRIM_LIMIT_HANDLES = new HashSet<String>();
		TRIM_LIMIT_HANDLES.add( MagnetTrimSupply.FIELD_RB_HANDLE );
		TRIM_LIMIT_HANDLES.add( MagnetTrimSupply.FIELD_SET_HANDLE );
	}
	
	
	protected void appendLimits( final SignalEntry entry, final IServerChannel pv ) {
		if ( MAIN_LIMIT_HANDLES.contains( entry.getHandle() ) ) {
			setLimits( pv, 0.0, 50.0 );
		}
		else if ( TRIM_LIMIT_HANDLES.contains( entry.getHandle() ) ) {
			setLimits( pv, -1.0, 1.0 );
		}
	}
}



/** Signal processor appropriate for processing BPMs */
class BPMProcessor extends NodeSignalProcessor {
	protected void appendLimits( final SignalEntry entry, final IServerChannel pv ) {
		final String handle = entry.getHandle();
		if ( BPM.AMP_AVG_HANDLE.equals( handle ) ) {
			setLimits( pv, 0.0, 50.0 );
		}
		else {
			setLimits( pv, -1000.0, 1000.0 );
		}
	}	
}



/** Signal processor appropriate for processing bends */
class BendProcessor extends NodeSignalProcessor {
	static final private Set<String> LIMIT_HANDLES;
	
	
	/**
	 * Static initializer for setting constant values
	 */
	static {		
		LIMIT_HANDLES = new HashSet<String>();
		LIMIT_HANDLES.add( Electromagnet.FIELD_RB_HANDLE );
		LIMIT_HANDLES.add( MagnetMainSupply.FIELD_SET_HANDLE );
		LIMIT_HANDLES.add( MagnetMainSupply.FIELD_RB_HANDLE );
	}
	
	
	
	protected void appendLimits( final SignalEntry entry, final IServerChannel pv ) {
		if ( LIMIT_HANDLES.contains( entry.getHandle() ) ) {
			setLimits( pv, -1.5, 1.5 );
		}
	}
}



/** Signal processor appropriate for processing dipole correctors */
class DipoleCorrectorProcessor extends NodeSignalProcessor {
	static final private Set<String> LIMIT_HANDLES;
	
	
	/**
	 * Static initializer for setting constant values
	 */
	static {
		LIMIT_HANDLES = new HashSet<String>();
		LIMIT_HANDLES.add( Electromagnet.FIELD_RB_HANDLE );
		LIMIT_HANDLES.add( MagnetMainSupply.FIELD_SET_HANDLE );
		LIMIT_HANDLES.add( MagnetMainSupply.FIELD_RB_HANDLE );
	}
	
	
	protected void appendLimits( final SignalEntry entry, final IServerChannel pv ) {
		if ( LIMIT_HANDLES.contains( entry.getHandle() ) ) {
			setLimits( pv, -0.01, 0.01 );
		}
	}
}



/** Implement the processor for the TimingCenter. */
class TimingCenterProcessor extends SignalProcessor {
	/**
	 * Get the handles from the TimingCenter.
	 * @param timingCenter The timing center whose handles we wish to get
	 * @return the collection of the node's handles we wish to process
	 */
	public Collection<String> getHandlesToProcess( final TimingCenter timingCenter ) {
		return timingCenter.getHandles();
	}

	@Override
	protected void appendLimits(SignalEntry entry, IServerChannel pv) {
	}
}



/** Signal/handle pair */
final class SignalEntry {
	final protected String _signal;
	final protected String _handle;
	
	
	/**
	 * Constructor
	 */
	public SignalEntry( final String signal, final String handle ) {
		_signal = signal;
		_handle = handle;
	}
	
	
	/**
	 * Get the signal
	 * @return the signal
	 */
	final public String getSignal() {
		return _signal;
	}
	
	
	/**
	 * Get the handle
	 * @return the handle
	 */
	final public String getHandle() {
		return _handle;
	}
	
	
	/**
	 * Two signal entries are equal if they have the same signal
	 * @param anObject The signal entry against which to compare
	 * @return true if the two signal entries have the same signal
	 */
	final public boolean equals( final Object anObject ) {
		return anObject instanceof SignalEntry && _signal.equals( ((SignalEntry)anObject).getSignal());
	}


	/** Override hashCode() as required for consistency with equals() */
	final public int hashCode() {
		return _signal.hashCode();
	}
}
