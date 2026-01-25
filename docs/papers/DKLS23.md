# Threshold ECDSA in Three Rounds (DKLS23)

**Authors:** Jack Doerner, Yashvanth Kondi, Eysa Lee, abhi shelat

**Published:** IEEE Symposium on Security and Privacy (S&P) 2023

**ePrint:** https://eprint.iacr.org/2023/765

---

# Threshold ECDSA in Three Rounds [∗]



Jack Doerner

j@ckdoerner.net

Technion, Reichman U, Brown U



Yashvanth Kondi

yash@ykondi.net

Silence Labs (Deel)



Eysa Lee

eysa_lee@brown.edu

Brown University



abhi shelat

abhi@neu.edu

Northeastern University



December 14, 2023


**Abstract**


We present a three-round protocol for threshold ECDSA signing
with malicious security against a dishonest majority, which informationtheoretically UC-realizes a standard threshold signing functionality, assuming only ideal commitment and two-party multiplication primitives.
Our protocol combines an intermediate representation of ECDSA signatures that was recently introduced by Abram et al. [ANO [+] 22] with an
efficient statistical consistency check reminiscent of the ones used by the
protocols of Doerner et al. [DKLs18, DKLs19]. We show that shared
keys for our signing protocol can be generated using a simple commitrelease-and-complain procedure, without any proofs of knowledge, and to
compute the intermediate representation of each signature, we propose a
two-round vectorized multiplication protocol based on oblivious transfer
that outperforms all similar constructions.


∗A preliminary version [DKLs24] of this work appeared in _IEEE S&P 2024_ .


## **Contents**

**1** **Introduction** **1**
1.1 A Brief History of Threshold ECDSA . . . . . . . . . . . . . . . 3
1.2 Our Approach and Contributions . . . . . . . . . . . . . . . . . . 7


**2** **Preliminaries** **11**
2.1 Notation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.2 Security and Communication Model . . . . . . . . . . . . . . . . 11
2.3 The ECDSA Signature Scheme . . . . . . . . . . . . . . . . . . . 11


**3** _t_ **-Party Three-Round Threshold ECDSA** **12**
3.1 Building Blocks . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
3.2 The Basic Three-Round Protocol . . . . . . . . . . . . . . . . . . 16
3.3 Pipelining and Presigning . . . . . . . . . . . . . . . . . . . . . . 20
3.4 Comparison to DKLs19 . . . . . . . . . . . . . . . . . . . . . . . 22
3.5 Two-Party Two-Message ECDSA . . . . . . . . . . . . . . . . . . 23


**4** **Proof of Security for** _t_ **-Party ECDSA** **25**


**5** **Random Vector OLE from Random OT** **37**
5.1 One-Message SoftSpokenOT in the ROM . . . . . . . . . . . . . 41


**6** **Proof of Security for OT-Based VOLE** **42**
6.1 Simulating Against Alice . . . . . . . . . . . . . . . . . . . . . . . 42
6.2 Simulating Against Bob . . . . . . . . . . . . . . . . . . . . . . . 53


**7** **Relaxed Threshold Key Generation** **56**
7.1 The Protocol . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 58
7.2 Proof of Security . . . . . . . . . . . . . . . . . . . . . . . . . . . 60


**8** **Analytical Efficiency** **63**
8.1 Oblivious Transfer . . . . . . . . . . . . . . . . . . . . . . . . . . 63
8.2 Our VOLE . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 64
8.3 VOLE from HMRT22 . . . . . . . . . . . . . . . . . . . . . . . . 65
8.4 Our Key Generation and ECDSA Protocols . . . . . . . . . . . . 65
8.5 Concrete Results . . . . . . . . . . . . . . . . . . . . . . . . . . . 66


**9** **A Two-Round Protocol for Honest Majorities** **67**


## **1 Introduction**

The Elliptic Curve Digital Signature Algorithm (ECDSA) is among the most
common and widely deployed cryptographic tools of any kind. Since its
standardization by the US National Institute of Standards and Technology
(NIST) [Nat13], it has become a ubiquitous component of the internet infrastructure. This makes it a natural and essential target for threshold cryptography; that is, for signing mechanisms that _distribute_ authority among a quorum
of parties larger than some threshold. Indeed, NIST has recently announced
an intent to standardize threshold ECDSA schemes [BP23], much as it did the
original signature,which motivates the design of schemes that are concretely efficient, yet secure under conservative assumptions and simple to analyze and
implement.
In a _t_ -of- _n_ ECDSA scheme, any _t_ parties can jointly sign a message under
the common public key, but no group of _t −_ 1 corrupt parties can sign an
unauthorized message, even by sending malformed protocol messages to honest
parties. Such schemes are already in use to facilitate defense-in-depth security
for digital assets linked to ECDSA public keys [Lin21].
Threshold signing schemes are straightforward to construct for some elliptic
curve signatures, such as BLS [BLS01] and Schnorr [Sch89], but ECDSA features
a non-linear signing equation that is challenging to compute in a distributed
fashion. ECDSA uses a basic discrete-logarithm key pair comprising a uniform
sk _←_ Z _q_ and a public pk = sk _· G_, where _G_ = (G _, G, q_ ) is the description of an
elliptic curve G of order _q_ that is genrated by _G_ . A signature on a message _m_
consists of a public nonce _R_ = _r · G_ and a value of the form _s_ = ( _a_ + sk _· b_ ) _/r_,
where _a_ = SHA2( _m_ ) and _b_ = _r_ [x] are effectively public coefficients, _r_ [x] is the xcoordinate of the curve point _R_, and _r_ is a uniform secret per-signature _instance_
_key_ . The computation of _s_ forms the core challenge of distributing the signing
process efficiently.
Most approaches to computing _s_ can be analyzed by _rewriting_ the equation
that defines _s_ in terms of some specific set of operations. For example, the modular inverse operation can be rewritten in terms of multiplication and addition,
and then generic multiparty computation (MPC) protocols (which support multiplication and addition natively) can be used to compute the rewritten equation.
Concrete efficiency improvements can be achieved by refining the machinery of
the computation, but efficiency can ultimately be bottlenecked by the rewriting
of the signing equation, which may impose some minimal number or depth of
nonlinear operations that can be computed securely only at a significant cost in
terms of bandwidth, computation, or rounds of interaction.


**In this Work.** We identify a specific rewriting of the signing equation and
a method to compute it that together eliminate long standing bottlenecks
in round complexity without incurring additional costs elsewhere, and yield
arguably-minimal MPC protocols for both key generation and signing. Specifically, we begin from the venerable Bar-Ilan and Beaver [BB89] protocol for
computing inverses of secret-shared values using secure multiplication; two


1


fused instances of this protocol with a single denominator are used to compute the two terms that define _s_ . The intermediate secret sharing of the signature that results from this process is similar to the one used by several prior
works [LN18, ANO [+] 22, GS22a]. Unlike prior works, we make dual use of correlated random values already present in the Bar-Ilan and Beaver protocol as implicit Message Authentication Codes (MACs) to authenticate the various parts
of the computation via checks evaluated over the signing curve in a manner
reministent of the protocols of Doerner et al. [DKLs18, DKLs19]. This obviates
the auxilliary verification mechanisms used by prior works, and it eliminates
the need to extract discrete logarithms via proofs of knowledge. The resulting
protocol has no zero-knowledge proofs of any kind during key generation or
signing, and its cost is dominated by the cost of our fused double-instance of
Bar-Ilan and Beaver. Finally, we propose a refinement of the secure multiplication protocols of Doerner et al. [DKLs18, DKLs19] that meets our syntactical
requirements, while noticeably improving upon the efficiency of the original.
Our protocol improves upon the state of the art in three aspects:


- **Simplicity** . Our signing protocol is constructed using only idealized commitments and multiplication—specifically, _Vector Oblivious Linear Evaluation_,
or VOLE, with a vector length of two—and both are invoked only once in
each direction between every pair of parties when signing a message. In addition, every party must perform six elliptic curve scalar operations for each of
its counterparties, as part of a statistical check to detect malicious behaviour.
Similarly, our key generation protocol comprises a single commit-and-release
action, followed by one round in which the parties can trigger an abort if
they received an inconsistent share of the secret key. The latter condition is
detectable using only two elliptic curve scalar operations per counterparty.


- **Security** . Assuming ideal versions of (i.e. black-box access to) the commitment and VOLE primitives, our key generation and signing protocols
permit a straightforward information-theoretic security analysis in the Universal Composition (UC) framework with a conservative threshold signing
functionality that simply computes the signature internally and outputs it
when a quorum of parties agrees to sign. Our proposed VOLE instantiation is secure in the random oracle model assuming oblivious transfer (OT),
and so concrete instantiations of our protocol (i.e. instantiations wherein all
ideal primitives are realized) can be founded upon any single assumption that
implies OT, such as the Diffie-Hellman assumption over the signing curve.


- **Efficiency** . Assuming a two-round VOLE such as the one we propose, the
components of our signing protocol can be arranged into three rounds without breaking any abstractions or performing any heuristic optimizations.
This is one round fewer than the best-known protocols from specific assumptions [CGG [+] 20, CCL [+] 20], and two rounds fewer than the best-known
protocol from general assumptions (i.e. OT) [HLNR23]. It also brings the
round complexity of threshold ECDSA to par with threshold Schnorr [Lin22]


2


for the first time. [1] Under pipelining and in the honest-majority setting the
round complexity of our protocol can be further reduced to two with no
compromise to security, and in the two-party context under pipelining only
a single message in each direction is necessary. In terms of computation and
bandwidth, our protocol incurs minimal overhead relative to the underlying
VOLE, and we demonstrate via concrete benchmarks that it is the fastest
threshold ECDSA protocol to date in scenarios ranging from only a few parties in a single location, to hundreds of parties participating globally.


**1.1** **A Brief History of Threshold ECDSA**


In order to justify the choices we made in constructing our protocol and contextualize our claim of simplicity, we give a qualitative account of the various
approaches to threshold ECDSA that have developed over time. We focus on
techniques and protocol structure, rather than security models, assumptions, or
comparisons of efficiency. In each case, we describe a _rewriting_ of the ECDSA
signing equation into a specific sequence of secure operations, summarize the
protocol machinery used to compute the operations in the rewritten equation,
and discuss any authentication or proof mechanism necessary to bind the various
operations together and prevent malicious behavior.


**Honest Majority.** Shortly after the original Digital Signature Algorithm
(DSA) was standardized, Langford [Lan95] devised a _[√]_ ~~_n_~~ ~~-~~ of- _n_ protocol to distribute its computation, and shortly thereafter Gennaro et al. generalized it
to any _t_ -of- _n_ such that _t > n/_ 2 [GJKR96]. Though these works came before
ECDSA, they easily extend to it. Both works rewrote the signing equation such
that _s_ = ( _a_ + sk _· b_ ) _· r_ and _R_ = _r_ _[−]_ [1] _· G_, and performed their computations over
Shamir-sharings of the secrets sk and _r_ . When _n ≥_ 2 _t_ + 1, secure multiplication
of Shamir-shared secrets is is easy, and if the output need not be multiplied
again, then degree-reduction is unnecessary. Gennaro et al. were the first to
propose computing _r_ _[−]_ [1] via the Bar-Ilan Beaver technique [BB89]. In their protocol, uniform sharings of _r_ and _ϕ_ are sampled, their product _r · ϕ_ is publicly
revealed, as is _ϕ · G_, and then _R_ = ( _r · ϕ_ ) _[−]_ [1] _· ϕ · G_ = _r_ _[−]_ [1] _· G_ can be computed
publicly.
These first protocols were secure in the semi-honest honest majority setting,
but honest majorities also permit simple and clean techniques for achieving
malicious security. Gennaro et al. [GJKR96] and Cerecedo et al. [CMI93] used
_verifiable secret sharing_ (VSS) techniques to build _robust_ protocols when _n ≥_
3 _t_ + 1, and Damgård et al. [DJN [+] 20] constructed a simple protocol that is
secure with abort against malicious adversaries when _n ≥_ 2 _t_ +1. More recently,
Groth and Shoup [GS22a] developed the first distributed ECDSA protocol that
achieves guaranteed output delivery in the _asynchronous_ setting when _n ≥_ 3 _t_ +1,


1A number of two-round distributed Schnorr protocols such as MuSig2 [NRS21] and
FROST [BCK [+] 22] also exist, with game-based security under non-standard assumptions.


3


which is optimal. Our focus in this work is the dishonest-majority setting, and
so we dwell no further on the details of these protocols.


**Dishonest Majority.** MacKenzie and Reiter [MR01] constructed the first
two-party (and thus dishonest-majority) protocol for ECDSA signing. They expressed the ECDSA signing equation as _s_ = ( _a/r_ )+(sk _·_ _b/r_ ), and then specified
that the parties sample _multiplicative_ shares of sk and _r_, from which _R_ can be
computed using a Diffie-Hellman key exchange and multiplicative shares of the
terms _a/r_ and sk _· b/r_ can be computed non-interactively. The latter terms
must be summed without revealing either of them. MacKenzie and Reiter do
this via Paillier’s _additively homomorphic encryption_ (AHE) scheme [Pai99].
Fifteen years later, Gennaro et al. [GGN16] used _threshold_ AHE to extend
this idea to the many-party setting, and then Boneh et al. [BGG17] reduced
the round count to four. Both many-party extensions rely on two severely inefficient components: threshold AHE requires an auxiliary RSA modulus of
unknown factorization, which can only be sampled via an additional highlycomplex protocol [HMRT12, FLOP18, CCD [+] 20, CHI [+] 21], and using Paillier
encryption to operate over a prime-order field like the one in which the sharesto-be-combined lie requires expensive zero-knowledge range proofs to ensure
ciphertext well-formedness. Further proofs are required to verify the relationships of the encrypted values to the public ones. Lindell [Lin17] eliminated
these bottlenecks in the two-party setting by ensuring that one of the parties is
given a homomorphic encryption of the other party’s share of the signing key
during key generation: this allows the same party to compute an encryption of _s_
non-interactively, and the other party can simply check if the signature is valid
upon decryption. Lindell’s signing protocol requires a new ad-hoc assumption
on the Paillier cryptosystem in order to achieve simulation security, but it is
computationally limited only by the large-integer arithmetic required to work
with Paillier encryption. Unfortunately, it is unclear how to generalize Lindell’s
improvements to the multiparty setting.
Doerner et al. [DKLs18] used the same form of the signing equation as
MacKenzie and Reiter and the same multiplicative secret sharings. They combined the multiplicative shares using an ideal secure multiplication functionality, and then proposed an actively-secure variant of Gilboa’s OT-based multiplication protocol [Gil99] to realize this functionality. Because their multiplication protocol operates natively over any prime-order field, it avoids
large integer arithmetic and range proofs. Its compatibility with OT extension [IKNP03, KOS15, Roy22] techniques makes it computationally lightweight
relative to Lindell’s scheme, at the expense of somewhat higher bandwidth
consumption. In a subsequent work, Doerner et al. [DKLs19] extended their
scheme to the multiparty setting by introducing a log _t_ -round protocol to
convert a _t_ -party multiplicative sharing to an additive one. Both of these
works [DKLs18, DKLs19] verified the consistency of intermediate computations
against malicious behavior using a set of bespoke checks that relate secret shares
to public values in the curve group G, and show reductions to standard assump

4


tions on G if the checks are violated without detection. In the multi-party
follow-up these checks are carried out via the simple commit-and-release of
shares that will sum to a known public target value if and only if all parties
have behaved honestly. In the original two-party protocol the check shares are
instead used to encrypt the final protocol message, such that it can only be
decrypted correctly if both parties are honest; this trick among others allows
the original protocol to produce a signature in two messages. Our work bespoke
checks that are similar in spirit to those employed previously by Doerner et al.,
but ours are evaluated in a pairwise fashion, and they are statistical instead of
computational.
Gennaro and Goldfeder [GG18] returned to Langford’s forumulation of the
ECDSA signing equation and devised a Paillier-based mechanism to compute
it that differs from previous Paillier-based schemes [GGN16, BGG17] in that
it does not require the secure sampling of biprimes of unknown factorization.
Their protocol is eight rounds in total and achieves malicious security: the first
three rounds resemble the protocol of Gennaro et al. [GJKR96], except that
they use Paillier encryption to perform secure multiplication. After these three
rounds, the signature cannot be revealed immediately: instead a five-round
interactive protocol is used to perform a masked verification of the putative
signature, ensuring that the signature is well-formed (and thus no cheating has
occurred) before it is assembled.
Concurrently, Lindell and Nof [LN18] presented a different eight-round
Paillier-based threshold ECDSA protocol that similarly avoided secure biprime
sampling. Unlike Goldfeder and Gennaro’s protocol, Lindell and Nof used a
new rewriting of the ECDSA equation wherein _R_ = _r · G_ and _s_ = _w/u_, where
_w_ = ( _a_ + sk _·_ _b_ ) _·_ _ϕ_, and _u_ = _r_ _·_ _ϕ_ for some randomly sampled _ϕ_ . This was the first
appearance in the literature of the rewriting that we use in _this_ work, i.e. the
fused double-instance of Bar-Ilan an Beaver. Again like Gennaro and Goldfeder,
Lindell and Nof proposed to use a “private but unauthenticated” computation
mechanism for this rewriting, and then verify the well-formedness of the signature before revealing it. Their verification mechanism essentially repeats the
signing computation in encrypted form, using a combination of ElGamal encryption and relatively-efficient zero-knowledge proofs. Since their analysis is
in the UC model, these proofs must be compiled for straight-line extraction via
the Fischlin transform [Fis05], which induces an overhead of roughly one order
of magnitude in terms of computation and communication.
Somewhat later, Canetti et al. [CGG [+] 20] presented a four-round signing
protocol that essentially followed the same core protocol layout as Gennaro and
Goldfeder [GG18], but they replaced the interactive masked signature verification to validate honest behaviour with a conceptuatlly-straightforward GMWstyle [GMW87] mechanistm in which the parties prove honest execution of
each step in zero-knowledge. The advantage of this alteration is an improved
round count and the ability to identify cheating parties. The downside is the
increased computational cost due to performing zero-knoweledge proofs over
cryptographic statements. Parties must prove at every step that certain Paillier
ciphertexts encrypt the discrete logarithms of public values, the results of some


5


affine operations, or values in some restricted range.
Lindell and Nof, Gennaro and Goldfeder, and Canetti et al. all instantiated
their secure multiplication primitives using Paillier encryption, and thus they
rely upon expensive range proofs to guarantee correctness. In a recent update
to Lindell and Nof’s work, Haitner et al. [HLNR23] replaced the original secure
multiplication protocol with OT-based _weak_ multiplication (which guarantees
privacy but not correct outputs), and achieved a round count of five by making
optimizations at the expense of breaching abstraction boundaries.
Castagnos et al. [CCL [+] 23] started from the protocol of Canetti et al. and
replaced Paillier encryption with the Castagnos-Laguillaumie (CL) encryption
scheme [CL15] from class groups of imaginary quadratic order, which eliminated
the zero-knowledge range proofs required by Canetti et al. and yielded a significant bandwidth improvement, but did not reduce the computational burden of
the original protocol due the inherently higher cost of CL encryption, relative
to Paillier.


**Generic Approaches.** Smart and Talibi [ST19] and Dalskov et al. [DOK [+] 20]
concurrently proposed generic MPC approaches to ECDSA signing. Both
groups observed that the MAC checks of SPDZ-style [DPSZ12] protocols can be
evaluated in an elliptic curve group directly. SPDZ-style protocols are typically
black-box in a Beaver-triple generator, which is essentially an authenticated secure multiplication primitive, and since SPDZ-style protocols are generic, they
can compute _any_ rewriting of the ECDSA signing equation. The downside
of such generic approaches was evident in the benchmarks that Dalskov et al.
reported [DOK [+] 20]: the overhead due generating MACs amounts to several additional rounds of interaction relative to other approaches, and a factor of two
in terms of bandwidth and computation.
Abram et al. [ANO [+] 22] studied how to construct threshold ECDSA in the
Pseudorandom Correlation Generator (PCG) paradigm, using a variant of the
Ring-LPN assumption. This involves first defining a multiparty correlation that
can be derandomized into an ECDSA signature, and then constructing cryptographic machinery to derive many instances of the correlation non-interactively
after a one-time setup. The correlation they defined comprises ( _ϕ, r, u, v_ ) such
that _u_ = _ϕ · r_ and _v_ = _ϕ ·_ sk. They refer to it as an “ECDSA Tuple.” Assuming a linear secret sharing scheme, this correlation can be assembled with the
message into an ECDSA signature in one round by locally computing shares of
_w_ = _a · ϕ_ + _b · v_ and then publishing shares of both _w_ and _u_, and publicly computing _s_ = _w/u_ . This correlation essentially distills Lindell and Nof’s [LN18]
rewriting of the ECDSA equation into a clean, succinct format, suitable for
many different kinds of secure computation machinery. Abram et al. themselves
took a generic approach: they augmented the correlation with BeDOZa-style
MACs [BDOZ11], which can be checked in an elliptic curve group much as
SPDZ-style MACs can be, and used these MACs to authenticate the honest
generation and assembly of the correlation.


6


**1.2** **Our Approach and Contributions**


Just as we have done with prior works, we can break down our protocol into
a rewriting of the ECDSA equation, a mechanism for securely computing the
operations in the rewritten equation, and an approach to hardening the secure
computation against malicious adversaries.


**Rewriting ECDSA.** In this work, we propose a protocol that securely computes _R_ = _r·G_ and _w_ = ( _a_ +sk _·b_ ) _·ϕ_ and _u_ = _r·ϕ_, where _a_ = SHA2( _m_ ) is a public
coefficient, _b_ = _r_ [x] is the x-coordinate of _R_, and _r_ is a uniform secret. Once _R_,
_w_, and _u_ are known to the signing parties, they can information-theoretically
construct an ECDSA signature by locally calculating _s_ = _w/u_ . This is the
same formulation of the signing equation originally introduced by Lindell and
Nof [LN18] and later explicitly construed as a random correlation by Abram
et al. [ANO [+] 22]. Unlike Lindell and Nof, we leverage the fact that under this
formulation (as opposed to others), the three nonlinear relations defining _R_,
_w_, and _u_ can be securely computed in parallel. This is critical for achieving
a three-round protocol. Unlike Abram et al. [ANO [+] 22], we compute the correlation exactly as we have written it, rather than extending it with explicit
BeDOZa-style MACs.


**Computing the ECDSA Correlation Securely.** We propose a protocol
that leverages the structure of the correlation itself to achieve security against
malicious adversaries, rather than relying upon zero-knowledge proofs or explicit
MACs on computed values. Specifically, we propose to use a pairwise _consis-_
_tency check_ that depends only upon the inputs and outputs of the operations
in our rewritten signing equation. This frees us to model the operations of the
signing equation as ideal objects and to instantiate them modularly. Among
prior works, only Doerner et al. [DKLs18, DKLs19] use a similar approach, but
our consistency checks are pairwise and statistical, whereas theirs were global
and computational, and the simulation strategy used in their proof requires the
checks to be evaluated over the course of multiple rounds, whereas ours can be
performed simultaneously with the computation of the correlation.
As we have said, our protocol securely computes _R_ = _r · G_ and _w_ = ( _a_ +
sk _· b_ ) _· ϕ_ and _u_ = _r · ϕ_, where _a_ = SHA2( _m_ ) is a public coefficient, _b_ = _r_ [x] is the
x-coordinate of _R_, and _r_ is a uniform secret. The computation of secret shares
of _w_ can be performed locally by the parties given shares _ϕ_ and _v_ = sk _· ϕ_ .
Assuming that shares of the two products _v_ and _u_ are computed _ideally_ (i.e.
in each case it is guaranteed that nothing is leaked in the course of computing
the product, and that the outputs are really shares of the product of the shared
inputs), there are only a few avenues to cheat:


1. A corrupt party could bias the sampling of _r_ . This can be prevented by using a standard commit-and-release sampling mechanism: the parties sample
shares of _r_, commit to corresponding shares of _R_ (which collectively fix _r_ ),
and then decommit the latter shares. This requires two rounds. So long as _r_


7


is otherwise information-theoretically hidden until after the commitment is
complete, this precludes any bias on the part of the adversary.


2. A corrupt party could use inconsistent values of _ϕ_ in the computations that
produce _v_ and _u_ . This can be prevented by using a _vectorized_ multiplication
primitive to compute both values at once, given a single value of _ϕ_ . Specifically, we use _vector oblivious linear evaluation_ (VOLE), which is evaluated
pairwise. Given any ordinary two-party two-message OLE (i.e. multiplication) protocol in which the party who speaks first supplies a share of _ϕ_, the
party who speaks second can vectorize their input simply by reusing the first
message for multiple responses. This essentially fuses the two multiplications.


3. In the computations that produce _v_ and _u_, a corrupt party could use values
of sk and _r_ that are not actually the respective discrete logarithms of pk
and _R_ . To mitigate this form of attack, we devise an extremely simple
consistency check mechanism hinging on the observation that if the shares of
_ϕ_ are interpreted as MAC keys, then the parties are _already_ in possession of
BeDOZa-style MACs on each other’s shares of sk and _r_ . Furthermore, these
MACs can be checked in the elliptic curve group against the publicly known
values of pk and _R_, and if the party that supplies a share of _ϕ_ speaks first
in the multiplication protocol, and the protocol requires two messages, then
the check can be performed _simultaneously_ and without additional messages.

Let us be more specific: _ϕi_ is party _Pi_ ’s share of _ϕ_, _rj_ is _Pj_ ’s share of _r_, and
_Rj_ = _rj · G_ is known to both parties. The two parties use a two-message
multiplication protocol that privately outputs _c_ to _Pj_ and _d_ to _Pi_ such that
_c_ + _d_ = _rj · ϕi_ . If the multiplication protocol involves two messages and _Pi_
speaks first, then _Pj_ must learn _c_ after receiving the first message from _Pi_ .
To ensure consistency, we specify that _Pj_ transmits Γ = _c · G_ to _Pi_ along
with the second message of the multiplication protocol, and then _Pi_ checks
that Γ + _d · G_ = _ϕi · Rj_ . The same check can be performed with respect to
pk _j_ = sk _j · G_ .

This statistical check is cheap, overwhelmingly sound, and extremely simple
to simulate. Since Γ can be computed as a function of _Rj_ and the secrets of
_Pi_, simulating this value toward _Pi_ without knowledge of _rj_ is trivial. On the
other hand, fixing _Rj_, _ϕi_, and _d_ fixes exactly one value of Γ that will cause
the consistency check to pass. Since _ϕi_ and _d_ are uniform and informationtheoretically hidden from _Pj_, the correct value of Γ can be guessed with
probability at most 1 _/q_ if _rj · G ̸_ = _Rj_ . Finally, even if the check is passed—
that is, if _Rj_ and a the correct value of Γ are known to _Pj_ —the remaining
degree of freedom defining the relationship between _ϕi_ and _d_ ensures that _ϕi_
is information-theoretically hidden from _Pj_, and thus it remains safe to use
_ϕi_ in constructing the signature even though it is also used in this check.


4. A corrupt party could send an incorrect share of _v_ or _u_, after they are computed. Since fixing _m_, _R_, and pk fixes the corresponding ECDSA signature
exactly, a cheat of this kind can be detected perfectly by verifying the signature that is assembled.


8


We have discussed a two-round commit-and-release mechanism to compute
_R_ and a two-round fused multiplication protocol with a consistency check that
requires (shares of) _R_ to be known after the second round. These two operations
can be performed concurrently. Afterward, only one more round is needed to
assemble the signature from the correlation, and the final check is performed
locally. Thus our protocol requires three rounds, in total. Our final theorem
statement is:


**Theorem** **1.1** (Informal Threshold ECDSA Security Theorem) **.** _In the_
( _F_ Com _, F_ Zero _, F_ RVOLE _, F_ RelaxedKeyGen) _-hybrid model,_ _π_ ECDSA( _G, n, t_ ) _statistically_
_UC-realizes F_ ECDSA( _G, n, t_ ) _against a malicious adversary that statically cor-_
_rupts up to t −_ 1 _parties._


where _n_ is the number of parties in total, _t_ is the threshold of parties required
for a signature to be produced, and _G_ is the description of an elliptic curve.
In addition to the commitment functionality _F_ Com and the randomized VOLE
functionality _F_ RVOLE, [2] our protocol uses _F_ Zero to generate secret-sharings of
zero, and we abstract the key generation process behind _F_ RelaxedKeyGen.


**Machinery for Multiplication.** The protocol we have just described requires a two-message vector OLE protocol in which the first party to speak
supplies one value, and the second supplies two. Doerner et al. [DKLs18]
gave a two-round multiplication protocol based upon _oblivious transfer_ (OT),
and in a follow-up work they gave a three-round variant with reduced bandwidth [DKLs19]. In this work, we refine their techniques and propose a new
VOLE protocol [2] that has lower concrete bandwidth costs than _either_ of their
protocols, only two rounds, and no new assumptions or primitives. In other
words, our new protocol is the best of both worlds. Specifically, if _F_ EOTE is
an endemic OT-extension functionality, [3] which can be realized efficiently from
many public-key assumptions using well-known techniques, we prove:


**Theorem 1.2** (Informal Random VOLE Security Theorem) **.** _In the F_ EOTE _-_
_hybrid non-programmable global random oracle model, π_ RVOLE( _q, ℓ_ ) _UC-realizes_
_F_ RVOLE( _q, ℓ_ ) _against a PPT malicious adversary that statically corrupts no more_
_than one party._


Since _F_ EOTE can be instantiated efficiently assuming only the decisional
or computational Diffie-Hellman assumption over the signing curve [MR19,
CSW20], it is possible to implement our protocol entirely from _native_ assumptions, much as Doerner et al. did [DKLs18, DKLs19]. We believe this VOLE
protocol to inhabit a practically-advantageous position in the spectrum of bandwidth/computation tradeoffs, but we stress that our protocol can use _any_ VOLE
protocol that realizes a suitable functionality, and in particular, if bandwidth


2 Technically, we only require and only propose a _random_ VOLE protocol, but such a
protocol can be trivially lifted to the standard notion of VOLE.
3We introduce this functionality and the rationale behind it in section 5. For now it can
be thought of as as performing batches of oblivious transfers, with random inputs.


9


savings is paramount, then a VOLE derived from additively-homomorphic encryption [CGG [+] 20, CCL [+] 23] can be substituted.


**Zero Zero-Knowledge Required.** Because our signing protocol uses _ideal_
multiplication, and our consistency check ensures that the inputs to the multiplication functionality are the discrete logarithms of _Ri_ and pk _i_ for each party _Pi_,
the multiplication functionality can be used to extract the adversary’s secrets.
Viewed in this way, the multiplication and consistency check together form a
designated-verifier zero-knowledge proof of knowledge. Since the adversary’s
secrets are required only to simulate the _last_ message in the signing protocol,
after the extraction has occurred, no additional proofs of knowledge are necessary, _even during key generation_ . This allows us to introduce a _relaxed_ key
generation functionality and an extremely simple commit-release-and-complain
protocol to realize that functionality, and it allows us to completely avoid the
overhead typically incurred when proofs of knowledge are compiled for straightline extraction via the Fischlin [Fis05] or Kondi-shelat [Ks22] transforms. This
is particularly advantageous when new keys are generated almost as frequently
as signatures, as is sometimes the case in blockchain contexts.


