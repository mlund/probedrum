#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import StringIO, glob, os, sys, getopt, copy

"""
@desc   Script for handling Probe Drum ascii data
@TODO   only tested w. one spectrum
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
  the `selSpec()` function.
  """

  def __getitem__(self,key): return self.prop[key]
  def wave(self): return self.prop["SPEC"][:,0]
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

  def abs(self, lmin=0, lmax=0):
    """ Get absorbance - full array or average in wavelengt interval """
    abs = self.prop["SPEC"][:,1]
    if lmax==0:
      return abs
    m = np.vstack( (self.wave(), abs) ).T       # matrix w lambda and absorbance
    m = m[ m[:,0] >= lmin ]
    m = m[ m[:,0] <= lmax ]
    return np.average( m[:,1] )

  def load(self, file):
    """ Load a single mxw data incl. header data and all spectra """
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

def fileList(path):
  """ Returns list of all .mxw files in directory """
  files = glob.glob( path+"/*.mxw" )
  if not files:
    sys.exit( "Error: No .mxw files found." )
  return files

# Main program
if len(sys.argv)!=2:
  print "Usage:", sys.argv[0], "[directory name]"
else:
  timedata = [] # list w. all data as a function of time
  for f in fileList( sys.argv[1] ):
    timedata.append( PDData().load(f) )

  # example: matrix w. time, electrode output, and avg. absorbance
  m = np.empty( shape=[0,3] )
  for i in timedata:
    m = np.append( m, [[ i["DSEC"], i["ELE"], i.abs(500,510) ]], axis=0 )

  time, pH, A = m.T  # break out columns to indivial arrays

  plt.plot( time, A ) 
  plt.show()
