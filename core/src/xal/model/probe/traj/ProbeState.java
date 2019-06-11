package xal.model.probe.traj;

import xal.tools.data.DataAdaptor;
import xal.tools.data.DataFormatException;
import xal.model.probe.Probe;
import xal.model.xml.ParsingException;

/**
 * Stores a snapshot of a probes state at a particular instant in time.  Concrete
 * extensions to this class should be developed for each type of probe.
 * 
 * @author Craig McChesney
 * @author Christopher K. Allen
 * 
 * @version June 26, 2014
 * 
 */
public abstract class ProbeState<S extends ProbeState<S>> implements IProbeState {



    /*
     * Global Constants
     */	
     
    // *********** I/O Support

    /** element tag for the probe state data */        
    public final static String STATE_LABEL = "state";
    
    /** attribute tag for concrete type of probe state */
    protected final static String TYPE_LABEL = "type";    
    
    
    /** element tag for locate state data */
    private final static String LOCATION_LABEL = "location";
    
    /** attribute tag for associated lattice element */
    private final static String ELEMENT_LABEL = "elem";
    
    /** attribute tag for probe elapsed time */
    private final static String TIME_LABEL = "t";

    /** attribute tag for probe position */
    private final static String POSITION_LABEL = "s";
    
    /** attribute tag for probe kinetic energy */
    private final static String KINETICENERGY_LABEL = "W";
    
    
    
    /** element tag for particle species data */
    private final static String SPECIES_LABEL = "species";
    
    /** attribute tag for particle charge */
    private final static String PARTCHARGE_LABEL="q";
    
    /** attribute tag for particle rest energy */
    private final static String PARTRESTENERGY_LABEL="Er";
    
    /*
     * Local Attributes
     */
     
    /** Species charge */
    private double  m_dblParQ = 0.0;
    
    /** Species rest energy */
    private double  m_dblParEr = 0.0;
    

    /** element id */
    private String m_strElemId = "";
    
    /** hardware node ID */
    private String  strSmfId = "";

    /** Current probe position in beamline */
    private double m_dblPos = 0.0;
    	    
    /** The time elapsed from the beginning of the tracking (sec) */
     private double m_dblTime = 0.0;

    /** Probe's average kinetic Energy */
    private double  m_dblW = 0.0;

    /** Probe's relativistic gamma */
    private double  m_dblGamma = Double.NaN;
    
    private double m_dblBeta = 0.0;
    
//  CKA This does not belong here
//      We have not way of knowing whether or not the  
//      derived probe class actually has Twiss parameters.
//    
//    protected boolean bolSaveTwiss = false;
//    
    
    /*
     * Abstract Methods
     */
    
    /**
     * Creates a new clone of this object.
     * 
     * @return  a deep copy of this object.
     *
     * @author Christopher K. Allen
     * @since  Jun 26, 2014
     */
    public abstract S copy();
    
    
    /*
     * Initialization
     */

    /**
     *  Default constructor - creates an empty <code>ProbeState</code> object. 
     */    
    public ProbeState() {
    }
    
    /**
     * Copy constructor for ProbeState.  Initializes the new
     * <code>ProbeState</code> objects with the state attributes
     * of the given probe state.
     *
     * @param state     initializing state
     *
     * @author Christopher K. Allen
     * @since  Jun 26, 2014
     */
    public ProbeState(final S state) {
        
        this.m_dblParQ = state.getSpeciesCharge();
        this.m_dblParEr = state.getSpeciesRestEnergy();
        this.m_strElemId = state.getElementId();
        this.strSmfId = state.getHardwareNodeId();
        this.m_dblPos = state.getPosition();
        this.m_dblTime = state.getTime();
        this.m_dblW = state.getKineticEnergy();
        this.m_dblGamma = state.getGamma();
        this.m_dblBeta = state.getBeta();
    }
    
