import datetime, json, numpy

# just some data
date = str(datetime.datetime.utcnow()) # date stamp in UCT format
cnt_samples = 1 # current sample count
cnt_spectra = 1 # current spectrum count

# let's generate an absorbance spectrum
l = numpy.arange(500,520,2.0)
a = numpy.random.random(len(l)).round(3)

d = {
        'comment' : 'Spectacular acid titration of acetic acid...',
        'operator': 'Gus McBain',
        'utcdate' : date,
        'version' : [1, 5, 2],     # software version
        'samplepoints' : {
            str(cnt_samples).zfill(4) : {
                'utcdate' : date,
                'electrode' : 7.1,
                'temperature' : 298.15,
                'volume' : 40.,
                'absorbance_spectra' : { # each sample point can have several spectra
                    str(cnt_spectra).zfill(2) : {
                        'wavelength' : l.tolist(),
                        'absorbance' : a.tolist()
                        }
                    }
                }
            }
        }

# pretty print
print json.dumps( d , indent=4, separators=(',', ': ')) + '\n'

# compact print
print json.dumps(d)

