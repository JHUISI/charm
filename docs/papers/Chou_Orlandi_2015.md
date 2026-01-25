# The Simplest Protocol for Oblivious Transfer

**Authors:** Tung Chou, Claudio Orlandi

**Published:** LATINCRYPT 2015

**ePrint:** https://eprint.iacr.org/2015/267

---

# **The Simplest Protocol for Oblivious Transfer**

Tung Chou and Claudio Orlandi


Technische Universieit Eindhoven and Aarhus University


**Abstract** Oblivious Transfer (OT) is one of the fundamental building blocks of cryptographic protocols. In this paper we describe the simplest and most efficient protocol for 1-out-of- _n_ OT to date, which
is obtained by tweaking the Diffie-Hellman key-exchange protocol. The protocol allows to perform _m_
1-out-of- _n_ OTs using only 2 + 3 _m_ full exponentiations (2 _m_ for the receiver, 2 + _m_ for the sender) and,
sending only _m_ + 1 group elements and 2 _mn_ ciphertexts. We also report on an implementation of the
protocol using elliptic curves, and on a number of mechanisms we employ to ensure that our software
is secure against active attacks too. Experimental results show that our protocol (thanks to both algorithmic and implementation optimizations) is at least one order of magnitude faster than previous
work.


**Update: The proceeding version of this paper contains incorrect claims. See Section 1.1 for**
**details.**


**1** **Introduction**
**Diffie-Hellman Key Exchange**



Oblivious Transfer (OT) is a cryptographic primitive defined as follows: in its simplest flavour, 1-out-of-2 OT,
a sender has two input messages _M_ 0 and _M_ 1 and a receiver has a choice bit _c_ . At the end of the protocol the
receiver is supposed to learn the message _Mc_ and nothing
else, while the sender is supposed to learn nothing. Perhaps surprisingly, this extremely simple primitive is sufficient to implement any cryptographic task [Kil88]. OT
can also be used to implement most advanced cryptographic tasks, such as secure two- and multi-party computation (e.g., the millionaire’s problem) in an efficient
way [NNOB12,BLN [+] 15].
Given the importance of OT, and the fact that most
OT applications require a very large number of OTs, it is
crucial to construct OT protocols which are at the same
time efficient and secure against realistic adversaries.


**A Novel OT Protocol.** In this paper we present a novel
and extremely _simple_, _efficient_ and _secure_ OT protocol.
The protocol is a simple tweak of the celebrated DiffieHellman (DH) key exchange protocol. Given a group G
and a generator _g_, the DH protocol allows two players
Alice and Bob to agree on a key as follows: Alice samples
a random _a_, computes _A_ = _g_ _[a]_ and sends _A_ to Bob. Symmetrically Bob samples a random _b_, computes _B_ = _g_ _[b]_

and sends _B_ to Alice. Now both parties can compute
_g_ _[ab]_ = _A_ _[b]_ = _B_ _[a]_ from which they can derive a key _k_ .
The key observation is now that Alice can also derive a
different key from the value ( _B/A_ ) _[a]_ = _g_ _[ab][−][a]_ [2], and that
Bob cannot compute this group element (assuming that
the computational DH problem is hard).



**Sender** **Receiver**
Input: ( _M_ ) Input: none
Output: none Output: _M_


_a ←_ Z _p_ _b ←_ Z _p_
_A_ = _g_ _[a]_       
_B_ = _g_ _[b]_


_k_ = _H_ ( _B_ _[a]_ ) _k_ = _H_ ( _A_ _[b]_ )
_e ←_ _Ek_ ( _M_ )

      
_M_ = _Dk_ ( _e_ )


**Our OT Protocol**


**Sender** **Receiver**
Input: ( _M_ 0 _, M_ 1) Input: _c_
Output: none Output: _Mc_


_a ←_ Z _p_ _b ←_ Z _p_
_A_ = _g_ _[a]_       
if _c_ = 0: _B_ = _g_ _[b]_

if _c_ = 1: _B_ = _Ag_ _[b]_

_B_


_k_ 0 = _H_ ( _B_ _[a]_ ) _kR_ = _H_ ( _A_ _[b]_ )
_k_ 1 = _H_ �� _BA_  - _a_  
_e_ 0 _←_ _Ek_ 0 ( _M_ 0)
_e_ 1 _←_ _Ek_ 1 ( _M_ 1)

      
_Mc_ = _DkR_ ( _ec_ )


**Figure 1.** Our protocol in a nutshell


We can now turn this into an OT protocol by letting Alice play the role of the sender and Bob the role of
the receiver (with choice bit _c_ ) as shown in Figure 1. The first message (from Alice to Bob) is left unchanged
(and can be reused over multiple instances of the protocol) but now Bob computes _B_ as a function of his
choice bit _c_ : if _c_ = 0 Bob computes _B_ = _g_ _[b]_ and if _c_ = 1 Bob computes _B_ = _Ag_ _[b]_ . At this point Alice
derives two keys _k_ 0 _, k_ 1 from ( _B_ ) _[a]_ and ( _B/A_ ) _[a]_ respectively. It is easy to check that Bob can derive the key
_kc_ corresponding to his choice bit from _A_ _[b]_, but cannot compute the other one. This can be seen as a _random_
_OT_ i.e., an OT where the sender has no input but instead receives two random messages from the protocol,
which can be used later to encrypt his inputs, thus achieving the OT functionality.


**A Secure and Efficient Implementation.** We report on an efficient and secure implementation of the
1-out-of-2 random OT protocol: Our choice for the group is a twisted Edwards curve that has been used
by Bernstein, Duif, Lange, Schwabe and Yang for building the Ed25519 signature scheme [BDL [+] 11]. The
security of the curve comes from the fact that it is birationally equivalent to Bernstein’s Montgomery curve
Curve25519 [Ber06] where ECDLP is believed to be hard: Bernstein and Lange’s SafeCurves website [BL14]
reports cost of 2 [125] _[.]_ [8] for solving ECDLP on Curve25519 using the _rho method_ . The speed comes from the
complete formulas for twisted Edwards curves proposed by Hisil, Wong, Carter, and Dawson in [HWCD08].
We first modify the code in [BDL [+] 11] and build a fast implementation for a single OT. Later we build
a vectorized implementation that runs OTs in batches. A comparison with the state of the art shows that
our vectorized implementation is at least an order of magnitude faster than previous work (we compare in
particular with the implementation reported by Asharov, Lindell, Schneider and Zohner in [ALSZ13]) on
recent Intel microarchitectures. Furthermore, we take great care to make sure that our implementation is
secure against both passive attacks (our software is _immune to timing attacks_, since the implementation is
_constant-time_ ) and active attacks (by designing an appropriate encoding of group elements, which can be
efficiently verified and computed on). Our code can be downloaded from `[http://orlandi.dk/simpleOT](http://orlandi.dk/simpleOT)` .


**Organization.** The rest of the paper is organized as follows: in Section 1 we discuss related work; in
Section 2 we formally describe and analyse our protocol; Section 3 describes the chosen representation of
group elements; Section 4 describes the low level building blocks of the group operations; and Section 5
reports the timings of our implementation.