**Bandwidth and Computational Efficiency.** We show via closed-form
analysis that when our VOLE protocol is used with our threshold ECDSA
protocol, the overall bandwidth cost is significantly reduced relative all prior
OT-based threshold ECDSA schemes [DKLs18, DKLs19, DOK [+] 20]. In terms of
bandwidth, our combined protocol is competitive with techniques based on _weak_
multiplication [HMRT22, HLNR23], which require more rounds. In terms of
concretely demonstrated performance (i.e. minimal wall-clock time in practical
benchmarks), the protocols of Doerner et al. [DKLs18, DKLs19] have heretofore
remained the state of the art due to the fact that competing approaches based
upon Paillier encryption [Pai99, CGG [+] 20] or class groups [CL15, CCL [+] 23] have
excessive computational costs. We show empirically that the protocol in this
work provides a strict improvement upon and fully subsumes the works of Doerner et al.. Moreover, the modularity and simplicity of our ECDSA signing
protocol imply that its performance properties can be adjusted to mimic those
of threshold ECDSA schemes based on other approaches simply by replacing
the VOLE with a different instantiation.


**Organization of this Paper.** After our preliminaries, we introduce our
Threshold ECDSA protocol in section 3 and prove it secure in section 4. In
section 5 we give our random VOLE construction, and we prove it secure in
section 6. In section 7 we give our key generation protocol. In section 8 we
give a closed-form cost analysis of all of our prototocols, and in section **??** we
discuss a proof-of-concept implementation and report benchmark results in a
number of settings. Finally, we give a brief account of a significantly simplified
two-round honest-majority protocol in section 9.


10


## **2 Preliminaries**

**2.1** **Notation**


We use = for equality, [..] = for right-to-left assignment, = [..] for left-to-right assignment, and _←_ for right-to-left sampling from a distribution. Single-letter
variables are set in _italic_ font, function names are set in sans-serif font, and
string literals are set in slab-serif font. We use X for an unspecified domain,
G for a group, Z for the integers, and N for the natural numbers. We use _λ_ c and
_λ_ s to denote the computational and statistical security parameters, respectively,
and _κ_ is the number of bits required to represent an element of the order field
of an elliptic curve. [4]

Vectors and arrays are given in bold and indexed by subscripts; thus **a** _i_ is the
_i_ [th] element of the vector **a**, which is distinct from the scalar variable _a_ . When
we wish to select a row or column from a multi-dimensional array, we place a _∗_
in the dimension along which we are not selecting. Thus **b** _∗,j_ is the _j_ [th] column
of matrix **b**, **b** _j,∗_ is the _j_ [th] row, and **b** _∗,∗_ = **b** refers to the entire matrix. We use
bracket notation to generate inclusive ranges, so [ _n_ ] denotes the integers from
1 to _n_ and [5 _,_ 7] = _{_ 5 _,_ 6 _,_ 7 _}_ . We use _|x|_ to denote the bit-length of _x_, and _|_ **y** _|_
to denote the number of elements in the vector **y** . Elliptic curve operations are
expressed additively, and curve points are typically given capitalized variables.
We use _Pi_ to indicate a party with index _i_ ; in a typical context, there will be
a fixed set of _n_ parties denoted _P_ 1 _, . . ., Pn_ . In contexts with only two parties,
they are given indices A and B and referred to as Alice and Bob, respectively.
The threshold is denoted _t_ .


**2.2** **Security and Communication Model**


We consider a malicious PPT adversary who can statically corrupt up to _t −_ 1
parties. All of our proofs are expressed in the Universal Composition framework [Can01]. Our techniques do not rely on any specific properties of the
framework. We assume that all of the parties in any protocol are fully connected via authenticated channels, and that the network is asynchronous. We
do not assume a broadcast channel, and we do not guarantee output or termination.


**2.3** **The ECDSA Signature Scheme**


All algorithms in the ECDSA signature scheme are parameterized by _G_ =
(G _, G, q_ ), which is the description of an elliptic curve group G of order _q_ that is
generated by _G_ . Here _κ_ = _|q|_ . At a minimum, security requires a curve-sampling
algorithm _G ←_ GrpGen(1 _[λ]_ [c] ) against which the discrete logarithm assumption
must hold. [5] In practice, the group description is fixed and standardized.


4In the context of non-pairing-friendly curves, _κ_ = 2 _· λ_ c, and all three security parameters
are asymptotically equivalent.
5This is necessary, but not known to be sufficient; as of writing ECDSA cannot be proven
secure under any standard assumption.


11


**Algorithm 2.1.** ECDSAGen( _G_ )


1. Uniformly choose a secret key sk _←_ Z _q_ .


2. Calculate the public key as pk [..] = sk _· G_ .


3. Output (pk _,_ sk).


**Algorithm 2.2.** ECDSASign( _G,_ sk _∈_ Z _q, m ∈{_ 0 _,_ 1 _}_ _[∗]_ )


1. Uniformly choose an instance key _r ←_ Z _q_ .


2. Calculate _R_ [..] = _r · G_ and let _r_ [x] be the _x_ -coordinate of _R_, modulo _q_ .



3. Calculate


4. Output _σ_ [..] = ( _s, r_ [x] ).



_s_ [..] = [SHA2][(] _[m]_ [) +][ sk] _[ ·][ r]_ [x]

_r_



**Algorithm 2.3.** ECDSAVerify( _G,_ pk _∈_ G _, m ∈{_ 0 _,_ 1 _}_ _[∗]_ _, σ ∈_ Z [2] _q_ [)]


1. Parse _σ_ as ( _s, r_ [x] ).



2. Calculate



_R_ _[′]_ [ ..] = [SHA2][(] _[m]_ [)] _[ ·][ G]_ [ +] _[ r]_ [x] _[ ·]_ [ pk]

_s_



and let _r_ [x] _[′]_ be the _x_ -coordinate of _R_ _[′]_, modulo _q_ .


3. Output 1 if and only if _r_ [x] _[′]_ = _r_ [x] .

## 3 t -Party Three-Round Threshold ECDSA


We present the functionality that our threshold ECDSA protocol realizes. In
contrast to the functionality given by Doerner et al. [DKLs19], ours uses the
ECDSA algorithms as _black boxes_, does not leak _R_ early, and formally distinguishes _aborts_, which prevent further interactions with the functionality, from
_failed signatures_, which do not. This distinction is important in threshold functionalities, because a single corrupt party should not, by participating in one
signing, be able to prevent signatures from being created in the future by other
groups of parties that exclude it.
**Functionality 3.1.** _F_ ECDSA( _G, n, t_ ) **: Threshold ECDSA**


This functionality is parameterized by the party count _n_, the threshold _t_,
and the elliptic curve _G_ = (G _, G, q_ ). The setup phase runs once with _n_
parties, and the signing phase may be run many times between (varying)
subgroups of parties indexed by **P** _⊆_ [ _n_ ] such that _|_ **P** _|_ = _t_ . If any party is


12


corrupt, then the adversary _S_ may instruct the functionality to abort selectively during the setup phase _only_ . _S_ may also instruct the functionality
to fail during the signing phase if any party indexed by **P** is corrupt, but
in this case the functionality does _not_ halt, and further signatures may be
attempted.


**Setup:** On receiving (init _,_ sid) from some party _Pi_ such that sid = [..]
_P_ 1 _∥_ _. . . ∥Pn∥_ sid _[′]_ and _i ∈_ [ _n_ ] and sid is fresh, send (init-req _,_ sid _, i_ ) to _S_ .
On receiving (init _,_ sid) from all parties,


1. Sample the joint secret and public keys, (pk _,_ sk) _←_ ECDSAGen( _G_ ).


2. Store (secret-key _,_ sid _,_ sk) in memory.


3. Send (public-key _,_ sid _,_ pk) directly to _S_ .


4. On receiving (release _,_ sid _, i_ ) for _i_ _∈_ [ _n_ ] from _S_, send
(public-key _,_ sid _,_ pk) to _Pi_ and store (pk-delievered _,_ sid _, i_ ) in
memory. On receiving (abort _,_ sid _, i_ ), send (abort _,_ sid) to _Pi_, and do
not interact with _Pi_ any further in this session.


**Signing:** On receiving (sign _,_ sid _,_ sigid _, mi_ ) from any party _Pi_, parse
sigid = [..] **P** _∥_ sigid _[′]_ such that _|_ **P** _|_ = _t_ and ignore the message if _i ̸∈_ **P** or
**P** _̸⊆_ [ _n_ ] or sigid is not fresh or if (pk-delievered _,_ sid _, i_ ) does not exist in
memory. Otherwise, send (sig-req _,_ sid _,_ sigid _, i, mi_ ) directly to _S_ .
On receiving (sign _,_ sid _,_ sigid _, mi_ ) from _Pi_ for every _i ∈_ **P**, sample _σ ←_

ECDSASign( _G,_ sk _, m_ **P** 1) and then


5. If there is any pair of signers _Pi_ and _Pj_ such that SHA2( _mi_ ) _̸_ =
SHA2( _mj_ ), then for every _i ∈_ **P**, then send (failure _,_ sid _,_ sigid) to _Pi_ .


6. If a corrupt party is indexed by **P**, and _S_ sends (fail _,_ sid _,_ sigid _, i_ )
such that _i ∈_ **P**, send (failure _,_ sid _,_ sigid) to _Pi_ and ignore any future
(fail _,_ sid _,_ sigid _, i_ ) or (proceed _,_ sid _,_ sigid _, i_ ) message.


7. If a corrupt party is indexed by **P**, and _S_ sends (proceed _,_ sid _,_ sigid _, i_ )
such that _i ∈_ **P**, send (signature _,_ sid _,_ sigid _, σ_ ) to _Pi_ and ignore any
future (fail _,_ sid _,_ sigid _, i_ ) or (proceed _,_ sid _,_ sigid _, i_ ) message.


8. If no corrupt parties are indexed by **P**, send (signature _,_ sid _,_ sigid _, σ_ ) to
_Pi_ for every _i ∈_ **P** .


9. Once every signing party has received an output, ignore all future messages with this sigid value.


In this work we do not make any assumptions about the SHA2 function.
If it is assumed to be collision resistant, then step 5 of _F_ ECDSA( _G, n, t_ ) can be
changed to emit a failure when the messages are unequal, rather than when
their images under SHA2 are unequal.


13


**3.1** **Building Blocks**


Here we define simpler functionalities from which our protocol will be constructed. All are standard and can be realized via standard techniques. We also
give notes on realization strategies and performance.
We begin with a functionality that samples Shamir sharings of keys for
discrete-log cryptosystems (e.g. ECDSA, the Schnorr signature scheme, the
ElGamal encryption scheme, the BBS+ signature scheme, etc). We refer to
this functionality as the _relaxed_ key generation functionality, because it does
not explicitly sample a secret key, and it may not even have enough information interally to compute the secret key, depending on the values of _t_ and _n_ .
However, it _always_ denies the adversary the ability to compute the secret key,
assuming that the discrete logarithm problem is hard. In section 7 we discuss
this design decision and its implications, and introduce a protocol to realize our
functionality.


**Functionality 3.2.** _F_ RelaxedKeyGen( _G, n, t_ ) **: Relaxed DLog Keygen**


This functionality is parameterized by the party count _n_, the threshold _t_,
and the elliptic curve _G_ = (G _, G, q_ ). The adversary _S_ may corrupt up to
_t −_ 1 parties that are indexed by **P** _[∗]_, and if _|_ **P** _[∗]_ _| ≥_ 1, then the adversary _S_
may instruct the functionality to abort.


**Key Generation:** On receiving (keygen _,_ sid) from some party _Pi_
such that sid = [..] _P_ 1 _∥_ _. . . ∥Pn∥_ sid _[′]_ and _i ∈_ [ _n_ ] and sid is fresh, send
(keygen-req _,_ sid _, i_ ) to _S_ . On receiving (keygen _,_ sid) from all parties,


1. Receive (adv-poly _,_ sid _, {p_ ˇ( _i_ ) _}i∈_ [ _n_ ] _\_ **P** _∗_ _, {P_ [ˇ] ( _j_ ) _}j∈_ **P** _[∗]_ ) from _S_ . Let _P_ [ˇ] ( _i_ ) [..] =
_p_ ˇ( _i_ ) _· G_ for _i ∈_ [ _n_ ] _\_ **P** _[∗]_, and abort if _P_ [ˇ] is not a degree-( _t −_ 1) polynomial
over G.


2. Sample a degree-( _t −_ 1) polynomial ˆ _p_ uniformly over Z _q_ . Let _P_ [ˆ] ( _k_ ) [..] =
_p_ ˆ( _k_ ) _·G_ and _P_ ( _k_ ) [..] = _P_ [ˇ] ( _k_ )+ _P_ [ˆ] ( _k_ ) for all _k ∈_ [ _n_ ], and let _p_ ( _i_ ) [..] = ˇ _p_ ( _i_ )+ ˆ _p_ ( _i_ )
for _i ∈_ [ _n_ ] _\_ **P** _[∗]_ . Note that _P_ is a polynomial of degree _t −_ 1 over G.
Interpolate _P_ (0).


3. Send (hon-poly _,_ sid _, P_ (0) _, {P_ [ˆ] ( _i_ ) _}i∈_ [ _n_ ] _\_ **P** _∗_ _, {p_ ˆ( _j_ ) _}j∈_ **P** _[∗]_ ) directly to _S_ .


4. On receiving (release _,_ sid _, i_ ) for _i ∈_ [ _n_ ] directly from _S_, if _Pi_ is honest,
then send (key-pair _,_ sid _, P_ (0) _, p_ ( _i_ )) to _Pi_ . If _Pi_ is corrupt, then do
nothing. If (abort _,_ sid _, i_ ) is received instead, then send (abort _,_ sid) to
_Pi_ .


Next, we introduce the standard commitment functionality, which can be
realized in the random oracle model via a folklore method: the commitment is
the image under the oracle of the committed value concatenated with a salt of
length 2 _λ_ c, and the decommitment is simply the committed value plus the salt.


14


**Functionality 3.3.** _F_ Com **: Commitment [CLOS02]**

In each instance one specific party _P_ S commits, and the other party _P_ R
receives the commitment and committed value.


**Commit:** On receiving (commit _,_ sid _, x_ ) from party _P_ S, parse sid = [..]
_P_ S _′∥P_ R _∥_ sid _[′]_ . If sid is a fresh value and S _[′]_ = S, then store
(commitment _,_ sid _, x_ ) in memory and send (committed _,_ sid) to _P_ R.


**Decommit:** On receiving (decommit _,_ sid) from _P_ S, if a record of the form
(commitment _,_ sid _, x_ ) exists in memory, then send (opening _,_ sid _, x_ ) to _P_ R.


We use a functionality that non-interactively samples uniform secret-sharings
of zero. It can be implemented in the _F_ Com-hybrid random oracle model: to
initialize the protocol, each pair of parties commits and decommits a pair of
_λ_ c-bit seeds to one another, then sums the pair to form a single shared seed.
When a party invokes the protocol, it evaluates the random oracle on each of
its shared seeds concatenated with the next index in sequence, and accumulates
the outputs: it subtracts oracle outputs for the party pairs in which it is lowerindexed, and adds oracle outputs for the party pairs in which it is higherindexed. The seeds can be reused indefinitely.

**Functionality 3.4.** _F_ Zero(G _, n_ ) **: Zero-Sharing Sampling [DKL** [+] **23]**

This functionality is parameterized by the party count _n_ and a group G.



**Sample:** Upon receiving (sample _,_ sid) from some party _Pi_ such that
sid = [..] _P_ 1 _∥_ _. . . ∥Pn∥_ sid _[′]_ and _i ∈_ [ _n_ ] and sid is fresh, uniformly sample **x** _←_ G _[n]_



1 _n_

conditioned on [�]



conditioned on _i∈_ [ _n_ ] _[x][i][ ≡]_ [0][G][ and send (][mask] _[,]_ [ sid] _[, x][i]_ [) to] _[ P][i]_ [. Upon receiv-]

ing (sample _,_ sid) from any other _Pj_ for _j ∈_ [ _n_ ] _\ {i}_, send (mask _,_ sid _, xj_ ) to
_Pj_ .



Finally, we use a randomized VOLE functionality _F_ RVOLE: [6] the first party
(Bob) to invoke the functionality receives a single random value; the second
party (Alice) then supplies a vector of chosen values, and _F_ RVOLE outputs to
both of them secret shares of the product of the random value and each of the
elements in the vector. We give a protocol to realize _F_ RVOLE in section 5, and
prove it secure in section 6.

**Functionality 3.5.** _F_ RVOLE( _q, ℓ_ ) **: Random Vector OLE**

This functionality interacts with two parties, _P_ A and _P_ B, who we refer to
as Alice and Bob. It also interacts directly with the ideal adversary _S_, who
can instruct the functionality to abort at any time. It is parameterized by
a prime _q_ that determines the order of the field over which multiplications
are performed.


6As we discuss in section 5, this is equivalent to plain VOLE under a simple informationtheoretic transformation.


15


**Sampling:** On receiving (sample _,_ sid) from Bob such that sid = [..]
_P_ B _∥P_ A _∥_ sid _[′]_ and sid is fresh and no record of the form (instance _,_ sid _, ∗_ )
exists in memory, sample _b_ _←_ Z _q_ if Bob is honest, or receive
(bob-sample _,_ sid _, b_ ) from _S_ if he is corrupt, and then store (instance _,_ sid _, b_ )
in memory, send (sample _,_ sid _, b_ ) to Bob, and send (ready _,_ sid) to Alice.


**Multiplication:** On receiving (multiply _,_ sid _,_ **a** ) from Alice, where **a** _∈_
Z _[ℓ]_ _q_ [, if there exists a message of the form (][instance] _[,]_ [ sid] _[, b]_ [) in memory, and]
if (complete _,_ sid) does not exist in memory, then:


 - If Alice is corrupt, receive (alice-share _,_ sid _,_ **c** ) from _S_ and compute
**d** [..] = _{_ **a** _i · b −_ **c** _i}i∈_ [ _ℓ_ ].


 - If Bob is corrupt, send (alice-multiplied _,_ sid) to _S_, wait for
(bob-share _,_ sid _,_ **d** ) in response, and compute **c** [..] = _{_ **a** _i · b −_ **d** _i}i∈_ [ _ℓ_ ].


 - If neither party is corrupt, sample **c** _←_ Z _[ℓ]_ _q_ [and] **[ d]** _[ ←]_ [Z] _q_ _[ℓ]_ [uniformly subject]
to _{_ **a** _i · b}i∈_ [ _ℓ_ ] = _{_ **c** _i_ + **d** _i}i∈_ [ _ℓ_ ].


and send (share _,_ sid _,_ **c** ) to Alice, send (share _,_ sid _,_ **d** ) to Bob, and store
(complete _,_ sid) in memory.


**3.2** **The Basic Three-Round Protocol**



In this section we give our three round signing protocol. We begin by developing
some intuition, building upon the sketch of our protocol in section 1.2. Suppose
that each party _Pi_ knows additive shares _ri_ and sk _i_ of _r_ and sk respectively, and
samples a uniform mask _ϕi_ . Suppose also that they know _ui_ and _vi_ such that

  -  -  -  -  -  



- 
_ui_ =
_i∈_ **P** _i∈_ **P**




- 
_ri ·_
_i∈_ **P** _i∈_ **P**




- 
_ϕi_ and
_i∈_ **P** _i∈_ **P**




- 
_vi_ =
_i∈_ **P** _i∈_ **P**




- 
sk _i ·_
_i∈_ **P** _i∈_ **P**



_ϕi_
_i∈_ **P**



It is easy to see that given these correlations,

   


_i∈_ **P** [(][SHA2] ~~�~~ [(] _[m]_ [)] _[ ·][ ϕ][i]_ [+] _[ r]_ [x] _[·][ v][i]_ [)]



_r_




_[m]_ [)] _[ ·][ ϕ][i]_ [+] _[ r]_ [x] _[·][ v][i]_ [)]

= [SHA2][(] _[m]_ [) +] _[ r]_ [x] _[ ·]_ [ sk]
_i∈_ **P** _[u][i]_ _r_



is a valid signature on _m_ under pk = sk _· G_ when combined with the nonce
_R_ = _r · G_ . Assuming the correlation to be generated with security against
malicious adversaries, it remains only to ensure that pk = sk _· G_ and that
_R_ = _r · G_, and to ensure that the adversary does not add any offsets to the
correlation when the signature is assembled. For the latter problem, once _m_, _R_,
and pk are fixed, there exists only one valid ECDSA signature, and so output
offsets can be detected perfectly by verifying the signature after it is assembled.
This leaves the problem of consistency.
Towards ensuring consistency, our main contribution is a novel method to
verify an enriched version of the correlation: each _Pi_ knows **c** [u] _i,j_ [and] **[ c]** _i,j_ [v] [and]


16


each _Pj_ knows **d** [u] _j,i_ [and] **[ d]** _j,i_ [v] [such that]

**c** [u] _i,j_ [=] _[ r][i]_ _[·][ ϕ][j]_ _[−]_ **[d]** [u] _j,i_ and **c** [v] _i,j_ [=][ sk] _[i]_ _[·][ ϕ][j]_ _[−]_ **[d]** [v] _j,i_

Under this correlation, if _Pi_ sends _Ri_ = _ri · G_ and pk _i_ = sk _i · G_ to _Pj_, then it
can also send **Γ** [u] _i,j_ [=] **[ c]** _i,j_ [u] _[·]_ _[G]_ [ and] **[ Γ]** _i,j_ [v] [=] **[ c]** _i,j_ [v] _[·]_ _[G]_ [ to] _[ authenticate]_ [ the former values.]
Because _ϕj_ is uniform and information-theoretically hidden from _Pi_, if _Pi_ sends
_Ri ̸_ = _ri · G_, then its chance of sending **Γ** [u] _i,j_ [satisfying]

**Γ** [u] _i,j_ [=] _[ R][i]_ _[·][ ϕ][j]_ _[−]_ **[d]** [u] _j,i_ _[·][ G]_


is exactly 1 _/q_ . Thus by checking the latter equality, _Pj_ can ensure that _Pi_ has
behaved _consistently_ with overwhelming probability. A similar check allows _Pj_
to ensure the consistency of pk _i_ and sk _i_ via **c** [v] _i,j_ [and] **[ d]** _j,i_ [v] [. Finally, it is easy to]
compute an appropriate value _ui_ given knowledge of _ri_, _ϕi_, **c** [u] _i,∗_ [, and] **[ d]** _i,_ [u] _∗_ [, and]
to compute an appropriate _vi_ given knowledge of sk _i_, _ϕi_, **c** [v] _i,∗_ [, and] **[ d]** _i,_ [v] _∗_ [, which]
implies that signature assembly can happen as before.
A few adjustments to the above simple scheme are required to write a security
proof. First, we do not insist that each _Pi_ use a consistent inversion mask _ϕi_ with
all of the other parties: instead, it uses an individual random mask with each
counterparty and checks consistency relative to that mask, and then _adjusts_
the correlation before signature assembly. This allows the correlation to be
generated by _F_ RVOLE. Second, _Ri_ is not sent, but committed and then released,
to avoid adversarial bias. Third, the shares of pk are rerandomized during each
signature, in order to prevent the adversary from inducing offsets that depend
on the honest parties’ secrets by using its mask values inconsistently among the
honest parties.
Our final protocol is three rounds. In the first round, each _Pi_ commits to
_Ri_ and instantiates an _F_ RVOLE instance toward each of the other parties. In the
second round, each party decommits _Ri_, inputs sk _i_ and _ri_ into the instances
of _F_ RVOLE that the other parties have instantiated toward it, and sends each of
the parties the values necessary to authenticate its inputs to _F_ RVOLE and adjust
the outputs of _F_ RVOLE so that they can be assembled into a signature. After
the second round, the inputs to _F_ RVOLE are authenticated. In the third round,
shares of the signature are swapped.
**Protocol 3.6.** _π_ ECDSA( _G, n, t_ ) **:** _t_ **-Party Three-Round ECDSA**


This protocol is parameterized by the party count _n_, the threshold _t_, and
the elliptic curve _G_ = (G _, G, q_ ). The setup phase runs once with parties _P_ 1 _, . . ., Pn_, and the signing phase may be run many times between
(varying) subsets of parties of size _t_ . The parties in this protocol interact with the ideal functionalities _F_ Com, _F_ Zero(Z _q, t_ ), _F_ RVOLE( _q,_ 2), and
_F_ RelaxedKeyGen( _G, n, t_ ). The SHA2 function is not assumed to have any cryptographic properties.


**Setup:**


1. On receiving (init _,_ sid) from the environment _Z_, each party _Pi_ checks


17


whether there exists a record of the form (key-pair _,_ sid _,_ pk _, p_ ( _i_ )) in
memory. If not, then _Pi_ sends (keygen _,_ sid) to _F_ RelaxedKeyGen( _G, n, t_ ).


2. On receiving (key-pair _,_ sid _,_ pk _, p_ ( _i_ )) from _F_ RelaxedKeyGen( _G, n, t_ ) each _Pi_
stores this message in memory and outputs (public-key _,_ sid _,_ pk) to the
environment. If _F_ RelaxedKeyGen( _G, n, t_ ) aborts, then _Pi_ aborts to the environment.


3. The parties perform any initialization procedure associated with
_F_ RVOLE( _q,_ 2) and _F_ Zero(Z _q, t_ ). _[a]_


**Signing:**


4. On receiving (sign _,_ sid _,_ sigid _, m_ ) from the environment _Z_, _Pi_ parses
**P** _∥_ sigid _[′]_ [ ..] = sigid such that _|_ **P** _|_ = _t_, and ignores the environment’s message if _i ̸∈_ **P** or **P** _̸⊆_ [ _n_ ] or sigid is not fresh or (key-pair _,_ sid _,_ pk _, p_ ( _i_ ))
does not exist in memory. Otherwise, _Pi_ continues to the next step.


5. _Pi_ samples a secret instance key _ri ←_ Z _q_ and an inversion mask _ϕi ←_ Z _q_
and computes


_Ri_ [..] = _ri · G_

**P** [-] _[j]_ [ ..] = **P** _\ {j}_ for _j ∈_ **P**


6. _Pi_ sends


 - (commit _, Pi∥Pj∥_ sid _∥_ sigid _, Ri_ ) to _F_ Com for every _j ∈_ **P** [-] _[i]_

 - (sample _, Pi∥Pj∥_ sid _∥_ sigid) to _F_ RVOLE( _q,_ 2) for every _j ∈_ **P** [-] _[i]_

 - (sample _, P_ **P** 1 _∥_ _. . . ∥P_ **P** _t∥_ sid _∥_ sigid) to _F_ Zero(Z _q, t_ )


This completes the first round.


if pipelining, supply _m_ here _[b]_


7. On receiving


 - (committed _, Pj∥Pi∥_ sid _∥_ sigid) from _F_ Com for every _j ∈_ **P** [-] _[i]_

 - (ready _, Pj∥Pi∥_ sid _∥_ sigid) from _F_ RVOLE( _q,_ 2) for every _j ∈_ **P** [-] _[i]_

 - (sample _, Pi∥Pj∥_ sid _∥_ sigid _,_ _**χ**_ _i,j_ ) from _F_ RVOLE( _q,_ 2) for every _j ∈_ **P** [-] _[i]_

 - (mask _, P_ **P** 1 _∥_ _. . . ∥P_ **P** _t∥_ sid _∥_ sigid _, ζi_ ) from _F_ Zero(Z _q, t_ )


_Pi_ computes
sk _i_ [..] = _p_ ( _i_ ) _·_ lagrange( **P** _, i,_ 0) + _ζi_


18


and sends (multiply _, Pj∥Pi∥_ sid _∥_ sigid _, {ri,_ sk _i}_ ) to _F_ RVOLE( _q,_ 2) for _j ∈_
**P** [-] _[i]_, and receives (share _, Pj∥Pi∥_ sid _∥_ sigid _, {_ **c** [u] _i,j_ _[,]_ **[ c]** [v] _i,j_ _[}]_ [) for] _[ j][ ∈]_ **[P]** [-] _[i]_ [ in re-]
sponse. Then _Pi_ computes


**Γ** [u] _i,j_ ..= **c** [u] _i,j_ _[·][ G]_

**Γ** [v] _i,j_ ..= **c** [v] _i,j_ _[·][ G]_

pk _i_ ..= sk _i · G_

_**ψ**_ _i,j_ ..= _ϕi −_ _**χ**_ _i,j_


for every _j ∈_ **P** [-] _[i]_ and for every _j ∈_ **P** [-] _[i]_ sends


 - (decommit _, Pi∥Pj∥_ sid _∥_ sigid) to _F_ Com

 - (check-adjust _,_ sid _,_ sigid _,_ **Γ** [u] _i,j_ _[,]_ **[ Γ]** _i,j_ [v] _[,]_ _**[ ψ]**_ _i,j_ _[,]_ [ pk] _i_ [) to] _[ P][j]_


if presigning, supply _m_ here _[b]_


8. On receiving


 - (opening _, Pj∥Pi∥_ sid _∥_ sigid _, Rj_ ) from _F_ Com

 - (share _, Pi∥Pj∥_ sid _∥_ sigid _, {_ **d** [u] _i,j_ _[,]_ **[ d]** _i,j_ [v] _[}]_ [) from] _[ F]_ RVOLE [(] _[q,]_ [ 2)]

 - (check-adjust _,_ sid _,_ sigid _,_ **Γ** [u] _j,i_ _[,]_ **[ Γ]** _j,i_ [v] _[,]_ _**[ ψ]**_ _j,i_ _[,]_ [ pk] _j_ [) from] _[ P][j]_


for every _j ∈_ **P** [-] _[i]_, _Pi_ checks whether


_**χ**_ _i,j · Rj −_ **Γ** [u] _j,i_ [=] **[ d]** _i,j_ [u] _[·][ G]_

_**χ**_ _i,j ·_ pk _j −_ **Γ** [v] _j,i_ [=] **[ d]** _i,j_ [v] _[·][ G]_


for every _j ∈_ **P** [-] _[i]_, and whether

     
pk _k_ = pk
_k∈_ **P**


and if these equations hold, then _Pi_ computes




 _R_ [..] =



_Rj_
_j∈_ **P**




- - 
_**ψ**_ _j,i_ +
_j∈_ **P** [-] _[i]_ _j∈_ **P** [-]




    -    _ui_ [..] = _ri ·_ _ϕi_ +




- - 
_**ψ**_ _j,i_ +
_j∈_ **P** [-] _[i]_ _j∈_ **P** [-]




    -     _vi_ [..] = sk _i ·_ _ϕi_ +



( **c** [u] _i,j_ [+] **[ d]** _i,j_ [u] [)]
_j∈_ **P** [-] _[i]_



( **c** [v] _i,j_ [+] **[ d]** _i,j_ [v] [)]
_j∈_ **P** [-] _[i]_



_wi_ [..] = SHA2( _m_ ) _· ϕi_ + _r_ [x] _· vi_


19


where _r_ [x] is the _x_ -coordinate of _R_, and sends (fragment _,_ sid _,_ sigid _, wi, ui_ )
to _Pj_ for every _j ∈_ **P** [-] _[i]_ . On the other hand, if _Pi_ ’s shared instance of
_F_ RVOLE with _Pj_ aborts, or if any of the aforementioned equations do not
hold for some _j ∈_ **P** [-] _[i]_, then _Pi_ sends (fail _,_ sid _,_ sigid) to all other parties
_and sends an analogous message at the corresponding point in all con-_
_current signing sessions that involve Pj_, outputs (failure _,_ sid _,_ sigid) to
the environment, does not continue to step 10, and does not participate
in any future signature signing sessions involving _Pj_ . This completes
the third round.


