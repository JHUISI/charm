from toolbox.pairinggroup import *
from charm.engine.util import *

m0 = "m1"
m1 = "m2"
m2 = "m3"

f_m0 = open('m1.pythonPickle', 'wb')
pickle.dump(m0, f_m0)
f_m0.close()

f_m1 = open('m2.pythonPickle', 'wb')
pickle.dump(m1, f_m1)
f_m1.close()

f_m2 = open('m3.pythonPickle', 'wb')
pickle.dump(m2, f_m2)
f_m2.close()