**Related Work.** OT owes its name to Rabin [Rab81] (a similar concept was introduced earlier by Wiesner [Wie83] under the name of “conjugate coding”). There are different flavours of OT, and in this paper
we focus on the most common and useful flavour, namely - _n_ 1�-OT, which was first introduced in [EGL85].
Many efficient protocols for OT have been proposed over the years. Some of the protocols which are most
similar to ours are those of Bellare-Micali [BM89] and Naor-Pinkas [NP01]. More recent OT protocols such
as [HL10,DNO08,PVW08] focus on achieving a strong level of security in concurrent settings [1] without relying on the random oracle model. Unfortunately this makes these protocols more cumbersome for practical
applications: even the most efficient of these protocols i.e., the protocol of Peikert, Vaikuntanathan, and
Waters [PVW08] requires 11 exponentiations for a single �21�-OT and a common random string (which must
be generated by some trusted source of randomness at the beginning of the protocol).


**OT Extension.** While OT provably requires “public-key” type of assumptions [IR89] (such as factoring,
discrete log, etc.), OT can be “extended” [Bea96] in the sense that it is enough to generate few “seed” OTs
based on public-key cryptography which can then be extended to any number of OTs using symmetric-key
primitives only (PRG, hash functions, etc.). This can be seen as the OT equivalent of _hybrid encryption_
(where one encrypts a large amount of data using symmetric-key cryptography, and then encapsulates the
symmetric-key using a public-key cryptosystem). OT extension can be performed very efficiently both against
passive [IKNP03,ALSZ13] and active [Nie07,NNOB12,Lar14,ALSZ15,KOS15] adversaries. Still, to bootstrap
OT extension we need a secure and efficient OT protocol for the seed OTs (as much as we need secure and
efficient public-key encryption schemes to bootstrap hybrid encryption): The OT extension of [ALSZ15]
reports that it takes time (7 _·_ 10 [5] + 1 _._ 3 _m_ ) _µs_ to perform _m_ OTs, where the fixed term comes from running
190 base OTs. Using our protocol as the base OT in [ALSZ15] would reduce the initial cost to approximately


1 I.e., UC security [Can01], which is impossible to achieve without some kind of trusted setup assumptions [CF01].


2


190 _·_ 114 _≈_ 2 _·_ 10 [4] _µs_ [Sch15], which leads to a significant overall improvement (e.g., a factor 10 for up to
4 _·_ 10 [4] OTs and a factor 2 for up to 5 _·_ 10 [5] OTs).


**1.1** **Incorrect Security Claim in Proceeding Version**


The proceeding version of this work [CO15] claims that our protocol achieves UC security. The claim is
incorrect, and has therefore been removed from this version.
Li and Micciancio [LM18] showed that the protocol cannot be simulated in the equational framework,
due to subtle timing attacks. Gen¸c, Iovino and Rial [GIR17] pointed out a problem with the proof of security,
noticing that the protocol cannot be proven secure under the CDH assumption. [2] This particular problem was
later fixed by Hauck and Loss using the GapDH assumption [HL17], who also proposed a different protocol
based on the CDH assumption only.
It was later pointed out by several authors (Byali, Patra, Ravi and Sarkar [BPRS17], Doerner, Kondi,
Lee and shelat [DKLs18]), that the extraction strategy in the case of a corrupt receiver in the original
proof of security is incompatible with composable security. In a nutshell, the issue is that a corrupt sender
can “attack” the protocol by delaying decryption. Thus, the simulator cannot extract the input of the
receiver before the protocol is over (and cannot use said inputs to simulate later protocol messages e.g.,
when combining our OT with garbled circuits). It appears that this problem can be circumvented if the next
protocol message is from the receiver to the sender, and this message is a “proof of timely decryption” in the
sense that the sender will check this “proof” and only accept if indeed the the receiver has performed the
necessary decryption queries. This technique has been employed by Barreto, David, Dowsley, Morozov and
Nascimento in [BDD [+] 17], where OT protocols in the random oracle from different assumptions are presented
(their protocol contains an ad-hoc “proof of timely decryption”) and in [DKLs18] (where our OT is combined
with an OT extension protocol, which informally works as “proof of timely decryption”). See [CJS14] for a
more thorough discussion of the issues arising in using random oracles in UC-proof of security, and for an
OT protocol that can be proven secure in the “global” random oracle model.


**2** **The Protocol**


**Notation.** If _S_ is a set _s ←_ _S_ is a random element sampled from _S_ . We work over an additive group
(G _, B, p,_ +) of prime order _p_ (with log( _p_ ) _> κ_ ) generated by _B_ (the base point), and we use the additive
notation for the group since we later implement our protocol using elliptic curves. Given the representation
of some group element _P_ we assume it is possible to efficiently verify if _P ∈_ G. We use [ _n_ ] as a shortcut for
_{_ 0 _,_ 1 _, . . ., n −_ 1 _}_ .


**Building Blocks.** We use a hash-function _H_ : (G _×_ G) _×_ G _→{_ 0 _,_ 1 _}_ _[κ]_ as a key-derivation function to extract
a _κ_ bit key from a group element, and the first two inputs are used to seed the function. [3] We model _H_ as a
random oracle when arguing about the security of our protocol.

**Input/Outputs.** We want to implement _m_ - _n_ 1�-OT’s for _ℓ_ -bit messages with _κ_ -bit security between a sender
_S_ and a receiver _R_ . The receiver _R_ has a vector of indices ( _c_ [1] _, . . ., c_ _[m]_ ) _∈_ [ _n_ ] _[m]_, and the sender _S_ has _m_
vectors of message _{_ ( _M_ 0 _[i][, . . ., M]_ _n_ _[ i]_ _−_ 1 [)] _[}]_ _i∈_ [ _m_ ] [for all] _[ i, j]_ [ :] _[ M][ j]_ _i_ _[∈{]_ [0] _[,]_ [ 1] _[}][ℓ]_ [. At the end of the protocol the receiver]
_R_ outputs a vector of _ℓ_ -bit strings ( _z_ [1] _, . . ., z_ _[n]_ ), such that for all _i ∈_ [ _m_ ], _z_ _[i]_ = _Mc_ _[i][i]_ [.]


**2.1** **Random OT**


We split the presentation in two parts: first, we describe and analyze a protocol for _random OT_ where the
sender outputs _n_ random keys and the receiver only learns one of them; then, we describe how to combine


2 See also `[https://eprint.iacr.org/forum/read.php?18,962](https://eprint.iacr.org/forum/read.php?18,962)` .
3 Standard hash functions do not take group elements as inputs, and in later sections we will give explicit encodings
of group elements into bitstrings.


3


this protocol with an appropriate encryption scheme to complete the OT. We are now ready to describe our
novel _random OT_ protocol:


**Setup:** (only once, independent of _m_ ):

1. _S_ samples _y ←_ Z _p_ and computes _S_ = _yB_ and _T_ = _yS_ ;
2. _S_ sends _S_ to _R_, who aborts if _S ̸∈_ G;
**Choose:** (in parallel for all _i ∈_ [ _m_ ])

1. _R_ (with input _c_ _[i]_ _∈_ [ _n_ ]) samples _x_ _[i]_ _←_ Z _p_ and computes


_R_ _[i]_ = _c_ _[i]_ _S_ + _x_ _[i]_ _B_


2. _R_ sends _R_ _[i]_ to _S_, who aborts if _R_ _[i]_ _̸∈_ G;
**Key Derivation:** (in parallel for all _i ∈_ [ _m_ ])

1. For all _j ∈_ [ _n_ ], _S_ computes
_kj_ _[i]_ [=] _[ H]_ ( _S,R_ _[i]_ ) [(] _[yR][i][ −]_ _[jT]_ [)]


2. _R_ computes
_kR_ _[i]_ [=] _[ H]_ ( _S,R_ _[i]_ ) [(] _[x][i][S]_ [)]


