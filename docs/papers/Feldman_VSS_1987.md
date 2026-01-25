# A Practical Scheme for Non-interactive Verifiable Secret Sharing

**Authors:** Paul Feldman

**Published:** FOCS 1987 (28th Annual Symposium on Foundations of Computer Science)

**URL:** https://www.cs.umd.edu/~gasarch/TOPICS/secretsharing/feldmanVSS.pdf

---



## Page 1

A Practical Scheme for Non-interactive Verifiable Secret Sharing
Paul Feldman
Massachusetts Institute of Technology
Abstract: This paper presents an extremely efficient,
the concept of a non-interactive VSS, in which a share
non-interactive
protocol for verifiable
secret sharing.
‘‘proves its own validity”. This widens the applicability
Verifiable secret sharing (VSS) is a way of bequeathing
of VSS to scenarios in which interaction is infeasible,
information to a set of processors such that a quorum of
such as sharing a secret among an entire nation. Also,
processors is needed to access the information. VSS is a
several executions of non-interactive protocols may be
fundamental tool of cryptography and distributed com- — yn in parallel. By contrast, interactive schemes may
puting. Seemingly difficult problems such as secret bid-
—_have to be run serially. Thus, non-interaction allows us
ding, fair voting, leader election, and flipping a fair coin
to use VSS as a subroutine without increasing the round
have simple one-round reductions to VSS. There is a
complexity.
constant-round reduction from Byzantine Agreement to
non-interactive
VSS.
Non-interactive
VSS
provides
.
asynchronous networks with a constant-round simula-
1.2 History of the Problem
tion of simultaneous broadcast networks whenever even
Chor, Goldwasser, Micali, and Awerbuch [CGMA]
a bare majority of processors are good. VSS is constantly
introduced the notion of VSS. They present a constant
repeated in the simulation of fault-free protocols by
round interactive scheme for verifiable secret sharing
faulty
systems.
As
verifiable
secret
sharing
is
a
based on the assumed intractability of factorization. In
bottleneck for so many results,
it is essential to find
their solution, t=O(logn), u=O(n); the communica-
efficient solutions.
tion complexity is exponential in ¢.
The powerful zero-knowledge proof system of Gol-
dreich, Micali and Wigderson [GMW] can be used to
1. Introduction
create a constant round interactive verifiable secret shar-
ing protocol for any threshhold ¢. Their solution may be
1.1 The Problem
based on the existence of any one-way function.
Informally, verifiable secret sharing is a protocol in
Benaloh [Be] assumes a reliable public “beacon”,
which a distinguished processor, or dealer, selects and
and uses it to demonstrate a verifiable secret sharing for
encrypts a ‘secret message”, s, and gives a ‘‘share” of s
any threshhold
¢ running in a constant num ber of
to each of n processors.
There exist parameters t,u
rounds. The beacon may be replaced by an interactive
such that no ¢ processors can recover s, but any set of
verification. This V8S assumes the existence of hard-to-
u processors are guaranteed that they can easily com-
invert encryption functions with certain properties.
pute s. When u=t+l, we say
t is a threshhold.
The
Our contribution
is the
first non-interactive VSS
efficiency of a VSS
protocol
is measured by other
protocol. Our protocol measures favorably on all of the
parameters as well:
above parameters.
The protocol works for any thresh-
1. The number of rounds of communication required.
hold ¢ and Tequires 2 rounds of communication. The
:
.
:
communication and computation complexity are small,
2. The number of bits which must be communicated
O(nk) and O((nlogn+k)(nklogk)) respectively, where
between processors.
k
is a security parameter (we assume unit cost for
3. The number of computations the processors must do.
broadcasts). We assume the existence of hard-to-invert
Another
important
characteristic
is
the way
in
encryption functions with certain properties; we show
which the processors are guaranteed that they can
that discrete log encryption in either finite fields or on
recover the
secret from
their shares.
All previous
elliptic curves, encryption based on r-th residues, and
schemes have been interactive; the validity of a share is
RSA all have the required properties.
proven by an interactive protocol. Here we introduce
427
0272-5428/87/0000/0427$01.00 © 1987 IEEE
Restrictions apply.


## Page 2

2. Preliminaries
We
assume
the
existence
of
polynomials
Qo= Q0(7,k), Q3=Q,(n,k)
such
that
all
processors
2.1 The Network
can execute Qo(n,k) steps between pulses, and no pro-
We consider a network of n processors with identi-
betwee or the adversary, ith execute Oiln sk) oer
ties
1,2,...,.2. Each processor, or player, is a probabilis-
th ‘ween | ty ook
n ial Q. ch th , ynomiar— ume
1
tic polynomial-time algorithm (PPTA). We assume that
ere exIsis @ polynoml
sue
at Q(s) is an upper
.
bound on its running time on inputs of length s. When-
every processor has a broadcast channel; a message sent
ver w
that ki
.
tto
algorith
f
on such a channel is received by all processors. Addi-
fo the k-bit strh
ined inpu
an
algorivam, we reter
tionally, we assume that there is a private channel from
ng
_
each processor to every other processor. We consider a
.
.
semt— synchronous network.
Messages sent at the r-th
2.3 Mathematical Notation
pulse
are
received by the
r+l-st pulse.
The
period
For a language L, L, consists of all &-bit strings in
between the
r-th and r+l1st pulses
is called the
r-th
L. For astring a,
|a
| is the number of bits in a.
Impli-
round. We shall see, in Section 7, that the assumptions
cit in the notation {a,b,...}CS
is the fact that a,b,...
of the broadcast channels and private channels may be
are distinct members of S.
relaxed;a complete network is sufficient. A processor
A function U is a probability distribution if it assigns
may initiate a protocol P with common input x by broad-
to each YE{0,1}* a non-negative value U(Y) such that
casting P,z. A protocol is non-interactive if all mes-
yiu(Y)=1.
sages are sentby one
processor
(the leader).
.
.
.
oa
8
y
;
P
.
(
)
A poly-size family of circuits is a family C={|_) C,}
A processor is considered good as long as he has
Pez
followed the protocol, and faulty once he has deviated
of probabilistic circuits such that for some polynomial
from the protocol.
The most general (and difficult to
Q, C, has at most Q(k) inputs and gates.
guard against) faulty behavior occurs when an adversary
To emphasize that an algorithm A receives one
coordinates the fau ty processors.
input we write A(-); if it receives two inputs we write
Definition: A (static) t-adversary acting on P is
a PPTA
A(-,*) and so on. If U
is a probability distribution, then
A, which need not be one of the n processors, such that
Y+U denotes the algorithm which assigns to Y an ele-
1. A can immediately read any message sent on a non-
ment randomly selected according to U; that is, Y is
private channel.
assigned the value
X with probability U(X).
If S isa
2. At pulse 0, A takes as input the common input x and
finite set, then (Yara) 8 assigns to (Yis---¥a) a d-
outputs a
t-tuple of processor
identities,
(4@4,...,a;),
tuple of elements of S with uniform probability. We let
which are immediately corrupted. When 7 is corrupted,
Pr J Yo)! XS; YR T(X);...] denote the probabil-
his current state and the contents of his tapes become
yt at t K Dredicate J(X,Y,...)
will be true, after the
inputs of A. A can replace 7’s finite state control with
ordered
(left to right) execution of X+S, Y+T(X),
any other finite state control. Without loss of generality,
ete.
A sends messages to
1, which
7 copies instantaneously
onto its output tapes.
2.4 Indistinguishability
of Probability Distributions
As a PPTA, A has an output tape; this enables us
and Zero-Knowledge
to formalize the concept that A must ‘‘know” something
Goldwasser, Micali, and Rackoff [GMR] define the
by saying thatA outputs it.
notion
of
computational
indistinguishability;
we
shall
We say that A is a dynamic t- adversary if
A may
adapt their definition to our needs.
corrupt as many as
¢ processors in the network at any
Let U= {U U,} and V={U V,} be families of
time. When A
corrupts
a processor
i
during P, A
vee
ye EE
z€L
.
.
receives as input only i’s current (and future) state(s)
probability distributions. het © be a poly-size family ie
dt
.
,
ana
vapes
P(C,U,z)=Pr[b=0: Y-U,;6+-C), (Y)].
Intuitively,
2.2 Polynomial Time and the Security Parameter
U and V
are indistinguishable if, for large z, Cz| can-
All cryptographic protocols must assume bounds on
not distinguish the output of U, from the output of V,.
the computational power of the players. A parameter of — Definition: Two families of probability distributions U
the protocol is a security parameter k. Informally, any
and V over a language L are indistinguishable
if for any
particular adversary has a good chance of
‘‘defeating
poly-size family of circuits C, Ve>0,
J ko 3k >ko>
the protocol only for sufficiently small values of k.
Pr[ |P(C,U,2)- P(C,V,2) |>k-°: e-L,] <k-°.
This notion had already been used by Goldwasser
and Micali [GM]
in the context of encryption and by
Yao [Y] in the context of pseudo-random number gen-
eration.
428
Restrictions apply.