9. On receiving (fail _,_ sid _,_ sigid) from any _Pj_ for _j ∈_ **P**, _Pi_ outputs
(failure _,_ sid _,_ sigid) to the environment, and does not continue to
step 10.



10. On receiving (fragment _,_ sid _,_ sigid _, wj, uj_ ) from _Pj_ for every _j ∈_ **P** [-] _[i]_, _Pi_
computes







_s_ [..] =



_wj_
_j∈_ **P**

~~�~~

_uj_
_j∈_ **P**



and outputs (signature _,_ sid _,_ sigid _,_ ( _s, r_ [x] )) to the environment if and
only if ECDSAVerify( _G,_ pk _, m,_ ( _s, r_ [x] )) = 1; otherwise, _Pi_ outputs
(failure _,_ sid _,_ sigid).


_a_ The functionalities have no such initialization per se, but their realizations might,
and this is the appropriate time for it.
_b_ In this case, the signing phase is initiated with a (pre-sign _,_ sid _,_ sigid) message from
the environment, and waits at the indicated point for a (sign _,_ sid _,_ sigid _, m_ ) message from
the enviornment. See section 3.3.


**3.3** **Pipelining and Presigning**


We have marked the above protocol in two places to show how it can be modified to add _pipelining_ or _presigning_ in order to reduce the number of rounds
under certain circumstances (like several previous works [DOK [+] 20, CGG [+] 20,
CCL [+] 23]). In each case, the parties must supply the message _m_ to the protocol
at the indicated point, instead of at the beginning of the protocol.


**Pipelining.** Pipelining allows the first round of the protocol to be evaluated
before the message is known. If a single group of parties signs many messages
together, they can evaluate the first round of one signing instance along simultaneously with the third round of a previous signature, which enables the signing
procedure to be completed with only _two_ rounds of latency. Because the nonce
_R_ is not defined until the second round, the standard order of quantifiers, in
which the message cannot depend upon _R_ is respected, and the output signatures are secure if single-party ECDSA signatures are. However, _R_ becomes
well-defined from the point of view of the adversary as soon as the the honest


20


parties are activated by the environment, and potentially before the corrupt
parties are. This necessitates a revised functionality, which we present below.


**Functionality 3.7.** _F_ PipelinableECDSA( _G, n, t_ ) **: Pipelineable TECDSA**


This functionality is parameterized by the party count _n_, the threshold _t_,
and the elliptic curve _G_ = (G _, G, q_ ). The setup phase runs once with _n_
parties, and the signing phase may be run many times between (varying)
subgroups of parties indexed by **P** _⊆_ [ _n_ ] such that _|_ **P** _|_ = _t_ . If any party
is corrupt, then the adversary _S_ may instruct the functionality to abort
during the setup phase. _S_ may also instruct the functionality to fail during
the signing phase if any party indexed by **P** is corrupt, but in this case the
functionality does _not_ halt, and further signatures may be attempted.


**Setup:** On receiving (init _,_ sid) from some party _Pi_ such that sid = [..]
_P_ 1 _∥_ _. . . ∥Pn∥_ sid _[′]_ and _i ∈_ [ _n_ ] and sid is fresh, send (init-req _,_ sid _, i_ ) to _S_ .
On receiving (init _,_ sid) from all parties,


1. Sample the joint secret and public keys, (pk _,_ sk) _←_ ECDSAGen( _G_ ).


2. Store (secret-key _,_ sid _,_ sk) in memory.


3. Send (public-key _,_ sid _,_ pk) directly to _S_ .


4. On receiving (release _,_ sid _, i_ ) for _i_ _∈_ [ _n_ ] from _S_, send
(public-key _,_ sid _,_ pk) to _Pi_ and store (pk-delievered _,_ sid _, i_ ) in
memory.


**Signing:** On receiving (pre-sign _,_ sid _,_ sigid) from any party _Pi_, parse
sigid = [..] **P** _∥_ sigid _[′]_ such that _|_ **P** _|_ = _t_ and ignore the message if _i ̸∈_ **P** or
**P** _̸⊆_ [ _n_ ] or sigid is not fresh or if (pk-delievered _,_ sid _, i_ ) does not exist in
memory. Otherwise, send (presig-req _,_ sid _,_ sigid _, i_ ) directly to _S_ and store
(ready _,_ sid _,_ sigid _, i_ ) in memory.
On receiving (sign _,_ sid _,_ sigid _, m_ ) from _Pi_ for some _i_ _∈_ **P**, if
(ready _,_ sid _,_ sigid _, j_ ) exists in memory for all _j ∈_ **P** then


5. If (signature _,_ sid _,_ sigid _, σ_ ) does not exist in memory, then sample
_σ_ _←_ ECDSASign( _G,_ sk _, m_ ), store (signature _,_ sid _,_ sigid _, σ_ ) in memory, and if at least one party indexed by **P** is corrupt, then send
(leakage _,_ sid _,_ sigid _, r_ [x] ) directly to _S_ .


6. If at least one party indexed by **P** is corrupt, then send
(sig-req _,_ sid _,_ sigid _, i, m_ ) directly to _S_ .


Once every _Pi_ for _i ∈_ **P** has sent (sign _,_ sid _,_ sigid _, m_ ),


7. If the value of _m_ submitted is not consistent among all parties,
then for every _i ∈_ **P**, wait for _S_ (fail _,_ sid _,_ sigid _, i_ ) and then send
(failure _,_ sid _,_ sigid) to _Pi_ .


21


8. If a corrupt party is indexed by **P**, and _S_ sends (fail _,_ sid _,_ sigid _, i_ )
such that _i ∈_ **P**, send (failure _,_ sid _,_ sigid) to _Pi_ and ignore any future
(fail _,_ sid _,_ sigid _, i_ ) or (proceed _,_ sid _,_ sigid _, i_ ) message.


9. If a corrupt party is indexed by **P**, and _S_ sends (proceed _,_ sid _,_ sigid _, i_ )
such that _i ∈_ **P**, send (signature _,_ sid _,_ sigid _, σ_ ) to _Pi_ and ignore any
future (fail _,_ sid _,_ sigid _, i_ ) or (proceed _,_ sid _,_ sigid _, i_ ) message.


10. If no corrupt parties are indexed by **P**, send (signature _,_ sid _,_ sigid _, σ_ ) to
_Pi_ for every _i ∈_ **P** .


11. Once every signing party has received an output, ignore all future messages with this sigid value.


**Presigning.** Presigning allows the first _two_ rounds of the protocol to be evaluated before the message is known, which leaves only the last round (containing
nothing but a few simple field operations and one signature verification per
party) as the only round that must be evaluated online. Unlike pipelining, presigning does not preserve the standard order of quantifiers: the environment
can potentially condition the message on _R_, which is fixed in the second round.
Groth and Shoup [GS22b] gave a proof under a new assumption on SHA2 in
a variant of the generic group model that ECDSA is secure even if this occurs. They also show a number of conditions under which presigning can lead
to attacks (none of which apply to our protocol, as presented). We warn that
presigning should only be used in practice by those who understand and accept the implications and risks associated with it. Nevertheless, our protocol is
compatible with it.


**3.4** **Comparison to DKLs19**


The clearest single ancestor of our protocol is the _t_ -of- _n_ signing protocol of Doerner et al. [DKLs19], hereafter referred to as the 2019 DKLs protocol. Although
our protocol contains some of the same fundamental ideas as that one, ours rearranges the main protocol structure and the eliminates an intermediate functionality (the so-called inverse-sampling functionality) to yield a significant improvement in the number of rounds and a completely new information-theoretic
proof. Specifically, whereas the 2019 DKLs protocol requires either 6 + log _t_ or
10 rounds under the computational Diffie-Hellman assumption in the signing
curve, our new protocol requires only 3 rounds (one of which is pipelineable)
and is statistically secure without a random oracle. Both protocols are otherwise expressed in similar hybrid models. Our new protocol requires exactly
as many secure multiplications to be performed as does the 10-round version
of the 2019 protocol, whereas the (6 + log _t_ )-round version requires fewer. In
spite of this fact, our improvements to the secure multiplication protocol (i.e.
our random VOLE) ensure that our new protocol has a lower bandwidth cost
overall, as we discuss in section 8. While the number of rounds is significantly


22


improved relative to the 2019 DKLs scheme, we note that the number of elliptic
curve scalar operations grows with the number of signers in our new scheme,
whereas in the 2019 DKLs scheme it is a constant.
The heart of the structural difference between the two protocols lies in the
way they compute shares of 1 _/r_ and sk _/r_, and in the way they check the correctness of these computations. In the 2019 DKLs protocol, a distinct functionality
is defined to sample _R_ along with shares of _r_ and 1 _/r_ . This functionality is
realized by a protocol that samples multiplicative shares of _r_, inverts them locally, and then uses a _O_ (log _t_ )-long sequence of pairwise secure multiplications
to compute additive shares of both _r_ and _ϕ/r_, where _ϕ_ is a uniform mask. A
single commit-and-release check assures the well-formedness of the shares in the
2019 scheme, before they are unmasked. At this point shares of 1 _/r_ are multiplied by shares of sk, and an additional commit-and-release check establishes
the correctness of this multiplication with respect to pk. The 2019 protocol’s
higher round count is due the fact that it performs the inversion and multiplication operations sequentially, and the fact that it performs two sequential
commit-and-release checks. In contrast the protocol introduced here performs
inversion, multiplication with sk, and consistency checking simultaneously.


**3.5** **Two-Party Two-Message ECDSA**


In addition to their general _t_ -of- _n_ protocol, Doerner et al. also proposed a
specialized 2-of- _n_ protocol [DKLs18] that required only one message to be sent
in each direction. When _t_ = 2, a simple modification of our new protocol allows
it to match the communication properties of theirs. In each signing instance,
one of the two parties is chosen as the initiator. We will label the initiator
as Alice, and the other party as Bob. Only Alice will receive the signature at
the end. The parties run _π_ ECDSA with pipelining, as described in sections 3.2
and 3.3, and make the following modifications:


1. Alice’s pipelined first message is not triggered by any message from the environment. Instead, she sends her first message with her second message, upon
receiving (sign _,_ sid _,_ sigid) from the environment.


2. Bob’s second message is not triggered by a (sign _,_ sid _,_ sigid) message from
the environment. Instead, upon receiving Alice’s first and second messages,
Bob outputs (sig-req _,_ sid _,_ sigid) to the environment, and sends his second
message only after the environment responds with (proceed _,_ sid _,_ sigid _, m_ ).


3. Bob sends his third message at the same time he sends his second message.
Since Alice’s second message has already been received, this is possible.


4. Alice never sends her third message, depriving Bob of the _s_ component of
the output signature.


We note that these modifications to the protocol are secure because they are
essentially equivalent to rushing behavior, and our proof in section 4 already
acounts for rushing adversaries. We illustrate the modifications in figure 1.


23


A B A B
P P P P

pre-sign pre-sign pre-sign


sign m sign m sign m


proceed m


signature σ signature σ


signature σ



original round 1 original round 2 original round 3



pipelined



**Figure 1: Two-party Message Structures Illustrated** . On the left is the
protocol structure, with pipelining, as described in sections 3.2 and 3.3. On the
right is the protocol structure suggested for the two-party setting in this section.


The resulting protocol comprises three messages, and if the parties pipeline the
messages of each signature to occur simultaneously with the last message of a
previous signature, then the resulting protocol has two messages in effect, just
like the 2018 2-of- _n_ DKLs protocol.


**Comparison to DKLs18.** Compared to the 2-of- _n_ DKLs protocol from 2018,
our new protocol requires pipelining (and thus the storage of intermediate state)
in order to achieve a two-round structure. We note that in the two party-case
the downside implied by this is minimal: the stored state is exclusively pairwise,
just like the stored state already required by the OT-extension protocol that is
used to realize _F_ RVOLE. On the other hand, our new protocol realizes a _stan-_
_dard_ threshold signing functionality, whereas the 2018 DKLs protocol realizes a


24


weaker functionality that allows the adversary to bias _R_, and that is only known
to be equivalent to the standard functionality in the generic group model. Moreover, our protocol is statistically secure, whereas the 2018 protocol requires a
reduction to the computational Diffie-Hellman assumption in the signing curve,
and a reduction to the forgery game for ECDSA. Finally, our protocol improves
upon the efficiency of the 2018 protocol. We do not make use of zero-knowledge
proofs of knolwedge, whereas the 2018 DKLs protocol does; this allows us to
avoid the overhead of straight-line extractable proofs [Fis05, Ks22], which is by
far the most computationally-expensive component of the 2018 protocol. We
also improve upon the bandwidth of the 2018 protocol: the chosen-input multiplication subprotocols used in that work require a total of 4 _κ_ + 4 _λ_ s correlated
OT instances, half of which have a payload size of 2 _κ_ and half of which have
a correlation size of 4 _κ_ . Realizing the randomized VOLE instances required
by our new protocol via the VOLE protocol proposed in section 6 requires a
total of 2 _κ_ + 4 _λ_ s correlated OT instances, all of which have a correlation size
of 3 _κ_ . When _κ_ = 256 and _λ_ s = 80, as is common in practice, this yields a
38% savings in the bandwidth due to the OT payload _alone_ . This improvement
is independent of improvements due to new OT-extension techniques, and independent of an additional bandwidth-saving optimization that we introduce
in our VOLE construction. As discussed in section 8, the overall bandwidth
reduction achieved by our protocol when these improvements are considered is
57.3%.

## 4 Proof of Security for t -Party ECDSA


In section 1, we stated our security theorem:


**Theorem** **1.1** (Informal Threshold ECDSA Security Theorem) **.** _In the_
( _F_ Com _, F_ Zero _, F_ RVOLE _, F_ RelaxedKeyGen) _-hybrid model,_ _π_ ECDSA( _G, n, t_ ) _statistically_
_UC-realizes F_ ECDSA( _G, n, t_ ) _against a malicious adversary that statically cor-_
_rupts up to t −_ 1 _parties._


There is, however, one caveat we must address when formalizing the above
theorem. The UC model officially captures only a computational notion of
security, and if it is extended to permit unbounded environments and adversaries, then a problem arises when considering protocols that realize reactive
functionalities such as _F_ ECDSA: if each invocation implies a statistically negligible chance of distinguishing the real and ideal worlds, but the environment
is allowed exponentially-many invokations, then, the overall probability of distinguishing such a protocol from its functionality becomes noticeable. To avoid
this, we enforce explicit (but arbitrary) polynomial bounds on both the number
of parties and the number of times the honest parties may be invoked, while allowing the environment to be otherwise unbounded. Thus we have the following
formal theorem:


**Theorem 4.1** (Formal Threshold ECDSA Security Theorem) **.** _For every mali-_
_cious adversary A that statically corrupts up to t_ _−_ 1 _parties, there exists a PPT_


25


_simulator S_ _[A]_



_simulator S_ ECDSA _[A]_ _[that uses][ A][ as a black box, such that for every environment]_

_Z and every pair of polynomials µ, ν, if µ_ ( _λ_ ) _bounds the number of times Z_
_invokes any honest party, then_
 
Real _π_ ( _G,n,t_ ) _,_ ( _λ, z_ ) : 



Real _π_ ECDSA( _G,n,t_ ) _,_ ( _λ, z_ ) :
_A,Z_









_λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _,_
_t∈_ [2 _,n_ ] _, z∈{_ 0 _,_ 1 _}_ _[∗]_







_G ←_ GrpGen(1 _[λ]_ )



_G ←_ GrpGen(1 _[λ]_ )









_λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _,_
_t∈_ [2 _,n_ ] _, z∈{_ 0 _,_ 1 _}_ _[∗]_



_≈_ s











Ideal _F_ ECDSA( _G,n,t_ ) _,_
_S_ _[A]_ [(] _[G][,n,t]_ [)] _[,]_



ECDSA( _G,n,t_ ) _,_ ( _λ, z_ ) :

ECDSA _[A]_ [(] _[G][,n,t]_ [)] _[,][Z]_



_Proof._ We begin by specifying the simulator _S_ _[A]_



_Proof._ We begin by specifying the simulator _S_ ECDSA _[A]_ [(] _[G][, n, t]_ [), after which we will]

give a sequence of hybrid experiments to establish that it produces a view for
the environment that is indistinguishable from the real world.
**Simulator 4.2.** _S_ _[A]_ [(] _[G][, n, t]_ [)] **[:]** _[ t]_ **[-Party ECDSA]**



ECDSA _[A]_ [(] _[G][, n, t]_ [)] **[:]** _[ t]_ **[-Party ECDSA]**



This simulator is parameterized by the party count _n_, the threshold _t_, and
the elliptic curve _G_ = (G _, G, q_ ). The simulator has oracle access to the
adversary _A_, and emulates for it an instance of the protocol _π_ ECDSA( _G, n, t_ )
involving the parties _P_ 1 _, . . ., Pn_ . The simulator forwards all messages from
its own environment _Z_ to _A_, and vice versa. When the emulated protocol
instance begins, _A_ announces the identities of up to _t −_ 1 corrupt parties.
Let the indices of these parties be given by **P** _[∗]_ _⊆_ [ _n_ ]. _S_ ECDSA _[A]_ [(] _[G][, n, t]_ [)]

interacts with the ideal functionality _F_ ECDSA( _G, n, t_ ) on behalf of every
corrupt party, and in the exeriment that it emulates for _A_, it interacts with
_A_ and the corrupt parties on behalf of every honest party and on behalf of
the ideal oracles _F_ Com, _F_ Zero(Z _q, t_ ), _F_ RVOLE( _q,_ 2), and _F_ RelaxedKeyGen( _G, n, t_ ).


**Setup:**


1. On receiving (keygen _,_ sid) from _Pi_ for some _i ∈_ **P** _[∗]_ on behalf of
_F_ RelaxedKeyGen( _G, n, t_ ), send


 - (init _,_ sid) to _F_ ECDSA( _G, n, t_ ) on behalf of _Pi_

 - (keygen-req _,_ sid _, i_ ) directly to _A_ on behalf of _F_ RelaxedKeyGen( _G, n, t_ )

2. On receiving (init-req _,_ sid _, j_ ) for some _j ∈_ [ _n_ ] _\_ **P** _[∗]_ directly from
_F_ ECDSA( _G, n, t_ ), send (keygen-req _,_ sid _, j_ ) directly to _A_ on behalf of
_F_ RelaxedKeyGen( _G, n, t_ ).


3. On receving (abort _,_ sid) from _A_ on behalf of _F_ RelaxedKeyGen( _G, n, t_ ), send
(abort _,_ sid) to _F_ ECDSA( _G, n, t_ ).


4. On receiving (adv-poly _,_ sid _, {p_ ˇ( _i_ ) _}i∈_ [ _n_ ] _\_ **P** _∗_ _, {P_ [ˇ] ( _j_ ) _}j∈_ **P** _[∗]_ ) from _A_ on behalf of _F_ RelaxedKeyGen( _G, n, t_ ), compute _P_ [ˇ] ( _i_ ) [..] = ˇ _p_ ( _i_ ) _· G_ for _i ∈_ [ _n_ ] _\_ **P** _[∗]_


26


and abort if _P_ [ˇ] ( _i_ ) is not a polynomial of degree _t −_ 1 over G.


5. On receiving


 - (public-key _,_ sid _,_ pk) directly from _F_ ECDSA( _G, n, t_ )

 - (adv-poly _,_ sid _, {p_ ˇ( _i_ ) _}i∈_ [ _n_ ] _\_ **P** _∗_ _, {P_ [ˇ] ( _j_ ) _}j∈_ **P** _[∗]_ ) from _A_ on behalf of
_F_ RelaxedKeyGen( _G, n, t_ )

sample ˆ _pi_ ( _j_ ) _←_ Z _q_ uniformly for all _j ∈_ **P** _[∗]_ and _i ∈_ [ _n_ ] _\_ **P** _[∗]_ and compute

      _P_ ( _j_ ) [..] = _P_ [ˇ] ( _j_ ) + _p_ ˆ _i_ ( _j_ ) _· G_

_i∈_ [ _n_ ] _\_ **P** _[∗]_


for every _j ∈_ **P** _[∗]_ . Let _P_ (0) [..] = pk. If there are fewer than _t_ points
fixed on the polynomial _P_, then fix _t −_ 1 _−|_ **P** _[∗]_ _|_ points uniformly.
Now, interpreting _P_ as a polynomial of degree _t −_ 1 over G, interpolate _P_ ( _i_ ) for _i ∈_ [ _n_ ] _\_ **P** _[∗]_ and compute _P_ [ˆ] ( _i_ ) ..= _P_ ( _i_ ) _−_ _p_ ˇ( _i_ ) _· G_ .
Send (hon-poly _,_ sid _, {P_ [ˆ] ( _i_ ) _}i∈_ [ _n_ ] _\_ **P** _∗_ _, {p_ ˆ( _j_ ) _}j∈_ **P** _[∗]_ ) directly to _A_ on behalf
of _F_ RelaxedKeyGen( _G, n, t_ ), and store (public-key _,_ sid _,_ pk _, {P_ ( _i_ ) _}i∈_ [ _n_ ]) in
memory.


6. On receiving (release _,_ sid _, i_ ) or (abort _,_ sid _, i_ ) from _A_ on behalf of
_F_ RelaxedKeyGen( _G, n, t_ ), forward this message directly to _F_ ECDSA( _G, n, t_ ).


7. On receiving (public-key _,_ sid _,_ pk) from _F_ ECDSA( _G, n, t_ ) on behalf of _Pj_
for _j ∈_ **P** _[∗]_, store (sk-released _,_ sid _, j_ ) in memory.


8. Initialize the blacklist for sid to be empty.


**Signing:**


9. On receiving (sig-req _,_ sid _,_ sigid _, j, mj_ ) from _F_ ECDSA( _G, n, t_ ) on behalf of
the corrupt signers, compute


**P** _∥_ sigid _[′]_ [ ..] = sigid such that _|_ **P** _|_ = _t_

**C** [..] = **P** _∩_ **P** _[∗]_

**H** [..] = **P** _\_ **C**

**P** [-] _[k]_ [ ..] = **P** _\ {k}_ for _k ∈_ **P**


and if there is any _i ∈_ **P** [-] _[j]_ such that ( _j, i_ ) is in the blacklist for sid,
then ignore these messages and act as though they had never arrived.
Otherwise, for every _i ∈_ **C** send to _Pi_


 - (committed _, Pj∥Pi∥_ sid _∥_ sigid) on behalf of _F_ Com

 - (ready _, Pj∥Pi∥_ sid _∥_ sigid) on behalf of _F_ RVOLE( _q,_ 2)


27


10. Upon receiving (sample _, P_ **P** 1 _∥_ _. . . ∥P_ **P** _t∥_ sid _∥_ sigid) from _Pi_ on
behalf of _F_ Zero(Z _q, t_ ), sample _ζi_ _←_ Z _q_ and respond with
(mask _, P_ **P** 1 _∥_ _. . . ∥P_ **P** _t∥_ sid _∥_ sigid _, ζi_ ) on behalf of _F_ Zero(Z _q, t_ ). Note
that this step may occur at any time.


11. Upon receiving


  - (sample _, Pi∥Pj∥_ sid _∥_ sigid) from _Pi_ on behalf of _F_ RVOLE( _q,_ 2)

  - (adv-sample _, Pi∥Pj∥_ sid _∥_ sigid _,_ _**χ**_ _i,j_ ) from _A_ on behalf of _F_ RVOLE( _q,_ 2)


for some _i ∈_ **C** and some _j ∈_ **H**, send (sample _, Pi∥Pj∥_ sid _∥_ sigid _,_ _**χ**_ _i,j_ ) to
_Pi_ on behalf of _F_ RVOLE( _q,_ 2).


12. Upon satisfying satisfying step 9 for every _j ∈_ **H** and also receiving


  - (commit _, Pi∥Pj∥_ sid _∥_ sigid _,_ **R** _i,j_ ) from _Pi_ on behalf of _F_ Com

  - (sample _, Pi∥Pj∥_ sid _∥_ sigid) from _Pi_ on behalf of _F_ RVOLE( _q,_ 2)

  - (adv-sample _, Pi∥Pj∥_ sid _∥_ sigid _,_ _**χ**_ _i,j_ ) from _A_ on behalf of _F_ RVOLE( _q,_ 2)

  - (adv-share _, Pi∥Pj∥_ sid _∥_ sigid _, {_ **d** [u] _i,j_ _[,]_ **[ d]** [v] _i,j_ _[}]_ [)] from _A_ on behalf of
_F_ RVOLE( _q,_ 2)


for every _i ∈_ **C** and some consistent _j ∈_ **H**, if sigid is fresh and the records
(public-key _,_ sid _,_ pk _, {P_ ( _i_ ) _}i∈_ [ _n_ ]) and (sk-released _,_ sid _, i_ ) for every _i ∈_
**C** are stored in memory, then


  - if _Pj_ is _not_ the last honest party for whom these conditions hold,
then sample _rj ←_ Z _q_, sk _j ←_ Z _q_, _ϕj ←_ Z _q_, _δj_ [u] _[←]_ [Z] _[q]_ [, and] _[ δ]_ _j_ [v] _[←]_ [Z] _[q]_ [,]
and compute _Rj_ [..] = _rj · G_ and pk _j_ ..= sk _j · G_

  - if _Pj is_ the last honest party for whom these conditions hold,
then let _h_ ..= _j_ . For every _i ∈_ **C**, send (sign _,_ sid _,_ sigid _, mh_ ) to
_F_ ECDSA( _G, n, t_ ) on behalf of _Pi_ and send (proceed _,_ sid _,_ sigid _, i_ ) directly
to _F_ ECDSA( _G, n, t_ ). If (signature _,_ sid _,_ sigid _,_ ( _s, r_ [x] )) is received in reply
on behalf of the corrupt parties, reconstruct _R_ from the x-coordinate
_r_ [x] and compute




  _Rh_ [..] = _R −_




- 
_Rk_ and pk _h_ ..= pk _−_
_k∈_ **P** [-] _[h]_ _k∈_ **P** [-]



pk _k_
_k∈_ **P** [-] _[h]_



If (failure _,_ sid _,_ sigid) is received in reply, then sample _R ←_ G and
_s ←_ Z _q_ uniformly and compute _Rh_ and pk _h_ as above.


28


and then for every _i ∈_ **C** compute


_**ψ**_ _j,i ←_ Z _q_
**Γ** [u] _j,i_ ..= _**χ**_ _i,j · Rj −_ **d** [u] _i,j_ _[·][ G]_

**Γ** [v] _j,i_ ..= _**χ**_ _i,j ·_ pk _j −_ **d** [v] _i,j_ _[·][ G]_


and send to _Pi_


  - (opening _, Pj∥Pi∥_ sid _∥_ sigid _, Rj_ ) on behalf of _F_ Com

  - (check-adjust _,_ sid _,_ sigid _,_ **Γ** [u] _j,_ _[,]_ **[ Γ]** [v] _j,i_ _[,]_ _**[ ψ]**_ _j,i_ _[,]_ [ pk] _j_ [) on behalf of] _[ P][j]_

  - (share _, Pi∥Pj∥_ sid _∥_ sigid _, {_ **d** [u] _i,j_ _[,]_ **[ d]** [v] _i,j_ _[}]_ [) on behalf of] _[ F]_ RVOLE [(] _[q,]_ [ 2)]


13. Upon satisfying satisfying steps 9 and 12 for every _j ∈_ **H** and receiving
(abort _, Pj∥Pi∥_ sid _∥_ sigid) directly from _A_ on behalf of _F_ RVOLE( _q,_ 2) for
some _i ∈_ **C** and some _j ∈_ **H**, send (fail _,_ sid _,_ sigid) to all corrupt parties
on behalf of _Pj_, _send the_ fail _message on behalf of Pj at the corre-_
_sponding point in all concurrent signing sessions involving Pj and Pi_,
append ( _j, i_ ) to the blacklist for sid, and ignore all future instructions
pertaining to the signature ID sigid.


14. Upon satisfying satisfying steps 9 and 12 for every _j ∈_ **H** and receiving


  - (multiply _, Pj∥Pi∥_ sid _∥_ sigid _, {_ **a** [u] _i,j_ _[,]_ **[ a]** [v] _i,j_ _[}]_ [)] from _Pi_ on behalf of
_F_ RVOLE( _q,_ 2)

  - (adv-share _, Pj∥Pi∥_ sid _∥_ sigid _, {_ **c** [u] _i,j_ _[,]_ **[ c]** [v] _i,j_ _[}]_ [)] from _A_ on behalf of
_F_ RVOLE( _q,_ 2)


for some _i_ _∈_ **C** and some _j_ _∈_ **H**, send
(share _, Pj∥Pi∥_ sid _∥_ sigid _, {_ **c** [u] _i,j_ _[,]_ **[ c]** [v] _i,j_ _[}]_ [) to] _[ P][i]_ [ on behalf of] _[ F]_ RVOLE [(] _[q,]_ [ 2).]


15. Upon satisfying satisfying steps 9 and 12 for every _j ∈_ **H** and receiving


  - (decommit _, Pi∥Pj∥_ sid _∥_ sigid) from _Pi_ on behalf of _F_ Com

  - (multiply _, Pj∥Pi∥_ sid _∥_ sigid _, {_ **a** [u] _i,j_ _[,]_ **[ a]** [v] _i,j_ _[}]_ [)] from _Pi_ on behalf of
_F_ RVOLE( _q,_ 2)

  - (adv-share _, Pj∥Pi∥_ sid _∥_ sigid _, {_ **c** [u] _i,j_ _[,]_ **[ c]** [v] _i,j_ _[}]_ [)] from _A_ on behalf of
_F_ RVOLE( _q,_ 2)

  - (check-adjust _,_ sid _,_ sigid _,_ **Γ** [u] _i,j_ _[,]_ **[ Γ]** _i,j_ [v] _[,]_ _**[ ψ]**_ _i,j_ _[,]_ **[ pk]** _i,j_ [) from] _[ P][i]_ [on behalf of] _[ P][j]_


for every _i ∈_ **C** and some consistent _j ∈_ **H**,


29


- If there exists some _i ∈_ **C** such that **a** [u] _i,j_ _[·][ G][ ̸]_ [=] **[ R]** _[i,j]_ [ or] **[ a]** _i,j_ [v] _[·][ G][ ̸]_ [=] **[ pk]** _i,j_
or **Γ** [u] _i,j_ [=] **[ c]** [u] _i,j_ _[·][ G]_ [ or] **[ Γ]** _i,j_ [v] [=] **[ c]** [v] _i,j_ _[·][ G]_ [, or if]




- 
**pk** _i,j_ +
_i∈_ **C** _k∈_ **H**







pk _k ̸_ = pk
_k∈_ **H**



then send (fail _,_ sid _,_ sigid _, k_ ) directly to _F_ ECDSA( _G, n, t_ ) for every _k ∈_
**H**, send (fail _,_ sid _,_ sigid) to all corrupt parties on behalf of _Pj_, _send_
_the_ fail _message on behalf of Pj at the corresponding point in all_
_concurrent signing sessions involving Pj and Pi_, append ( _j, i_ ) to the
blacklist for sid, and ignore all future instructions pertaining to the
signature ID sigid.

