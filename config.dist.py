from charm.toolbox.enum import Enum

libs = Enum('openssl', 'gmp', 'pbc', 'miracl', 'relic', 'ntl')

pairing_lib=libs 
ec_lib=libs 
lattice_lib=libs 
int_lib=libs 