**Basic Properties.** The key _kj_ _[i]_ [is computed by hashing] _[ x][i][yB]_ [ + (] _[c][i][ −]_ _[j]_ [)] _[T]_ [ and therefore at the end of the]
protocol _kR_ _[i]_ [=] _[ k]_ _c_ _[i][i]_ [ if both parties are honest. It is also easy to see that:]


**Lemma 1.** _No (computationally unbounded) S_ _[∗]_ _on input R_ _[i]_ _can guess c_ _[i]_ _with probability greater than_ 1 _/n._


_Proof._ Since _B_ generates G, fixed any _P_ = _x_ 0 _B_ the probability that _R_ _[i]_ = _P_ when _c_ _[i]_ = _j_ is the probability
that _x_ _[i]_ = ( _x_ 0 _−_ _c_ _[i]_ _y_ ), therefore _∀S, P ∈_ G _, j ∈_ [ _n_ ], Pr[ _R_ _[i]_ = _P_ _|c_ _[i]_ = _j_ ] = 1 _/p_, which is independent of _j_ .


**Lemma 2.** _No (computationally bounded) R_ _[∗]_ _can output any two keys kj_ _[i]_ 0 _[and][ k]_ _j_ _[i]_ 1 _[with][ j]_ [0] _[ ̸]_ [=] _[ j]_ [1] _[ ∈]_ [[] _[n]_ []] _[ if the]_
_computational Diffie-Hellman problem is hard in_ G _._


_Proof._ In the random oracle model _R_ _[∗]_ can only (except with negligible probability) compute _kj_ _[i]_ 0 _[, k]_ _j_ _[i]_ 1 [by]
querying the oracle on points of the form _U_ 0 _[i]_ [= (] _[yR][i][ −]_ _[j]_ [0] _[T]_ [) and] _[ U]_ 1 _[ i]_ [= (] _[yR][i][ −]_ _[j]_ [1] _[T]_ [). Assume for the sake]
of contradiction that there exist a PPT _R_ _[∗]_ who outputs ( _R, j_ 0 _, j_ 1 _, U_ 0 _, U_ 1) _←R_ _[∗]_ ( _B, S_ ) such that ( _j_ 1 _−_
_j_ 0) _[−]_ [1] ( _U_ 0 _−_ _U_ 1) = _T_ = log _B_ ( _S_ ) [2] _B_ with probability at least _ϵ_ . We show an algorithm _A_ which on input
( _B, X_ = _xB, Y_ = _yB_ ) outputs _Z_ = _xyB_ with probability greater than _ϵ_ [3] . Run ( _R_ _[X]_ _, U_ 0 _[X]_ _[, U]_ 1 _[ X]_ [)] _[ ←R][∗]_ [(] _[B, X]_ [),]
( _R_ _[Y]_ _, U_ 0 _[Y]_ _[, U]_ 1 _[ Y]_ [)] _[ ←R][∗]_ [(] _[B, Y]_ [ ), then run (] _[R]_ [+] _[, U]_ 0 [ +] _[, U]_ 1 [ +][)] _[ ←R][∗]_ [(] _[B, X]_ [ +] _[ Y]_ [ ) and finally output]


_Z_ = [(] _[p]_ [ + 1)] �( _U_ 0 [+] [+] _[ U]_ 1 [ +][)] _[ −]_ [(] _[U]_ 0 _[ X]_ [+] _[ U]_ 1 _[ X]_ [)] _[ −]_ [(] _[U]_ 0 _[ Y]_ [+] _[ U]_ 1 _[ Y]_ [)]         
2


Now _Z_ = _xyB_ with probability at least _ϵ_ [3], since when all three executions of _R_ _[∗]_ are successful, then
_U_ 0 _[X]_ [+] _[ U]_ 1 _[ X]_ [= (] _[x]_ [2][)] _[B]_ [,] _[ U]_ 0 _[ Y]_ [+] _[ U]_ 1 _[ Y]_ [= (] _[y]_ [2][)] _[B]_ [ and] _[ U]_ 0 [ +] _[, U]_ 1 [ +] [= (] _[x]_ [ +] _[ y]_ [)][2] _[B]_ [ and therefore] _[ Z]_ [ =] _[p]_ [+1] 2 [2] _[xyB]_ [ =] _[ xyB]_ [.] _⊓⊔_


Note that the above proof loses a cubic factor. A better proof for this lemma, which only loses a quadratic
factor, can be found in [BCP04].


**From Random OT to** _**standard**_ **OT.** We start by adding a transfer phase to the protocol, where the
sender sends the encryption of his messages to the receiver:


**Transfer:** (in parallel for all _i ∈_ [ _m_ ])

1. For all _j ∈_ [ _n_ ], _S_ computes _e_ _[i]_ _j_ _[←]_ _[E]_ [(] _[k]_ _j_ _[i]_ _[, M]_ _j_ _[ i]_ [)]
2. _S_ sends ( _e_ _[i]_ 0 _[, . . ., e]_ _n_ _[i]_ _−_ 1 [) to] _[ R]_ [;]
**Retrieve:** (in parallel for all _i ∈_ [ _m_ ])

1. _R_ computes and outputs _z_ _[i]_ = _D_ ( _k_ _[i]_ _, e_ _[i]_ _c_ _[i]_ [).]


4


The protocol uses a symmetric encryption scheme ( _E, D_ ). We call _K, M, C_ the key space, message space
and ciphertext space respectively and _κ_ the security parameter. We allow the decryption algorithm to output
a special symbol _⊥_ to indicate an invalid ciphertext. We want to use an encryption scheme that satisfies the
following properties:


**Definition 1.** _We say a symmetric encryption scheme_ ( _E, D_ ) _is_ non-committing _if there exist PPT algo-_
_rithms S_ 1 _, S_ 2 _such that ∀M ∈M_ ( _e_ _[′]_ _, k_ _[′]_ ) _and_ ( _e, k_ ) _are computationally indistinguishable where e_ _[′]_ _←S_ 1(1 _[κ]_ ) _,_
_k_ _[′]_ _←S_ 2( _e_ _[′]_ _, M_ ) _, k ←K and e ←_ _E_ ( _k, M_ ) _(S_ 1 _, S_ 2 _are allowed to share a state)._


The definition says that it is possible for a simulator to come up with a ciphertext _e_ which can later be
“explained” as an encryption of any message, in such a way that the joint distribution of the ciphertext
and the key in this simulated experiment is indistinguishable from the normal use of the encryption scheme,
where a key is first sampled and then an encryption of _M_ is generated.


**Definition 2.** _Let S be a set of random keys from K and VS,e ⊆_ _S the subset of valid keys for a given_
_ciphertext e i.e., the keys in S such that D_ ( _k, e_ ) _̸_ = _⊥._
_We say_ ( _E, D_ ) _satisfies_ robustness _if for all ciphertexts e ←A_ (1 _[κ]_ _, S_ ) _adversarially generated by a PPT_
_A, |VS,e| ≤_ 1 _except with negligible probability._


The definition says that it should be hard for an adversary to generate a ciphertext which can be
decrypted to more than one valid ciphertext using any polynomial number of randomly generated keys (even
for adversaries who see those keys before generating the ciphertext).
Traditionally ciphertext integrity is defined for an adversary who has access to an encryption oracle, but
the above definition suffices for our goal.