    /**
     * Initializing Constructor.  Creates a <code>ProbeState</code> object initialized
     * to the state of the <code>Probe</code> argument.
     * 
     * @param probe     <code>Probe</code> object containing initial values
     */
    public ProbeState(final Probe<S> probe) {
        this.setSpeciesCharge( probe.getSpeciesCharge() );
        this.setSpeciesRestEnergy( probe.getSpeciesRestEnergy() );

        this.setElementId( probe.getCurrentElement() );
        this.setHardwareNodeId( probe.getCurrentHardwareId() );
        this.setPosition( probe.getPosition() );
        this.setTime( probe.getTime() );
        this.setKineticEnergy( probe.getKineticEnergy() );
    }
    
    
    
    /*
     * Property Accessors
     */
    
    /** 
     *  Set the charge of the particle species in the beam 
     *  
     *  @param  q       species particle charge (<b>Coulombs</b>)
     */
    public void setSpeciesCharge(double q) { 
       this.m_dblParQ = q; 
    }
    
    
    /** 
     *  Set the rest energy of a single particle in the beam 
     *
     *  @param  Er      particle rest energy (<b>electron-volts</b>)
     */
    public void setSpeciesRestEnergy(double Er) { 
        this.m_dblParEr = Er; 
    }

    
    /** 
     *  Set the current position of the probe along the beamline.
     *
     *  @param  s       new probe position (<b>meters</b>)
     *
     *  @see    #getPosition
     */
    public void setPosition(double s) {
    	this.m_dblPos = s;
    }
    
    /** 
     * Set the current probe time elapsed from the start of the probe tracking.
     *  
     * @param   dblTime     elapsed time in <b>seconds</b>
     */
    public void setTime(double dblTime) {
        this.m_dblTime = dblTime; 
     }

    /**
     *  Set the current kinetic energy of the probe.
     *
     *  @param  W       new probe kinetic energy (<b>electron-volts</b>)
     *
     *  @see    #getKineticEnergy
     */
    public void setKineticEnergy(double W) {
        this.m_dblW = W;
        
        this.m_dblGamma = this.computeGammaFromW(m_dblW);
        this.m_dblBeta = this.computeBetaFromGamma(m_dblGamma);
    }
    
    /**
     * Set the lattice element id associated with this state.
     * 
     * @param id  element id of current lattice element
     */
    public void setElementId(String id) {
        m_strElemId = id;
    }
    
    /**
     * Sets the hardware node ID modeled by the element owning this state.
     * 
     * @param strSmfId  hardware ID of the state
     *
     * @author Christopher K. Allen
     * @since  Sep 3, 2014
     */
    public void setHardwareNodeId(String strSmfId) {
        this.strSmfId = strSmfId;
    }
    
//    //sako
//    public void setUseTwiss(boolean bool) {
//        bolSaveTwiss = bool;
//    }
//    

//    //sako
//    public boolean getUseTwiss() {
//        return bolSaveTwiss;
//    }
//

    /** 
     *  Returns the charge of probe's particle species 
     *  
     *  @return     particle species charge (<b>Coulombs</b>)
     */
    public double getSpeciesCharge() { 
    	return m_dblParQ; 
    }
    
    /** 
     *  Returns the rest energy of particle species 
     *
     *  @return     particle species rest energy (<b>electron-volts</b>)
     */
    public double getSpeciesRestEnergy() { 
    	return m_dblParEr; 
    }
    

    /** Returns the momentum
     * 
     * @return particle momentum
     */
    public double getMomentum() {
    	return (getSpeciesRestEnergy()*getGamma()*getBeta());
    }
    

    /**
     * Returns the id of the lattice element associated with this state.
     * 
     * @return  string ID of associated lattice element
     */
    public String getElementId() {
        return m_strElemId;
    }
    
    /**
     * Returns the identifier of the hardware node modeled by the
     * associated modeling element for this state.
     * 
     * @return  hardware ID of this state's modeling element
     *
     * @author Christopher K. Allen
     * @since  Sep 3, 2014
     */
    public String getHardwareNodeId() {
        return this.strSmfId;
    }
    
