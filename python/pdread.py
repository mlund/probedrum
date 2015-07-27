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

  Example:

    d = MXWdata().load( "myfile.mxw" )
    d.parse( 't E A(500,510)/A(410/415)' )

  where the math and the following keywords can be used:

  - `E`  = electrode value
  - `t` = time in deciseconds
  - `T` = temperature
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

  def parse( self, expr ):
    """ Convert expression string to list """
    t = self.prop["DSEC"]
    E  = self.prop["ELE"]
    V  = self.prop["VOL"]
    T = self.prop["TEMP"]
    C = self.prop["CONC"]
    S = self.prop["SPEC"]
    expr = expr.replace("A", "self.absorbance")
    row = []
    for i in expr.split():
      exec 'row.append(' + i + ')'
    return row

# If run as main program (instead of as module)
if __name__ == "__main__":
  import argparse, parser

  ps = argparse.ArgumentParser( description='Read Probe Drum MXW data files' )
  ps.add_argument( '--plot', type=int, nargs=2, default=[0,0], help='plot columns')
  ps.add_argument( '--fmt', type=str, nargs=1, default='t E A(500,510)',\
      help = 'output format string where \
          t=time; E=electrode; T=temp; V=vol; C=conc; \
          A(..,..)=avg. absorbance.\
          Default: \"%(default)s\". Python math is allowed:\
          --fmt \"t T+298.15 A(420,425) / A(500,501)\"')
  ps.add_argument( 'files', nargs='+', type=str, help='List of MXW ascii files' )
  args = ps.parse_args()

  timedata = []                       # list w. ALL data from every file
  for file in args.files:
    timedata.append( MXWdata().load( file ) )

  d = []                              # list w. select data from every file
  for i in timedata:
    args.fmt = ''.join( args.fmt )
    d.append( i.parse( args.fmt ) )

  for row in d:
    print " ".join( map(str, row) )   # print to screen, filter out brackets

  colx = args.plot[0]
  coly = args.plot[1]
  if colx != coly:
    import matplotlib.pyplot as plt
    m = np.array( d )
    plt.plot( m[:,colx], m[:,coly] )
    plt.show()
