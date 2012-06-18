from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.zkp_compiler.zkp_generator import *
from socket import *
import sys
def main(argv):
    HOST, PORT = "", 8090
    party_info = {}
    if argv[1] == '-p':
        print("Operating as prover...")
        prover_sock = socket(AF_INET, SOCK_STREAM)
        prover_sock.connect((HOST, PORT))
        prover_sock.settimeout(15)
        user = 'prover'
        party_info['socket'] = prover_sock
    elif argv[1] == '-v':
        print("Operating as verifier...")
        svr = socket(AF_INET, SOCK_STREAM)
        svr.bind((HOST, PORT))
        svr.listen(1)
        verifier_sock, addr = svr.accept()
        print("Connected by ", addr)
        user = 'verifier'
        party_info['socket'] = verifier_sock
    else:
        print("ERROR!")
        exit(-1)

    group = PairingGroup('a.param')
    party_info['party'] = user
    party_info['setting'] = group
    # statement: '(h = g^x) and (j = g^y)'

    if(user == 'prover'):
        g = group.random(G1)
        x,y = group.random(ZR), group.random(ZR)
        pk = {'h':g ** x, 'g':g, 'j':g**y}
        sk = {'x':x, 'y':y}
    #    pk = {'h':g**x, 'g':g}
    #    sk = {'x':x, 'y':y}
        result = executeIntZKProof(pk, sk, '(h = g^x) and (j = g^y)', party_info)
        print("Results for PROVER =>", result)

    elif(user == 'verifier'):
        # verifier shouldn't have this information
    #    pk = {'h':1, 'g':1, 'j':1}
    #    sk = {'x':1, 'y':1} 
        pk = {'h':1, 'g':1, 'j':1}
        sk = {'x':1}
        result = executeIntZKProof(pk, sk, '(h = g^x) and (j = g^y)', party_info)
        print("Results for VERIFIER =>", result)
if __name__ == "__main__":
    main(sys.argv)