- If _j ̸_ = _h_ and **a** [u] _i,j_ _[·][ G]_ [ =] **[ R]** _[i,j]_ [ and] **[ a]** _i,j_ [v] _[·][ G]_ [ =] **[ pk]** _i,j_ [and] **[ Γ]** _i,j_ [u] [=] **[ c]** _i,j_ [u] _[·][ G]_
and **Γ** [v] _i,j_ [=] **[ c]** _i,j_ [v] _[·][ G]_ [ for every] _[ i][ ∈]_ **[C]** [, and if]




- 
**pk** _i,j_ +
_i∈_ **C** _k∈_ **H**







pk _k_ = pk
_k∈_ **H**



then compute




  _uj_ [..] = _rj ·_



_**ψ**_ _i,j_ + _δj_ [u]
_i∈_ **C**








 +



_i∈_ **C**




( _**ϕ**_ _j −_ _**ψ**_ _j,i_ ) _·_ **a** [u] _i,j_
+ _**χ**_ _i,j · rj −_ **c** [u] _i,j_ _[−]_ **[d]** _i,j_ [u]




  _vj_ [..] = sk _j ·_



_**ψ**_ _i,j_ + _δj_ [v]
_i∈_ **C**








 +


_i∈_ **C**




( _**ϕ**_ _j −_ _**ψ**_ _j,i_ ) _·_ **a** [v] _i,j_
+ _**χ**_ _i,j ·_ sk _j −_ **c** [v] _i,j_ _[−]_ **[d]** _i,j_ [v]



_wj_ [..] = SHA2( _mh_ ) _· ϕj_ + _r_ [x] _· vj_


and send (fragment _,_ sid _,_ sigid _, wj, uj_ ) to _Pi_ for every _i ∈_ **C** on behalf
of _Pj_ .

- If _j_ = _h_ and **a** [u] _i,h_ _[·][ G]_ [ =] **[ R]** _[i,h]_ [ and] **[ a]** _i,h_ [v] _[·][ G]_ [ =] **[ pk]** _i,h_ [and] **[ Γ]** _i,h_ [u] [=] **[ c]** _i,h_ [u] _[·][ G]_
and **Γ** [v] _i,h_ [=] **[ c]** _i,h_ [v] _[·][ G]_ [ for every] _[ i][ ∈]_ **[C]** [, and if]




- 
**pk** _i,j_ +
_i∈_ **C** _k∈_ **H**







pk _k_ = pk
_k∈_ **H**



then sample _uh ←_ Z _q_ and compute


_ϕi_ [..] = _**ψ**_ _i,h_ + _**χ**_ _i,h_ for _i ∈_ **C**


30






�� 
_ϕk_ + _**ψ**_ _h,i_
_k∈_ **P** [-] _[h]_




 _u_ ˆ [..] =


_i∈_ **C**



 ��

**a** [u] _i,h_ _[·]_

 _k∈_ **P** [-]



+ **c** [u] _i,h_ [+] **[ d]** _i,h_ [u]




 +








  _δj_ [u] [+] _[ r][j]_ _[·]_







_j∈_ **H** _\{h}_



�� 
_ϕk_ + _**ψ**_ _h,i_
_k∈_ **P** [-] _[h]_



_ϕi_
_i∈_ **C**























 _v_ ˆ [..] =


_i∈_ **C**



 ��

**a** [v] _i,h_ _[·]_

 _k∈_ **P** [-]



+ **c** [v] _i,h_ [+] **[ d]** _i,h_ [v]








 +








  _δj_ [v] [+][ sk] _[j]_ _[·]_



_j∈_ **H** _\{h}_




   _w_ ˆ [..] = SHA2( _mh_ ) _·_



_ϕi_
_i∈_ **C**



_ϕk_ + _r_ [x] _·_ ˆ _v_

_k∈_ **P** [-] _[h]_



_wh_ [..] = _s · uh_ + _s ·_ ˆ _u −_ _w_ ˆ


and send (fragment _,_ sid _,_ sigid _, wh, uh_ ) to _Pi_ for every _i ∈_ **C** on behalf
of _Ph_ .


16. On receiving (fail _,_ sid _,_ sigid) from _Pi_ on behalf of _Pj_ for some _j ∈_ **H**
and some _i ∈_ **C**, send (fail _,_ sid _,_ sigid _, j_ ) directly to _F_ ECDSA( _G, n, t_ ).


17. On receiving (fragment _,_ sid _,_ sigid _,_ **w** _i,j,_ **u** _i,j_ ) from _Pi_ on behalf of _Pj_ for
some _j ∈_ **H** and _every i ∈_ **C**, if

      - [�]





_wk_ + [�]
_k∈_ ~~�~~ **H** _i∈_

_uk_ + ~~[�]~~
_k∈_ **H** _i∈_



_wk_ + **w** _i,j_
_∈_ ~~�~~ **H** _i_ ~~[�]~~ _∈_ **C**



= _s_

~~[�]~~ **u** _i,j_

_i∈_ **C**



then send (proceed _,_ sid _,_ sigid _, j_ ) directly to _F_ ECDSA( _G, n, t_ ); otherwise,
send (fail _,_ sid _,_ sigid _, j_ ) directly to _F_ ECDSA( _G, n, t_ ).


Our sequence of hybrid experiments begins with the real world



_G ←_ GrpGen(1 _[λ]_ )









_λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _,_
_t∈_ [2 _,n_ ] _, z∈{_ 0 _,_ 1 _}_ _[∗]_



_H_ 0 =











Real _π_ ECDSA( _G,n,t_ ) _,_ ( _λ, z_ ) :
_A,Z_



and proceeds by gradually replacing the code of the real parties with elements
of the simulator until _S_ ECDSA _[A]_ [(] _[G][, n, t]_ [) is fully implemented and the experiment]

is the ideal one.


**Hybrid** _H_ 1 **.** This hybrid experiment replaces all of the individual honest parties
and ideal functionalities in _H_ 0 with a single simulator machine _S_ that runs


31


their code and interacts with the adversary, environment, and corrupt parties
on their behalf. Since _S_ interacts with the adversarial entities on behalf of the
ideal functionalities, it learns any values they receive or that are defined by
their internal state (for example, the value ˆ _p_ (0) that defines the honest parties’
contributions to the secret key sk). This is a purely syntactical change, and so
it must be the case that _H_ 1 = _H_ 0.


**Hybrid** _H_ 2 **.** This hybrid behaves identically to _H_ 1, except that the consistency
checks that are performed by _S_ on behalf of the _honest_ parties in step 8 of
_π_ ECDSA are replaced. Let **R** _i,j_ denote the value of _Ri_ actually transmitted from
party _Pi_ to party _Pj_ (although the protocol specifies that _Pi_ should use a single
consistent value _Ri_ with all honest parties, _Pi_ might use inconsistent values if
it is corrupt and misbehaves). Similarly, let **pk** _i,j_ be the value of pk _i_ actually
transmitted to _Pj_ . In _H_ 2, _S_ does not check whether


_**χ**_ _j,i ·_ **R** _i,j −_ **Γ** _i,j_ [u] [=] **[ d]** _j,i_ [u] _[·][ G]_ (1)

_**χ**_ _j,i ·_ **pk** _i,j −_ **Γ** _i,j_ [v] [=] **[ d]** _j,i_ [v] _[·][ G]_ (2)


but instead checks whether **a** [u] _i,j_ _[·]_ _[G]_ [ =] **[ R]** _[i,j]_ [ and] **[ a]** _i,j_ [v] _[·]_ _[G]_ [ =] **[ pk]** _i,j_ [and] **[ Γ]** _i,j_ [u] [=] **[ c]** _i,j_ [u] _[·]_ _[G]_
and **Γ** [v] _i,j_ [=] **[ c]** _i,j_ [v] _[·][ G]_ [, as specified in step][ 15][ of] _[ S]_ ECDSA [.]
Because the code of _F_ RVOLE enforces that


_**χ**_ _j,i ·_ **a** [u] _i,j_ [=] **[ c]** _i,j_ [u] [+] **[ d]** _j,i_ [u] and _**χ**_ _j,i ·_ **a** [v] _i,j_ [=] **[ c]** _i,j_ [v] [+] **[ d]** _j,i_ [v]


we know that if the consistency checks evaluated in _H_ 2 pass, then the checks
in _H_ 1 also pass. We also know that if **a** [u] _i,j_ _[·][ G]_ [ =] **[ R]** _[i,j]_ [ and] **[ a]** _i,j_ [v] _[·][ G]_ [ =] **[ pk]** _i,j_ [, then]
the checks in both hybrids pass if and only if **Γ** _i,j_ [u] [=] **[ c]** _i,j_ [u] _[·][ G]_ [ and] **[ Γ]** _i,j_ [v] [=] **[ c]** _i,j_ [v] _[·][ G]_ [.]
Thus, the adversary can only distinguish the two by setting **a** [u] _i,j_ _[·][ G][ ̸]_ [=] **[ R]** _[i,j]_
or **a** [v] _i,j_ _[·][ G][ ̸]_ [=] **[ pk]** _i,j_ [for some corrupt] _[ P][j]_ [ and contriving to pass the consistency]
check in _H_ 1, while failing the check (with certainty) in _H_ 2. Because **R** _i,j_ is
fixed, there is exactly one value of **Γ** _i,j_ [u] [that will satisfy equation][ 1][ for any]
assignment of _**χ**_ _j,i_ and **d** [u] _j,i_ [.] Since _**χ**_ _j,i_ and **d** [u] _j,i_ [are uniformly sampled and]
information-theoretically hidden from the adversary at the time that it must
commit to **Γ** [u] _i,j_ [, the probability that the adversary sends this value is exactly]
1 _/q_ if **a** [u] _i,j_ _[·][ G][ ̸]_ [=] **[ R]** _[i,j]_ [. A similar argument implies that the adversary has a 1] _[/q]_
probability of satisfying equation 2 if **a** [v] _i,j_ _[·][ G][ ̸]_ [=] **[ pk]** _i,j_ [.]
Note that if a consistency check fails, the honest party that observes the
failure will never again allow a signing session to produce an output when it
involves the party that caused the failure. Even if an unbounded environment
were permitted to invoke an unbounded number of signing sessions, at most
( _t_ _−_ 1) _·_ ( _n_ _−_ _t_ +1) failed consistency checks can occur before there are no honest
parties that are willing to sign with any corrupt party. The probability that at
least one of the first ( _t −_ 1) _·_ ( _n −_ _t_ + 1) distinguishing attempts will result in
success is upper-bounded by ( _t −_ 1) _·_ ( _n −_ _t_ + 1) _/q ≤_ _n_ [2] _/q_, and since _n_ = _ν_ ( _λ_ )
is polynomially-bounded while _q_ is exponential in _λ_, it follows that _H_ 2 _≈_ s _H_ 1.


32


**Hybrid** _H_ 3 **.** This hybrid behaves identically to _H_ 2, except that if the environment triggers a single signing instance with ID sigid among a group of _exclu-_
_sively_ honest parties with messages that have consistent images under SHA2,
then the protocol code no longer runs. Instead, upon (sign _,_ sid _,_ sigid _, m_ ) on
behalf of all of the parties, _S_ reconstructs sk from the honest parties’ points
on the polynomial _p_, locally evaluates _σ ←_ ECDSASign( _G,_ sk _, m_ ), and outputs
(signature _,_ sid _,_ sigid _, σ_ ) to the environment on behalf of all parties.
Observe that in _H_ 2, a group of honest parties compute their views such that


_ri ←_ Z _q_ for every _i ∈_ **P** (3)

_ri ·_ _**χ**_ _j,i_ = **c** [u] _i,j_ [+] **[ d]** _j,i_ [u] [for every] _[ i, j][ ∈]_ **[P]** [ :] _[ i][ ̸]_ [=] _[ j]_

sk _i ·_ _**χ**_ _j,i_ = **c** [v] _i,j_ [+] **[ d]** _j,i_ [v] [for every] _[ i, j][ ∈]_ **[P]** [ :] _[ i][ ̸]_ [=] _[ j]_



_**ψ**_ _j,i_ = _ϕj −_ _**χ**_ _j,i_ for every _i, j ∈_ **P** : _i ̸_ = _j_




 _u_ =




- _ri · ϕi_ +



_i∈_ **P**




 - 
( _ri ·_ _**ψ**_ _j,i_ + **c** [u] _i,j_ [+] **[ d]** _i,j_ [u] [)]
_j∈_ **P** _\{i}_



= _r · ϕ_




 _v_ =




- sk _i · ϕi_ +



_i∈_ **P**


= sk _· ϕ_




 - 
( _ri ·_ _**ψ**_ _j,i_ + **c** [v] _i,j_ [+] **[ d]** _i,j_ [v] [)]
_j∈_ **P** _\{i}_



_s_ = [SHA2][(] _[m]_ [)] _[ ·][ ϕ]_ [ +] _[ r]_ [x] _[ ·][ v]_



(4)
_r_




_[ ·][ ϕ]_ [ +] _[ r]_ [x] _[ ·][ v]_

= [SHA2][(] _[m]_ [) +] _[ r]_ [x] _[ ·]_ [ sk]
_u_ _r_



The consistency checks introduced in _H_ 2 trivially pass when all of the participants are honest, and by inspection we can see that equations 3 and 4 yield
a signature with a distribution identical to that produced by ECDSASign, which
implies that the verification check in step 10 of _π_ ECDSA always passes when all
signing parties are honest. Thus the output distributions for all signing parties
are identical in _H_ 3 and _H_ 2, and in both hybrids the probability of a failed signature is zero. No other values are observable by the adversary, and so the two
hybrids are perfectly indistinguishable.


**Hybrid** _H_ 4 **.** This hybrid behaves identically to _H_ 3, except when the environment triggers a single signing instance with ID sigid between a group containing
two or more honest parties, but uses inconsistent messages with the honest parties. Suppose _Ph_ is the last honest party in the group to be activated by the
environment. In _H_ 4, _S_ replaces _mj_ with _mh_ in the calculations of every honest
_Pj_ for _j ∈_ **H** _\ {h}_ . If there exists some _j ∈_ **H** _\ {h}_ such that environment
sends (sign _,_ sid _,_ sigid _, mj_ ) to _Pj_ and SHA2( _mj_ ) _̸_ = SHA2( _mh_ ), then _S_ samples
_wh ←_ Z _q_ instead of calculating _wh_ per the instructions in step 8 of _π_ ECDSA as
in _H_ 3, always outputs (failure _,_ sid _,_ sigid) to the environment on behalf of all
honest parties, and ignores all future messages with the same sigid.
In _H_ 3, honest parties fail if they do not receive a valid signature as output, and we have argued in the context of _H_ 3 that a group of signers always
receives a valid signature as output when their messages have the same image


33


under SHA2 and nobody deviates from the protocol. In _H_ 3, _S_ always calculates
_wh_ [..] = SHA2( _mh_ ) _· ϕh_ + _r_ [x] _· vh_ and _wj_ [..] = SHA2( _mj_ ) _· ϕj_ + _r_ [x] _· vj_ . We make
three observations. First, the leftmost terms of these equations are the _only_
constituent parts of the final signature that depend upon _mh_ or _mj_ . Second,
_S_ effectively samples _wh_ and _wj_ uniformly subject to a condition on their sum,
because _vj_ and _vh_ depend linearly on **c** [v] _j,h_ [+] **[ d]** _j,h_ [v] [and] **[ c]** _h,j_ [v] [+] **[ d]** _h,j_ [v] [respectively,]
and the latter values are sampled uniformly subject to a condition on their sum.
Third, due to similar linear dependencies upon **c** [u] _j,h_ [+] **[ d]** _j,h_ [u] [and] **[ c]** _h,j_ [u] [+] **[ d]** _h,j_ [u] [, we]
can conclude that _uj_ and _uh_ commit _S_ to the _sum_ of _ϕj_ and _ϕh_, but _S_ still has
a degree of freedom in choosing the individual values. [7]

Summing and rewriting, we have


_wh_ + _wj_ = SHA2( _mh_ ) _·_ ( _ϕh_ + _ϕj_ ) + _r_ [x] _·_ ( _vh_ + _vj_ )

+ (SHA2( _mj_ ) _−_ SHA2( _mh_ )) _· ϕj_


If SHA2( _mh_ ) = SHA2( _mj_ ), then (SHA2( _mj_ ) _−_ SHA2( _mh_ )) _· ϕj_ = 0 and the
signature is valid if the corrupt parties follow the protocol. If SHA2( _mh_ ) _̸_ =
SHA2( _mj_ ), then (SHA2( _mj_ ) _−_ SHA2( _mh_ )) _· ϕj_ is distributed uniformly, because
_ϕj_ is, as we have observed, uniformly sampled and information-theoretically
hidden from the adversary. All other terms that the honest parties contribute
to the signature _are the same in either case_ . In other words, if SHA2( _mh_ ) _̸_ =
SHA2( _mj_ ), then _wh_ and _wj_ are not uniform subject to a condition on their
sum, but simply uniform. This implies that the joint distribution of _wi_ for
every _i ∈_ **H** is identical in _H_ 4 and _H_ 3, both when SHA2( _mh_ ) = SHA2( _mj_ ) and
when SHA2( _mh_ ) _̸_ = SHA2( _mj_ ).
Once the message, public key, and nonce are fixed, there is exactly one valid
ECDSA signature. When SHA2( _mh_ ) _̸_ = SHA2( _mj_ ) and _wh_ and _wj_ are uniform
without constraint, the chance that the resulting signature will be valid for any
honest party’s message (and that party will consequently output a signature
in _H_ 3) is no greater than _t/q_ in each signing session. Since _t < n_ = _ν_ ( _λ_ )
is polynomial in _λ_, and we have assumed the number of signing sessions to
be bounded by _µ_ ( _λ_ ), which is polynomial in _λ_, but _q_ is exponential in _λ_, we
can conclude that the distribution of honest party failures in _H_ 4 is statistically
indistinguishable from the distribution in _H_ 3. It follows that _H_ 4 _≈_ s _H_ 3 overall.
For the remainder of this proof, we will assume that if any group of _honest_
signing parties does not output a failure, then their messages have identical
images under SHA2.


**Hybrid** _H_ 5 **.** The behavior of this hybrid differs from _H_ 4 when the environment
triggers a signing instance among a group of parties, some of whom are corrupt.
In _H_ 5, if the honest parties receive messages that have identical images under
SHA2, then _S_ uses the ECDSASign to generate the signature, and embeds it into
the protocol by altering the code of one of the honest signers. Specifically, _S_


7Fixing one of these two values also fixes the other, but the simulator cannot calculate
both without implicitly breaking the discrete logarithm problem on _R_ . Fortunately it will not
be necessary to calculate both.


34


follows the code of the honest parties on their behalves until step 7 of _π_ ECDSA.
Whichever honest party reaches this step _last_ is designated _Ph_ (as before), and
if the honest parties have messages with identical images under SHA2, then the
code of _Ph_ is replaced for the remainder of the protocol.
When the time comes for _S_ to decommit _Ph_ ’s contribution to the nonce on
behalf of _F_ Com, rather that decommitting the value of _Rh_ that was committed
by _Ph_ in step 6 of _π_ ECDSA, _S_ instead computes




 sk [..] =




- 
**a** [v] _i,h_ [+]
_i∈_ **C** _i∈_ **H**



sk _i_
_i∈_ **H**



samples ( _s, r_ [x] ) _←_ ECDSASign( _G,_ sk _, m_ ), reconstructs _R_ from the x-coordinate
_r_ [x], computes _Rh_ [..] = _R −_ _Rk_


_k∈_ **P** [-] _[h]_

and then decommits this value of _Rh_ on behalf of _F_ Com. This embeds the value
of _r_ [x] that was sampled by ECDSASign into the protocol output, if the parties do
not deviate from the protocol. Note that the distribution of _r_ [x] has not changed:
in both _H_ 5 and _H_ 4 it is uniform.
Next, if the consistency checks (specified in step 15 of _S_ ECDSA) pass, then _S_
uses its knowledge of the corrupt parties’ inputs and outputs from _F_ RVOLE to
predict the values of _ui_ and _wi_ that all of the parties apart from _Ph_ would use,
if no parties cheated. We will denote the _sum_ of these predicted values as ˆ _u_
and ˆ _w_ respectively. These values depend upon _ϕi_ for _i ∈_ **C**, which might have
been used inconsistently in interactions with the different honest parties, if the
corrupt parties have misbehaved. _S_ defines the true value of _ϕi_ to be the value
implied by the interaction between _Pi_ and _Ph_ . Note that _ϕi −_ _**ψ**_ _i,h −_ _**χ**_ _i,h_ = 0
by definition, which implies that there is no discrepancy between the values _Ph_
computes if the corrupt parties follow the protocol and the values it computes
if they misbehave, conditioned on the fact that the consistency check passes.
If we let _δj_ [u] [for] _[ j][ ∈]_ **[H]** _[ \ {][h][}]_ [ represent the sum of the terms comprising] _[ u][j]_
that arise from interactions between the honest _Pj_ and the other honest parties,
and likewise let _δj_ [v] [represent the sum of the honestly-derived terms comprising]
_vj_, then we have




   _δj_ [u] [=] _[ r][j]_ _[·][ ϕ][j]_ [+]



( **c** [u] _j,k_ [+] **[ d]** _j,k_ [u] [)] for _j ∈_ **H**
_k∈_ **H** _\{j}_




   _δj_ [u] [=][ sk] _[j]_ _[·][ ϕ][j]_ [+]







( **c** [v] _j,k_ [+] **[ d]** _j,k_ [v] [)] for _j ∈_ **H**
_k∈_ **H** _\{j}_











 _u_ ˆ [..] =


_i∈_ **C**



��
 **a** [u] _i,h_ _[·]_




      _ϕk_ + _**ψ**_ _h,i_ + **c** [u] _i,h_ [+] **[ d]** _i,h_ [u]
_k∈_ **P** [-] _[h]_




 +


_j∈_ **H** _\{h}_








  _δj_ [u] [+] _[ r][j]_ _[·]_







_ϕi_
_i∈_ **C**



35














 _v_ ˆ [..] =


_i∈_ **C**



��
 **a** [v] _i,h_ _[·]_




      _ϕk_ + _**ψ**_ _h,i_ + **c** [v] _i,h_ [+] **[ d]** _i,h_ [v]
_k∈_ **P** [-] _[h]_




 +








  _δj_ [v] [+][ sk] _[j]_ _[·]_







_j∈_ **H** _\{h}_




   _w_ ˆ [..] = SHA2( _m_ ) _·_



_ϕi_
_i∈_ **C**



_ϕk_ + _r_ [x] _·_ ˆ _v_

_k∈_ **P** [-] _[h]_



Note that because **c** [u], **d** [u], **c** [v], and **d** [v] are uniformly sampled subject to constraints upon their component-wise sums, _δj_ [u] [and] _[ δ]_ _j_ [v] [are uniform when considered]
indepently of the view of _Ph_ . Note also that when the consistency check passes
for _Ph_, we can be sure that **a** [v] _i,h_ _[·][ G]_ [ =] **[ pk]** _i,h_ [for every] _[ i][ ∈]_ **[C]** [, which implies]
that sk _· G_ = pk. By the same argument as we made in the context of _H_ 3,
these constraints imply that the output of the protocol in _H_ 4 is a valid ECDSA
signature on _m_ under pk and _R_ when all parties follow the protocol.
In _H_ 5, _S_ samples _uh ←_ Z _q_ and _δj_ [u] _[←]_ [Z] _[q]_ [ and] _[ δ]_ _j_ [v] _[←]_ [Z] _[q]_ [ for] _[ j][ ∈]_ **[H]** _[ \ {][h][}]_
uniformly, calculates ˆ _u_ and ˆ _w_ as defined above, and then computes




   _wh_ [..] = _s · uh_ +


_k∈_ **P** [-] _[h]_




- _s ·_ ˆ _uk −_ _w_ ˆ _k_



This embeds the value of _s_ that was sampled by ECDSASign into the protocol
output, if the parties do not deviate from the protocol. In both hybrids _uj_ and
_wj_ for _j ∈_ **H** are all uniformly distributed subject to the fact that _s_ is the single
valid ECDSA signature on _m_ that exists under pk and _R_ when no party deviates
(and the honest parties have messages with identical images under SHA2). If
the corrupt parties _do_ deviate then the offsets they induce upon the output
satisfy the same algebraic relationship with the embedded value of _s_ in _H_ 5 as
they do with the hypothetical value of _s_ that would occur if they did not cheat
in _H_ 4. Thus _H_ 5 = _H_ 4.



**Hybrid** _H_ 6 **.** This final hybrid differs from _H_ 5 in the following way: _S_ no longer
acts on behalf of any honest parties, nor does it use ECDSAGen or ECDSASign
internally to sample signatures. Instead, _S_ ECDSA _[A]_ [(] _[G][, n, t]_ [) is fully implemented]

in _H_ 6 (that is, _S_ = _S_ ECDSA _[A]_ [(] _[G][, n, t]_ [)), and the experiment now incorporates]



in _H_ 6 (that is, _S_ = _S_ ECDSA _[A]_ [(] _[G][, n, t]_ [)), and the experiment now incorporates]

_F_ ECDSA( _G, n, t_ ). The honest parties run dummy-party code as is standard for
ideal-world experiements in the UC model, and _S_ ECDSA _[A]_ [(] _[G][, n, t]_ [) speaks to] _[ F]_ ECDSA

on behalf of corrupt parties.
The differences between _H_ 6 and _H_ 5 are purely syntactical, which is to say
that _H_ 5 = _H_ 6. Notice that in _H_ 5, _S_ did not require knowledge of _rh_ or sk _h_
in order to simulate, except insofar as sk _h_ determined sk. Moreover, because
sk _k_ for _k ∈_ **P** were computed by adding a uniform secret-sharing of zero _ζk_ to
the interpolated Shamir-shares lagrange( **P** _, k,_ 0) _· p_ ( _k_ ) of the secret key, sk _k_ for
_k ∈_ **P** were uniform subject to

     


sk _k · G_ = pk
_k∈_ **P**



36


In _H_ 6, at initialization time, _S_ invokes _F_ ECDSA( _G, n, t_ ) on behalf of the corrupt
parties, and learns pk but _not_ the discrete logarithm of pk. At signing time, it
samples sk _j_ for _j ∈_ **H** _\ {h}_ uniformly, and computes pk _h_ such that the above
equation holds. _S_ waits to invoke _F_ ECDSA on behalf of the corrupt parties until
after _F_ ECDSA is invoked by the very last honest party _Ph_, and uses _mh_ (the
message on which a signature was requested by _Ph_ ) on the corrupt parties’
behalves. If _S_ receives ( _s, r_ [x] ) from _F_ ECDSA on the corrupted parties’ behalves,
then it embeds these values into the protocol just as it did in _H_ 5. If it receives
a failure message from _F_ ECDSA, then it samples ( _s, r_ [x] ) uniformly amd embeds
them, just as it did in _H_ 5. Since the failure conditions are identical, pk _j_ for _j ∈_ **H**
are identically distributed, the signature values are identically distributed, and
the embedding of the signature is otherwise performed identically in the two
hybrids, _H_ 6 = _H_ 5.


We now have



_G ←_ GrpGen(1 _[λ]_ )









_λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _,_
_t∈_ [2 _,n_ ] _, z∈{_ 0 _,_ 1 _}_ _[∗]_



_H_ 6 =











Ideal _F_ ECDSA( _G,n,t_ ) _,_
_S_ _[A]_ [(] _[G][,n,t]_ [)] _[,]_



ECDSA( _G,n,t_ ) _,_ ( _λ, z_ ) :

ECDSA _[A]_ [(] _[G][,n,t]_ [)] _[,][Z]_



and by transitivity we also have



_G ←_ GrpGen(1 _[λ]_ )









_λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _,_
_t∈_ [2 _,n_ ] _, z∈{_ 0 _,_ 1 _}_ _[∗]_



_H_ 6 _≈_ s _H_ 0 =











Real _π_ ECDSA( _G,n,t_ ) _,_ ( _λ, z_ ) :
_A,Z_



where the total statistical distance between _H_ 6 and _H_ 0 is upper-bounded by
_ν_ ( _λ_ ) _·_ ( _ν_ ( _λ_ ) + _µ_ ( _λ_ )) _/q_, such that _ν_ and _µ_ are polynomials and _q_ is exponential
in _λ_ . We can conclude that theorem 4.1 holds.

## **5 Random Vector OLE from Random OT**


In section 3.1, we introduce the random VOLE functionality _F_ RVOLE and here
we describe a protocol to realize it.
Recall that Vector OLE is a one-sided vectorization of Oblivious Linear Evaluation, i.e. the secure computation of additive shares of a product. This is in
contrast to two-sided vectorization, which is sometimes referred to as _Batch_ .
The term _VOLE_ was coined by Applebaum et al. [ADI [+] 17]; protocols realizing OLE, VOLE, etc. have traded under many names, including simply _secure_
_multiplication_ or _multiplicative-to-additive conversion_ . A large and diverse set
of approaches for constructing such protocols is available, and most variants of
the functionality can be realized via most approaches.
Of particular note are folkloric approaches based on additively homomorphic encryption. Such approaches are implicitly used in many other
threshold ECDSA protocols that do not make explicit use of an OLE functionality. For example, Lindell [Lin17], Lindell and Nof [LN18], Gennarro


37


and Goldfeder [GG18], and Canetti et al. [CGG [+] 20] all implicitly construct
OLE protocols [8] using Paillier’s encryption scheme [Pai99]. Castagnos et
al. [CCL [+] 20, CCL [+] 23] make similar use of homomorphic encryption from class
groups [CL15]. It is also known how to construct VOLE from code-theoretic assumptions [ADI [+] 17, CRR21] and lattice assumptions [dJV21, BDM22], and
in the amortized setting the celebrated _silent_ random VOLE protocol family [BCGI18, BCG [+] 19, SGRR19, YWL [+] 20] has bandwidth costs almost independent of the vector length.
It should be stressed that it is possible to realize _F_ RVOLE using _any_ of these
techniques, and therefore the security of our threshold ECDSA protocol can be
founded on _any_ of the above assumptions while achieving a wide variety of potential performance tradeoffs. However, we do make a specific recommendation
that we believe leads to concretely efficient results in many use-cases.
Our VOLE protocol ultimately derives from one of the oldest OLE techniques, Gilboa’s OT-based multiplication protocol [Gil99], which uses a simple
schoolbook technique to destructure a multiplication in an arbitrary field of
size _q_ into _|q|_ -many one-bit multiplications, which are performed using oblivious
transfer. Gilboa’s protocol is secure only against semi-honest adversaries. Keller
et al. [KOS16] implicitly constructed a version with malicious security as a component in a protocol for generating Beaver triples. Two years later, Doerner et
al. [DKLs18] explicitly constructed a malicious-secure variant of Gilboa’s OLE
protocol. To our knowledge, this was the first two-message maliciously secure
OLE protocol. In a follow-up work, Doerner et al. [DKLs19] presented batched
version of their protocol with somewhat reduced bandwidth requirements, at
the cost of an additional round. Later, Haitner et al. [HMRT22] made another
moderate reduction in the bandwidth cost of this technique, again requiring
three rounds, but only realizing a weakened functionality that does not ensure
correct outputs are produced in the event that the protocol completes without
an abort.
In this work, we revisit and improve Doerner et al.’s malicious OLE technique. We construct a (random) VOLE with two rounds, which has concretely
lower bandwidth requirements than either their original or their batched construction, and also lower bandwidth requirements than the protocol of Haitner
et al. under some parameterizations, even though it realizes a stronger functionality in fewer rounds. As with prior iterations of this idea, our protocol is based
upon vectors of OT instances, which we model using an OT-extension functionality (although this can be realized using a vector of normal OT functionalities,
if desired). We choose to base our scheme upon an _endemic_ OT-extension functionality [MR19]; that is, upon vectors of OT instances wherein the adversary
is always allowed to determine the outputs of any corrupt party. This is the
weakest well-defined OT functionality, and all other varieties of OT trivially
imply it. The specific functionality is as follows:


8Though not necessarily ones that achieve security independently of the context in which
they are embedded.


38


**Functionality 5.1.** _F_ EOTE(X _, ℓ_ OT) **: Endemic OT Extension**

This functionality interacts with two active participants, _P_ A and _P_ B, who
we refer to as Alice and Bob, and with the ideal adversary _S_ .


**OT Extension:** On receiving (choose _,_ sid _,_ _**β**_ ) from Bob, if sid is fresh,
and _**β**_ _∈{_ 0 _,_ 1 _}_ _[ℓ]_ [OT], then:


 - If Alice is corrupt, then send (bob-chosen _,_ sid) to _S_ and wait for
(alice-messages _,_ sid _,_ _**α**_ [0] _,_ _**α**_ [1] ) in response such that _**α**_ [0] _∈_ X _[ℓ]_ [OT] and
_**α**_ [1] _∈_ X _[ℓ]_ [OT]


 - If Alice is corrupt, then wait for (bob-message _,_ sid _,_ _**γ**_ ) from _S_ such that
_**γ**_ _∈_ X _[ℓ]_ [OT], and then for _i ∈_ [ _ℓ_ OT] let _**α**_ _**[β]**_ _i_ _[i]_ ..= _**γ**_ and sample _**α**_ 1 _i_ _−_ _**β**_ _i_ _←_ X.


 - If either party is corrupt and _S_ sends (abort _,_ sid), then forward this
message to both parties and perform no further instructions related to
the session with ID sid.


 - If neither party is corrupt, then sample _**α**_ [0] _←_ X _[ℓ]_ [OT] and _**α**_ [1] _←_ X _[ℓ]_ [OT] .


Finally send (choice-made _,_ sid _,_ _**α**_ [0] _,_ _**α**_ [1] ) to Alice and (chosen _,_ sid _,_ _**γ**_ ) to
Bob.


We suggest to realize the foregoing functionality via the recent SoftSpoken
random OT-extension protocol of Roy [Roy22], because it requires only one
round in the Random Oracle model (under a simple modification that we will
describe in section 5.1), performs well in the non-amortized setting given a fast
one-time setup procedure, and assumes only ideal OT. Most other OT and
OT-extension protocols are also suitable, and in particular we expect _silent_
OT-extension [BCG [+] 19] to be the most efficient option when a large number
of signatures must be generated at once. Next, we give our protocol. Since it
derives strongly from Doerner et al. [DKLs18, DKLs19], the proof of security
that we present in section 6 is inspired by theirs.


**Protocol 5.2.** _π_ RVOLE( _q, ℓ_ ) **: OT-Based Random Vector OLE**


This protocol is parameterized by the vector length _ℓ_ and modulus _q_ of
the group Z _q_ over which multiplication is to be performed. Let _κ_ = _|q|_
and for convenience let _ξ_ = _κ_ + 2 _λ_ s and _ρ_ = _⌈κ/λ_ c _⌉_ . This protocol makes
use of a public _gadget vector_ **g** _←_ Z _[ξ]_ _q_ [,] _[a]_ [ and it invokes the] _[ F]_ EOTE [(][Z] _q_ _[ℓ]_ [+] _[ρ]_ _, ξ_ )
functionality and the non-programmable global random oracle ROX, which
has a paramatric range specified by its subscript.


**Sampling:**


1. When Bob receives (sample _,_ sid) from the environment, where sid is a
fresh session ID, Bob samples a set of uniform OT choice bits _**β**_ _←_
_{_ 0 _,_ 1 _}_ _[ξ]_ and calculates his random “input” _b_ [..] = _⟨_ **g** _,_ _**β**_ _⟩_ and then he sends


39


(choose _,_ sid _,_ _**β**_ ) to _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ), and outputs (sample _,_ sid _, b_ ) to the
environment.

         2. Upon receiving choice-made _,_ sid _,_ _**α**_ [0] _,_ _**α**_ [1][�] from _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ), Alice
outputs (ready _,_ sid) to the environment.


**Multiplication:**


3. When Alice has received both (� multiply _,_ sid _,_ **a** ) from the environment
and choice-made _,_ sid _,_ _**α**_ [0] _,_ _**α**_ [1][�] from _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ), _[b]_ she computes her
output share, samples a set of check values, derandomizes her OT messages using her inputs as correlations, calculates a challenge via the
Fiat-Shamir heuristic, and compresses her response via the random oracle













**c** [..] =



 
 _[−]_



**g** _j ·_ _**α**_ [0] _j,i_
_j∈_ [ _ξ_ ]



 _j_ _j,i_ 

_j∈_ [ _ξ_ ]

_i∈_ [ _ℓ_ ]
**ˆa** _←_ Z _[ρ]_ _q_



��   **˜a** [..] = _**α**_ [0] _j,i_ _[−]_ _**[α]**_ _j,i_ [1] [+] **[ a]** _[i]_




  -   _i∈_ [ _ℓ_ ] _[∥]_ _**α**_ [0] _j,ℓ_ + _k_ _[−]_ _**[α]**_ _j,ℓ_ [1] + _k_ [+] **[ ˆa]** _[i]_



_k∈_ [ _ρ_ ]







_j∈_ [ _ξ_ ]
_**θ**_ [..] = ROZ _ℓq×ρ_ (sid _,_ **˜a** )













_**η**_ [..] =




  **[ˆa]** _[k]_ [ +]




_k∈_ [ _ρ_ ]








_**θ**_ _i,k ·_ **a** _i_
_i∈_ [ _ℓ_ ]



_**θ**_ _k,k ·_ _**α**_ [0] _j,i_
_i∈_ [ _ℓ_ ]














_k∈_ [ _ρ_ ]



_**µ**_ [..] =











 
_j,ℓ_ + _k_ [+]
 _**[α]**_ [0]



 _j,ℓ_ + _k_ _i∈_ [ _ℓ_ ] _j,i_  

_k∈_ [ _ρ_ ] _j∈_ [ _ξ_ ]

_µ_ [..] = RO _{_ 0 _,_ 1 _}_ 2 _λ_ c (sid _,_ _**µ**_ )



and after this, she sends (multiply _,_ sid _,_ **˜a** _,_ _**η**_ _, µ_ ) to Bob and outputs outputs (share _,_ sid _,_ **c** ) to the environment.


4. When Bob receives (multiply _,_ sid _,_ **˜a** _,_ _**η**_ _, µ_ ) from Alice and
(chosen _,_ sid _,_ _**γ**_ ) from _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ), Bob computes



_**θ**_ [..] = ROZ _ℓq×ρ_ (sid _,_ **˜a** )



�� _q_   **˙d** . [.] = _**γ**_ _j,i_ + _**β**_ _j ·_ **˜a** _j,i_







_i∈_ [ _ℓ_ ]



_j∈_ [ _ξ_ ]
��   **ˆd** . [.] = _**γ**_ _j,ℓ_ + _k_ + _**β**_ _j ·_ **˜a** _j,ℓ_ + _k_ _k∈_ [ _ρ_ ]



_k∈_ [ _ρ_ ]






_j∈_ [ _ξ_ ]



40


_**θ**_ _i,k ·_ **d** **[˙]** _j,i −_ _**β**_ _j ·_ _**η**_ _k_
_i∈_ [ _ℓ_ ]








_j∈_ [ _ξ_ ]



_**µ**_ _[′]_ [ ..] =
















 
**ˆd** _j,k_ +









_k∈_ [ _ρ_ ]



and checks whether _µ_ = RO _{_ 0 _,_ 1 _}_ 2 _λ_ c (sid _,_ _**µ**_ _[′]_ ). If this check fails _[c]_ then Bob
aborts. If it passes, then Bob computes








_i∈_ [ _ℓ_ ]



**d** [..] =















**g** _j ·_ **d** **[˙]** _j,i_
_j∈_ [ _ξ_ ]



and outputs (share _,_ sid _,_ **d** ) to the environment.


_a_ This vector can be sampled by Bob and reused, or it can be a CRS reused by _multiple_
Bobs in different instances of the protocol.
_b_ If _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ) aborts instead of delivering a choice-made message, then Alice
aborts to the environment.
_c_ Or if _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ) aborts instead of delivering a chosen message.


**Derandomizing our Random VOLE.** Finally, we note that it is trivial to
construct standard chosen-input VOLE using the random VOLE functionality
that the foregoing protocol realizes: Bob simply transmits to Alice the difference between his true input and _b_, and for each of Alice’s inputs, she adds the
product of this difference and her input to her corresponding output. This requires no additional rounds, and allows our performance improvements to be
applied to other protocols that use the DKLs OLE protocols, including Chen
et al.’s [CCD [+] 20] RSA modulus sampling protocol and Doerner et al.’s threshold BBS+ protocol [DKL [+] 23], in which context it saves more than half of the
bandwidth cost.


**5.1** **One-Message SoftSpokenOT in the ROM**


As previously mentioned, we must modify the SoftSpokenOT protocol in order
to achieve our round count target. The modification we make is well-explored
and does not alter the security analysis of the protocol in a significant way. It
requires the use of a non-programmable random oracle. An analogous technique
is used by the KOS OT-extension protocol [KOS15], and by our own VOLE
construction and its progenitors, and it was previously suggested to apply this
modification to SoftSpokenOT by Doerner et al. [DKL [+] 23]. In this subsection,
we describe SoftSpokenOT in terms of the notation of Keller et al. [KOS15],
who describe a version of SoftSpokenOT in a recent update to their work.
As written, SoftSpokenOT requires three rounds to create a batch of extensions, after the initial one-time setup is complete. These rounds comprise
a statistical check with the form of a sigma protocol: first the OT-extension
receiver commits, then the sender transmits a challenge, then the receiver responds. However, the protocol does not require rewinding to achieve secu

41


rity, and the simulator does not use this test to extract anything from the
receiver’s view. As a result, we can apply the Fiat-Shamir transform using a
non-programmable (and even non-observable) global random oracle, and the
protocol retains UC security. That is, in the notation of Keller et al., we compute ( _χ_ 1 _, . . ., χm_ ) _←_ $ H( **u** 1 _, . . .,_ **u** _κ_ ). This reduces the protocol to a single round
from receiver to sender (after the initial setup). Note that because the adversary
can attempt to find a convenient challenge by brute force under this optimization, each occurrence of the statistical parameter ( _s_ in the notation of Keller
et al.) in the original protocol must be replaced by the computational security
parameter ( _κ_ in the notation of Keller et al.).

## **6 Proof of Security for OT-Based VOLE**


In section 1, we stated the following security theorem for our protocol:


**Theorem 1.2** (Informal Random VOLE Security Theorem) **.** _In the F_ EOTE _-_
_hybrid non-programmable global random oracle model, π_ RVOLE( _q, ℓ_ ) _UC-realizes_
_F_ RVOLE( _q, ℓ_ ) _against a PPT malicious adversary that statically corrupts no more_
_than one party._


In this section, we give our security theorem formally, and provide a proof.



**Theorem 6.1** (Formal OT-Based Random VOLE Security Theorem) **.** _For ev-_
_ery malicious PPT adversary A that statically corrupts either P_ A _or P_ B _, there_
_exists a PPT simulator S_ RVOLE _[A]_ _[that uses][ A][ as a black box, such that for every]_
_PPT environment Z and every polynomial ν,_

  -  Real _π_ RVOLE( _q,ℓ_ ) _,A,Z_ ( _λ, z_ ) _λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _, t∈_ [2 _,n_ ] _,_
_q∈_ [2 _[ν]_ [(] _[λ]_ [)] ] : _q_ is prime _, ℓ∈_ [ _ν_ ( _λ_ )] _, z∈{_ 0 _,_ 1 _}_ _[∗]_




 -  _≈_ c Ideal _F_ RVOLE( _q,ℓ_ ) _,S_ RVOLE _A_ [(] _[q,ℓ]_ [)] _[,][Z]_ [ (] _[λ, z]_ [)]



_λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _, t∈_ [2 _,n_ ] _,_
_q∈_ [2 _[ν]_ [(] _[λ]_ [)] ] : _q_ is prime _, ℓ∈_ [ _ν_ ( _λ_ )] _, z∈{_ 0 _,_ 1 _}_ _[∗]_



_Proof._ Lemma 6.2 in section 6.1 asserts that there exists a simulator _S_ RVOLE-Alice
under which theorem 6.1 holds, conditioned on _A_ corrupting only _P_ A.
Lemma 6.11 in section 6.2 asserts the existence of _S_ RVOLE-Bob such that theorem 6.1 holds when _A_ corrupts only _P_ B. The conjunction of these statements
yields theorem 6.1.


**6.1** **Simulating Against Alice**


**Lemma 6.2** (OT-Based VOLE Security against Alice) **.** _For every malicious_
_PPT adversary A that statically corrupts_ only _P_ A _, there exists a simulator_
_S_ RVOLE _[A]_ -Alice _[that uses][ A][ as a black box, such that for every PPT environment][ Z]_


42


_and every polynomial ν,_

 -  Real _π_ RVOLE( _q,ℓ_ ) _,A,Z_ ( _λ, z_ ) _λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _, t∈_ [2 _,n_ ] _,_
_q∈_ [2 _[ν]_ [(] _[λ]_ [)] ] : _q_ is prime _, ℓ∈_ [ _ν_ ( _λ_ )] _, z∈{_ 0 _,_ 1 _}_ _[∗]_




 _≈_ c Ideal _F_ RVOLE( _q,ℓ_ ) _,S_ _A_




      

_A_

RVOLE-Alice [(] _[q,ℓ]_ [)] _[,][Z]_ [ (] _[λ, z]_ [)]



_λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _, t∈_ [2 _,n_ ] _,_
_q∈_ [2 _[ν]_ [(] _[λ]_ [)] ] : _q_ is prime _, ℓ∈_ [ _ν_ ( _λ_ )] _, z∈{_ 0 _,_ 1 _}_ _[∗]_



_Proof._ We begin by presenting _S_ RVOLE _[A]_ -Alice [, after which we prove the lemma via]

a sequence if hybrid experiments.



**Simulator 6.3.** _S_ RVOLE _[A]_ -Alice [(] _[q, ℓ]_ [)] **[: Random VOLE against Alice]**



This simulator is parameterized by the vector length _ℓ_ and modulus _q_ of the
group Z _q_ over which linear evaluation is to be performed. The simulator
has oracle access to the adversary _A_ that statically corrupts _P_ A (i.e. the
party playing Alice) _only_, and emulates for it an instance of the protocol
_π_ RVOLE( _q, ℓ_ ) involving the parties _P_ A and _P_ B. The simulator forwards all
messages from its own environment _Z_ to _A_, and vice versa. _S_ RVOLE _[A]_ -Alice [(] _[q, ℓ]_ [)]

interacts with the ideal functionality _F_ RVOLE( _q, ℓ_ ) on behalf of _P_ A, and in
the exeriment that it emulates for _A_, it interacts with _A_ and _P_ A on behalf
of _P_ B and on behalf of the ideal oracle _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ). As in _π_ RVOLE( _q, ℓ_ ),
let _κ_ = _|q|_ and _ξ_ = _κ_ +2 _λ_ s and _ρ_ = _⌈κ/λ_ c _⌉_, let **g** _←_ Z _[ξ]_ _q_ [be a uniform gadget]
vector, and let ROX be a non-programmable global random oracle with a
paramatric range specified by its subscript.


**Sampling:**


1. On receiving (ready _,_ sid) from _F_ RVOLE( _q, ℓ_ ) on behalf of _P_ A, send
(bob-chosen _,_ sid) to _A_ on behalf of _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ) and wait
�to receive (alice-messages _,_ sid _,_ _**α**_ [0] _,_ _**α**_ [1] ) in response, then send
choice-made _,_ sid _,_ _**α**_ [0] _,_ _**α**_ [1][�] to _P_ A on behalf of _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ). If _A_ sends
abort instead of alice-messages, then send (abort _,_ sid) to _F_ RVOLE( _q, ℓ_ )
and perform no further instructions related to the session with ID sid.


**Multiplication:**


2. On receiving (multiply _,_ sid _,_ **˜a** _,_ _**η**_ _, µ_ ) from Alice, check the table of
queries that have been made to the global random oracle for a query
on a value _**µ**_ _∈_ Z _[ξ]_ _q_ _[×][ρ]_ such that _µ_ = RO _{_ 0 _,_ 1 _}_ 2 _λ_ c (sid _,_ _**µ**_ ). If there is not exactly one such value, then send (abort _,_ sid) to _F_ RVOLE( _q, ℓ_ ) and perform
no further instructions related to the session with ID sid. Otherwise,
continue to the next step.


3. Using the value _**µ**_ extracted in the previous step, compute two vectors
of offsets, relative to the expectation:


_**θ**_ [..] = ROZ _ℓq×ρ_ (sid _,_ **˜a** )


43












_k∈_ [ _ρ_ ]








_**δ**_ _[µ]_ [ ..] =


_**δ**_ _[η]_ [ ..] =























 
_j,ℓ_ + _k_ _[−]_
 _**[µ]**_ _[j,k][ −]_ _**[α]**_ [0]



_**θ**_ _i,k ·_ _**α**_ [0] _j,i_
_i∈_ [ _ℓ_ ]




_j∈_ [ _ξ_ ]












- - 
_**θ**_ _j,i ·_ _**α**_ [1] _j,i_ _[−]_ _**[α]**_ _j,i_ [0] [+] **[ ˜a]** _[j,i]_
_i∈_ [ _ℓ_ ]



_**α**_ [1] _j,ℓ_ + _k_ _[−]_ _**[α]**_ _j,ℓ_ [0] + _k_ [+] **[ ˜a]** _[j,ℓ]_ [+] _[k]_ _[−]_ _**[η]**_ _k_








 
_k∈_ [ _ρ_ ] _j∈_ [ _ξ_ ]




 +



Note that if Alice has behaved honestly, then _**δ**_ _[µ]_ and _**δ**_ _[η]_ will contain
only zeros. Sample _**β**_ _[∗]_ _←{_ 0 _,_ 1 _}_ _[ξ]_ and if

      
_**δ**_ _[µ]_ _j,k_ [=] _**[ β]**_ _[∗]_ _j_ _[·]_ _**[ δ]**_ _j,k_ _[η]_



_k∈_ [ _ρ_ ]
_j∈_ [ _ξ_ ]


then send (abort _,_ sid) to _F_ RVOLE( _q, ℓ_ ) and perform no further instructions related to the session with ID sid. Otherwise, continue to the next
step.


4. Find _j_ _[∗]_ _∈_ [ _ξ_ ] such that _**δ**_ _[η]_ _j,k_ [= 0 for every] _[ k][ ∈]_ [[] _[ρ]_ [], and let this index]
define Alice’s true input:




  -   **a** [..] = _**α**_ [1] _j_ _[∗]_ _,i_ _[−]_ _**[α]**_ _j_ [0] _[∗]_ _,i_ [+] **[ ˜a]** _[j][∗][,i]_



_i∈_ [ _ℓ_ ]



If there are multiple candidate values for _j_ _[∗]_, then choose the smallest one. If there exists no _j_ _[∗]_ satisfying these conditions then send
(abort _,_ sid) to _F_ RVOLE( _q, ℓ_ ) and perform no further instructions related
to the session with ID sid. Otherwise, continue to the next step.


5. Compute Alice’s output, and the offset induced into Bob’s output by
any “undetected” cheats, and subtract the latter from the former














  _[−]_








_i∈_ [ _ℓ_ ]



**c** [..] =


_**δ**_ _[d]_ [ ..] =



**g** _j ·_ _**β**_ _[∗]_ _j_ _[·]_ [ (] _**[α]**_ _j,i_ [1] _[−]_ _**[α]**_ _j,i_ [0] [+] **[ ˜a]** _[j,i]_ _[−]_ **[a]** _[i]_ [)]
_j∈_ [ _ξ_ ]











**g** _j ·_ _**α**_ [0] _j,i_
_j∈_ [ _ξ_ ]








  -   **c** _[∗]_ [..] = **c** _i −_ _**δ**_ _[d]_ _i_

_i∈_ [ _ℓ_ ]




_i∈_ [ _ℓ_ ]



and then send



44


  - (multiply _,_ sid _,_ **a** ) to _F_ RVOLE( _q, ℓ_ ) on behalf of Alice.

  - (alice-share _,_ sid _,_ **c** _[∗]_ ) directly to _F_ RVOLE( _q, ℓ_ ).


Our sequence of hybrid experiments begins with the real world

     -     _H_ 0 = Real _π_ RVOLE( _q,ℓ_ ) _,A,Z_ ( _λ, z_ ) _λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _, t∈_ [2 _,n_ ] _,_
_q∈_ [2 _[ν]_ [(] _[λ]_ [)] ] : _q_ is prime _, ℓ∈_ [ _ν_ ( _λ_ )] _, z∈{_ 0 _,_ 1 _}_ _[∗]_


and proceeds by gradually replacing the code of the real _P_ B with elements of
the simulator until _S_ RVOLE _[A]_ -Alice [is fully implemented and the experiment is the]

ideal one.


**Hybrid** _H_ 1 **.** This hybrid experiment replaces the honest party _P_ B and the
ideal functionality _F_ EOTE in _H_ 0 with a single simulator machine _S_ that runs
their code and interacts with the adversary, environment, and corrupt party
_P_ A on their behalf. Since _S_ interacts with the adversarial entities on behalf of
_F_ EOTE it learns any values that _F_ EOTE receives or that are defined by its internal
state. Furthermore, _S_ is permitted to observe queries to the random oracle, but
not to program the output. These changes are purely syntactical, and so it must
be the case that _H_ 1 = _H_ 0.


**Hybrid** _H_ 2 **.** In this hybrid, _S_ aborts on behalf of Bob upon receiving
(multiply _,_ sid _,_ **˜a** _,_ _**η**_ _, µ_ ) from Alice if there does not exist exactly one value
_**µ**_ _∈_ Z _[ξ]_ _q_ _[×][ρ]_ such that _µ_ = RO _{_ 0 _,_ 1 _}_ 2 _λ_ c (sid _,_ _**µ**_ ). This can be determined efficiently
by scanning the table of random oracle queries.


We claim that _H_ 2 _≈_ c _H_ 1. Consider the two distinguishing cases: first, that
no query of the form Z _[ξ]_ _q_ _[×][ρ]_ has ever yielded the output _µ_, and second, that
more than one has. In the first case, we know _S_ will query a value that has
never before been queried, per Bob’s code in step 4 of the protocol, and so
the probabilty that _µ_ = RO _{_ 0 _,_ 1 _}_ 2 _λ_ c (sid _,_ _**µ**_ _[′]_ ) is exactly 2 _[−]_ [2] _[λ]_ [c] . The second case
implies that the environment has found a collision in the random oracle. The
probability that a collision occurs within the first _Q_ queried values is the sum
of the probabilities that each new attempt produces a collision; specifically, the
probability of a collision is within the first _Q_ queried values is


0 + 2 _[−]_ [2] _[λ]_ [c] + 2 _·_ 2 _[−]_ [2] _[λ]_ [c] + 3 _·_ 2 _[−]_ [2] _[λ]_ [c] + _. . ._ + ( _Q −_ 1) _·_ 2 _[−]_ [2] _[λ]_ [c] _≤_ _Q_ [2] _·_ 2 _[−]_ [2] _[λ]_ [c] _[−]_ [1]


and by union bound, we have a total distinguishing probability no greater than
_Q_ [2] _·_ 2 _[−]_ [2] _[λ]_ [c] _[−]_ [1] + 2 _[−]_ [2] _[λ]_ [c] . Since the environment can make only polynomially many
random oracle queries, this probability is negligible in _λ_ c.


**Hybrid** _H_ 3 **.** In this hybrid, _S_ does not condition an abort on whether _µ_ =
RO _{_ 0 _,_ 1 _}_ 2 _λ_ c (sid _,_ _**µ**_ _[′]_ ) as specified in step 4 of the protocol. Instead, _S_ computes
implements step 3 of _S_ RVOLE-Alice, but uses Bob’s actual choice bits _**β**_ instead of


45


_**β**_ _[∗]_ . More precisely, in _H_ 3, _S_ computes



_**θ**_ [..] = ROZ _ℓq×ρ_ (sid _,_ **˜a** )













_k∈_ [ _ρ_ ]








_**δ**_ _[µ]_ [ ..] =


_**δ**_ _[η]_ [ ..] =
























   _j,ℓ_ + _k_ _[−]_
 _**[µ]**_ _[j,k][ −]_ _**[α]**_ [0]



_**θ**_ _i,k ·_ _**α**_ [0] _j,i_
_i∈_ [ _ℓ_ ]









- - 
_**θ**_ _j,i ·_ _**α**_ [1] _j,i_ _[−]_ _**[α]**_ _j,i_ [0] [+] **[ ˜a]** _[j,i]_
_i∈_ [ _ℓ_ ]




_j∈_ [ _ξ_ ]






_**α**_ [1] _j,ℓ_ + _k_ _[−]_ _**[α]**_ _j,ℓ_ [0] + _k_ [+] **[ ˜a]** _[j,ℓ]_ [+] _[k]_ _[−]_ _**[η]**_ _k_









_k∈_ [ _ρ_ ]




 +




_j∈_ [ _ξ_ ]



and then aborts if 

_k∈_ [ _ρ_ ]
_j∈_ [ _ξ_ ]



_**δ**_ _[µ]_ _j,k_ [=] _**[ β]**_ _j_ _[·]_ _**[ δ]**_ _j,k_ _[η]_



We claim that _H_ 3 _≈_ s _H_ 2. Observe that in _H_ 2, the exeriment aborts with
certainty if there is not exactly one correctly formatted preimage _**µ**_ of _µ_ under
the random oracle. Because _**µ**_ is the only (correctly formatted) preimage of _µ_,
we have Pr _µ_ = RO _{_ 0 _,_ 1 _}_ 2 _λ_ c (sid _,_ _**µ**_ _[′]_ ) : _**µ**_ _̸_ = _**µ**_ _[′]_ [�] = 2 _[−]_ [2] _[λ]_ [c]

or, in other words, conditioned on _**µ**_ being well-defined, _H_ 2 aborts with overwhelming probability if _**µ**_ _̸_ = _**µ**_ _[′]_, and if _**µ**_ = _**µ**_ _[′]_ then it does not abort. We
will show that _H_ 3 aborts if and only if _**µ**_ _̸_ = _**µ**_ _[′]_, again conditioned on _**µ**_ being
well-defined.
We can subtract
  
        -  













 
_j,ℓ_ + _k_ [+]
 _**[α]**_ [0]









_k∈_ [ _ρ_ ]











_**θ**_ _i,k ·_ _**α**_ [0] _j,i_
_i∈_ [ _ℓ_ ]




_j∈_ [ _ξ_ ]







from both sides of _**µ**_ _̸_ = _**µ**_ _[′]_ to yield










 
_j,ℓ_ + _k_ _[−]_
 _**[µ]**_ _[j,k][ −]_ _**[α]**_ [0]




_j∈_ [ _ξ_ ]







_j∈_ [ _ξ_ ]







_**θ**_ _i,k ·_ _**α**_ [0] _j,i_
_i∈_ [ _ℓ_ ]











_**θ**_ _i,k ·_ _**α**_ [0] _j,i_
_i∈_ [ _ℓ_ ]









_k∈_ [ _ρ_ ]







_k∈_ [ _ρ_ ]



=



 
_j,k_ _[−]_ _**[α]**_ _j,ℓ_ [0] + _k_ _[−]_
 _**[µ]**_ _[′]_




_j∈_ [ _ξ_ ]



and then substituting in the definitions of _**µ**_ _[′]_ and _**δ**_ _[µ]_ we have








_j∈_ [ _ξ_ ]




- 
_**θ**_ _i,k ·_ **d** **[˙]** _j,i −_ _**α**_ [0] _j,ℓ_ + _k_ _[−]_ _**[β]**_ _j_ _[·]_ _**[ η]**_ _k_ _[−]_
_i∈_ [ _ℓ_ ] _i∈_ [ _ℓ_ ]



_**θ**_ _i,k ·_ _**α**_ [0] _j,i_
_i∈_ [ _ℓ_ ]



_**δ**_ _[µ]_ =
















 
**ˆd** _j,k_ +









_k∈_ [ _ρ_ ]



46


after which, substituting the definitions of **d** **[˙]** and **d** **[ˆ]** and then the definition of _**γ**_
and simplifying yields




 +



_**θ**_ _i,k ·_ ( _**α**_ [1] _j,i_ _[−]_ _**[α]**_ _j,i_ [0] [+] **[ ˜a]** _[j,i]_ [)]
_i∈_ [ _ℓ_ ]
















_**δ**_ _[µ]_ =






_**β**_ _j ·_













_**α**_ [1] _j,ℓ_ + _k_ _[−]_ _**[α]**_ _j,ℓ_ [0] + _k_ [+] **[ ˜a]** _[j,ℓ]_ [+] _[k]_ _[−]_ _**[η]**_ _k_




_k∈_ [ _ρ_ ]








_j∈_ [ _ξ_ ]



which is equivalent to 

_k∈_ [ _ρ_ ]
_j∈_ [ _ξ_ ]



_**δ**_ _[µ]_ _j,k_ [=] _**[ β]**_ _j_ _[·]_ _**[ δ]**_ _j,k_ _[η]_



and it follows from this that _H_ 3 _≈_ s _H_ 2 with statistical distance 2 _[−]_ [2] _[λ]_ [c] .


**Hybrid** _H_ 4 **.** In this hybrid, _S_ implements step 4 of _S_ RVOLE-Alice. That is, it
finds the smallest _j_ _[∗]_ _∈_ [ _ξ_ ] such that _**δ**_ _[η]_ _j,k_ [= 0 for every] _[ k][ ∈]_ [[] _[ρ]_ [], and defines]




           -            **a** [..] = _**α**_ [1] _j_ _[∗]_ _,i_ _[−]_ _**[α]**_ _j_ [0] _[∗]_ _,i_ [+] **[ ˜a]** _[j][∗][,i]_


if such a _j_ _[∗]_ exists, or aborts if no such _j_ _[∗]_ exists.



_i∈_ [ _ℓ_ ]



We claim that _H_ 4 _≈_ s _H_ 3. Consider an adversary that distinguishes the two
hybrids; specifically, consider an adversary that fixes _**δ**_ _[η]_ such that for every
_j ∈_ [ _ξ_ ] there exists some _k ∈_ [ _ρ_ ] such that _**δ**_ _[η]_ _j,k_ [= 0. If this adversary avoids an]
abort in _H_ 3, then 
_**δ**_ _[µ]_ _j,k_ [=] _**[ β]**_ _j_ _[·]_ _**[ δ]**_ _j,k_ _[η]_

