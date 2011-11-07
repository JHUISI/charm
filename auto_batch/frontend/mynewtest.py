from toolbox.pairinggroup import *
from charm.engine.util import *

m2 = ' asdf kafl  asdfk '
#m2 = 'this is a new test'
f_m2 = open('m2.pythonPickle', 'wb')
pickle.dump(m2, f_m2)
f_m2.close()
