import datetime, json, numpy as np

# just some data
date = str(datetime.datetime.utcnow())
version = 1
revision = 2

# let's generate a spectrum
l = np.arange(500,520,2.0)
a = np.random.random(len(l))

d = {
        'comment' : 'Spectacular acid titration of acetic acid...',
        'operator': 'Gus McBain',
        'uctdate' : date,
        'version' : version,
        'revision' : revision,
        'samplepoints' : {
            '0' : {
                'uctdate' : date,
                'electrode' : 7.1,
                'temperature' : 298.15,
                'volume' : 40.,
                'absorbance_spectra' : {
                    "0" : {
                        'wavelength' : l.tolist(),
                        'absorbance' : a.tolist()
                        }
                    }
                }
            }
        }

print json.dumps( d , indent=4, separators=(',', ': '))