    /** 
     *  Returns the current beam-line position of the probe 
     *  
     *  @return     probe position (<b>meters</b>)
     */
    public double getPosition() {
        return m_dblPos;
    }
    
    /** 
     * Return the time elapsed from the start of the probe tracking
     * 
     * @return      time elapsed since probe began tracking, in <b>seconds</b> 
     */
    public double getTime() { 
        return m_dblTime;
    }
    
    /**
     *  Return the kinetic energy of the probe.  Depending upon the probe type,
     *  this could be the actual kinetic energy of a single constituent particle,
     *  the average kinetic energy of an ensemble, the design energy, etc.
     *
     *  @return     probe kinetic energy    (<b>electron-volts</b>)
     */
    public double getKineticEnergy() {
    	return m_dblW;
    }
    
    /** 
     *  Returns the probe velocity normalized to the speed of light. 
     *
     *  @return     normalized probe velocity v/c (<b>unitless</b>
     */
    public double getBeta() { 
    	return m_dblBeta;  
    }
    
    /**
     *  Return the relativistic gamma of the probe.  Depending upon the probe type,
     *  this could be the actual gamma of a single constituent particle,
     *  the average gamma of an ensemble, the design gamma, etc.
     *
     *  @return     probe kinetic energy    (<b>electron-volts</b>)
     */
    public double getGamma() {

        if (Double.isNaN(m_dblGamma))  {
            
            m_dblGamma = 1. + m_dblW / m_dblParEr;
        }
        
        return m_dblGamma;
    }

    
    /*
     * Object Overrides
     */

    /**
     *  Return a textual representation of the <code>ProbeState</code> internal state.
     * 
     *  @return     string containing current <code>ProbeState</code> state
     */
    @Override
    public String toString() {
    	return " elem: "     + getElementId() +
               " s=" + getPosition() + 
               " t=" + getTime() + 
               " W=" + getKineticEnergy();
    }
    
    
    
    /*
     * IArchive Interface
     */
// Sako,  Sorry I need to revive this
//  CKA - No way to know if Twiss parameters exist in this base class!    
//    
//    /**
//     * Save the state information to a data sink represented by 
//     * a <code>DataAdaptor</code> interface
//     * 
//     * @param   container   data source to receive state information
//     * @param  bolSaveTwiss    If want to dump Twiss parameters instead of correlation matrix, set it to 'true'
//     */
//    public void save(DataAdaptor container, boolean useTwiss) {
//        
//        DataAdaptor stateNode = container.createChild(STATE_LABEL);
//        stateNode.setValue(TYPE_LABEL, getClass().getName());
//        stateNode.setValue("id", this.getElementId());
//        
//        this.bolSaveTwiss = useTwiss;
//        addPropertiesTo(stateNode);
//    }
    
    /**
     * Save the state information to a data sink represented by 
     * a <code>DataAdaptor</code> interface
     * 
     * @param   daSink   data source to receive state information
     */
    public final void save(DataAdaptor daSink) {
        
        DataAdaptor stateNode = daSink.createChild(STATE_LABEL);
        stateNode.setValue(TYPE_LABEL, getClass().getName());
        stateNode.setValue("id", this.getElementId());
        
        addPropertiesTo(stateNode);
    }

    /**
     * Recovers the state information from a data source represented
     * by a <code>DataAdaptor</code> interface.
     * 
     * @param   container   data source containing state information
     * 
     *  @exception DataFormatException  data in <code>container</code> is malformated
     */    
    public final void load(DataAdaptor container) throws DataFormatException {
        try {
            readPropertiesFrom(container);
        } catch (ParsingException e) {
            e.printStackTrace();
            throw new DataFormatException("error loading from adaptor: " + 
                    e.getMessage());
        }
    }
    
    
    /** 
     *  Computes the relatavistic factor gamma from the current beta value
     *  
     *  @param  beta    speed of probe w.r.t. the speed of light
     *  @return         relatavistic factor gamma
     */
    protected double computeGammaFromBeta(double beta) { 
        return 1.0/Math.sqrt(1.0 - beta*beta); 
    }
    
