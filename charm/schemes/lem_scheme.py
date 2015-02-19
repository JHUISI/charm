'''
Iraklis Leontiadis, Kaoutar Elkhiyaoui, Refik Molva(Aggregation Scheme)
   
| From: "Private and Dynamic Time-Series Data Aggregation with Trust Relaxation" 
| Published in: CANS 2014
| Available from: http://eprint.iacr.org/2014/256.pdf
 

   
type:           Plaintext Evaluation of the sum from encrypted values. 
setting:        Integer

Authors:    Iraklis Leontiadis
Date:            2/2015
'''
                          
#!/usr/bin/env python3
from charm.toolbox.integergroup import RSAGroup
from charm.schemes.pkenc.pkenc_paillier99 import Pai99
from charm.toolbox.integergroup import lcm,integer
from charm.toolbox.PKEnc import PKEnc
from charm.core.engine.util import *
from datetime import datetime
from time import mktime
import hashlib , os , math, sys, random
from fractions import gcd
from timeit import default_timer as timer

#This generates values of p,q,n and n2
global n,n2
group=RSAGroup()
pai=Pai99(group)
(public_key,secret_key)=pai.keygen()
npom=public_key['n']
n=int(npom)
nn=public_key['n2']
n2=int(nn)

def hash():
    '''
        Computing hash value of time
    '''
    t = datetime.now()
    d=t.strftime("%b/%d/%Y/%H:%M:%S")
    e=d.encode('utf-8')
    c=hashlib.sha256(e).hexdigest()
    htp=int(c,16)
    if htp < n2:
        if gcd(htp,n2) == 1:
            return htp
        else:
            hash()
    else:
        hash()

def secretkey():
    '''
        Generating random secret key smaller than n2
    '''
    b=os.urandom(256)
    ska=int.from_bytes(b, byteorder='big')
    if ska < n2:
        return ska
    else:
        secretkey()

class  Aggregator():
    '''
        Class for computing Pka and generating Ska
    '''

    def __init__(self):
        global pka,ht
        ht=hash()
        self.ska=secretkey()
        while 1:
            if gcd(self.ska,n2)==1:
                break
            else:
                self.ska=secretkey()
        self.pkap=pow(ht,self.ska,n2)
        pka=self.pkap

    def decrypt(self,*encarray):
        '''
            Decrypting the sum
        '''

        cprod=1
        #length=len(encarray)
        #for x in range(length):

         #   cprod=(cprod*int(encarray[x]))
         #   cprodfin=cprod%n2
        array = map(int, encarray)
        for x in array:
            cprod *= x
            cprod %= n2
        cprodfin=cprod
        pt=pow(cprodfin,self.ska,n2)
        auxin=modinv(auxt,n2)
        it=(pt*auxin)%n2-1
        pom1=it//n
        skapr=self.ska%n
        pom2=modinv(skapr,n)
        rez=(pom2*pom1)%n
        return rez
       

def encryptfunc(a,d):
    '''
        Encryption of one value, where a=plaintext(number), d=ski
    '''
    v1=pow(ht,d,n2)
    v2=(1+int(a)*n)%n2
    v3=(v1*v2)%n2
    rez=v3
    return rez

def auxiliaryfunc(b):
    '''
        Auxiliary information of one value, where  b=ski 
    '''
    rez=pow(pka,b,n2)
    return rez

def egcd(a, b):
    '''
        Extended Euclidian gcd function between a and b
    '''
    x,y, u,v = 0,1, 1,0
    while a != 0:
        q, r = b//a, b%a
        m, n = x-u*q, y-v*q
        b,a, x,y, u,v = a,r, u,v, m,n
    gcd = b
    return gcd, x, y

def modinv(a, m):
    '''
        Finding modulo inverse of a mod m
    '''
    gcd, x, y = egcd(a, m)
    if gcd != 1:
        return None  # modular inverse does not exist
    else:
        return x % m


class Users():
    '''
        Computing users secret keys(ski) for users list *userdata
    '''

    def __init__(self,*userdata):

        self.i=len(userdata)
        self.dat=[int(userdata[x]) for x in range(self.i)]
        self.sk=[secretkey() for x in range(self.i)]

    def encrypt(self):
        '''
            Encrypts all user data into a list
        '''

        encp=[encryptfunc(self.dat[x],self.sk[x]) for x in range(self.i)]
        return encp

    def auxiliary(self):
        '''
            Computes auxiliary for all users into a list
        '''

        array=[auxiliaryfunc(self.sk[x]) for x in range(self.i)]
        return array

class Collector():
    '''
        Computes auxt from list of auxiliary information from all users
    '''

    def __init__(self,*auxarray):

        global auxt
        auxtpom=1
        #length=len(auxarray)
        #for x in range(length):
        #    auxtpom=(auxtpom*int(auxarray[x]))%n2

        #auxt=auxtpom
        array = map(int, auxarray)
        for x in array:
            auxtpom *= x
            auxtpom %= n2
        auxt=auxtpom


if __name__=="__main__":

    for l in range(1):

        a=Aggregator()
        param=sys.argv #inputing number of users from command line
        pp=int(param[1])
        parameters=[random.randrange(1,int(param[2])) for x in range(pp)]
        fileinput = open("input_parameters"+str(l)+".txt","w")
        fileparam=str(parameters)
        fileinput.write(fileparam)
        fileinput.close()
        print("\n" + "N bit-size:",n.bit_length(),"\n")
        print("Step: 0\n""Data produced:\n\n",parameters,"\n")
        start=timer()
        sum(parameters)
        end=timer()
        print("Plaintext computations:\n""1. Overhead for the  sum of " +str(pp)+" values:", end-start,"seconds")
        print("2. Result=",sum(parameters),"\n")
        u=Users(*parameters)
        start1 = timer()
        enc=u.encrypt()
        end1=timer()
        print("Step: 1\n""Encryption:\n""3. Overall encryption overhead for " + str(pp) +" users:",end1-start1,"seconds")
        print("4. Average encryption overhead:", (end1-start1)/pp,"seconds"+"\n")
        fileenc=open("Output_enc"+str(l)+".txt","w")
        fileenc.write(str(enc))
        fileenc.close()
        start2=timer()
        aux=u.auxiliary()
        end2=timer()
        print("Step: 2\n""Auxiliary information:\n""5. Overall overhead for" +str(pp) + " users", end2-start2,"seconds")
        print("6. Computation time for auxiliary information per user:", (end2-start2)/pp,"seconds"+"\n")
        fileauxit=open("Output_auxit_values"+str(l)+".txt","w")
        fileauxit.write(str(aux))
        fileauxit.close()
        start3=timer()
        c=Collector(*aux)
        end3=timer()
        print("Step: 3\n""Collector\n""7. Auxiliary information aggregate overhead for "+str(pp)+" users:",end3-start3,"seconds"+"\n"+"\n")
        
        start4=timer()
        final=a.decrypt(*enc)
        end4=timer()
        print("Step: 4\n""Aggregator:\n""8. Decryption overhead for "+str(pp)+" users:",end4-start4,"seconds")
        print("9. Result=",final,"\n")
