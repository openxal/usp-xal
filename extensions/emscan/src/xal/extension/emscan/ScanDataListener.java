/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package xal.extension.emscan;

/**
 *
 * @author az9
 */
public interface ScanDataListener {
    public void dataReceived(double x, double xPrime, double[] waveForm);
}
