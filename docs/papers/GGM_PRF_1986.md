# How to Construct Random Functions

**Authors:** Oded Goldreich, Shafi Goldwasser, Silvio Micali

**Published:** Journal of the ACM (JACM), Volume 33, Issue 4, October 1986

**URL:** https://people.csail.mit.edu/silvio/Selected%20Scientific%20Papers/Pseudo%20Randomness/How%20To%20Construct%20Random%20Functions.pdf

---


## Page 1

How to Construct Random Functions
ODED GOLDREICH, SHAFI GOLDWASSER,
AND SILVIO MICAL
Masachsets Inte
of Technology: Cambrde, Mastacarets
Absract A consti theory of randomnest for fnesonk, tseon smputsona
‘devetoped. anda presdorandom fancon psec is peteried, Thsoer
t
Dolomitealgochm tat tansorms pus (7), were i ny one-way fu
‘ancom
it snag toporomia-imecompuabl
fanesons
fl
2" [ln
anne
tinged fom random fenton y ay potas plyomiime
‘sks and reeves the ale ofa fancton a arguments
choice. The ret hs
‘poerapn.
random consrscions angcompli they
Categories and Subst Deriptor: F. [Theaey of Compuatin: Gener: F. 
‘Aburct Devices: Mel ofComputation
troy: C0 [Mathematics
GeneralG3 (Mathemats
of Computing: Prosabity ndSatssc~pob
alg
umber entation
(General Terms: Alors Sean. Theory
Adsona
Key WordsandParaseCrypograpy.one.nafancon. recon probl
{havesetup om 2 Manchester computer 2 s
‘sino 1000 unis oftorage whe
te 
hone seen gre mabe’ eis withan
{bean
I woul ef onyone 1 lear fom t
{lem aoutiheproramone 0B ef pred
ned vaaen,
1,
Introduction
What is meant by saying that certain functions “behave randomly"?
In this paper we provide a precise answer tothe above question. We
an efficient way to construct functions that behave randomly, ifone-w
exist. We conclude by demonstrating applications of our construction
‘Randomness has attracted much attention in the second half of 
However, mast of the previous work focused on measuring the ra
strings.
(0.Gokdrech
wassupponedia pany a Weizmann postdoctoral felowsi: S.Go
in par
by an IBM fealty seelopment award (195) and National Sconce Foundat
‘5.9008 and. Mica wassuponed bya Naonal Science Founeaton gat DCR 
TBM acl devopment Award 988)


## Page 2

How to Consiruct Random Functions
In Kolmogorov Complexity {10, 13,22. 24-26, 30, 34, 37, and 42] 
‘of randomness of a string isthe iength of its shonest description. K
randomness is an inherent property of individual strings. This appro
constructive and far from being applicable to pseudorandom string
Notably, the set of Kolmogorov-random strings is nonrecursive.
Interesting generalizations ofKolmogorov complexity have been c
(1). {19}, (36), and (38). Here a string sis “random” if't cannot be p
‘program that is both efficient (polynomial-time) and shorter than s. T
‘remains far from pseudorandom number generation. In fact no efficie
‘that uses less than k truly random bits can output a Kbit string ra
above sense.
Recently, a constructive approach to the randomness of strings
computational complerity has emerged (8. 41) In this approach aset
's polynomial random (poly-random) ifprograms that run in polynomi
to identical results when fed either with elements randomly selected 
clements randomly selected in the setof all strings. This approach is 
inthe following way: There exists a deterministic polynomial-time al
upon input of
a Abit string. outputs a poly(k)-bit string. such that,
functions exist, then the set of all output strings is poly-random.
Tnthis paper we further develop thislatter approach by introducing a 
theory ofrandomness for functions. In particular,
(1) We introduce a computational complexity measure of the ran
functions: Loosely speaking, we calla function poly-random ifn0 
time algorithm, asking forthe values of the function at arguments 
can distinguish a computation during which it receives the true v
function, from a computation during which it receives the outco
‘pendent coin flip. Notice the analogy with the Turing Test for in
(2) Assuming the existence of one-way functions we present an al
Constructing poly-random functions. Our work was motivated 
problem of[9] and [7].
Inthe est of this introduction we informally discuss the notion of 
collection: ast of functions
easy to select and evaluate, which achieve
‘with respect 10 polynomial-time computation. We compare this new
the previously considered notions of one-way functions and crypt
strong pseudorandom bit generators (CSB generator)
LLL,
Poty-RANDOM COLLECTIONS.
Let J, denote the set of all 
Consider the set He of ll functions from / nto s. Note that the card
is 2, Thusto specify
a function in H., we would need A2* bts: an
task even fora moderately large k. Assume now that forallinte
k o
selects


## Page 3

74
©. GOLD
collection # = [F;| has the following properties:
(0 frdexing: Each function in Fy bas a unigue Abit index asoca
ESU/S Ll. Thus picking randomly a funcion fe F.isexy,
bits are available.
(2) Poletime Evaluation: There exists a polynomial algrthm that (
Bon input ofan index /€ /, and an argument x 1, comput
(©) Beudorandomeness: No probabilistic algorithm that runs it tim
‘pcan distinguish the functions
in , trom the functions in He
3.1 fora precise definition.)
Seopa lection offuntion Fiscalledapoy-random collection.Loose
SSIRAE the fact thatthe functions in Fare easy to select and evalua
SERRE to an examiner with polynomially bounded resources, all the 
functions randomly selected in £4,
‘Tig, above defintion i highly consructve, We transform any CS
Gietauality pseudorandom bit generator, discused in Section 2)
fandom collection, It has been shown (se the discussion in Section 2.
‘senerators can be constructed if one-way functions exist,
I
aCOMPARSON WITH One-Way FUNCTIONS.
Informally, one-wa
Feonentians that ae eay to compute, but hard wo inver for some no
feasiga, ofthe instances. We constrict random functions fom an
ence is <onfiems the great potential present in the nouon of
function. However, this power needs to be carefully brought out
/thoueh theinvere
ofa one-way function is somewhat unpredictabl
ot mean that iti random, Infact. all functions that are currently bel
Gear -utis® vaous algebraic identities (eg, the Rivest Shamir
(RSA) function (33] is a muttiplicative permutation; thus given is m
Amy
ote can easly infer its inverse atx + y), This clearly does not ha
ceca nam fneons and infact will not happen with a function 
sitet tom a poly-candom collection (Fi. In particular, our construc
SRA
sora ientties that may be sated by the one-way func
se’ Biss from any observer with polynomially bounded resourc
the following property holds forpoly-random collections.
Rendomly choose and fx /& F. Let a probabilistic poly kbtime al
3 forthe value of on polynomially many (in k) argumentsof c
Wdig
g2ty
Then let A choosean argument
x (x # 1, for all's
as
Is now given two numbers in random order, one of whichis /Le
cine giqandom Abit number, it eannot guess which of the twois 


## Page 4

‘How to Construct Random Functions
CSB generators are efficient deterministic programs that stre
‘cbit-long input seed to 2 &-bitlong output (pseudorandom) seq
constant
1 > 0. These sequences are indistinguishable, in polynom
--bitiong truly random sequences
(see Section 2.1 fora detailed di
we can replace the coin tosses in a probabilistic poly()-time comp
bit sequence generated by a CSB generatoron a random k-bit str
almost the same results.
‘We now address the problem of efficiently simulating more compl
‘computations: computations
witha random oracle. A random oracl
‘ese of a random function:
it associates the result of a single co
‘ring. In computing witha random oracle. an algorithm queries t
stringq and receives qs associated bit (denoted 6(q)). Since 6(@) d
with time, the algorithm need not store the pair (g, b(g)) but r
‘oracleon g whenever it needs 6(q). The advantages of computing
‘oracle are clarified by all the applications listed in Secion
‘A polynomial-time computation that queries a random oracle 
length k can be trivially simulated using a CSB generator and on
below). However, this trivial simulation of the oracle requiresk' 
‘Store a randomly selected k-bit string s and denote by b the i
‘by a CSB generatoron inputs.
Let g be the ith new query (ie
asked before). Then set b(q) = 6,, append (an enco
of) 4,
(queries. and answer b. The ordered list of past queries enables
whether
a query has occurred before and, is, to give the sam
Note that the lst of past queries is indeed necessary. Such a l
‘Sgnificantly compressable (eg. for randomly selected queries). Thu
‘case the simulation requires atleast k'* bts ofstorage.
‘An interesting property of poly-random collections is that the
same result for any polynomial-time computation with a random 
‘rings. by using only & coin fips and by storing only & bits! This 
randomly selecting and storing a Kbit index specifying a functi
random collection, The bit associated with each stringx willbe
the 
Sharing Randomness in @ Distributed Environment.
An additi
‘of poly-random collections is that they enable many parties to sh
random function fin a distributed environment. By sharing fwe m
‘evaluated at diferent times by different partison the same argum
value f(x) will be obtained. Such sharing can be achieved by fli
specify a function fin a poly-random collection. These k bits are 
toand stored by each processor. No further messages need tobe excha
f-


## Page 5

Eeeere
the notion of a cryptographically strong pseudorandom bit generato
the next-bit-test T if, for all polynomials Q. for all sufficiently la
all integers
/ € (0. P(X);


## Page 6

How (o Construct Random Functions
2.2 POLYNOMIAL-TiME StaTISICAL TESTS FOR STRINGS
Jeiriion 20).
Let Pand P, be polynomials and S = U, 
tea ringaes OfPt eaences A polbnom
Fah
aint 8 probabilistic polynomialtime agora 7t
aiePE 2c PUk-it ong. andoupus ether O or 1, We
‘he tes Tl. or any polynomial @, forall suffieny large
1
lat
obi <a
shee
2! denotes the probability that T outputs 1 on Pik) r
Sting cach ar
anoles the probability that T outputs | on 
Strings, each oflength P(R),
sr seal imeret i thecase
in which the polynomial P(A)ist
‘hat the tatsical test receivesasan input a Single sag
The
following definition plays an important role in relating the 
Sroeadomness We say that'a muliset S™~ Uy Sis nen
Probab polynomiaitime algorithm that,piven
as inpet u
june
1.
(Yao [61D
Let $ =U, S, be @ samplable 
seauences. Then thefollowing thre statements are eutvalern
(8 S passes the nextbistes.
{i$ ases alpynomiatime statiica testsfr sings.
COC feases el polmomiaime satsicales whoseep con
sing
in S.
Novice that CSB sequences form a samplabe muse. Therefore,
(9 CSB sequences pass allpolmomialtime statistical ests
taini
ames! (9) evoiidy appears in (4. Howe
Theorsn'
th, 23s needed for proving te equivalence ofthe the
Trent
Thereader can derive a proto Theorem |ifomthe
‘(hich can be viewed asa generalization ofTheorem 1),
sipaMnRMETATION OF CSB GeNtRATORS.
Blum and Mic
penta mie scheme for constructing CSB generators based on a
They usec asumption asketch canbe oundin Section oi
sone lt resented the fistinsance
oftheirscheme based on spe
Nameirosntacabiltyastump
ofthe dsreelogarithm pr
Names
the next bit in the sequences produced by therpe
Teor Tan probably seater than 1+
then there would xar
aut
af en
oreyant


## Page 7

78
©. GOL
Mere
seneraly. Yao [$1] has shown how to obtain CSB generat
sencrcuation is sven. Levin (27] shows how to obtain CSB ge
‘ssmintly weaker condition: The existence of one-way functions (d
aefntion (Levin).
Let Dy & k. Let: Dk —» Dy be a sequen
spots
eetntoR be defined as follows fix) =fx) ite De 
spol
mes. LetD: & D, such that » © Di ify = /tx) for som
oneswayfunction if
(1) Fis polynomial-time computable:
(2)Jshardto inver: thats, for every probabilsic polynomial-ti
and forall sufficiently large , for every
15 15 8, x) JC
constant fraction ofthe x € Di:
(3) UD is samplable.
uonea 2. (Levin (27).
There exits a onesuay function an
exists a CSB generator,
co's bow theorem is constructive. Levin shows a particular gene
SY Eracraor ifany CSB generator exists. Levin makes use of aco
10 Yao [41], which is sketeched in Section A2 of the Appendis,
24 CSB Generators wit Easy ACCESS.
Notice that. even 
Savers feerated with a kcbiclong seed consists of polynomially
Dis @ CSB generator and a seeds define an infinite (ultimately 
Seayence bv by... Am interesting feature fis present in the gen
Ghat (71.5 that knowledge
ofthe seed allows easy accesso each othe
Ta
lok < &: the th bitin the string & can be computed in 
Teng
is due 10 the special one-way permuation on which the sec
seneror
is based. However thiseasly accestibe exponeatialy long b
Tacs ena “andor.” Blum etal. only prove that any single poly
Falezral of consecutive bits in te string passes all polynomialimne st
forssrings, provided that squaring mod a Bium.ineger’n isa one-way 
(pucrthe squares mod n). Indeed. it may be the case tha, givenB
brite
Dota its easy 10 compute any other bitin the snag,
ie easaccess open problem consists ofwhether
easy acoso e
{Ay egyts m their pseudorandom padis a “randomness preserving
din broblem was posed by Brasard [9] and Blum etal. 7]. The prob
discussed by Angluin
and Lichtenstein [3],
Notice
that there isa natural one-to-one correspondence between “
reserving” cay accesible & » 2-bi-ong strings and random funct


## Page 8

‘How
to Construct Random Functions
3. Constructing Pol»-Random Collections
In this section we show how to construct collections of functio
[Bolvmomially bounded” statistical tests A collection offunctions 
VF), such that for all k and all PE Fu f+Le
3.1 POLYNOMIAL-TIME STATISTICAL TESTS FOR FUNCTIONS.
Definition
polynomialsime statistical test for functions is
Plynomial-time algorithm T that. given & as input and acces
OF fora function
J: fs ~ 1s. outputs eitherO or
I. Algorithm T
oracle O, only by writing on a special query tape some y € /, an
oracle
answer/(») on a separate answer-tape. As usual, O, prints it
step.
Let £= \Fil be a collection of functions. We say that Fpasses c
‘any polynomial Q, forall sufficiently lange k:
opty <
Wl- <a.
Where
of denotes the probability that T outputs 1 on input k an
Grace ©) fora function Ex F, and p! denotes the probability tha
when given the input & and access t0 an oracle O, fora functionE
random function). Here the probabilities are taken over all the poss
(1'€ F. ot Hand the internal coin tosses of T.
The above definition can be interpreted as follows: & functio
/'
be random depending on its input-output relation. The test T co
phases. First it gathers information about / by getting /°s values at 
AN choice, Then it outputsits “verdict O (ift “thinks” that fy 
Gihinks” that / Ex H.) If the collection F pases the test T, then th
hen
given access to an oracle O, gives no information on whethe
1S,
He In either case T will output | with esentally the same proba
Passing all polynomial-time satisical tests for Functions isan extr
Fandommness criterion, For example, suppose that some efficient alg
Find dependencies among input-output pairs offF then d can 
[03
statistical test 7, that will output 0 upon 's detection of such 
(ie
judging that J €x F.), Since such dependencies cannot be 
[Ex Hh. the collection F = |F,| will not pass the west T,, (Fora m
discussion see Section 4.)
MWe
now exhibit a collection F that passes all polynomial-time sta
lunder the assumption that there exists
a one-way function.


## Page 9

00
©. co
Let & f By Gols)we denote the fist k bits output by
G on 
Gils) = bi s-- bic By Gi) we denote the next & bits ouput
Gis) = bias <1 bi, Let a= ayn os a be a binary mi
G0) = 60-4, AG ul)
For.
h, the function
fo
is defined
follows:
Aly) = Gx),
Let P= Longo Then P= [Fi the desired colletion*
‘The reader may find it useful to picture a function ff. +f 
binary tee of depth & with it sings stored inthe nodes nd ed
1. The Abi sting x will be sored inthe coot Ifa kt ating S
intemal node. v, then Gs) is stored in o's leftson sy and Git)
SahtsonoThe edge(0) islabeled
Oand the edge(ois bele
L{2) is then stored inthe leaf reachable from the fot following
labeledv. See Figure|
We remark that computing() on inputs x and
yrequites & - 
T. denote the aumber of tps for computing Gx) on input x ©
‘hat the functions in F, may not be one-to-one
3.3 THE Poty-Rasoouness
oF F. The collection F just define
titons
| tindesing) and
2(poy-time evaluation)
of a poy-random 
Section
1.1). The main theorem shows that condition 3 ipseado
also satis
Tutonew 3 (Mar TroRen), Let Fea collection of fnetions
im Secion 32 wsing a CSB generator G.
Then F pases al p
statistical tet forfunctions.
Paoor.
Let ws fistgivean overview ofthe proo: Weassume. fo 
that there exists some probabilistic polysomial-time saisia et f
that F does ot pas We then use 740 construct a poljnomial-ime
|
for strings. 47. We‘each acontradiction
by showing that the set of 
produced
by G does not past.
Let us consider computations ofthe statistical est Tin which T
answered by one ofthe following probabilistic algorithms f=
|
(instead of being answered by an oracle O,).
Algontho 4, answers 7s queesas follows’ Let y= iss «=yx
1. Thea
iis
ie querywith retin»
thee SecsSaga
and soshpi
pr
and
hse Finn pcr osu) and anonen 6,


## Page 10

How to Construct Random Functions
°
:
(en
&)
°
'
oA,
veo"
Guin)
= 40
fo.
The sting tthe sor in ee ecb om
‘ottotl aed
Define pt
be the probability that T outputs
| when given k
queries
are answered bralgonthm 40-1
k
Defineof (pl respecivey) tobe theprobity that Toutpts
2 input and aces to an oracle 0, for a function
/ Ex FUG f
Note that pf = pf and that p=p
As Fi asumed otto pass
thee exis
polynomial Q and
Ko tat Int =p > 1/QUU) Equivalent, Ipt
pi] > TOM)
these ofall such
We are now ready to describe the polynomiaime statistical te
Let
P be
a polynomial such that the test? makes at most Pi) o
K On input k © Kand a set Uz of Pk) sings. cath 2 be l
performs a swostagecompusaton. Inthe fist sae. ly picks | 
£-
1 with uniform probability.
In sage tw, algrity ts ves
algorthim Tand answers I's oracle quenes consistent Wing ie
|
Assume T writes y= 3)
+9 onthe orale tape.