## Page 3

Intuitively, a protocol is zero-knowledge if for any
Finally, we require that w be hard to compute given
dynamic adversary A
acting on
it, there
is a PPTA
only
¢
pieces output by Share; no
static adversary
which could output strings indistinguishable from those
should be able to guess w significantly better than ran-
output by A. If all processors have initially blank tapes,
domly given ¢ labelled pieces.
then all protocols are zero-knowledge by this definition,
Definition: We
say (Share(-,-),Recover(--:))
is
an
since one can construct a PPTA simulating the entire
(n,t,w) secret sharing if for a language L,
network,
including
the
adversary.
Zero-knowledge
1, WeeL V wEMES, ,( dy,...;d,)—Share(x,w)=>
becomes meaningful when we allow processors to start
V {a4y-.5¢,}C[1,n], Recover(x,(a1,d, )y---(
Gy
ydq.))=w.
with private auztiary mputs which are not easily com-
,
.
putable functions of the common input. For example,
2. V PPTAs A(-), Guess( --- ),We>0,3 ko, | |>ko>
assuming NP is not contained in BPP, one processor
Pr[ w= Guess(x,(a1,dq,)y.0+(
dyydg,)): (4 y).+50,) A(x);
may start with a satisfying assignment of a SAT for-
w—MES, ;( dy,...;dy )+-Share(x,w)]
<1/|MES, |+|z |.
mula, where the formula is given as input to the net-
.
work.
Later, we shall strengthen property 2, by allowing a
dynamic adversary to choose which pieces of the secret
We
define zero-knowledge for a non-interactive
to take as input.
protocol P in which all processors except the leader start
.
.
with blank tapes. The leader, +, runs a PPTA Start on
Shamir [S] presents an (n,t,¢+1) secret sharing for
input (k,n), where k is the security parameter and n is
any threshhold
¢t. Let L be the set of prime numbers
the size of the network. The outputs of Start are the
 8reater than n. For pel, we define Share=Share(p,-)
