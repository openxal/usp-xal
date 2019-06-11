/*
 * Created on Feb 19, 2004
 *
 */
package xal.tools.math.poly;

/**
 * Represents a polynomial object with real coefficients over one real
 * variable.  This class is meant more as an encapsulation of a polynomial
 * function rather than an algebraic object, as is implemented in the
 * <code>JSci</code> mathematical/science package.
 *
 * @author Chris Allen
 *
 */
public class UnivariateRealPolynomial {

    /*
     *  Local Attributes
     */

     /** the vector of coefficients */
     private double[]   m_arrCoef = null;


     /*
      * Initialization
      */


    /**
     * Creates an empty polynomial object, the zero polynomial.
     */
    public UnivariateRealPolynomial() {
    }

    /**
     * Creates and initializes a polynomial to the specified coefficients.
     *
     * @param iOrder
     * @return
     */
    public UnivariateRealPolynomial(double[] arrCoef)   {
        this.setCoefArray(arrCoef);
    }

    /**
     * Set the entire coefficient array.  The coefficient
     * array is arranged in order of ascending indeterminate order.
     *
     * @param arrCoef   double array of coefficients.
     */
    public void setCoefArray(double[] arrCoef)   {
        this.m_arrCoef = arrCoef;
    }


    /*
     * Attribute Queries
     */


    /**
     * Return the degree of the polynomial.  That is, the highest
     * indeterminant order for all the nonzero coefficients.
     */
    public int  getDegree() {
        return this.getCoefs().length-1;
    }

    /**
     * Get the specified coefficient value.  The value of parameter
     * <code>iOrder</code> specifies order of the indeterminate.  For example,
     * calling <code>getCoef(2)</code> would return the coefficient for the
     * intdeterminate of second order.
     *
     * If the value of <code>iOrder</code> is larger than the size of the
     * coefficient array then the coefficient is assumed to have value zero.
     *
     * @param iOrder    order of the indeterminate
     * @return          coefficient of the specified indeterminate order
     */
    public double getCoef(int iOrder)   {
        if (this.m_arrCoef.length == 0)
            return 0.0;
        if (iOrder >= this.m_arrCoef.length)
            return 0.0;

        return this.m_arrCoef[iOrder];
    }

    /**
     * Return the entire array of polynomial coefficients.  The coefficient
     * array is arranged in order of ascending indeterminate order.
     *
     * @return      the entire coefficient array
     */
    public double[] getCoefs()      {
        return this.m_arrCoef;
    }



    /*
     *  Polynomial operations
     */

    /**
     * Evaluate the polynomial for the specifed value of the indeterminate.
     * If the coefficient vector has not been specified this
     * @param   dblVal      indeterminate value to evaluate the polynomial
     *
     * @author Chris Allen
     */
    public double evaluateAt(double dblVal) {
        if (this.m_arrCoef == null)
            return 0.0;

        int     N = this.m_arrCoef.length;      // number of coefficients
        double  dblAccum = 0.0;                 // accumulator

        for (int n=N-1; n>=0; n--)
		dblAccum += this.getCoef(n) * Math.pow(dblVal, n);

        return dblAccum;
    }

    /**
     * Evaluate derivative of the polynomial for the specifed value of the indeterminate.
     * If the coefficient vector has not been specified this
     * @param   dblVal      indeterminate value to evaluate the polynomial
     *
     * @author Chris Allen
     */
    public double evaluateDerivativeAt(double dblVal) {
        if (this.m_arrCoef == null)
            return 0.0;

        int     N = this.m_arrCoef.length;      // number of coefficients
        double  dblAccum = 0.0;                 // accumulator

        for (int n=N-1; n>=1; n--) {
					dblAccum += this.getCoef(n) * n* Math.pow(dblVal, n-1);
				}

        return dblAccum;
    }


    /**
     * Nondestructively add two polynomials.  The current polynomial and the
     * argument are added according to standard definitions (i.e., the
     * coefficient array is added vectorily).
     *
     * @param   polyAddend  polynomial to be added to this
     * @return              a new polynomial object representing the sum
     */
    public UnivariateRealPolynomial plus(UnivariateRealPolynomial polyAddend)  {
        UnivariateRealPolynomial    polySum;

        int nLen = Math.max(polyAddend.getDegree(), this.getDegree()) + 1;
        double[]  arrCoef = new double[nLen];

        for (int n=0; n<nLen; n++)  {
            arrCoef[n] = this.getCoef(n) + polyAddend.getCoef(n);
        }

        return new UnivariateRealPolynomial(arrCoef);
    }

    /**
     * Nondestructive multiply two polynomials.  The current polynomial and the
     * argument are multiplied according to standard definitions.
     *
     * @param polyFac   polynomial to be multiplied by this
     * @return          a new polynomial object representing the product
     */
    public UnivariateRealPolynomial times(UnivariateRealPolynomial polyFac) {
        UnivariateRealPolynomial    polyProd;

        int nLen = polyFac.getDegree() * this.getDegree() + 1;
        double[]  arrCoef = new double[nLen];
        double    dblAccum;

        for (int n=0; n<nLen; n++)  {
            dblAccum = 0;

            for (int i=0; i<=n; i++) {
                dblAccum += this.getCoef(i)*polyFac.getCoef(n-i);
            }
            arrCoef[n] = dblAccum;
        }

        return new UnivariateRealPolynomial(arrCoef);
    }


    /*
     * Testing and Debugging
     */



    /**
     * Construct and return a textual representation of the contents of this
     * polynomial as a <code>String</code> object.
     *
     * @return a String representation of the polynomial contents
     *
     * @see java.lang.Object#toString()
     */
    @Override
    public String toString() {
        int     N = this.getDegree();

        String  strPoly = Double.toString(this.getCoef(0));

        for (int n=1; n<=N; n++)
            strPoly += " + " + this.getCoef(n) + "x^" + n;

        return strPoly;
    }


    /**
     * Testing driver
     */
    public static void main(String args[])  {
        UnivariateRealPolynomial    poly1 = new UnivariateRealPolynomial( new double[]{1.0,2.0,3.0} );
        UnivariateRealPolynomial    poly2 = new UnivariateRealPolynomial( new double[]{1.1,1.2,1.3} );

        System.out.println("poly1 = " + poly1.toString());
        System.out.println("poly2 = " + poly2.toString());
        System.out.println("poly1 + poly2 = " + (poly1.plus(poly2)).toString());
        System.out.println("poly1 * poly2 = " + (poly1.times(poly2)).toString());
        System.out.println("poly1(1.0) = " + poly1.evaluateAt(1.0));
        System.out.println("poly1(2.0) = " + poly1.evaluateAt(2.0));
        System.out.println("poly2(1.0) = " + poly2.evaluateAt(1.0));
    }


}