## Page 11

02
0. 
The
probability that 4outputs | when Ui, is a randomly ch
iepreheat
CSB neater
nin g
2G ote at abu
when Cs
ta o
fan E O/0 rc Mths © aeoc
Feast (1/A) «Ip phy> Lik Qk), Thus, the sequences prod
sthaisles and we wathscone
a Ne, RL RADON COUEETUAS. Let Pan
joan some application ne woud Ihe 10 hve mo
teal thas we mn nam eters eee
Meet this need by Constructing a generalized poly-random co
prea consucion cnt sity Serie aeo
Ieper Gane Beans mo2ganc
input bits into P.(k) pseudorandom bits. For x © i, the func
att tt 28 Bou
Iw hin = Onc Be
that
of the Main Theorem, we can) prove that the collection, {
Propet}
of poyandomcee
4. Prediction Problemsand Poy Rand Clecons
IRzaa'P” Pea a eeiton podem. Th poem m
teat
|
(1) There is an a priori guarantee that the “laws ofnature” are “sim
{2 Wi posable
conduc seta
|
(3) The goal is only 10. approximately infer the “laws of nature,”
Sn(SQ en, an may contrea
aco
mine
£9cae pren one hn ee
angente tempor ace
anae
aaa
|
INSU 90 the case. uner he astimeion that on sayho
Siete SENG,
Let F = Fb 3 clin of fncti
SUS penoma ine artim capa afaa S
denay want fr atunctoneh priee
sen
eres © abou
per apna c
Sa a kt
ale the caer
OU
Sifongected from 0)ans presented the twovlees ens|e 
:
Ba aha tasercamttconciy peas ay Sa
|
is f(x). Let Q be a polynomial, We ‘Say that A Quinfers the col
BEM
Denies many parte ea ethcs
:


## Page 12

How to Construct Random Functions
CHIGREM 4. Let
F = IF) be acolecton ofanctions sats
plindesing) and
2 (polynomialtime evaluation) ofapoly-ran
F cannot be polmnomally inferred if and only if it passes 
‘Statistical tet forfunctions
peoer
Assume. rst that thee exists
probabilistic pol
{ithe
that Q.infers the collection F, Then F does not pass t
functions, 7,, descnibed here
On input
k and access
to an oracleO/(/x FoF /&y H.),
{he
inferring algorithm A with input k. For everyquery@ 
7 asks O, for f(g) and returns the answer to. Finally. w
String « a8 its chosen exam. 7. queries O, on x, randomly
Feturns
y and /(x) to
in random order. If correctly iden
Outputs I; otherwise 7; outputs
0,
or ald. when /Es Hi the probability that T, outpus | is
ther hand, for infniely many k, when Gx F. the probability
's greater
than 1+ 1/Q(0). Thus,
F does not pass the tet 7,
Conversely. assume
that F does not passa statistical test 7: T
{ folemomial Q such that for infinitely many &, |p — pi!| > 
(ot respectively) is the probability that T outputs | on input 
grace O For
Ex Fi Ue Gx Ha, respectively), Without los of g
SMa at fOr infinitely many kf — pl! > 1/Q(k), and let 
all such & Also, without loss ofgenerality. during
the sime comp
asks the same query twice and. on input k asks exactly Pik) 
Polynomial P).
{Xe construct 3 probabilistic polynomial-time algorithm ay 
subroutine
and
2+ P(&)-Qckpinfers F. On input k and acc
Qi{yEn
Fi). the algorithm Ar
proceedsas follows. I first choose
P14) ~ 1 with uniform probability. (We later reer 10 as the
invokes T with input & and uses the oracle O; to answer Ts frst
Tass for iss + Ist query. xn. then Ar outputs xe, a8 its cho
‘eceving (Xs) and 8. where Gy Je Arandomiy chooses= ©
fives = San answer to query x. Next. algorithm r continu
Queries: through ‘nwOf Tby randomly selected
iit strings F
3 bit and halts If T's output wasa 0.then
ly guesses that 2G, 
_BueSeS that: = fx.)
tn analyzing
the probably that
Ar makes a correctgues
the 
of a(k. i, ghexperiment (where # © F,) will be useful:
Ran T with input
and answer it queriesas follows. Let x, 
of:


## Page 13

08
©. co
the event “Algorithm chose index =i, Thea,
rob) iscoret
=F probit) » probiay
is correct | 4';)
= Fay
Wobeee hay)
1: prob
guesses = Eq Uzx Land 45
+ prob = fix.s)|
4'p)
Probar
guesses == flies)|z =fle.) 
1
mehy
"
= ig E [$+ poet oupus of: ey
and ary
*} ONT ouput 11s tu) ada
ssh Fa -pnteryets
TPA
3
P+
ES
2 PK) OUR)
Conoutany. Paterandom collection an not Bepolynomial i
Remark.
Out consration of polyeandom collections hat 4 
fest” Assume that Fs a plyandom cllecionconsracted 
‘ay function g Then the functonsinF" cannot be pvaomali
ifand/or ¢~' is polynomially inferable.
5.
Cryptographic Applications and Further Improvements.
Pelyrandom coectionsconstnute
avery powerfl olin a cryptog
Tas functions in such colons are ety to sles and compu v
alte desired satis prperes of random functions wih ose
tht are bounded to polyomal-ime computation, Ths gees
tmthalog for protocol ein. Fist, designaprsocal hat(p
‘andom functions and prove it comet. This ep soften vey cag 
the tay random functions by functions randomly Seed ows a
collection. Ths replacement will povaby maintain all proposes 
roto! wih respect
polynomially bounded advesanee
‘This methodology tas provided rgnous slows to such crypto
lems as message authentication with time sampng, soranclce 
‘eee identification number. identihng tend or fc systems.and
cally song hashing, A detailed discussion of thee aplication, 
Us.
Levin and Golden pointed out in (17 tat poly-random clle


## Page 14

‘How to Construct Random Functions
Sree it NC then there exits apoy-andom collin off
be evaluated in NC,
Appendix.
JE RGENT, CONDMONS FOR CovsTaucTNG CSB G
PS andBe D. ~ 10,1 Letgobe a permutation over
Some
4
f= |. Blum and Micali[8] showed that CSB 
‘constructed under the following conditions
(1)
The domain is accesible: There exists a probabilisticpolyno
Fiat on input k, chooses x & D, with uniform probl
(2) The permutation i easy
evaluate: There existsa pamonia
that on input
k andx€ D,, compute gacx)
(9)
The predicate is inapproximable: Lett be any probabilisticP
‘tgortim and Q be any polynomial. Then for al sufiemiy 
14
AUX)
# B(x) forat least
a fraction 27am te 
(6)
fete exissa polynomialsime algorithm that on input kand
Bu
8.2).
Irgeta hs shove conditions imply that gis
«one-way permuta
winset 23, Y20 [61] showed thatthe existence o's oncay p
‘suffcient condition for constructing CSB generators
Mpa RITEHOF Ya0'sConsraucrion.
Yao'sconstucion [J
Ta peyote construct Band
g as above, when given any onewi
Ahm
th| over the accessible domain £ = U. E,-By the aietons
ta Lee
eagle polynomial algorithm can inven
without 
Gna 1 faction ofthe domain, fr some constant «when ks su
$<.Ds 10 bethe Cartesian product ofk** copies
of E>
SEB
x)
= hala iat)
hae) where& By
Set Bi(x) tobe the ith bit ofhzi(x), where x © E, amd
BRS oo 0) mB @ Bilsva1n)
where @ denotes the exclusive-OR function,