**A concrete example.** We give a concrete example of a very simple scheme which satisfies Definition 1
and 2: let _M_ = _{_ 0 _,_ 1 _}_ _[ℓ]_ and _K_ = _C_ = _{_ 0 _,_ 1 _}_ _[ℓ]_ [+] _[κ]_ . The encryption algorithm _E_ ( _k, m_ ) parses _k_ as ( _α, β_ ) and
_e_ = ( _m ⊕_ _α, β_ ). The decryption algorithm _D_ ( _k, e_ ) parses _k_ = ( _α, β_ ) and _e_ = ( _e_ 1 _, e_ 2) and outputs _⊥_ if _e_ 2 _̸_ = _β_
or outputs _m_ = _e_ 1 _⊕_ _α_ otherwise. It can be shown that:


**Lemma 3.** _The scheme_ ( _E, D_ ) _defined above satisfies Definition 1 and 2._


_Proof._ We show that the scheme satisfies Definition 1 and 2 in a strong, information theoretic sense. For
Definition 1: _S_ 1 outputs a random _e ←{_ 0 _,_ 1 _}_ _[ℓ]_ [+] _[κ]_ ; _S_ 2( _e, M_ ) parses _e_ = ( _e_ 1 _, e_ 2) and outputs _k_ = ( _e_ 1 _⊕_ _M, e_ 2).
The simulated distribution is trivially identical to the real one. For Definition 2: given any ciphertext _e_ =
( _e_ 1 _, e_ 2), _D_ (( _α, β_ ) _, e_ ) _̸_ = _⊥_ implies that _β_ = _e_ 2. Thus even an unbounded adversary can break robustness of
the scheme only if there are two keys _ki, kj ∈_ _S_ such that _βi_ = _βj_ which only happens with probability
negligible in _κ_ .


**Non-Malleability in Practice.** When instantiating our protocol we must replace the random oracle with
a hash function. To approximate the model, one can “localize” the random oracle by prepending the parties
_id_ ’s and the session _id_ to the hash function. We argue here that our choice of using the transcript of the
protocol ( _S, R_ _[i]_ ) as salt for the hash function helps in making sure that the oracle is _local_ to the protocol,
and helps against malleability attacks in cases where the parties’ and session _id_ ’s are unavailable. Consider
the following man-in-the middle attack, where an adversary _A_ plays two copies of the - _n_ 1�-OT, one as the
sender with _R_ and one as the receiver with _S_ . Here is how the attack works: 1) _A_ receives _S_ from _S_ and
forwards it to _R_ ; 2) Then the adversary receives _R_ from _R_ and sends _R_ _[′]_ = _S_ + _R_ to _S_ ; 3) Finally _A_ receives
the _{ei}i∈_ [ _n_ ] from _S_ and sets _e_ _[′]_ _i_ [=] _[ e]_ [(] _[i][−]_ [1 mod] _[ n]_ [)] [to] _[ R]_ [. It is easy to see that if the same hash function is used to]
instantiate the random oracle in the two protocols (and if _c ̸_ = 0), then the honest receiver outputs _z_ = _Mc_ +1,
which is clearly a breach of security (i.e., this attack could not be run if the protocols are replaced with OT
functionalities).
The previous attack can be seen as a malleability attack on the choice bit. An adversary can also try a
malleability attack on the sender messages by forwarding ( _S_ _[′]_ _, R_ _[′]_ ) = ( _S, R_ ) but then manipulating the _ei_ ’s
into ciphertexts _e_ _[′]_ _i_ [which decrypt to related messages. In the] �21�-OT, these attacks can be mitigated by using


5


_authenticated encryption_ for ( _E, D_ ) (which also satisfies _robustness_ as in Definition 2). Now an adversary
who changes both ciphertext is equivalent to an ideal adversary using input ( _⊥, ⊥_ ), while an adversary who
only changes one ciphertext, say _ec_, is equivalent to an adversary which uses input bit 1 _−_ _c_ on the left and
inputs ( _m_ 1 _−c, ⊥_ ) on the right. This attack could also be run in an idealized world where parties have access
to an OT functionality. Unfortunately for - _n_ 1�-OT (with _n >_ 2) this is not the case, since the protocol allows
to “copy” any subset of messages, which would not be possible in an idealized setting.


**3** **The Random OT Protocol in Practice**


This section describes how the random OT protocol can be realized in practice. In particular, this section
focuses on describing how group elements are represented as bitstrings, i.e., the _encodings_ . In the abstract
description of the random OT protocol, the sender and the receiver transmit and compute on “group elements”, but clearly any implementation of the protocol transmits and computes on bitstrings. We describe
how the encodings are designed to achieve efficiency (both for communication and computation) and security
(particularly against a malicious party who might try to send malformed encodings).

**The Group.** The group G we choose for the protocol is a subset of G [¯] ; G [¯] is defined by the set of points on
the twisted Edwards curve


_{_ ( _x, y_ ) _∈_ F2255 _−_ 19 _×_ F2255 _−_ 19 : _−x_ [2] + _y_ [2] = 1 + _dx_ [2] _y_ [2] _}_


and the twisted Edwards addition law




      - _x_ 1 _y_ 2 + _x_ 2 _y_ 1
( _x_ 1 _, y_ 1) + ( _x_ 2 _, y_ 2) =



1 _−_ _dx_ 1 _x_ 2 _y_ 1 _y_ 2



_x_ 1 _y_ 2 + _x_ 2 _y_ 1

_,_ _[y]_ [1] _[y]_ [2][ +] _[ x]_ [1] _[x]_ [2]
1 + _dx_ 1 _x_ 2 _y_ 1 _y_ 2 1 _−_ _dx_ 1 _x_ 2 _y_ 1







introduced by Bernstein, Birkner, Joye, Lange, and Peters in [BBJ [+] 08]. The constant _d_ and the generator
_B_ can be found in [BDL [+] 11]. The two groups G [¯] and G are isomorphic respectively to Z _p ×_ Z8 and Z _p_ with
_p_ = 2 [252] + 27742317777372353535851937790883648493.


**Encoding of Group Element.** An _encoding E_ for a group G0 is a way of representing group elements
as fixed-length bitstrings. We write _E_ ( _P_ ) for a bitstring which represents _P ∈_ G0. Note that there can be
multiple bitstrings that represent _P_ ; if there is only one bitstring for each group element, _E_ is said to be
_deterministic_ ( _E_ is said to be _non-deterministic_ otherwise [4] ). Also note that some bitstrings (of the fixed
length) might not represent any group element; we write _E_ (G1) for the set of bitstrings which represent some
element in G1 _⊆_ G0. _E_ is said to be _verifiable_ if there exists an efficient algorithm that, given a bitstring as
input, outputs whether it is in _E_ (G0) or not.

**The Encoding** _EX_ **for Group Operations.** The non-deterministic encoding _EX_ for G [¯], which is based
on the _extended coordinates_ in [HWCD08], represents each point using the tuple ( _X_ : _Y_ : _Z_ : _T_ ) with
_XY_ = _ZT_, representing _x_ = _X/Z_ and _y_ = _Y/Z_ . We use _EX_ whenever we need to perform group operations
since given _EX_ ( _P_ ) _, EX_ ( _Q_ ) where _P, Q ∈_ G [¯], it is efficient to compute _EX_ ( _P_ + _P_ ), _EX_ ( _P_ + _Q_ ), and _EX_ ( _P −_ _Q_ ).
In particular, given an integer scalar _r ∈_ Z _p_ it is efficient to compute _EX_ ( _rB_ ), and given _r_ and _EX_ ( _P_ ) it is
efficient to compute _EX_ ( _rP_ ).

