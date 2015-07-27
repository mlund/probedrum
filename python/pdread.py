#!/usr/bin/env python

import numpy as np
import StringIO, glob, os, sys

"""
@desc   module for handling Probe Drum ascii data
@todo   only tested w. one spectrum
@date   july 2015, malmo
@author m. lund
"""

class MXWdata:
  """
  Load and structure a single .mxw ASCII file

  Data can be accessed using the keywords:

  - `ELE`  = electrode value
  - `DSEC` = time in deciseconds
  - `TIME` = real time as text
  - `TEMP` = temperature
  - `SPEC` = spectral data (matrix)

  To select between different spectra, use the `selSpec()` function (unfinished).
  """

  def __getitem__( self, key ): return self.prop[key]
  def wavelength( self ): return self.prop["SPEC"][:,0]
  def numSpec( self ): return self.prop["SPEC"].ndim

  def selSpec( self,i ):
    """ Select which recorded spectrum to use """
    if i < numSpec():
      self.ispec=i
    else:
      sys.exit( "Error: Requested spectrum not available." )

  def __init__( self ):
    self.prop = {}  # dict w all properties
    self.ispec = 0  # current spectrum id

  def absorbance( self, lmin=0, lmax=0 ):
    """ Get absorbance - full array or average in wavelengt interval """
    A = self.prop["SPEC"][:,1]
    if lmax>0:
      m = np.vstack( (self.wavelength(), A) ).T   # matrix w lambda and absorbance
      m = m[ m[:,0] >= lmin ]                     # slice by wavelength...
      m = m[ m[:,0] <= lmax ]
      return np.average( m[:,1] )                 # scalar
    return A                                      # array

  def load( self, file ):
    """ Load a single mxw file incl. header data and all spectra """
    s = open( file, 'U' ).read().replace(',','.') # convert CR and commas
    s = StringIO.StringIO( s )                    # a new, in-memory file
    for i in s.readline().split("\t"):            # loop over tab-separated header items
      key, val = i.split("=")
      try:
        self.prop[key] = float(val)               # convert to float and store...
      except ValueError:
        self.prop[key] = val                      # ...but not possible for text time stamp
    self.prop["SPEC"]  = np.loadtxt(s)            # store spectra as numpy matrix
    return self

def loaddir( path ):
  """ Returns list w all data as a function of time """
  if not os.path.isdir( path ):
    sys.exit( "Error: " + path + " is not a directory." )
  l = []
  for file in glob.glob( path + "/*.mxw" ):
    l.append( MXWdata().load( file ) )
  return l

# If run as main program (instead of as module)
if __name__ == "__main__":
  import getopt
  import matplotlib.pyplot as plt

  if len( sys.argv ) != 2:
    print "Usage:", sys.argv[0], "[directory name]"
  else:
    timedata = loaddir( sys.argv[1] )

    # example: matrix w. time, electrode output, and avg. absorbance
    m = np.empty( shape=[0,3] )
    for i in timedata:
      row = [ i["DSEC"], i["ELE"], i.absorbance(500,510) ]
      m = np.append( m, [row], axis=0 )

    for row in m:
      print " ".join( map(str, row) ) # print to screen

    time, pH, A = m.T                 # break out columns to indivial arrays
    plt.plot( time, A )               # ...and plot 
    plt.show()