_k∈_ [ _ρ_ ]
_j∈_ [ _ξ_ ]


or, in other words, that it has exactly guessed the entire vector _**β**_ of Bob’s choice
bits. Notice that Bob’s output _b_ is the _only_ value that depends upon _**β**_ in the
view of the environment at the point that _**δ**_ _[η]_ and _**δ**_ _[η]_ are fixed.
We now construct an alternative experiment. In our alternative experiment
behaves exactly like _H_ 4, except that _S_ samples _b ←_ Z _q_ uniformly rather than
deriving it from _**β**_, and our alternative experiment terminates when Bob receives
(multiply _,_ sid _,_ **˜a** _,_ _**η**_ _, µ_ ) from Alice, fixing _**δ**_ _[η]_ and _**δ**_ _[η]_ . We make a sequence of
claims:


**Claim 6.4.** _In our alternative experiment,_






_≤_ 2 _−ξ_




��������





_**δ**_ _[η]_ _j,∗_ [=] _[ {]_ [0] _[}][ρ]_
_j∈_ [ _ξ_ ]







Pr





 
_k∈_ [ _ρ_ ]
_j∈_ [ _ξ_ ]



_**δ**_ _[µ]_ _j,k_ [=] _**[ β]**_ _j_ _[·]_ _**[ δ]**_ _j,k_ _[η]_



Our first claim holds because _**β**_ is perfectly information-theoretically hidden
from the adversary in our alternative experiment: no value derived from it
enters the adversary’s view. When _**δ**_ _[η]_ contains no zero values, the adversary’s
best strategy for avoiding the abort condition is to guess.


47


**Claim 6.5.** _At the moment of our alternative experiment’s termination, the_
_statistical difference between the adversary’s view in our alternative experiment_
_and its view at the equivalent point in H_ 4 _is at most_ 2 _[−][λ]_ [s] _._


Our second claim holds because the only distinction between the two is the
way in which _b_ is calculated. In our alternative experiment it is uniform and
independent of all other values, whereas in _H_ 4 we have _b_ = _⟨_ **g** _,_ _**β**_ _⟩_ and no other
values depend upon _**β**_ . Because (by construction) _κ < ξ_, we can apply part 2 of
proposition 1.1 of Impagliazzo and Naor [IN96] to conclude that the statistical
difference between the two experiments is at most 2 [(] _[κ][−][ξ]_ [)] _[/]_ [2] = 2 _[−][λ]_ [s] .


**Claim 6.6.** _In H_ 4 _,_






_≤_ 2 _−ξ_ + 2 _−λ_ s




��������





_**δ**_ _[η]_ _j,∗_ [=] _[ {]_ [0] _[}][ρ]_
_j∈_ [ _ξ_ ]







Pr





 
_k∈_ [ _ρ_ ]
_j∈_ [ _ξ_ ]



_**δ**_ _[µ]_ _j,k_ [=] _**[ β]**_ _j_ _[·]_ _**[ δ]**_ _j,k_ _[η]_



Our final claim holds by conjunction of claims 6.5 and 6.4, and it implies
that _H_ 4 _≈_ s _H_ 3 with statistical distance at most 2 _[−][ξ]_ + 2 _[−][λ]_ [s] .


**Hybrid** _H_ 5 **.** This hybrid changes the way in which _S_ computes an output for
Bob. In _H_ 4, Bob’s output **d** was calculated via his protocol code. In _H_ 5, if
no abort occurs, then _S_ uses the index _j_ _[∗]_ that was initially defined in _H_ 4 to
extract an ideal input for Alice




  -   **a** [..] = _**α**_ [1] _j_ _[∗]_ _,i_ _[−]_ _**[α]**_ _j_ [0] _[∗]_ _,i_ [+] **[ ˜a]** _[j][∗][,i]_ _i∈_ [ _ℓ_ ]



and in addition, _S_ calculates the output **c** that Alice will emit if she behaves
honestly, and uses this to compute the ideal output **d** _[∗]_ that Bob would emit
if Alice behaved honestly. _S_ then computes the vector _**δ**_ _[d]_ of additive offsets
induced into Bob’s outputs by Alice’s cheats, and applies them to Bob’s ideal
output in order to calculate his actual output **d**













**c** [..] =



 
 _[−]_



**g** _j ·_ _**α**_ [0] _j,i_
_j∈_ [ _ξ_ ]



 _j_ _j,i_ 

_j∈_ [ _ξ_ ]

_i∈_ [ _ℓ_ ]
**d** _[∗]_ [..] = _{b ·_ **a** _i −_ **c** _i}i∈_ [ _ℓ_ ]








_**δ**_ _[d]_ [ ..] =















**g** _j ·_ _**β**_ _j ·_ ( _**α**_ [1] _j,i_ _[−]_ _**[α]**_ _j,i_ [0] [+] **[ ˜a]** _[j,i]_ _[−]_ **[a]** _[i]_ [)]
_j∈_ [ _ξ_ ]




  -  **d** [..] = **d** _[∗]_ _i_ [+] _**[ δ]**_ _i_ _[d]_

_i∈_ [ _ℓ_ ]




_i∈_ [ _ℓ_ ]



This effectively implements step 5 of _S_ RVOLE-Alice, but using Bob’s actual choice
bits _**β**_ instead of _**β**_ _[∗]_ .


48


We claim that _H_ 5 and _H_ 4 are identically distributed. Observe that by
substituting the definitions of _**δ**_ _[d]_ and **d** _[∗]_ into the equation that defines **d** in
_H_ 5, we have














_i∈_ [ _ℓ_ ]



**d** =




   _[b][ ·]_ **[ a]** _[i][ −]_ **[c]** _[i]_ [ +]



**g** _j ·_ _**β**_ _j ·_ ( _**α**_ [1] _j,i_ _[−]_ _**[α]**_ _j,i_ [0] [+] **[ ˜a]** _[j,i]_ _[−]_ **[a]** _[i]_ [)]
_j∈_ [ _ξ_ ]



and since _b_ = _⟨_ **g** _,_ _**β**_ _⟩_ we can plug in the definition of **c** and simplify to arrive at















**g** _j ·_ _**α**_ [0] _j,i_
_j∈_ [ _ξ_ ]








_i∈_ [ _ℓ_ ]



**d** =




- 
**g** _j ·_ _**β**_ _j ·_ ( _**α**_ [1] _j,i_ _[−]_ _**[α]**_ _j,i_ [0] [+] **[ ˜a]** _[j,i]_ [) +]
_j∈_ [ _ξ_ ] _j∈_ [ _ξ_ ]



wherafter we can substitute _**γ**_ _j,i_ + ( _**β**_ _j −_ 1) _·_ _**α**_ [0] _j,i_ [=] _**[ β]**_ _j_ _[·]_ _**[ α]**_ _j,i_ [1] [, which follows from]
the code of _F_ EOTE, to yield












_i∈_ [ _ℓ_ ]
















_i∈_ [ _ℓ_ ]



**d** =





- - �

**g** _j ·_ _**β**_ _j ·_ **˜a** _j,i_ + _**γ**_ _j,i_



_j∈_ [ _ξ_ ]











**g** _j ·_ **d** **[˙]** _j,i_
_j∈_ [ _ξ_ ]



=



which is precisely the equation used to calculate Bob’s output in _H_ 4.


**Hybrid** _H_ 6 **.** This hybrid is identical to _H_ 5, except that in _H_ 6, _b ←_ Z _q_ is
sampled uniformly, rather than being computed as _b_ [..] = _⟨_ **g** _,_ _**β**_ _⟩_ . Note that while
_b_ is now independent of _**β**_, _S_ still aborts based upon _**β**_, and Bob’s output **d**
depends upon both.


We claim that _H_ 6 _≈_ c _H_ 5. Recall that in both, Alice’s true input is defined
to be - **a** [..] = _**α**_ [1] _j_ _[∗]_ _,i_ _[−]_ _**[α]**_ _j_ [0] _[∗]_ _,i_ [+] **[ ˜a]** _[j][∗][,i]_ _i∈_ [ _ℓ_ ]

where _j_ _[∗]_ _∈_ [ _ξ_ ] is the smallest number such that _**δ**_ _[η]_ _j,k_ [= 0 for every] _[ k][ ∈]_ [[] _[ρ]_ []. We]
now define some additional values:




  -   **ˆa** [..] = _**α**_ [1] _j_ _[∗]_ _,ℓ_ + _k_ _[−]_ _**[α]**_ _j_ [0] _[∗]_ _,ℓ_ + _k_ [+] **[ ˜a]** _[j][∗][,ℓ]_ [+] _[k]_



��   _**δ**_ _[a]_ [ ..] = _**α**_ [1] _j,i_ _[−]_ _**[α]**_ _j,i_ [0] [+] **[ ˜a]** _[j,i]_ _[−]_ **[a]** _[i]_







_k∈_ [ _ρ_ ]



_i∈_ [ _ℓ_ ]



_j∈_ [ _ξ_ ]



��   _**δ**_ _[a]_ [ˆ][ ..] = _**α**_ [1] _j,ℓ_ + _k_ _[−]_ _**[α]**_ _j,ℓ_ [0] + _k_ [+] **[ ˜a]** _[j,ℓ]_ [+] _[k]_ _[−]_ **[ˆa]** _[k]_






_j∈_ [ _ξ_ ]



_k∈_ [ _ρ_ ]



_**δ**_ _d_ ˙ ..= �� _**β**_ _j ·_ _**δ**_ _[a]_ [�]







_i∈_ [ _ℓ_ ]



_j∈_ [ _ξ_ ]
**∆** [..] = _{j ∈_ [ _ξ_ ] : _**δ**_ _[η]_ _j,∗_ [=] _[ {]_ [0] _[}][ρ][}]_



For clarity, **ˆa** is defined to be Alice’s true check vector, _**δ**_ _[a]_ and _**δ**_ _[a]_ [ˆ] are vectors
of the offsets by which Alice has deviated from her true input and check vector


49


respectively, and _**δ**_ _d_ ˙ is a vector of the offsets that her deviations induce into
Bob’s output. Notice that



_**δ**_ _[d]_ =















**g** _j ·_ _**δ**_ _dj,i_ ˙
_j∈_ [ _ξ_ ]








_i∈_ [ _ℓ_ ]



Finally, **∆** indexes all of the elements in _**β**_ that _might_ influence the probability
that the experiment aborts; an abort may also happen with certainty independent of these elements. We now make a sequence of claims, from which we will
construct our argument that _H_ 6 _≈_ c _H_ 5:

**Claim 6.7.** _If for some j ∈_ [ _ξ_ ] _there exists i ∈_ [ _ℓ_ ] _such that_ _**δ**_ _[a]_ _j,i_ [= 0] _[, then]_
Pr [ _j ∈_ **∆** ] _≥_ 1 _−_ _Q_ _·_ 2 _[−][λ]_ [c] _, where Q is the number of random oracle queries made_
_by the adversary._



Suppose _j ̸∈_ **∆** . This implies that _**δ**_ _[η]_ _j,∗_ [=] _[ {]_ [0] _[}][ρ]_ [, and for every] _[ k][ ∈]_ [[] _[ρ]_ [] we have]
 



_**α**_ [1] _j,ℓ_ + _k_ _[−]_ _**[α]**_ _j,ℓ_ [0] + _k_ [+] **[ ˜a]** _[j,ℓ]_ [+] _[k]_




 +









- - 
_**θ**_ _j,i ·_ _**α**_ [1] _j,i_ _[−]_ _**[α]**_ _j,i_ [0] [+] **[ ˜a]** _[j,i]_
_i∈_ [ _ℓ_ ]




















- - 
_**θ**_ _j∗,i ·_ _**α**_ [1] _j_ _[∗]_ _,i_ _[−]_ _**[α]**_ _j_ [0] _[∗]_ _,i_ [+] **[ ˜a]** _[j][∗][,i]_
_i∈_ [ _ℓ_ ]



_**α**_ [1] _j_ _[∗]_ _,ℓ_ + _k_ _[−]_ _**[α]**_ _j_ [0] _[∗]_ _,ℓ_ + _k_ [+] **[ ˜a]** _[j][∗][,ℓ]_ [+] _[k]_











=




 +



Recall that _**α**_ [0] and _**α**_ [1] are fixed and then the adversary computes _**θ**_ =
ROZ _ℓq×ρ_ (sid _,_ **˜a** ). For any given adversarial choice of **˜a**, the probability over the
coins of the random oracle that the above equality holds simultaneously for
every _k ∈_ [ _ρ_ ] is 1 _/q_ _[ρ]_ _≤_ 2 _[−][λ]_ [c] . If we let _Q_ be the total number of random oracle
queries made by the adversary over the course of the experinment, then the
claim follows.


**Claim 6.8.** _In H_ 5 _, if_ **a** _is well-defined, then the probability that the experiment_
_does not abort is at most_ 2 _[−|]_ **[∆]** _[|]_ _._

For every _j ∈_ **∆**, the experiment aborts if _**δ**_ _[µ]_ _j,∗_ [=] _[ {]_ _**[β]**_ _j_ _[·]_ _**[ δ]**_ _j,k_ _[η]_ _[}][k][∈]_ [[] _[ρ]_ []][, which]
happens with probability at least 1 _/_ 2. [9] Thus the probability of an abort is at
least 1 _−_ 2 _[−|]_ **[∆]** _[|]_ and taking the complement yields claim 6.8.


**Claim 6.9.** _The probability that H_ 6 _aborts and the probability that H_ 5 _aborts_
_have an absolute difference no greater than_ 2 _[−][λ]_ [s] _._


The above claim follows from the same argument as claim 6.5.


**Claim 6.10.** _If |_ **∆** _| ≤_ 2 _λ_ s _and neither hybrid aborts, then the statistical differ-_
_ence between H_ 6 _and H_ 5 _is upper-bounded by_ 2 _[−]_ [(] _[ξ][−][κ][−|]_ **[∆]** _[|]_ [)] _[/]_ [2] + _ξ · Q ·_ 2 _[−][λ]_ [c] _, where_
_Q is the number of random oracle queries made by the adversary._


9The experiment aborts with probability 1 if _**δ**_ _[µ]_ _j,∗_ [=] _**[ δ]**_ _[η]_ _j,∗_ [and] _**[ δ]**_ _j,_ _[µ]_ _∗_ [=] _[ {]_ [0] _[}][ρ]_ [.]


50


To aid our analysis of this claim, we will first develop an alternate view of
_H_ 6 and _H_ 5. Suppose that in _H_ 5, we write




- **g** _j ·_ _**β**_ _j_ and _b_ ∆¯ ..= 
_j∈_ **∆** _j∈_ [ _ξ_ ] _\_




 _b_ [∆] [..] =



**g** _j ·_ _**β**_ _j_ and _b_ [..] = _b_ [∆] + _b_ ∆¯
_j∈_ [ _ξ_ ] _\_ **∆**



which is, of course, only a syntactical change. Now in _H_ 6 we write

_b_ [∆] [..] =     - **g** _j ·_ _**β**_ _j_ and _b_ ∆¯ _←_ Z _q_ and _b_ [..] = _b_ [∆] + _b_ ∆¯

_j∈_ **∆**


and again, we have not changed the distribution of _H_ 6; _b_ remains uniform. Assuming _|_ **∆** _| < ξ −_ _κ_ = 2 _λ_ s, we can again apply part 2 of proposition 1.1 of
Impagliazzo and Naor [IN96] to conclude that the statistical difference between
_b_ [∆][¯] in _H_ 6 and _H_ 5 is at most 2 _[−]_ [(] _[ξ][−][κ][−|]_ **[∆]** _[|]_ [)] _[/]_ [2] .
It remains to show that _no variables_ in either experiment depend upon _**β**_ _j_
for _j ∈_ [ _ξ_ ] _\_ **∆**, except indirectly via _b_ . For every _j ∈_ [ _ξ_ ] _\_ **∆** we have by definition
that _**δ**_ _[η]_ _j,∗_ [=] _[ {]_ [0] _[}][ρ]_ [, which implies that] _**[ δ]**_ _[µ]_ _j,k_ [=] _**[ β]**_ _j_ _[·]_ _**[ δ]**_ _j,k_ _[η]_ [is satisfied (or not) for all]
_k ∈_ [ _ρ_ ] independently of the value of _**β**_ _j_ . Similarly, claim 6.7 implies that for
each _j ∈_ [ _ξ_ ] _\_ **∆**, we have Pr[ _**δ**_ _[a]_ _j,∗_ [=] _[ {]_ [0] _[}][ℓ]_ []] _[ ≤]_ _[Q][ ·]_ [ 2] _[−][λ]_ [c] [. Taking the compliment of]
the union bound over all _j ∈_ [ _ξ_ ] _\_ **∆**, we have






 _≥_ 1 _−_ _ξ · Q ·_ 2 _[−][λ]_ [c]



Pr





  _**δ**_ _[a]_ _j,∗_ [=] _[ {]_ [0] _[}][ℓ]_

_j∈_ [ _ξ_ ] _\_ **∆**



This implies that _**δ**_ _d_ ˙ and consequently _**δ**_ _d_ and are independent of _**β**_ _j_ for _j ∈_

[ _ξ_ ] _\_ **∆** with probability no less than 1 _−_ _ξ · Q ·_ 2 _[−][λ]_ [c] . If they are independent,
then the statistical distance between the two hybrids is at most 2 _[−]_ [(] _[ξ][−][κ][−|]_ **[∆]** _[|]_ [)] _[/]_ [2],
and if they are dependent, then we assume the two hybrids can be distinguished
with probability 1. Claim 6.10 follows.


Finally, we are ready to complete our argument that _H_ 6 _≈_ c _H_ 5. Per
claim 6.8, the probability that _H_ 5 completes without an abort is at most 2 _[−|]_ **[∆]** _[|]_ .
Per claim 6.9, the distribution of aborts in _H_ 6 is statistically indistinguishable
from the distribution of aborts in _H_ 5. The we can pair the input tapes for
_H_ 6 and _H_ 5 in such a way that the fraction of pairs that cause both hybrids to
compete without aborting with is at most 2 _[−|]_ **[∆]** _[|]_ _−_ 2 _[−][λ]_ [s], and the fraction of pairs
that cause both to abort is at least 1 _−_ 2 _[−|]_ **[∆]** _[|]_ _−_ 2 _[−][λ]_ [s] .
The only variable that distinguishes an aborted instance of _H_ 6 from an
aborted instance of _H_ 5 is _b_ . A simple application of part 2 of proposition 1.1 of
Impagliazzo and Naor [IN96] (as already performed twice before in this proof)
implies that the statistical distance between the distributions of the two hybrids
is upper bounded by 2 _[−]_ [(] _[ξ][−][κ]_ [)] _[/]_ [2] = 2 _[−][λ]_ [s], conditioned on both hybrids aborting.
The probability that _|_ **∆** _| >_ 2 _λ_ s and neither hybrid aborts is less than 2 _[−]_ [2] _[λ]_ [s] +
2 _[−][λ]_ [s] . We assume that if _|_ **∆** _| >_ 2 _λ_ s and the experiment does not abort, then the
adversary can distinguish.


51


Per claim 6.10, if _|_ **∆** _| ≤_ 2 _λ_ s and neither hybrid aborts, then the statistical
difference between _H_ 6 and _H_ 5 is upper-bounded by 2 _[−]_ [(] _[ξ][−][κ][−|]_ **[∆]** _[|]_ [)] _[/]_ [2] + _ξ · Q ·_ 2 _[−][λ]_ [c] .
Putting the pieces together, the total statistical distance between the two
hybrids is no greater than

      -      2 _[−|]_ **[∆]** _[|]_ _−_ 2 _[−][λ]_ [s] [�] _·_ 2 _[−]_ [(] _[ξ][−][κ][−|]_ **[∆]** _[|]_ [)] _[/]_ [2] + _ξ · Q ·_ 2 _[−][λ]_ [c] [�]

       + 1 _−_ 2 _[−|]_ **[∆]** _[|]_ _−_ 2 _[−][λ]_ [s] [�] _·_ 2 _[−][λ]_ [s] + 2 _·_ 2 _[−][λ]_ [s] + 2 _[−]_ [2] _[λ]_ [s] + 2 _[−][λ]_ [s]

        _<_ 2 _[−|]_ **[∆]** _[|]_ _·_ 2 _[−]_ [(2] _[λ]_ [s] _[−|]_ **[∆]** _[|]_ [)] _[/]_ [2] + _ξ · Q ·_ 2 _[−][λ]_ [c] [�] + 5 _·_ 2 _[−][λ]_ [s]


= 2 _[−][λ]_ [s] _[−|]_ **[∆]** _[|][/]_ [2] + 2 _[−|]_ **[∆]** _[|]_ _· ξ · Q ·_ 2 _[−][λ]_ [c] + 5 _·_ 2 _[−][λ]_ [s]

_<_ _ξ · Q ·_ 2 _[−][λ]_ [c] + 6 _·_ 2 _[−][λ]_ [s]


which is negligible in _λ_ c so long as _Q_ is at most polynomial in _λ_ c.



**Hybrid** _H_ 7 **.** This final hybrid differs from _H_ 6 in the following way: _S_ no
longer acts on behalf of any honest parties. Instead, _S_ RVOLE _[A]_ -Alice [(] _[q, ℓ]_ [) is fully im-]

plemented in _H_ 7, and the experiment now incorporates _F_ RVOLE( _q, ℓ_ ). The honest
parties run dummy-party code as is standard for ideal-world experiements in the
UC model, and _S_ RVOLE _[A]_ -Alice [(] _[q, ℓ]_ [) speaks to] _[ F]_ RVOLE [on behalf of corrupt parties.]



The differences between _H_ 7 and _H_ 6 are essentially syntactical, which is to
say that _H_ 6 = _H_ 7. The simulator’s choice bit vector is now denoted _**β**_ _[∗]_ (whereas
in _H_ 6 it was denoted _**β**_ ). The simulator uses this vector to determine whether an
abort will occur and to calculate the vector of offsets _**δ**_ _[d]_ induced into the output
by Alice’s inconsistencies, as before, but instead of adding these offsets to Bob’s
output, the simulator instead computes **c** _[∗]_ _i_ ..= **c** _i −_ _**δ**_ _[d]_ _i_ [for] _[ i][ ∈]_ [[] _[ℓ]_ [] and supplies] **[ c]** _[∗]_

to _F_ RVOLE in place of Alice’s output **d** . The functionality then computes **c** such
that for every _i ∈_ [ _ℓ_ ] it holds that **a** _i · b_ = **c** _[∗]_ _i_ [+] **[ d]** _[i]_ [, and thus the relationship]
between **a**, _b_, **c**, and **d** is maintained.



We now have




      

_A_

RVOLE-Alice [(] _[q,ℓ]_ [)] _[,][Z]_ [ (] _[λ, z]_ [)]




  _H_ 7 = Ideal _F_ RVOLE( _q,ℓ_ ) _,S_ _A_



_λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _, t∈_ [2 _,n_ ] _,_
_q∈_ [2 _[ν]_ [(] _[λ]_ [)] ] : _q_ is prime _, ℓ∈_ [ _ν_ ( _λ_ )] _, z∈{_ 0 _,_ 1 _}_ _[∗]_



and by transitivity we also have

      -       _H_ 7 _≈_ c _H_ 0 = Real _π_ RVOLE( _q,ℓ_ ) _,A,Z_ ( _λ, z_ ) _λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _, t∈_ [2 _,n_ ] _,_
_q∈_ [2 _[ν]_ [(] _[λ]_ [)] ] : _q_ is prime _, ℓ∈_ [ _ν_ ( _λ_ )] _, z∈{_ 0 _,_ 1 _}_ _[∗]_


where the total statistical distance between the _H_ 7 and _H_ 0 is no more than


_ξ · Q ·_ 2 _[−][λ]_ [c] + 6 _·_ 2 _[−][λ]_ [s] + 2 _[−][ξ]_ + 2 _[−][λ]_ [s] + 2 _[−]_ [2] _[λ]_ [c] + _Q_ [2] _·_ 2 _[−]_ [2] _[λ]_ [c] _[−]_ [1] + 2 _[−]_ [2] _[λ]_ [c]

_<_ _ξ · Q ·_ 2 _[−][λ]_ [c] + _Q_ [2] _·_ 2 _[−]_ [2] _[λ]_ [c] _[−]_ [1] + 8 _·_ 2 _[−][λ]_ [s] + 2 _·_ 2 _[−]_ [2] _[λ]_ [c]


and since the environment is PPT, we know that the total number of random
oracle queries _Q_ is at most polynomial in _λ_ c. We can conclude that Lemma 6.2
holds.


52


**6.2** **Simulating Against Bob**



**Lemma 6.11** (OT-Based VOLE Security against Bob) **.** _For every malicious_
_PPT adversary A that statically corrupts_ only _P_ B _, there exists a simulator_
_S_ RVOLE _[A]_ -Bob _[that uses][ A][ as a black box, such that for every PPT environment]_

_Z and every polynomial ν,_

 -  Real _π_ RVOLE( _q,ℓ_ ) _,A,Z_ ( _λ, z_ ) _λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _, t∈_ [2 _,n_ ] _,_
_q∈_ [2 _[ν]_ [(] _[λ]_ [)] ] : _q_ is prime _, ℓ∈_ [ _ν_ ( _λ_ )] _, z∈{_ 0 _,_ 1 _}_ _[∗]_




      

_A_

RVOLE-Bob [(] _[q,ℓ]_ [)] _[,][Z]_ [ (] _[λ, z]_ [)]




 = Ideal _F_ RVOLE( _q,ℓ_ ) _,S_ _A_



_λ∈_ N _, n∈_ [2 _,ν_ ( _λ_ )] _, t∈_ [2 _,n_ ] _,_
_q∈_ [2 _[ν]_ [(] _[λ]_ [)] ] : _q_ is prime _, ℓ∈_ [ _ν_ ( _λ_ )] _, z∈{_ 0 _,_ 1 _}_ _[∗]_



_Proof._ We begin by presenting _S_ RVOLE _[A]_ -Bob [, after which we present an argument]

for the indistinguishability of the two experiments.



**Simulator 6.12.** _S_ RVOLE _[A]_ -Bob [(] _[q, ℓ]_ [)] **[: Random VOLE against Bob]**



This simulator is parameterized by the vector length _ℓ_ and modulus _q_ of the
group Z _q_ over which linear evaluation is to be performed. The simulator
has oracle access to the adversary _A_ that statically corrupts _P_ B (i.e. the
party playing Bob) _only_, and emulates for it an instance of the protocol
_π_ RVOLE( _q, ℓ_ ) involving the parties _P_ A and _P_ B. The simulator forwards all
messages from its own environment _Z_ to _A_, and vice versa. _S_ RVOLE _[A]_ -Bob [(] _[q, ℓ]_ [)]

interacts with the ideal functionality _F_ RVOLE( _q, ℓ_ ) on behalf of _P_ B, and in
the exeriment that it emulates for _A_, it interacts with _A_ and _P_ B on behalf
of _P_ A and on behalf of the ideal oracle _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ). As in _π_ RVOLE( _q, ℓ_ ),
let _κ_ = _|q|_ and _ξ_ = _κ_ +2 _λ_ s and _ρ_ = _⌈κ/λ_ c _⌉_, let **g** _∈_ Z _[ξ]_ _q_ [be an arbitrary non-]
zero gadget vector, _[a]_ and let ROX be a non-programmable global random
oracle with a paramatric range specified by its subscript.


**Sampling:**


1. On receiving (choose _,_ sid _,_ _**β**_ ) from Bob on behalf of _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ), compute _b_ [..] = _⟨_ **g** _,_ _**β**_ _⟩_ and send


  - (sample _,_ sid) to _F_ RVOLE( _q, ℓ_ ) on behalf of Bob

  - (bob-sample _,_ sid _, b_ ) directly to _F_ RVOLE( _q, ℓ_ ).


2. On receiving (bob-message _,_ sid _,_ _**γ**_ ) from _A_ on behalf of _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ),
send (chosen _,_ sid _,_ _**γ**_ ) to Bob on behalf of _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ ). If _A_ sends
abort instead of bob-message, then send (abort _,_ sid) to _F_ RVOLE( _q, ℓ_ )
and perform no further instructions related to the session with ID sid.


**Multiplication:**


3. After receiving both


 - (alice-multiplied _,_ sid) from _F_ RVOLE( _q, ℓ_ )


53


- (bob-message _,_ sid _,_ _**γ**_ ) from _A_ on behalf of _F_ EOTE(Z _[ℓ]_ _q_ [+] _[ρ]_ _, ξ_ )


sample **˜a** _←_ Z _[ξ]_ _q_ [+] _[ρ]_ and _**η**_ _←_ Z _[ρ]_ _q_ [, compute]



��   **˙d** . [.] = _**γ**_ _j,i_ + _**β**_ _j ·_ **˜a** _j,i_



_i∈_ [ _ℓ_ ]











_j∈_ [ _ξ_ ]
��   -   **ˆd** . [.] = _**γ**_ _j,ℓ_ + _i_ + _**β**_ _j ·_ **˜a** _j,ℓ_ + _i_ _i∈_ [ _ρ_ ]



_j∈_ [ _ξ_ ]








_**θ**_ _i,k ·_ **d** **[˙]** _j,i −_ _**β**_ _j ·_ _**η**_ _k_
_i∈_ [ _ℓ_ ]



_i∈_ [ _ρ_ ]














_k∈_ [ _ρ_ ]



_**µ**_ [..] =












  **ˆd** _j,k_ +




 _i∈_ [ _ℓ_ ] _j_ _k_  

_k∈_ [ _ρ_ ] _j∈_ [ _ξ_ ]

_µ_ [..] = RO _{_ 0 _,_ 1 _}_ 2 _λ_ c (sid _,_ _**µ**_ )









_i∈_ [ _ℓ_ ]



**d** [..] =















**g** _j ·_ **d** **[˙]** _j,i_
_j∈_ [ _ξ_ ]



and send


  - (multiply _,_ sid _,_ **˜a** _,_ _**η**_ _, µ_ ) to Bob on behalf of Alice.

  - (bob-share _,_ sid _,_ **d** ) directly to _F_ RVOLE( _q, ℓ_ ).


_a_ When simulating against a corrupt Bob, it is not necessary that **g** have any particular
distribution.


The view of the environment in the two experiments is characterized by the
view of the corrupt Bob, and by Alice’s input **a**, and her output **c** . Bob’s view
is characterized by the vector _**β**_, which determines _b_, by the vector _**γ**_ that he
receives from _F_ EOTE, and by the values **˜a**, _**η**_, and _µ_ that he receives from Alice.
We claim that the joint distribution of these values is identical in the real and
ideal experiments.
In both experiments, **a** is chosen by the environment, _**β**_ is chosen bythe
corrupt Bob, and _**γ**_ is supplied directly by the adversary. In both experiments,
_µ_ = RO _{_ 0 _,_ 1 _}_ 2 _λ_ c (sid _,_ _**µ**_ ) for some _**µ**_, and _**θ**_ = ROZ _ℓq×ρ_ (sid _,_ **˜a** ). The values **˜a**, _**η**_, and
_**µ**_, are calculated by the simulator in the ideal experiment and **c** is calculated
by _F_ RVOLE; in the real experiment, these four values are all calculatd by honest
Alice.
In the ideal experiment _**η**_ is sampled uniformly per step 3 of _S_ RVOLE-Bob,
whereas in the real experiment Alice calculates













_k∈_ [ _ρ_ ]