**The Encoding** _E_ 0 **and Related Encodings.** The deterministic encoding _E_ 0 for G [¯] represents each group
element as a 256-bit bitstring: the natural 255-bit encoding of _y_ followed by a sign bit which depends only
on _x_ . The way to recover the full value _x_ is described in [BDL [+] 11, Section 5], and group membership can be
verified efficiently by checking whether _x_ [2] ( _y_ [2] _−_ 1) = _dy_ [2] + 1 holds; therefore _E_ 0 is verifiable. See [BDL [+] 11]
for more details of _E_ 0.
For the following discussions, we define deterministic encodings _E_ 1 and _E_ 2 for G as


_E_ 1( _P_ ) = _E_ 0(8 _P_ ) _, E_ 2( _P_ ) = _E_ 0(64 _P_ ) _, P ∈_ G _._


4 We stress that non-deterministic in this context does not mean that the encoding involves any randomness.


6


We also define non-deterministic encodings _E_ [(0)] and _E_ [(1)] for G as


_E_ [(0)] ( _P_ ) = _E_ 0( _P_ + _t_ ) _, E_ [(1)] ( _P_ ) = _E_ 0(8 _P_ + _t_ _[′]_ ) _, P ∈_ G _,_


where _t, t_ _[′]_ can be any 8-torsion point. Note that each element in G has exactly 8 representations under _E_ [(0)]

and _E_ [(1)] .


**Point Compression/Decompression.** It is efficient to convert from _EX_ ( _P_ ) to _E_ 0( _P_ ) and back; since
_E_ 0 represents points as much shorter bitstrings, these operations are called _point compression_ and _point_
_decompression_, respectively. Roughly speaking, point compression outputs _y_ = _Y/Z_ along with the sign bit
of _x_ = _X/Z_, and point decompression first recovers _x_ and then outputs _X_ = _x, Y_ = _y, Z_ = 1 _, T_ = _xy_ . We
always check for group membership during point decompression.
We use _E_ 0 for data transmission: the parties send bitstrings in _E_ 0(G [¯] ) and expect to receive bitstrings in
_E_ 0(G [¯] ). This means a computed point encoded by _EX_ has to be compressed before it is sent, and a received
bitstring has to be decompressed for subsequent group operations. Sending compressed points helps to reduce
the communication complexity: the parties only need to transfer 32 + 32 _m_ bytes in total.


**Secure Data Transmission.** At the beginning of the protocol _S_ computes and sends _E_ 0( _S_ ). In the ideal
case, _R_ should receive a bitstring in _E_ 0(G) which he interprets as _E_ 0( _S_ ). However, an attacker (a corrupted
_S_ _[∗]_ or a man-in-the-middle) can send _R_ 1) a bitstring that is not in _E_ 0(G [¯] ) or 2) a bitstring in _E_ 0(G [¯] _\_ G). In
the first case, _R_ detects that the received bitstring is not valid during point decompression and ignores it.
In the second case, _R_ can check group membership by computing the _p_ th multiple of the point, but a more
efficient way is to use a new encoding _E_ _[′]_ such that each bitstrings in _E_ 0(G [¯] ) represents a point in G under _E_ _[′]_ .
Therefore _R_ considers the received bitstring as _E_ [(0)] ( _S_ ) = _E_ 0( _S_ + _t_ ), where _t_ can be any 8-torsion point.
The encoding _E_ [(0)] (along with point decompression) makes sure that _R_ receives bitstrings representing
elements in G. However, an attacker can derive _c_ _[i]_ by exploiting the extra information given by a nonzero _t_ :
a naive _R_ would compute and send _E_ 0( _c_ _[i]_ ( _S_ + _t_ ) + _x_ _[i]_ _B_ ) = _E_ 0( _c_ _[i]_ _t_ + _R_ _[i]_ ); now by testing whether the result is
_E_ 0(G) the attacker learns whether _c_ _[i]_ = 0.
To get rid of the 8-torsion point, _R_ can multiply received point by 8 _·_ (8 _[−]_ [1] mod _p_ ), but a more efficient
way is to just multiply by 8 and then operate on _EX_ (8 _S_ ) and _EX_ (8 _x_ _[i]_ _B_ ) to obtain and send _E_ 1( _R_ _[i]_ ) = _E_ 0(8 _R_ _[i]_ ),
i.e, the encoding switches to _E_ 1 for _R_ _[i]_ . After this _S_ works similarly as _R_ : to ensure that the received bitstring
represents an element in G, _S_ interprets the bitstring as _E_ [(1)] ( _R_ _[i]_ ) = _E_ 0(8 _R_ _[i]_ + _t_ ); to get rid of the 8-torsion
point _S_ also multiplies the received point by 8, and then _S_ operates on _EX_ (64 _R_ _[i]_ ) and _EX_ (64 _T_ ) to obtain
_EX_ (64( _yR_ _[i]_ _−_ _jT_ )).


**Key Derivation.** The protocol computes _HS,Ri_ ( _P_ ) where _P_ can be _x_ _[i]_ _S, yR_ _[i]_ _,_ or _yR_ _[i]_ _−_ _jT_ for _j ∈_ [ _n_ ]. This is
implemented by hashing _E_ 1( _S_ ) _∥E_ 2( _R_ _[i]_ ) _∥E_ 2( _P_ ) with Keccak [BDPVA09] with 256-bit output. The choice of
encodings is natural: _S_ computes _EX_ ( _S_ ), and _R_ computes _EX_ (8 _S_ ); since multiplication by 8 is much cheaper
than multiplication by (8 _[−]_ [1] mod _p_ ), we use _E_ 1( _S_ ) = _E_ 0(8 _S_ ) for hashing. For similar reasons we use _E_ 2 for _R_ _[i]_

and _P_ .


**Actual Operations.** For completeness, we present in Table 1 a full overview of operations performed during
the protocol for the case of 1 out of 2 OT (i.e., _n_ = 2).


**4** **Field Arithmetic**


This section describes our implementation strategy for arithmetic operations in F2255 _−_ 19, which serve as
low-level building blocks for operations on the curve. Field operations are decomposed into double-precision
floating-point operations using our strategy. A straightforward way for implementation is then using doubleprecision floating-point instructions. However, a better way to utilize the 64 _×_ 64 _→_ 128-bit serial multiplier
is to decompose field operations into integer instructions as [BDL [+] 11] does. The real reason we decide to
use floating-point operations is that it allows us to use 256-bit vector instructions on the target microarchitectures, which are functionally equivalent to 4 double-precision floating-point instructions. The technique,


7


