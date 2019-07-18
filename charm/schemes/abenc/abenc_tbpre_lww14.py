'''
Qin Liu, Guojun Wang, Jie Wu
 
| From: Time-based proxy re-encryption scheme for secure data sharing in a cloud environment
| Published in: Information Sciences (Volume: 258, year: 2014)
| Available From: http://www.sciencedirect.com/science/article/pii/S0020025512006275
| Notes: 

* type:      ciphertext-policy attribute-based encryption (public key)
* setting:   Pairing

:Author:	artjomb
:Date:		07/2014
'''

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil

from functools import reduce

# taken from https://gist.github.com/endolith/114336
def gcd(*numbers):
    """Return the greatest common divisor of the given integers"""
    import sys
    if sys.version_info < (3, 5):
        from fractions import gcd
    else:
        from math import gcd
    return reduce(gcd, numbers)

# taken from https://gist.github.com/endolith/114336
def lcm(numbers):
    """Return lowest common multiple."""    
    def lcm(a, b):
        return (a * b) // gcd(a, b)
    return reduce(lcm, numbers, 1)

class TBPRE(object):
    def __init__(self, groupObj):
        self.util = SecretUtil(groupObj, verbose=False)  #Create Secret Sharing Scheme
        self.group = groupObj    #:Prime order group
        #self.users = {}
        #self.authorities = {}
    
    def setup(self, attributes):
        '''Global Setup (executed by CA)'''
        P0 = self.group.random(G1) # generator
        P1 = self.group.random(G1) # random element
        s = self.group.random()
        mk0 = self.group.random()
        mk1 = self.group.random()
        Q0 = P0 ** mk0
        SK1 = P1 ** mk0
        
        Htemp = lambda x, y: self.group.hash(x + y, ZR)
        H = {
            'user': lambda x: self.group.hash(str(x), ZR), # first convert G1 to str, then hash
            'attr': lambda x: Htemp(x,"_attribute"),
            'sy': lambda x: Htemp(x,"_year"),
            'sym': lambda x: Htemp(x,"_year_month"),
            'symd': lambda x: Htemp(x,"_year_month_day")
        }
        
        PK = { 'A': {}, 'Q0': Q0, 'P0': P0, 'P1': P1 }
        MK = { 'A': {}, 'mk0': mk0, 'mk1': mk1, 'SK1': SK1 }
        for attribute in attributes:
            ska = self.group.random()
            PKa = P0 ** ska
            PK['A'][attribute] = PKa
            MK['A'][attribute] = ska
        
        #self.MK = MK # private
        #self.s = s   # sent to cloud service provider
        #self.PK = PK # public
        
        return (MK, PK, s, H)
    
    def registerUser(self, PK, H):
        '''Registers a user by id (executed by user)'''
        sku = self.group.random()
        PKu = PK['P0'] ** sku
        mku = H['user'](PKu)
        
        #self.users[userid] = { 'PKu': PKu, 'mku': mku }
        return (sku, { 'PKu': PKu, 'mku': mku }) # (private, public)
    
    def hashDate(self, H, time, s):
        hash = s
        key = 'y'
        if "year" in time:
            hash = H['sy'](time['year']) ** hash
        else:
            print("Error: time has to contain at least 'year'")
            return None, None
        if "month" in time:
            hash = H['sym'](time['month']) ** hash
            key = 'ym'
            if "day" in time:
                hash = H['symd'](time['day']) ** hash
                key = 'ymd'
        elif "day" in time:
            print("Error: time has to contain 'month' if it contains 'year'")
            return None, None
        return hash, key
    
    def timeSuffices(self, timeRange, needle):
        # assumes that the time obj is valid
        if timeRange['year'] != needle['year']:
            return False
        if 'month' not in timeRange:
            return True
        if 'month' not in needle:
            return None # Error
        if timeRange['month'] != needle['month']:
            return False
        if 'day' not in timeRange:
            return True
        if 'day' not in needle:
            return None # Error
        return timeRange['day'] == needle['day']
    
    def policyTerm(self, user, policy):
        userAttributes = user['A'].keys()
        for i, term in zip(range(len(policy)), policy):
            notFound = False
            for termAttr in term:
                if termAttr not in userAttributes:
                    notFound = True
                    break
            if not notFound:
                return i
        return False
    
    def keygen(self, MK, PK, H, s, user, pubuser, attribute, time):
        '''Generate user keys for a specific attribute (executed by CA)'''
        
        hash, key = self.hashDate(H, time, s)
        if hash is None:
            return None
        
        if 'SKu' not in user:
            user['SKu'] = PK['P0'] ** (MK['mk1'] * pubuser['mku'])
        PKat = PK['A'][attribute] * (PK['P0'] ** hash)
        SKua = MK['SK1'] * (PKat ** (MK['mk1'] * pubuser['mku']))
        
        if 'A' not in user:
            user['A'] = {}
        if attribute not in user['A']:
            user['A'][attribute] = []
        user['A'][attribute].append((time, SKua))
    
    def encrypt(self, PK, policy, F):
        '''Generate the cipher-text from the content(-key) and a policy (executed by the content owner)'''
        r = self.group.random()
        nA = lcm(map(lambda x: len(x), policy))
        U0 = PK['P0'] ** r
        attributes = []
        U = []
        for term in policy:
            Ui = 1
            for attribute in term:
                Ui *= PK['A'][attribute]
            U.append(Ui ** r)
        V = F * pair(PK['Q0'], PK['P1'] ** (r * nA))
        return { 'A': policy, 'U0': U0, 'U': U, 'V': V, 'nA': nA }
        
    def decrypt(self, CT, user, term = None):
        '''Decrypts the content(-key) from the cipher-text (executed by user/content consumer)'''
        if term is None:
            term = self.policyTerm(user, CT['A'])
            if term is False:
                print("Error: user attributes don't satisfy the policy")
                return None
        
        sumSK = 1
        for attribute in CT['A'][term]:
            foundTimeSlot = False
            for timeRange, SKua in user['A'][attribute]:
                if self.timeSuffices(timeRange, CT['t']):
                    foundTimeSlot = True
                    sumSK *= SKua
                    break
            if not foundTimeSlot:
                print("Error: could not find time slot in user attribute keys")
                return None
        
        
        n = CT['nA'] // len(CT['A'][term])
        return CT['Vt'] / (pair(CT['U0t'], sumSK ** n) / pair(user['SKu'], CT['Ut']['year'][term] ** n)) # TODO: fix year
    
    def reencrypt(self, PK, H, s, CT, currentTime):
        '''Re-encrypts the cipher-text using the current time (executed by cloud service provider)'''
        if 'year' not in currentTime or 'month' not in currentTime or 'day' not in currentTime:
            print("Error: pass proper current time containing 'year', 'month' and 'day'")
            return None
        
        day = currentTime
        month = dict(day)
        del month['day']
        year = dict(month)
        del year['month']
        
        day, daykey = self.hashDate(H, day, s)
        month, monthkey = self.hashDate(H, month, s)
        year, yearkey = self.hashDate(H, year, s)
        
        rs = self.group.random()
        U0t = CT['U0'] * (PK['P0'] ** rs)
        
        Ut = { 'year': [], 'month': [], 'day': [] }
        for term, Ui in zip(CT['A'], CT['U']):
            Uit_year = Ui
            Uit_month = Ui
            Uit_day = Ui
            for attribute in term:
                Uit_year *= (PK['A'][attribute] ** rs) * (U0t ** year)
                Uit_month *= (PK['A'][attribute] ** rs) * (U0t ** month)
                Uit_day *= (PK['A'][attribute] ** rs) * (U0t ** day)
            Ut['year'].append(Uit_year)
            Ut['month'].append(Uit_month)
            Ut['day'].append(Uit_day)
        
        Vt = CT['V'] * pair(PK['Q0'], PK['P1'] ** (rs * CT['nA']))
        
        return { 'A': CT['A'], 'U0t': U0t, 'Ut': Ut, 'Vt': Vt, 'nA': CT['nA'], 't': currentTime }