common input to P, z, and an auxiliary input for i. We
as follows. The domain is MES=Z,. Protocol Share,
assume that A may not corrupt i. Let A output strings
© input wEMES, sets Yow and lets (91,....%)-Zp.
according to probability distribution U, when P is ini-
Let Q(s) be the polynomial YD ys. Then the output of
tiated on input z.
.
i=0
.
Definition: A
non-interactive
protocol P
is
tzero-
Share is Q(1),9(2) rer Q( 0) mod p. Recover is polyno-
knowledge
if for every dynamic t—adversary A, there
mial interpolation, which 8 used to find Q(0)=w.
exists
a PPTA A’ which takes as input EL and outputs
Informally» We argue that ¢ pieces are no help in Tecov~
strings according to V, such that the families of proba-
vale ot O nanely Mew, usigucly seahee a wy
ey:
‘
.
.
‘
oye
:
’
om
wv,
=
bility distributions {U,} and {V,} are indistinguishable.
mial Q. Since all other coefficients were chosen uni-
.
.
formly, the chance that a particular polynomial was
3. Verifiable Secret Sharing
picked is directly proportional to the probability that its
We begin by describing ordinary secret sharing ina
constant term was the secret chosen. Therefore, seeing
t¢
framework which generalizes naturally to VSS.
Pieces gives no additional information.
An (n,t,u) secret sharing (Share ,Recover) suggests
3.1. Ordinary Secret Sharing
a non-interactive protocol in which the leader, or dealer,
Ordinary secret sharing enables a dealer to split
can ‘‘split” a secret among n
players in such a way that
information among a network so that a quorum of pro-
only a quorum of u can recover the secret. Namely, the
cessors
is
needed
to
recover
the
information.
An
dealer broadcasts x and sends piece d, to player i via
(n,t,u)
secret
sharing
is
a
pair
of
PPTAs
private channel. When u players wish to recover the
(Share(-,:),Recover(---));
Recover takes u+1 inputs
secret, each broadcasts his labeled piece, and Recover
and is deterministic. The first input of both Share and
am be run to return
the secret.
Recover
is
tE€L
for
some
language
L.
We
call
Can
this
protocol
be
used
if
¢
players may be
MES,=Domain(Share(z,-))
the
message
space;
faulty?
No! It is true that no set of t faulty players can
|MES, |>1.
CYPH,=Range(Share(z,:))
is the cypher-
recover
the
secret
themselves.
However,
even
if
text space. We consider a particular z€ZL and omit the
u<n-t, in which case there are enough good players to
argument z.
The input of Share
is a secret wEMES,
recover
the
secret,
bad
players
may
interfere.
For
and
Share
outputs
an
ordered
n-tuple
example, a bad player 1 may broadcast a spurious value
(dj,...,d,)€CYPH.
Each d, is called a piece, or share,
in place of d;.
Good players cannot distinguish good
of w. The input of Recover is a u-tuple of ordered pairs
Pieces from spurious pieces. If t=0(n), then a random
((@,¢;),-.,(@,,c,)),
where
a;€[1,n], ¢;€CYPH,
and
u-tuple consists entirely of good players with exponen-
the a; are distinct. The output is an element of MES. _ tially small probability.
When the input to Recover is any labelled subset of u
pieces output by Share on input
wE MES, Recover out
puts w. Formally,
(dyyer, )-Share(w)=>V {aj,...,¢, }C[1,n], (2.1)
Recover((a,,d, Jasees(a,,d,))=w.
429
Restrictions apply.


## Page 4

Indeed, the dealer can prevent this problem by
3.3 Applications of Verifiable Secret Sharing
authenticating the Pieces. In this way, good players
Verifiable secret sharing enables a communication
oud roenize which pieces truly came from the
network to simulate a simultaneous broadcast network.
ing: what ha ae “the.dealer ee fault . nd follow:
Informally, every processor is required to share his
players themeelves might
ect auth ati ted .
: € goo
round r message before any round r message
is
:
d
they
will
&
'
b
enticated
yet spurious — revealed. This trivializes the design of protocols such as
Pieces, and
they will
not
be able to recover the secret.
secret, bidding, leader election, and flipping a fair coin.
Depending on the behavior of Recover on
‘‘invalid”
.
:
.
inputs, the good players may not be aware that different
In the simulation of a simulataneous broadcast net-
sets of pieces would return different secrets. The secret
ven” each (GMW} hoewd Rabin |CR] merave
returned could depend on which bad
players chose to
such
as
,
'n
broadcast their authenticated, spurious pieces, The best
logn rounds are sufficient for n processors to prove the
kind of secret sharing would allow any player to verify
validity of their pieces; it is not known whether this can
during Share whether or not his piece is valid; more-
be done in a constant number of rounds. In a non-
over, he should be
able
to check during Recover
interactive VSS, all processors may deal secrets in paral-
whether or not the piece another player broadcast is
[es therefore, our protocol gives constant round solu-
valid.
tions to all these problems.
Another application
is achieving a fast Byzantine
3.2 Verifiable Secret Sharing
Agreement without, any preprocessing. The best previ-
Informally, a verifiable secret sharine
protocol
'
ously known algorithm which could tolerate a linear
meet the following tw
:
‘aring protoco! mus
number of faulty processors, due to Chor and Coan
ne
fon
&
two requirements:
[CC],[C], required expected O(n/logn) rounds. Feld-
1. Verifiablility constraint: upon receiving a share of the
man and Micali [FM] show that running non-interactive
secret, a player must be able to test whether or not it is
verifiable secret sharing without broadcast channels,
a valid piece.
If a piece is valid, there exists a unique
using Crusader Agreement instead, yields a constant
secret which will be output by Recover when it is run on
expected time Byzantine Agreement protocol.
any u distinet valid pieces.
Even beyond the protocols which directly follow
2. Unpredictability: there is no polynomial-time strategy
from it, verifiable secret sharing now plays a central role
for picking ¢ pieces of the secret, such that they can be
in cryptographic protocol design in a most dramatic way.
used to predict the secret with any perceivable advan-
In [GMW] it is shown that all protocols can be designed
tage.
to resist t faulty players out of 2¢+1.
Verifiable secret
This framework allows for an interactive protocol
sharing is one of the three main blocks needed for their
proving validity of the pieces. A VSS
protocol is non-
simulation.
This highlights even more the need for an
interactive if there is a polynomial-time dgorithm Check
efficient verifiable secret sharing, as it may enter as a
which tests validity of the pieces.
Obviously, the same
key subroutine in a large class of protocols.
Pieces are not valid for different secrets; we introduce a
‘A Encrypt to handle this.
4. Motivation for Our Solution
Informal Definition: An (n,t,u) non-interactive verifiable
The motivation behind our solution
is to utilize
secret
sharing
is
a
quadruple
of
PPTAs
homomorphic relationships which may exist between
(Share Recover,
Check ,Encrypt) such that
values and their encryptions. For a certain class of
1. (Share,Recover) is an (n,t,u) secret sharing over a
encryption schemes, which we shall call homomorphic,
language L.
we can construct an algorithm Check which enables a
2. V2€L,W
wEMES, ,V1<j<n, Y¥+-Enerypt(z,w);
player to verify the validity of his piece.
(d1,.4)d,)+-Share(z,w)>, Check (2. Y,7,d;)=1.°
4.1. Probabilistic En
*
aan
lL.
cryption
3. VEL ,V YeRange(Encrypt(z,")), J we MES, >
A problem with deterministic encryption schemes is
V {ay 5-+-54y }C[1,7] 1W dy,..)dy€MES,,
that it is easy to check whether or not a
gi
iphertext
(Cheek (2° ¥,a;,d;)=1 W1<i<u)>
t
a given ciphertex
1995
is the encryption of any given message. Goldwasser and
Recover( x ,(@1,d1),+++5( @y,dy))= w.
Micali [GM] showed how to overcome this problem by
.
probabilistic
encryption.
They define
the
notion of a
Remark: Actually, we
require that (Share , Recover)
family
of
unapprozimable
predicates.
Let
remains
an
(n,t,u)
secret
sharing
even
when
H= {Hard,: c€L} be a family of predicates, each Hard,
Y+-Encrypt(z ,w) Is given; Share itself may take Y iM
maps CYPH,-— {0,1}. Elements which map to 0 (1) are
an input. To formalize the definition, Share itself wou
considered encryptions of0 (1). Intuitively, such an
set Y+-Encrypt(z,w) and append Y to each piece.
430
Restrictions apply.


## Page 5

encryption is secure if there is no efficient way of com-
4.2
Homomorphic Encryption Functions
puting Hard, on random elements; H is unapproximable
.
;
.
if no poly-size family of circuits can compute Hard,(y)
Often,
a rich
algebraic
structure
underlies an
we
.
encryption scheme. Relations among
cleartext values
significantly better than randomly guessing when z and
.
:
.
y are randomly selected.
may imply relations among the encryptions. For exam-
.
.
i
ple,
in RSA_ encryption,
Encrypt(yz)==(yz)°
mod
Let
C={C,: kEZ} be a poly-size family of circuits,
m=Enecrypt(y)Encrypt(z). More generally, when both
C,(-,") takes as input r€L, and y€CYPH, and outputs
the domain and range of Encrypt are groups, Encrypt
a bit. For €L,, let
may be a homomorphism of the groups. Benaloh [Be]
P(C,k,2)=Pr| C,(2,y)=Hard,(y): yCYPH,].
utilized such homomorphisms in his secret sharing, and
Definition: The predicate H is unapprozimable if
pointed ou that ee (Bea) extends to such a class of
encryption functions
2|.
Let
VO={Qyi KEZ}We>0, dk >k2>ko>
(4.1)
MES=Domain( Encrypt)
be an additive group, and
Pr[P(C,k,2)>.5+k~°: Ly] <k-*
CYPH =Range( Encrypt) be a multiplicative group. The
To probabilistically encrypt a bit using Hard€H, there
key property is that for all B,CEMES,
must be a way for the encrypter to find ‘‘random” ele-
Encrypt(B+C)=Encrypt(B):Encrypt(C)
(4.2)
ments which map to 0 (or 1). One possibility is if Hard
pro,
c€Z,
we
define
the
scalar
product
is a trapdoor function, that is, Hard is easy to compute
c-B=B+B+...+B with c summands. Induction may be
given a short string Hint. In this scenario, the encrypter
used to show that
V BEMES, Vc€Z,
generates a pair z,Hint,; he can then com pute Hard, on
Enerypt(c-B)=(Encrypt(B))°.
random elements of CYPH,, and picks one which maps
S
.
.
eas
to the desired bit.
ecurity can only be achieved by picking among a
family of encryption functions. Let Generator(-,-) be a
Another
method exists if Hard is an easy predicate
PpPTA which, on input k,n, selects ae(Ly) L") for
composed
with a one-way function, as we now explain.
some language L; we define L"CL below. We impose
Let MES be a message space, and let Encrypt be an —_uniformity constraints by requiring a PPTA Encrypt(-,-)
injection from MES—CYPH . Informally, Encrypt is
such that Enerypt(x,-)—=Encrypt,(-), and similarly for
one-way if Encrypt is easy to compute, but Encrypt”' is
Predicate(-,-).
Likewise, there must be uniform algo-
hard to compute.
Let Predicate: MES — {0,1} be an = sithms for computing the group operations, uniformly
easily
computable 4
function.
Suppose
sampling MES, and the following function Divide,
Hard
= Predicate( Encrypt
). Then the encrypter can
whose purpose will first become clear in Section 5.3. For
randomly pick y€CYPH, and compute z—Encrypt(y)
all BEMES,, Divide(x,n,n!-B)=Predicate(x,B). Since
and
b = Predicate(y). By construction, Hard(z)=6,
scalar multiplication by n! need not be a 1-1 function,
hence aia probabilistic encryption of 6. All encryp-
the existence of Divide imposes a certain structure on
tions we shall consider will be com puted by this latter
Predicate. Moreover,
this says that Predicate,(B)
is
method, even though some are also trapdoor schemes.
easily computable given only n!-B as input. We define
Example: RSA probabilistic encryption, developed by
MES!={BEMES,: Predicate(B)=s}.
We
define
Rivest, Shamir, and Adleman [RSA] may be computed
[r= {zEL; (Divide(x,n,-) is well defined ) and
either way. Let m be a product of large primes, and e a
.
number such that (e,¢(m))=1.
Let d=e~! mod
( [Range( Predicate(,-) |>m)}.
¢(m); d, which is not easy to compute without knowing
If
these
properties
are
satisfied,
and
the factorization of m, is the trapdoor hint. We define
Hard=Predicate( Encrypt-1) is unapproximable, we say
CYPH = Zn. For yEZm; we define Hard(y) to be the
Generator is a homomorphic probabilistic encryption scheme
parity of y° mod m. This is easy to compute for anyone — generator,
Equation (4.1) implies that NP is not con-
knowing d, but it is believed to be hard to com pute oth-
tained in BPP, so we will need to make certain unpro-
erwise. We shall focus on the method of encrypting bits
yen complexity assumptions to assert that we have such
without knowing d. Let Encrypt(y)=y* mod m and
generators.
Predicate(y) be the parity of y; both are easy to com-
pute. A O (1)
is encrypted by raising a random even
In Section 8, we construct homomorphic probabilis-
(odd) element of Z 7, to the e power mod m.
tic encryption scheme generators based on different
We shall find it convenient to generalize this notion
problems. One
is based on the
difficulty of taking
by enlarging the range of Predicate, and hence Hard, to
discrete logs in a finite field; a suitable restriction of the
[1,/]; the value of / is a parameter of the particular
domain is required. The same method lets us base a
encryption function.
generator on the difficulty of taking discrete logs on a
elliptic curves.
Benaloh [Be2]
has pointed out that a
generator may be based on the difficulty of distinguish-
ing r-th powers in Z,,, where
r
is a prime dividing
¢(m);
the
nature
of
these
probabilistic
encryptions
differs slightly from the description given here. RSA is
431
Restrictions apply.


## Page 6

sufficiently homomorphic for our purposes if we define
Q(h).
Player
j
is
not convinced
that
the
dealer
the “addition” on the domain MES=Z,, to be multipli-
encrypted a real permutation, but he knows that the
cation mod m.
h-th piece is designated exclusively for him, since only
A,
can encrypt to Encrypt(A,) and Predicate(A,)=J.
4.3. Using a Homomorphic Probabilistic Encryption
To facilitate the simulation, this step will precede the
Scheme to Produce a Non-interactive (n,t,t-+ 1) VSS
broadcast of the encrypted variables.
We restrict the rest of this chapter to an informal
With respect to a static adversary, the simulation
discussion of our protocol.
The formal presentation is
may be done without permuting the shares. We argue
given in Section 5.
without proof, in Section 9.2, that the shares need not
Given Encrypt, we show how to share a secret in
be
permuted
even
against
a
dynamic
adversary,
[1,1]; a longer secret may be shared by sharing blocks of
although there are problems with the simulation in that
|! -bit secrets in parallel. We convert Shamir’s secret
case.
sharing into a non-interactive VSS as follows. The dealer
uniformly picks a secret s+-[(1,/], and yo€MES* and
5. Our Protocol
sets yo to be the constant term of a degree ¢ polynomial
Q. He chooses the
¢ other coefficients of Q uniformly
5.1 Initialization
in MES.
He
then broadcasts
encryptions
of the
Let Generator be a homomorphic
probabilistic
coefiicients of Q, Enerypt( Yo) -+-»Enerypt vs) As m
encryption scheme generator. The dealer ¢ sets
Shamir’s scheme, he sends Q(3) to player j via a
z+-Generator(k,n), where k is the security parameter,
private channel. The point is that 7 can verify his piece
and n is the size of the network. We omit the depen-
by checking that
dence
on
Z.
Let
MES=Domain( Encrypt),
Encrypt( Q(7))=
(4.3)
CYPH =Range( Encrypt).
(Encrypt( yo))-( Encrypt( y,))2---( Enerypt( y,))*
The dealer ¢ uniformly picks a secret s+-[1,/], sets
eyes
.
Yo*-MES*, and computes Y=Encrypt(yo). The VSS is
Even
for probabilistic encryption schemes, we must
initialized with
input i2.Y. All
pl
to
still prove that broadcasting the encryptions does not
intaized
wi
common inpUl tT,7-
Players store
#,z,Y on a work tape;
1 additionally stores
yo
as his
allow an adversary to guess the secret advantageously.
‘ary
input.
0
This is done by showing that the adversary can simulate
auxiliary Input.
his view by himself. To facilitate the simulation, we
alter the protocol slightly by having the dealer encrypt a
5.2. The Protocol Share
certain multiple of the coefficients, as will be described
The dealer broadcasts messages in steps 1 and 3;
below.
the players perform calculations in steps 2 and 4.
4.4 Tolerating
a Dynamic Adversary
1. The dealer ¢ selects 7+-S,, a uniformly chosen per-
;
.
mutation of [1,n]. He sets A,—-MES"(3) for each j and
It
would seem that a non-interactive VSS could not
broadcasts th
babilisti
J
i
thi
if
be zero-knowledge with respect to a dynamic adversary.
roadeas
&
prodabuisiic encrypuion
this species,
O
.
a
:
Encrypt(A,),...,Encrypt(A,).
He sends h,A, on the
nm the one hand, by the intractability assumption, a
rivate channel to
7.
wh
hen
4
simulator cannot reconstruct the secret. On the other
P
°
: I where =n
(3).
hand, we wish that he can simulate the output of an
2. Each player j lets A=(Encrypt(A)),...,Encrypt(A,))
adversary, who could corrupt any ¢ players and output
denote the values he received on ?’s broadcast channel
valid pieces with those indices. However, if the simula
924 4 and C denote the values he received on the
tor knew all the pieces, he could compute the secret,
Private
channel | from
¢
in
round
1.
We
define
The resolution of this difficulty is to permute the shares
Checkid(j,h,C,A)=1 iff Enerypt(C)=Encrypt(A,) and
in a way unknown to the adversary; the adversary does
Predicate(C’)=j. When this is the case, j stores h but
not know which share a player should have before cor-
not C=A,; if this fails, 7 immediately rejects the dealer
rupting him.
In this way, a simulator knowing ¢ shares
as faulty.
can ‘‘fool” an adversary into thinking that these are the
3. The dealer sets (4},...,y,)—-MES. He computes and
correct shares for the players corrupted. Of course, this
broadcasts
leaves the problem of how to convince a player that he
(Y1,-.-. ¥;)=(Enerypt(n!-y,),...,Enerypt(n!-y,)).
Let
is receiving the proper share.
Q: Z—MES
denote
the
‘‘polynomial”
function,
This latter problem is solved by having the dealer
Q(a)= Yial-y. The dealer privately sends M,=Q(h)
probabilistically encrypt a random permutation 7€S,.
1=0
The dealer lets (A,;+MES™(})),...,(A,—-MES*™(")) and
to player j=m(h).
broadcasts
Encrypt(Aj),...,Encrypt(A,).
The
dealer
sends A, on the
private channel to player
j, where
h==m-1(j); 7 can verify that Predicate(A,)=j. This
designates that player j should subsequently receive
432
Restrictions apply.


## Page 7

4. Each player
j computes Yo= Y"!, Let
2. Likewise, A’ perfectly simulates A and all other
Y=(Yo,Yj,...,¥;) denote Yo and the values broadcast
Playersin step 2.
last round; let N, be the value j just received on the
3+ Let J1,...)J, denote the players A corrupts by the end
private channel. Define Check(Y,N,,h)=1 iff
of step 2, and let m(h,)=3
for lE[1,to].
A’ picks
Encrypt(n!-N,)=(Yo)-(Yt)--( ¥#'). When this is true, j
Asspise-yh,
uniformly among
the
as-yet
unselected
stores h,N,; otherwise, he rejects the dealer as faulty.
indices in [1,n], so Aj,...,h, are all distinct. Let ho=0,
Remark: As we mentioned in Section 4.2, scalar multi-
pho... (Ao)!
plication by n! need not be 1-1.
Therefore, coefficient
1hy...( hy)!
y,
is
not
uniquely
determined
by
the
encryption
and
let H=|:....
.
|.
This
is
a Vandermonde
Y,=Encrypt(n!-y,). However, Encrypt is 1-1, so n!-y,
Pie
;
is
uniquely
determined
by
Y,.
Therefore,
if
Thy"( hy)
Check(Y,N,h)=1,
this
only
guarantees
that
matrix, and its determinantis
D =
[[
(h,- hy).
n!:N=n!-Q(h). Fortunately, this is good enough, since
O<l<e<t
it suffices to find n!-yg to recover the secret.
Lemma 6.1: Let H={h,,}, where
| and e range from 0
to t and h,, =Af; let G=H~1={G;,}. Then the denom-
5.3 The Protocol Recover
inator of G,, divides [J (A;- ,).
At any time
after Share was executed on input
je
(1,2,Y), Recover may be initiated on the same input.
This is proved by showing that [[
[J (4,- 4)
Each player 7 retrieves and broadcasts the private values
_
,
iAe i¢{je}
he
stored
for
that execution,
h,N,.
Each
j runs
divides the determinant of the /,e minor of H. Since
Check ( Y,N,,1) to test whether an indexed piece which
{ho,--s4t}C[0,n], the denominator of G), divides n! for
was broadcast,
/,N,,
is valid.
Assume that
7 can find
22Y @-
t+1 valid indexed pieces ((41,Ne,) 5-9 Ge415Mo,,1))+ The
A'
sets
(Mj,....M,)—MES. We
implicitly
set
polynomial
Q
is
found
by
interpolation,
Mo=¥o (which is well defined as E~'(Y)).
t+1
zZ-a
ej
Q=y) (0 (aan)i) |e. We observe that this formula
We define the ar i product by
Isa nei @- a), )
(Cy,+05¢q) *(By,...,By)=3)
¢;'B;, for cy,....cgEZ and
would give a polynomial-time algorithm for computing
_
ial
.
.
Q
if we could perform scalar division.
In particular,
21)--»By€MES. This extends to a *matrix product in
t+
(a; )
the
natural
way.
Observe
that
the
conditions
Yo= Q(0)=),Hicern
@;) ae Although we cannot
M,=Q(h,), for /€[0,t] may be written as a matrix
=l
necessarily do arbitrary scalar division, the denominator
vo
Yo
of each term of the sum divides n!, so n!-yp may be
equation M=H#W, where
M =|
.'|
and
¥ = 7
are
computed by additions and scalar multiplications by
M
,
integers.
Therefore, j can compute n!-yg and hence
.
'
eye %
Divide(n,n!-yo)= Predicate
(yo)=s.
considered as column vectors. By *multiplying both
°
sides
by
G=H-},
we
obtain
.
GM =G+(H¥)=(G-H) Y¥=7 (the associative law fol-
5.4aFae of Share
lows from direct calculation). Denote row I of (n!)-G
n
, we modify Share by allowing each player to
:
-M
=n!-
i
broadcast a single termination message. On the basis of
by the integers go. Jiys SO die M,=n'-y. Applying
these messages, the players can determine whether or
Encrypt to both sides and using equation 4.2,
not enough good players received good pieces to ensure
t
recovery of the secret. This determination
is based
II (Encrypt(M,))"=Encrypt(n!-y)
(6.1)
~
solely on broadcast messages, hence
all good players
e=0
reach the same conclusion.
Observe that A’ can compute the left hand side, since
Encrypt(My)=Y is part of the common input and M,
6. A Proof of the Security
was chosen by A’ for e>0. The right hand side is the
definition of
Y,. Therefore,
at step
3, A’ broadcasts
6.1. The Zero-Knowledge Simulation
(Yj,..,¥;) and sends M, to y for 1</<to. By construc-
Let A be any dynamic t- adversary. We construct a
tion, Check (Y,M,,:)=1.
PPTA A’ which simulates the whole network, including
Let J+: be the next player A corrupts; A’ simu-
A, without benefit of the auxiliary input. Assume that
lates 44,
starting from
the end of round
2, with
Share is initiated with common input 7,z,Y; henceforth,
1,2, Y hip yA as the only values on Jtgt1'S work tape.
we
omit the argument £.
By construction, A! is able to give the proper piece
1. Since
1 does not utilize the auxiliary input, namely
M,,41 at round 3. In like manner, the next player cor-
10 in round 1, A’ simulates i (and A) perfectly at step
rupted will have stored the value hy,+49) and so on.
433
Restrictions apply.


