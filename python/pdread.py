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
    if not os.path.isfile( file ):
      sys.exit( "Error: File ", file, " does not exist." )
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

# If run as main program (instead of as module)
if __name__ == "__main__":
  import argparse

  datakeys = ['DSEC', 'ELE', 'VOL', 'TEMP', 'CONC', 'ABS']

  parser = argparse.ArgumentParser( description='Read Probe Drum MXW data files' )
  parser.add_argument( '--plot',    action='store_true', help='plot using matplotlib' )
  parser.add_argument( '--plotfmt', type=str, nargs=2, default=['DSEC', 'ELE'], choices=datakeys,
      help='specify which two columns for plot')
  parser.add_argument( '--lrange',  type=float, nargs=2, default=[500,510],
      help='wavelength range for absorbance average [nm]' )
  parser.add_argument( 'files',     nargs='+', type=str, help='List of MXW ascii files' )
  args = parser.parse_args()

  timedata = []                       # list w. ALL data from every file
  for file in args.files:
    timedata.append( MXWdata().load( file ) )

  d = []                              # list w. select data from every file
  for i in timedata:
    row = []
    for key in datakeys:              # loop over all keys
      if key=="ABS":
        row.append( i.absorbance( *args.lrange ) )
      else:
        row.append( i[key] )
    d.append( row )

  for row in d:
    print " ".join( map(str, row) )   # print to screen

  if args.plot:
    import matplotlib.pyplot as plt
    m = np.array( d )
    colx = datakeys.index( args.plotfmt[0] )
    coly = datakeys.index( args.plotfmt[1] )
    plt.plot( m[:,colx], m[:,coly] )
    plt.show()
