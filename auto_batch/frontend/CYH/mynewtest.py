from toolbox.pairinggroup import *
from charm.engine.util import *

#m0 = 'please sign this new message!'
m0 = 'try me instead'
f_m0 = open('m0.pythonPickle', 'wb')
pickle.dump(m0, f_m0)
f_m0.close()


#m1 = 'asdfk k asdfasdf kasdf'
m1 = 'instead use this'
f_m1 = open('m1.pythonPickle', 'wb')
pickle.dump(m1, f_m1)
f_m1.close()

#m2 = ' asdf kafl  asdfk '
m2 = 'this is a new test'
f_m2 = open('m2.pythonPickle', 'wb')
pickle.dump(m2, f_m2)
f_m2.close()