_**η**_ [..] =



 
 **[ˆa]** _[k]_ [ +]



_**θ**_ _i,k ·_ **a** _i_
_i∈_ [ _ℓ_ ]



(5)



per step 3 of _π_ RVOLE. **ˆa** is sampled uniformly by Alice, and none of the variables
that we have analyzed so far depend upon it; therefore, from the adversary’s
perspective, _**η**_ is uniform in both worlds when considered jointly with ( **a** _,_ _**β**_ _,_ _**γ**_ ).


54


In the ideal experiment, **˜a** is sampled uniformly, whereas in the real experiment Alice calculates



��  **˜a** [..] = _**α**_ [0] _j,i_ _[−]_ _**[α]**_ _j,i_ [1] [+] **[ a]** _[i]_




  -   _i∈_ [ _ℓ_ ] _[∥]_ _**α**_ [0] _j,ℓ_ + _k_ _[−]_ _**[α]**_ _j,ℓ_ [1] + _k_ [+] **[ ˆa]** _[k]_ _k∈_ [ _ρ_ ]







(6)
_j∈_ [ _ξ_ ]



For every _j ∈_ [ _ξ_ ] and _k ∈_ [ _ρ_ ], _**α**_ 1 _j,k−_ _**β**_ _j_ is uniformly sampled by _F_ EOTE and
information-theoretically hidden from the adversary in the real experiment,
which implies that from the adversary’s point of view, **˜a** is uniform in both
experiments when considered jointly with ( **a** _,_ _**β**_ _,_ _**γ**_ _,_ _**η**_ ). This also implies that
the distribution of _**θ**_ is identical in both experiments.
In the ideal experiment, _S_ RVOLE-Bob calculates











_**θ**_ _i,k ·_ **d** **[˙]** _j,i −_ _**β**_ _j ·_ _**η**_ _k_
_i∈_ [ _ℓ_ ]


















_k∈_ [ _ρ_ ]




_j∈_ [ _ξ_ ]



_**µ**_ [..] =



 
**ˆd** _j,k_ +




and by substituting in the equations that _S_ uses to calculate **d** **[ˆ]** and **d** **[˙]**, we have


















_**γ**_ _j,ℓ_ + _k_ + _**β**_ _j ·_ **˜a** _j,ℓ_ + _k_









_k∈_ [ _ρ_ ]



_**µ**_ =












 +



_**θ**_ _i,k ·_ ( _**γ**_ _j,k_ + _**β**_ _j ·_ **˜a** _j,k_ ) _−_ _**β**_ _j ·_ _**η**_ _k_
_i∈_ [ _ℓ_ ]



in the ideal world. In the real experiment, Alice calculates



_**θ**_ _i,k ·_ _**α**_ [0] _j,i_
_i∈_ [ _ℓ_ ]













_k∈_ [ _ρ_ ]









_j∈_ [ _ξ_ ]



_**µ**_ [..] =












  _j,ℓ_ + _k_ [+]
 _**[α]**_ [0]





] _j∈_ [ _ξ_ ]







which expands to














- - 
_**θ**_ _i,k ·_ (1 _−_ _**β**_ _j_ ) _·_ _**α**_ [0] _j,i_ [+] _**[ β]**_ _j_ _[·]_ _**[ α]**_ _j,i_ [0]
_i∈_ [ _ℓ_ ]



(1 _−_ _**β**_ _j_ ) _·_ _**α**_ [0] _j,ℓ_ + _k_ [+] _**[ β]**_ _j_ _[·]_ _**[ α]**_ _j,ℓ_ [0] + _k_









_k∈_ [ _ρ_ ]




_j∈_ [ _ξ_ ]



_**µ**_ =












 +



(7)


(8)



and since _**γ**_ _j,i_ = (1 _−_ _**β**_ _j_ ) _·_ _**α**_ [0] _j,i_ [+] _**[ β]**_ _j_ _[·]_ _**[ α]**_ _j,i_ [1] [, if follows that]













_j∈_ [ _ξ_ ]









 +




- - 
_**θ**_ _i,k ·_ _**γ**_ _j,i_ + _**β**_ _j ·_ ( _**α**_ [0] _j,i_ _[−]_ _**[α]**_ _j,i_ [1] [)]
_i∈_ [ _ℓ_ ]



_**γ**_ _j,ℓ_ + _k_ + _**β**_ _j ·_ ( _**α**_ [0] _j,ℓ_ + _k_ _[−]_ _**[α]**_ _j,ℓ_ [1] + _k_ [)]








_k∈_ [ _ρ_ ]



_**µ**_ =







in the real experiment. Now rearanging equation 6 to solve for _**α**_ [0] _j,i_ _[−]_ _**[α]**_ _j,i_ [1] [and]
then substituting it into equation 8, we find that














 +




- - 
_**θ**_ _i,k ·_ _**γ**_ _j,i_ + _**β**_ _j ·_ ( **˜a** _j,i −_ **a** _i_ )
_i∈_ [ _ℓ_ ]








_**γ**_ _j,ℓ_ + _k_ + _**β**_ _j ·_ ( **˜a** _j,ℓ_ + _k −_ **ˆa** _k_ )









_k∈_ [ _ρ_ ]






_j∈_ [ _ξ_ ]



_**µ**_ =







(9)



55


in the real experiment, and finally, substituting equation 5 into equation 9 yields
equation 7, which is the ideal-world distribution. Thus the distribution of _**µ**_
is identical in the real and ideal experiments, when considered jointly with
( **a** _,_ _**β**_ _,_ _**γ**_ _,_ _**η**_ _,_ **˜a** _,_ _**θ**_ ).
The final variable is **c** . In the ideal world, _F_ RVOLE calculates **c**, and plugging
in the definitions of the values supplied to _F_ RVOLE by _S_ RVOLE-Bob, we have




_i∈_ [ _ℓ_ ]












**c** =











**g** _j ·_ ( _**β**_ _j ·_ **a** _i_ + _**β**_ _j ·_ **˜a** _j,i −_ _**γ**_ _j,i_ )
_j∈_ [ _ξ_ ]



(10)


(11)



in the ideal world. In the real world, Alice calculates













_i∈_ [ _ℓ_ ]



**c** [..] =



 
 _[−]_



**g** _j ·_ _**α**_ [0] _j,i_
_j∈_ [ _ξ_ ]



and we can rewrite equation 6 and substitute the result into equation 11 to find
that  




_i∈_ [ _ℓ_ ]












**c** =











**g** _j ·_ ( **a** _i −_ **˜a** _j,i −_ _**α**_ [1] _j,i_ [)]
_j∈_ [ _ξ_ ]



and adding 0 = (1 _−_ _**β**_ _j_ ) _·_ _**α**_ [0] _j,i_ [+] _**[ β]**_ _j_ _[·]_ _**[ α]**_ _j,i_ [1] _[−]_ _**[γ]**_ _j,i_ [to this we find]




_i∈_ [ _ℓ_ ]












**c** =











**g** _j ·_ ( **a** _i −_ **˜a** _j,i_ + ( _**β**_ _j −_ 1) _·_ ( _**α**_ [1] _j,i_ _[−]_ _**[α]**_ _j,i_ [0] [)] _[ −]_ _**[γ]**_ _j,i_ [)]
_j∈_ [ _ξ_ ]



(12)



in the real experiment. Finally, rewriting equation 6 and plugging it into equation 12 yields equation 10. It follows that the distribution of **c** is identical in the
real and ideal experiments when considered jointly with ( **a** _,_ _**β**_ _,_ _**γ**_ _,_ _**η**_ _,_ **˜a** _,_ _**θ**_ _,_ _**µ**_ ), and
from this it follows that the two experiments are identically distributed overall,
and lemma 6.11 holds.

## **7 Relaxed Threshold Key Generation**


In this section we discuss our key generation functionality, _F_ RelaxedKeyGen, which
was introduced in section 3.1. In section 7.1 we introduce a protocol to realize
our functionality, and in section 7.2 we prove it to be perfectly secure.
We refer to our key generation functionality as _relaxed_ because it differs in a
crucial way from those used in prior works. Consider as an example of the typical
approach the key generation functionality that accompanies the threshold BBS+
protocol Doerner et al. [DKL [+] 23]. This functionality works in the “obvious”
way: it samples a uniform secret key internally and outputs a corresponding
public key to all parties, accepts Shamir shares of the secret key from the corrupt


56


parties, and outputs consistent shares to each of the honest parties. To prove
that any protocol realizes this functionality, it is necessary for the simulator
to program into the views of the corrupt parties a specific public key, and to
extract their Shamir shares so that the functionality can produce consistent ones.
In order to enable this, the three-round protocol that Doerner et al. specify
includes a proof of knowledge for the contributions of each party. Such proofs
of knowledge are a hallmark of simulation-secure key generation protocols in the
dishonest-majority setting, [10] and in the context of universal composability, they
must be straight-line extractable, which implies significant overhead in terms
of both computation and communication due to the use of the Pass [Pas03],
Fischlin [Fis05], or Kondi-shelat [Ks22] transforms.
Consider the above “obvious” key generation formulation. The outputs of
the functionality to the honest parties are non-negotiable, since they will be
forwarded directly to the environment in the UC model. The interface with the
corrupt parties, on the other hand, is driven by the needs of the simulators:
both the simulator for the key generation protocol, and also the simulator for
any eventual signing protocol that uses the key generation functionality and
requires knowledge of the adversary’s shares in order to simulate signing.
Our signing protocol differs from many others in that it does _not_ require the
adversary’s contributions to the secret key to be extracted during key generation, because the secret key shares are rerandomized and extracted afresh by
_F_ RVOLE for each signature. This liberates us in our choice of a key generation
functionality: we need only ensure that the public key is uniformly sampled,
and that the honest parties’ shares are distributed consistently with the corrupt
parties’ shares. In this section, we achieve these guarantees _without_ extracting
the corrupt parties’ shares; that is, our key generation protocol has _no_ proofs
of knowledge.
The intuition behind our relaxed functionality is simple: the ideal adversary
(i.e. the simulator) sends it the corrupt parties’ additive contributions to the
_honest_ parties’ Shamir shares and to the public key, but the corrupt parties’
additive contributions to their own Shamir shares are supplied only in the same
group G as the public key (from which they cannot be recovered, under the
hardness of discrete logarithm). The functionality can check (in G) that these
contributions form a polynomial of the correct degree, and if so, it samples a
uniform additive contribution (i.e. another polynomial of correct degree) to
the Shamir shares of all parties on behalf of the honest parties. As in other
approaches, the public key is uniform from the perspective of the adversary, and
the joint secret key is unrecoverable by the adversary (assuming that the discrete
logarithm problem is hard in G), so long as the number of corruptions is less than
the threshold. Unlike other approaches, the secret key is _also_ unrecoverable to
the functionality itself, if the number of _honest_ parties is less than the threshold.
We stress that our relaxed key generation functionality is sufficient for use
with the signing protocol proposed in this work, but it _cannot_ necessarily be


10See, for example, [Lin17, DKLs18, LN18, GG18, DKLs19, CGG+20, CCL+20, Lin22,
HLNR23, CCL [+] 23]. [DOK [+] 20, ANO [+] 22] use full-blown MPC for key generation.


57


used with other threshold signing protocols that use discrete-log keypairs. Consider for example, the classic folkloric threshold Schnorr protocol, as recently
discussed by Lindell [Lin22]: in this protocol, the secret key shares of the corrupt
parties are required in order to simulate signing, but they are _only_ extracted
during key generation. Consequently Lindell’s protocol becomes unsimulatable
if his key generation functionality is replaced by ours.
Finally, we note that our functionality is strictly weaker than the more typical functionality of Doerner et al. [DKL [+] 23], which we discussed above. Because
our functionality can be replaced with theirs, our protocol can also be replaced
with theirs, if desired.


**7.1** **The Protocol**


In this work, we have restricted ourselves to point-to-point authenticated channels and studiously avoided the use of broadcast channels. As a consequence
we have achieved only security with selective abort. Because public keys may
be linked _irrevocably_ to identity or authority, it is often desirable to achieve at
least _unanimous_ abort in key generation protocols, so that each honest party
is convinced that _all_ honest parties can participate in signing and that a single
agreed-upon public key exists, if no abort is observed. We present our key generation protocol in the hybrid model of a broadcast commitment functionality
_F_ Com( _n_ ), which behaves like the version of _F_ Com introduced in section 3.1, except that it delivers consistent outputs to _n −_ 1 recipients simultaneously. This
functionality is easily realized by combining any UC-secure commitment scheme
with a broadcast channel. We will refer to the non-broadcast commitment functionality as _F_ Com(2) hereafter.
When only point-to-point channels are assumed, as is otherwise the case in
our work, our the broadcast channel underlying our enhanced _F_ Com( _n_ ) can be
replaced by the _echo-broadcast_ technique of Goldwasser and Lindell [GL05], in
which each broadcasted message is sent to all parties in a point-to-point fashion,
and then the parties swap hashes of the broadcast channel to ensure that the
messages they received are consistent. The result is that the adversary can
force _F_ Com( _n_ ) (and therefore our key generation protocol) to abort selectively.
The echo can occur simultaneously with the last round of our key generation
protocol, and thus the number of rounds is not affected by this technique.
On the other hand, if a true broadcast channel is available, then the final
round of messages in our key generation protocol can also make use of it, and
the result is that our protocol achieves unanimous abort.


**Protocol 7.1.** _π_ RelaxedKeyGen( _G, n, t_ ) **: Relaxed DLog Keygen**


This protocol is parameterized by the party count _n_, the threshold _t_, and
the elliptic curve _G_ = (G _, G, q_ ). The parties _P_ 1 _, . . ., Pn_ participate in this
protocol and interact with the ideal functionality _F_ Com.


58


**Key Generation:**


1. On receiving (keygen _,_ sid) from the environment, each party _Pi_ samples
a random degree polynomial _pi_ of degree _t −_ 1 over Z _q_ . Let _Pi_ denote
the corresponding polynomial in G; i.e. let _Pi_ ( _x_ ) = _pi_ ( _x_ ) _· G_ for _x ∈_ Z _q_ .


2. _Pi_ computes **P** [-] _[j]_ [ ..] = [ _n_ ] _\ {j}_ for every _j ∈_ **P**, and then sends


 - (commit _, Pi∥P_ **P** -1 _i_ _[∥]_ _[. . .][ ∥P]_ **[P]** _n_ [-] _[i]_ _−_ 1 _[∥]_ [sid] _[,][ {][P][i]_ [(] _[j]_ [)] _[}][j][∈]_ [[0] _[,t][−]_ [1]][) to] _[ F]_ [Com][(] _[n]_ [).]

 - (commit _, Pi∥Pj∥_ sid _, pi_ ( _j_ )) to _F_ Com(2) for _j ∈_ **P** [-] _[i]_ .


3. Upon being notified of all other parties’ commitments, each party _Pi_
releases its committed values by sending


 - (decommit _, Pi∥P_ **P** -1 _i_ _[∥]_ _[. . .][ ∥P]_ **[P]** _n_ [-] _[i]_ _−_ 1 _[∥]_ [sid][) to] _[ F]_ [Com][(] _[n]_ [).]

 - (decommit _, Pi∥Pj∥_ sid) to _F_ Com(2) for _j ∈_ **P** [-] _[i]_ .


4. Each party _Pi_ receives


 - (opening _, Pj∥P_ **P** -1 _j_ _[∥]_ _[. . .][ ∥P]_ **[P]** _n_ [-] _[j]_ _−_ 1 _[,][ {][P][i]_ [(] _[j]_ [)] _[}][j][∈]_ [[0] _[,t][−]_ [1]][) from] _[ F]_ [Com][(] _[n]_ [)]

 - (opening _, Pi∥Pj∥_ sid _, pj_ ( _i_ )) from _F_ Com(2) for _j ∈_ **P** [-] _[i]_


for each _j ∈_ **P** [-] _[i]_ . Let _P_ denote the sum of _Pj_ for _j ∈_ [ _n_ ]; i.e. let
_P_ ( _x_ ) = [�] _j∈_ [ _n_ ] _[P][j]_ [(] _[x]_ [) for] _[ x][ ∈]_ [Z] _[q]_ [.] _[ P][i]_ [ computes]

      _P_ _[′]_ ( _i_ ) [..] = _pj_ ( _i_ ) _· G_


_j∈_ [ _n_ ]


and then verifies that



otherwise
lagrange([ _t −_ 1] _∪{i}, i,_ 0)



_P_ ( _i_ ) if _i ∈_ [ _t −_ 1]



_P_ _[′]_ ( _i_ ) =












  _P_ (0) _−_



lagrange([ _t −_ 1] _∪{i}, j,_ 0) _· P_ ( _j_ )
_j∈_ [ _t−_ 1]



and if this equality holds, then _Pi_ sends (ok _,_ sid) to all other parties. If
this equality does not hold, then _Pi_ sends (abort _,_ sid) to all parties.


5. If any party sends (abort _,_ sid) to _Pi_, or _Pi_ itself sent such a message,
then _Pi_ outputs (abort _,_ sid) to the environment, and performs no future instructions related to this session. If _Pi_ transmitted (ok _,_ sid) and
receives an identical message from all other parties, then it outputs
(key-pair _,_ sid _, P_ (0) _, p_ ( _i_ )) to the environment.


59


**7.2** **Proof of Security**



**Theorem 7.2** (Key Generation Security Theorem) **.** _For every group described_
_by G and every malicious adversary A that statically corrupts up to t−_ 1 _parties,_
_there exists a simulator S_ RelaxedKeyGen _[A]_ _[that uses][ A][ as a black box, such that for]_

_every environment Z it holds that_

 - Real _π_ RelaxedKeyGen( _G,n,t_ ) _,A,Z_ ( _λ_ s _, z_ ) _[∗]_



s         

_A_

RelaxedKeyGen [(] _[G][,n,t]_ [)] _[,][Z]_ [ (] _[λ]_ [s] _[, z]_ [)]




 = Ideal _F_ RelaxedKeyGen( _G,n,t_ ) _,S_ _A_



_λ_ s _∈_ N _,n∈_ N: _n>_ 1 _,t∈_ [2 _,n_ ] _,z∈{_ 0 _,_ 1 _}_ _[∗]_



_λ_ s _∈_ N _,n∈_ N: _n>_ 1 _,t∈_ [2 _,n_ ] _,z∈{_ 0 _,_ 1 _}_ _[∗]_



_Proof._ This proof is direct, without any hybrid experiments. The simulator is
as follows:

**Simulator 7.3.** _S_ RelaxedKeyGen _[A]_ [(] _[G][, n, t]_ [)] **[: Relaxed DLog Keygen]**


This simulator is parameterized by the party count _n_, the threshold _t_,
and the elliptic curve _G_ = (G _, G, q_ ). The simulator has oracle access
to the adversary _A_, and emulates for it an instance of the protocol
_π_ RelaxedKeyGen( _G, n, t_ ) involving the parties _P_ 1 _, . . ., Pn_ . The simulator forwards all messages from its own environment _Z_ to _A_, and vice versa.
When the emulated protocol instance begins, _A_ announces the identities
of up to _t −_ 1 corrupt parties. Let the indices of these parties be given
by **P** _[∗]_ _⊆_ [ _n_ ]. _S_ RelaxedKeyGen _[A]_ [(] _[G][, n, t]_ [) interacts with the ideal functionality]

_F_ RelaxedKeyGen( _G, n, t_ ) on behalf of every corrupt party, and in the exeriment
that it emulates for _A_, it interacts with _A_ and the corrupt parties on behalf
of every honest party and on behalf of the ideal functionality _F_ Com.


**Key Generation:**


1. On receiving (keygen-req _,_ sid _, j_ ) from _F_ RelaxedKeyGen( _G, n, t_ ) such that
_j ∈_ [ _n_ ] _\_ **P** _[∗]_, compute **P** [-] _[i]_ [ ..] = [ _n_ ] _\ {i}_ for every _i ∈_ **P** and send to each
_Pi_ for _i ∈_ **P** _[∗]_


  - (committed _, Pj∥P_ **P** -1 _j_ _[∥]_ _[. . .][ ∥P]_ **[P]** _n_ [-] _[j]_ _−_ 1 _[∥]_ [sid][)) on behalf of] _[ F]_ [Com][(] _[n]_ [).]

  - (committed _, Pj∥Pi∥_ sid) on behalf of _F_ Com(2).


2. On receiving


  - (commit _, Pi∥P_ **P** -1 _i_ _[∥]_ _[. . .][ ∥P]_ **[P]** _n_ [-] _[i]_ _−_ 1 _[∥]_ [sid] _[,][ {][P][i]_ [(] _[j]_ [)] _[}][j][∈]_ [[0] _[,t][−]_ [1]][)] on behalf of
_F_ Com( _n_ ).

  - (commit _, Pi∥Pj∥_ sid _, pi_ ( _j_ )) on behalf of _F_ Com(2) for some _consistent_
_j ∈_ **P** [-] _[i]_ _\_ **P** _[∗]_ .


from every _Pi_ for _i ∈_ **P** _[∗]_


   - If there exists some _j_ _[′]_ _∈_ **P** [-] _[i]_ _\_ **P** _[∗]_ with respect to which such messages
have not all been received, such that _j_ _[′]_ = _j_, then sample _pj_ ( _i_ ) _←_ Z _q_


60


uniformly for each _i ∈_ **P** _[∗]_ and sample _Pj_ as a uniform polynomial of
degree _t −_ 1 over G such that _Pj_ ( _i_ ) = _pj_ ( _i_ ) _· G_ for every _i ∈_ **P** _[∗]_ .


- If _j_ is the _last_ value which satisfies the above conditions, then

(a) For every _i ∈_ **P** _[∗]_ and _k ∈_ [ _t, n_ ] compute



_Pi_ ( _k_ ) [..] =




  _Pi_ (0) _−_ lagrange([ _t −_ 1] _∪{k}, l,_ 0) _· Pi_ ( _l_ )

_l∈_ [ _t−_ 1]

lagrange([ _t −_ 1] _∪{k}, k,_ 0)



and then for every _k ∈_ [ _n_ ] _\_ **P** _[∗]_ compute




  _p_ ˇ( _k_ ) [..] = _pi_ ( _k_ )

_i∈_ **P** _[∗]_

  _P_ ˇ( _k_ ) ..= _Pi_ ( _k_ )

_i∈_ **P** _[∗]_



(b) Send (adv-poly _,_ sid _, {p_ ˇ( _k_ ) _}k∈_ [ _n_ ] _\_ **P** _∗_ _, {P_ [ˇ] ( _i_ ) _}i∈_ **P** _[∗]_ ) directly to
_F_ RelaxedKeyGen( _G, n, t_ ).

(c) On receiving (hon-poly _,_ sid _, P_ (0) _, {P_ [ˆ] ( _k_ ) _}k∈_ [ _n_ ] _\_ **P** _∗_ _, {p_ ˆ( _i_ ) _}i∈_ **P** _[∗]_ )
from _F_ RelaxedKeyGen( _G, n, t_ ), compute



_P_ ˆ( _i_ ) ..= ˆ _p_ ( _i_ ) _· G_ for _i ∈_ **P** _[∗]_




   _pj_ ( _i_ ) [..] = ˆ _p_ ( _i_ ) _−_



_pk_ ( _i_ ) for _i ∈_ **P** _[∗]_
_k∈_ **P** [-] _[j]_ _\_ **P** _[∗]_




   _Pj_ ( _k_ ) [..] = _P_ [ˆ] ( _k_ ) _−_



_Pj_ ( _k_ ) for _k ∈_ [ _t −_ 1]
_i∈_ **P** [-] _[j]_ _\_ **P** _[∗]_




   _Pj_ (0) [..] = _P_ (0) _−_



_Pi_ (0)

_i∈_ **P** [-] _[j]_



(d) If (abort _,_ sid) is received from _F_ RelaxedKeyGen( _G, n, t_ ) instead of
hon-poly, then sample _pj_ ( _i_ ) _←_ Z _q_ uniformly for each _i ∈_ **P** _[∗]_

and sample _Pj_ as a uniform polynomial of degree _t −_ 1 over G
such that _Pj_ ( _i_ ) = _pj_ ( _i_ ) _· G_ for every _i ∈_ **P** _[∗]_ .


and finally, send to each _Pi_ for _i ∈_ **P** _[∗]_


 - (opening _, Pj∥P_ **P** -1 _j_ _[∥]_ _[. . .][ ∥P]_ **[P]** _n_ [-] _[j]_ _−_ 1 _[∥]_ [sid] _[,][ {][P][j]_ [(] _[k]_ [)] _[}][k][∈]_ [[0] _[,t][−]_ [1]][)] on behalf of

_F_ Com( _n_ ).

 - (opening _, Pj∥Pi∥_ sid _, pj_ ( _i_ )) on behalf of _F_ Com(2).


3. On receiving


 - (decommit _, Pi∥P_ **P** -1 _i_ _[∥]_ _[. . .][ ∥P]_ **[P]** _n_ [-] _[i]_ _−_ 1 _[∥]_ [sid][) on behalf of] _[ F]_ [Com][(] _[n]_ [).]


61


  - (decommit _, Pi∥Pj∥_ sid) on behalf of _F_ Com(2) for some _consistent j ∈_
**P** [-] _[i]_ _\_ **P** _[∗]_ .


from every _Pi_ for _i ∈_ **P** _[∗]_, if ˇ _p_ ( _j_ ) _· G ̸_ = _P_ [ˇ] ( _j_ ), then send (abort _,_ sid)
to all corrupt parties on behalf of _Pj_ and send (abort _,_ sid _, k_ ) to
_F_ RelaxedKeyGen( _G, n, t_ ) for every _k ∈_ [ _n_ ] _\_ **P** _[∗]_ . Otherwise send (ok _,_ sid)
to all corrupt parties on behalf of _Pj_ .


4. On receiving (abort _,_ sid) from _Pi_ on behalf of _Pj_ for some _i ∈_ **P** _[∗]_ and
_j ∈_ [ _n_ ] _\_ **P** _[∗]_, send (abort _,_ sid _, j_ ) to _F_ RelaxedKeyGen( _G, n, t_ ).

5. On receiving (ok _,_ sid) from _Pi_ on behalf of _Pj_ some consistent _j ∈_ [ _n_ ] _\_ **P** _[∗]_

and _every i ∈_ **P** _[∗]_, if ˇ _p_ ( _k_ ) _· G_ = _P_ [ˇ] ( _k_ ) for every _k ∈_ [ _n_ ] _\_ **P** _[∗]_, then send
(release _,_ sid _, j_ ) to _F_ RelaxedKeyGen( _G, n, t_ ).


The view of the adversary is completely characterized by the values transmitted by the corrupt parties and by the values emitted by the honest parties,
both in the protocol and to the environment. That is, the adversary’s view is
characterized by the public key _P_ (0) and for every _j ∈_ [ _n_ ] _\_ **P** _[∗]_ by the secret
key share _p_ ( _j_ ), the polynomial _Pj_, and the selected discrete logarithms _pj_ ( _i_ ) of
points on _Pj_, for _i ∈_ **P** _[∗]_ .
We argue first about the distribution of aborts, then about the distribution
of values when an abort occurs, then about the distribution of values when an
abort does not occur.
We observe first of all that in the ideal world, the values _{P_ [ˇ] ( _i_ ) _}i∈_ **P** _[∗]_ supplied
to _F_ RelaxedKeyGen by _S_ RelaxedKeyGen are interpolated from the adversary’s commitments to _t_ polynomial points. These, therefore, lie on a degree _t −_ 1 polynomial
(or many such polynomials, if _|_ **P** _[∗]_ _| < t−_ 1), and it follows that an abort based on
the conditions in step 1 only occurs if the values _{p_ ˇ( _k_ ) _}k∈_ [ _n_ ] _\_ **P** _∗_ are inconsistent
with this polynomial (or with all polynomials that pass through _{P_ [ˇ] ( _i_ ) _}i∈_ **P** _[∗]_, if
_|_ **P** _[∗]_ _| < t −_ 1). Recall that per step 2,




 _p_ ˇ( _k_ ) =




- 
_pi_ ( _k_ ) and _P_ ˇ( _k_ ) =
_i∈_ **P** _[∗]_ _i∈_ **P**



_Pi_ ( _k_ )
_i∈_ **P** _[∗]_



for every _k ∈_ [ _n_ ] _\_ **P** _[∗]_ . In the real world, per step 4 of _π_ RelaxedKeyGen, each honest
party _Pk_ for _k ∈_ [ _n_ ] _\_ **P** _[∗]_ signals the other parties to abort if

    -     



- 
_pi_ ( _k_ ) _· G ̸_ =

