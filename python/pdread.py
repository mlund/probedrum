#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import StringIO, glob, os, sys, getopt, copy

"""
@desc   script for handling Probe Drum ascii data
@todo   only tested w. one spectrum
@date   july 2015, malmo
@author m. lund
"""

class PDData:
  """
  Load and structure a single .mxw ASCII file

  Data can be accessed using the keywords:

  - `ELE`  = electrode value
  - `DSEC` = time in deciseconds
  - `TIME` = real time as text
  - `TEMP` = temperature
  - `SPEC` = spectral data (matrix)

  To select between different spectra, use
  the `selSpec()` function (unfinished).
  """

  def __getitem__(self,key): return self.prop[key]
  def wavelength(self): return self.prop["SPEC"][:,0]
  def numSpec(self): return self.prop["SPEC"].ndim

  def selSpec(self,i):
    """ Select which recorded spectrum to use """
    if i < numSpec():
      self.ispec=i
    else:
      sys.exit("Error: Requested spectrum not available.")

  def __init__(self):
    self.prop = {}  # dict w all properties
    self.ispec = 0  # current spectrum id

  def absorbance(self, lmin=0, lmax=0):
    """ Get absorbance - full array or average in wavelengt interval """
    A = self.prop["SPEC"][:,1]
    if lmax>0:
      A = np.vstack( (self.wavelength(), A) ).T # matrix w lambda and absorbance
      A = A[ A[:,0] >= lmin ]                   # slice by wavelength...
      A = A[ A[:,0] <= lmax ]
      return np.average( A[:,1] )               # scalar
    return A                                    # array

  def load(self, file):
    """ Load a single mxw file incl. header data and all spectra """
    s = open(file, 'U').read().replace(',','.') # convert CR and commas
    s = StringIO.StringIO(s)                    # a new, in-memory file
    for i in s.readline().split("\t"):          # loop over tab-separated header items
      key, val = i.split("=")
      try:
        self.prop[key] = float(val)             # convert to float and store...
      except ValueError:
        self.prop[key] = val                    # ...but not possible for text time stamp
    self.prop["SPEC"]  = np.loadtxt(s)          # store spectra as numpy matrix
    return self

# Main program
if len(sys.argv)!=2:
  print "Usage:", sys.argv[0], "[directory name]"
else:
  path = sys.argv[1]
  if not os.path.isdir( path ):
    sys.exit("Error: " + path + " is not a directory.")

  timedata = [] # list w. all data as a function of time
  for file in glob.glob( path + "/*.mxw" ):
    timedata.append( PDData().load( file ) )

  # example: matrix w. time, electrode output, and avg. absorbance
  m = np.empty( shape=[0,3] )
  for i in timedata:
    m = np.append( m, [[ i["DSEC"], i["ELE"], i.absorbance(500,510) ]], axis=0 )

  time, pH, A = m.T  # break out columns to indivial arrays

  plt.plot( time, A ) 
  plt.show()