## Page 8

4. A’ simulates corrupted players by running A ansd
A random pad r; may be sent privately by the use
outputs the output of A.
of trapdoor encryption functions.
Suppose that player 7
broadcasts an encryption function, Encrypt; for which he
6.2 Indistinguishability of the Output of A from the
knows a trapdoor hint, Hint; The dealer picks a ran-
Output of A’
dom pad r; and computes a probabilistic encryption of
Actually, Share is zero-knowledge even if Encrypt
it, Enerypt;( r;) and sends this to j. Player J decrypts to
is easy to invert, in which case i’s auxiliary input is
find the pad r;. Assuming Encrypt; is secure, an adver-
easily computable, and A’ can perfectly simulate the
SFY, Om Input Encrypt,(r;), cannot guess any bit of rj
entire network and output what A outputs. For simpli-
Significantly better than at random.
city, we shall prove that Share is zero-knowledge assum-
Although
our
algorithm
only required
that the
ing equation 4.1, which implies that Encrypt
is hard to
dealer send messages along a private channel, this tech-
invert.
If the output of A
is distinguishable from the
nique can be used to simulate, simultaneously, a com-
output of A’, then A distinguishes the probability distri-
plete
network of private
channels.
In
particular,
all
butions on its inputs. Thus, it suffices to show that the _ players may still ‘‘deal” secrets simultaneously.
inputs to A acting on Share are indistinguishable from
The assumption of a broadcast channel
is very
the inputs to A in the simulation.
strong. We can eliminate this assumption by simulating
The selection of 7,A),...,A,
is done exactly as in
the broadcast channel by Crusader Agreement, which is
Share. Also, the probability distribution on Y=y},...,y,
a weak form of Byzantine Agreement. The simplest ver-
which is the uniform one when A acts on Share, is also
sion
requires
the
assumption
that
t<n/3;
a more
uniform in the simulation for the following reason. A’
involved version tolerates any value of t<n/2, provided
selected
all elements of M=M,,...,M, uniformly in
that the processors start with secure signature schemes.
MES. Given fixed values of M,
and yo, there is a 1-1
:
*
onto map between choices of it and choices of ¥ -- H
8. Candidates for Homomorphic Encryption Schemes
sends M=(Mo)M) to ¥=(4¥0,7), so the uniform distri-
.
.
.
_
bution on one implies the uniform distribution on the
8-1
[Emeryption Based on Discrete Logs in Finite
other.
In Share,
the elements of J=yj,...,y, were
Fields
selected uniformly. Since in both cases,
M
is uniquely
Generator, on input (k,n) uniformly selects a k-bit
determined by 7, this also has identical distribution.
prime p and the prime factorization of p—1 subject to
There is only one difference in the inputs to A in
the condition below.
(Bach [Ba] shows how to uni-
the two cases. When A acts on Share, if player j is cor-
formly generate numbers of known factorization.) Let
rupted
after
round
2,
j
stored
h
where
d,,=I[I (¢’,r),
that
is,
the
largest
divisor
of
r
h = Predicate(A;)=Hard(Encrypt(A;)).
In the simula
gostne
tion, the /-th player j corrupted by A after round 2 will
without a prime factor exceeding n. We require that
have stored the value h,,,,, regardless of the actual
dpi n<n’, For random k-bit numbers r, d,, approxi-
value Hard(Encrypi(A;)). Therefore, any PPTA which
mates a normal distribution with expected value n ", So
can
distinguish _ the
views
can
determine
dy-in<n for all but an exponentially small fraction of
Hard ( Encrypt(A;))
better
than
randomly
guessing,
Ps and this remains true when we restrict P to k-bit
:
primes. (We could use any polynomial in place of n°).
given only Encrypt(A;). However, by (4.1), A cannot
Since the only
f
.
.
:
y
fast algorithms for taking discrete logs
guess Hard(E(A;)) better than randomly. Therefore,
require that p-1 has only small prime factors, any p
the inputs to A are indistinguishable.
which did not satisfy this condition would not be con-
sidered a good choice for discrete log encryption in any
7. Extending the Protocol to a Larger Class of Net-
case.
works
Generator uniformly selects a generator of the mul-
We informally remark that Share,Recover may be __ tiplicative group Z,;, 9- The index
is the concatenation
implemented without private channels and/or broadcast
P,g; we omit reference to it. The domain of Encrypt is
channels;
a complete network
is
sufficient.
Formal
Z,-1, and the range is Z,. For y€Z,_1, Encrypt(y)=g"
proof of the claims in this section will appear in [F].
mod
Dp. This
satisfies the homomorphism
property,
We first observe that random pads can be used to
_Encrypt(B+C)=g®*° mod p=Encrypt( B)-Encrypt( C).
simulate private channels. Assume that the dealer once
_It is easy to design PPTAs for the group operations and
privately sent a long string of random bits, r;, to each
sampling MES; we describe Predicate and Divide below.
player j, but all future messages may be input by an
We make the following intractability assumption for tak-
adversary. To privately send message m; to j, he sends
_ing discrete logs:
mPr;, a bitwise exclusive-or-of the real message and an
Ve>0,Vn>0,V PPTA Logarithm(-,-,-),
(8.1)
“unused” portion of the random
pad. Player 7, who
knows 1;, easily computes m;. The adversary, who does
J ko: D-k > ko Pr[y=Logarithm(p,g,z):
not know 1; cannot distinguish the sent message from
(p,g)+-Generator(k,n);y+-Z,_132=9" mod p]<k~°
random noise.
434
Restrictions apply.


## Page 9

Notice that n!, being even, does not have a multiplica-
Generator, on input (n,k), uniformly selects an
tive inverse in MES=Z,_,. A necessary condition for
|n|+1-bit prime
r, k-bit primes p and
q such that
the existence of Divide is that
r|p-1, and z—{uEZ: ul? Y/t mod p71}, that is, a
Vv
non-r-th
power modulo
p.
Set m=pq; c=r,m,z.
B,CEMES,n!-B=n!-C=> Predicate (B)=Predicate(C). Here, Encrypt
itself is probabilistic. The domain of
Let
e=(p-1)/d,_1,.
We
partition
MES
into
Encrypt, MES, is [1,r]; the range, CYPH, is Z,,. For
equivalence classes mod e, so B=C mod e=>
8€[1,r],
Encrypt( 8) {2° v"
mod
m: vez a}
Predicate(B)= Predicate(C).
By
construction,
Predicate(s)==s. No way of computing Hard without
(e,n!)=1, so n!:(B- C)=0 mod p-1>B=C mod e.
knowing the factorization of m is known. To check the
Division by n! is easy mod e, so Divide is no harder to
homomorphism
property,
let
(23 of
mod
compute than Predicate.
m)+—Enerypt( B) and
Long
and
Wigderson
[LW],[L]
show
the
(z de rae) Ener C), and observe that their
equivalence of computing discrete logs and guessing BAG (2°*°(vw)’
mod
m), is a possible encryption
whether or not the log is in the top half of the residues
°
+¢.
mod p—1. In fact, the ability to guess any predicate of
In this scheme, division by n!
is easy in MES.
the top O(log |p |) bits of the log better than at random
However,
this
method
of
probabilistic
encryption
is equivalent to computing the log.
Kaliski [Ka] gen-
requires the dealer to append to each piece M, a string
eralizes this result to apply to logarithms in arbitrary
% enabling the recipient to verify equation 4.3, that the
commutative groups. There is a correlation between the
appropriate product of the encrypted
coefficients
is a
most significant bits of
f+-Z,_, and the most significant
possible encryption of M;. A real problem is how to
bits of
f mod e, hence the ability to predict one better
convince the players that 2 is not an r-th power without
than guessing implies the same for the other.
revealing
the _ factorization of
m.
This
apparently
Set
1,
the size of MES,
to be 2Itl,
For fez
requires prefacing an interactive zero-knowledge proto-
.,
,
.
. °’
col proving that z is not an r-th power.
define Predicate(f)=[(f mod e)l/e].
Then equation
8.1 implies equation 4.1, that Hard is hard to compute.
8.4 RSA
8.2 Discrete Logs on Elliptic Curves
As we mentioned in Section 4.1, the RSA encryp-
A homomorphie probabilistic eneryption scheme for
tion scheme behaves sufficiently homomorphic to be
which no sub-exponential
inverting
algorithms
are
used in the VSS.
An advantage of RSA
is that
known involves taking discrete logarithms on an elliptic
®Umerous attempts to
‘‘break”
the scheme have been
curve. Miller [M2] suggested the ‘‘supersingular” case,
made. The only successes have been for the special case
which is the simplest and most efficient; the interested
of a very small exponent, which, we Shall see, could not
reader should see [M1]. Everything is analogous to the
be used for VSS in any case. Alexi, Chor, Goldreich,
previous section. Generator, on input (k,n), uniformly
224 Schnorr [ACGS] prove a reduction from advanta-
selects a k-bit prime p such that p=3 mod 4 and
geously guessing Hard (as defined in Example 4.1) to
d?+12<n3, Let Curve ={(2,y)EZ,: y2=2°+2 mod p}
inverting the RSA function Encrypt. They extend the
and a point called co. The points on Curve, form a
reduction to the case where the predicate Hard contains
cyclic group of order p+l. A generator PE Curve, is
O( |k |) bits.
chosen;
z=(p,P).
For
y€MES=Z, 41,
let
Generator, on input (k,n), uniformly selects k-bit
Encrypt(y)=y-P. This satisfies the homomorphism pro-
primes p and g and a 2k-bit prime e, e>n. Set m=pq;3
perty,
z=e,m.
The domain and range of Encrypt are both
Encrypt(B+C)=(B+C):-P=Encrypt(B)Encrypt(C).
Zm-
For y€Z,, Encrypt(y)=y? mod m. The ‘‘addi-
Set
e=ptl/d,,,,.
Let Predicate(y)
be
the
most
tion”
for RSA
is
multiplication
mod
m,
so
the
significant |k| bits of y mod e. By Kaliski [Ka], guess-
homomorphism property is
ing Hard better than randomly is equivalent to comput-
Encrypt(BC)=(BC)* mod m=Encrypt(B)Encrypt(C).
ing discrete logs on (supersingular) elliptic curves. We
Since (e,¢(m))=1, Encrypt is 1-1. We set Predicate (y)
could have Generator select a general elliptic curve (sub-
to be the
|k
| least significant bits of y.
ject to some restrictions), but this would entail high
We
defined
Divide(n,n!-y)=Predicate(y).
For
(polynomial) computation and lengthier analysis.
RSA, this is inherently ill-defined, since n!-y=y"! mod
m=n!(m—y)
but
—Predicate( y)Predicate (m- y)
8.3 Encryption Based on the Difficulty of Distinguish-
(exactly one of them is even). We remedy the situation
ing r-th Powers
by making Encrypt(y) an additional input to Divide.
The following probabilistic encryption scheme was
Since
(e,n!)=1,
we
can
find
u,v
such
that
first
suggested by Cohen and Fisher [CF] with applica-
ue+v(n!)=1. Notice that Encrypt(y) and y"! mod m,
tion to a voting protocol; Benaloh [Be2] suggested its
uniquely determine y and show how
to compute
it
use for our VSS.
easily: y= y"?+"!==(Encrypt(y)")((y"')”) mod m, so
Divide(n,n!-y,Encrypt(y)) is easily computable.
435
Restrictions apply.


## Page 10

9. Other Variations
9.3 Must We Permute the Pieces?
.
:
:
We believe that our protocol may be simplified to 1
9.1 Basing the VSS on Multiple Homomorphic
round of communication. The pieces were permuted to
Encryption Functions
facilitate the zero-knowledge simulation in the proof;
Note that one can easily combine the security of
indeed, we do not know how to do this simulation in
multiple homomorphic encryption schemes. For exam-
the simpler setting for a dynamic adversary. (The simu-
ple to encode a secret s using Encrypt and Encrypt!, the
lation
for
a
static
adversary
is
straightforward.)
dealer picks s’ at random, shares the secret s’ using
Nevertheless, we conjecture that the simplified protocol
Encrypt’ and the secret sos" using Encrypt. The good
ig secure against a dynamic adversary as well.
players can recover both s and ss h and hence $- The
We see no way that knowledge of encryptions of
adversary cannot recover § unless
he can Inver
bo
the coefficients of Q, or any subset of the pieces, can
Encrypt and Encrypt’.
make certain other pieces ‘‘more useful”. In fact, we
could try the simulation for the simplified protocol with
9.2 Efficiency
respect
to
a dynamic
adversary A,
and we
would
The communicational complexity of VSS for
all
succeed whenever we guessed the
¢ players that A cor-
homomorphic encryption schemes proposed is very rea-
_rupts; however,
this happens with probability inverse
sonable.
The dealer initiates Share by broadcasting his
exponential in n. This would contradict a strong intrac-
identity, the index of Encrypt, z, and an encryption of a
 tability assumption; that is, if we assumed that any algo-
secret, Y. In step 1, he broadcasts the encrypted A,’s.In
rithm inverting Encrypt with significant probability must
round
3,
he
broadcasts
encryptions
of the other
¢
run in time exponential in n. This may apply to discrete
coefficients, the
Y,’s. Each broadcast has O(nk) bits.
logs on elliptic curves whenever k>n, and to all the
Also, O(k) bits are privately sent to each player. For
other schemes described when k is a sufficiently large
all
homomorphic encryption schemes proposed here,
function of n.
we feel that 1000
is a reasonable value for k
given
sufficient for discrete logs on elliptic curves.
10. Conclusion
We shall examine the computational complexity in
We have presented a noninteractive verifiable
the case where discrete logs in finite fields are used. We
secret sharing, optimal in that it tolerates up to (n-1)
/2
ignore the cost of finding p.
This is a one-time cost
bad players, which is provably bitwise secure, assuming
which is not large if we allow non-uniform selection; it
the intractability of taking discrete logarithms (or one of
may be avoided entirely by choosing p from a list of
the other
homomorphic encryption schemes). As we
known very large primes. In such a case the security of
observed in Section 3.3, verifiable secret sharing can be
the protocol hinges on a bolder assumption than the
ysed as a subroutine to simulate a simultaneous broad-
discrete log assumption (equation 8.1).
cast network, which makes protocols such as secret bid-
The
most
costly
part
of
the
computations
is
ding as efficient as the best verifiable secret sharing. We
exponentiation. Evaluating Encrypt(z)==g7 mod p can
have also remarked that our VSS enables a network to
be performed in at most 2 |r |<2 |p |=2k multiplications
reach Byzantine Agreement in constant expected time
mod p and at most k additions. The complexity will be
without any
preprocessing.
Moreover,
the work of
determined by the speed of multiplication, which we
(GMW] suggests that verifiable secret sharing may enter
take to be O(klogk).
The dealer must encrypt a total
as a key subroutine
in protecting any protocol from
of O(n) values, hence this can be done in O(nk?logk)
faulty players, making the search for an efficient one
steps. This term swallows the cost of randomly selecting
even more important.
The bitwise communication and
the values and evaluating the polynomial at n points.
local computation complexity of our protocols are small
For the other players, the most costly steps are run-
enough, O(nk) and O((nlogn+k)nklogk) respectively,
ning Checkpiece and Recover.
A reasonable way to com-
making them feasible to implement. We believe that the
pute the product ( Yo)-( ¥2)--( Y2') is the following:
proof technique introduced to prove security may have
application to many other cryptographic protocols.
1. Set Zt o= Y;.
2. Set 244; Yj-1-1'(a)*.
Acknowledgement: I would like to thank the many peo-
3. Reset J to /+1; if /<¢ return to step 2.
ple who greatly contributed to the writeup of this paper.
The desired product is 2.
Since
|h |<logn, step 2
1 participated in an interactive proof of the results of
requires at most O(logn) multiplications, hence Check-
this
paper
with
Silvio
Micali,
whose
suggestions
piece requires O(nlogn+k) multiplications. (The & are
immeasurably helped
both
the
technical
proof and
for the exponentiation of the piece itself.) In Recover,
Presentation.
Josh Benaloh suggested basing the proto-
finding ¢+1 good pieces can require running Checkpiece
col on arbitrary encryption functions with the homomor-
2t times. Having found t+1 good pieces, a player can
phism property. Shafi Goldwasser helped simplify the
perform
the
polynomial
interpolation
using
at most
O(n?) multiplications and divisions. Thus, a player may
recover the secret in O(n(nlogn +k)klogk) steps.
436
Restrictions apply.


## Page 11

presentation by pointing out that certain complications
were
unnecessary.
David Shmoys
spent much
time
proofreading drafts so other readers wouldn’t have to;
the text was greatly clarified by his suggestions.
Sugges-
tions of Lance Fortnow and Joe Halpern have also been
incorporated.
{[ACGS]
W.
Alexi,
B.Chor,
O.
Goldreich,
and
C.
Schnorr, RSA/Rabin Bits are 1/2+1/poly(logn) Secure,
1984 FOCS.
[Ba] E. Bach, How to Generate Random Integers With
Known Factorization, 1983 STOC.
[Be] J. Benaloh, Secret Sharing Homomorphisms: Keep-
ing Shares of a Secret Secret, 1986 Crypto.
[Be2] J. Benaloh, personal communication.
[C]
B. Coan, Achieving Consensus
in Fault-Tolerant
Distributed
Computer
Systems:
Protocols,
Lower
Bounds, and Simulations, PhD. thesis, MIT, 1987.
[CC] B. Chor and B. Coan, A Simple and Efficient Ran-
domized Byzantine Agreement Algorithm, IEEE Tran-
sactions
on
Software
Engineering,
Vol.
SE-11,
No.6
1985.
[CF] J. Cohen and M. Fischer, A Robust and Verifiable
Cryptographically Secure Election Scheme, 1985 FOCS.
{[CGMA]
B. Chor,
S. Goldwasser,
S. Micali, and B.
Awerbuch
Verifiable
Secret
Sharing
and
Achieving
Simultaneity in the Presence of Faults, 1985 FOCS.
[CR] B. Chor and M. Rabin, Achieving Independence in
Logarithmic Number of Rounds,
to appear in PODC
1987.
[F] P. Feldman, MIT thesis, to appear.
[FM] P. Feldman and S. Micali, Byzantine Agreement
From Scratch in Constant Expected Time, manuscript.
[GM] S. Goldwasser and S. Micali, Probabilistic Encryp-
tion, JCSS, Vol. 28, No. 2, April 1984.
[GMW]
O. Goldreich,
S. Micali, and A. Wigderson,
Proofs
that Yield Nothing
but Their Validity and
a
Methodology of Cryptographic Protocol Design,
1986
FOCS.
[Ka] B. Kaliski, MIT thesis, to appear.
[L] D. Long, The Security of Bits in the Discrete Loga-
rithm, Princeton Thesis, 1984.
[LW] D. Long and A. Wigderson, How Discrete is the
Discrete Log?, 1983 STOC.
[M1]
V.
Miller,
Elliptic
Curves
and
Cryptography,
Crypto 1985.
[M2] V. Miller, personal communication.
[RSA]
R. Rivest, A.
Shamir,
and L. Adleman, A
Method for Obtaining Digital Signature and Public Key
Cryptosystems, Comm. of the ACM,
Vol.
21,
Feb.
1978.
[S] A. Shamir, How to Share a Secret, CACM Vol.22
No.11, 1979.
[Y] A. Yao, Theory and Applications of Trapdoor Func-
tions, 1982 FOCS.
437
Restrictions apply.