_i∈_ [ _n_ ] _i∈_ [ _n_



_Pi_ ( _k_ )

_i∈_ [ _n_ ]



where _Pi_ ( _k_ ) is interpolated from the first _t_ points on _Pi_, if necessary. Since
_pj_ ( _k_ ) _·G_ = _Pj_ ( _k_ ) for all _j, k ∈_ [ _n_ ] _\_ **P** _[∗]_ by construction, this condition is equivalent
to the ideal-world abort condition expressed by _F_ RelaxedKeyGen.
Next, we analyze the distributions of the values in the protocol, conditioned
on an abort occurring. In the ideal world, the _S_ RelaxedKeyGen samples _pk_ for
_k ∈_ [ _n_ ] _\_ **P** _[∗]_ uniformly, whereas in the real world, _Pk_ samples _pk_ for _k ∈_ [ _n_ ] _\_


62


**P** _[∗]_ uniformly. In both worlds, we have _Pk_ ( _x_ ) = _pk_ ( _x_ ) _· G_ for _x ∈_ Z _q_, and
neither world does the environment learn _p_ ( _k_ ), due to the fact that an abort
occurs. Thus the two worlds are identically distributed, conditioned on an abort
occurring.
If an abort does not occur, then the situation is very similar. The distinction
is that _F_ RelaxedKeyGen samples ˆ _p_ uniformly, defines _P_ [ˆ] ( _x_ ) = ˆ _p_ ( _x_ ) _· G_ for _x ∈_ Z _q_,
and sends _{P_ [ˆ] ( _k_ ) _}k∈_ [ _n_ ] _\_ **P** _∗_ and _{p_ ˆ( _i_ ) _}i∈_ **P** _[∗]_ to _S_ RelaxedKeyGen. If we let _Ph_ denote
the _last_ honest party to decommit in step 4 of the protocol, then we can see
that in the ideal world, _S_ RelaxedKeyGen samples _pk_ for _k ∈_ **P** [-] _[h]_ _\_ **P** _[∗]_ uniformly as
before, calculates _Ph_ ( _x_ ) such that




  _P_ ˆ( _x_ ) =



_Pj_ ( _x_ )
_j∈_ [ _n_ ] _\_ **P** _[∗]_



for every _x ∈_ Z _q_, and calculates _ph_ ( _i_ ) such that




  _p_ ˆ( _i_ ) =



_pj_ ( _i_ )
_j∈_ [ _n_ ] _\_ **P** _[∗]_



for _i ∈_ **P** _[∗]_ . Thus the joint distributions of _Pj_ for _j ∈_ [ _n_ ] and _pj_ ( _i_ ) for _j ∈_ [ _n_ ] and
_i ∈_ **P** _[∗]_ are identical in the real and ideal worlds. It remains finally to observe
that in the ideal world, each honest party _Pj_ emits _p_ ( _j_ ) = ˇ _p_ ( _j_ ) + ˆ _p_ ( _j_ ), whereas
in the real world, it emits _p_ ( _i_ ) = _pj_ ( _i_ )


_j∈_ [ _n_ ]


which is distributed identically.

## **8 Analytical Efficiency**


In this section, we give a closed-form accounting of the bandwidth costs of our
protocol and its various building blocks. We account for the number of elliptic
curve scalar operations that our protocol requires during signing, since this is
a substantial portion of the computational cost. We begin by analyzing the
realizations for non-VOLE building blocks that were suggested in section 3.1:
an _F_ Com commitment to any payload requires 2 _λ_ c bits to be transmitted, and
a decommitment to a payload of size _x_ requires 2 _λ_ c + _x_ bits. We assume that
the “broadcast” variant of _F_ Com multiplies the foregoing costs by the number
of recipients, and that then adds 2 _λ_ c transmitted bits per recipient in order to
implement echo-broadcast. We assume _F_ Zero(Z _q, t_ ) requires a one-time setup cost
of ( _t_ _−_ 1) commitments and decommitments to _λ_ c bits on the part of each party,
and that invocation by that same set of parties is free in terms of bandwidth
thereafter.


**8.1** **Oblivious Transfer**


Our VOLE protocol relies on OT, which we realize via the OT-extension protocol
of Roy [Roy22], using the one-round optimization introduced in section 5.1, with


63


base OTs supplied by the two-round UC-secure endemic OT protocol of Masny
and Rindal [MR19]. We instantiate the latter primitive from the decisional
Diffie-Hellman assumption over the same group _G_ in which signatures are to
be computed. For _ℓ_ OT OT instances, the protocol of Masny and Rindal has an
average per-party bandwidth cost of


EOTCost( _|G|, ℓ_ OT) _�→_ 2 _· |G| · ℓ_ OT


and it requires each party to compute 3 _ℓ_ OT elliptic curve scalar operations, on
average.
Roy’s protocol requires a one-time setup that comprises exactly _λ_ c instances
of OT. This is followed by any number of extension batches. Per the accounting
of Doerner et al. [DKL [+] 23], each batch of _ℓ_ OTE endemic OT instances has an
average per-party bandwidth cost of




       3 1
EOTECost( _λ_ c _, ℓ_ OTE) _�→_

2 [+] 2 _k_ SSOT





_·_ ( _λ_ c2 + _λ_ c) + _[λ]_ [c] _[·][ ℓ]_ [OTE]

2 _k_ SSOT



where _k_ SSOT is a parameter that also impacts computation time. Roy suggested that _k_ SSOT = 2 yields a strict improvement over all other OT-extension
protocols; we adopt this value when calculating concrete costs. If correlated
OT-extension instances are required then


COTECost( _λ_ c _, ℓ_ OTE _, |m|_ ) _�→_ _ℓ_ OTE _· |m|/_ 2 + EOTECost( _λ_ c _, ℓ_ OTE)


where _|m|_ is the size of the correlation in bits.


**8.2** **Our VOLE**


For the purposes of our cost analysis, we assume that setup for endemic OT
extension is performed once per pair of parties, and reused thereafter in all
instances of the protocol realizing _F_ EOTE among those two parties. Our protocol
involves an endemic OT-extention batch of size _ℓ_ OTE = _ξ_ = _κ_ + 2 _λ_ s, and the
transmission of ( _ℓ_ + 1) _· ξ_ + 1 elements of Z _q_ and 2 _λ_ c bits directly from Alice
to Bob. This brings the total online (i.e. excluding one-time setup) average
per-party bandwidth cost of our DKLs-derived VOLE protocol to


VOLECost( _λ_ c _, λ_ s _, κ, ℓ_ ) _�→_

EOTECost( _λ_ c _, κ_ + 2 _λ_ s) + ( _κ/_ 2 + _λ_ s) _·_ ( _ℓ_ + 1) _· κ_ + _κ/_ 2 + _λ_ c


The one-time setup for our protocol comprises the one-time setup for endemic OT-extensions, plus the sending of a single security-parameter-length seed
from Bob to Alice. Thus, assuming Roy’s OT-extension protocol and Masny
and Rindal’s OT protocol are used, we have an average per-party bandwidth
cost of


VOLESetupCost( _λ_ c _, λ_ s _, κ, |G|_ ) _�→_ EOTCost( _|G|, λ_ c) + _λ_ c _/_ 2


64


**8.3** **VOLE from HMRT22**


Next, we present the cost of using an alternate VOLE protocol derived from
the work of Haitner et al. [HMRT22]. Their protocol realizes a weaker functionality than the one we have specified, and we have _not_ proven the combination
secure, and we remind the reader that the protocol of Haitner et al. requires
an additional round, relative to the DKLs-derived VOLE described in section 5.
Nevertheless, we include a cost analysis of their protocol for the sake of comparison.
Haitner et al.’s description of their protocol specifies correlated OT rather
than correlated OT-extension. In order to make an apples-to-apples comparison
against our VOLE, we assume OT-extension is used, and as a consequence it is
necessary to perform a one-time setup procedure. Thus


VOLESetupCost( _λ_ c _, λ_ s _, κ, |G|_ ) _�→_ EOTCost( _|G|, λ_ c) + _λ_ c _/_ 2


The evaluation stage of their protocol involves a batch of _ℓ_ OTE = _κ_ + 4 _λ_ s
correlated OT instances. Per a random-oracle-based optimization mentioned in
their paper, the only additional data that must be sent is a single _λ_ c-bit seed,
plus a single element of Z _q_ . [11] If we derive a VOLE from their OLE in the same
way that we derived _π_ RVOLE from the DKLs OLE protocols, then the average
per-party bandwidth cost is


VOLECost( _λ_ c _, λ_ s _, κ, ℓ_ ) _�→_ COTECost( _λ_ c _, κ_ + 4 _λ_ s _, κ · ℓ_ ) + ( _κ · ℓ_ + _λ_ c) _/_ 2


Assuming that SoftSpokenOT is used to realize the correlated OT-extension,
their protocol outperforms ours in terms of bandwidth costs only when


2 _λ_ c _· λ_ s

+ 2 _λ_ s _· κ · ℓ_ + _κ · ℓ< κ_ [2] + 2 _λ_ s _· κ_ + _κ_ + _λ_ c
_k_ SSOT


**8.4** **Our Key Generation and ECDSA Protocols**


When the echo-broadcast synchronization messages are coalesced, the bandwidth cost of realizing _F_ RelaxedKeyGen( _G, n, t_ ) via the protocol introduced in section 7 is given by


KeyGenCost( _n, λ_ c _, κ, |G|_ ) _�→_ ( _n −_ 1) _·_ (10 _λ_ c + _t · |G|_ + _κ_ )


The one-time initialization for _π_ ECDSA involves running _F_ RelaxedKeyGen and
initializing two instances of _F_ RVOLE per pair of parties. Each party must also
commit and release a pair of _λ_ c-bit seeds, in order to initialize the protocol
that realizes _F_ Zero. Our signing protocol is very simple. Each pair of parties
performs two VOLE evaluations, and each party _Pi_ commits and releases _Ri_


11They specify only that the random oracle can be used to compress the value denoted
in their paper as **v**, but do not give specifics. We assume that a seed is used to generate a
random vector, and the single Z _q_ element is used to adjust that vector such that it meets the
constraints that they require.


65


and transmits **Γ** [u] _i,j_ [,] **[ Γ]** [v] _i,j_ [,] _**[ ψ]**_ _i,j_ [,][ pk] _i_ [,] _[ w][i]_ [, and] _[ u][i]_ [to every] _[ P][j]_ [such that] _[ j][ ̸]_ [=] _[ i]_ [. This]
gives us a total average per-party bandwidth cost of


SignCost( _t, λ_ c _, λ_ s _, κ, |G|_ ) _�→_

( _t −_ 1) _·_ (4 _λ_ c + 3 _κ_ + 4 _|G|_ + 2 _·_ VOLECost( _λ_ c _, λ_ s _, κ,_ 2))


Finally, each party must perform 6 _t −_ 2 elliptic curve scalar operations in
order to generate a signature. To set up their VOLE instances (for all counterparties), each party must perform 6 _λ_ c _·_ ( _n −_ 1) scalar operations. To generate a
shared keypair, each party must perform at most 2 _t_ scalar operations.


**8.5** **Concrete Results**


In table 1, we substitute values into the above equations to derive the concrete
average per-party bandwidth costs for common security parameters. We assume
that point compression is used for elements of G, such that they require only
one byte more than elements of Z _q_ . [12] In all cases, we assume that _κ_ = 2 _λ_ c
and _λ_ s = 80. Note that the seeds used to initialize the VOLE protocol and
the protocol that realized _F_ Zero can be combined, which implies that the cost
of VOLE setup (and therefore the overall setup cost) is the same regardless of
which VOLE method is used.
For comparison, when _λ_ c = 256 and _λ_ s = 80, the 2-of- _n_ signing protocol of
Doerner et al. [DKLs18] requires each party to send 116.4 KiB (on average),
whereas our new protocol (with our new DKLs-derivedVOLE) requires only
49.7 KiB per party to be sent. On the other hand, our new protocol has the
same communication pattern as theirs (under pipelining), requires fewer elliptic curve scalar operations than theirs does, [13] realizes a standard functionality,
whereas their functionality allows the adversary to bias _R_, and achieves statistical security, whereas theirs is secure only assuming that the computational
Diffie-Dellman problem is hard in G and that ECDSA is a signature scheme
over _G_ . We therefore claim that our protocol is strictly superior to the original
2-of- _n_ DKLs protocol.
The _t_ -of- _n_ protocol of Doerner et al. [DKLs19] requires ( _t −_ 1) _·_ 88 _._ 3 KiB
to be sent by each party (on average) when the ( _⌈_ log2( _t_ ) _⌉_ + 6)-round variant is
used. [14] Our new protocol requires only ( _t −_ 1) _·_ 49 _._ 7 KiB to be sent, has only
three rounds (or two, if pipelining is employed), and achieves statistical security
if the VOLE is ideal, whereas theirs is secure assuming that the computational
Diffie-Hellman problem is hard in G. However, their protocol requires each
party to compute only 6 elliptic curve scalar operations during signing, and
ours requires 6 _t −_ 2. Given the efficiency of elliptic curve operations on modern
hardware, and the additional latency incurred by additional parties, we believe


12This is not true of elliptic curves in general, but is true of the ones over which ECDSA is
most commonly deployed.
13While their protocol only requires 9 such operations as implemented, achieving UCsecurity for their protocol requires a straight-line extractable proof of knowledge [Fis05, Ks22],
which requires many more.
14Their 10-round variant requires more bandwidth, but they do not give a precise figure.


66


our new protocol to have the advantage in nearly any real-world deployment
scenario.


_λ_ c 128 192 256

_κ_ 256 384 512
_|G|_ 264 392 520
Setup ( _n −_ 1) _·_ 137232 ( _n −_ 1) _·_ 304144 ( _n −_ 1) _·_ 536592
Signing (our VOLE) ( _t −_ 1) _·_ 406752 ( _t −_ 1) _·_ 812864 ( _t −_ 1) _·_ 1354144
Signing (HMRT22) ( _t −_ 1) _·_ 392544 ( _t −_ 1) _·_ 742400 ( _t −_ 1) _·_ 1194656


**Table 1: Bandwidth Costs**, in total bits transmitted per party, for _t_ signers
out of _n_ total parties. We assume the worst-case cost for setup; i.e. _t_ = _n_ . Note
that in all cases, the statistical parameter _λ_ s = 80.

## **9 A Two-Round Protocol for Honest Majorities**


When the number of corrupt parties is strictly less than _t/_ 2, a much simpler protocol is possible than the one presented in section 3, leveraging honest-majority
techniques for significant bandwidth and round-efficiency improvements. In
spite of its simplicity, we present it here for the sake of completeness, and give
a provisional theorem.


**Theorem** **9.1** (Informal Honest-Majority Security Theorem) **.** _When_
( _t_ choose _⌈t/_ 2 _⌉_ ) _∈_ poly( _λ_ ) _, there exists a two-round protocol that UC-_
_realizes F_ ECDSA( _G, n, t_ ) _against a malicious adversary that statically corrupts_
_fewer than t/_ 2 _parties, assuming the existence of pseudo-random functions._


The protocol begins by sampling _replicated_ secret shares of sk, _r_, _ζ_ = 0,
and _ϕ_, with a reconstruction threshold of _⌈t/_ 2 _⌉_ . To non-interactively generate
replicated secret shares of zero, there is a direct extension of the protocol we have
given for realizing _F_ Zero in section 3.1. To non-interactively sample replicated
secret shares of a _uniform_ value, one can use a classic protocol of Cramer,
Damgård, and Ishai [CDI05]: simply replicate shares of a seed, and use a PRF
to expand the replicated seeds when necessary.
It is possible to perform multiplications of the shared values in replicated
form; however, the output shares would also be replicated and therefore inefficient to send. Instead, the parties non-interactively convert their replicated sharings into Shamir sharings of degree _⌈t/_ 2 _⌉−_ 1 via another technique of Cramer,
Damgård, and Ishai [CDI05], and then perform a standard non-interactive multiplication (as in the BGW protocol [BGW88], without degree-reduction) to
compute Shamir shares of _u_ and _v_ . The latter sharings are of degree _t −_ 1 if _t_
is odd, or _t −_ 2 if _t_ is even. Following this, a non-interactive linear combination
yields Shamir shares of _w_ .


67


The final honest-majority protocol, then, is two rounds: the parties perform
all of the non-interactive operations specified above, and swap degree-( _⌈t/_ 2 _⌉−_ 1)
shares shares of _R_ over G. They check that these shares lie on a polynomial of the
correct degree, and if so, then they interpolate _R_ and use _r_ [x] to compute shares
of _w_, which they swap. These are interpolated and the signature assembled and
verified.
Honest-majority techniques make our consistency check and the commitand-release mechanism for _R_ superfluous. Since the honest parties’ shares fully
specify _R_, any attempt by the adversary to bias this value will result in a
polynomial of incorrect degree, which can be detected. Since the multiplication operations are completely non-interactive, any cheating on the part of the
adversary _must_ be independent of the honest parties’ secrets, and therefore expressable in terms of simple linear offsets relative to the expected values, which
can be perfectly detected by verifying the signature, just as in the protocol from
section 3. In terms of communication, each party must only send a single share
of _R_ to the others, followed by one share each of _u_ and _w_ ; thus, when _κ_ = 256,
the total amount of data sent by every party to each of the others is 776 bits.
Note that in the above scheme, the size of each replicated secret share is a
factor of ( _t_ choose _⌈t/_ 2 _⌉_ ) greater than the size of an ordinary additive share.
In the case that this yields impractically large shares, Shamir sharing can be
used throughout the protocol, and sharings of zero and uniform values can be
sampled interactively via the well-known techniques of Feldman [Fel87] and
Pedersen [Ped91]. Under this modification, the protocol requires three rounds.

## **Acknowledgements**


The authors of this work are supported by NSF grants 1646671, 1816028,
and 2055568, by the ERC projects NTSC (742754), SPEC (803096), and HSS
(852952), by ISF grant 2774/2, by AFOSR award FA9550-21-1-0046, by the
Azrieli Foundation, by the Brown University Data Science Institute, and by the
Carlsberg Foundation under the Semper Ardens Research Project CF18-112
(BCM).

## **References**


[ADI [+] 17] Benny Applebaum, Ivan Damgård, Yuval Ishai, Michael Nielsen,
and Lior Zichron. Secure arithmetic computation with constant
computational overhead. In _Advances in Cryptology – CRYPTO_
_2017, part I_, 2017.


[ANO [+] 22] Damiano Abram, Ariel Nof, Claudio Orlandi, Peter Scholl, and
Omer Shlomovits. Low-bandwidth threshold ECDSA via pseudorandom correlation generators. In _Proceedings of the 43rd IEEE_
_Symposium on Security and Privacy (S&P)_, 2022.


68


[BB89] Judit Bar-Ilan and Donald Beaver. Non-cryptographic fault-tolerant
computing in constant number of rounds of interaction. In _Proceed-_
_ings of the 8th Annual ACM Symposium on Principles of Distributed_
_Computing (PODC)_, 1989.


[BCG [+] 19] Elette Boyle, Geoffroy Couteau, Niv Gilboa, Yuval Ishai, Lisa
Kohl, and Peter Scholl. Efficient pseudorandom correlation generators: Silent OT extension and more. In _Advances in Cryptology_

_– CRYPTO 2019, part III_, 2019.


[BCGI18] Elette Boyle, Geoffroy Couteau, Niv Gilboa, and Yuval Ishai. Compressing vector OLE. In _Proceedings of the 25th ACM Conference_
_on Computer and Communications Security (CCS)_, 2018.


[BCK [+] 22] Mihir Bellare, Elizabeth C. Crites, Chelsea Komlo, Mary Maller,
Stefano Tessaro, and Chenzhi Zhu. Better than advertised security
for non-interactive threshold signatures. In _Advances in Cryptology_

_– CRYPTO 2022, part IV_, 2022.


[BDM22] Pedro Branco, Nico Döttling, and Paulo Mateus. Two-round oblivious linear evaluation from learning with errors. In _Proceedings of_
_the 25th International Conference on the Theory and Practice of_
_Public-Key Cryptography (PKC), part I_, 2022.


[BDOZ11] Rikke Bendlin, Ivan Damgård, Claudio Orlandi, and Sarah Zakarias.
Semi-homomorphic encryption and multiparty computation. In _Ad-_
_vances in Cryptology – EUROCRYPT 2011_, 2011.


[BGG17] Dan Boneh, Rosario Gennaro, and Steven Goldfeder. Using level-1
homomorphic encryption to improve threshold DSA signatures for
bitcoin wallet security. 2017.


[BGW88] Michael Ben-Or, Shafi Goldwasser, and Avi Wigderson. Completeness theorems for non-cryptographic fault-tolerant distributed computation (extended abstract). In _Proceedings of the 20th Annual_
_ACM Symposium on Theory of Computing (STOC)_, 1988.


[BLS01] Dan Boneh, Ben Lynn, and Hovav Shacham. Short signatures from
the weil pairing. In _Advances in Cryptology – ASIACRYPT 2001_,
2001.


[BP23] Luís T. A. N. Brandão and René Peralta. NISTIR 8214c ipd NIST
first call for multi-party threshold schemes (initial public draft). In
_Computer Security Resource Center_, 2023.


[Can01] Ran Canetti. Universally composable security: A new paradigm for
cryptographic protocols. In _Proceedings of the 42nd Annual Sympo-_
_sium on Foundations of Computer Science (FOCS)_, 2001.


69


[CCD [+] 20] Megan Chen, Ran Cohen, Jack Doerner, Yashvanth Kondi, Eysa
Lee, Schuyler Rosefield, and abhi shelat. Multiparty generation of
an RSA modulus. In _Advances in Cryptology – CRYPTO 2020, part_
_III_, 2020.


[CCL [+] 20] Guilhem Castagnos, Dario Catalano, Fabien Laguillaumie, Federico
Savasta, and Ida Tucker. Bandwidth-efficient threshold EC-DSA.
In _Proceedings of the 23rd International Conference on the Theory_
_and Practice of Public-Key Cryptography (PKC), part II_, 2020.


[CCL [+] 23] Guilhem Castagnos, Dario Catalano, Fabien Laguillaumie, Federico
Savasta, and Ida Tucker. Bandwidth-efficient threshold EC-DSA revisited: Online/offline extensions, identifiable aborts proactive and
adaptive security. _Theoretical Computer Science_, 939, 2023.


[CDI05] Ronald Cramer, Ivan Damgård, and Yuval Ishai. Share conversion,
pseudorandom secret-sharing and applications to secure computation. In _Proceedings of the 2nd Theory of Cryptography Conference_
_(TCC)_, 2005.


[CGG [+] 20] Ran Canetti, Rosario Gennaro, Steven Goldfeder, Nikolaos
Makriyannis, and Udi Peled. UC non-interactive, proactive, threshold ECDSA with identifiable aborts. In _Proceedings of the 27th ACM_
_Conference on Computer and Communications Security (CCS)_,
2020.


[CHI [+] 21] Megan Chen, Carmit Hazay, Yuval Ishai, Yuriy Kashnikov, Daniele
Micciancio, Tarik Riviere, Abhi Shelat, Muthu Venkitasubramaniam, and Ruihan Wang. Diogenes: Lightweight scalable RSA modulus generation with a dishonest majority. 2021.


[CL15] Guilhem Castagnos and Fabien Laguillaumie. Linearly homomorphic encryption from DDH. In _Proceedings of the Cryptographers’_
_Track at the RSA Conference (CT-RSA)_, 2015.


[CLOS02] Ran Canetti, Yehuda Lindell, Rafail Ostrovsky, and Amit Sahai.
Universally composable two-party and multi-party secure computation. In _Proceedings of the 34th Annual ACM Symposium on Theory_
_of Computing (STOC)_, 2002.


[CMI93] Manuel Cerecedo, Tsutomu Matsumoto, and Hideki Imai. Efficient
and secure multiparty generation of digital signatures based on discrete logarithms. In _IEICE TRANSACTIONS on Fundamentals of_
_Electronics, Communications and Computer Sciences, Vol.E76-A,_
_No.4, pp.532-545_, 1993.


[CRR21] Geoffroy Couteau, Peter Rindal, and Srinivasan Raghuraman. Silver: Silent VOLE and oblivious transfer from hardness of decoding
structured LDPC codes. In _Advances in Cryptology – CRYPTO_
_2021, part III_, 2021.


70


[CSW20] Ran Canetti, Pratik Sarkar, and Xiao Wang. Blazing fast OT for
three-round UC OT extension. In _Proceedings of the 23rd Interna-_
_tional Conference on the Theory and Practice of Public-Key Cryp-_
_tography (PKC), part II_, 2020.


[DJN [+] 20] Ivan Damgård, Thomas Pelle Jakobsen, Jesper Buus Nielsen,
Jakob Illeborg Pagter, and Michael Bæksvang Østergaard. Fast
threshold ECDSA with honest majority. 2020.


[dJV21] Leo de Castro, Chiraag Juvekar, and Vinod Vaikuntanathan. Fast
vector oblivious linear evaluation from ring learning with errors.
In _Proceedings of the 9th on Workshop on Encrypted Computing &_
_Applied Homomorphic Cryptography (WAHC)_, 2021.


[DKL [+] 23] Jack Doerner, Yashvanth Kondi, Eysa Lee, abhi shelat, and LaKyah
Tyner. Threshold BBS+ signatures for distributed anonymous credential issuance. In _Proceedings of the 44th IEEE Symposium on_
_Security and Privacy (S&P)_, 2023.


[DKLs18] Jack Doerner, Yashvanth Kondi, Eysa Lee, and abhi shelat. Secure
two-party threshold ECDSA from ECDSA assumptions. In _Proceed-_
_ings of the 39th IEEE Symposium on Security and Privacy (S&P)_,
2018.


[DKLs19] Jack Doerner, Yashvanth Kondi, Eysa Lee, and abhi shelat. Threshold ECDSA from ECDSA assumptions: The multiparty case. In
_Proceedings of the 40th IEEE Symposium on Security and Privacy_
_(S&P)_, 2019.


[DKLs24] Jack Doerner, Yashvanth Kondi, Eysa Lee, and abhi shelat. Threshold ECDSA in three rounds. In _Proceedings of the 45th IEEE Sym-_
_posium on Security and Privacy (S&P)_, 2024.


[DOK [+] 20] Anders P. K. Dalskov, Claudio Orlandi, Marcel Keller, Kris
Shrishak, and Haya Shulman. Securing DNSSEC keys via threshold ECDSA from generic MPC. In _Proceedings of the 25th European_
_Symposium on Research in Computer Security (ESORICS), Part II_,
2020.


[DPSZ12] Ivan Damgård, Valerio Pastro, Nigel P. Smart, and Sarah Zakarias.
Multiparty computation from somewhat homomorphic encryption.
In _Advances in Cryptology – CRYPTO 2012_, 2012.


[Fel87] Paul Feldman. A practical scheme for non-interactive verifiable secret sharing. In _Proceedings of the 28th Annual Symposium on Foun-_
_dations of Computer Science (FOCS)_, 1987.


[Fis05] Marc Fischlin. Communication-efficient non-interactive proofs of
knowledge with online extractors. In _Advances in Cryptology –_
_CRYPTO 2005_, 2005.


71


[FLOP18] Tore Kasper Frederiksen, Yehuda Lindell, Valery Osheter, and
Benny Pinkas. Fast distributed RSA key generation for semi-honest
and malicious adversaries. In _Advances in Cryptology – CRYPTO_
_2018, part II_, 2018.


[GG18] Rosario Gennaro and Steven Goldfeder. Fast multiparty threshold
ECDSA with fast trustless setup. In _Proceedings of the 25th ACM_
_Conference on Computer and Communications Security (CCS)_,
2018.


[GGN16] Rosario Gennaro, Steven Goldfeder, and Arvind Narayanan.
Threshold-optimal DSA/ECDSA signatures and an application to
bitcoin wallet security. 2016.


[Gil99] Niv Gilboa. Two party RSA key generation. In _Advances in Cryp-_
_tology – CRYPTO 1999_, 1999.


[GJKR96] Rosario Gennaro, Stanislaw Jarecki, Hugo Krawczyk, and Tal Rabin. Robust threshold DSS signatures. In _Advances in Cryptology –_
_EUROCRYPT 1996_, 1996.


[GL05] Shafi Goldwasser and Yehuda Lindell. Secure multi-party computation without agreement. _Journal of Cryptology_, 18(3), 2005.


[GMW87] Oded Goldreich, Silvio Micali, and Avi Wigderson. How to play any
mental game or A completeness theorem for protocols with honest
majority. In _Proceedings of the 19th Annual ACM Symposium on_
_Theory of Computing (STOC)_, 1987.


[GS22a] Jens Groth and Victor Shoup. Design and analysis of a distributed ECDSA signing service. Cryptology ePrint Archive, Paper
2022/506, 2022.


[GS22b] Jens Groth and Victor Shoup. On the security of ECDSA with
additive key derivation and presignatures. In _Advances in Cryptology_

_– EUROCRYPT 2022, part I_, 2022.


[HLNR23] Iftach Haitner, Yehuda Lindell, Ariel Nof, and Samuel Ranellucci.
Fast secure multiparty ecdsa with practical distributed key generation and applications to cryptocurrency custody. Cryptology ePrint
Archive, Paper 2018/987, Version 20230529:135032, 2023.


[HMRT12] Carmit Hazay, Gert Læssøe Mikkelsen, Tal Rabin, and Tomas Toft.
Efficient RSA key generation and threshold paillier in the two-party
setting. In _Proceedings of the Cryptographers’ Track at the RSA_
_Conference (CT-RSA)_, 2012.


[HMRT22] Iftach Haitner, Nikolaos Makriyannis, Samuel Ranellucci, and Eliad
Tsfadia. Highly efficient OT-based multiplication protocols. In _Ad-_
_vances in Cryptology – CRYPTO 2022, part I_, 2022.


72


[IKNP03] Yuval Ishai, Joe Kilian, Kobbi Nissim, and Erez Petrank. Extending
oblivious transfers efficiently. In _Advances in Cryptology – CRYPTO_
_2003_, 2003.


[IN96] Russell Impagliazzo and Moni Naor. Efficient cryptographic schemes
provably as secure as subset sum. _Journal of Cryptology_, 9(4), 1996.


[KOS15] Marcel Keller, Emmanuela Orsini, and Peter Scholl. Actively secure
OT extension with optimal overhead. In _Advances in Cryptology –_
_CRYPTO 2015, part I_, 2015.


[KOS16] Marcel Keller, Emmanuela Orsini, and Peter Scholl. MASCOT:
faster malicious arithmetic secure computation with oblivious transfer. In _Proceedings of the 23th ACM Conference on Computer and_
_Communications Security (CCS)_, 2016.


[Ks22] Yashvanth Kondi and abhi shelat. Improved straight-line extraction
in the random oracle model with applications to signature aggregation. In _Advances in Cryptology – ASIACRYPT 2022, part II_,
2022.


[Lan95] Susan K. Langford. Threshold dss signatures without a trusted
party. In _Advances in Cryptology – CRYPTO 1995_, 1995.


[Lin17] Yehuda Lindell. Fast secure two-party ECDSA signing. In _Advances_
_in Cryptology – CRYPTO 2017, part II_, 2017.


[Lin21] Yehuda Lindell. Secure multiparty computation. _Communications_
_of the ACM_, 64(1), 2021.


[Lin22] Yehuda Lindell. Simple three-round multiparty schnorr signing with
full simulatability. Cryptology ePrint Archive, Paper 2022/374,
2022.


[LN18] Yehuda Lindell and Ariel Nof. Fast secure multiparty ECDSA with
practical distributed key generation and applications to cryptocurrency custody. In _Proceedings of the 25th ACM Conference on Com-_
_puter and Communications Security (CCS)_, 2018.


[MR01] Philip D. MacKenzie and Michael K. Reiter. Two-party generation
of DSA signatures. In _Advances in Cryptology – CRYPTO 2001_,
2001.


[MR19] Daniel Masny and Peter Rindal. Endemic oblivious transfer. In
_Proceedings of the 26th ACM Conference on Computer and Com-_
_munications Security (CCS)_, 2019.


[Nat13] National Institute of Standards and Technology. FIPS PUB 186[4: Digital Signature Standard (DSS). http://nvlpubs.nist.gov/](http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf)
[nistpubs/FIPS/NIST.FIPS.186-4.pdf, 2013.](http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf)


73


[NRS21] Jonas Nick, Tim Ruffing, and Yannick Seurin. Musig2: Simple
two-round schnorr multi-signatures. In _Advances in Cryptology –_
_CRYPTO 2021, part I_, 2021.


[Pai99] Pascal Paillier. Public-key cryptosystems based on composite degree residuosity classes. In _Advances in Cryptology – EUROCRYPT_
_1999_, 1999.


[Pas03] Rafael Pass. On deniability in the common reference string and
random oracle model. In _Advances in Cryptology – CRYPTO 2003_,
2003.


[Ped91] Torben P. Pedersen. Non-interactive and information-theoretic secure verifiable secret sharing. In _Advances in Cryptology – CRYPTO_
_1991_, 1991.


[Roy22] Lawrence Roy. SoftSpokenOT: Communication-computation tradeoffs in OT extension. In _Advances in Cryptology – CRYPTO 2022,_
_part I_, 2022.


[Sch89] Claus-Peter Schnorr. Efficient identification and signatures for smart
cards. In _Advances in Cryptology – CRYPTO 1989_, 1989.


[SGRR19] Phillipp Schoppmann, Adrià Gascón, Leonie Reichert, and Mariana Raykova. Distributed vector-ole: Improved constructions and
implementation. In _Proceedings of the 26th ACM Conference on_
_Computer and Communications Security (CCS)_, 2019.


[ST19] Nigel P. Smart and Younes Talibi Alaoui. Distributing any elliptic
curve based protocol. In _IMA International Conference on Cryptog-_
_raphy and Coding_, 2019.


[YWL [+] 20] Kang Yang, Chenkai Weng, Xiao Lan, Jiang Zhang, and Xiao Wang.
Ferret: Fast extension for correlated OT with small communication.
In _Proceedings of the 27th ACM Conference on Computer and Com-_
_munications Security (CCS)_, 2020.


74