def basicTest():
    print("RUN basicTest")
    groupObj = PairingGroup('SS512')
    tbpre = TBPRE(groupObj)
    attributes = ["ONE", "TWO", "THREE", "FOUR"]
    MK, PK, s, H = tbpre.setup(attributes)
    
    users = {} # public
    
    alice = { 'id': 'alice' }
    alice['sku'], users[alice['id']] = tbpre.registerUser(PK, H)
    alice2 = { 'id': 'alice2' }
    alice2['sku'], users[alice2['id']] = tbpre.registerUser(PK, H)
    
    year = { 'year': "2014" }
    pastYear = { 'year': "2013" }
    
    for attr in attributes[0:-1]:
        tbpre.keygen(MK, PK, H, s, alice, users[alice['id']], attr, year)
        tbpre.keygen(MK, PK, H, s, alice2, users[alice2['id']], attr, pastYear)
    
    k = groupObj.random(GT)
    
    policy = [['ONE', 'THREE'], ['TWO', 'FOUR']] # [['ONE' and 'THREE'] or ['TWO' and 'FOUR']]
    currentDate = { 'year': "2014", 'month': "2", 'day': "15" }
    
    CT = tbpre.encrypt(PK, policy, k)
    CTt = tbpre.reencrypt(PK, H, s, CT, currentDate)
    PT = tbpre.decrypt(CTt, alice)
    
    assert k == PT, 'FAILED DECRYPTION! 1'
    print('SUCCESSFUL DECRYPTION 1')
    
    PT2 = tbpre.decrypt(CTt, alice2)
    
    assert k != PT2, 'SUCCESSFUL DECRYPTION! 2'
    print('DECRYPTION correctly failed')

def basicTest2():
    '''Month-based attributes are used'''
    print("RUN basicTest2")
    groupObj = PairingGroup('SS512')
    tbpre = TBPRE(groupObj)
    attributes = ["ONE", "TWO", "THREE", "FOUR"]
    MK, PK, s, H = tbpre.setup(attributes)
    
    users = {} # public
    
    alice = { 'id': 'alice' }
    alice['sku'], users[alice['id']] = tbpre.registerUser(PK, H)
    
    year = { 'year': "2014", 'month': '2' }
    
    for attr in attributes[0:-1]:
        tbpre.keygen(MK, PK, H, s, alice, users[alice['id']], attr, year)
    
    k = groupObj.random(GT)
    
    policy = [['ONE', 'THREE'], ['TWO', 'FOUR']] # [['ONE' and 'THREE'] or ['TWO' and 'FOUR']]
    currentDate = { 'year': "2014", 'month': "2", 'day': "15" }
    
    CT = tbpre.encrypt(PK, policy, k)
    CTt = tbpre.reencrypt(PK, H, s, CT, currentDate)
    PT = tbpre.decrypt(CTt, alice)
    
    assert k == PT, 'FAILED DECRYPTION!'
    print('SUCCESSFUL DECRYPTION')

def test():
    # print 1, lcm(1, 2)
    print(2, lcm([1, 2]))

if __name__ == '__main__':
    basicTest()
    # basicTest2()
    # test()