## Page 15

306
©. GO
REFERENCES
(ote: Rete1 [14 i and 32atin
et)
"Aosta
Line
Siac ndRandomne:Th Meo 13, abratry o
ET. Cote, M1
2
Arn, W Chon, BGO. 0. 40 SOOM CP. RSA and Rai
as eat Bed he whole STA
J Cpa abpear (Aa trae 
‘Prserigs ofthe 20 IEEE Sogo
on FndaonsCompas
en
{ots pp 8-87),
3 StU. ANo Levon. B. Proalexu ofcapanneme: A 
284 Dent ofCompas Scene Yate Unie New Haven Coos to
+ Bewse.. H AN0 Gi
J. Relves andom ork.
P* N
robb. SATY? Compu 14188) 9618
§ Bowe
M. Cyon.
2. AN9 Stat. On heenpta
scr of 
Prxenies of he 58 ACM Simpson on Thy ofCompany
oes 
‘ACME New Yon 98, p21,
|
© RiS-Or M. Goxpaicn. . Mica. Saxo RIVES. R LA fir protoce fo
{n dwomata,Lanewae
on Prorareing. 30Clos W. Baer 8
Compu Sint
194 Sprig Vera New York 198 p04oh
7 Biot
L- BlumML 290 Sit Mr singe unpredicabe peudo-andoa 
SUAMS Compas 15 hay 1986, 36-383,
* RieM saMicaS\Howo rete cplogapicly rong ques 
iS147 Compa 15 Now 90 50S
%
Brssuto-G. On compuatonsly see sentation teu
short 
In tunes in Crpuoy:Prceding
of Crpted2 B:Caum Re
Riven a
Es Meum Pra New Var 18) pp Te
10 Cur
GJ. ”On Be eho propane comping nie inary se
(e968 7-30
1 Dare
ano Huge. M.E. New direction in rtapaphy. IEEE 
ITiNe. 890, oust
1 Faaze
4M Kanan AMO LAGARAG JC. Lina cngremi enalo
REPRE Pree ofthe2hSopraonFoun
@ 
{EE
New Yor 198 p. shots,
12 Gace
P."On tesyne ofan
maton Sov Mah Dot 15(9
| Gotonuen
0. Gotowasien
§. avo Meas S How tacoun
Meno 24 Labor
fr Compu ence MIT.Cambs:
Ms, Now 10
"5 Gotonbon 0.Couowasen
Sano Men 8. Ontcypupapies
{encons. In Advances
in Contin Prcenngs
of Cre B Buty€6 
Gomoue Sens. vl. 196. Seige
New York 8368
"6 Goxown, Praline encryption Thorsd applcatens, Pa. is
Comoe Scene,Un of aor, Sey Cas at
17 Govowase 5: MicaSnRET.
RL.” Apn
sqnaure ee
:
ofthe 350 IEEE Sooo om Pounds of Compaer Samce TEE N
mesic,
!
‘17 GoupwasseR, A MICALL S. ANO Rivest, RL L. A cipal signature schem
iin chen mete asc.Sar Corp tages
"8 Govow se S. Mica ano Ton,” Why ad how eb pate
[nek In csing of he2d EE Simp
on Fanon of Compa
New Yor (9825p. testa
"9
Hearwani
J.”Genezes Kolmgoroycompe and hestro ee


## Page 16

How to Consiruet Random Functions
25, Lew. LA. Vanous meats of compleity for finite obec (axiomat
Mah Ook 17,2(0996 332-538
26
Levin: LA Randomecs conseration teqeiies infomation and in
‘matical thease la”Con4 {T984 15-37
27 Lavy LA" Onesay function and pewdorandom serra Proceedi
Sampo
on Theory of Compuing(Prodence. Rl May ©8) AC
pp 3-36,
2% Lowe, D.L- ao Wicoenon. A. How dirt is dcr log? I pepa
Elon seared
Proceeding of
13th ACMSige on Tae o
Mas. Aor.25-27) ACM. Now York. 1988 pp 13-050
29. Lun Mo RacxorC. Paes random pean generators abd 
$50,
iscen
fhe 8th ACM Symposium on Taeoryf Compu 
24-30, ACM New York.1986
pp.5882363
70
ManroLor.P. The deaition ofrandom sequences.
Conrol (196),
531 PluwsreaD.Iemng egence genes by linea compres a P
IEEE Simiposum on Founions
of Computer Sconce IEEE New Vor, N
5% Ratin MO
Diilizes gates
and public keySncto
a intacab
Rep 212 Latoratory for Computer Science Cambri. Mas, 1D
5, Ror, R. Suan A. aso ADLEMAN, LA method for bung itl 
keycrvpoayems.Comman. 4C¥. 21-2 (Feb 979, 120-198
M Scwonn.
C.F. felt und Wohnen. Lect Noe in Ma
‘SeringerVerig New York. 197
58 Stat A On theeneraion ofcnprogapnicaly strong puedorandom eq
{Comput Sf eb 983, 38-8
36,
Sieh. M.A complenty theoretic approach 1 randomes. In Poeedn
Semana ox Theo of Comuaine (Boson, Mat. Apr 25-27) ACME
bosses
3. Souomonort.R.
J.”
formal theory indie ference ff Contr. (
3% Wats: RE Randomses and the densty of ha pcos In Paet
‘Somposam ov Foundatoes of Comper Sconce IEEE. New York. 1983 9p 
2%. Nazi UV. ao VastWs¥, RSA bare 732 + setae Ia
Pecedies
of Cspot. Chum.Ed Peni Press New Yor, AL op 
©. Vaz Uv. Avo Varbane VV. Elin nd sou peudoranioe 
In Prcedings ofthe 250k IEEE Simpoium on Foundation of Computer 
‘York
1984p 456-1653.
41 Yao A.C. Theoryand application of poor functions In Prcedigs
‘Semposum onFoundation of Compuer Sconce IEEE New York. 1008 pe
‘2 Ziowus AK. ano tvs L.A Thecompli f Bite cersand s
‘feandompes
and iran, UMN (Rutan Mah Sunennens
oeiSNO 
ICEIVEO CCToRER 1984; VIED NovEuM 1985; AccEFTEO NovEMER 1985
