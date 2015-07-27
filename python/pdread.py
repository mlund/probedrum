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

  Example:

    d = MXWdata().load( "myfile.mxw" )
    d.parse( ['t', 'E', 'A(500,510)/A(410,415)'] )

  where math and the following keywords can be mixed:

  - `E` = electrode value (same as `pH`)
  - `t` = time [deciseconds]
  - `T` = temperature [degrees]
  - `A` = avg. absorbance in internal [nm]
  - `S` = spectral data (matrix)

  To select between different spectra, use the `selSpec()` function (unfinished).
  """

  #def __getitem__( self, key ): return self.prop[key]
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

  def parse( self, exprlist ):
    """ Parse list of expressions """
    t  = self.prop["DSEC"]
    E  = self.prop["ELE"]
    V  = self.prop["VOL"]
    T  = self.prop["TEMP"]
    C  = self.prop["CONC"]
    S  = self.prop["SPEC"]
    pH = E
    row = []
    for i in exprlist:
      i = i.replace("A", "self.absorbance")
      exec 'row.append(' + i + ')'
    return row

# If run as main program (instead of as module)
if __name__ == "__main__":
  import argparse
  from argparse import RawTextHelpFormatter

  ps = argparse.ArgumentParser( description='Read Probe Drum MXW data files', formatter_class=RawTextHelpFormatter )
  ps.add_argument( '--plot', type=int, nargs=2, default=[0,0], metavar=('xcol', 'ycol'),
      help='plot columns using matplotlib')
  ps.add_argument( '--fmt', nargs="+", type=str, default=('t', 'E', 'C'),\
      help = 'output format where:\n\n'
      't = time (deciseconds)\n'
      'E = electrode (pH may be used instead)\n'
      'T = temperature (degrees)\n'
      'V = sample volume (microliter)\n'
      'C = concentration (mM)\n'
      'S = spectrum (matrix)\n' 'A(..,..) = avg. absorbance in wavelength interval\n\n'
      'Examples:\n'
      '  --fmt t E C (default)\n'
      '  --fmt pH T+298.15 "A(420,425)/A(500,501)"\n'
      '  --fmt "min( S[:,0] )" (minumum wavelength)\n'
      '  --fmt "S[ np.argmax(S[:,1]) ][0] (wavelength w. min absorbance)\n'
      '  --fmt "max(S, key=lambda r: r[1] )[0]" (also wavelength w. max absorbance)')
  ps.add_argument( 'files', nargs='+', type=str, help='List of MXW ascii files' )
  args = ps.parse_args()

  timedata = []                       # list w. ALL data from every file
  for file in args.files:
    timedata.append( MXWdata().load( file ) )

  d = []                              # list w. select data from every file
  for i in timedata:
    d.append( i.parse( args.fmt ) )

  for row in d:
    print " ".join( map(str, row) )   # print to screen, filter out brackets

  colx, coly = args.plot
  if colx != coly:
    import matplotlib.pyplot as plt
    m = np.array( d )
    plt.plot( m[:,colx], m[:,coly] )
    plt.show()