    /**
     *  Convenience function for computing the relatistic factor gamma from the 
     *  probe's kinetic energy (using the particle species rest energy m_dblParEr).
     *
     *  @param  W       kinetic energy of the probe
     *  @return         relatavistic factor gamma
     */
    protected double computeGammaFromW(double W)   {
        double gamma = W/m_dblParEr + 1.0;
        
        return gamma;
    }
    
    /**
     *  Convenience function for computing the probe's velocity beta (w.r.t. the 
     *  speed of light) from the relatistic factor gamma.
     *
     *  @param gamma     relatavistic factor gamma
     *  @return         speed of probe (w.r.t. speed of light)
     */
    protected double computeBetaFromGamma(double gamma) {
        double beta = Math.sqrt(1.0 - 1.0/(gamma*gamma));

        return beta;
    }
    
    /** 
     *  Convenience function for multiplication of beta * gamma
     */
    protected double getBetaGamma() { 
    	return m_dblBeta*m_dblGamma; 
    }


    /*
     * Support Methods
     */    
     
    /**
     * Save the state information to a <code>DataAdaptor</code> interface.
     * 
     * @param  container   data sink with <code>DataAdaptor</code> interface
     */
    protected void addPropertiesTo(DataAdaptor container) {
        DataAdaptor  specNode = container.createChild(SPECIES_LABEL);
        specNode.setValue(PARTCHARGE_LABEL, getSpeciesCharge());
        specNode.setValue(PARTRESTENERGY_LABEL, getSpeciesRestEnergy());

        DataAdaptor locNode = container.createChild(LOCATION_LABEL);
        locNode.setValue(ELEMENT_LABEL, getElementId());
        locNode.setValue(POSITION_LABEL, getPosition());
        locNode.setValue(TIME_LABEL, getTime());
        locNode.setValue(KINETICENERGY_LABEL, getKineticEnergy());
    }
    
    /**
     * Recover the state information from a <code>DataAdaptor</code> interface.
     * 
     * @param container             data source with <code>DataAdaptor</code> interface
     * 
     * @throws ParsingException     data source is malformatted
     */
    protected void readPropertiesFrom(DataAdaptor container) 
    		throws ParsingException 
    {
        // Read particle species data
        DataAdaptor specNode = container.childAdaptor(SPECIES_LABEL);
        if (specNode == null)
            throw new ParsingException("ProbeState#readPropertiesFrom(): no child element = " + SPECIES_LABEL);
        
        if (specNode.hasAttribute(PARTCHARGE_LABEL))
            setSpeciesCharge(specNode.doubleValue(PARTCHARGE_LABEL));
        if (specNode.hasAttribute(PARTRESTENERGY_LABEL))
            setSpeciesRestEnergy(specNode.doubleValue(PARTRESTENERGY_LABEL));


        // Read state data
        DataAdaptor locNode = container.childAdaptor(LOCATION_LABEL);
        if (locNode == null)
            throw new ParsingException("ProbeState#readPropertiesFrom(): no child element = " + LOCATION_LABEL);

        if (locNode.hasAttribute(ELEMENT_LABEL))
            setElementId(locNode.stringValue(ELEMENT_LABEL));
        if (locNode.hasAttribute(POSITION_LABEL))        
            setPosition(locNode.doubleValue(POSITION_LABEL));
        if (locNode.hasAttribute(TIME_LABEL))
            setTime( locNode.doubleValue(TIME_LABEL));
        if (locNode.hasAttribute(KINETICENERGY_LABEL))
            setKineticEnergy(locNode.doubleValue(KINETICENERGY_LABEL));

    }
    
}
