from toolbox.pairinggroup import *
from charm.engine.util import *

#m0 = 'hello'
m0 = 'try me instead'
f_m0 = open('m1BLS.pythonPickle', 'wb')
pickle.dump(m0, f_m0)
f_m0.close()


#m1 = 'bye'
m1 = 'instead use this'
f_m1 = open('m2BLS.pythonPickle', 'wb')
pickle.dump(m1, f_m1)
f_m1.close()

m2 = 'goodbye'
#m2 = 'this is a new test'
f_m2 = open('m3BLS.pythonPickle', 'wb')
pickle.dump(m2, f_m2)
f_m2.close()