|S|Col2|Col3|
|---|---|---|
|Output|Input|Operations|
|_S_<br>_E_(0)(_S_)<br>8_S_<br>_E_1(_S_)<br>64_T_|_y_<br>_S_<br>_S_<br>8_S_<br>8_y,_ 8_S_|_y · B_<br>_C_(_S_)<br>8_ · S_<br>_C_(8_S_)<br>8_ ·_ (_y ·_ 8_S_)|
|64_R_~~_i_~~<br>_E_2(_Ri_)<br>64_yRi_<br>_E_2(_yRi_)<br>64(_yRi −T_)<br>_E_2(_yRi −T_)|_E_(1)(_Ri_)<br>64_Ri_<br>_y,_ 64_Ri_<br>64_yRi_<br>64_T,_ 64_yRi_<br>64(_yRi −T_)|8_ · D_(_E_(1)(_Ri_)<br>_C_(64_Ri_)<br>_y ·_ 64_Ri_<br>_C_(64_yRi_)<br>64_yRi −_64_T_<br>_C_(64(_yRi −T_))|


|R|Col2|Col3|
|---|---|---|
|Output|Input|Operations|
|8_S_<br>_E_1(_S_)|_E_(0)(_S_)<br>8_S_|8_ · D_(_E_(0)(_S_))<br>_C_(8_S_)<br>|
|8_x_~~_i_~~_B_<br>8_xiB_ + 8_S_<br>_E_(1)(_Ri_)<br>_E_2(_Ri_)<br>64_xiS_<br>_E_2(_xiS_)|8_x_~~_i_~~<br>8_S,_ 8_xiB_<br>8_Ri_<br>8_Ri_<br>8_xi,_ 8_S_<br>64_xiS_|8_x_~~_i _~~_· B_<br>8_xiB_ + 8_S_<br>_C_(8_Ri_)<br>_C_(8_ ·_ 8_Ri_)<br>8_xi ·_ 8_S_<br>_C_(64_xiS_)|



**Table 1.** How the parties compute encodings of group elements: each row shows that the “Output” is computed
given “Input” using the operations “Operations”. The input might come from the output of a previous row, a received
string (e.g., _E_ [(1)] ( _R_ _[i]_ )), or a random scalar that the party generates (e.g., 8 _x_ _[i]_ ). The upper half of the table are the
operations that does not depend on _i_, which means the operations are performed only once for the whole protocol.
_EX_ is suppressed: group elements written without encoding are actually encoded by _EX_ . _C_ and _D_ stand for point
compression and point decompression respectively. Computation of the _r_ th multiple of _P_ is denoted as “ _r · P_ ”. In
particular, 8 _· P_ can be carried out with only 3 point doublings.


which is called _vectorization_, makes our vectorized implementation achieve much higher throughtput than
our non-vectorized implementation based on [BDL [+] 11].


**Representation of Field Elements.** Each field element _x ∈_ F2255 _−_ 19 is represented as 12 _limbs_ ( _x_ 0 _, x_ 1 _, . . ., x_ 11)
such that _x_ = [�] _xi_ and _xi/_ 2 _[⌈]_ [21] _[.]_ [25] _[i][⌉]_ _∈_ Z. Each _xi_ is stored as a double-precision floating-point number. Field
operations are then carried out by limb operations such as floating-point additions and multiplications.


When a field element gets initialized (e.g., when obtained from a table lookup), each _xi_ uses no more
than 21 bits of the 53-bit mantissa. However, after a series of limb operations, the number of bits _xi_ takes
can grow. It is thus necessary to reduce the number of bits (in the mantissa) with carries before any precision
is lost; see below for more discussions.


**Field Arithmetic.** Additions and subtractions of field elements are implemented in a straightforward way:
simply adding/subtracting the corresponding limbs. This does increase the number of bits in the mantissa,
but in our application it suffices to reduce bits only at the end of the multiplication function.


A field multiplication is divided into two steps. The first step is a schoolbook multiplication on the 2 _·_ 12
input limbs, with reduction modulo 2 [255] _−_ 19 to bring the result back to 12 limbs. The schoolbook multiplication takes 132 floating-point additions, 144 floating-point multiplications, and a few more multiplications
by constants to handle the reduction.


Let ( _c_ 0 _, c_ 1 _, . . ., c_ 11) be the result after schoolbook multiplication. The second step is to perform carries to
reduce number of bits in _ci_ . Carry from _ci_ to _ci_ +1 (indices work modulo 12), which we denote as _ci →_ _ci_ +1,
is performed with 4 floating-point operations: _c ←_ _ci_ + _αi_ ; _c ←_ _c −_ _αi_ ; _ci ←_ _ci −_ _c_ ; _ci_ +1 _←_ _ci_ +1 + _c._ The idea
is to use _αi_ = 3 _·_ 2 _[k][i]_ where _ki_ is big enough so that the less significant part of _ci_ are discarded in _ci_ + _αi_,
forcing _c_ to contain only the more significant part of _ci_ . For _i_ = 11, one extra multiplication is required to
scale _c_ by 19 _·_ 2 _[−]_ [255] before it is added to _c_ 0.


A straightforward way to reduce number of bits in all limbs is to use the carry chain _c_ 0 _→_ _c_ 1 _→_ _c_ 2 _→· · · →_
_c_ 11 _→_ _c_ 0 _→_ _c_ 1 _._ The problem with the straightforward carry chain is that there is not enough instruction
level parallelism to hide the 3-cycle latencies (see discussion below). To hide the latencies we thus interleave


8


|instruction|latency|throughput|description|
|---|---|---|---|
|`vandpd`<br>`vorpd`<br>`vxorpd`<br>`vaddpd`<br>`vsubpd`<br>`vmulpd`|1<br>1<br>1<br>3<br>3<br>5|1<br>1<br>1 (4)<br>1<br>1<br>1|bitwise and<br>bitwise or<br>bitwise xor<br>4-way parallel double-precision ﬂoating-point additions<br>4-way parallel double-precision ﬂoating-point subtractions<br>4-way parallel double-precision ﬂoating-point multiplications|


**Table 2.** 256-bit vector instructions used in our implementation. Note that `vxorpd` has throughput of 4 when it has
only one source operand.


the following 3 carry chains:


_c_ 0 _→_ _c_ 1 _→_ _c_ 2 _→_ _c_ 3 _→_ _c_ 4 _→_ _c_ 5 _,_

_c_ 4 _→_ _c_ 5 _→_ _c_ 6 _→_ _c_ 7 _→_ _c_ 8 _→_ _c_ 9 _,_

_c_ 8 _→_ _c_ 9 _→_ _c_ 10 _→_ _c_ 11 _→_ _c_ 0 _→_ _c_ 1 _._


In total the multiplication function takes 192 floating-point additions/subtractions and 156 floating-point
multiplications.
When the input operands are the same, many limb products will repeat in the schoolbook multiplication;
a field squaring is therefore cheaper than a field multiplication. In total the squaring function takes 126
floating-point additions/subtractions and 101 floating-point multiplications.
Field inversion is implemented as a fix sequence of field squarings and multiplications.


**Vectorization.** We decompose field operations into 64-bit floating-point and logical operations. The Intel
Sandy Bridge and Ivy Bridge microarchitectures, as well as many recent microarchitectures, offer instructions
that operate on 256-bit registers. Some of these instructions treat the registers as vectors of 4 double-precision
floating-point numbers and perform 4 floating-point operations in parallel; there are also 256-bit logical
instructions that can be viewed as 4 64-bit logical instructions. We thus use these instructions to run 4 scalar
multiplications in parallel. Table 2 shows the instructions we use, along with their latencies and throughputs
on the Sandy Bridge and Ivy Bridge given in Fog’s well-known survey [Fog14].


**5** **Implementation Results**


This section compares the speed of our implementation of �21�-OT (i.e., _n_ = 2) with other similar implementations. We stress that our software is a constant-time one: timing attacks are avoided using the same
high-level strategy as [BDL [+] 11].
To show that our speeds for curve operations are competitive, we modify the software to support the
function of Diffie-Hellman key exchange and compare the results with existing Curve25519 implementations
(our implementation performs scalar multiplications on the twisted Edwards curve, so it is not the same as
Curve25519). The experiments are carried out on two machines on the eBACS site for publicly verifiable
benchmarks [BL15]: `h6sandy` (Sandy Bridge) and `h9ivy` (Ivy Bridge). Since our protocol can serve as the
base OTs for an OT extension protocol, we also compare our speed with a base OT implementation presented
in [ALSZ13], which is included in the Scapi multi-party computation library; the experiments are made on
an Intel Core i7-3537U processor (Ivy Bridge) where each party runs on one core. Note that all experiments
are performed with Turbo Boost disabled.


**Comparing with Curve25519 Implementations.** Table 3 compares our work with existing Curve25519
implementations. “Cycles to generate a public key” indicates the time to generate the public key given
a secret key; the Curve25519 implementation is the implementation by Andrew Moon [MF15]. “Cycles to
compute a shared secret” indicates the time to generate the shared secret, given a secret key and a public key;
the Curve25519 implementation is from [BDL [+] 11]. Note that since our software runs 4 scalar multiplications


9


|Col1|Col2|h6sandy h9ivy|
|---|---|---|
|[MF15]<br>[BDL+11]|Average cycles to compute a public key<br> Average cycles to compute a shared secret|61828<br>57612<br>194036 182708|
|this work|Average cycles to generate a public key<br>Average cycles to compute a shared secret|61458<br>60853<br>182169 180343|


**Table 3.** DH speeds of our work and existing Curve25519 implementations.

|Col1|m|4 8 16 32 64 128 256 512 1024|
|---|---|---|
|this work|Running time of_ S_<br>Running time of_ R_|548<br>381<br>321<br>279<br>265<br>257<br>246<br>237<br>228<br>472<br>366<br>279<br>229<br>205<br>200<br>193<br>184<br>177|
|[ALSZ13]|Running time of_ S_<br>Running time of_ R_|17976 10235 6132 4358 3348 2877 2650 2528 2473<br> 16968<br>9261 5188 3415 3382 2909 2656 2541 2462|



**Table 4.** Timings for per OT in kilocycles. Multiplying the number of kilocycles by 0 _._ 5 one can obtain the running
time (in _µs_ ) on our test architecture.


in parallel, the numbers in the table are the time for generating 4 public keys or 4 shared secrets divided by
4. In other words, our implementation is optimized for _througput_ instead of _latency_ .


**Comparing with Scapi.** Table 4 shows the timings of our implementation for the random OT protocol,
along with the timings of a base-OT implementation presented in [ALSZ13]. The paper presents several
base-OT implementations; the one we compare with is Miracl-based with “long-term security” using random
oracle (cf. [ALSZ13, Section 6.1]). The implementation uses the NIST K-283 curve and SHA-1 for hashing,
and it is not a constant-time implementation. It turns out that our work is an order of magnitude faster for
_m ∈{_ 4 _,_ 8 _, . . .,_ 1024 _}_ .


**Memory consumption.** Our code for public-key generation uses a 284-KB table. For shared-secret computation the table size is 12 KB. For OTs, _S_ uses a 12-KB table, while _R_ is _allowed_ to use a table of size up
to 1344 KB which depends on the parameters given. The current code provides 4 copies of the precomputed
points, one for each of the 4 scalar multiplcations, so it is possible to reduce the table sizes by a factor
of 4 by broadcasting the precomputed points. Another reason that we have large tables is because of the
representation for field elements: each limbs takes 8 bytes, so each field element already takes 12 _·_ 8 = 96
bytes. The window sizes we use are the same as [BDL [+] 11]. See [BDL [+] 11] for issues related to table sizes.


**Acknowledgments.** We are very grateful to: Daniel J. Bernstein and Tanja Lange for invaluable comments
and suggestions regarding elliptic curve cryptography and for editorial feedback on earlier versions of this
paper; Yehuda Lindell for useful comments on our proof of security; Peter Schwabe for various helps on implementation, including providing low-level code for field arithmetic; the anonymous LATINCRYPT reviewer
and in particular Gregory Neven.
Tung Chou is supported by Netherlands Organisation for Scientific Research (NWO) under grant 639.073.005.
Claudio Orlandi is supported by: the Danish National Research Foundation and The National Science Foundation of China (grant 61361136003) for the Sino-Danish Center for the Theory of Interactive Computation;
the Center for Research in Foundations of Electronic Markets (CFEM); the European Union Seventh Framework Programme ([FP7/2007-2013]) under grant agreement number ICT-609611 (PRACTICE).


10


**References**


ALSZ13. Gilad Asharov, Yehuda Lindell, Thomas Schneider, and Michael Zohner. More efficient oblivious transfer
and extensions for faster secure computation. In _Proceedings of the 2013 ACM SIGSAC conference on_
_Computer communications security_, pages 535–548. ACM, 2013.
ALSZ15. Gilad Asharov, Yehuda Lindell, Thomas Schneider, and Michael Zohner. More efficient oblivious transfer
extensions with security for malicious adversaries. Cryptology ePrint Archive, Report 2015/061, 2015.
`[http://eprint.iacr.org/](http://eprint.iacr.org/)` .
BBJ [+] 08. Daniel J Bernstein, Peter Birkner, Marc Joye, Tanja Lange, and Christiane Peters. Twisted edwards
curves. In _Progress in Cryptology–AFRICACRYPT 2008_, pages 389–405. Springer, 2008.
BCP04. Emmanuel Bresson, Olivier Chevassut, and David Pointcheval. New security results on encrypted key
exchange. In _Public Key Cryptography - PKC 2004, 7th International Workshop on Theory and Practice_
_in Public Key Cryptography, Singapore, March 1-4, 2004_, pages 145–158, 2004.
BDD [+] 17. Paulo S. L. M. Barreto, Bernardo David, Rafael Dowsley, Kirill Morozov, and Anderson C. A. Nascimento.
A framework for efficient adaptively secure composable oblivious transfer in the rom. Cryptology ePrint
Archive, Report 2017/993, 2017. `[https://eprint.iacr.org/2017/993](https://eprint.iacr.org/2017/993)`, Version 21 December 2017.
BDL [+] 11. Daniel J. Bernstein, Niels Duif, Tanja Lange, Peter Schwabe, and Bo-Yin Yang. High-speed high-security
signatures. In _Cryptographic Hardware and Embedded Systems – CHES 2011_, volume 6917 of _Lecture_
_Notes in Computer Science_, pages 124–142. Springer-Verlag Berlin Heidelberg, 2011.
BDPVA09. Guido Bertoni, Joan Daemen, Micha¨el Peeters, and Gilles Van Assche. Keccak sponge function family
main document. _Submission to NIST (Round 2)_, 3:30, 2009.
Bea96. Donald Beaver. Correlated pseudorandomness and the complexity of private computations. In _Proceedings_
_of the Twenty-Eighth Annual ACM Symposium on the Theory of Computing, Philadelphia, Pennsylvania,_
_USA, May 22-24, 1996_, pages 479–488, 1996.
Ber06. Daniel J Bernstein. Curve25519: new Diffie-Hellman speed records. In _Public Key Cryptography-PKC_
_2006_, pages 207–228. Springer, 2006.
BL14. Daniel J. Bernstein and Tanja Lange. Safecurves: choosing safe curves for elliptic-curve cryptography,
accessed 1 December 2014. `[http://safecurves.cr.yp.to](http://safecurves.cr.yp.to)` .
BL15. Daniel J Bernstein and Tanja Lange. eBACS: Ecrypt benchmarking of cryptographic systems, accessed
16 March 2015. `[http://bench.cr.yp.to](http://bench. cr. yp. to)` .
BLN [+] 15. Sai Sheshank Burra, Enrique Larraia, Jesper Buus Nielsen, Peter Sebastian Nordholt, Claudio Orlandi,
Emmanuela Orsini, Peter Scholl, and Nigel P. Smart. High performance multi-party computation for
binary circuits based on oblivious transfer. Cryptology ePrint Archive, Report 2015/472, 2015. `[http:](http://eprint.iacr.org/)`
`[//eprint.iacr.org/](http://eprint.iacr.org/)` .
BM89. Mihir Bellare and Silvio Micali. Non-interactive oblivious transfer and spplications. In _Advances in_
_Cryptology - CRYPTO ’89, 9th Annual International Cryptology Conference, Santa Barbara, California,_
_USA, August 20-24, 1989, Proceedings_, pages 547–557, 1989.
BPRS17. Megha Byali, Arpita Patra, Divya Ravi, and Pratik Sarkar. Fast and universally-composable oblivious
transfer and commitment scheme with adaptive security. Cryptology ePrint Archive, Report 2017/1165,
2017. `[https://eprint.iacr.org/2017/1165](https://eprint.iacr.org/2017/1165)`, Version 21 Mar 2018.
Can01. Ran Canetti. Universally composable security: A new paradigm for cryptographic protocols. In _42nd_
_Annual Symposium on Foundations of Computer Science, FOCS 2001, 14-17 October 2001, Las Vegas,_
_Nevada, USA_, pages 136–145, 2001.
CF01. Ran Canetti and Marc Fischlin. Universally composable commitments. _IACR Cryptology ePrint Archive_,
2001:55, 2001.
CJS14. Ran Canetti, Abhishek Jain, and Alessandra Scafuro. Practical UC security with a global random
oracle. In _Proceedings of the 2014 ACM SIGSAC Conference on Computer and Communications Security,_
_Scottsdale, AZ, USA, November 3-7, 2014_, pages 597–608, 2014.
CO15. Tung Chou and Claudio Orlandi. The simplest protocol for oblivious transfer. In _Progress in Cryptology_

_- LATINCRYPT 2015 - 4th International Conference on Cryptology and Information Security in Latin_
_America, Guadalajara, Mexico, August 23-26, 2015, Proceedings_, pages 40–58, 2015.
DKLs18. Jack Doerner, Yashvanth Kondi, Eysa Lee, and shelat abhi. Secure two-party threshold ecdsa from ecdsa
assumptions. IEEE Security and Privacy Symposium, Cryptology ePrint Archive, Report 2018/499, 2018.
`[https://eprint.iacr.org/2018/499](https://eprint.iacr.org/2018/499)`, Version 23 May 2018.
DNO08. Ivan Damg˚ard, Jesper Buus Nielsen, and Claudio Orlandi. Essentially optimal universally composable
oblivious transfer. In _Information Security and Cryptology - ICISC 2008, 11th International Conference,_
_Seoul, Korea, December 3-5, 2008, Revised Selected Papers_, pages 318–335, 2008.


11


EGL85. Shimon Even, Oded Goldreich, and Abraham Lempel. A randomized protocol for signing contracts.
_Commun. ACM_, 28(6):637–647, 1985.
Fog14. Agner Fog. Instruction tables. 2014. `[http://www.agner.org/optimize/instruction_tables.pdf](http://www.agner.org/optimize/instruction_tables.pdf)` .
GIR17. Ziya Alper Gen¸c, Vincenzo Iovino, and Alfredo Rial. ”the simplest protocol for oblivious transfer”
revisited. Cryptology ePrint Archive, Report 2017/370, 2017. `[https://eprint.iacr.org/2017/370](https://eprint.iacr.org/2017/370)`,
Version 24 May 2017.
HL10. Carmit Hazay and Yehuda Lindell. _Efficient Secure Two-Party Protocols - Techniques and Constructions_ .
Information Security and Cryptography. Springer, 2010.
HL17. Eduard Hauck and Julian Loss. Efficient and universally composable protocols for oblivious transfer from
the cdh assumption. Cryptology ePrint Archive, Report 2017/1011, 2017. `[https://eprint.iacr.org/](https://eprint.iacr.org/2017/1011)`
`[2017/1011](https://eprint.iacr.org/2017/1011)`, Version 24 October 2017.
HWCD08. Huseyin Hisil, Kenneth Koon-Ho Wong, Gary Carter, and Ed Dawson. Twisted Edwards curves revisited.
In _Advances in Cryptology-ASIACRYPT 2008_, pages 326–343. Springer, 2008.
IKNP03. Yuval Ishai, Joe Kilian, Kobbi Nissim, and Erez Petrank. Extending oblivious transfers efficiently. In _Ad-_
_vances in Cryptology - CRYPTO 2003, 23rd Annual International Cryptology Conference, Santa Barbara,_
_California, USA, August 17-21, 2003, Proceedings_, pages 145–161, 2003.
IR89. Russell Impagliazzo and Steven Rudich. Limits on the provable consequences of one-way permutations.
In _Proceedings of the 21st Annual ACM Symposium on Theory of Computing, May 14-17, 1989, Seattle,_
_Washigton, USA_, pages 44–61, 1989.
Kil88. Joe Kilian. Founding cryptography on oblivious transfer. In _Proceedings of the 20th Annual ACM_
_Symposium on Theory of Computing, May 2-4, 1988, Chicago, Illinois, USA_, pages 20–31, 1988.
KOS15. Marcel Keller, Emmanuela Orsini, and Peter Scholl. Actively secure ot extension with optimal overhead.
CRYPTO, 2015.
Lar14. Enrique Larraia. Extending oblivious transfer efficiently, or - how to get active security with constant
cryptographic overhead. _IACR Cryptology ePrint Archive_, 2014:692, 2014.
LM18. Baiyu Li and Daniele Micciancio. Equational security proofs of oblivious transfer protocols. In _Public-Key_
_Cryptography - PKC 2018 - 21st IACR International Conference on Practice and Theory of Public-Key_
_Cryptography, Rio de Janeiro, Brazil, March 25-29, 2018, Proceedings, Part I_, pages 527–553, 2018.
MF15. Andrew Moon “Floodyberry”. Implementations of a fast elliptic-curve digital signature algorithm, accessed 16 March 2015. `[https://github.com/floodyberry/ed25519-donna](https://github.com/floodyberry/ed25519-donna)` .
Nie07. Jesper Buus Nielsen. Extending oblivious transfers efficiently - how to get robustness almost for free.
Cryptology ePrint Archive, Report 2007/215, 2007. `[http://eprint.iacr.org/](http://eprint.iacr.org/)` .
NNOB12. Jesper Buus Nielsen, Peter Sebastian Nordholt, Claudio Orlandi, and Sai Sheshank Burra. A new approach to practical active-secure two-party computation. In _Advances in Cryptology - CRYPTO 2012 -_
_32nd Annual Cryptology Conference, Santa Barbara, CA, USA, August 19-23, 2012. Proceedings_, pages
681–700, 2012.
NP01. Moni Naor and Benny Pinkas. Efficient oblivious transfer protocols. In _Proceedings of the Twelfth Annual_
_Symposium on Discrete Algorithms, January 7-9, 2001, Washington, DC, USA._, pages 448–457, 2001.
PVW08. Chris Peikert, Vinod Vaikuntanathan, and Brent Waters. A framework for efficient and composable
oblivious transfer. In _Advances in Cryptology - CRYPTO 2008, 28th Annual International Cryptology_
_Conference, Santa Barbara, CA, USA, August 17-21, 2008. Proceedings_, pages 554–571, 2008.
Rab81. Michael O. Rabin. How to exchange secrets with oblivious transfer. _Technical Report TR-81, Aiken_
_Computation Lab, Harvard University_, 1981.
Sch15. Thomas Schneider. Personal communication, 2015.
Wie83. Stephen Wiesner. Conjugate coding. _SIGACT News_, 15(1):78–88, January 1983.


12


