# Efficient Pseudorandom Correlation Generators: Silent OT Extension and More

**Authors:** Elette Boyle, Geoffroy Couteau, Niv Gilboa, Yuval Ishai, Lisa Kohl, Peter Scholl

**Published:** CRYPTO 2019

**ePrint:** https://eprint.iacr.org/2019/448

---

# **Efficient Pseudorandom Correlation Generators:** **Silent OT Extension and More [∗]**

Elette Boyle [1], Geoffroy Couteau [2], Niv Gilboa [3], Yuval Ishai [4],
Lisa Kohl [2], and Peter Scholl [5]


1 IDC Herzliya
2 Karlsruhe Institute of Technology
3 Ben-Gurion University of the Negev
4 Technion
5 Aarhus University


**Abstract.** Secure multiparty computation (MPC) often relies on sources of correlated randomness
for better efficiency and simplicity. This is particularly useful for MPC with no honest majority,
where input-independent correlated randomness enables a lightweight “non-cryptographic” online
phase once the inputs are known. However, since the amount of correlated randomness typically
scales with the circuit size of the function being computed, securely generating correlated randomness forms an efficiency bottleneck, involving a large amount of communication and storage.
A natural tool for addressing the above limitations is a _pseudorandom correlation generator_ (PCG).
A PCG allows two or more parties to securely generate long sources of useful correlated randomness
via a local expansion of correlated short seeds and no interaction. PCGs enable MPC with _silent_
_preprocessing_, where a small amount of interaction used for securely sampling the seeds is followed
by silent local generation of correlated pseudorandomness.
A concretely efficient PCG for Vector-OLE correlations was recently obtained by Boyle et al. (CCS
2018) based on variants of the learning parity with noise (LPN) assumption over large fields. In
this work, we initiate a systematic study of PCGs and present concretely efficient constructions for
several types of useful MPC correlations. We obtain the following main contributions:


**– PCG foundations.** We give a general security definition for PCGs. Our definition suffices
for any MPC protocol satisfying a stronger security requirement that is met by existing protocols. We prove that a stronger security requirement is indeed necessary, and justify our PCG
definition by ruling out a stronger and more natural definition.

**– Silent OT extension.** We present the first concretely efficient PCG for oblivious transfer correlations. Its security is based on a variant of the binary LPN assumption and any correlationrobust hash function. We expect it to provide a faster alternative to the IKNP OT extension
protocol (Crypto ’03) when communication is the bottleneck. We present several applications,
including protocols for non-interactive zero-knowledge with bounded-reusable preprocessing
from binary LPN, and concretely efficient related-key oblivious pseudorandom functions.

**– PCGs for simple 2-party correlations.** We obtain PCGs for several other types of useful
2-party correlations, including (authenticated) one-time truth-tables and Beaver triples. While
the latter PCGs are slower than our PCG for OT, they are still practically feasible. These
PCGs are based on a host of assumptions and techniques, including specialized homomorphic
secret sharing schemes and pseudorandom generators tailored to their structure.

**– Multiparty correlations.** We obtain PCGs for multiparty correlations that can be used
to make the circuit-dependent communication of MPC protocols scale _linearly_ (instead of
quadratically) with the number of parties.


**1** **Introduction**


Correlated secret randomness is a valuable resource for secure multi-party computation (MPC).
A simple example is a common random key that is given to two parties, who can later use
it as a one-time pad for secure message transmission. In the context of MPC, a more useful
example is a random _oblivious transfer_ (OT) correlation, in which one party is given a pair of
random bits (more generally, strings) ( _s_ 0 _, s_ 1) and the other party is given the pair ( _r, sr_ ) for
a random bit _r_ . The OT correlation can serve as a basis for general MPC protocols with no
honest majority [GMW87, Kil88, IPS08]. Other kinds of two-party correlations that are useful


_∗_ This is a full version of [BCG+19].


for MPC include _oblivious linear-function evaluation_ (OLE) correlations [NP06,IPS09,ADI [+] 17],
_multiplication triples_ (also known as “Beaver triples”) [Bea91, BDOZ11, DPSZ12], and _one-time_
_truth tables_ [IKM [+] 13, DNNR17, DKS [+] 17].
The above types of correlated randomness are commonly used to implement efficient MPC
protocols in the _preprocessing model_ . Such protocols consist of an offline, input-independent
_preprocessing phase_, where many independent instances of the correlated randomness are generated, followed by a fast _online phase_ that consumes this correlated randomness for the purpose of
securely evaluate a given function of the inputs. In many cases, the online phase is “informationtheoretic” [6] and its computational complexity is only a small-constant times higher than that of
an insecure function evaluation. Most importantly for the present work, the online phase of such
protocols typically outperforms all competing approaches in terms of concrete efficiency.
A major challenge in implementing such offline-online protocols is that the preprocessing
phase needs to _securely_ generate and store a large amount of correlated randomness. This is
typically done by using a special-purpose interactive MPC protocol, which involves a significant
amount of communication and computation for each gate of a circuit that should be evaluated
in the online phase. A dream goal would be to replace this source of correlated randomness
with _short_ correlated seeds, which can be “silently” expanded _without any interaction_ to produce
a large amount of _pseudorandom_ correlated randomness. This process should emulate an ideal
process for generating the target correlation not only from the point of view of outsiders, but
also from the point of view of _insiders_ who can observe the correlated seeds. We refer to such
an object as a _pseudorandom correlation generator_, or PCG for short.


A bit more precisely, a two-party PCG is defined as follows. Let ( _R_ 0 _, R_ 1) be a target correlation, defined by some efficient sampling algorithm _C_ that on input 1 _[λ]_ outputs a pair of
correlated strings ( _r_ 0 _, r_ 1). For instance, _C_ (1 _[λ]_ ) may output _n_ = _λ_ [3] independent instances of an
OT correlation. A PCG is a pair of efficient algorithms (Gen _,_ Expand) such that:


**–** Gen samples a pair of short correlated seeds (k0 _,_ k1) _←_ $ Gen(1 _λ_ ),

**–** Expand is a _local_ deterministic seed expansion algorithm mapping k _i_ to _ri ←_ Expand( _i,_ k _i_ ),
where _|ri| > |_ k _i|_ .


We would like the outputs ( _r_ 0 _, r_ 1) resulting from this process to be “indistinguishable” from an
ideal sample ( _R_ 0 _, R_ 1) generated by _C_ (1 _[λ]_ ), even to a party who receives one of the seeds k _b_ .
A useful special case of PCG was recently considered by Boyle et al. [BCGI18], who constructed (under variants of the Learning Parity with Noise assumption [BFKL93]) a concretely
efficient PCG for the _vector OLE_ (VOLE) correlation. The VOLE correlation over a field F
samples a random scalar _x ∈_ F and vectors _**u**_ _,_ _**v**_ _∈_ F _[n]_, and outputs _r_ 0 = ( _**u**_ _,_ _**v**_ ) to one party (the
“sender”) and _r_ 1 = ( _x,_ _**w**_ = _**u**_ _x_ + _**v**_ ) to the other party (the “receiver”). The VOLE correlation is
useful for secure computation of functions that employ scalar-vector products over large fields,
such as ones arising in the context of linear algebra and keyword search [ADI [+] 17].
Designing efficient PCGs for a wider class of correlations is strongly motivated by the goal
of improving the efficiency of _general_ MPC in the preprocessing model, where the preprocessing
phase is used to securely generate the PCG seeds. We refer to this as _MPC with silent prepro-_
_cessing_ . More concretely, such a protocol consists of three phases: (1) an interactive _setup phase_
for securely distributing the seed generation algorithm Gen; in the end of this phase, which
involves a small amount of communication, only the short seeds are stored for later use; (2) a
silent _seed expansion_ phase, where the seeds are expanded into long correlated randomness via
a local computation of Expand and without any interaction; (3) a final _online phase_ where the
correlated randomness is consumed to evaluate a given function of the inputs. One could employ
Phase 1 when deciding that an MPC interaction _might_ take place in the future, Phase 2 when


6 This can be formalized by requiring that the joint states of the parties in the end of the offline phase can
be swapped by _computationally indistinguishable_ states, given which the online protocol is secure against
computationally unbounded parties.


2


interaction seems likely to take place in the near future, and Phase 3 to carry out the MPC interaction once the inputs are available. The low communication footprint of silent preprocessing
can eliminate traffic analysis attacks that anticipate future MPC plans. Finally, another benefit
of the PCG-based approach is that it can help reduce the cost of protecting MPC protocols
against malicious parties. Indeed, since Phase 2 does not involve any interaction, it suffices to
protect Phase 1 and Phase 3 against malicious parties, which is typically much cheaper.
Several different kinds of PCG constructions are implicit in the MPC literature. These include PCGs for simple multi-party linear correlations from any pseudorandom generator [GI99,
CDI05], for general correlations from indistinguishability obfuscation [HW15, HIJ [+] 16], for socalled “bilinear” correlations from homomorphic secret sharing [BCG [+] 17], for restricted variants
of OT correlations from key-homomorphic pseudorandom functions [Sch18] and, most recently,
for VOLE correlation from LPN [BCGI18]. With the exception of linear multi-party correlations [GI99, CDI05] and VOLE correlations [BCGI18], none of these prior constructions seem
appealing from a practical point of view. In particular, there was no prior approach (even a
heuristic one) for constructing a concretely efficient PCG for OT correlations.


**1.1** **Our Contributions**


In this work, we initiate a more systematic study of pseudorandom correlation generators. Our
contributions are on both the foundational side, where we present new definitions, impossibility
results and connections with other primitives, and the applied side, with concretely efficient
constructions for commonly used MPC correlations, including OT correlations and others. Our
most practical PCG constructions handle restricted (yet still useful) classes of correlations, while
our more general constructions can handle much larger classes of correlations, at the expense
of a bigger seed size and higher computational costs (and, for some of them, public-key-style
assumptions such as lattice-based or pairing-based cryptography).
We now give a more detailed account of our contributions. Unless noted otherwise, we refer
to MPC with computational security against semi-honest (i.e., passive) and static (i.e., nonadaptive) adversaries who may corrupt an arbitrary subset of parties.


**1.1.1** **Foundations of Pseudorandom Correlation Generators**


Our first goal is to present a general security definition for the intuitive notion of PCG described
above. As pointed out in [GI99], this is not quite as straightforward as one might imagine, and
previous works side-stepped the problem by taking an ad-hoc approach. To motivate our general
definition, we start by discussing the most natural alternative.


**Ruling Out a Simulation-Based Definition.** Recall that the ultimate desire would be that
in any protocol, one can securely replace an ideal correlated randomness functionality _C_ with
pseudo-randomness obtained from expanding the correlated seeds of a PCG for _C_ . This would
indeed follow from a natural simulation-based security definition for PCG as a computationally secure, dealer-assisted protocol for computing the randomized functionality defined by _C_ .
Concretely, in the two-party case, the simulation-based definition requires the existence of a
simulator _S_ such that the _real_ distribution (k _b,_ Expand(k1 _−b_ )), where (k0 _,_ k1) are generated by
Gen (capturing the view of a corrupted party _b_ jointly with the output of the uncorrupted party
1 _−b_ ) is computationally indistinguishable from the _ideal_ distribution ( _S_ ( _rb_ ) _, r_ 1 _−b_ ), where ( _r_ 0 _, r_ 1)
are sampled by _C_ . Unfortunately, we show (building on [HW15], and extending an informal argument from [GI99]) that such a definition is impossible to realize even for simple correlations.
Intuitively, the impossibility follows from the fact that in the real distribution k _b_ “explains” the
output of the honest party in an efficiently verifiable way, whereas such an explanation of _r_ 1 _−b_
cannot be generated from _rb_ in the ideal distribution.


3


**A General PCG Definition.** To get around the above impossibility, we present a relaxed
indistinguishability-based definition of PCG security, generalizing the specialized security definition for the VOLE correlation from [BCGI18]. Our definition requires that given its PCG
key k _b_, corrupted party _b_ cannot distinguish the _true_ expanded output of the honest party
_r_ 1 _−b_ = Expand(1 _−_ _b,_ k1 _−b_ ) from a _random_ output _r_ 1 _−b_ consistent with the correlation _C_ and its
own expanded output _rb_ = Expand( _b,_ k _b_ ). In other words, we replace the ideal distribution in the
above simulation-based definition by (k _b,_ [ _r_ 1 _−b | Rb_ = Expand(k _b_ )]). Note that the latter distribution involves reverse-sampling from _R_ 1 _−b_ conditioned on a fixed value for _Rb_, which may not
be well-defined. However, in this work we only consider _additive_ correlations, where ( _R_ 0 _, R_ 1) are
additive secret shares (over a finite Abelian group) of a sample from some core distribution. For
such additive correlations, the reverse-sampling is well-defined and is computationally efficient.
More broadly, our general PCG definition is meaningful when this reverse-sampling is efficient.


**Limitations.** Our PCG definition is not good enough for generating correlated randomness in _all_
applications. Indeed, the impossibility of the simulation-based definition discussed above implies
such simple counterexamples for randomized functionalities. Concretely, for any _C_ to which the
impossibility result applies, there is a trivial MPC protocol for _C_ given correlated randomness
from _C_ in which each party outputs its correlated randomness. However, the impossibility result
shows that using _any_ PCG for _C_ would render this simple protocol insecure. We show, under
standard cryptographic assumptions, that a similar impossibility holds even if one restricts
attention to MPC for _deterministic_ functionalities. Concretely, we show a protocol which uses
correlated randomness _C_ to realize a deterministic functionality with statistical security against
malicious parties, but which becomes completely _insecure_ (even against semi-honest parties)
when _C_ is replaced by a specific PCG for _C_ that meets our indistinguishability-based definition.


**A Plug-and-Play Use of PCG.** We complement the above negative results by a positive
result, showing that our PCG definition does suffice to imply our “ultimate desire” in the context
of most applications. Concretely, we put forward a slightly stronger security requirement for MPC
with preprocessing, such that in any protocol satisfying this requirement, a PCG can be used as
a drop-in replacement for correlated randomness. The stronger security requirement asserts that
security still hold even if the ideal correlation functionality ( _R_ 0 _, R_ 1) is replaced by a _corruptible_
functionality that allows corrupted party _b_ to pick its own randomness _rb_ _[∗]_ [, and then delivers to the]
uncorrupted party a sample _r_ 1 _−b_ from the conditional distribution [ _r_ 1 _−b | Rb_ = _rb_ _[∗]_ []][. It fortunately]
turns out that natural MPC protocols in the preprocessing model already satisfy this stronger
security requirement. This allows for a plug-and-play use of PCGs in many application scenarios.


**Relation with Homomorphic Secret Sharing.** A (two-party) homomorphic secret sharing
(HSS) scheme [BGI16a, BGI [+] 18] for a function class _F_ splits a secret _x_ into two shares ( _x_ 0 _, x_ 1),
such that given any _f ∈F_ one can efficiently evaluate _additive_ shares of _f_ ( _x_ ) via local computation on the shares. We show a two-way relation between PCG and HSS. First, we show that a
PCG for any _additive_ correlation (as defined above) can be reduced to HSS for a related function
class _F_, generalizing and formalizing a previous observation from [BCG [+] 17]. In particular, HSS
for general circuits implies PCG for all additive correlations, which include most of the useful
MPC correlations as special cases. (This is only a feasibility result, which does not directly
imply concretely efficient constructions.) Second, we show that some converse is also true: a
PCG for the degree- _d_ “tensoring” correlation, obtained by picking a random vector _X ∈R_ _[n]_ and
outputting additive shares of all products of at most _d_ entries of _X_, implies HSS for the class _F_
of degree- _d_ ( _n_ -variate) polynomials over _R_ _[n]_, where the share size grows linearly with _n_ and the
homomorphic evaluation time grows linearly with _n_ _[d]_ .


4


**1.1.2** **Silent OT Extension**


A central contribution of this work is the first _concretely efficient_ construction of PCG for the
oblivious transfer (OT) correlation. From an asymptotic point of view, our PCG can achieve
an arbitrary polynomial stretch, assuming: (1) The _binary_ Learning Parity with Noise (LPN)
assumption [BFKL93] with a conservative choice of parameters, and (2) A correlation-robust
hash function [IKNP03]. The hash function primitive, which is only used in a black-box way, can
be instantiated in practice by a general-purpose hash function or block cipher. Assuming LPN
with a linear number of samples and inverse-polynomial noise rate holds for the dual of a nearlinear time encodable code (such as the codes proposed in [HKL [+] 12, DI14, ABD [+] 16, ADI [+] 17]),
which is still a conservative assumption, the _computational_ complexity of Expand is nearly linear
in the output length. [7]

In a nutshell, our efficient PCG for OT applies the PCG for VOLE from [BCGI18] over a
large extension field F2 _λ_, except for restricting the sender’s output _**u**_ to be over the base field.
This yields _n_ correlated instances of random OT that can be converted into standard OT by
using a correlation-robust hash function, as in [IKNP03]. See Section 2 for more details.
By applying a secure two-party protocol for distributing Gen, we obtain a _silent OT extension_
protocol that generates _n_ pseudo-random OT instances using a small number of OTs, with a
total of _O_ ( _n_ _[ϵ]_ ) bits of communication for any _ϵ >_ 0. This should be compared with existing OT
extension protocols [Bea96, IKNP03] that do not require the LPN assumption but where the
communication complexity is bigger than _n_ .


**Concrete Efficiency.** Our LPN-based PCG for OT is very attractive in terms of concrete
efficiency, and we expect it to outperform state-of-the-art OT extension protocols [IKNP03,
ALSZ13,KK13] in settings where communication is the bottleneck. To give a few data points, our
PCG can expand a pair of seeds of length 10KB into a million instances of random 128-bit stringOT, of total size 16MB (receiver) and 32MB (sender), in an estimated [8] time of around a second
on a single core of a modern CPU. Alternatively, seeds of length 7KB can be expanded into 65
thousand OTs at roughly half the amortized computational cost. Factoring in the cost of securely
distributing Gen (with semi-honest security, building on [Ds17]), the amortized communication
complexity of our silent OT extension protocol is 0–3 bits _for each random 128-bit string-OT_ . To
put that into context, state-of-the-art OT extension protocols [IKNP03,ALSZ13] require 128 bits
of communication per random 128-bit string-OT and can generate around 10 million OTs per
second [GKWY19] over a fast network, so the price we pay for the (much) lower communication
complexity seems quite modest. Even for the easier case of random _bit_ -OT, the best previous
OT extension protocol [KK13] required roughly 80 bits of communication per OT.


**1.1.3** **Other PCG Constructions**


We present an assortment of practically feasible PCGs for other useful two-party correlations,
based on a variety of underlying tools and assumptions.


**– PCG for Constant-Degree Polynomials from LPN.** We show that a generalization
of the LPN-based VOLE generator from [BCGI18] can be used to obtain a PCG for any
constant-degree additive correlation, namely a correlation that additively secret-shares a
vector of degree- _d_ polynomials of a random _X ∈_ F _[n]_ for some constant _d ≥_ 2. This PCG
relies on LPN over F in a similar noise regime as the PCG for OT from Section 1.1.2. In fact,
by increasing the computation time (but still keeping it polynomial), one can use the LPN


7 In Section 1.1.3 below we describe an alternative LPN-based approach to constructing PCG for OT that
dispenses with assumption (2), but requires at least quadratic computation in the output length _n_ .
8 We caution that we have not implemented our constructions. Our estimates are based on counting basic
operations and estimating their cost; the actual running times may vary due to other costs we neglected such
as cache misses. We leave the task of optimizing and implementing our constructions to future work.


5


assumption in a parameter regime that is not known to imply public-key encryption [Ale03],
let alone OT. The main caveat is that even for generating simple degree- _d_ correlations, such
as _Ω_ ( _n_ ) Beaver triples ( _d_ = 2), the _computational_ complexity of Expand is bigger than _n_ _[d]_ .
While much slower than our PCG for OT, this construction may still be practically feasible
for _d_ = 2 even with reasonably large _n_ . We leave the question of obtaining more efficient
variants of this construction to future work.


As discussed in Section 1.1.1, this PCG construction implies (2-party) HSS schemes for
constant-degree polynomials from LPN. By additionally assuming a standard OT protocol, it implies secure two-party computation protocols for constant-degree polynomials in
which the communication complexity is nearly linear in the input size. Using the techniques
from [BGI16a, Cou19], it also implies an “almost-sublinear” general secure computation protocol: for any constant _c >_ 1 and layered boolean circuit of size _s_ (and assuming binary LPN
and OT), there is a secure two-party computation protocol with polynomial computation
and total communication bounded by _s/c_ . We stress again that these are mainly feasibility
results because of the high computational cost of this PCG construction.


**– PCG for One-Time Truth Tables from any PRG.** One-time truth tables (OTTT) are a
type of correlation that allow secure evaluation of a public lookup table in MPC, on a secretshared input [IKM [+] 13, DNNR17, DKS [+] 17], and are well-suited to computations such as the
S-box of AES. For MPC with active security, the correlation outputs need to be authenticated with information-theoretic MACs, as in the recent TinyTable protocol [DNNR17]. We
present a very simple PCG for authenticated OTTT using only a distributed point function
(DPF) [GI14, BGI16b], which in turn can be efficiently constructed from any pseudorandom generator (PRG). This PCG follows naturally from a building block of the silent OT
extension construction (as we explain in Section 2). It compresses the storage cost of an
authenticated OTTT from _O_ ( _λn_ ) bits down to _O_ ( _λ_ log _n_ ) bits, for a table of size _n_, giving
a reduction in size of over 20x for a length-256 table such as the AES S-box. There is a
concretely efficient protocol to distribute the seed generator Gen with semi-honest security
by using the distributed DPF key generation protocol from [Ds17]. While a similar protocol with malicious security is considerably more expensive, even a naive approach based
on general-purpose secure computation (e.g., using recent protocols such as [KRRW18]) is
feasible in practice, enabling the compressed storage benefit of the PCG-based approach.


**– PCGs from Homomorphic Secret Sharing.** We give practically feasible PCG constructions for OLE and (authenticated) Beaver triple correlations, which are useful for
arithmetic MPC protocols such as SPDZ [DPSZ12]. For these constructions we use HSS
based on ring-LWE [BGV12, DHRW16, BKS19] and the BGN (pairing-based) cryptosystem [BGN05, BGI16a, BCG [+] 17]. To expand the seeds, we rely on a multivariate quadratic
(MQ) assumption based PRG, which limits the stretch to sub-quadratic, but allows for reasonable computational efficiency. For example, with our ring-LWE-based PCG we estimate
that one should be able to expand a pair of 3GB seeds into 17GB of authenticated Beaver
triples in a 128-bit field, at a rate of around 6 thousand triples per second; various tradeoffs
are possible between seed size and computation time, and we also explore an iterative variant which produces triples in small batches. Securely computing Gen to distribute the seeds
is relatively cheap compared to the expansion phase, and the overall performance should
be comparable to recent work on actively secure triple generation with much more interaction [KPR18]. With BGN, we estimate around 200ms for computing an OLE correlation over
Z _N_ for small _N_ (say, _N <_ 10). Although much more expensive than our silent OT extension,
an advantage of the ring-LWE-based constructions, beyond the richer class of correlations,
is that they can be extended to the _multi-party_ setting, as we discuss next.


6


**1.1.4** **PCGs for Multi-Party Correlations**


Finally, we present a general transformation for extending certain classes of PCGs from the
2-party to the multi-party setting. This can be applied to PCGs for simple bilinear correlations,
including VOLE and Beaver triples, giving the first non-trivial, efficient PCG constructions in
the multi-party setting. The transformation applies to most of our 2-party PCGs, including the
LPN-based PCG for constant-degree correlations.
On top of the silent preprocessing feature, an appealing application of our multi-party PCGs
is in obtaining secure _M_ -party computation protocols with _total_ communication complexity
_O_ ( _Ms_ + _M_ [2] _· s_ _[ϵ]_ ) (for circuit size _s_ and constant 0 _< ϵ <_ 1). The _O_ ( _Ms_ ) term is the cost of the
(information-theoretic) online phase, and the _O_ ( _M_ [2] _·s_ _[ϵ]_ ) term is the cost of distributing the PCG
seed generation, which is the only part of the protocol requiring pairwise communication. This
should be contrasted with OT-based MPC protocols, which have total communication complexity
_Ω_ ( _M_ [2] _s_ ) [GMW87,HOSS18] . Protocols with such communication complexity (without the silent
preprocessing feature) could previously be based on different flavors of somewhat homomorphic
encryption [FH96, CDN01, DPSZ12]. We get the first such protocol that only relies on LPN and
OT, and the first practically feasible protocol that has sublinear-communication offline phase
and information-theoretic online phase.


**Table 1.** Summary of the New PCG Constructions


PCG Section 5 Section B Section 6 Section 4.4 Sections 7.3,C,D,E Sections 7.4,F


Assumption LPN PRG [*] LPN deg- _d_ HSS + MQ/LPN SXDH + LPN LWE + MQ


Correlations OT [*] OTTT [*] deg- _d_ degree- _d/_ 2 small-ring deg-2 deg- _d_


Efficiency 1M OT/s _[†]_ - - - 5 OLE/s _[‡]_ 7000 ABT/s [**]


Multiparty
(bilinear corr.)


  - PRG stands for an arbitrary pseudorandom generator, OT for random oblivious transfer, and OTTT for
authenticated one-time truth-table correlation.

_†_ Estimated (approximate) cost over one core of a standard laptop, with average communication of 2.6 bits/OT.
See Tables 3 and 4.

_‡_ Estimated (approximate) cost over one core of a standard laptop, for OLE correlation over a small (constant
size) ring. See Section E.3, and Tables 9 and 10.
** ABT stands for authenticated Beaver triple. Estimated (approximative) cost over one core of a standard
laptop. See Table 2.


**1.1.5** **Additional Applications**


From our silent OT extension protocol, we obtain the following additional results:


**–** _Oblivious Pseudorandom Functions (OPRFs)._ An OPRF [FIPR05] is a two-party protocol
for securely evaluating a pseudorandom function, whose key is known by one party, on a
secret input known by the second party. OPRFs serve as the main building blocks in recent
protocols for private set intersection [KKRT16]. Our silent OT construction can be used
to obtain a form of batch OPRF with cost as little as 1 bit of communication per OPRF
evaluation on a random input, leading to around a factor two reduction in communication
for these protocols.

**–** _Reusable-Preprocessing NIZK._ Consider the following setting for non-interactive zero knowledge (NIZK) with reusable interactive setup: In an offline setup phase, before the statements
to be proved are known, the prover and the verifier interact to securely generate correlated
random seeds. The seeds can then be used to prove any polynomial number of statements by


7


having the prover send a single message to the verifier for each statement. Such a notion was
recently constructed in [BCGI18], building on [CDI [+] 18], using their PCG for VOLE. Our
silent OT extension can be used to obtain an improved reusable-preprocessing NIZK system
for NP, under the standard LPN assumption over F2. As compared to the reusable NIZK
of [BCGI18], our NIZK relies on a more standard assumption (LPN over F2 versus large F),
and the setup cost is independent of both the number of statements and their size (whereas
in [BCGI18], the setup cost was independent of the number of statements, but grows linearly
with a bound on their size). On the down side, our OT-based NIZK protocols do not have
the computational complexity advantages of the VOLE-based constructions from [BCGI18].

**–** _Efficient Secure Matrix Multiplication._ As a stepping stone towards silent OT extension, we
construct a PCG for a generalization of VOLE called _subfield VOLE_ . This can be seen as
a form of batch VOLE where the _**u**_ value is reused across several instances, and can be
applied to compute secret-shared tensor products and matrix multiplication more efficiently.
Compared with naively using a PCG for standard VOLE, we reduce the seed size by at least
a _O_ (log _n_ ) factor.


Finally, our PCG for OTTT yields the following application.


**–** _Improved 2-PC with Sublinear Online Communication._ Standard approaches to secure computation with preprocessing (e.g., SPDZ) still require online communication that is linear in the circuit size. Recently, Couteau [Cou19] demonstrated asymptotic feasibility of
information-theoretic secure 2-party computation (2-PC) in the preprocessing model for a
natural class of circuits (namely, “layered” circuits), with sublinear online communication,
_O_ ( _s/_ log log _s_ ) for circuit size _s_ . However, this comes at the cost of generating and storing
_O_ ( _s_ [2] ) bits of correlated randomness.
Our compressed one-time truth-table (OTTT) construction allows one to match the asymptotic complexity of [Cou19], while reducing the amount of correlated randomness from
quadratic to quasilinear in the circuit size, in exchange for settling for computational security and assuming the existence of one-way functions.


**1.2** **Paper Organization**


We begin in Section 2 with an overview of our techniques, followed by preliminaries in Section 3.
In Section 4, we present our PCG definition and foundational results. Section 5 contains our
silent OT extension construction, and applications to OPRFs and NIZK from LPN. Section 6
provides an LPN-based construction of PCG for general constant-degree correlations. We then
present generic constructions of PCGs from specific classes of PRGs (Section 4.4); we instantiate
this framework for more complex correlations based on group-based and lattice-based HSS, in
Section 7.3 and Section 7.4, respectively. Finally, in Section 8 we construct general, multi-party
PCGs for simple bilinear correlations based on any “programmable” 2-party PCG.


**2** **Technical Overview of Constructions**


In this section we give a high-level overview of the techniques that underly our different PCG
constructions.


**2.1** **Background**


Our PCG constructions rely on different types of _homomorphic secret sharing_ (HSS) and _function_
_secret sharing_ (FSS) schemes. Informally, HSS is a form of secret sharing that allows a secret
_x_ to be split up into shares k0 _,_ k1, such that a party holding k _i_ can _locally_ obtain an additive
secret share of _f_ ( _x_ ), for some function _f_ . FSS is the dual notion: starting with a function _f_, and


8


splitting into shares _f_ 0 _, f_ 1 such that each share _fi_ hides _f_, but can be used to obtain an additive
sharing of _f_ ( _x_ ) for some public input _x_ . [9] FSS for a class of point functions (i.e., functions _f_
which evaluate to 0 on all but a single input) is called a _distributed point function_ [GI14], and
can be constructed very efficiently based on a pseudorandom generator (PRG) [BGI16b]. There
are HSS constructions for branching programs based on DDH [BGI16a] or lattices [BKS19], or
general circuits from strong forms of fully homomorphic encryption [DHRW16].


**2.2** **Overall methodology**


At a high level, our constructions can all be seen as examples of the following blueprint: construct
an HSS scheme that can homomorphically evaluate the composition of a pseudorandom generator
(PRG) with a function _f_ that uses the expanded randomness to compute the desired correlation.
This can be used to obtain PCGs for any _additive_ correlation; i.e., that outputs random additive
shares of some distribution. Of course, the main challenge lies in instantiating this _efficiently_,
since plugging in even a low-degree PRG to an off-the-shelf HSS scheme is typically not practical.
We instead use specialized HSS constructions that pair well with our carefully chosen PRGs.
As a stepping stone, our constructions implicitly construct a _compressible_ form of HSS,
which allows the sharing of inputs from some distribution _D_, such that the share size is _smaller_
_than_ an uncompressed output of _D_, and we can still compute some useful function _f_ on the
expanded inputs. We typically choose _D_ to be a sparse distribution on vectors, or another
similarly compressible distribution. We then convert these long _D_ -vectors to slightly shorter (but
still long) _random_ -looking vectors, by homomorphically multiplying by a compressive linear map.
Under a suitable LPN-type assumption, this combination of expanding the compressed _D_ -vector
followed by linear compression acts as a PRG in the above blueprint, and we can proceed to
homomorphically compute the desired correlation.
For example, when _D_ samples a sparse, low-weight vector _**e**_ over F2, and the linear map
is a random matrix _H_, then distinguishing ( _H,_ _**e**_ _· H_ ) from random is as hard as the problem
of decoding a random binary linear code, which corresponds to the standard LPN assumption [BFKL93, Ale03]. Another example is when _D_ outputs a _tensor product_ of two short, uniform vectors. Recovering the short vectors given only ( _**x**_ _⊗_ _**y**_ ) _· H_ is the problem of solving a
random system of multivariate quadratic equations (MQ problem), which is believed to be hard
for a suitable choice of parameters [MI88, Wol05, BGP06, AHI [+] 17]. In particular, the decision
version of MQ is polynomially reducible to its search version [BGP06].
We remark that the resulting PRGs do not necessarily conform to standard metrics of simplicity, such as low degree or low locality, and in isolation may appear somewhat unnatural.
This exemplifies an interesting observation that “HSS-friendliness” may indeed be a new type of
metric that does not directly align with those previously studied.


**2.3** **Silent OT Extension**


As a building block for silent OT extension, we start by constructing a PCG for a two-party
correlation we call _subfield vector oblivious linear evaluation_ (subfield VOLE). This correlation
works over a field F _q_, and a subfield F _p_, where _q_ = _p_ _[r]_ . It first samples a random _x ∈_ F _q_,
_**u**_ _∈_ F _[n]_ _p_ _[,]_ _**[ v]**_ _[ ∈]_ [F] _[n]_ _q_ [, then outputs][ (] _**[u]**_ _[,]_ _**[ v]**_ [)][ to the sender and][ (] _[x,]_ _**[ w]**_ [ =] _**[ u]**_ _[x]_ [ +] _**[ v]**_ [)][ to the receiver.][10][ Our]
construction is a generalization of the vector-OLE construction from [BCGI18]: when _p_ = _q_ the
correlation is exactly vector-OLE, but using _q > p_ opens up additional applications. For example,
viewing _x ∈_ F _q_ as a vector _**x**_ _∈_ F _[r]_ _p_ [, subfield VOLE can be seen as computing additive shares of]
the _r × n_ tensor product _**x**_ _⊗_ _**u**_, which can be useful for secure two-party matrix multiplication,


9 FSS is actually equivalent to HSS for a related class of functions, but we differentiate between the two for
convenience, depending on the applications.
10 We view elements of F _p_ embedded into F _q_ throughout, so that the multiplication _**u**_ _· x_ happens over F _q_ .


9


and other linear algebra tasks. Compared with using _r_ copies of VOLE [BCGI18] to achieve the
same task, we reduce the seed size by a _O_ (log _n_ ) factor and obtain more efficient computation.
To build a PCG for subfield VOLE, we consider a compressible distribution _D_ that outputs
random sparse vectors of weight _t_ and length _n_ _[′]_ . First, notice that we can compress a secretsharing of the _j_ -th unit vector _**e**_ _j ∈{_ 0 _,_ 1 _}_ _[n][′]_, using a distributed point function (DPF) for the
point ( _j,_ 1): evaluating a DPF key on input _i_ produces a random share of 0 on all inputs except
_i_ = _j_, where it outputs a share of 1. Hence, performing all _n_ _[′]_ evaluations results in shares of the
entire vector _**e**_ _j_ . This easily extends to weight _t_ vectors, by naively using _t_ DPFs and summing up
the shares of the _t_ unit vectors (this step can be optimized with a multi-point DPF as described
in [BCGI18]).
Although it may appear that this only allows us to compress sparse vectors, and not perform
any useful HSS computations afterwards, we observe that with a small tweak we can use this to
build HSS for the family of randomized functions


_F_ = _{fH_ : F _q →_ F _[n]_ _q_ _[, x][ �→]_ _[x][ ·]_ _**[ e]**_ _[ ·][ H][ |]_ _**[ e]**_ _←HW_ $ _t, H ∈_ F _np_ _[′]_ _×n}_ (1)

where _HW_ _t_ is the distribution that outputs a random weight- _t_ vector over F _[n]_ _p_ _[′]_ [(with each entry]
either 0 or uniform). We remark that a naive description of the class _F_ gives functions with
very high degree, which could _not_ be evaluated using simple HSS schemes, which highlights the
importance of tailoring a specific solution.
To upgrade the above sketch to get HSS for _F_, we make one small modification: using _t_ DPFs
that output shares over F _q_, we specify the _i_ -th DPF by the point ( _ji, yi · x_ ) for some random
index _ji_ and _yi ∈_ F _[∗]_ _p_ [, instead of][ (] _[j][i][,]_ [ 1)][ as before. When evaluating the DPFs, the parties now]
obtain additive shares of _**e**_ _· x_, where _**e**_ contains all _t yi_ ’s in random positions. Since additive
secret sharing is linear, any linear map _H_ can then be locally applied on the shares.
If _H ∈_ F _[n]_ _p_ _[′][×][n]_ is a compressive linear map with _n < n_ _[′]_, the vector _**u**_ = _**e**_ _· H_ is pseudorandom
under a suitable form of the LPN (or syndrome decoding) assumption. Concretely, we require
that a _t_ -noisy random codeword in the code whose _parity check_ matrix is _H_ is pseudorandom.
This immediately yields a subfield VOLE generator, where each party’s seed contains a set of
DPF seeds, and the sender additionally gets the points ( _ji, yi_ ), and the receiver gets _x_, since
additive shares of _x_ _·_ _**u**_ can be locally converted to the ( _**v**_ _,_ _**w**_ ) components of a VOLE correlation.
Our next observation, inspired by the OT extension protocol of Ishai et al. [IKNP03], is that
subfield VOLE already gives as a restricted form of oblivious transfer, known as correlated OT
or _∆_ -OT. If we run subfield VOLE over F2, embedded in F2 _[r]_, then the VOLE sender obtains
$ $ $
a set of pairs _ui_ _←_ F2 _, vi_ _←_ F2 _r_, while the VOLE receiver gets _x_ _←_ F2 _r_ and _wi_ = _x · ui_ + _vi_,
for _i_ = 1 _, . . ., n_ . Now switch the roles of sender and receiver, so the VOLE sender becomes an
OT receiver with choice bit _ui_ and string _vi_ . If _ui_ = 0 then _vi_ = _wi_, whilst if _ui_ = 1 then
_vi_ = _wi −_ _x_, hence, this is exactly a 1-out-of-2 OT where the OT sender’s (formerly VOLE
receiver’s) messages are all of the form ( _wi, wi −_ _x_ ).
On its own, this type of _∆_ -OT is already useful for many applications such as garbled circuits
and secure computation with information-theoretic MACs [WRK17a, NNOB12]. However, most
importantly, following [IKNP03], the parties can locally convert such a correlated OT into an
OT on random strings, using a hash function that is pseudorandom under correlated inputs.
This gives us a PCG for random oblivious transfer, where the seed size is essentially that of _t_
distributed point functions, or _O_ ( _tλ_ log _n_ ) bits. Combining this with an efficient secure protocol
for setting up a pair of DPF keys [Ds17], we obtain our silent OT extension protocol, which
produces _n_ pseudorandom string-OTs with _o_ ( _n_ ) bits of communication.


**2.4** **One-Time Truth Tables**


We next show how to adapt the above approach to produce authenticated, one-time truth table
correlations, which can be used to efficiently perform table lookups in MPC [IKM [+] 13,DNNR17,


10


DKS [+] 17]. This construction is straightforward given the above description of our subfield-VOLE
generator, so we informally explain it here and defer the complete description to Section B of
the Appendix.
The correlation we want to produce, for a lookup table _T_ : [ _n_ ] _→{_ 0 _,_ 1 _}_ _[m]_, is an additive
secret-sharing of


        - _α, {yi, γi}i∈_ [ _n_ ]� where _yi_ = _T_ ( _s_ + _i_ mod _n_ ) _, γi_ = _yi · α ∈_ F2 _λ_ (2)


$ $
for _α_ _←_ F2 _λ, s_ _←_ [ _n_ ]. Here, the _yi_ ’s are equal to _T_ shifted by a random offset _s_, while the _γi_ ’s are
information-theoretic MACs on _yi_ under the key _α_, used to obtain active security in the MPC
protocol.
Our starting point is the observation from [KOR [+] 17] that the _yi_ ’s can be generated locally,
given secret-shares of a random unit vector. This is because, if _**e**_ _s ∈{_ 0 _,_ 1 _}_ _[n]_ is the _s_ -th unit
vector, then we have



_T_ ( _s_ + _i_ mod _n_ ) =



_n_


_**e**_ _s_ [ _j_ ] _· T_ ( _i_ + _j_ mod _n_ )

_j_ =1



which is linear in _**e**_ _s_ . We can further obtain the _γi_ ’s (namely, the authenticated _γi_ = _yi · α_ ) if we
additionally have secret-shares of the corresponding scaled vector _α ·_ _**e**_ _s_ .
The core observation is that a DPF gives precisely a _compressed_ secret sharing of such a
secret vector (1 _||α_ ) _·_ _**e**_ _s ∈_ ( _{_ 0 _,_ 1 _}_ [1+] _[λ]_ ) _[n]_ : requiring only _O_ ( _λ_ log _n_ ) bits in the place of _O_ ( _λn_ ).
More concretely, this leads to the following, simple approach for a PCG to generate shares of
(2): use the previous DPF-based construction of HSS for the family in (1) over F2, with _t_ = 1,
$
_x_ = (1 _∥α_ ) for _α_ _←_ F2 _λ_, and _H_ the linear map induced by _T_ in the equation above. The resulting
PCG has seed size essentially the same as one DPF, which is _O_ ( _λ_ log _n_ ) bits. This gives a large
compression over the previous, practical approach from [DNNR17], which required _O_ ( _λn_ ) bits
per table. Expanding the PCG is relatively cheap in practice, since in 2-PC applications only
a single entry of each table is ever used, and this can be computed on-the-fly with _O_ ( _n_ ) PRG
evaluations.

A downside of this construction is that it seems difficult to produce the necessary PCG seeds
with good concrete efficiency in the malicious setting, since the only known approach in this
setting requires evaluating a PRG inside 2-PC [Ds17]. However, our result is still interesting for a
preprocessing phase with semi-honest security, or when a trusted dealer is present. Alternatively,
if one can afford the cost of distributing Gen with malicious security via general-purpose 2-PC,
the resulting correlated seeds only require a small amount of storage, and their local expansion
is (automatically) secure against malicious parties.


**2.5** **PCGs for Constant-Degree Polynomials from LPN**


We construct PCGs for constant-degree polynomials, using again function secret sharing for
multi-point functions together with LPN. At a high level, the construction builds upon the fact
that given two sparse vectors _**a**_ _,_ _**b**_, their tensor product _**a**_ _⊗_ _**b**_ is sparse as well, hence shares of
_**a**_ _⊗_ _**b**_ can be compressed using an FSS, as for vector-OLE generators and silent OT extension.
Then, a compressive mapping can be applied to obtain _**x**_ _⊗_ _**y**_ from _**a**_ _⊗_ _**b**_, where _**x**_ = ( _**a**_ _· H_ )
and _**y**_ = ( _**b**_ _· H_ ) are _pseudorandom_ under the LPN assumption, thanks to the bilinearity of the
tensor product (and linearity of _H_ ). This immediately leads to a PCG for bilinear functions,
which can be easily generalized to a PCG for constant-degree polynomials. However, the share
size grows as _O_ ( _t_ _[d]_ ), where _t_ is the number of noisy coordinates in the LPN instance, and _d_ is
the degree of the polynomial. The computation cost grows as _O_ ( _n_ [2] _[d]_ ), where _n_ is the input size.


11


**2.6** **PCGs from Ring-LWE and BGN-based HSS**


We construct PCGs for more general two-party correlations, building upon the specific structure of homomorphic encryption-based HSS schemes [DHRW16, BKS19] and group-based HSS
schemes [BGI16a, BGI17, BCG [+] 17]. Our key observation is that in both HSS schemes encodings
of large pseudorandom strings can be compressed efficiently using an “HSS-friendly PRG” as described in Section 2.2. For the ring-LWE based construction, we obtain compression with a PRG
based on the multivariate quadratic equations problem, and present several ways of optimizing
this with batching techniques for homomorphic encryption, which lead to different tradeoffs for
seed size and computational cost.
The group-based approach requires more involved techniques: The underlying HSS scheme
uses two types of encodings, where so-called level-1 encodings are ElGamal ciphertexts, and level2 encodings are shares of sk _·_ _**x**_ for a vector _**x**_, where sk is the secret key of the homomorphic
encryption scheme. Then, a special HSS operation allows to compute level-2 encodings of bilinear
functions applied to a level-1 encoding and a level-2 encoding. Using two parallel instances of
the PCG for vector-OLE of [BCGI18] allows us to efficiently compress shares of _**y**_ and sk _·_ _**y**_,
where _**y**_ is a pseudorandom vector and sk is a shared value, to only _O_ ( _λt_ log _n_ ) bits, under
the LPN assumption with _t_ noisy coordinates. Furthermore, encrypting short random sparse
vectors suffices for homomorphically evaluating a specific LPN-based PRG directly on the level1 encodings, as long as they support evaluation of degree-2 functions. This can be ensured by
using BGN-style pairing-based encryption for the group-based HSS. Since the HSS comes with
an inverse-polynomial error probability, we further develop a new method to efficiently remove
the faulty outputs, building upon our silent OT extension protocol.
For both schemes, we discuss various optimizations and provide detailed efficiency estimations.


**2.7** **Multi-Party PCGs**


As our final contribution, we construct _multi-party_ PCGs for a useful class of bilinear correlations.
Concretely, for a given bilinear map _e_ : G1 _×_ G2 _→_ G _T_, we consider _M_ -party correlations of the
form _{_ ( _ai, bi, ci_ ) _}i∈_ [ _M_ ], consisting of additive secret shares of random elements _a ∈_ G1, _b ∈_ G2,
and their image _c_ = _e_ ( _a, b_ ) _∈_ G _T_ . For appropriate choice of groups and bilinear operation, this
captures _M_ -party OT, _M_ -party vector OLE, _M_ -party Beaver triples, and more.
Our construction approach provides a semi-generic transformation from any PCG for a corresponding _2-party_ correlation _{_ ( _a, c_ 1) _,_ ( _b, c_ 2) _}_ for random _a, b_, and _c_ 1 + _c_ 2 = _e_ ( _a, b_ ), if the
PCG satisfies an additional programmability property. Roughly, this property requires a way of
“reusing” the inputs _a_ and _b_ across instances without compromising security.
The _M_ -party construction leverages this structure by executing _M_ ( _M −_ 1) pairwise instances
of the underlying 2-party PCG, for all the “cross-terms.” Namely, we think of each _ai_ and _bi_ from
the final _M_ -party correlation as playing the role of _a_ or _b_ in the 2-party correlation, with all
possible partners. The desired _M_ -party additive shares _ci_ can then be derived by combining _cii_ =
_aibi_ (computable locally) together with _{cij, cji}j∈_ [ _M_ ] _\{i}_ resulting from the 2-party correlations
for pairs ( _ai, bj_ ) and ( _aj, bi_ ). The resulting _M_ -party PCG keys consist of _M_ ( _M −_ 1) keys from
the 2-party PCG, together with short expandable shares of 0 for rerandomization.
We observe that the necessary programmability property is satisfied by our subfield VOLE
construction and the 2-party VOLE PCG from [BCGI18], as well as the 2-party bilinear PCGs
constructed in this work (including OT and Beaver triples) from group-based and lattice-based
HSS (Section 7) and from LPN (Section 6). As a corollary, we obtain _M_ -party variants of
these correlations with quadratic blowup in computation and share size. Interestingly, our silent
OT extension construction does _not_ seem to support the necessary programmability, since the
resulting sender message pairs are implicitly defined as a function of the receiver’s bit selections.


12


**3** **Preliminaries**


We say that a function negl : N _→_ R [+] is _negligible_ if it vanishes faster than every inverse polynomial. For two families of distributions _X_ = _{Xλ}_ and _Y_ = _{Yλ}_ indexed by a security parameter
c
_λ ∈_ N, we write _X_ _≈_ _Y_ if _X_ and _Y_ are _computationally indistinguishable_ (namely, any family of
s
circuits of size poly( _λ_ ) has a negligible distinguishing advantage), _X_ _≈_ _Y_ if they are _statistically_
_indistinguishable_ (namely, the above holds for arbitrary distinguishers), and _X ≡_ _Y_ if the two
families are identically distributed.


**Notation.** We usually denote matrices with capital letters ( _A, B, C_ ) and vectors with bold
lowercase ( _**x**_ _,_ _**y**_ ). By default, vectors are assumed to be row vectors. We write _A|i,j_ to denote the
entry ( _i, j_ ) of a matrix _A_ . Given a vector _**x**_ of length _|_ _**x**_ _|_ = _n_, the notation HW ( _x_ ) denotes the
Hamming weight _**x**_, _i.e._, the number of its nonzero entries. Given a distribution _D_, we denote
by Im( _D_ ) the image of _D_ (i.e., its support set).


**3.1** **Function Secret Sharing**


Informally, an FSS scheme for a class of functions _C_ is a pair of algorithms FSS = (FSS _._ Gen _,_ FSS _._ Eval)
such that:


**–** FSS _._ Gen given a function _f ∈C_ outputs a pair of keys ( _K_ 0 _, K_ 1);,

**–** FSS _._ Eval, given _Kb_ and input _x_, outputs _yb_ such that _y_ 0 and _y_ 1 form additive shares of _f_ ( _x_ ).


The security requirement is that each key _Kb_ computationally hide _f_, except for revealing the
input and output domains of _f_ . We formalize this below.


**Definition 1 (Function Secret Sharing; adapted from [BGI16b]).** _A_ 2 _-party_ function
secret sharing _(FSS) scheme for a class of functions C_ = _{f_ : _I →_ G _} with input domain I and_
_output domain an abelian group_ (G _,_ +) _, is a pair of PPT algorithms_ FSS = (FSS _._ Gen _,_ FSS _._ Eval)
_with the following syntax:_

**–** FSS _._ Gen(1 _[λ]_ _, f_ ) _, given security parameter λ and description of a function f ∈C, outputs a_
_pair of keys_ ( _K_ 0 _, K_ 1) _;_

**–** FSS _._ Eval( _b, Kb, x_ ) _, given party index b ∈{_ 0 _,_ 1 _}, key Kb, and input x ∈_ _I, outputs a group_
_element yb ∈_ G _._

_Given an allowable leakage function_ Leak : _{_ 0 _,_ 1 _}_ _[∗]_ _→{_ 0 _,_ 1 _}_ _[∗]_ _, the scheme_ FSS _should satisfy the_
_following requirements:_

**– Correctness:** _For any f_ : _I →_ G _in C and x ∈_ _I, we have_ Pr[( _K_ 0 _, K_ 1) _←_ $ FSS _._ Gen(1 _λ, f_ ) :

 _b∈{_ 0 _,_ 1 _}_ [FSS] _[.]_ [Eval][(] _[b, K][b][, x]_ [) =] _[ f]_ [(] _[x]_ [)] = 1] _[.]_

**– Security:** _For any b ∈{_ 0 _,_ 1 _}, there exists a PPT simulator_ Sim _such that for any polynomial-_
_size function sequence fλ ∈C, the distributions {_ ( _K_ 0 _, K_ 1) _←_ $ FSS _._ Gen(1 _λ, fλ_ ) : _Kb} and_
_{Kb_ _←_ $ Sim(1 _λ,_ Leak( _fλ_ )) _} are computationally indistinguishable._


_Unless otherwise specified, we assume that for f_ : _I →_ G _, the allowable leakage_ Leak( _f_ ) _outputs_
( _I,_ G) _, namely a description of the input and output domains of f_ _._


_Remark 2._ In any FSS scheme for a sufficiently rich class of functions (including point functions), each of the two evaluation functions _FK_ _[b]_ [(] _[x]_ [) =][ FSS] _[.]_ [Eval][(] _[b, K, x]_ [)][ is a pseudorandom func-]
tion [BGI15]. Some of our constructions will use this property.


Some applications of FSS require applying the evaluation algorithm on _all inputs_ . Following [BGI16b, BCGI18], given an FSS scheme (FSS _._ Gen _,_ FSS _._ Eval), we denote by FSS _._ FullEval an
algorithm which, on input a bit _b_, and an evaluation key _Kb_ (which defines the input domain _I_ ),
outputs a list of _|I|_ elements of G corresponding to the evaluation of FSS _._ Eval( _b, Kb, ·_ ) on every
input _x ∈_ _I_ (in some predetermined order). While FSS _._ FullEval can always be realized with _|I|_
invocations of FSS _._ Eval, it is typically possible to obtain a more efficient construction. Below,
we recall some results from [BGI16b] on FSS schemes for useful classes of functions.


13


**3.1.1** **Distributed Point Functions**


A distributed point function (DPF) [GI14] is an FSS scheme for the class of point functions
_fα,β_ : _{_ 0 _,_ 1 _}_ _[ℓ]_ _→_ G which satisfy _fα,β_ ( _α_ ) = _β_, and _fα,β_ ( _x_ ) = 0 for any _x ̸_ = _α_ . A sequence of
works [GI14, BGI15, BGI16b] has led to highly efficient constructions of DPF schemes from any
pseudorandom generator (PRG), which can be implemented in practice using block ciphers such
as AES.


**Theorem 3 (PRG-based DPF [BGI16b], Theorems 3.3 and 3.4).** _Given a PRG G_ :
_{_ 0 _,_ 1 _}_ _[λ]_ _→{_ 0 _,_ 1 _}_ [2] _[λ]_ [+2] _, there exists a DPF for point functions fα,β_ : _{_ 0 _,_ 1 _}_ _[ℓ]_ _→_ G _with key size_
_ℓ_ _·_ ( _λ_ + 2) + _λ_ + _⌈_ log2 _|_ G _|⌉_ _bits. For m_ = _⌈_ [log] _λ_ +2 _[ |]_ [G] _[|]_ _[⌉][, the key generation algorithm]_ [ Gen] _[ invokes][ G][ at]_

_most_ 2( _ℓ_ + _m_ ) _times, the evaluation algorithm_ Eval _invokes G at most ℓ_ + _m times, and the full_
_evaluation algorithm_ FullEval _invokes G at most_ 2 _[ℓ]_ (1 + _m_ ) _times._


Note that a naive construction of FullEval from Eval would require 2 _[ℓ]_ ( _ℓ_ + _m_ ) invocations of
_G_ .


**3.1.2** **FSS for Multi-Point Functions**


Similarly to [BCGI18], we use FSS for _multi-point functions_ . A _k_ -point function evaluates to 0
everywhere, except on _k_ specified points. When specifying multi-point functions we often view
the domain of the function as [ _n_ ] for _n_ = 2 _[ℓ]_ instead of _{_ 0 _,_ 1 _}_ _[ℓ]_ .


**Definition 4 (Multi-Point Function [BCGI18]).** _An_ ( _n, t_ ) _-multi-point function over an_
_abelian group_ (G _,_ +) _is a function fS,_ _**y**_ : [ _n_ ] _→_ G _, where S_ = ( _s_ 1 _, · · ·, st_ ) _is an ordered sub-_
_set of_ [ _n_ ] _of size t and_ _**y**_ = ( _y_ 1 _, · · ·, yt_ ) _∈_ G _[t]_ _, defined by fS,_ _**y**_ ( _si_ ) = _yi for any i ∈_ [ _t_ ] _, and_
_fS,y_ ( _x_ ) = 0 _for any x ∈_ [ _n_ ] _\ S._


We assume that the description of _S_ includes the input domain [ _n_ ] so that _fS,_ _**y**_ is fully
specified.
A _Multi-Point Function Secret Sharing_ (MPFSS) is an FSS scheme for the class of multipoint functions, where a point function _fS,_ _**y**_ is represented in a natural way. We assume that an
MPFSS scheme leaks not only the input and output domains but also the number of points _t_
that the multi-point function specifies. An MPFSS can be easily obtained by adding _t_ instances
of DPF; optimized constructions of MPFSS, using batch codes [IKOS04] to speed up the full
domain evaluation algorithm, were presented in [BCGI18].


**3.2** **Homomorphic Secret Sharing**


We consider homomorphic secret sharing (HSS), a dual form of FSS introduced in [BGI16a].
HSS can be viewed as the natural secret-sharing analogue of fully homomorphic encryption. In
this work, we consider a _secret-key_ variant of HSS in which a common secret key is used to share
multiple inputs, and the output is shared additively over an Abelian group. Furthermore, we
will be mainly interested in HSS schemes that support the evaluation of _low-degree_ multivariate polynomials on shared input vectors. Informally, a degree- _d_ HSS is a triple of algorithms
(Gen _,_ Share _,_ Eval) such that:


**–** Gen generates a secret key sk and an evaluation key ek,

**–** Share uses the secret key to share an input vector into ( _s_ 0 _, s_ 1), and

**–** Eval, given share _sb_, evaluation key ek, and a description of a function _f_ of algebraic degree
_d_, outputs _yb_ such that _y_ 0 + _y_ 1 = _f_ ( _x_ ).


Security states that a single share _sb_ together with ek computationally hide the input _x_ .


More formally, we consider degree- _d_ HSS over a finite ring _R_ . In this work we will consider
rings _R_ that are either finite fields or rings Z _m_ of integers modulo _m_ . We view the ring as being


14


implicitly defined by the security parameter _λ_, and assume that the bit-length of ring elements
is at most polynomial in _λ_ .


**Definition 5 (Degree-** _d_ **Homomorphic Secret Sharing).** _A (2-party, secret-key)_ Degree- _d_
Homomorphic Secret Sharing (HSS) _scheme over a ring_ ( _R_ = _R_ ( _λ_ ) _,_ + _, ·_ ) _is a triple of PPT_
_algorithms_ HSS = (HSS _._ Gen _,_ HSS _._ Share _,_ HSS _._ Eval) _with the following syntax:_


**–** HSS _._ Gen(1 _[λ]_ ) _: On input a security parameter_ 1 _[λ]_ _, the key generation algorithm outputs a secret_
_key_ sk _and an evaluation key_ ek _._

**–** HSS _._ Share(sk _, x_ ) _: Given secret key_ sk _and secret input value x ∈R_ _[n]_ _, the sharing algorithm_
_outputs a pair of shares_ ( _s_ 0 _, s_ 1) _. We assume that a description of the ring R and the input_
_length n are included in each of_ ( _s_ 0 _, s_ 1) _._

**–** HSS _._ Eval( _b,_ ek _, sb, P_ ) _: On input party index b ∈{_ 0 _,_ 1 _}, evaluation key_ ek _, share sb of an input_
_vector x ∈R_ _[n]_ _, and degree-d arithmetic circuit P over R with n inputs and m outputs, the_
_(deterministic) homomorphic evaluation algorithm outputs yb ∈R_ _[m]_ _, constituting party b’s_
_share over R of an output y ∈R_ _[m]_ _._


_The algorithms_ (HSS _._ Gen _,_ HSS _._ Share _,_ HSS _._ Eval) _should satisfy the following correctness and se-_
_curity requirements:_


**– Correctness:** _For every polynomial_ poly( _λ_ ) _there exists a negligible_ negl( _λ_ ) _such that for_
_every λ, input x ∈R_ _[n]_ _(where R_ = _R_ ( _λ_ ) _), and degree-d arithmetic circuit P of size_ poly( _λ_ )
_we have:_
Pr[ _y_ 0 + _y_ 1 _̸_ = _P_ ( _x_ )] _≤_ negl( _λ_ ) _,_


_where probability is taken over_


(sk _,_ ek) _←_ HSS _._ Gen(1 _[λ]_ ); ( _s_ 0 _, s_ 1) _←_ HSS _._ Share(sk _, x_ );

_yb ←_ HSS _._ Eval( _b,_ ek _, sb, P_ ) _, b ∈{_ 0 _,_ 1 _}._


**– Security:** _For any b ∈{_ 0 _,_ 1 _}, pair of input sequences xλ, x_ _[′]_ _λ_ _[∈R][n][ of polynomial length]_
_n_ ( _λ_ ) _, the distribution ensembles Cb_ ( _λ, xλ_ ) _and Cb_ ( _λ, x_ _[′]_ _λ_ [)] _[ are computationally indistinguish-]_
_able, where Cb_ ( _λ, z_ ) _for z ∈{xλ, x_ _[′]_ _λ_ _[}][ is obtained by sampling]_ [ (][sk] _[,]_ [ ek][)] _[ ←]_ [HSS] _[.]_ [Gen][(1] _[λ]_ [)] _[, sam-]_
_pling_ ( _s_ 0 _, s_ 1) _←_ HSS _._ Enc(sk _, z_ ) _, and outputting_ (ek _, sb_ ) _._


**3.3** **Learning Parity with Noise**


Our constructions rely on variants of the Learning Parity with Noise (LPN) assumption [BFKL93]
over either F2 or a large finite field F. Unlike the LWE assumption, in LPN over F the noise is
assumed to have a small Hamming weight. Concretely, the noise is a random field element in
a small fraction of the coordinates and 0 elsewhere. Similar assumptions have been previously
used in the context of secure arithmetic computation [NP06, IPS09, ADI [+] 17, DGN [+] 17, GNN17].
Unlike most of these works, the flavors of LPN on which we rely do not require the underlying
code to have an algebraic structure and are thus not susceptible to algebraic (list-) decoding
attacks.


**Definition 6 (LPN).** _Let D_ ( _R_ ) = _{Dk,q_ ( _R_ ) _}k,q∈_ N _denote a family of distributions over a ring_
_R, such that for any k, q ∈_ N _,_ Im( _Dk,q_ ( _R_ )) _⊆R_ _[q]_ _. Let_ **C** _be a probabilistic code generation_
_algorithm such that_ **C** ( _k, q, R_ ) _outputs a matrix A ∈R_ _[k][×][q]_ _. For dimension k_ = _k_ ( _λ_ ) _, number_
_of samples (or block length) q_ = _q_ ( _λ_ ) _, and ring R_ = _R_ ( _λ_ ) _, the_ ( _D,_ **C** _, R_ )-LPN( _k, q_ ) _assumption_
_states that_


_{_ ( _A,_ _**b**_ ) _| A_ _←_ $ **C** ( _k, q, R_ ) _,_ _**e**_ _←D_ $ _k,q_ ( _R_ ) _,_ _**s**_ _←_ $ F _k,_ _**b**_ _←_ _**s**_ _· A_ + _**e**_ _}_

_≈{_ c ( _A,_ _**b**_ ) _| A_ _←_ $ **C** ( _k, q, R_ ) _,_ _**b**_ _←R_ $ _q}_


15


Here and in the following, all parameters are functions of the security parameter _λ_ and
computational indistinguishability is defined with respect to _λ_ .
When _R_ = F2 and _D_ is the Bernoulli distribution over F _[q]_ 2 [, where each coordinate is 1 with]
probability _r_ and 0 otherwise, this corresponds to the standard binary LPN assumption.
Note that the search LPN problem, of finding the vector can be reduced to the decisional
LPN assumption as defined above above when the code generator **C** outputs a uniform matrix
_A_ [BFKL93, AIK09]. However, this is less relevant for us as we are mainly interested in efficient variants with more structured codes. See [DI14] for further discussion of search-to-decision
reductions in the general case.


**3.3.1** **Example: LPN with Fixed Weight Noise**


For a finite field F, we denote by _HW_ _r_ (F) the distribution of uniform, weight _r_ vectors over
F; that is, a sample from _HW_ _r_ (F) is a uniformly random nonzero field element in _r_ random
positions, and zero elsewhere. The (Ber _r_ (F) _[q]_ _,_ **C** _,_ F) _−_ LPN( _k, q_ ) assumption corresponds to the
standard (non-binary, fixed-weight) LPN assumption over a field F with code generator **C**,
dimension _k_, number of samples (or block length) _q_, and noise rate _r_ .
When the block length _q_ and noise rate _r_ are such that _k_ random coordinates will be all
noiseless with non-negligible probability (e.g., when _r_ is constant and _q_ = _Ω_ ( _k_ [2] )), LPN can be
broken via Gaussian elimination (cf. [AG11]). This attack does not apply to our constructions,
which typically have _q_ = _O_ ( _k_ ).


**Definition 7 (dual LPN).** _Let D_ ( _R_ ) _and_ **C** _be as in Definition 6, n, n_ _[′]_ _∈_ N _with n_ _[′]_ _> n, and_
_define_ **C** _[⊥]_ ( _n_ _[′]_ _, n, R_ ) = _{B ∈R_ _[n][′][×][n]_ : _A · B_ = 0 _, A ∈_ **C** ( _n_ _[′]_ _−_ _n, n_ _[′]_ _, R_ ) _,_ rank( _B_ ) = _n}._
_For n_ = _n_ ( _λ_ ) _, n_ _[′]_ = _n_ _[′]_ ( _λ_ ) _and R_ = _R_ ( _λ_ ) _, the_ ( _D,_ **C** _, R_ )-dual-LPN( _n_ _[′]_ _, n_ ) _assumption states_
_that_


_{_ ( _H,_ _**b**_ ) _| H_ _←_ $ **C** _⊥_ ( _n′, n, R_ ) _,_ _**e**_ _←D_ $ ( _R_ ) _,_ _**b**_ _←_ _**e**_ _· H}_

_≈{_ c ( _H,_ _**b**_ ) _| H_ _←_ $ **C** _⊥_ ( _n′, n, R_ ) _,_ _**b**_ _←R_ $ _n}_


The search version of the dual LPN problem is also known as syndrome decoding. The
decision version defined above is equivalent to primal variant of LPN from Definition 6 with
dimension _k_ = _n_ _[′]_ _−_ _n_ and number of samples _q_ = _n_ _[′]_ . This follows from the simple fact that
( _**s**_ _· A_ + _**e**_ ) _· H_ = _**s**_ _· A · H_ + _**e**_ _· H_ = _**e**_ _· H_, when _H_ is the parity-check matrix of _A_ .


_Remark 8._ For any code generation algorithm **C** where dual-LPN is hard, it must hold that for
_H_ _←_ $ **C** _⊥_ ( _n′, n′, R_ ), _H_ is full rank with overwhelming probability. If that was not the case,
then we could easily distinguish _**e**_ _· H_ from uniform due to a linear relation between some of its
outputs.


_Remark 9._ As a concrete example of the actual flavor of the dual-LPN assumption we will use,
our construction of silent OT from Section 5 relies on the dual-LPN assumption of Definition 6
with respect to a random linear code over the field F2. For deriving our concrete parameters,
we choose a _regular_ error distribution of weight _t_, where a length- _n_ _[′]_ error vector has _t_ non-zero
coordinates spread across weight-1 blocks of length _n_ _[′]_ _/t_ . This is known as the regular-LPN or
_regular syndrome decoding_ problem. When _n ≥_ 2 [16] and _n_ _[′]_ = 4 _n_, a fixed-weight noise of _t ≈_ 32
suffices to achieve 80-bit security against the best known attacks on this flavor of LPN, which
all take time exponential in ( _n_ _[′]_ _/n_ ) _· t_ . We will also consider alternative choices of linear codes
(such as LDPC codes or quasi-cyclic codes) to improve the concrete computational efficiency in
our estimates; such codes still lead to plausible variants of LPN and do not significantly improve
known attacks compared with random codes.


16


**4** **Pseudorandom Correlation Generators**


In this section we put forward a general notion of pseudorandom correlation generator (PCG)
and study some of its limitations, capabilities, and relation with other primitives. We start with
our formal definition of PCG in Section 4.1. We then prove in Section 4.2 that a simpler and
more natural simulation-based definition of PCG, that would suffice for _all_ applications, is not
realizable. As a second-best alternative, we show in Section 4.3 that PCGs can be used as a dropin replacement for correlated randomness in every protocol that meets a slightly stronger security
requirement, which is indeed met by natural MPC protocols in the correlated randomness model.
Finally in Section 4.4 we show a two-way relation between PCGs for a useful class of “low-degree
correlations” and HSS for low-degree polynomials as defined in Section 3.2.


**4.1** **Defining Pseudorandom Correlation Generators**


At a high level, a pseudorandom correlation generator (PCG) for some relation takes as input
a pair of short, correlated seeds and outputs long correlated pseudorandom strings, where the
expansion procedure is deterministic and can be applied locally.
For correctness we require that the expanded output of a PCG is indistinguishable from truly
random correlated strings.
For security it would be natural and straightforward to require that we can securely replace
long correlated strings by short correlated seeds in any secure protocol execution. Unfortunately,
as shown in the following section, this security requirement would be impossible to meet. Therefore, we will introduce (and subsequently prove useful) an indistinguishability based security
notion. Namely, we require that an adversary given access to one of the short seeds k _σ_, cannot
distinguish the pseudorandom string _R_ 1 _−σ_ from a pseudorandom string that is chosen at random
conditioned on ( _R_ 0 _, R_ 1) being correlated (where _Rσ_ = PCG(k _σ_ )). In other words, an adversary
given access to a short seed cannot learn more about the other party’s pseudorandom string
than what is obvious given access to its own pseudorandom string.
In order to formally define pseudorandom correlations, we first introduce the concept of a
_correlation generator_ as a PPT algorithm outputting correlated elements.


**Definition 10 (Correlation Generator).** _A PPT algorithm C is called a_ correlation generator _, if C on input_ 1 _[λ]_ _outputs a pair of elements in {_ 0 _,_ 1 _}_ _[n]_ _× {_ 0 _,_ 1 _}_ _[n]_ _for n ∈_ poly( _λ_ ) _._


In order to define security, we require the notion of a reverse-sampleable correlation generator
introduced in the following.


**Definition 11 (Reverse-sampleable Correlation Generator).** _Let C be a correlation gen-_
_erator. We say C is_ reverse sampleable _if there exists a PPT algorithm_ RSample _such that for_
_σ ∈{_ 0 _,_ 1 _} the correlation obtained via:_


_{_ ( _R_ 0 _[′]_ _[, R]_ 1 _[′]_ [)] _[ |]_ [(] _[R]_ [0] _[, R]_ [1][)] _←C_ $ (1 _λ_ ) _, Rσ′_ [:=] _[ R][σ][, R]_ 1 _[′]_ _−σ_ _←_ $ RSample( _σ, Rσ_ ) _}_


_is computationally indistinguishable from C_ (1 _[λ]_ ) _._


The following definition of pseudorandom correlation generators can be viewed as a generalization of the definition of the pseudorandom VOLE generator in [BCGI18]. Note though that
we do not enforce perfect correctness.


**Definition 12 (Pseudorandom Correlation Generator (PCG)).** _Let C be a reverse-sampleable_
_correlation generator. A_ pseudorandom correlation generator (PCG) for _C is a pair of algorithms_
(PCG _._ Gen _,_ PCG _._ Expand) _with the following syntax:_


**–** PCG _._ Gen(1 _[λ]_ ) _is a PPT algorithm that given a security parameter λ, outputs a pair of seeds_
(k0 _,_ k1) _;_


17


**–** PCG _._ Expand( _σ,_ k _σ_ ) _is a polynomial-time algorithm that given party index σ ∈{_ 0 _,_ 1 _} and a_
_seed_ k _σ, outputs a bit string Rσ ∈{_ 0 _,_ 1 _}_ _[n]_ _._


_The algorithms_ (PCG _._ Gen _,_ PCG _._ Expand) _should satisfy the following:_


**– Correctness.** _The correlation obtained via:_


_{_ ( _R_ 0 _, R_ 1) _|_ (k0 _,_ k1) _←_ $ PCG _._ Gen(1 _λ_ ) _, Rσ ←_ PCG _._ Expand( _σ,_ k _σ_ ) _for σ ∈{_ 0 _,_ 1 _}}_


_is computationally indistinguishable from C_ (1 _[λ]_ ) _._

**– Security.** _For any σ ∈{_ 0 _,_ 1 _}, the following two distributions are computationally indistin-_
_guishable:_


_{_ (k1 _−σ, Rσ_ ) _|_ (k0 _,_ k1) _←_ $ PCG _._ Gen(1 _λ_ ) _,Rσ ←_ PCG _._ Expand( _σ,_ k _σ_ ) _} and_

_{_ (k1 _−σ, Rσ_ ) _|_ (k0 _,_ k1) _←_ $ PCG _._ Gen(1 _λ_ ) _,R_ 1 _−σ ←_ PCG _._ Expand( _σ,_ k1 _−σ_ ) _,_

_Rσ_ _←_ $ RSample( _σ, R_ 1 _−σ_ ) _}_


_where_ RSample _is the reverse sampling algorithm for correlation C._


Note that the above definition is trivial to achieve in general: We can let PCG _._ Gen on input
1 _[λ]_ return ( _R_ 0 _, R_ 1) _←C_ (1 _[λ]_ ), and simply define Expand to be the identity. Typically, we will be
interested in non-trivial constructions of PCGs, in which the seed size is significantly shorter
than the output size. A pseudorandom generator with image in _{_ 0 _,_ 1 _}_ _[n]_ is a simple example for
an expanding PCG for the equality correlation _{_ ( _R, R_ ) _| R ∈{_ 0 _,_ 1 _}_ _[n]_ _}_ . In the following we will
be interested in constructing PCGs for a much broader class of correlations, like OT correlations,
OLE correlations and (authenticated) Beaver triples.


_Remark 13 (PCG with Setup)._ We sometimes consider an additional algorithm PCG _._ Setup to
sample a secret key, public parameters and a share of evaluation keys (or a subset of the
mentioned), which can be reused throughout several instances. More precisely: On input 1 _[λ]_,
PCG _._ Setup returns a tuple (pp _,_ sk _, {_ ek _σ}σ∈{_ 0 _,_ 1 _}_ ), PCG _._ Gen receives the secret key sk as additional input (always assumed to include the public parameters pp), and PCG _._ Expand receives
the public parameters pp and the respective evaluation key share ek _σ_ as additional inputs.


_Remark 14 (PCG in the Multi-Party Setting)._ We also consider multi-party PCGs for reverse
sampleable multi-correlation generators _C_ _[M]_ which on input 1 _[λ]_ outputs elements in ( _{_ 0 _,_ 1 _}_ _[n]_ ) _[M]_ .
In this case, PCG _._ Gen(1 _[λ]_ ) returns a _M_ -tuple (k1 _, . . .,_ k _M_ ). Correctness is defined accordingly and
security required against any subset of colluding parties. More precisely: For any _T ⊂{_ 1 _, . . ., M_ _}_,
we require the following two distributions to be computationally indistinguishable:


_{_ ( _{_ k _j}j∈T, {Ri}i/∈T_ ) _|_ (k1 _, . . .,_ k _M_ ) _←_ $ PCG _._ Gen(1 _λ_ ) _,_

_∀i /∈_ _T_ : _Ri ←_ PCG _._ Expand( _i,_ k _i_ ) _}_ and

_{_ ( _{_ k _j}j∈T, {Ri}i/∈T_ ) _|_ (k1 _, . . .,_ k _M_ ) _←_ $ PCG _._ Gen(1 _λ_ ) _,_

_∀j ∈_ _T_ : _Rj ←_ PCG _._ Expand( _j,_ k _j_ ) _,_

_{Ri}i/∈T_ _←_ $ RSample( _T, {Rj}j∈T_ ) _}_


where RSample is the reverse sampling algorithm corresponding to the multi-correlation _C_ _[M]_ .


18


**4.2** **Impossibility of a Simulation-Based Definition**


A natural and useful alternative to the security definition we gave in Section 4, is the following:
In any secure protocol (say against semi-honest adversaries), one can replace sampling a pair of
strings from the correlation _C_ by generating a pair of seeds (which are later expanded) using a
PCG for _C_ without compromising security. Unfortunately, as sketched in [GI99], a non-trivial
PCG construction cannot satisfy such a simulation-based definition. Consider the simple protocol, where _P_ 0 samples a pair ( _R_ 0 _, R_ 1) _←C_ (1 _[λ]_ ) and sends _R_ 1 to _P_ 1, who simply outputs _R_ 1. This
protocol obviously realizes the protocol dictated by _C_, with one-sided security against _P_ 1. But,
if _P_ 0 instead generates (k0 _,_ k1) according to the seed generation algorithm of the PCG and sends
k1 to _P_ 1, a possible simulator runs into the following problem. Simulating the above protocol
given only the output _R_ 1 corresponds to finding a short seed k1 that can be (deterministically)
expanded to _R_ 1. If the entropy in the second output of _C_ exceeds the seed-length _|_ k1 _|_, such
a compression violates correctness, as it could be used to distinguish _R_ 1 from a string that is
indeed chosen via _C_ .
In the following, we present a formal and more general version of the above argument for
ruling out a simulation-based definition for non-trivial correlations. Our negative result is based
on a lower bound given by Hubáček and Wichs [HW15]. There, the notion of Yao incompressibility entropy, the computational equivalent to Shannon entropy, is employed to establish a lower
bound on the required communication in a secure protocol with long outputs. More precisely,
Yao incompressibility entropy [HLR07,Yao82] is a measure on how well outputs of a distribution
can be compressed on average, when the compressing and decompressing algorithms are required
to be efficient. For example, a pseudorandom bit string of length _ℓ_ has Yao incompressibility
entropy _ℓ_ .


**Definition 15 (Yao Incompressiblity Entropy [HLR07] (simplified)).** _Let ℓ_ = _ℓ_ ( _λ_ ) _∈_ N _._
_A probability ensemble X_ = _{Xλ} has_ Yao incompressibility entropy at least _ℓ, if for every pair_
_of polynomial sized circuit-ensembles C_ = _{Cλ}, D_ = _{Dλ} where C has output bit-length at_
_most ℓ_ _−_ 1 _, there exists a negligible function_ negl : N _→_ R [+] _such that for every sufficiently large_
_positive integer λ we have_


Pr [ _x ←_ _X_ : _D_ ( _C_ ( _x_ )) = _x_ ] _≤_ [1]

2 [+][ negl][(] _[λ]_ [)] _[.]_


One of the main results of [HW15] is that the communication in a secure protocol has to
at least meet the Yao incompressibility entropy of the output, when the adversary is allowed
to fix the random coins of the corrupted party. Applying this result rules out meaningful PCG
instantiations of a simulation-based security definition.


**Theorem 16 (Impossiblity of Simulation-Based Definition for Non-Trivial PCGs).**
_Let C be a reverse-sampleable correlation generator, where the Yao incompressibility entropy of_
_the output is ℓ. Then, for every pseudorandom correlation generator_ PCG = (PCG _._ Gen _,_ PCG _._ Expand)
_satisfying simulation-based security, the output of the seed generation_ PCG _._ Gen _algorithm must_
_at least have bit-length ℓ._


_Proof._ Let PCG = (PCG _._ Gen _,_ PCG _._ Expand) be a pseudorandom correlation generator for _C_ that
satisfies simulation-based security. Then, in particular, the following protocol _Π_ PCG has to satisfy
one-sided security against _P_ 1: Party _P_ 0 runs ( _k_ 0 _, k_ 1) _←_ $ PCG _._ Gen(1 _λ_ ) and sends _k_ 1 to _P_ 1. Finally,
_P_ 1 outputs _R_ 1 _←_ PCG _._ Expand(1 _, k_ 1).
Let _ℓ_ 1 be the Yao incompressibility entropy of the output of _C_ [1] (1 _[λ]_ ) := _{R_ 1 _|_ ( _R_ 0 _, R_ 1) _←_
_C_ (1 _[λ]_ ) _}_ . Further, let


_C_ PCG [1] [(1] _[λ]_ [) :=] _[ {][R]_ [1] _[ |]_ [ (][k][0] _[,]_ [ k][1][)] _←_ $ PCG _._ Gen(1 _λ_ ) _, R_ 1 _←_ PCG _._ Expand(1 _,_ k1) _}._


19


By correctness of the PCG, the output of _C_ PCG [1] [(and therefore the output of the protocol] _[ Π]_ [PCG][)]
must meet the Yao incompressibility entropy _ℓ_ 1, as an efficient pair of compressor and decompressor could be used as a distinguisher between _C_ [1] and _C_ PCG [1] [.]
By [HW15, Theorem 5], for any protocol between two parties _P_ 0 and _P_ 1 with one-sided
security against “honest-but-deterministic” [11] _P_ 1, where _P_ 1 has no input, it holds: _If the Yao_
_incompressibility entropy of the output of P_ 1 _is ℓ_ 1 _, then the communication complexity from P_ 0
_to P_ 1 _must be at least ℓ_ 1 _bits._
Therefore, as seed expansion is deterministic, the bit-length _|k_ 1 _|_ of the seed of the second
party must be at least _ℓ_ 1. Reversing the roles of _P_ 0 and _P_ 1 together with additivity of Yao
incompressibility entropy yields the required.


For the special case, where _C_ outputs pairs of identical random strings ( _R, R_ ), Gilboa and
Ishai [GI99] sketched why pseudorandom pads cannot securely substitute perfectly-random pads
returned by _C_ in every secure protocol. We obtain this result as a straightforward corollary of
Theorem 16.


**Corollary 17.** _Let C be the correlation generator that on input_ 1 _[λ]_ _draws a string R_ _←{_ $ 0 _,_ 1 _}ℓ_

_uniformly at random and returns_ ( _R, R_ ) _. Then, there exists no pseudorandom generator with seed_
_length strictly less than ℓ, such that sampling a seed (and later expanding via the pseudorandom_
_generator) can securely replace sampling uniformly at random from {_ 0 _,_ 1 _}_ _[ℓ]_ _in every protocol._


_Extension to deterministic functionalities._ The above negative result gives a general counterexample for randomized functionalities. We add to this by showing that our weaker definition of
PCG cannot replace correlated randomness in general, even in protocols that only realize _de-_
_terministic_ functionalities. We prove this using public-key type assumptions, since we will use a
correlation that produces the public key of a _messy_ cryptosystem, where public keys statistically
hide the message. We show that if instantiated with a PCG for _C_ that produces a _real_ public
key, we completely break privacy of a (rather contrived) protocol.


**Theorem 18.** _Suppose that the DDH, QR or LWE assumption holds, and let F_ corr _[C]_ _[be a sampling]_
_functionality for a correlation C. Then there exists a reverse-sampleable correlation C, a secure_
_PCG for C, and a protocol π for some deterministic functionality F such that: (i) π securely_
_realizes F in the F_ corr _[C]_ _[-hybrid model with malicious, statistical security; and (ii)][ π][ is passively]_
_insecure when F_ corr _[C]_ _[is replaced by][ F]_ corr [PCG] _[.]_ [Gen] _._


_Proof._ Let _F_ be a trivial functionality which takes private inputs ( _x_ 0 _, x_ 1) and outputs zero. Consider a public-key encryption scheme that, in addition to the usual algorithms (Gen _,_ Enc _,_ Dec),
supports a _messy mode_ of key generation, Gen _[∗]_, where public keys output by Gen _[∗]_ are computationally indistinguishable from a real public key, however, ciphertexts produced with a messy
public key are not decryptable, and _statistically hide_ the message. This can be constructed
from a range of assumptions including DDH, QR or LWE with standard methods, see for instance [PVW08].
Define the reverse-sampleable distribution to output ( _pk, pk_ ) _←C_ $ (1 _λ_ ), where ( _pk, sk_ ) _←_ $
Gen _[∗]_ (1 _[λ]_ ). In the protocol _π_, party _Pi_ sends Enc _pk_ ( _xi_ ) to the other party and outputs zero. This
is easily seen to be statistically secure by the messy property of the encryption scheme. We
now construct a secure PCG for _C_ . PCG _._ Gen samples a real key pair ( _pk, sk_ ) _←_ $ Gen(1 _λ_ ) and
outputs (k0 _,_ k1) where k0 = ( _pk, sk_ ) and k1 = _pk_ . PCG _._ Expand for either party simply outputs
_pk_ . This is a (computationally) secure PCG, due to the indistinguishability of the two modes of
key generation. Nevertheless, the protocol _π_ is now completely insecure when using PCG instead
of _F_ corr _[C]_ [, since] _[ P]_ [0] [can decrypt] _[ P]_ [1][’s input with the secret key.]


11 A “honest-but-deterministic” adversary has to behave according to the protocol, but is allowed to fix its random
coins.


20


**4.3** **Applying PCGs in Protocols with Correlated Randomness**


In this section we show that one _can_ use PCGs in a “plug-and-play” fashion in protocols consuming correlated randomness sampled by a given functionality. More precisely, we show that
PCGs can be directly applied to any protocol using a weaker form of correlated randomness,
where corrupted parties can influence their outputs.
A simple example is random OT, where the weaker functionality we can realize allows a
corrupt sender/receiver to choose its outputs, then the other party’s outputs are sampled at
random correspondingly. When using OT in an MPC protocol, the OT is typically implemented
from random OT by masking the actual OT inputs with fresh random OT outputs. Allowing a
corrupt party to choose its own OT outputs does not affect the security of these protocols, since
(intuitively) this can only weaken security for the corrupt party and not for honest parties. More
generally, it turns out that many practical MPC protocols, including those based on preprocessed
multiplication triples for arithmetic circuits [BDOZ11, DPSZ12] and binary circuits [NNOB12,
WRK17a, WRK17b], use this kind of corruptible, correlated randomness, since it is often easier
to design a protocol that realizes this.
More formally, the randomness is modelled by the functionality _F_ corr _[C]_ _∗_ [(Fig.][ 1][), where a]
corrupted party may first _choose_ its own output, and then the honest party’s output is computed
with the reverse sampling algorithm for _C_ . As we show in the following, PCGs can be used to
securely realize _F_ corr _[C]_ _∗_ [, opening up many important applications at no extra cost.]
To realize _F_ corr _[C]_ _∗_ [, we use a simple protocol,] _[ Π]_ corr _[C]_ _∗_ [, that calls] _[ F]_ corr [PCG] _[.]_ [Gen] so that each party
obtains a seed k _σ_, which is then expanded to get the output PCG _._ Expand( _σ,_ k _σ_ ).


**Functionality** _F_ corr _[C]_ _∗_


On input 1 _[λ]_, the functionality does as follows:


**–** If no parties are corrupt, sample ( _R_ 0 _, R_ 1) _←C_ $ (1 _λ_ ).

**–** Otherwise, if _Pσ_ is corrupt, wait to receive _Rσ ∈{_ 0 _,_ 1 _}_ _[n][σ]_ from _A_, then sample _R_ 1 _−σ_ _←_ $
RSample( _σ, Rσ_ ).


The functionality outputs _R_ 0 to _P_ 0 and _R_ 1 to _P_ 1, and then halts.


**Fig. 1.** Corruptible correlated randomness functionality for a reverse-sampleable correlation generator, _C_


**Theorem 19.** _Let_ PCG = (PCG _._ Gen _,_ PCG _._ Expand) _be a secure PCG for a reverse-sampleable_
_correlation generator, C. Then the protocol Π_ corr _∗_ _securely realizes the F_ corr _[C]_ _∗_ _[functionality against]_
_a static, malicious adversary._


_Proof._ Let _A_ be a static adversary against the protocol _π_ . We construct a simulator Sim, which
interacts with _A_ and _F_ corr _[C]_ _∗_ [to produce a view for] _[ A]_ [ that is indistinguishable from a real execution]
of the protocol. When both parties are corrupted, the simulator just runs _A_ internally and
security is straightforward. Similarly, when both parties are honest, simulation is trivial and
indistinguishability follows from the correctness of PCG. Now suppose that only _Pσ_ is corrupted,
for _σ ∈{_ 0 _,_ 1 _}_ . On receiving the input 1 _[λ]_, Sim samples a pair of seeds (k0 _,_ k1) _←_ $ PCG _._ Gen(1 _λ_ ),
then sends k _σ_ to _A_ as its output of _F_ corr [PCG] _[.]_ [Gen], computes _Rσ ←_ PCG _._ Expand( _σ,_ k _σ_ ) and sends this
to _F_ corr _[C]_ _∗_ [. Notice that in the ideal execution, the view of the distinguisher consists of the seed][ k] _[σ]_
and the honest party’s output _R_ 1 _−σ_, which is computed by _F_ corr _[C]_ _∗_ [as] _[ R]_ [1] _[−][σ]_ _←_ $ RSample( _σ, Rσ_ ).
The only difference in the real execution, is that there the honest party’s output is computed
with PCG _._ Expand(1 _−_ _σ,_ k1 _−σ_ ). These two views are computationally indistinguishable, due to
the security property of PCG.


21


**4.4** **Relation Between PCGs and HSS**


In this section we elaborate on the two-way relation between pseudorandom correlation generators and homomorphic secret sharing (HSS) schemes.
First, we show how to generically construct a PCG for additive correlations by combining a
pseudorandom generator with a suitable HSS scheme. If the correlation is a degree- _d_ polynomial
and the PRG has degree _d_ _[′]_, then the HSS scheme must support evaluation of degree _dd_ _[′]_ polynomials. This can be viewed as a step forward towards the concretely efficient PCG constructions
given in Section 7.
Second, in the other direction, we show that a PCG for degree- _d_ additive correlations, for
constant _d_, implies (secret-key) HSS for degree- _d_ multivariate polynomials. By the results of

[BGI16a], this has implications for secure multi-party computation. For details we refer to Section
6.1.


**4.4.1** **Generic Construction of PCG for Additive Correlations from HSS**


Our high-level strategy is as follows: We combine a standard pseudorandom generator (PRG),
expanding a short seed into a long pseudorandom string, with a suitable HSS scheme, which
allows to _locally_ compute the target correlation on shares of a random input. More precisely, we
consider the special case of additive correlations, where _R_ 0, _R_ 1 are uniformly distributed subject
to _R_ 0 + _R_ 1 = _f_ ( _X_ ) for a random input _X_ and fixed function _f_ . Now, consider an HSS scheme
with additive reconstruction for _f_ . Recall that given _shares of the input X_ an HSS allows to
locally evaluate _f_ on the shares, such that the respective outputs add up to _f_ ( _X_ ).
This gives rise to the following PCG construction: During key generation a short seed k is
shared between the players (as HSS shares). For expansion, the players can then locally evaluate
_f_ (PRG(k)) via the HSS operations. By the correctness of the HSS that indeed gives outputs
_R_ 0 _, R_ 1 with _R_ 0 + _R_ 1 = _f_ ( _X_ ), where _X_ = PRG(k). In this section we formally prove that the
described construction meets the PCG requirements.
Note that the challenge lies in actually instantiating the described approach efficiently. This is
due to the fact that known efficient HSS constructions only apply to limited classes of functions,
for instance functions admitting small branching programs. It is therefore crucial to carefully
select the underlying PRG and HSS. We will elaborate on how we address these challenges in
Section 7.
To formalize the above outline, we first give a generalized definition of a pseudorandom generator, then formally define additive correlations corresponding to a function, before presenting
the construction.
Let _R_ be a ring and _ℓ, n ∈_ N. We consider distributions _D_ _[ℓ]_ over a ring _R_ _[ℓ]_ and write
_X_ _←D_ $ _ℓ_ ( _R_ ) or simply _X_ _←D_ $ _ℓ_ (if _R_ is clear from the context) to denote sampling from _Rℓ_ via
_D_ _[ℓ]_ . Note that the following definition of _D_ _[ℓ]_ -pseudorandom generator coincides with the standard
definition of a PRG, if we choose _D_ _[ℓ]_ ( _R_ ) = _U_ _[ℓ]_ ( _R_ ). We use this more general notion of a PRG,
as for our PRG instantiation from LPN the seed is not chosen uniformly at random.


**Definition 20 (** _D_ _[ℓ]_ **-Pseudorandom Generator).** _Let R be a ring (parametrized implicitly by_
_λ) and let D_ _[ℓ]_ _be a distribution on R_ _[ℓ]_ _. We say_ PRG : _R_ _[ℓ]_ _→R_ _[n]_ _is a D_ _[ℓ]_ -pseudorandom generator
(PRG) _, if the following two distributions are computationally indistinguishable:_


      - _Y | X_ _←D_ $ _ℓ_ ( _R_ ) _, Y_ := PRG( _X_ )� _and_       - _Y | Y_ _←U_ $ _n_ ( _R_ )� _._


We will consider _additive correlations_ corresponding to a family of functions _F_ . Such a
correlation is generated by outputting an additive secret-sharing of a function from _f ∈F_
applied to a source of randomness.


22


**–** PCG _._ Setup(1 _[λ]_ ): Sample and output (sk _, {_ ek _σ}σ∈{_ 0 _,_ 1 _}_ ) _←_ HSS _._ Gen(1 _[λ]_ ).

**–** PCG _._ Gen(sk): Sample _r ←D_ _[ℓ]_ and output (k0 _,_ k1) _←_ HSS _._ Share(sk _, r_ ).

**–** PCG _._ Expand( _σ,_ ek _σ,_ k _σ, f_ ): Output _Rσ ←_ HSS _._ Eval( _σ,_ ek _σ,_ k _σ, f ◦_ PRG).


**Fig. 2.** PCG for correlation _CF_ . Here, PRG is a _D_ _[ℓ]_ -PRG and HSS = (HSS _._ Gen _,_ HSS _._ Share _,_ HSS _._ Eval) an HSS for
the family of functions _F_ HSS := _{f ◦_ PRG : _r �→_ _f_ (PRG( _r_ )) _| f ∈F}_ .


**Definition 21 (Correlation Generators for Additive Correlations).** _Let R be a ring. Let_
_n, m ∈_ N _and F ⊆{f_ : _R_ _[n]_ _→R_ _[m]_ _} be a family of functions. Then we define a_ correlation
generator _CF_ for _F as follows: On input_ 1 _[λ]_ _and f ∈F the correlation generator CF samples_
_X_ _←U_ $ _n_ ( _R_ ) _, and returns a pair_ ( _R_ 0 _, R_ 1) _∈Rm × Rm, which is distributed uniformly at random_
_conditioned on R_ 0 + _R_ 1 = _f_ ( _X_ ) _._


Note that _CF_ is reverse-sampleable for any family of functions _F_, as given a function _f ∈F_
and a share _Rσ_, one can draw an input _X_ _←U_ $ _n_ ( _R_ ) and set _R_ 1 _−σ_ := _Rσ −_ _f_ ( _X_ ). Further, note
that it is straightforward to includes shares of the inputs in the correlation by considering the
family _F_ _[′]_ := _{f_ _[′]_ : _R_ _[n]_ _→R_ _[n]_ [+] _[m]_ _, X �→_ ( _X, f_ ( _X_ )) _| f ∈F}_ .


**Definition 22 (HSS satisfying Pseudorandomness of Outputs).** _We say an HSS_ HSS =
(HSS _._ Gen _,_ HSS _._ Share _,_ HSS _._ Eval) _for a function family F_ := _{f_ : _R_ _[n]_ _→R_ _[m]_ _} satisfies_ pseudorandomness of outputs _, if for all f_ : _R_ _[n]_ _→R_ _[m]_ _∈F,_ (sk _, {_ ek _σ}σ∈{_ 0 _,_ 1 _}_ ) _←_ HSS _._ Gen(1 _[λ]_ ) _, X_ _←U_ $ _n_ ( _R_ ) _,_
(k0 _,_ k1) _←_ $ Share(sk _, X_ ) _, and σ ∈{_ 0 _,_ 1 _} the output Rσ_ _←_ $ HSS _._ Eval( _σ,_ ek _σ,_ k _σ, f_ ) _is distributed_
_computationally close to uniformly at random over the output space._


Note that if _f_ ( _U_ _[n]_ ( _R_ )) is close to being uniformly random on _R_ _[m]_, this property follows from the
security of HSS.


**Theorem 23. (PCG for Additive Correlations from HSS).** _Let R be a ring and n, m, ℓ_ _∈_
N _. Let F ⊆{f_ : _R_ _[n]_ _→R_ _[m]_ _} be a family of functions. Let_ PRG _be a D_ _[ℓ]_ _-PRG and_ HSS =
(HSS _._ Gen _,_ HSS _._ Share _,_ HSS _._ Eval) _an HSS with overhead O_ HSS [12] _for the family of functions F_ HSS :=
_{f ◦_ PRG : _R_ _[ℓ]_ _→R_ _[m]_ _, r �→_ _f_ (PRG( _r_ )) _| f ∈F} that further satisfies pseudorandomness of out-_
_puts. Then,_ PCG = (PCG _._ Setup _,_ PCG _._ Gen _,_ PCG _._ Expand) _as defined in Figure 2 is a_ PCG _for the_
_correlation generator CF with key-length upper bounded by ℓ_ _· O_ HSS _._


_Proof. Correctness._ Let _f ∈F_ . We have


_{_ ( _R_ 0 _, R_ 1) _|_ (k0 _,_ k1) _←_ $ PCG _._ Gen(1 _λ_ ) _, Rσ ←_ PCG _._ Expand( _σ,_ k _σ_ ) for _σ ∈{_ 0 _,_ 1 _}}_

_≈{c_ ( _R_ 0 _, R_ 1) _|_ (sk _, {_ ek _σ}σ∈{_ 0 _,_ 1 _}_ ) _←_ HSS _._ Gen(1 _λ_ ) _, r_ _←D_ $ _ℓ_ ( _R_ ) _,_ (k0 _,_ k1) _←_ HSS _._ Share(sk _, r_ ) _,_

_R_ 0 _←_ HSS _._ Eval(0 _,_ ek0 _,_ k0 _, f ◦_ PRG) _, R_ 1 := _f_ (PRG( _r_ )) _−_ _R_ 0 _}_

_≈{c_ ( _R_ 0 _, R_ 1) _|r_ _←D_ $ _ℓ_ ( _R_ ) _, R_ 0 _←Rm, R_ 1 := _f_ (PRG( _r_ )) _−_ _R_ 0 _}_

_≈{c_ ( _R_ 0 _, R_ 1) _|X_ _←U_ $ _n_ ( _R_ ) _, R_ 0 _←Rm, R_ 1 := _f_ ( _X_ ) _−_ _R_ 0 _}_


as required, where the first transition follow by correctness of HSS, the second by pseudorandomness of outputs of HSS and the last by pseudorandomness of PRG.
_Security._ Let _σ ∈{_ 0 _,_ 1 _}_ . We have


_{_ (k1 _−σ, Rσ_ ) _|_ (k0 _,_ k1) _←_ $ PCG _._ Gen(1 _λ_ ) _, Rσ ←_ PCG _._ Expand( _σ,_ k _σ_ ) _}_

_≈{c_ (k1 _−σ, Rσ_ ) _|_ (sk _, {_ ek _σ}σ∈{_ 0 _,_ 1 _}_ ) _←_ HSS _._ Gen(1 _λ_ ) _, r_ _←D_ $ _ℓ_ ( _R_ ) _,_ (k0 _,_ k1) _←_ HSS _._ Share(sk _, r_ ) _,_

_R_ 1 _−σ ←_ HSS _._ Eval(1 _−_ _σ,_ ek1 _−σ,_ k1 _−σ, f ◦_ PRG) _, Rσ_ := _f_ (PRG( _r_ )) _−_ _R_ 1 _−σ}_

_≈{c_ (k1 _−σ, Rσ_ ) _|_ (sk _, {_ ek _σ}σ∈{_ 0 _,_ 1 _}_ ) _←_ HSS _._ Gen(1 _λ_ ) _, r_ _←D_ $ _ℓ_ ( _R_ ) _, r′_ _←D_ $ _ℓ_ ( _R_ ) _,_


12 We say a HSS has _overhead O_ HSS, if for every input the share size does not exceed _O_ HSS times the input size.


23


(k0 _,_ k1) _←_ HSS _._ Share(sk _, r_ _[′]_ ) _, R_ 1 _−σ ←_ HSS _._ Eval(1 _−_ _σ,_ ek1 _−σ,_ k1 _−σ, f ◦_ PRG) _,_

_Rσ_ := _f_ (PRG( _r_ )) _−_ _R_ 1 _−σ}_

_≈{c_ (k1 _−σ, Rσ_ ) _|_ (sk _, {_ ek _σ}σ∈{_ 0 _,_ 1 _}_ ) _←_ HSS _._ Gen(1 _λ_ ) _, X_ _←U_ $ _n_ ( _R_ ) _, r′_ _←D_ $ _ℓ_ ( _R_ ) _,_

(k0 _,_ k1) _←_ HSS _._ Share(sk _, r_ _[′]_ ) _, R_ 1 _−σ ←_ HSS _._ Eval(1 _−_ _σ,_ ek1 _−σ,_ k1 _−σ, f ◦_ PRG) _,_

_Rσ_ := _f_ ( _X_ ) _−_ _R_ 1 _−σ},_


where the first transition follows by correctness of HSS, the second transition by security of HSS
and the last by pseudorandomness of PRG.


**4.4.2** **Generic Construction of HSS from a PCG**


We observe that there is also a connection in the reverse direction. Namely, given a PCG for
general, additive degree- _d_ correlations for a constant _d_, we show how to construct a homomorphic
secret sharing scheme for degree- _d_ multivariate polynomials, a primitive which is interesting in its
own right. Consider two parties who wish to compute shares of _P_ ( _**x**_ ) for some public multivariate
polynomial _P_, given shares of _**x**_ . Let _⊗d_ _**x**_ denote the degree- _d_ tensor product _**x**_ _⊗· · ·⊗_ _**x**_ . Given
a PCG for the additive, degree- _d_ correlation ( _**r**_ _, ⊗_ 2 _**r**_ _, · · ·, ⊗d_ _**r**_ ), we construct a (secret-key)
homomorphic secret sharing scheme HSS = (HSS _._ Gen _,_ HSS _._ Share _,_ HSS _._ Eval) for _P_ as follows.


**–** HSS _._ Share( _**x**_ ): generate PCG keys (k0 _,_ k1) which expand to shares of ( _**r**_ _, ⊗_ 2 _**r**_ _, · · ·, ⊗d_ _**r**_ ), set
_**x**_ _[′]_ _←_ _**x**_ + _**r**_, and give to each party _Pσ_ a share _sσ_ = (k _σ,_ _**x**_ _[′]_ ).

**–** HSS _._ Eval( _σ, sb, P_ ): On input party index _σ ∈{_ 0 _,_ 1 _}_, share _sσ_ of a size- _n_ input, and a degree_d_ multivariate polynomial _P_, compute a share _Pσ_ _[′]_ [of the polynomial] _[ P][ ′]_ [ satisfying] _[ P][ ′]_ [(] _[X]_ [) =]
_P_ ( _X −_ _**r**_ ). Note that the coefficients of _P_ _[′]_ are public degree _≤_ _d_ polynomials in _**r**_, hence
shares of the coefficients can be locally computed given shares of the monomials _**r**_ _, · · ·, ⊗d_ _**r**_ .
Output _Pσ_ _[′]_ [(] _**[x]**_ _[′]_ [)][.]


Correctness follows immediately by inspection, and security reduces to the security of the
underlying PCG.


**5** **Silent Oblivious Transfer Extension From LPN**


In this section we present a protocol for silent OT extension, which allows to generate _n_ instances
of random OT with sublinear communication complexity. To this end, we first show how to tweak
the construction of Boyle et al. [BCGI18] to give correlated OT. Combining this observation with
the OT extension technique of Ishai et al. [IKNP03] we obtain a PCG for random OT. Finally,
we show how to use the protocol of Doerner and shelat [Ds17] for secure computation of the
seed, giving sublinear OT extension.


**5.1** **Subfield Vector-OLE**


Here, we introduce the notion of subfield vector oblivious linear evaluation (sVOLE), and show
that sVOLE for F _q_ over subfield F _p ⊂_ F _q_ gives 1-out-of- _p_ correlated OT. More precisely, a
single big instance of sVOLE will give many 1-out-of- _p_ OTs at once. Our construction of sVOLE
comes with two additional advantages: It enjoys lower computational costs, because matrix
multiplications are performed with a matrix over F _p_, and for _p_ = 2 we can reduce security to
the better-studied binary LPN problem, instead of its arithmetic variant over larger fields.
Subfield VOLE is a form of vector oblivious linear evaluation (VOLE) over F _q_, which computes _**w**_ = _**u**_ _x_ + _**v**_, where the vector _**u**_ is restricted to lie over a subfield F _p ⊂_ F _q_, for _q_ = _p_ _[r]_

(and we multiply _**u**_ with _x ∈_ F _q_ component-wise, by viewing _x_ as a vector over F _p_ ). It outputs
( _**u**_ _,_ _**v**_ ) to the sender and ( _x,_ _**w**_ ) to the receiver.


24


The construction in Fig. 3 uses the function spread _n_ ( _S,_ _**y**_ ), which expands a set _S_ = ( _s_ 1 _, . . ., s|S|_ ) _⊂_

[ _n_ ] and a vector _**y**_ _∈_ F _[|]_ _p_ _[S][|]_ into the vector _**µ**_ _∈_ F _[n]_ _p_ [, where] _[ µ][s]_ _i_ [=] _[ y][i]_ [for] _[ i]_ [ = 1] _[, . . .,][ |][S][|]_ [, and] _[ µ][j]_ [= 0]
for _j ∈_ [ _n_ ] _\ S_ . It is a generalization of the VOLE generator from [BCGI18], which follows from
the case _p_ = _q_ .


**Construction** _G_ sVOLE


Parameters:


**–** Security parameter 1 _[λ]_, integers _n_ _[′]_ _> n_, _q_ = _p_ _[r]_, and noise weight _t_ .

**–** A code generation algorithm **C** and _Hn′,n_ _←_ $ **C** ( _n′, n,_ F _p_ ).

**–** A multi-point FSS scheme (MPFSS _._ Gen _,_ MPFSS _._ FullEval).


Correlation: Output ( _**u**_ _,_ _**v**_ ) and ( _x,_ _**w**_ ), where _x ←_ F _q_, _**u**_ _←_ $ F _np_ [,] _**[ v]**_ _←_ $ F _nq_ [and] _**[ w]**_ [ =] _**[ u]**_ _[x]_ [ +] _**[ v]**_ [.]


Gen: On input 1 _[λ]_ :


1. Pick a random size- _t_ subset _S_ of [ _n_ _[′]_ ], sorted in increasing order.

$
2. Pick a random vector _**y**_ _∈_ (F _[∗]_ _p_ [)] _[t]_ [ and] _[ x]_ _←_ F _q_ .
3. Compute ( _K_ 0 [fss] _[, K]_ 1 [fss][)] _←_ $ MPFSS _._ Gen(1 _λ, fS,x·_ _**y**_ ).
4. Let k0 _←_ ( _m, n, K_ 0 [fss] _[, S,]_ _**[ y]**_ [)][ and][ k] 1 _[←]_ [(] _[m, n, K]_ 1 [fss] _[, x]_ [)][.]
5. Output (k0 _,_ k1).


Expand: On input ( _σ,_ k _σ_ ):


1. If _σ_ = 0: parse k0 as ( _m, n, K_ 0 [fss] _[, S,]_ _**[ y]**_ [)][. Set] _**[ µ]**_ _[ ←]_ [spread] _n_ _[′]_ [(] _[S,]_ _**[ y]**_ [)][ in][ F] _p_ _[n][′]_ [. Compute] _**[ v]**_ 0 _←_
MPFSS _._ FullEval(0 _, K_ 0 [fss][)][ in][ F] _q_ _[n][′]_ [. Output][ (] _**[u]**_ _[,]_ _**[ v]**_ [)] _[ ←]_ [(] _**[µ]**_ _[ ·][ H]_ _n_ _[′]_ _,n_ _[,][ −]_ _**[v]**_ 0 _[·][ H]_ _n_ _[′]_ _,n_ [)][.]
2. If _σ_ = 1: parse k1 as ( _m, n, K_ 1 [fss] _[, x]_ [)][. Compute] _**[ v]**_ 1 _[←]_ [MPFSS] _[.]_ [FullEval][(1] _[, K]_ 1 [fss][)][ in][ F] _q_ _[n][′]_ [, and output]
( _x,_ _**w**_ _←_ _**v**_ 1 _· Hn′,n_ ).


**Fig. 3.** PCG for subfield vector-OLE


**Theorem 24.** _Suppose the_ ( _HW_ _t,_ **C** _,_ F _p_ )-dual-LPN( _n_ _[′]_ _, n_ ) _assumption holds, and that_ MPFSS _is_
_a secure multi-point FSS scheme. Then the construction G_ sVOLE _(Fig. 3) is a secure PCG for_
_the subfield vector-OLE correlation._


_Proof._ First let _σ_ = 0. Here, in the real distribution, the adversary is given a key k0 =
( _m, n, K_ 0 [fss] _[, S,]_ _**[ y]**_ [)][, where][ (][k][0] _[,]_ [ k][1][)] _←_ $ _G_ sVOLE _._ Gen(1 _λ_ ), as well as the expanded output _R_ 1 =
( _x,_ _**w**_ ) _←_ $ _G_ sVOLE _._ Expand(k1). We need to show that this is indistinguishable from the ideal
distribution, where _R_ 1 _←_ $ RSample(0 _, R_ 0).

$
Recall that RSample(0 _, R_ 0) proceeds by sampling _x_ _←_ F _q_ and outputing ( _x,_ _**w**_ = _**u**_ _x_ + _**v**_ ). In
the real distribution, _x_ is also uniformly random, and from the correctness of MPFSS we have
that


_**w**_ = _**v**_ 1 _· Hn′,n_ = ( _**v**_ 0 + _x ·_ spread _n′_ ( _S,_ _**y**_ )) _· Hn′,n_ = _**v**_ + _x ·_ _**u**_


which is identically distributed to the ideal distribution.

Next consider the case of _σ_ = 1. We use the following sequence of games.
**Game** _G_ 0 **.** This is the real distribution, where the adversary gets k1 = ( _m, n, K_ 1 [fss] _[, x]_ [)][ and]
$ $
_R_ 0 = ( _**u**_ _,_ _**v**_ ) _←_ _G_ sVOLE _._ Expand(0 _,_ k0), that is, _**u**_ = _**µ**_ _· Hn′,n_ for _**µ**_ _←HW_ _t,n′_ (F _p_ ) and _**v**_ =
_**v**_ 0 _· Hn′,n_ = ( _**v**_ 1 + _x ·_ _**µ**_ ) _· Hn′,n_ .
**Game** _G_ 1 **.** Here, we compute _K_ 1 [fss] using the MPFSS simulator Sim(1 _[λ]_ _, · · ·_ ), and _**v**_ = ( _**v**_ 1 +
_x ·_ _**µ**_ ) _· Hn′,n_ . This is indistinguishable from _G_ 0, by the security of the MPFSS.


25


**Game** _G_ 2 **.** Finally, here we compute _**u**_ _←_ $ F _np_ [instead of] _**[ µ]**_ _[·][H][n][′][,n]_ [, and let] _**[ v]**_ [ =] _**[ v]**_ [1] _[·][H][n][′][,n]_ [+] _[x][·]_ _**[u]**_ [.]
Notice that since _K_ 1 [fss] is independent of _**µ**_, any adversary distinguishing _G_ 1 and _G_ 2 can be used
to attack ( _HW_ _t,_ **C** _,_ F _p_ )-dual-LPN( _n_ _[′]_ _, n_ ).
Game _G_ 2 is identical to the ideal distribution, so this completes the proof of the security
property.
Finally, we show the correctness property, namely, that the outputs ( _R_ 0 _, R_ 1) = ( _**u**_ _,_ _**v**_ _, x,_ _**w**_ )
are computationally indistinguishable from outputs of _D_ (1 _[λ]_ ). By the same reasoning as security
for _σ_ = 0, _R_ 1 is already identically distributed to the output of RSample(0 _, R_ 0), so we write
_**w**_ = _**u**_ _x_ + _**v**_ . Denoting the uniform distribution on F _[n]_ _p_ [by] _[ U]_ _p_ _[n]_ [, we then use the following sequence]
of hops:


( _**u**_ _,_ _**v**_ _, x,_ _**w**_ ) = ( _**µ**_ _· Hn′,n,_ ( _**v**_ 1 + _x ·_ _**µ**_ ) _· Hn′,n, x,_ _**u**_ _x_ + _**v**_ )

c _n′_
_≈_ ( _**µ**_ _· Hn′,n,_ ( _Uq_ [+] _[ x][ ·]_ _**[ µ]**_ [)] _[ ·][ H][n][′][,n][, x,]_ _**[ u]**_ _[x]_ [ +] _**[ v]**_ [)] (3)

s _n_
_≈_ ( _**µ**_ _· Hn′,n, Uq_ _[, x,]_ _**[ u]**_ _[x]_ [ +] _**[ v]**_ [)] (4)

_≈_ c ( _Upn_ _[, U]_ _q_ _[n][, x,]_ _**[ u]**_ _[x]_ [ +] _**[ v]**_ [)] (5)

_≡D_ (1 _[λ]_ )


where (3) follows from the pseudorandomness of the MPFSS outputs (cf. Remark 2). Hop (4)
holds because the LPN assumption implies from Remark 8 that _Hn′,n_ must be full-rank with
overwhelming probability, so preserves uniformity when multiplying by a uniform vector. Finally,
(5) also holds due to the pseudorandomness of the LPN assumption.


**5.1.1** **Application to Correlated OT**


Subfield VOLE immediately gives a PCG for _correlated OT_ (or _∆_ -OT). This is a batch of 1-outof-2 OTs where the sender’s strings are of the form ( _wi, wi_ _⊕∆_ ) for some fixed string _∆_, and is the
main building block in practical MPC protocols such as TinyOT [NNOB12] and authenticated
garbling [WRK17a, WRK17b].
To obtain correlated OT, we run subfield VOLE with _p_ = 2 and _q_ = 2 _[r]_, so the VOLE
sender obtains _ui ∈_ F2 _, vi ∈_ F2 _[r]_, while the VOLE receiver gets _x ∈_ F2 _[r]_ and _wi_ = _x · ui_ + _vi_, for
_i_ = 1 _, . . ., n_ . Now switching the roles of sender and receiver, the VOLE sender can be seen as an
OT receiver with choice bit _ui_ and string _vi_ . This gives us a correlated OT, since the OT sender
(formerly VOLE receiver) can compute the strings ( _wi, wi_ + _x_ ), and we have _vi_ = _wi_ if _ui_ = 0
and _vi_ = _wi_ + _x_ if _ui_ = 1.


**5.1.2** **Application to Matrix Multiplication**


Our construction for subfield VOLE can alternatively be seen as a PCG for _tensor product_ :
writing _x ∈_ F _q_ as _**x**_ = ( _x_ 1 _, . . ., xr_ ) _∈_ F _[r]_ _p_ [, and] _**[ u]**_ [ = (] _[u]_ [1] _[, . . ., u][n]_ [)] _[ ∈]_ [F] _[n]_ _p_ [, sVOLE computes secret]
shares of _**x**_ _⊗_ _**u**_, that is, _xi · uj_ for every ( _i, j_ ) _∈_ [ _r_ ] _×_ [ _n_ ]. This allows evaluation of secret-shared
tensor products in 2-PC, which can in turn be used for matrix multiplication.
The seed size scales linearly in _r_, but this still improves upon the naive way of using _r_
PCGs for VOLE over F _p_ ; the latter approach (with the VOLE from [BCGI18]) has seed size
_O_ ( _rt ·_ ( _λ_ log _n_ + log _p_ )) bits, whereas we reduce this to _O_ ( _t ·_ ( _λ_ log _n_ + _r_ log _p_ )) bits, saving at
least a log _n_ factor when log _p_ = _O_ ( _λ_ ).


**5.2** **PCG for Random Oblivious Transfer**


In Fig. 4, we use the _G_ sVOLE PCG to construct a PCG for the random oblivious transfer correlation. Given the above observation that subfield VOLE implies correlated OT, this is straightforward, as we can apply the OT extension technique of Ishai et al. [IKNP03], which converts


26


**Construction** _G_ OT


Parameters:


**–** Security parameter 1 _[λ]_, integers _n_, _q_ = _p_ _[r]_ = _λ_ _[ω]_ [(1)] .

**–** An F _p_ -correlation-robust function H : _{_ 0 _,_ 1 _}_ _[λ]_ _×_ F _q →{_ 0 _,_ 1 _}_ _[λ]_ .

**–** The subfield-VOLE PCG ( _G_ sVOLE _._ Gen _, G_ sVOLE _._ Expand)


Correlation: Outputs ( _R_ 0 _, R_ 1) =   - _{_ ( _ui, wi,ui_ ) _}i∈_ [ _n_ ] _, {wi,j}i∈_ [ _n_ ] _,j∈_ [ _p_ ]�, where _wi,j_ _←{_ $ 0 _,_ 1 _}λ_ and

_ui_ _←{_ $ 1 _, . . ., p}_, for _i ∈_ [ _n_ ] _, j ∈_ [ _p_ ].


Gen: On input 1 _[λ]_, output (k0 _,_ k1) _←_ _G_ sVOLE _._ Gen(1 _[λ]_ _, n, p, q_ ).


Expand: On input ( _σ,_ k _σ_ ):

1. If _σ_ = 0: compute ( _**u**_ _,_ _**v**_ _[′]_ ) _←_ _G_ sVOLE _._ Expand( _σ,_ k _σ_ ), where _**u**_ _∈_ F _[n]_ _p_ _[,]_ _**[ v]**_ _[′][ ∈]_ [F] _q_ _[n]_ [. Compute]


_vi ←_ H( _i, vi_ _[′]_ [)] for _i_ = 1 _, . . ., n_


and output ( _ui, vi_ ).
2. If _σ_ = 1: compute ( _x,_ _**w**_ _[′]_ ) _←_ _G_ sVOLE _._ Expand( _σ,_ k _σ_ ), where _x ∈_ F _q,_ _**w**_ _[′]_ _∈_ F _[n]_ _q_ [. Compute]


_wi,j ←_ H( _i, wi_ _[′]_ _[−]_ _[j][ ·][ x]_ [)] for _i_ = 1 _, . . ., n, ∀j ∈_ F _p_


and output _{wi,j}i,j_ .


**Fig. 4.** PCG for _n_ sets of 1-out-of- _p_ random OT


correlated OTs into random OTs using a suitable hash function. We extend this in a natural way
to generate 1-out-of- _p_ random OTs using subfield VOLE over F _p_ . Note that for security when
applying the hash function, we now need _q_ = _λ_ _[ω]_ [(1)] .
We use the following generalization of a correlation robust function over F _p_ . As recently shown
in [GKWY19], this can be instantiated with fixed-key AES modeled as a random permutation
when _p_ = 2.


**Definition 25 (** F _p_ **-correlation robust function).** _Let n_ = poly( _λ_ ) _and t_ 1 _, . . ., tn, x be uni-_
_formly sampled from_ F _[r]_ _p_ _[, where][ p][r]_ [ =] _[ λ][ω]_ [(1)] _[. Then,]_ [ H][ :] _[ {]_ [0] _[,]_ [ 1] _[}][λ][ ×]_ [ F] _[r]_ _p_ _[→{]_ [0] _[,]_ [ 1] _[}][λ][ is]_ [ F] _[p][-]_ [correlation]
robust _if the distribution_


          - _t_ 1 _, . . ., tn, {_ H(1 _, t_ 1 _−_ _j · x_ ) _, . . .,_ H( _n, tn −_ _j · x_ ) _}j∈_ F _p\{_ 0 _}_          

_is computationally indistinguishable from uniform on_ F _[rn]_ _p_ _[× {]_ [0] _[,]_ [ 1] _[}][λ]_ [(] _[p][−]_ [1)] _[n][.]_


**Theorem 26.** _Suppose that_ H _is an_ F _p-correlation robust hash function and G_ sVOLE _is a secure_
_PCG. Then the silent OT construction (Fig. 4) is a secure PCG for the random 1-out-of-p OT_
_correlation._


_Proof._ We start by showing the correctness property. First, from the correctness of _G_ sVOLE we
have
_vi_ = H( _i, vi_ _[′]_ [) =][ H][(] _[i, w]_ _i_ _[′]_ _[−]_ _[u][i]_ _[·][ x]_ [) =] _[ w][i,u]_ _i_

as required. Indistinguishability of the outputs from OT _[n]_ _p_ [follows first from indistinguishability]
of the VOLE outputs ( _ui, vi_ _[′][, x, w]_ _i_ _[′]_ [)][, and secondly by a standard reduction to the][ F] _[p]_ [-correlation]
robustness property of H.


c
_ui, vi, wi,j_ = _ui,_ H( _i, wi_ _[′]_ _[−]_ _[u][i]_ _[·][ x]_ [)] _≈_ ( _U,_ H( _i,_ ))


We now consider the security property, for the case _σ_ = 0. Here, the real distribution consists
of the seed k0 and the sender’s outputs _wi,j_, for _i_ = 1 _, . . ., n_ and _j ∈_ F _p_ . From correctness we have


27


that for _**u**_ _,_ _**v**_ _[′]_ _←_ _G_ sVOLE _._ Expand(0 _,_ k0), it holds that H( _i, vi_ _[′]_ [) =] _[ w][i,u]_ _i_ [. From the security property]
of _G_ sVOLE, we can replace all the sender’s outputs _wi,j_, except for _wi,ui_, with ones computed
using uniform values _x, wi_ _[′]_ [, instead of from] _[ G]_ [sVOLE] _[.]_ [Expand][. These are then indistinguishable]
from uniform under the F _p_ -correlation robustness of H.
When _σ_ = 1, the real distribution contains the seed k1 and the receiver’s outputs _ui, vi_ . As
before, from the correctness property we have that _vi_ = _wi,ui_, where _wi,j_ is computed from k1 via
_G_ sVOLE _._ Expand and the hash function. We only need to show that _ui_ is uniform, which follows
directly from the security property of _G_ sVOLE when _σ_ = 1.


**5.3** **From a PCG to Silent OT Extension**


To construct an OT extension protocol, we can use 2-PC to securely compute the Gen algorithm
of _G_ OT, and then have each party locally expand its output using _G_ OT _._ Expand. Applying Theorem 19 from Section 4.3, this realizes a _corruptible_ form of the ideal functionality for random
oblivious transfer, where corrupt parties may influence their random outputs.
To do this efficiently with semi-honest security, we use the black-box protocol of Doerner
and shelat [Ds17] (also used in [BCGI18]) for setting up distributed point function keys. For a
single point function of domain size _n_, this requires _O_ (log _n_ ) OTs on _O_ ( _λ_ )-bit strings, giving
_O_ ( _t_ log _n_ ) OTs for a multi-bit point function. Implementing each OT with (non-silent) OT extension [IKNP03] costs _O_ ( _λ_ ) bits of communication, plus a setup phase of _λ_ base OTs. Putting
this together, we obtain the following.


**Theorem 27.** _Suppose the_ ( _HW_ _t,_ **C** _,_ F _p_ )-dual-LPN( _n_ _[′]_ _, n_ ) _assumption holds, and an_ F _p-correlation_
_robust hash function exists. Then there is a protocol that uses O_ ( _λ_ ) _1-out-of-2 OTs to realize n_
_instances of random 1-out-of-p OT with semi-honest security, using O_ ( _tλ_ log _n_ ) + poly( _λ_ ) _bits of_
_communication._


We remark that this gives OT with _sublinear communication_ when _t_ = _o_ ( _n/_ ( _λ_ log _n_ )), which
translates to an instance of LPN with noise rate 1 _/ω_ ( _λ_ log _n_ ). If the matrix _Hn′,n_ in _G_ sVOLE is
uniformly random, the computational complexity is dominated by _O_ ( _n_ _[′]_ _·n_ ) arithmetic operations;
using more structured matrices based on LDPC codes or quasi-cyclic codes, we get respective
costs of _O_ ( _n_ _[′]_ ) or _O_ [˜] ( _n_ _[′]_ ) arithmetic and PRG operations.


**5.3.1** **Concrete Efficiency**


In Section A of the Appendix, we analyze these costs more concretely and give a breakdown
of the communication complexity, as well as some approximate runtime estimates based on the
cost of the main operations. For example, for _n ≤_ 2 [22] OTs, the PCG seed size is under 10kB
and requires less than 30kB of communication to create with the distributed setup procedure.
After setup, we estimate that these seeds can be expanded into 16MB of OTs on 128-bit strings
at a rate of around 1 million per second, or 2 million per second when expanding to 1MB, using
a single core of a CPU on a modern laptop. When including the distributed setup procedure, in
these two cases we get an amortized communication complexity of just 2.6 and 0.2 bits per OT,
respectively.


**5.4** **Applications of Silent OT Extension**


Protocols generating (pseudo)random OT have a wide range of applications. In this section we
show how our silent OT extension can plugged in to obtain a batch oblivious pseudorandom
function (OPRF) with under 1 bit of communication per OPRF evaluation on a random input,
which is useful for private set intersection protocols. Further, we sketch how to construct a NIZK
proof system in the preprocessing model, where the setup cost is independent of both the number
and size of statements.


28


_Batch oblivious PRF._ Our random 1-out-of- _p_ OT generator can even be used when _p_ is exponentially large, provided the sender only needs to obtain polynomially many outputs. This type of
random OT can be viewed as a form of batch, one-time oblivious PRF: each string _wi,j_ output
by the sender can be seen as a PRF evaluation _F_ ( _ki, j_ ), where _ki_ is a key implicitly defined
by the sender’s randomness. The receiver learns a random _ui_ and the value _wi,ui_ = _F_ ( _ki, ui_ ).
We can also allow the receiver to choose its evaluation point _ui_, with an additional _λ_ = log _p_
bits of communication. In [KKRT16], this type of OPRF was used to improve the efficiency of
private set intersection protocols. Applying our PCG, we get a highly efficient batch related key
OPRF usable in PSI, where each OPRF evaluation at a chosen point costs around _λ_ bits of
communication. This reduces the overall communication in the PSI protocol from [KKRT16] by
around a factor of two.


_Resuable NIZKs from LPN._ In [BCGI18], it was shown how to use a PCG for vector-OLE to
build a reusable NIZK in the preprocessing model. NIZK in the preprocessing model relaxes
the standard NIZK definition by allowing the prover and the verifier to interact during a preprocessing phase, to generate a respective proving key and verification key. The construction
from the vector-OLE PCG obtained a reusable preprocessing NIZK, where the preprocessing
cost is _independent_ of the number of theorems to be proven, if this is a priori bounded, under
an arithmetic version of LPN.
In Section A of the Appendix, we observe that we can obtain an alternative NIZK construction by using our PCG for random OT, which brings two main advantages:


**–** It only requires the standard LPN assumption over F2, while the NIZK of [BCGI18] must
rely on a generalization of LPN to exponentially large fields.

**–** The preprocessing phase is independent of both the number of theorems to be proven, and the
size of these theorems. In comparison, the preprocessing phase in [BCGI18] is independent
of the number of theorems to be proven, but grows linearly with a bound on the size of each
statement. This is because we use OT instead of VOLE, so are no longer restricted to a batch
setting where the same query must be reused for many statements.


On the down side, our OT-based NIZK protocols do not enjoy some of the efficiency features
of the VOLE-based constructions from [BCGI18]. The latter support NIZK for an NP-relation
represented by an _arithmetic_ circuit of size _s_ over F, where the online computation of both the
prover and the verifier consists of _O_ ( _s_ ) arithmetic operations, and with _O_ (1 _/|_ F _|_ ) soundness error.
We do not know how to achieve this using the current OT-based approach.


**6** **PCG for Constant-Degree Correlations from LPN**


In this section, we describe a pseudorandom correlation generator for arbitrary constant-degree
correlations, from the dual LPN assumption over large fields. We first describe the construction
for the case of bilinear correlations. More precisely, we consider the following type of additive
correlations: the party _Pσ_ receives pseudorandom vectors ( _**x**_ _σ,_ _**z**_ _σ_ ) such that _B_ ( _**x**_ 0 _,_ _**x**_ 1) = _**z**_ 0 + _**z**_ 1,
where _B_ is a bilinear function. We note that this type of correlation generalizes naturally to the
setting where the entries _**x**_ 0 and _**x**_ 1 are additively shared between the parties (instead of being
respectively known to one party), see Section C.


**Theorem 28.** _Suppose the_ ( _HW_ _t,_ **C** _,_ F _p_ )-dual-LPN( _n_ _[′]_ _, n_ ) _assumption holds, and that_ MPFSS _is_
_a secure multi-point FSS scheme. Then the construction G_ bil _(Fig. 5) is a secure PCG for general_
_bilinear correlations._


Correctness follows by inspection, using the correctness of the MPFSS, and the bilinearity of
the tensor product, and the security analysis is essentially indentical to the analysis of the dual
vector-OLE generator described in [BCGI18] (see also Section 5.1).


29


**Construction** _G_ bil


Parameters: 1 _[λ]_ _, n, n_ _[′]_ _, t, p_ _∈_ N, where _n_ _[′]_ _>_ _n_ . A code generation algorithm **C** and
_Hn′,n_ _←_ $ **C** ( _n′, n,_ F _p_ ). A bilinear function _B_ _**c**_ : ( _**α**_ _,_ _**β**_ ) _→_ _**c**_ _·_ ( _**α**_ _⊗_ _**β**_ )⊺, where _⊗_ denotes the
tensor product.


**Gen:** On input 1 _[λ]_ :


1. Pick two random size- _t_ subsets ( _S_ 0 _, S_ 1) of [ _n_ _[′]_ ], sorted in increasing order.
2. Pick two random vector ( _**y**_ 0 _,_ _**y**_ 1) _∈_ (F _[t]_ _p_ [)][2][.]
3. Compute ( _K_ 0 [fss] _[, K]_ 1 [fss][)] _←_ $ MPFSS _._ Gen(1 _λ, fS_ 0 _×S_ 1 _,_ _**y**_ 0 _⊗_ _**y**_ 1 ).
4. Let k0 _←_ ( _n, K_ 0 [fss] _[, S]_ 0 _[,]_ _**[ y]**_ 0 [)][ and][ k] 1 _[←]_ [(] _[n, K]_ 1 [fss] _[, S]_ 1 _[,]_ _**[ y]**_ 1 [)][.]
5. Output (k0 _,_ k1).


**Expand:** On input ( _σ,_ k _σ_ ), parse k _σ_ as ( _n, Kσ_ [fss] _[, S]_ _σ_ _[,]_ _**[ y]**_ _σ_ [)][. Set] _**[ µ]**_ _σ_ _[←]_ [spread] _n_ _[′]_ [(] _[S]_ _σ_ _[,]_ _**[ y]**_ _σ_ [)][ in][ F] _[n]_ _p_ _[′]_ [and] _**[ x]**_ _σ_ _[←]_

_**µ**_ _σ ·_ _Hn′,n_ . Compute _**v**_ _σ ←_ MPFSS _._ FullEval( _σ, Kσ_ [fss][)][ in][ F] _p_ [(] _[n][′]_ [)][2] and set _**z**_ _σ ←−_ _**c**_ _·_ ( _**v**_ _σ ·_ ( _Hn′,n ⊗_ _Hn′,n_ )) [⊺] .
Output ( _**x**_ _σ,_ _**z**_ _σ_ ).


**Fig. 5.** PCG for Bilinear Correlations


_Efficiency._ Instantiating the MPFSS as in [BCGI18], the setup algorithm of _G_ bil outputs seeds of
size _t_ [2] _·_ ( _⌈_ log _n_ _[′]_ _⌉_ ( _λ_ +2)+ _λ_ +log2 _|_ F _|_ ) bits, which amounts to _O_ [˜] ( _t_ [2] ) field elements over a large field
(log2 _|_ F _|_ = _O_ ( _λ_ )). Expanding the seed involves ( _tn_ _[′]_ ) [2] PRG evaluations and _O_ ( _n · n_ _[′]_ ) [2] = _O_ ( _n_ [4] )
arithmetic operations.


_Generalization._ The scheme _G_ bil immediately generalizes to a PCG for arbitrary constant-degree
polynomials, [13] where the size of the shares grows as _O_ [˜] ( _t_ _[d]_ ) and the computational complexity is
_O_ ˜(( _tn_ _[′]_ ) _[d]_ + ( _nn_ _[′]_ ) _[d]_ ). It allows two parties to locally compute, given the shares, additive shares of
( _**r**_ _, P_ ( _**r**_ )), where _**r**_ is pseudorandom (under LPN) and _P_ is a degree- _d_ multivariate polynomial
over F.
To see this, notice that we can replace _**y**_ 0 _⊗_ _**y**_ 1 in **Gen** with _⊗d_ _**y**_ = _**y**_ _⊗· · · ⊗_ _**y**_, where _⊗d_ _**y**_
denotes the tensor product of _**y**_ with itself _d_ times (that is, the list of all degree- _d_ monomials
of _**y**_ ). The parties can then compute shares of all degree- _d_ terms in _P_ ( _**r**_ ) for a random _**r**_ ;
to obtain shares of _**r**_ and the lower-degree terms, we extend the MPFSS values to include
( _**y**_ _,_ _**y**_ _⊗_ _**y**_ _, · · ·, ⊗d−_ 1 _**y**_ ) as well as _⊗d_ _**y**_ .


**Corollary 29.** _Suppose the_ ( _HW_ _t,_ **C** _,_ F _p_ )-dual-LPN( _n_ _[′]_ _, n_ ) _assumption holds, and that_ MPFSS
_is a secure multi-point FSS scheme. Then there exists a secure PCG for general constant-degree_
_correlations, with share size_ _O_ [˜] ( _t_ _[d]_ ) _and computational complexity O_ (( _n · n_ _[′]_ ) _[d]_ ) _._


In particular, using _n_ _[′]_ = _O_ ( _n_ ), we get:


**Corollary 30.** _Assuming the standard LPN assumption over_ F _p with noise rate r_ = _o_ ( _n_ [1] _[/d][−]_ [1] )
_and linear number of samples, there exists a PCG for general degree-d polynomials, with sublinear_
_share size (in the output size n) and polynomial computation._


**6.1** **HSS and Secure Computation for Constant-Degree Polynomials from LPN**


We observe that by Section 4.4 (Generic Construction of HSS from PCG), the above construction
directly gives rise to a homomorphic secret sharing scheme for degree- _d_ multivariate polynomials.
Therefore, we get:


13 In fact, assuming that dual-LPN has 2 _O_ ( _t_ ) security (which is in line with the best known attacks), _t_ can be taken
as small as _ω_ (log _λ_ ), in which case the degree _d_ ( _λ_ ) of the polynomial can be larger, up to _O_ (log _λ/_ log log _λ_ ). The
shares are still of polynomial size _O_ [˜] ( _t_ _[d]_ ), although the computational cost _O_ (( _n·n_ _[′]_ ) _[d]_ ) is slightly superpolynomial.


30


**Corollary 31.** _Suppose the_ ( _HW_ _t,_ **C** _,_ F _p_ )-dual-LPN( _n_ _[′]_ _, n_ ) _assumption holds, and that_ MPFSS _is_
_a secure multi-point FSS scheme. Then there exists a secure HSS for general degree-d multivariate_
_polynomials over_ F _, with share size n_ + _O_ [˜] ( _t_ _[d]_ ) _and computational complexity O_ (( _n · n_ _[′]_ ) _[d]_ ) _._


Plugging this new HSS construction into the result of [BGI16a], we immediately obtain new
results regarding secure computation from the LPN assumption:


**Corollary 32.** _Suppose the_ ( _HW_ _t,_ **C** _,_ F _p_ )-dual-LPN( _n_ _[′]_ _, n_ ) _assumption holds, and that_ MPFSS
_is a secure multi-point FSS scheme. Then there exists a 2-party secure computation protocol with_
_semi-honest security for general degree-d multivariate polynomials over_ F _, with communication_
_O_ ˜( _n_ + _t_ _[d]_ ) _and computational complexity O_ (( _n · n_ _[′]_ ) _[d]_ ) _._


In particular, applying the above corollary to layered circuits, we obtain a generic secure
two-party protocol from LPN with communication smaller than the circuit size:


**Corollary 33.** _Suppose the_ ( _HW_ _t,_ **C** _,_ F _p_ )-dual-LPN( _n_ _[′]_ _, n_ ) _assumption holds, and that_ MPFSS
_is a secure multi-point FSS scheme. Then for any constant c, there exists a 2-party secure com-_
_putation protocol with semi-honest security for arbitrary layered circuits of size s, with total_
_communication bounded by s/c, and computational complexity bounded by s · λ_ [2] _[O]_ [(] _[c]_ [)] _._


**7** **PCG Constructions from Groups and Lattices**


In this section we give PCG constructions for a range of correlations, starting from the generic
construction of Section 4.4. In particular, we will describe PCGs for the generation of bilinear
correlations from groups, and PCGs for so-called authenticated Beaver triples from lattices.
We start this section by presenting two specialized low-degree PRG constructions that will
serve as crucial building blocks for our high-end constructions. Note that a straightforward
choice like Goldreich’s low-degree PRG [Gol00, MST03] turns out to be not suitable. (For more
discussion we refer to Section 7.3.)
In Section 7.3 we deviate from the generic construction by splitting up the evaluation of the
PRG and the evaluation of the function _f_ itself, which is captured in the notion of _compressible_
HSS.
To give a high-level idea, note that one can roughly think of the underlying HSS scheme
to consist of two levels, where multiplication of a level-1 share with a level-2 share yields a
level-2 share. The idea now is to start with _compressed_ level-1 and level-2 shares, which can be
expanded to long pseudorandom level-1 and level-2 shares, on which subsequently _f_ is evaluated
via the HSS itself. In other words, the PRG is evaluated _on the shares directly_ and not via the
HSS operation (see also Section 7.2).
In Section 7.4 we follow the generic construction of Section 4.4 more closely, building on the
MQ-based PRG described in the following and several variants of lattice-based HSS schemes.


**7.1** **Pseudorandom Generators from MQ and LPN**


Let _R_ be a ring and _n ∈_ N. By _U_ _[n]_ ( _R_ ) we denote the uniform distribution on _R_ _[n]_ . Recall that
we consider distributions _D_ _[ℓ]_ over a ring _R_ _[ℓ]_ and write _X ←D_ _[ℓ]_ ( _R_ ) or simply _X ←D_ _[ℓ]_ (if _R_ is
clear from the context) to denote sampling from _R_ _[ℓ]_ via _D_ _[ℓ]_ . Further, for a matrix distribution
_M_ over a ring _R_ _[n][×][m]_ we write _M_ ( _n, m, R_ ) to make the parameters explicit.


_Remark 34 (PRG from MQ)._ Let _R_ be a ring, and _ℓ, n ∈_ N. Let _M_ be a distribution over _R_ _[ℓ]_ [2] _[×][n]_

and **M** _←M_ $ ( _ℓ_ 2 _, n, R_ ). We assume that for an appropriate choice of parameters


PRGMQ : _R_ _[ℓ]_ _→R_ _[n]_ _, r �→_ **M** _[⊤]_ _·_ ( _r ⊗_ _r_ )


31


is a PRG. We say _M_ ( _ℓ_ [2] _, n, R_ ) has _sparsity ρ_, if for every matrix **M** in the image of _M_ ( _ℓ_ [2] _, n, R_ ),
the number of non-zero entries in any column of **M** is at most _ρ_ .
Note that if we choose _M_ ( _ℓ_ [2] _, n, R_ ) = _U_ _[ℓ]_ [2] _[×][n]_ ( _R_ ), the above assumption equals the MQ
assumption of [MI88, Wol05, AHI [+] 17]. While multivariate public-key cryptography has a long
history of schemes being built then broken, we stress that the MQ assumption itself (which
states that it is infeasible to solve a random system of quadratic equations) is believed to be a
conservative assumption (in particular, the pseudorandomness of the MQ-based PRG reduces to
the conjectured _one-wayness_ of solving a random system of quadratic assumptions [BGP06]), and
underlies the security of plausible and well-studied primitives in minicrypt (such as signatures
scheme, or the stream cipher QUAD [BGP06]). Existing attacks on multivariate public-key
cryptosystems all exploited the fact that the security of these systems did not in fact reduce to
the MQ assumption. Furthermore, variants of MQ with a sparse matrix were considered several
time as a natural optimization of MQ-based schemes [BCJ07, LLY08], and the resistance of the
variant with sparse matrix against classical attacks was analyzed in [BCJ07, DyY07].


_Remark 35 (D_ _[ℓ]_ ( _R_ ) _-PRG from LPN)._ Let _R_ be a ring, and _ℓ, k, c, τ, n ∈_ N, such that _ℓ_ = _τck_ .
Let _M_ be a distribution on _R_ _[τ][ c][×][n]_ and **M** _←M_ $ ( _τ c, n, R_ ). Let



PRGLPN : ( _R_ _[τ]_ ) _[ck]_ _→R_ _[n]_ _,_ ( _r_ 1 _, . . ., rck_ ) _�→_ **M** _[⊤]_ _·_



_k−_ 1


_r_ 1+ _i·c ⊗· · · ⊗_ _rc_ + _i·c,_

_i_ =0



where _ri ∈{_ 0 _,_ 1 _}_ _[τ]_ for all 1 _≤_ _i ≤_ _ck_ . We assume that for appropriate choice of parameters
PRGLPN is a _D_ _[ℓ]_ ( _R_ )-PRG, where _D_ _[ℓ]_ is the distribution returning vectors that have _exactly_ one
non-zero entry (chosen uniformly at random in _R\{_ 0 _}_ ) in every block of length _τ_ .
Note that [�] _[k]_ _i_ =0 _[−]_ [1] _[r]_ [1+] _[i][·][c][ ⊗· · · ⊗]_ _[r][c]_ [+] _[i][·][c]_ [ yields a random vector in] _[ R][τ][ c]_ [ with exactly] _[ k]_ [ non-zero]
entries. Therefore, the above assumption corresponds to the (Ber _k_ ( _R_ ) _[τ][ c]_ _, M, R_ )-dual-LPN( _τ_ _[c]_ _, n_ )
assumption, where Ber _k_ ( _R_ ) _[τ][ c]_ is the distribution returning vectors in _R_ _[τ][ c]_ with exactly _k_ non-zero
entries.


**7.2** **Semi-Generic PCG Construction from Compressible HSS**


As mentioned before, while our group-based constructions described in the following section build
upon the generic approach, they exploit the specific structure of the underlying HSS to achieve
better parameters: the generic construction would require a degree-4 HSS already to generate
bilinear correlations using the LPN-based PRG. In contrast, our constructions achieve the same
expressivity starting only from degree-2 HSS, building upon their homomorphic properties. The
essence of this approach is captured in the following corollary. For a more formal treatment of
compressible HSS we refer to Section C.3.


**Corollary 36 (Informal).** _Let R be a ring and n, m, τ, c, k ∈_ N _. Let F ⊆{f_ : _R_ _[n]_ _→R_ _[m]_ _}_
_be a family of functions. Let_ HSS = (HSS _._ Gen _,_ HSS _._ Share _,_ HSS _._ Eval) _be an homomorphic se-_
_cret sharing scheme for F with overhead O_ HSS _that supports degree-c compression of the shares_
_(i.e. compressed shares can be decompressed via degree-c homomorphic operations preserving the_
_respective share-level). Then, under the_ (Ber _k_ ( _R_ ) _[τ][ c]_ _, M, R_ ) _-dual-LPN_ ( _τ_ _[c]_ _, n_ ) _assumption, there_
_exists a PCG for the correlation generator CF with key-length upper bounded by τck · O_ HSS _._


**7.3** **Group-Based PCG for Bilinear Correlations: an Overview**


In this section, we describe a construction of a PCG for general bilinear correlations, building
upon the group-based HSS scheme of [BGI16a, BGI17, BCG [+] 17]. Since our construction is quite
involved, and the full description would not fit in the body of this paper, we only provide a highlevel overview here; the detailed construction is given in Appendices C, D, and E. The high-level


32


idea of our construction is best explained by the compressible HSS abstraction, outlined in the
“Overall Methodology” section of the introduction. To construct a PCG for bilinear correlations,
we rely on the group-based HSS of [BGI16a, BGI17, BCG [+] 17]. While this HSS can support
evaluation of arbitrary branching programs, this comes at a very high computational cost, which
makes it concretely impractical. Note that the full version of [BCG [+] 17] describes a construction
of PCG (which is called “cryptographic capsule” in their terminology) building upon the groupbased HSS together with Goldreich’s low-degree PRG [Gol00, MST03]. While the authors did
not provide concrete efficiency estimations for this construction, our rough calculations show
that it is entirely impractical: Goldreich’s PRG requires very large seeds (at least 2 [14] bit long
to achieve a stretch of only _n_ [1] _[.]_ [45] according to the recent study of [CDM [+] 18]), and the HSS
must be employed in a parameter regime where encoding _each bit_ of the seed requires _O_ ( _λ_ )
ElGamal ciphertext (e.g. 160 ciphertexts, when targetting 80 bits of security). Furthermore, the
group-based HSS has an inverse failure probability per output which scales superlinearly with
the encoding size. We estimate that an optimized implementation of their scheme would require
a few hours of runtime to generate each output, and the PCG seed remains larger than the total
amount of correlation generated (in fact, larger than the cost of a naive interactive generation
of the material) for any feasible value of _n_ .


Our improvement stems from two key observations. First, when the HSS is restricted to
evaluating only _bilinear_ function (as opposed to general branching programs), the encodings
in the group-based HSS can be considerably smaller, a single ElGamal ciphertext per bit of
the seed (this was observed in [BCG [+] 17]). This in itself would not suffice, since generating the
bilinear correlation requires first evaluating a PRG, then computing a bilinear function on top
of that, which requires HSS of degree at least 4 (since a PRG must have degree at least 2 in
its inputs). Our second key observation is that by relying on the BGN cryptosystem instead
of ElGamal (which requires pairings but allows homomorphic evaluation of degree-3 functions
on the ciphertext), extending the HSS-encoded seed into long pseudorandom encodings can be
done directly on the encoding, without requiring any of the HSS operations. More precisely,
the group-based HSS requires two types of encodings: a level-1 encoding of a vector _**x**_, which
is essentially a bitwise ElGamal encryption (when restricting our attention to HSS for degree-2
functions), and a level-2 encoding of a vector _**y**_, which is essentially a pair of additive shares of
both _**y**_ and sk _·_ _**y**_, where sk is the ElGamal secrey key; the HSS operations allows the parties to
locally compute shares of _B_ ( _**x**_ _,_ _**y**_ ) from these encodings, for any bilinear function _B_ .


Using the BGN encryption scheme [BGN05], the level-1 encoding of a pseudorandom vector _**x**_
of length _n_ can be locally compressed by relying on the LPN-based PRG described in Section 4.4:
the compressed encoding contains 2 _k_ component-wise BGN encryptions of random length- _[√]_ ~~_n_~~
unit vectors _**u**_ _i,_ _**v**_ _i_, for a total size of 2 _k_ _[√]_ ~~_n_~~ BGN ciphertexts, where _k_ is a parameter of ther
underlying LPN assumption which denotes the number of noisy coordinates in the error vector.
Then, the parties can homomorphically compute BGN encryptions of _**x**_ = _M_ _·_ [�] _[k]_ _i_ =1 _**[u]**_ _[i][⊗]_ _**[v]**_ _[i]_ [, where]
_M_ is a public code matrix; security follows from the dual LPN assumption with code matrix _M_
by observing that [�] _i_ _[k]_ =1 _**[u]**_ _[i][ ⊗]_ _**[v]**_ _[i]_ [ is just a uniformly random] _[ k]_ [-sparse vector. At the same time,]
using two parallel instances of the recent LPN-based PCG for vector-OLE of [BCGI18] allows to
efficiently compress shares of _**y**_ and sk _·_ _**y**_, where _**y**_ is a pseudorandom vector and sk is a shared
value, to only _O_ ( _λk_ log _n_ ) bits. Hence, we get a highly optimized PCG for bilinear functions by
distributing compressed shares of level-1 and level-2 encodings of pseudorandom vectors to the
parties, from which they can locally expand the compressed shares and apply the HSS operation
to obtain shares of _B_ ( _**x**_ _,_ _**y**_ ).


In Appendix C, we formally introduce the construction following the above informal overview.
In Appendix D, we discuss many optimizations that can be applied to the scheme, in particular
by relying on new variants of the LPN assumption, which we introduce and analyze in the
same section. Eventually, in Appendix E, we provide detailed concrete efficiency estimations for
our PCG, for generating OLE correlations over small fields, together with further optimizations


33


tailored to this setting, and a concrete analysis of the resistance of our new assumption to a
variety of attacks. Note that our PCG are already useful for generating OT correlations, since
they are _programmable_, and therefore allow to generate multiparty correlations from pairwise
correlations (unlike our silent OT extension protocol) – see Section 8 for the details.
A downside of the group-based HSS is that it only guarantees an imperfect correctness
for the output, with an inverse-polynomial failure probability. To use the generated material
in a subsequent protocols, the parties must therefore first _sanitize_ the output, converting the
faulty correlations into non-faulty correlations. This is non-trivial, since the position of the faulty
outputs cannot be simply revealed, as it depends on secret information that should not be leaked.
We apply the punctured OT strategy of [BGI17] to describe an efficient sanitization procedure,
and we provide detailed concrete estimates of its efficiency in our setting. The strategy only
requires adding a negligible amount of material to the PCG seed, and requires less than 3 bits of
amortized communication per sanitized correlation. Eventually, building upon our new protocol
for silent OT extension from Section 5, we devise an entirely new sanitization procedure, which
is much more efficient and is compatible with efficient distributed seed generation.


**7.3.1** **Concrete Efficiency**


Based on our our calculations in Appendices C, D, and E, we estimate that our group-based
PCG for bilinear correlations should generate correlations at a rate of a few hundred milliseconds
per (sanitized) output (e.g. about 200ms for generating one OLE correlation over a small ring,
amortizing over _n >_ 2 [20] outputs), with a seed size reaching its breakeven point (where the
size in bits of the seed is smaller than the number of outputs generated) for target number of
correlations around 2 [24] . Since this is a fairly low number (preprocessing phases in standard MPC
protocols must already generate billions of correlated values for securely evaluating moderately
large functions), we believe that our result is already of practical interest. We stress again that
our estimates are based on counting the number of operations and estimating the cost of each
operation using benchmarks; the actual running time of an implementation might be somewhat
higher due to other costs such as cache misses.


**7.4** **PCG from Lattices**


In this section we consider constructing PCGs from lattices for generating a broader range of
correlations. One example of useful correlations are authenticated Beaver triples which are used
to achieve fast online computation time in multi-party protocols like [DPSZ12]. PCGs based on
lattices can replace the preprocessing phase to yield protocols with very fast online time, where
the players can exchange a short seed at any point of time and then expand their respective
seeds silently before engaging in a secure computation. Thus, even though PCGs from lattices
come with an expensive setup and slower expansion time, they are useful to obtain protocols
with better overall complexity.
We focus on the use-case of generating 2-party shares of authenticated Beaver triples, that
is additive shares of tuples ( _a, b, ab_ ) _,_ ( _aα, bα, abα_ ), where _α_ is a MAC-key for authentication
(not known to any party in the plain). In the following we describe different lattice-based PCG
constructions for generating such shared triples and provide efficiency estimates in Figure 2. For
details we refer to Section F in the Appendix.
We follow the high-level approach of Section 4.4 based on homomorphic secret sharing (HSS),
where the parties first jointly generate a shared PRG seed and for expansion disjointly evaluate
_fα ◦_ PRG on the shares, where _fα_ : ( _a, b_ ) _�→_ ( _a, b, ab, aα, bα, abα_ ). We instantiate the HSS scheme
required in different ways. As underlying encryption scheme we use the BGV encryption scheme

[BGV12]. For the most efficient instantiation we use the pseudorandom generator PRGMQ : Z _[ℓ]_ _p_ _[→]_
Z _[n]_
_p_ [from Remark][ 34][ with] _[ n]_ [ =] _[ ℓ]_ [2] _[/]_ [24][, where we choose a matrix with sparsity] _[ ρ]_ [ = 100][. Note that]
the choice of _ρ_ is somewhat arbitrary and should be taken with some care, but to our knowledge


34


Underlying HSS |key| |triples| setup expansion exp./triple


[BGV12] 3 GB 17 GB _≈_ 20 s 8 _._ 0 h 0 _._ 16 ms

[BGV12] (iterative) 3 GB 1 _._ 6 MB/it. _≈_ 20 s 10 s/it. 0 _._ 57 ms

[BGV12] (w/ packing) 6 MB 1 _._ 1 GB _<_ 0 _._ 1 s 900 h 280 ms

[BGV12, BKS19] 3 GB 17 GB _≈_ 20 s 7 _._ 6 h 0 _._ 15 ms


**Table 2.** Overview of estimated efficiency of lattice-based approach to generate authenticated Beaver triples. The
numbers provided are time estimates for joint seed generation (with security against semi-honest adversaries)
and expansion. The numbers are based on [CS16], for [BGV12] supporting depth-4 homomorphic operations
(note that depth-3 would suffice) and plaintext space modulus _p ≈_ 2 [128] . As underlying encryption scheme we
consider [BGV12] with plaintext space _Rp_ = _[∼]_ Z _[N]_ _p_ [and ciphertext space] _[ R]_ _q_ [2][, where] _[ R]_ [ :=][ Z][[] _[X]_ []] _[/]_ [(] _[X]_ _[N]_ [ + 1)][. The]
runtime estimates are based on NFLLib [ABG [+] 16] with log _q ≈_ 744 and _N_ = 2 [14] . Our results: We can expand
correlated seeds of size ‘|key|’ to 128-bit authenticated multiplication triples of total size ‘|triples|’. As PRG we

employ PRGMQ : Z _[ℓ]_ _p_ _[→]_ [Z] _p_ _[ℓ]_ [2] _[/]_ [24], based on the _M_ ( _ℓ_ [2] _, ℓ_ [2] _/_ 24 _, Rp_ )-MQ assumption with sparsity _ρ_ = 100 (here, _ℓ_ = 2 [9]

for all rows w/o packing and _ℓ_ = _N_ for the row w/ packing). The number of (maximal) obtained triples is
_ℓ_ [2] _· N/_ 24 for the rows with naive ciphertext packing (including the iterative version) and _N_ [2] _/_ 24 for the row with
smart packing. Setup requires communication of roughly size |key| per party. We ignore small contributions like
setting up the public key and generating suitable shares of the MAC key _α_, as computation and communication
are dominated by generation and distribution of encryptions of the PRG seeds.


does not give rise to any attacks: While algebraic attacks either do not profit from sparsity at
all (like the Groebner basis attack) or not significantly (like the XL attack), SAT solvers, which
indeed heavily take advantage of sparsity, are still far from feasible for our choice of parameters.
In [DHRW16, BKS19] it is shown how to construct an HSS directly from a somewhat homomorphic encryption scheme, when the underlying encryption scheme additionally supports
distributed decryption (i.e. decryption with additive shares of the secret key yields additive
shares of the plaintext). We give a more detailed explanation in Theorem 55 in the Appendix.
Our first PCG is based on this construction (instantiated with the encryption scheme of Brakerski et al. [BGV12]). On a high level, the resulting PCG is as follows.


**Seed generation.** The key generation algorithm of the underlying encryption scheme is called
and additive shares of the secret key generated. Further, a MAC key _α ∈_ Z _p_ and PRG seeds
_ra, rb_ _←_ $ Z _ℓp_ [are chosen uniformly at random and encrypted (componentwise). The parties]
each obtain the public key, their respective share of the secret key and _all_ encryptions as
PCG seed. Public key and secret key shares of the encryption scheme and the encryption of
the MAC key _α_ can be reused across many instances.
**Expansion.** Both parties homomorphically evaluate _Fα_ (PRG( _ra_ ) _,_ PRG( _rb_ )) on the ciphertexts
(via the homomorphic operations of the underlying encryption scheme), where _Fα_ : Z _[n]_ _p_ _[×]_ [Z] _[n]_ _p_ _[→]_
(Z _[n]_ _p_ [)][6][ corresponds to evaluating] _[ f][α]_ [componentwise on each of the] _[ n]_ [ input tuples. Finally,]
each party decrypts the result with their respective share of the secret key.


The described approach would allow expanding 2 _ℓ_ ciphertexts into _n_ shares of authenticated
Beaver triples (over Z _p_ ). Additionally, we employ naive ciphertext packing [SV14]: Instead of
encrypting a single Z _p_ -element at a time one can ‘pack’ _N_ Z _p_ -elements into each ciphertext
(where _N_ = 2 [14] is the dimension of the plaintext space over Z). This way, starting with 2 _ℓ_
ciphertexts, expansion yields _N ·_ _n_ shared authenticated Beaver triples. For more details we refer
to Section F in the Appendix.
The second approach is based on the observation that not all authenticated Beaver triples
have to be computed at once, employing the sparsity of the MQ-matrix. This is particularly
desirable, as it allows computing correlations incrementally, only when needed. Note though
that the given iterative approach is somewhat limited, as it is still restricted to sub-quadratic
stretch and allows only to compute _N_ Beaver triples at a time (due to naive ciphertext packing).
The third approach uses ciphertext packing more smartly, by letting the different ‘slots’ of
the ciphertexts interact with each other. Here, starting with a single ciphertext (holding 2 [14]


35


plaintexts), we achieve almost quadratic stretch to 2 [28] _/_ 24 triples. The better expansion rate
(allowing to go from _N_ to _≈_ _N_ [2] instead of from _ℓN_ to _≈_ _ℓ_ [2] _N_ triples), comes at a cost: Due
to the high computational costs introduced by key switching during matrix multiplication, this
approach seems currently impractical.
The last approach replaces the homomorphic multiplication with the MAC key _α_ on ciphertexts with the more efficient multiplication operation of the HSS by Boyle et al. [BKS19]. More
precisely, during seed generation secret shares of the MAC key _α_ times the secret key sk are
generated (instead of an encryption of _α_ ). Then, the last level of multiplication (i.e. to obtain
_aα, bα, abα_ ) can be replaced by a distributed decryption with the shares of _α ·_ sk, saving 3 homomorphic multiplications per triple generated. Note that this construction is compatible with
the ‘iterative’ and ‘packed’ versions of BGV described. It does not seem competitive to use an
HSS solely based on [BKS19], as, when handling more than one homomorphic multiplication,
their scheme has to account for the plaintext magnitude, which in the described setting would
lead to significantly larger parameters.


**8** **Multi-Party PCG for Bilinear Correlations**


In this section, we construct _multi-party_ PCGs for a useful class of bilinear correlations, capturing _M_ -party OT, _M_ -party vector OLE, _M_ -party Beaver triples, and more. Incorporating
into appropriate existing secure computation protocols, this yields secure _M_ -party protocols for
corresponding computations, with short correlated randomness, whose online execution requires
only lightweight information theoretic operations and communication that scales _linearly_ in the
number of parties _M_ .
Our construction approach provides a semi-generic transformation from any PCG for the corresponding 2-party bilinear correlation that satisfies an additional “programmability” property.
Roughly, this property requires a way of “reusing” inputs across instances without compromising
security. The _M_ -party construction will leverage this structure by executing _M_ ( _M −_ 1) pairwise
instances of the underlying 2-party PCG, for all the “cross-terms.”
We obtain _M_ -party PCGs for various bilinear correlations by identifying corresponding 2party PCG constructions that satisfy the required programmability notion. In particular:


**–** _M_ -party VOLE: From lightweight DPF and LPN, leveraging the 2-party VOLE generator
of [BCGI18].

**–** _M_ -party OT / Beaver triple: From group-based or lattice-based HSS, leveraging our 2-party
PCGs from the previous sections.


Interestingly, the lightweight 2-party OT PCG from Section 5 does not seem to support programmability in the necessary manner, since the resulting sender message pairs are implicitly
defined as a function of the receiver’s bit selections.


We begin by defining the class of bilinear correlations, and the PGC programmability property to which our transformation applies.


**Definition 37 (Simple Bilinear Correlation: 2-party).** _A_ 2 _-party correlation C is a_ simple
bilinear relation _if there exists Abelian groups_ G1 _,_ G2 _,_ G _T and a bilinear map e_ : G1 _×_ G2 _→_ G _T_
_for which C is a distribution over_ (G1 _,_ G _T_ ) _×_ (G2 _×_ G _T_ ) _of the form_


_C_ = _{_ (( _a, c_ ) _,_ ( _b, d_ )) _| a ←_ G1 _, b ←_ G2 _, c ←_ G _T, d_ = _e_ ( _a, b_ ) + _c} ._


_Note that the groups_ G _and map e are implicitly parametrized by λ._


This captures, for example, Vector OLE (with G1 = G _T_ = F _[n]_ and _e_ : F _[n]_ _×_ F _→_ F _[n]_ by
_e_ ( _**u**_ _, x_ ) = _x_ _**u**_ ), _n_ -OLE (with G1 = G2 = G _T_ = F _[n]_ and _e_ : F _[n]_ _×_ F _[n]_ _→_ F _[n]_ by _e_ ( _**u**_ _,_ _**y**_ ) = _**u**_ _∗_ _**v**_
componentwise multiplication), and String OT and _n_ -OT as special cases for F = F2.


36


**Definition 38 (Simple Bilinear Correlation:** _M_ **-party).** _For simple bilinear_ 2 _-party cor-_
_relation C_ 2 _specified by e_ : G1 _×_ G2 _→_ G _T we define the corresponding M_ _-party correlation CM_
_by_



$ $ $
_ai_ _←_ G1 _, bi_ _←_ G2 _∀i ∈_ [ _M_ ] _, ci_ _←_ G _T ∀i ∈_ [ _M −_ 1] _,_

�� _M_     
����� _cM_ = _e_ _i_ =1 _[a][i][,]_ [ �] _i_ _[M]_ =1 _[b][i]_ _−_ [�] _[M]_ _i_ =1 _[−]_ [1] _[c][i]_







_CM_ =





( _ai, bi, ci_ ) _i∈_ [ _M_ ]



_Example 39._ Useful specific examples:


**–** _CM_ -VOLE: Each party holds random ( _**u**_ _i, xi,_ _**v**_ _i_ ) _∈_ F _[n]_ _×_ F _×_ F _[n]_

s.t. ( [�] _xi_ ) ( [�] _**u**_ _i_ ) = ( [�] _**v**_ _i_ )

**–** _CM_ -OLE: Each party holds random ( _**u**_ _i,_ _**v**_ _i,_ _**w**_ _i_ ) _∈_ F _[n]_ _×_ F _[n]_ _×_ F _[n]_

s.t. ( [�] _**u**_ _i_ ) _∗_ ( [�] _**v**_ _i_ ) = ( [�] _**w**_ _i_ ) (componentwise)


We consider 2-party PCGs that support the following notion of _programmability_ : loosely,
that allow a party to “reuse” a piece of his input (either _a ∈_ G1 or _b ∈_ G2) in multiple instances
of the 2-party correlation, while maintaining security.


**Definition 40 (Programmability).** _We will say that a PCG_ PCG = (PCG _._ Gen _,_ PCG _._ Expand)
_for simple bilinear_ 2 _-party correlation C_ 2 _(specified by e_ : G1 _×_ G2 _→_ G _T ) support_ reusable inputs
_if_ PCG _._ Gen(1 _[λ]_ ) _takes additional random inputs a_ _[′]_ _, b_ _[′]_ _∈{_ 0 _,_ 1 _}_ _[⋆]_ _such that:_


**–** _**Programmability.**_ _There exist public efficiently computable functions fa, fb for which_



 _a_ _[′]_ _, b_ _[′]_ _←_ $ _,_ (k0 _,_ k1) _←_ $ PCG _._ Gen(1 _λ, a′, b′_ )

 ( _a, c_ ) _←_ PCG _._ Expand(0 _,_ k0) _,_ : _b_ _[a]_ = [ =] _f_ _[ f]_ _b_ _[a]_ ( [(] _b_ _[a][′]_ ) _[′]_ [)]
( _b, d_ ) _←_ PCG _._ Expand(1 _,_ k1)



Pr






 _≥_ 1 _−_ negl( _λ_ ) _._




**–** _**Security.**_ _The distributions_


      - ( _a_ _[′]_ _, b_ _[′]_ ) _←_ $       (k1 _, b_ _[′]_ _, fa_ ( _a_ _[′]_ )) ���� (k0 _,_ k1) _←_ $ PCG _._ Gen(1 _λ, a′, b′_ ) _and_




- ( _a_ _[′]_ _, b_ _[′]_ ) _←_ $ _,_ ˜ _a ←_ $ (k1 _, b_ _[′]_ _, fa_ (˜ _a_ )) ���� (k0 _,_ k1) _←_ $ PCG _._ Gen(1 _λ, a′, b′_ )



_are computationally close. A symmetric requirement holds for b_ _[′]_ _,_ [˜] _b._


In Appendix G, we present and analyze the following general transformation from any _pro-_
_grammable_ 2-party PCG for a simple bilinear correlation to a _M_ -party PCG for the corresponding
multi-party correlation.


**Theorem 41 (Multi-party Simple Bilinear PCG).** _Let_ PCG2 = (PCG2 _._ Gen _,_ PCG2 _._ Expand)
_be a programmable PCG for simple bilinear_ 2 _-party correlation C_ 2 _(specified by e_ : G1 _×_ G2 _→_ G _T_ )
_with key sizes s_ 0( _λ_ ) _, s_ 1( _λ_ ) _. Then there exists a PCG_ PCG _M_ = (PCG _M_ _._ Gen _,_ PCG _M_ _._ Expand) _for_
_the corresponding M_ _-party correlation CM with the following properties._


**–** PCG _M_ _._ Gen(1 _[λ]_ ) _runs M_ ( _M −_ 1) _executions of_ PCG2 _._ Gen _; each output key_ k _i, i ∈_ [ _M_ ] _, has_
_size_ ( _M −_ 1)( _s_ 0( _λ_ ) + _s_ 1( _λ_ ) + _λ_ ) _bits._

**–** PCG _M_ _._ Expand( _i,_ k _i_ ) _runs_ 2( _M_ _−_ 1) _executions of_ PCG2 _._ Expand _and makes_ ( _M_ _−_ 1) _evaluations_
_of a pseudorandom generator._


37


_Acknowledgements._ We would like to thank Peter Rindal and Melissa Rossi for helpful discussions
and pointers, and the anonymous Crypto 2019 reviewers for their comments.


E. Boyle, N. Gilboa, and Y. Ishai supported by ERC Project NTSC (742754). E. Boyle additionally supported by ISF grant 1861/16 and AFOSR Award FA9550-17-1-0069. G. Couteau
supported by ERC Project PREP-CRYPTO (724307). N. Gilboa additionally supported by ISF
grant 1638/15 and a grant by the BGU Cyber Center. Y. Ishai additionally supported by ISF
grant 1709/14, NSF-BSF grant 2015782, and a grant from the Ministry of Science and Technology, Israel and Department of Science and Technology, Government of India. L. Kohl supported
by ERC Project PREP-CRYPTO (724307), by DFG grant HO 4534/2-2 and by a DAAD scholarship. This work was done in part while visiting the FACT Center at IDC Herzliya, Israel.
P. Scholl supported by the European Union’s Horizon 2020 research and innovation programme
under grant agreement No 731583 (SODA), and the Danish Independent Research Council under
Grant-ID DFF-6108-00169 (FoCC).


**References**


ABD [+] 16. C. Aguilar, O. Blazy, J.-C. Deneuville, P. Gaborit, and G. Zémor. Efficient encryption from random
quasi-cyclic codes. Cryptology ePrint Archive, Report 2016/1194, 2016. `[http://eprint.iacr.org/](http://eprint.iacr.org/2016/1194)`
`[2016/1194](http://eprint.iacr.org/2016/1194)` .
ABG [+] 16. C. Aguilar Melchor, J. Barrier, S. Guelton, A. Guinet, M.-O. Killijian, and T. Lepoint. NFLlib:
NTT-based fast lattice library. In _CT-RSA 2016_, LNCS. Springer, 2016.
ADI [+] 17. B. Applebaum, I. Damgård, Y. Ishai, M. Nielsen, and L. Zichron. Secure arithmetic computation
with constant computational overhead. LNCS. Springer, 2017.
AFS03. D. Augot, M. Finiasz, and N. Sendrier. A fast provably secure cryptographic hash function. Cryptology ePrint Archive, Report 2003/230, 2003. `[http://eprint.iacr.org/2003/230](http://eprint.iacr.org/2003/230)` .
AG10. S. Arora and R. Ge. Learning parities with structured noise. In _Electronic Colloquium on Computa-_
_tional Complexity (ECCC)_, page 66, 2010.
AG11. S. Arora and R. Ge. New algorithms for learning in presence of errors. In _ICALP 2011, Part I_,
LNCS. Springer, July 2011.
AHI11. B. Applebaum, D. Harnik, and Y. Ishai. Semantic security under related-key attacks and applications.
In _ICS 2011_ . Tsinghua University Press, January 2011.
AHI [+] 17. B. Applebaum, N. Haramaty, Y. Ishai, E. Kushilevitz, and V. Vaikuntanathan. Low-complexity
cryptographic hash functions. 2017.
AIK09. B. Applebaum, Y. Ishai, and E. Kushilevitz. Cryptography with constant input locality. _Journal of_
_Cryptology_, (4), October 2009.
Ale03. M. Alekhnovich. More on average case vs approximation complexity. In _44th FOCS_ . IEEE Computer
Society Press, October 2003.
ALSZ13. G. Asharov, Y. Lindell, T. Schneider, and M. Zohner. More efficient oblivious transfer and extensions
for faster secure computation. In _ACM CCS 13_ . ACM Press, November 2013.
Bar04. M. Bardet. _Étude des systèmes algébriques surdéterminés. Applications aux codes correcteurs et à la_
_cryptographie_ . PhD thesis, Université Pierre et Marie Curie-Paris VI, 2004.
BCG [+] 17. E. Boyle, G. Couteau, N. Gilboa, Y. Ishai, and M. Orrù. Homomorphic secret sharing: Optimizations
and applications. In _ACM CCS 17_ . ACM Press, 2017.
BCG [+] 19. E. Boyle, G. Couteau, N. Gilboa, Y. Ishai, L. Kohl, and P. Scholl. Efficient pseudorandom correlation
generators: Silent OT extension and more. In _Advances in Cryptology - CRYPTO 2019, 38th Annual_
_International Cryptology Conference, Santa Barbara, CA, USA, August 18-22, 2019. Proceedings_,
2019.
BCGI18. E. Boyle, G. Couteau, N. Gilboa, and Y. Ishai. Compressing vector OLE. In _ACM CCS 18_ . ACM
Press, 2018.
BCJ07. G. V. Bard, N. T. Courtois, and C. Jefferson. Efficient methods for conversion and solution of
sparse systems of low-degree multivariate polynomials over GF(2) via SAT-Solvers. Cryptology ePrint
Archive, Report 2007/024, 2007. `[http://eprint.iacr.org/2007/024](http://eprint.iacr.org/2007/024)` .
BDOZ11. R. Bendlin, I. Damgård, C. Orlandi, and S. Zakarias. Semi-homomorphic encryption and multiparty
computation. In _EUROCRYPT 2011_, LNCS. Springer, May 2011.
Bea91. D. Beaver. Efficient multiparty protocols using circuit randomization. In _Advances in Cryptology -_
_CRYPTO ’91, 11th Annual International Cryptology Conference, Santa Barbara, California, USA,_
_August 11-15, 1991, Proceedings_, _Lecture Notes in Computer Science_ 576, pages 420–432. Springer,
1991.


38


Bea96. D. Beaver. Correlated pseudorandomness and the complexity of private computations. In _Proceedings_
_of the Twenty-Eighth Annual ACM Symposium on the Theory of Computing, Philadelphia, Pennsyl-_
_vania, USA, May 22-24, 1996_, pages 479–488, 1996.
BFKL93. A. Blum, M. L. Furst, M. J. Kearns, and R. J. Lipton. Cryptographic primitives based on hard
learning problems. In _Advances in Cryptology - CRYPTO ’93, 13th Annual International Cryptology_
_Conference, Santa Barbara, California, USA, August 22-26, 1993, Proceedings_, pages 278–291, 1993.
BFSY05. M. Bardet, J. Faugere, B. Salvy, and B. Yang. Asymptotic behaviour of the index of regularity of
quadratic semi-regular polynomial systems. In _The Effective Methods in Algebraic Geometry Confer-_
_ence (MEGA’05)(P. Gianni, ed.)_, pages 1–14. Citeseer, 2005.
BGI15. E. Boyle, N. Gilboa, and Y. Ishai. Function secret sharing. LNCS. Springer, 2015.
BGI16a. E. Boyle, N. Gilboa, and Y. Ishai. Breaking the circuit size barrier for secure computation under
DDH. In _CRYPTO 2016, Part I_, LNCS. Springer, August 2016.
BGI16b. E. Boyle, N. Gilboa, and Y. Ishai. Function secret sharing: Improvements and extensions. In _ACM_
_CCS 16_ . ACM Press, 2016.
BGI17. E. Boyle, N. Gilboa, and Y. Ishai. Group-based secure computation: Optimizing rounds, communication, and computation. LNCS. Springer, 2017.
BGI [+] 18. E. Boyle, N. Gilboa, Y. Ishai, H. Lin, and S. Tessaro. Foundations of homomorphic secret sharing.
In _9th Innovations in Theoretical Computer Science Conference, ITCS 2018, January 11-14, 2018,_
_Cambridge, MA, USA_, pages 21:1–21:21, 2018.
BGN05. D. Boneh, E.-J. Goh, and K. Nissim. Evaluating 2-DNF formulas on ciphertexts. In _TCC 2005_,
LNCS. Springer, February 2005.
BGP06. C. Berbain, H. Gilbert, and J. Patarin. QUAD: A practical stream cipher with provable security. In
_EUROCRYPT 2006_, LNCS. Springer, May / June 2006.
BGV12. Z. Brakerski, C. Gentry, and V. Vaikuntanathan. (Leveled) fully homomorphic encryption without
bootstrapping. In _ITCS 2012_ . ACM, January 2012.
BH74. J. R. Bunch and J. E. Hopcroft. Triangular factorization and inversion by fast matrix multiplication.
_Mathematics of Computation_, 28(125):231–236, 1974.
BKS19. E. Boyle, L. Kohl, and P. Scholl. Homomorphic secret sharing from lattices without fhe. In _EURO-_
_CRYPT ’19_, 2019. `[https://eprint.iacr.org/2019/129](https://eprint.iacr.org/2019/129)` .
Bor57. J. L. Bordewijk. Inter-reciprocity applied to electrical networks. _Applied Scientific Research, Section_
_A_, 6(1):1–74, 1957.
CCK [+] 18. M. Chen, C. Cheng, P. Kuo, W. Li, and B. Yang. Multiplying boolean polynomials with frobenius
partitions in additive fast fourier transform. _CoRR_, abs/1803.11301, 2018.
CDI05. R. Cramer, I. Damgård, and Y. Ishai. Share conversion, pseudorandom secret-sharing and applications
to secure computation. In _TCC 2005_, LNCS. Springer, February 2005.
CDI [+] 18. M. Chase, Y. Dodis, Y. Ishai, D. Kraschewski, T. Liu, R. Ostrovsky, and V. Vaikuntanathan. Reusable
non-interactive secure computation. _IACR Cryptology ePrint Archive_, 2018:940, 2018.
CDM [+] 18. G. Couteau, A. Dupin, P. Méaux, M. Rossi, and Y. Rotella. On the concrete security of Goldreich’s
pseudorandom generator. LNCS. Springer, December 2018.
CDN01. R. Cramer, I. Damgård, and J. B. Nielsen. Multiparty computation from threshold homomorphic
encryption. In _Advances in Cryptology - EUROCRYPT 2001, International Conference on the Theory_
_and Application of Cryptographic Techniques, Innsbruck, Austria, May 6-10, 2001, Proceeding_, pages
280–299, 2001.
Cou19. G. Couteau. A note on the communication complexity of multiparty computation in the correlated
randomness model. In _Advances in Cryptology - EUROCRYPT_ . Springer, 2019.
CS16. A. Costache and N. P. Smart. Which ring based somewhat homomorphic encryption scheme is best?
In _CT-RSA 2016_, LNCS. Springer, 2016.
CW90. D. Coppersmith and S. Winograd. Matrix multiplication via arithmetic progressions. _Journal of_
_symbolic computation_, 9(3):251–280, 1990.
DGN [+] 17. N. Döttling, S. Ghosh, J. B. Nielsen, T. Nilges, and R. Trifiletti. TinyOLE: Efficient actively secure
two-party computation from oblivious linear function evaluation. In _ACM CCS 17_ . ACM Press, 2017.
DHRW16. Y. Dodis, S. Halevi, R. D. Rothblum, and D. Wichs. Spooky encryption and its applications. LNCS.
Springer, August 2016.
DI14. E. Druk and Y. Ishai. Linear-time encodable codes meeting the gilbert-varshamov bound and their
cryptographic applications. In _ITCS 2014_ . ACM, 2014.
DKK18. I. Dinur, N. Keller, and O. Klein. An optimal distributed discrete log protocol with applications to
homomorphic secret sharing. In _CRYPTO_, 2018.
DKS [+] 17. G. Dessouky, F. Koushanfar, A.-R. Sadeghi, T. Schneider, S. Zeitouni, and M. Zohner. Pushing the
communication barrier in secure computation using lookup tables. In _NDSS 2017_, 2017.
DNNR17. I. Damgård, J. B. Nielsen, M. Nielsen, and S. Ranellucci. The TinyTable protocol for 2-party secure
computation, or: Gate-scrambling revisited. LNCS. Springer, 2017.
DPSZ12. I. Damgård, V. Pastro, N. P. Smart, and S. Zakarias. Multiparty computation from somewhat
homomorphic encryption. In _CRYPTO 2012_, LNCS. Springer, August 2012.


39


DRRT18. D. Demmler, P. Rindal, M. Rosulek, and N. Trieu. PIR-PSI: Scaling private contact discovery. In
_PETS ’18_, 2018.
Ds17. J. Doerner and a. shelat. Scaling ORAM for secure computation. In _ACM CCS 17_ . ACM Press,
2017.
DyY07. J. Ding and B. yin Yang. Multivariates polynomials for hashing. Cryptology ePrint Archive, Report
2007/137, 2007. `[http://eprint.iacr.org/2007/137](http://eprint.iacr.org/2007/137)` .
FH96. M. K. Franklin and S. Haber. Joint encryption and message-efficient secure computation. _J. Cryp-_
_tology_, 9(4):217–232, 1996.
FIPR05. M. J. Freedman, Y. Ishai, B. Pinkas, and O. Reingold. Keyword search and oblivious pseudorandom
functions. In _TCC 2005_, LNCS. Springer, February 2005.
Fis74. P. C. Fischer. Further schemes for combining matrix algorithms. In _International Colloquium on_
_Automata, Languages, and Programming_, pages 428–436. Springer, 1974.
Fre10. D. M. Freeman. Converting pairing-based cryptosystems from composite-order groups to prime-order
groups. In _EUROCRYPT 2010_, LNCS. Springer, May 2010.
Frö85. R. Fröberg. An inequality for hilbert series of graded algebras. _Mathematica Scandinavica_, 56(2):117–
144, 1985.
Gal62. R. Gallager. Low-density parity-check codes. _IRE Transactions on information theory_, 8(1):21–28,
1962.
GGM86. O. Goldreich, S. Goldwasser, and S. Micali. How to construct random functions. _Journal of the ACM_,
(4), October 1986.
GI99. N. Gilboa and Y. Ishai. Compressing cryptographic resources. In _CRYPTO’99_, LNCS. Springer,
August 1999.
GI14. N. Gilboa and Y. Ishai. Distributed point functions and their applications. In _EUROCRYPT 2014_,
LNCS. Springer, 2014.
GIK [+] 15. S. Garg, Y. Ishai, E. Kushilevitz, R. Ostrovsky, and A. Sahai. Cryptography with one-way communication. In _CRYPTO 2015, Part II_, LNCS. Springer, August 2015.
GKWY19. C. Guo, J. Katz, X. Wang, and Y. Yu. Efficient and secure multiparty computation from fixed-key
block ciphers. Cryptology ePrint Archive, Report 2019/074, 2019. `[https://eprint.iacr.org/2019/](https://eprint.iacr.org/2019/074)`
`[074](https://eprint.iacr.org/2019/074)` .
GMW87. O. Goldreich, S. Micali, and A. Wigderson. How to play any mental game or A completeness theorem
for protocols with honest majority. In _19th ACM STOC_ . ACM Press, May 1987.
GNN17. S. Ghosh, J. B. Nielsen, and T. Nilges. Maliciously secure oblivious linear function evaluation with
constant overhead. LNCS. Springer, December 2017.
Gol00. O. Goldreich. Candidate one-way functions based on expander graphs. Cryptology ePrint Archive,
Report 2000/063, 2000. `[http://eprint.iacr.org/2000/063](http://eprint.iacr.org/2000/063)` .
HIJ [+] 16. S. Halevi, Y. Ishai, A. Jain, E. Kushilevitz, and T. Rabin. Secure multiparty computation with
general interaction patterns. ACM, 2016.
HKL [+] 12. S. Heyse, E. Kiltz, V. Lyubashevsky, C. Paar, and K. Pietrzak. Lapin: An efficient authentication
protocol based on ring-LPN. In _FSE 2012_, pages 346–365, 2012.
HLR07. C.-Y. Hsiao, C.-J. Lu, and L. Reyzin. Conditional computational entropy, or toward separating
pseudoentropy from compressibility. In _EUROCRYPT 2007_, LNCS. Springer, May 2007.
HOSS18. C. Hazay, E. Orsini, P. Scholl, and E. Soria-Vazquez. TinyKeys: A new approach to efficient multiparty computation. LNCS. Springer, 2018.
HS14. S. Halevi and V. Shoup. Algorithms in HElib. In _CRYPTO 2014, Part I_, LNCS. Springer, August
2014.
HS18. S. Halevi and V. Shoup. Faster homomorphic linear transformations in HElib. LNCS. Springer, 2018.
HW15. P. Hubacek and D. Wichs. On the communication complexity of secure function evaluation with long
output. In _ITCS 2015_ . ACM, 2015.
IKM [+] 13. Y. Ishai, E. Kushilevitz, S. Meldgaard, C. Orlandi, and A. Paskin-Cherniavsky. On the power of
correlated randomness in secure computation. In _TCC 2013_, LNCS. Springer, March 2013.
IKNP03. Y. Ishai, J. Kilian, K. Nissim, and E. Petrank. Extending oblivious transfers efficiently. In
_CRYPTO 2003_, LNCS. Springer, August 2003.
IKOS04. Y. Ishai, E. Kushilevitz, R. Ostrovsky, and A. Sahai. Batch codes and their applications. In _36th_
_ACM STOC_ . ACM Press, June 2004.
IKOS07. Y. Ishai, E. Kushilevitz, R. Ostrovsky, and A. Sahai. Zero-knowledge from secure multiparty computation. In _39th ACM STOC_ . ACM Press, June 2007.
IKOS08. Y. Ishai, E. Kushilevitz, R. Ostrovsky, and A. Sahai. Cryptography with constant computational
overhead. In _40th ACM STOC_ . ACM Press, May 2008.
IPS08. Y. Ishai, M. Prabhakaran, and A. Sahai. Founding cryptography on oblivious transfer - efficiently. In
_Advances in Cryptology - CRYPTO 2008, 28th Annual International Cryptology Conference, Santa_
_Barbara, CA, USA, August 17-21, 2008. Proceedings_, pages 572–591, 2008.
IPS09. Y. Ishai, M. Prabhakaran, and A. Sahai. Secure arithmetic computation with no honest majority. In
_TCC 2009_, LNCS. Springer, March 2009.


40


Kap04. I. Kaporin. The aggregation and cancellation techniques as a practical tool for faster matrix multiplication. _Theoretical Computer Science_, 315(2-3):469–510, 2004.
Kil88. J. Kilian. Founding cryptography on oblivious transfer. In _Proceedings of the 20th Annual ACM_
_Symposium on Theory of Computing, May 2-4, 1988, Chicago, Illinois, USA_, pages 20–31, 1988.
KK13. V. Kolesnikov and R. Kumaresan. Improved OT extension for transferring short secrets. In
_CRYPTO 2013, Part II_, LNCS. Springer, August 2013.
KKRT16. V. Kolesnikov, R. Kumaresan, M. Rosulek, and N. Trieu. Efficient batched oblivious PRF with
applications to private set intersection. In _ACM CCS 16_ . ACM Press, 2016.
KMO90. J. Kilian, S. Micali, and R. Ostrovsky. Minimum resource zero-knowledge proofs (extended abstract).
In _CRYPTO’89_, LNCS. Springer, August 1990.
KOR [+] 17. M. Keller, E. Orsini, D. Rotaru, P. Scholl, E. Soria-Vazquez, and S. Vivek. Faster secure multi-party
computation of AES and DES using lookup tables. In _ACNS 17_, LNCS. Springer, 2017.
KPR18. M. Keller, V. Pastro, and D. Rotaru. Overdrive: Making SPDZ great again. LNCS. Springer, 2018.
KRRW18. J. Katz, S. Ranellucci, M. Rosulek, and X. Wang. Optimizing authenticated garbling for faster secure
two-party computation. In _Advances in Cryptology - CRYPTO 2018 - 38th Annual International_
_Cryptology Conference, Santa Barbara, CA, USA, August 19-23, 2018, Proceedings, Part III_, pages
365–391, 2018.
KS12. K. Kobayashi and T. Shibuya. Generalization of lu’s linear time encoding algorithm for ldpc codes.
In _Information Theory and its Applications (ISITA), 2012 International Symposium on_, pages 16–20.
IEEE, 2012.
LG12. F. Le Gall. Faster algorithms for rectangular matrix multiplication. In _Foundations of Computer_
_Science (FOCS), 2012 IEEE 53rd Annual Symposium on_, pages 514–523. IEEE, 2012.
LJKS [+] 16. C. Löndahl, T. Johansson, M. Koochak Shooshtari, M. Ahmadian-Attari, and M. R. Aref. Squaring
attacks on mceliece public-key cryptosystems using quasi-cyclic codes of even dimension. _Des. Codes_
_Cryptography_, 80(2):359–377, August 2016.
LLY08. F.-H. Liu, C.-J. Lu, and B.-Y. Yang. Secure PRNGs from specialized polynomial maps over any.
2008.
LM10. J. Lu and J. M. Moura. Linear time encoding of ldpc codes. _IEEE Transactions on Information_
_Theory_, 56(1):233–249, 2010.
LPR10. V. Lyubashevsky, C. Peikert, and O. Regev. On ideal lattices and learning with errors over rings. In
_EUROCRYPT 2010_, LNCS. Springer, May 2010.
MBD [+] 18. C. A. Melchor, O. Blazy, J. Deneuville, P. Gaborit, and G. Zémor. Efficient encryption from random
quasi-cyclic codes. _IEEE Trans. Information Theory_, 64(5):3927–3943, 2018.
MI88. T. Matsumoto and H. Imai. Public quadratic polynominal-tuples for efficient signature-verification
and message-encryption. In _EUROCRYPT’88_, LNCS. Springer, May 1988.
MN96. D. J. MacKay and R. M. Neal. Near shannon limit performance of low density parity check codes.
_Electronics letters_, 32(18):1645, 1996.
MST03. E. Mossel, A. Shpilka, and L. Trevisan. On e-biased generators in NC0. In _44th FOCS_ . IEEE
Computer Society Press, October 2003.
MTSB12. R. Misoczki, J.-P. Tillich, N. Sendrier, and P. S. L. M. Barreto. MDPC-McEliece: New McEliece
variants from moderate density parity-check codes. Cryptology ePrint Archive, Report 2012/409,
2012. `[http://eprint.iacr.org/2012/409](http://eprint.iacr.org/2012/409)` .
NNOB12. J. B. Nielsen, P. S. Nordholt, C. Orlandi, and S. S. Burra. A new approach to practical active-secure
two-party computation. In _CRYPTO 2012_, LNCS. Springer, August 2012.
NP01. M. Naor and B. Pinkas. Efficient oblivious transfer protocols. In _12th SODA_ . ACM-SIAM, January
2001.
NP06. M. Naor and B. Pinkas. Oblivious polynomial evaluation. _SIAM J. Comput._, 35(5):1254–1281, 2006.
Pan18. V. Y. Pan. Fast feasible and unfeasible matrix multiplication. _arXiv preprint arXiv:1804.04102_, 2018.
Pra62. E. Prange. The use of information sets in decoding cyclic codes. _IRE Transactions on Information_
_Theory_, 8(5):5–9, 1962.
PsV06. R. Pass, a. shelat, and V. Vaikuntanathan. Construction of a non-malleable encryption scheme from
any semantically secure one. In _CRYPTO 2006_, LNCS. Springer, August 2006.
PVW08. C. Peikert, V. Vaikuntanathan, and B. Waters. A framework for efficient and composable oblivious
transfer. In _CRYPTO 2008_, LNCS. Springer, August 2008.
Sch18. P. Scholl. Extending oblivious transfer with low communication via key-homomorphic PRFs. LNCS.
Springer, 2018.
Spi96. D. A. Spielman. Linear-time encodable and decodable error-correcting codes. _IEEE Transactions on_
_Information Theory_, 42(6):1723–1731, 1996.
Str69. V. Strassen. Gaussian elimination is not optimal. _Numerische mathematik_, 13(4):354–356, 1969.
SV14. N. P. Smart and F. Vercauteren. Fully homomorphic simd operations. _Des. Codes Cryptography_,
71(1):57–81, April 2014.
TS16. R. C. Torres and N. Sendrier. Analysis of information set decoding for a sub-linear error weight. In
_International Workshop on Post-Quantum Cryptography_, pages 144–161. Springer, 2016.


41


Wol05. C. Wolf. Multivariate quadratic polynomials in public key cryptography. Cryptology ePrint Archive,
Report 2005/393, 2005. `[http://eprint.iacr.org/2005/393](http://eprint.iacr.org/2005/393)` .
WRK17a. X. Wang, S. Ranellucci, and J. Katz. Authenticated garbling and efficient maliciously secure twoparty computation. In _ACM CCS 17_ . ACM Press, 2017.
WRK17b. X. Wang, S. Ranellucci, and J. Katz. Global-scale secure multiparty computation. In _ACM CCS 17_ .
ACM Press, 2017.
Yao82. A. C.-C. Yao. Theory and applications of trapdoor functions (extended abstract). In _23rd FOCS_ .
IEEE Computer Society Press, November 1982.
Zic17. L. Zichron. Locally computable arithmetic pseudorandom generators. Master’s thesis, School of
Electrical Engineering, Tel Aviv University, 2017.


42


# **Appendix**

**A** **Details on Silent OT Extension**


**A.1** **Application to Reusable NIZK From LPN**


We sketch in this section an application of the silent OT extension from subfield vector-OLE
given in Section 5 to non-interactive zero-knowledge proofs in the preprocessing model. NIZK
in the preprocessing model relaxes the standard NIZK definition by allowing the prover and
the verifier to interact during a preprocessing phase, to generate respective proving key and
verification key. It is well known that preprocessing NIZKs can be constructed from any oblivious transfer [KMO90, PsV06, IKOS07, GIK [+] 15]; in fact, these works even imply the existence
of _information-theoretic_ preprocessing NIZKs in the OT-hybrid model. However, in all these
protocols, the computation and communication of the preprocessing grow with the size (and
the number) of the theorems to be proven; in other words, the preprocessing implies an a-priori
bound on the size and number of statements to be proven later.


**A.1.1** **Reusable Preprocessing NIZK from Silent OT**


Plugging our random OT PCG given in Section 5 into the construction of preprocessing NIZK
from OT, we readily obtain an improved preprocessing NIZK: following a one-time preprocessing phase whose communication and computation grow only with the _soundness parameter_ [14]

of the proofs to be sent in the online phase. After this preprocessing phase, the prover and
the verifier can locally, without further interaction, extend the preprocessed material into an
arbitrary polynomial number of (pseudo)random OTs, leading to a preprocessing NIZK with
preprocessing cost _independent_ of the size and number of theorems to be proven. In other word,
the same preprocessing material can be reused for an a-priori arbitrary number of proofs. (Adaptive, multi-theorem) zero-knowledge and (adaptive, reusable) soundness readily follow from the
security properties of the silent OT extension, and soundness holds even if the prover is allowed
to get the answer of the verifier for an arbitrary polynomial number of proofs before trying to
prove a false statement.
Using our construction of silent OT extension from LPN and correlation-robust assumption,
this readily implies the existence of a reusable preprocessing NIZK from the same assumptions.
Compared to the recent reusable preprocessing NIZK of [BCGI18], our preprocessing NIZK has
two advantages:


**–** It only requires the standard LPN assumption over F2 (together with correlation-robust hash
functions), while the NIZK of [BCGI18] must rely on a generalization of LPN to exponentially
large fields;

**–** The preprocessing phase is independent of both the number of theorems to be proven, and
the size of these theorems. In comparison the preprocessing phase in [BCGI18] is independent
of the number of theorems to be proven, but grows linearly with a bound on the size of each
statement.


**A.1.2** **Removing the Correlation-Robust Hash Functions**


Our silent OT extension of Section 5 relies on a correlation-robust hash function. Intuitively, this
comes from the use of the classical IKNP strategy for OT extension [IKNP03]: to generate _m_
random OTs of strings of length _ℓ_, the sender and the receiver exchange their roles and perform


14 We say that a NIZK has soundness parameter _t_ if the probability for the prover to cause the verifier to accept
a proof for an invalid statement is at most 2 _[−][k]_ .


_λ_ executions of a length- _m_ OT protocol ( _λ_ is a security parameter): that is, the receiver with
selection bits _**b**_ = ( _bi_ ) _i≤m_ plays the role of the sender with inputs ( _**x**_ _[j]_ _,_ _**x**_ _[j]_ + _**b**_ ) _j≤λ_, where _**x**_ _[j]_

is a random string of length _m_, and the sender plays the role of the receiver with a random
selection vector _**s**_ of length _λ_ . This allows the sender to reconstruct _**k**_ _i_ = _**x**_ _i_ + _bi_ _**s**_, where
_**x**_ _i_ is the length- _λ_ vector of the _i_ -th coordinates of the vectors _**x**_ _[j]_ . Then, to execute an OT
protocol with length _ℓ_ -inputs ( _s_ [0] _i_ _[, s]_ _i_ [1][)][ from the sender and] _[ b][i]_ [ from the verifier, the sender sends]
( _zi_ [0] _[, z]_ _i_ [1][) = (] _[s]_ _i_ [0] _[⊕]_ _[H]_ [(] _**[k]**_ _[i]_ [)] _[, s]_ _i_ [1] _[⊕]_ _[H]_ [(] _**[k]**_ _[i][ −]_ _**[s]**_ [))][. Note that the verifier knows] _**[ x]**_ _[i]_ [ =] _**[ k]**_ _[i][ −]_ _[b][i]_ _**[s]**_ [, hence he]
can reconstruct _s_ _[b]_ _i_ _[i]_ [=] _[ z]_ _i_ _[b][i]_ _[⊕]_ _[H]_ [(] _**[x]**_ _[i]_ [)][; sender security follows from the correlation-robustness of the]
hash function.
In [AHI11], it was observed that a similar construction can be obtained by replacing the
correlation-robust hash function by an encryption scheme semantically secure against related-key
attack for the class of linear functions under general group. An RKA-secure scheme maintains it’s
semantic security even if the keys satisfy a known (in fact, adaptively chosen by the adversary)
relation. In the above construction, the sender can send ( _zi_ [0] _[, z]_ _i_ [1][) = (][Enc][(] _[s]_ _i_ [0] _[,]_ _**[ k]**_ _[i]_ [)] _[,]_ [ Enc][(] _[s]_ _i_ [1] _[,]_ _**[ k]**_ _[i][ −]_ _**[s]**_ [))][,]
where Enc is semantically secure against RKA attacks for linear functions: the sender security
reduces to the hardness of distinguishing Enc( _si_ [1] _[−][b][i]_ _,_ _**k**_ _i −_ (1 _−_ _bi_ ) _**s**_ ) = Enc( _s_ [1] _i_ _[−][b][i]_ _,_ _**x**_ _i_ + ( _−_ 1) _[b][i]_ _**s**_ )
from Enc(0 _[ℓ]_ _,_ _**x**_ _i_ + ( _−_ 1) _[b][i]_ _**s**_ ), even given the keys _**x**_ _i_ for each _i_, which follows from the semantic
security of Enc against RKA attacks. Furthermore, [AHI11] provides in particular a construction
of an encryption scheme semantically secure against RKA-attacks for linear functions, from the
standard LPN assumption over F2. Plugging their scheme as a replacement for the correlationrobust hash function in our construction of preprocessing NIZK from silent OT, we obtain a
reusable preprocessing NIZK _solely_ under the standard LPN assumption.


**Theorem 42.** _Under the standard LPN assumption over_ F2 _, with dimension n, number of sam-_
_ples_ poly( _n_ ) _, and slightly sub-constant noise rate_ 1 _/ω_ ( _λ_ log _n_ ) _, there exists a reusable prepro-_
_cessing NIZK proof system for NP which satisfies adaptive multi-theorem zero-knowledge and_
_adaptive reusable soundness, where the communication and the computation of the preprocessing_
_phase depend solely on the soundness error of the proof system, but are independent of the size_
_and number of statements to be proven._


We note that the flavor of LPN used in our construction is a “minicrypt-style” assumption: it
belongs to a parameter regime which is not known to imply the existence of public key encryption
(which is only known from LPN with smaller noise rate _O_ (1 _/_ _[√]_ ~~_n_~~ ~~)~~ ). Furthermore, the exact flavor
of LPN that we need is in fact slightly weaker than the one given in the theorem above. Our
NIZK can be based on the assumption that the following two variants of LPN are secure:


**–** LPN over F2 with dimension _n_, _very small number of samples n_ + _o_ ( _n_ ), and slightly subconstant noise rate 1 _/ω_ ( _λ_ log _n_ ) (this assumption underlies our silent OT extension), and

**–** LPN over F2 with dimension _n_, polynomial number of samples poly( _n_ ), and _constant noise_
_rate O_ (1) (this assumption underlies the RKA-secure symmetric-key encryption scheme
of [AHI11]).


**A.1.3** **Replacing 1-out-of-2 OT with Rabin OT**


While the construction described above relies on 1-out-of-2 oblivious transfer, it is also possible
to build preprocessing NIZKs directly from the original Rabin OT primitive (where the sender
has a single input, and the receiver learns it with probability 1 _/_ 2) [GIK [+] 15]. We note that our
silent OT extension can also be used to generate Rabin-type OT correlations, with a factor 2 of
savings compared to the 1-out-of-2 silent OT extension protocol.


**A.2** **Efficiency Analysis**


To improve the efficiency, we modify the construction to use the _regular_ version of the syndrome
decoding (or dual-LPN) problem, where the error vector _**e**_ is divided into _t_ equally-spaced blocks,


44


each of weight one. This means the MPFSS scheme can be built by concatenating _t_ DPFs of size
_n_ _[′]_ _/t_, instead of XORing _t_ DPFs of size _n_ _[′]_ .
In Tables 3 and 4, we present the communication complexity and estimated runtimes of our
Silent OT extension protocol for various choices of parameters. We chose our parameters as
in [BCGI18], so that the best known attacks against the regular syndrome decoding problem
cost at least 2 [80] operations. We always use _n_ _[′]_ = 4 _n_, and values of the noise-weight _t_ as shown
in the table. We estimated runtimes based on the costs of the main operations in the Doernershelat [Ds17] protocol for running a distributed DPF setup with semi-honest security, and our
own estimates for the cost of matrix multiplication. These are based on a single core of an i7-7600
CPU @2.8GHz with SSE and AES-NI instructions.


_Communication complexity._ When using the DPF setup protocol of [Ds17], for a single DPF
of size _N_ we need log _N_ OTs [15] on _λ_ -bit strings, except the last OT which has length 2 _λ_ .
With the regular LPN variant, we use _t_ DPFs of size _N_ = _n_ _[′]_ _/t_, with _n_ _[′]_ = 4 _n_ . Using OT
extension, an OT on _ℓ_ -bit strings requires _λ_ +2 _ℓ_ bits of communication [ALSZ13], giving a total
of _t_ (log( _n_ _[′]_ _/t_ ) + 1)(2 _λ_ + 1) bits of communication for these. The base OTs for OT extension can
be implemented with the Naor-Pinkas protocol [NP01] based on DDH over a 256-bit elliptic
curve group, at a cost of sending 1024 bits per OT.
This gives rough overall costs as follows, shown in detail in Table 3.
(log( _N_ ) _−_ 1) _·_ 3 _λ_ + 5 _λ_ = 3 _λ ·_ log( _N_ ) + 2 _λ_


**–** _Seed size: ≈_ _t ·_ ( _λ ·_ log( _n_ _[′]_ _/t_ ) + 2 _λ_ ) bits

**–** _Base OTs (one-time cost):_ 1024 _· λ_ bits

**–** _Distributed setup: ≈_ 2 _· λ · t ·_ (log( _n_ _[′]_ _/t_ ) + 1) bits


_Encoding method._ It seems likely that when _n_ is large the dominating cost is the F _[n]_ 2 _[λ][′]_ _[ ×]_ [ F] 2 _[n][′][×][n]_
matrix multiplication. We consider two different encoding methods, both suggested in [BCGI18].


**–** _Quasi-cyclic codes. H_ is the parity-check matrix of a random quasi-cyclic code. Multiplication by _H_ can be computed as a length _n_ _[′]_ _/n_ inner product over Z2[ _X_ ] _/_ ( _X_ _[n]_ _−_ 1), for which
we estimate costs using a state-of-the-art implementation of fast binary polynomial multiplication [CCK [+] 18]. Security reduces to the quasi-cyclic syndrome decoding problem; note that
this requires _n_ to be prime to avoid attacks expoiting the quasi-cyclic structure [LJKS [+] 16].

**–** _LDPC codes. H_ is the _transpose_ of the generator matrix for an LDPC (low-density parity
check) code, which is defined by a random parity check matrix with constant sparsity _d_ . This
implies that we need LPN to be hard for _d_ -local codes, which is the same assumption that
was conjectured in [Ale03]. We use _d_ = 10, as suggested in [ADI [+] 17]. Multiplication by _H_
is essentially the transpose of an LDPC encoding, which can be done in _O_ ( _n_ ) operations by
“transposing” a linear-time LDPC encoding algorithm.


We have not implemented the LDPC encoding algorithm, but instead tested a dummy algorithm which performs the same operation count, with a worst-case access pattern where each
operation reads from a random component of the input. As can be seen in Table 4, this becomes
much slower beyond inputs of size 2 [20] bits, which no longer fit in the L1 cache (128KiB). However,
we expect that carefully implementing the algorithm could lead to performance improvements.


_Other costs._ The other costs involved are a DPF full-domain evaluation, and the cost of distributed setup for the DPFs. We ignore the cost of the OTs in the DPF setup procedure, since for
our parameters we always need under 1000 OTs, which take under 1ms using modern OT extension implementations. To simplify estimates, we therefore assume the DPF cost in setup is the
same as one full-domain evaluation, and estimate this using the implementation from [DRRT18],


15 In [Ds17], 2 log _N_ OTs are needed, but in our case all the OTs in one direction can be avoided, since one party
knows the secret point.


45


which reports a throughput of 2.6 billion bits/s for full-domain evaluation. Since our DPFs output 128 bits instead of one, we scale this down to get around 20 million evaluations per second.


_n_ 2 [12] 2 [14] 2 [16] 2 [18] 2 [20] 2 [22] 2 [24]


_t_ 39 34 32 31 30 29 28
Seed size (kB) 5.65 6.02 6.69 7.97 8.67 9.31 9.89
Comp. ratio 11.6 43.6 157 526 1930 7210 27150
Base OT comms. (kB) 16.38 16.38 16.38 16.38 16.38 16.38 16.38
Setup comms. (kB) 18.10 19.04 20.99 24.80 26.88 28.77 30.46
Bits per OT (exc. base) 35.34 9.30 2.56 0.76 0.21 0.05 0.01


**Table 3.** Communication complexity of silent OT for various parameter sets, all with _n_ _[′]_ = 4 _n_ . Compression ratio
is _λn_ divided by the seed size in bits, with _λ_ = 128.


_n_ 2 [12] 2 [14] 2 [16] 2 [18] 2 [20] 2 [22] 2 [24]


Quasi-cyclic 11.3 12.8 53.8 238 1113 5212 21090
LDPC transpose 0.3 1.18 9.9 74.3 646 4460 47960
MPFSS full eval 0.8 3.2 12.9 51.6 207 826 3300


Total time (quasi-cyclic) 12.9 19.2 79.6 341 1527 6864 27690
Total time (LDPC) 1.9 7.58 35.7 178 1060 6112 54560


Throughput, QC (million/s) 0.32 0.85 0.82 0.77 0.69 0.61 0.60
Throughput, LDPC (million/s) 2.16 2.16 1.84 1.47 0.99 0.69 0.31


**Table 4.** Estimated runtimes (ms) and throughput for _n_ silent OTs. Based on (total time) _≈_ 2 _×_ (MPFSS full
eval) + (encoding time)


**B** **One-Time Truth Table Generator**


We define the authenticated, masked truth table correlation, _C_ TT for a lookup table _T_ : [ _n_ ] _→_
$ $
_{_ 0 _,_ 1 _}_ _[m]_ as follows. _C_ TT first samples MAC key shares _α_ 0 _, α_ 1 _←_ F2 _λ_ and a mask _s_ _←_ [ _n_ ], then
computes _α_ = _α_ 0 + _α_ 1, _yi_ = _T_ ( _s_ + _i_ mod _n_ ) and _γi_ = _yi · α_ in F2 _λ_, for _i ∈_ [ _n_ ], viewing the
outputs of _T_ as elements of the field. It outputs



( _R_ 0 _, R_ 1) = �( _ασ, {yi_ _[σ][, γ]_ _i_ _[σ][}]_ _i∈_ [ _n_ ] [)] 


_σ∈{_ 0 _,_ 1 _}_



where _yi_ _[σ]_ _[∈{]_ [0] _[,]_ [ 1] _[}][m][, γ]_ _i_ _[σ]_ _[∈]_ [F] 2 _[λ]_ [ are sampled at random such that] _[ y]_ _i_ [0] [+] _[ y]_ _i_ [1] [=] _[ y][i]_ [ and] _[ γ]_ _i_ [0] [+] _[ γ]_ _i_ [1] [=] _[ γ][i]_ [.]
Our starting point is the observation from [KOR [+] 17] that this correlation can be generated
locally, given secret-shares of a random unit vector. This is because, if _s ∈_ [ _n_ ] is the random
mask, and _**e**_ _s ∈{_ 0 _,_ 1 _}_ _[n]_ is the _s_ -th unit vector, then we have



_T_ ( _i_ + _s_ mod _n_ ) =



_n_


_**e**_ _s_ [ _j_ ] _· T_ ( _i_ + _j_ mod _n_ )

_j_ =1



and this can be computed locally given additive shares of _**e**_ _s_, since _T_ is public.
Given a DPF for the function with domain [ _n_ ] that maps _s_ to 1 and is zero elsewhere, two
parties can compute shares of _**e**_ _s_ by simply evaluating the DPF on every input in [ _n_ ]. This
already allows us to compress a simple, semi-honest version of _C_ TT without MACs. We can
extend this to also create the secret-shared MACs _at no extra cost_, just by choosing the DPF to


46


map _s_ to (1 _∥α_ ), where _α_ is a random MAC key. We remark that, as described in Section 2, this
can be seen as an instance of the DPF-based HSS scheme that is implicit in our subfield-VOLE
PCG.
The complete construction is given in Fig. 6. Instantiating DPF with [BGI16b], the total
PCG seed size is log _n ·_ ( _λ_ + 2) + 3 _λ_ + 1 bits, and note that this is independent of the precise
lookup table, or even the length of its values. Compared with the cost of naively storing a 1-bit
output one-time truth table with MACs of _n_ _·_ ( _λ_ +1)+ _λ_ bits from [DNNR17], we obtain storage
savings of over 20x for a length-256 table (as in the AES S-box), and this increases to almost 80x
for a table of size 1024. The computational cost of expanding the entire correlation is _n_ calls to
DPF _._ FullEval, however, when using this for 2-PC only a single entry of the table is needed, and
this can be computed on-the-fly with just 1 call to FullEval, for a cost of _O_ ( _n_ ) PRG evaluations.


**Construction** _G_ TT


Parameters: A lookup table _T_ : [ _n_ ] _→_ _{_ 0 _,_ 1 _}_ _[m]_, and a distributed point function
DPF = (DPF _._ Gen _,_ DPF _._ FullEval).


**Gen:** On input 1 _[λ]_ :


1. Pick a random index _s_ _←{_ $ 1 _, . . ., n}_ .

$
2. Sample _α_ 0 _, α_ 1 _←_ F2 _λ_ and let _α_ = _α_ 0 _⊕_ _α_ 1.
3. Compute ( _K_ 0 [fss] _[, K]_ 1 [fss][)] _←_ $ DPF _._ Gen(1 _λ, fs,_ 1 _∥α_ ).
4. Let k0 _←_ ( _K_ 0 [fss] _[, α]_ 0 [)][ and][ k] 1 _[←]_ [(] _[K]_ 1 [fss] _[, α]_ 1 [)][.]
5. Output (k0 _,_ k1).


**Expand:** On input ( _σ,_ k _σ_ ):


1. Parse k _σ_ as ( _Kσ_ [fss] _[, α]_ _σ_ [)][.]
2. Compute _**v**_ _[σ]_ _←_ DPF _._ FullEval( _σ, Kσ_ [fss][)][ in] _[ {]_ [0] _[,]_ [ 1] _[}][n][·]_ [(] _[λ]_ [+1)][.]
3. For each _i ∈_ [ _n_ ], write _vi_ _[σ]_ [= (] _[b]_ _i_ _[σ][∥][c]_ _i_ _[σ]_ [)] _[ ∈{]_ [0] _[,]_ [ 1] _[} ×]_ [ F] 2 _[λ]_ [. Compute, for] _[ j][ ∈]_ [[] _[n]_ []][:]



_n_

- _c_ _[σ]_ _i_ _[·][ T]_ [(] _[i]_ [ +] _[ j]_ [ mod] _[ n]_ [)] _[ ∈]_ [F] 2 _[λ]_


_i_ =1



_yj_ _[σ]_ [=]



_n_

- _b_ _[σ]_ _i_ _[·][ T]_ [(] _[i]_ [ +] _[ j]_ [ mod] _[ n]_ [)] _[ ∈{]_ [0] _[,]_ [ 1] _[}][m][,]_ _γj_ _[σ]_ [=]


_i_ =1



and output ( _ασ, {yj_ _[σ][, γ]_ _j_ _[σ][}]_ _j_ _[n]_ =1 [)][.]


**Fig. 6.** PCG for authenticated, one-time truth table correlations


The following theorem can be proven with a reduction to MPFSS, similarly to (and simpler
than) the proof of Theorem 24 for the subfield-VOLE generator.


**Theorem 43.** _Let_ DPF _be a secure distributed point function. Then construction G_ TT _in Fig. 6_
_is a secure PCG for the correlation G_ TT _._


**B.1** **Application to Sublinear-Communication MPC in the Preprocessing Model**


Secure computation in the correlated randomness model typically requires communicating _O_ ( _s_ )
values in the online phase, where _s_ is the circuit size. In a recent paper, Couteau [Cou19] showed
that this is not inherent: given access to a trusted source of (polynomially many) large one-time
truth tables correlations, _N_ parties can securely evaluate arbitrary _layered_ (boolean or arithmetic) circuits (whose nodes can be partitioned into layers such that any edge connects adjacent
layers – such circuits capture a variety of circuits that arise in practice) with informationtheoretic security and _sublinear_ communication _O_ ( _s/_ log log _s_ ). A downside of this protocol,
that strongly limits its partical implications, is that it requires a large amount of preprocessing
material: to securely evaluate the circuit in the online phase, the parties need to generate and
store _O_ ( _s_ [2] log log _s_ ) bits of preprocessed material (i.e., _O_ ( _s/_ log log _s_ ) one-time truth tables of


47


size _O_ ( _s_ ) each). Using our PCG for truth table correlations, this can be compressed to a quasilinear amount _O_ ( _λs_ log _s/_ log log _s_ ) of preprocessing material, assuming only one-way functions.
The preprocessing material can then be _locally_ expanded by the parties, without any interaction,
into _O_ ( _s_ [2] log log _s_ ) bits of (pseudo)random one-time truth tables.


**C** **Group-Based PCG for Bilinear Correlations**


In this section, we exhibit a construction of PCG from the (external) DDH assumption over
pairing-friendly elliptic curves, for the class of (additive) bilinear correlations. This construction
builds upon the group-based HSS developed in [BGI16a, BGI17, BCG [+] 17]. Note that all these
constructions satisfy an imperfect correctness notion, where correctness is only guaranteed to
hold except with probability _δ_, and the evaluation algorithm is allowed to run in time polynomial
in 1 _/δ_ (it is called a “Las Vegas” HSS in [BGI16a, BGI17, BCG [+] 17]). Our construction of groupbased PCG will inherit this imperfect correctness. However, the parties can detect when a given
output has a high risk of being incorrect; knowing the location of the faulty outputs allows them
to use efficient techniques (such as punctured OT [BGI17] or leakage-absorbing pads [BCG [+] 17])
to securely delete them in a _sanitization phase_ . Hence, we denote PCG with imperfect correctness
and detectable failures _sanitizable pseudorandom correlation generators_ .
Our full construction is somewhat technical. Because of the inverse polynomial failure probability, our group-based PCG does not directly fit into the definition of PCG given in Section 4.
To simplify the presentation, we therefore first introduce the notion of _sanitizable bilinear corre-_
_lation generators_, which are PCG for the class of bilinear correlations with an inverse polynomial
failure probability whose incorrect outputs can be _detected_ efficiently. Then, to proceed with the
construction, we introduce an intermediate notion: the notion of _compressible_ HSS. Informally,
a compressible HSS is an HSS schemes in which the encodings of the inputs can be compressed
to a small string when they come from an appropriate distribution. This captures the fact that
our construction will build upon the specific homomorphic properties of the group-based HSS
of [BGI16a, BGI17, BCG [+] 17] to show that the encodings of (pseudo)random inputs can be efficiently compressed. Then, we show that a compressible Las Vegas degree-2 HSS for bilinear
correlations can be used to construct a sanitizable bilinear correlation generator, assuming the
learning parity with noise (LPN) assumption. Afterward, we proceed with a description of a compressible Las Vegas degree-2 HSS for bilinear correlations, which builds upon the homomorphic
properties of the group-based Las Vegas HSS of [BGI16a, BGI17, BCG [+] 17] when instantiated
over a pairing-friendly elliptic curves, and upon the VOLE generator of [BCGI18]. Eventually,
we discuss optimizations of our construction.


_Notations._ For vectors _**x**_ _i_ over a multiplicative group, we denote by [�] _i_ _**[x]**_ _[i]_ [ their component-wise]
product. Given a multiplicative group G of order _q_, a length- _n_ vector _**g**_ = ( _g_ 1 _, · · ·, gn_ ) _∈_ G _[n]_,
and a length- _n_ vector of exponents _**x**_ = ( _x_ 1 _, · · ·, xn_ ) _∈_ Z _[n]_ _q_ [, we denote] _**[ x]**_ _[ •]_ _**[ g]**_ [ the “scalar product]
in the exponent”: _**x**_ _•_ _**g**_ = [�] _i_ _[n]_ =1 _[g]_ _i_ _[x][i]_ [; for any] _[ g][ ∈]_ [G][,] _[ g]_ _**[x]**_ [ denotes][ (] _[g][x]_ [1] _[,][ · · ·][, g][x][n]_ [)][.]


_A Note on Additive Bilinear Correlations._ The general notion of additive correlations which we
consider in this paper are those in which the parties receive shares of some input _**x**_, as well
as shares of _C_ ( _**x**_ ) for some correlation _C_ . However, when restricting our attention to bilinear
correlations, it is more convenient to consider that each party will know _in the clear_ one of two
inputs, _**x**_ and _**y**_, as well as shares of a bilinear function _B_ ( _**x**_ _,_ _**y**_ ). Indeed, letting the parties
know part of the output in the clear will allow for several non-trivial optimizations of the
construction. Furthermore, in the specific case of bilinear correlation, it turns out that this
is without loss of generality: the general case (where the inputs are shared as well) can be
obtained in a blackbox way using two parallel calls to the PCG for these restricted forms of
bilinear correlations. We demonstrate this with the construction below, where BCG _s_ denotes a


48


pseudorandom correlation generator for general bilinear correlations, and BCG denotes a PCG
for restricted bilinear correlations.


**–** BCG _s._ Setup(1 _[λ]_ ) outputs (pp _,_ sk) _←_ $ BCG _._ Setup(1 _λ_ );

**–** BCG _s._ Gen(sk _, B_ ) runs twice BCG _._ Gen(sk _, B_ ), and outputs ((k0 _,_ k _[′]_ 0 [)] _[,]_ [ (][k][1] _[,]_ [ k] _[′]_ 1 [))][;]

**–** BCG _s._ Expand(pp _, σ,_ (k _σ,_ k _[′]_ _σ_ [))][ runs twice][ BCG] _[.]_ [Expand][, and outputs] _**[ z]**_ _[σ]_ [= ((1] _[−][σ]_ [)] _**[x]**_ _[σ]_ [+] _[σ]_ _**[x]**_ _[′]_ _σ_ _[, σ]_ _**[x]**_ _[σ]_ [+]
(1 _−_ _σ_ ) _**x**_ _[′]_ _σ_ _[,]_ _**[ y]**_ _[σ]_ [+] _**[ y]**_ _[′]_ _σ_ [+] _[ B]_ [(] _**[x]**_ _[σ][,]_ _**[ x]**_ _σ_ _[′]_ [))][.]


Then, it holds that


_**z**_ 0 + _**z**_ 1 = ( _**x**_ 0 + _**x**_ _[′]_ 1 _[,]_ _**[ x]**_ 0 _[′]_ [+] _**[ x]**_ [1] _[, B]_ [(] _**[x]**_ [0] _[,]_ _**[ x]**_ **[1]** [) +] _[ B]_ [(] _**[x]**_ 0 _[′]_ _[,]_ _**[ x]**_ 1 _[′]_ [) +] _[ B]_ [(] _**[x]**_ [0] _[,]_ _**[ x]**_ 0 _[′]_ [) +] _[ B]_ [(] _**[x]**_ [1] _[,]_ _**[ x]**_ 1 _[′]_ [))]

= ( _**x**_ 0 + _**x**_ _[′]_ 1 _[,]_ _**[ x]**_ 0 _[′]_ [+] _**[ x]**_ [1] _[, B]_ [(] _**[x]**_ [0] [+] _**[ x]**_ _[′]_ 1 _[,]_ _**[ x]**_ 0 _[′]_ [+] _**[ x]**_ [1][))]

= ( _**x**_ _,_ _**x**_ _[′]_ _, B_ ( _**x**_ _,_ _**x**_ _[′]_ )) _,_ denoting _**x**_ = _**x**_ 0 + _**x**_ _[′]_ 1 _[,]_ _**[ x]**_ _[′]_ [ =] _**[ x]**_ 0 _[′]_ [+] _**[ x]**_ [1] _[.]_


**C.1** **Sanitizable Bilinear Correlation Generator**


Since our group-based construction will be inherently limited to generating _bilinear_ correlations,
with an inverse polynomial failure probability, we provide a self-contained formal definition of
_sanitizable bilinear correlation generators_ . A sanitizable BCG is a PCG for bilinear correlations,
where correctness holds except with some inverse polynomial probability. To capture the fact that
in our construction, a part of the seed generation can be reused accross several instantiations,
we add to the definition a Setup algorithm, which produces the reusable part of the seed (which
contains public and secret parameters).


**Definition 44 (Sanitizable Bilinear Correlation Generator).** _A (δ-failure) sanitizable bi-_
_linear correlation generator over a ring R is a triple of algorithms_ (BCG _._ Setup _,_ BCG _._ Gen _,_ BCG _._ Expand)
_with the following syntax:_


**–** BCG _._ Setup(1 _[λ]_ ) _is a PPT algorithm that given a security parameter λ, outputs public param-_
_eters_ pp _and a secret key_ sk _;_

**–** BCG _._ Gen(sk _, B_ ) _is a PPT algorithm that given secret key_ sk _and a bilinear map B_ : _R_ _[n]_ _×_
_R_ _[n]_ _�→R_ _[m]_ _, outputs a pair of seeds_ (k0 _,_ k1) _;_

**–** BCG _._ Expand(pp _, σ,_ k _σ, δ_ ) _is an algorithm running in time polynomial in λ and_ 1 _/δ that, given_
_party index σ ∈{_ 0 _,_ 1 _}, a seed_ k _σ, and a failure bound δ, outputs a pair of vectors_ ( _**x**_ _,_ _**y**_ ) _∈_
_R_ _[n]_ _× R_ _[m]_ _, as well as a list of m confidence flags γσ,i ∈{⊥, ⊤} for i_ = 1 _to m to indicate full_
_confidence (⊤) or a possibility of failure (⊥) for any given output._


_The algorithms_ (BCG _._ Setup _,_ BCG _._ Gen _,_ BCG _._ Expand) _should satisfy the following:_


**–** _δ_ **-Correctness.** _For every i ≤_ _m and every polynomial p, there is a negligible ν such that_
_for every positive integer λ, bilinear function B_ : _R_ _[n]_ _× R_ _[n]_ _�→R_ _[m]_ _, and failure bound δ >_ 0 _,_
_where |B|,_ 1 _/δ ≤_ _p_ ( _λ_ ) _, we have:_


Pr[( _γ_ 0 _,i_ = _⊥_ ) _∧_ ( _γ_ 1 _,i_ = _⊥_ )] _≤_ _δ_ + _ν_ ( _λ_ ) _,_


_and_
Pr[(( _γ_ 0 _,i_ = _⊤_ ) _∨_ ( _γ_ 1 _,i_ = _⊤_ )) _∧_ _y_ 0 _,i_ + _y_ 1 _,i ̸_ = _B_ ( _**x**_ 0 _,_ _**x**_ 1) _i_ ] _≤_ _ν_ ( _λ_ ) _,_


_where the probability is taken over_


(pp _,_ sk) _←_ $ BCG _._ Setup(1 _λ_ ) _,_ (k0 _,_ k1) _←_ $ BCG _._ Gen(sk _, B_ )


_and where we denote_ ( _**x**_ 0 _,_ _**y**_ 0) _←_ BCG _._ Expand(0 _,_ k0) _, and_ ( _**x**_ 1 _,_ _**y**_ 1) _←_ BCG _._ Expand(1 _,_ k1) _._


49


**– Security.** _For any σ ∈{_ 0 _,_ 1 _} and any (stateful, nonuniform) polynomial-time adversary A,_
_it holds that_










Pr


_≈_ Pr



(pp _,_ sk) _←_ $ BCG _._ Setup(1 _λ_ ) _, B ←A_ (pp) _,_

(k0 _,_ k1) _←_ $ BCG _._ Gen(sk _, B_ ) _,_ : _A_ ( _**x**_ _σ,_ k1 _−σ_ ) = 1
( _**xσ**_ _,_ _**yσ**_ _,_ _**γσ**_ ) _←_ BCG _._ Expand(pp _, σ,_ k _σ_ )







(pp _,_ sk) _←_ $ BCG _._ Setup(1 _λ_ ) _, B ←A_ (pp) _,_
(k0 _,_ k1) _←_ $ BCG _._ Gen(sk _, B_ ) _,_ : _A_ ( _**x**_ _σ,_ k1 _−σ_ ) = 1
_**xσ**_ _←R_ $ _n,_ _**γσ**_ _←_ $ Ber _δ_ ( _{⊥, ⊤}_ ) _m_











 _._



**C.2** **Las Vegas HSS**


We recall below the definition of _δ_ -failure HSS (with a Las Vegas correctness guarantee), adapted
from [BCG [+] 17].


**Definition 45 (Las Vegas Homomorphic Secret Sharing).** _A (2-party, secret-key, Las_
_Vegas δ-failure)_ Degree- _d_ Homomorphic Secret Sharing (HSS) _scheme over a ring_ ( _R,_ + _, ·_ ) _is a_
_triple of PPT algorithms_ HSS = (HSS _._ Gen _,_ HSS _._ Share _,_ HSS _._ Eval) _with the following syntax:_


**–** HSS _._ Gen(1 _[λ]_ ) _: On input a security parameter_ 1 _[λ]_ _, the key generation algorithm outputs a secret_
_key_ sk _and an evaluation key_ ek _._

**–** HSS _._ Share(sk _, x_ ) _: Given secret key_ sk _and secret input value x ∈R_ _[n]_ _, the sharing algorithm_
_outputs a pair of shares_ ( _s_ 0 _, s_ 1) _. We assume that the input length n is included in each of_
( _s_ 0 _, s_ 1) _._

**–** HSS _._ Eval( _σ,_ ek _, sb, P, δ_ ) _: On input party index σ ∈{_ 0 _,_ 1 _}, evaluation key_ ek _σ, share sσ of_
_a size-n input, degree-d arithmetic circuit P with n input bits and m output bits, and a_
_failure bound δ, the homomorphic evaluation algorithm outputs yb ∈R_ _[m]_ _, constituting party_
_b’s share over R of an output y ∈R_ _[m]_ _, as well as a confidence flag γb ∈{⊥, ⊤} to indicate_
_full confidence (⊤) or a possibility of failure (⊥)._


_The algorithms_ (HSS _._ Gen _,_ HSS _._ Share _,_ HSS _._ Eval) _should satisfy the following correctness and se-_
_curity requirements:_


**– Correctness:**
_For every polynomial p there is a negligible ν such that for every sufficiently large integer λ,_
_input_ _**x**_ _∈R_ _[n]_ _, degree-d arithmetic circuit P with input length n, and failure bound δ >_ 0 _,_
_where |P_ _|,_ 1 _/δ ≤_ _p_ ( _λ_ ) _, we have:_


Pr[( _γ_ 0 = _⊥_ ) _∧_ ( _γ_ 1 = _⊥_ )] _≤_ _δ_ + _ν_ ( _λ_ ) _,_


_and_
Pr[(( _γ_ 0 = _⊤_ ) _∨_ ( _γ_ 1 = _⊤_ )) _∧_ _**y**_ 0 + _**y**_ 1 _̸_ = _P_ ( _**x**_ )] _≤_ _ν_ ( _λ_ ) _,_


_where probability is taken over_


(sk _,_ ek) _←_ HSS _._ Gen(1 _[λ]_ ); ( _s_ 0 _, s_ 1) _←_ HSS _._ Share(sk _,_ _**x**_ );

( _**y**_ _σ, γσ_ ) _←_ HSS _._ Eval( _σ,_ ek _, sσ, P, δ_ ) _, σ ∈{_ 0 _,_ 1 _}._


**– Security:** _For any σ ∈{_ 0 _,_ 1 _}, any pair of inputs x, x_ _[′]_ _of the same length, the distribution en-_
_sembles Cσ_ ( _λ, x_ ) _and Cσ_ ( _λ, x_ _[′]_ ) _are computationally indistinguishable, where Cσ_ ( _λ, y_ ) _for y ∈_
_{x, x_ _[′]_ _} is obtained by sampling_ (sk _,_ ek) _←_ HSS _._ Gen(1 _[λ]_ ) _, sampling_ ( _s_ 0 _, s_ 1) _←_ HSS _._ Enc(sk _, y_ ) _,_
_and outputting_ (ek _, sσ_ ) _._


50


**C.3** **(** _**D,**_ **comp)-Compressible HSS**


In this section, we introduce a variant of homomorphic secret sharing, called _compressible HSS_
_for a family of distributions D_ (CHSS). Intuitively, a CHSS allows to share inputs sampled from
a distribution _Dn_, and guarantees that the size of each share is upper-bounded by comp( _λ, n_ ),
where comp is called the _compression ratio_ of the CHSS.


**Definition 46 (** ( _D,_ comp) **-Compressible HSS).** _A (2-party, secret-key, degree-d) compress-_
_ible homomorphic secret sharing over a ring R for a family of distributions D_ ( _R_ ) = _{Dn_ ( _R_ ) _}n∈_ N
_(such that_ Im( _Dn_ ( _R_ )) _⊆R_ _[n]_ _) with compression ratio_ comp _, or_ ( _D_ ( _R_ ) _,_ comp) _-CHSS, is a (2-party,_
_secret-key, degree-d) homomorphic secret sharing over R whose correctness is relaxed as follows:_


**– Relaxed Correctness.** _For every sufficiently large positive integers λ, n and degree-d arith-_
_metic circuit P with input length n, we have:_


Pr[ _**y**_ 0 + _**y**_ 1 _̸_ = _P_ ( _**x**_ )] _≤_ negl( _λ_ ) _,_


_where probability is taken over_


(sk _,_ ek) _←_ HSS _._ Gen(1 _[λ]_ ); _**x**_ _←D_ ( _R_ ) _n_ ; ( _s_ 0 _, s_ 1) _←_ $ HSS _._ Share(sk _,_ _**x**_ );

_**y**_ _b ←_ HSS _._ Eval( _b,_ ek _, sb, P_ ) _, b ∈{_ 0 _,_ 1 _},_


_and which satisfies an additional_ compressibility _property:_


**– Compressibility.** _A_ ( _D,_ comp) _-CHSS is_ compressible with compression ratio comp _if for_
_every sufficiently large integers λ, n, every input_ _**x**_ _∈_ Im( _Dn_ ) _, every_ (sk _,_ ek) _in the image_
_of_ HSS _._ Gen(1 _[λ]_ ) _, and every_ ( _s_ 0 _, s_ 1) _in the image of_ HSS _._ Share(sk _,_ _**x**_ ) _, it holds that |sσ| ≤_
comp( _λ, n_ ) _for σ_ = 0 _,_ 1 _._


**C.4** **BCG from LPN and Degree-2 CHSS**


Let _R_ be a ring. Let _D_ ( _R_ ) = _{D_ ( _R_ ) _n}n∈_ N be a family of efficiently sampleable distributions
over _R_ _[n]_ . Let comp be a compression ratio. Let HSS = (HSS _._ Gen _,_ HSS _._ Share _,_ HSS _._ Eval) be a
(2-party secret-key) degree-2 ( _D_ ( _R_ ) _× D_ ( _R_ ) _,_ comp)-CHSS. We describe below a construction of
a bilinear correlation generator over _R_ . Note that any bilinear function _B_ : _R_ _[n]_ _× R_ _[n]_ _�→R_ _[m]_ can
be fully described by a list of _m_ matrices _B_ 1 _· · · Bm_ with _Bi ∈R_ _[n][×][n]_ such that for any inputs
( _**x**_ _,_ _**x**_ _[′]_ ) _∈R_ _[n]_ _× R_ _[n]_, _B_ ( _**x**_ _,_ _**x**_ _[′]_ ) = ( _**x**_ [⊺] _Bi_ _**x**_ _[′]_ ) _i≤m_ . Let _α_ be a positive constant.


**–** BCG _._ Setup(1 _[λ]_ ) : output (pp = ek _,_ sk) _←_ $ HSS _._ Gen(1 _λ_ ).

**–** BCG _._ Gen(sk _, B_ ) : let _n_ denote the input size of _B_ and let _ℓ_ _←_ _αn_ . Let _M ←_ **C** ( _ℓ, ℓ_ _−_ _n, R_ )
be the encoding matrix of a linear code, and let _N ∈R_ _[n][×][ℓ]_ denote its parity check matrix
( _i.e._, _N_ is the matrix over _R_ _[n][×][ℓ]_ which satisfies _NM_ = 0). Pick two vectors ( _**z**_ 0 _,_ _**z**_ 1) _←_
_Dℓ_ ( _R_ ) _× Dℓ_ ( _R_ ) and let _r_ 0 (resp. _r_ 1) denote the random coin used to sample _**z**_ 0 (resp. _**z**_ 1).
Run ( _s_ 0 _, s_ 1) _←_ HSS _._ Share(sk _,_ ( _**z**_ 0 _,_ _**z**_ 1)). Output k _σ ←_ ( _rσ, sσ_ ) for _σ_ = 0 _,_ 1.

**–** BCG _._ Expand(pp _, σ,_ k _σ_ ) : parse k _σ_ as ( _rσ, sσ_ ) and reconstruct _**z**_ _σ_ from _rσ_ (using the sampling
procedure of _Dn_ ( _R_ )). Define the bilinear function _P_ : _R_ _[ℓ]_ _× R_ _[ℓ]_ _�→R_ _[m]_ as follows: on input
( _**x**_ _,_ _**x**_ _[′]_ ) _∈R_ _[ℓ]_ _× R_ _[ℓ]_, _P_ outputs ( _**x**_ [⊺] _· Bi_ _[′]_ _[·]_ _**[ x]**_ _[′]_ [)] _[i][≤][m]_ [, where] _[ B]_ _i_ _[′]_ [is defined as] _[ B]_ _i_ _[′]_ _[←]_ _[N]_ [⊺] _[B][i][N]_ [. Set]
_**x**_ _σ ←_ _N_ _**z**_ _σ_ . Compute _**y**_ _σ ←_ HSS _._ Eval( _σ,_ pp _, sσ, P_ ), and output ( _**x**_ _σ,_ _**y**_ _σ_ ).


**Theorem 47.** _Assuming the_ ( _D_ ( _R_ ) _,_ **C** ) _-_ LPN( _ℓ, ℓ_ _−_ _n_ ) _assumption, the above construction is a_
_bilinear correlation generator with seed size upper-bounded by_ 2 _·_ comp( _λ, ℓ_ ) _._


51


**C.5** **Proof of Theorem 47**


**C.5.1** **Correctness.**


As ( _**z**_ 0 _,_ _**z**_ 1) is sampled from _Dℓ_ ( _R_ ) _×Dℓ_ ( _R_ ), the relaxed correctness property of the CHSS applies,
and we get:


_**y**_ 0 + _**y**_ 1 = HSS _._ Eval(0 _,_ ek _, s_ 0 _, P_ ) + HSS _._ Eval(1 _,_ ek _, s_ 1 _, P_ )

= ( _**z**_ [⊺] 0 _[B]_ _i_ _[′]_ _**[z]**_ [1][)] _[i][≤][m]_ [= ((] _[N]_ _**[z]**_ [0][)][⊺] _[B][i]_ [(] _[N]_ _**[z]**_ [1][))] _[i][≤][m]_
= ( _**x**_ [⊺] 0 _[B][i]_ _**[x]**_ [1][)] _[i][≤][m]_ [ =] _[ B]_ [(] _**[x]**_ [0] _[,]_ _**[ x]**_ [1][)] _[.]_


**C.5.2** **Security.**


Let _A_ be a (stateful, nonuniform) PPT adversary, and let _σ_ be a bit. We proceed through a
sequence of game.


**– Game** _G_ 0 **.** In this game, we run (pp _,_ sk) _←_ $ BCG _._ Setup(1 _λ_ ), set _B ←A_ (pp), (k0 _,_ k1) _←_ $
BCG _._ Gen(sk _, B_ ), and
( _**x**_ _σ,_ _**y**_ _σ_ ) _←_ BCG _._ Expand(pp _, σ,_ k _σ_ ) _._


This corresponds to the first experiment in the security definition of bilinear correlation
generators. Let _b_ 0 be the output of _A_ ( _**x**_ _σ,_ k1 _−σ_ ).

**– Game** _G_ 1 **.** In this game, we modify the execution of BCG _._ Gen as follows: instead of computing
( _s_ 0 _, s_ 1) _←_ HSS _._ Share(sk _,_ ( _**z**_ 0 _,_ _**z**_ 1)), we set ( _s_ 0 _, s_ 1) _←_ HSS _._ Share(sk _,_ 0 [2] _[ℓ]_ ). Let _b_ 1 denote the
output of _A_ in this game. By the security property of the CHSS, the distribution of (ek _, s_ 1 _−σ_ )
in this game is computationally indistinguishable from the distribution of (ek _, s_ 1 _−σ_ ) in _G_ 0,
hence we have Pr[ _b_ 0 _̸_ = _b_ 1] = negl( _λ_ ).

**– Game** _G_ 2 **.** In this game, we modify the execution of BCG _._ Expand as follows: instead of
computing _**x**_ _σ_ as _N_ _**z**_ _σ_, we pick _**x**_ _σ_ _←R_ $ _n_ . Note that k1 _−σ_ does not depend on _**z**_ _σ_, hence
distinguishing between the games _G_ 2 and _G_ 1 amounts to distinguishing _N_ _**z**_ _σ_ from a random
vector over _R_ _[n]_, where _**z**_ _σ_ is drawn from _Dℓ_ ( _R_ ). Note also that _N_ _**z**_ _σ_ = _N_ ( _M_ _**a**_ + _**z**_ _σ_ ) for
any vector _**a**_ _∈R_ _[n]_ (as _NM_ = 0). Therefore, this amounts to distinguishing _M_ _**a**_ + _**z**_ _σ_ from
random, for an arbitrary secret vector _**a**_ _∈R_ _[n]_, and a noise vector _**z**_ _σ_ sampled from _Dℓ_ ( _R_ ),
which is infeasible under the ( _D_ ( _R_ ) _,_ **C** ) _−_ LPN( _ℓ, ℓ_ _−_ _n_ ) assumption. Therefore, denoting _b_ 2
the output of _A_ in _G_ 2, we have Pr[ _b_ 1 _̸_ = _b_ 2] = negl( _λ_ ).

**– Game** _G_ 3 **.** In this game, we revert the change made in _G_ 1 and compute again ( _s_ 0 _, s_ 1) as
HSS _._ Share(sk _,_ ( _**z**_ 0 _,_ _**z**_ 1)). Let _b_ 3 denote the output of _A_ in this game. By the security property
of the CHSS, we have Pr[ _b_ 2 _̸_ = _b_ 3] = negl( _λ_ ). Furthermore, this game is exactly the second
experiment in the security definition of a BCG, which concludes the proof.


**C.5.3** **Efficiency.**


The seed size of the BCG is _|_ k _σ|_ = _|rσ|_ + _|sσ|_ . By the compressibility of the CHSS, _|sσ| ≤_
comp( _λ, ℓ_ ). Furthermore, by the restricted correctness of the CHSS, it must hold that _|rσ| ≤_
_|sσ| ≤_ comp( _λ, ℓ_ ) (otherwise, using HSS _._ Share and HSS _._ Eval would allow to compress samples
from _Dℓ_ ( _R_ ) below their amount of entropy, which is impossible). Hence, we get _|_ k _σ| ≤_ 2 _·_
comp( _λ, ℓ_ ).


**C.5.4** **Sanitizable BCG from LPN and Compressible Las Vegas HSS.**


Given a compressible Las Vegas HSS, one immediately gets a sanitizable BCG under the LPN
assumption, using the above construction. The security analysis of the construction is almost
identical, with the failure probability of Las Vegas HSS translating directly to the failure probability of BCG outputs. Note that the standard formulation of Las Vegas HSS considers a global


52


failure probability for the entire vector output, and outputs a single flag in _{⊤, ⊥}_ to indicate
correctness of the output, while our definition of sanitizable BCG requires outputting a different
flag for each output (with the goal of later removing faulty outputs while keeping correct ones).
This is essentially a syntactic difference: existing construction of Las Vegas HSS can easily be
modified to output a flag for each output bit. In the formal construction of sanitizable BCG
from Las Vegas HSS, it suffices to apply the Las Vegas HSS independently for each functions _fi_
outputting the _i_ th bit of the target bilinear correlation, to get independent failure flags for each
output bit.


**C.6** **Group-Based HSS for Bilinear Functions**


In this section, we provide an overview of the group-based homomorphic secret sharing scheme
first introduced in [BGI16a], and subsequently optimized in [BGI17, BCG [+] 17, DKK18]. When
restricted to bilinear functions, as observed in [BCG [+] 17, Section 4.6], the scheme can be considerably simplified and optimized. Below, we briefly recall the HSS scheme of [BGI16a], taking into
account the optimizations for bilinear functions of [BCG [+] 17]. The scheme allows to compute
bilinear functions over any ring Z _t_ of polynomial size; it relies on a group G where the discrete
log is conjectured to be hard.


**C.6.1** **Encoding** Z _**q**_ **Elements.**


Let _q_ be a large prime, and let G be a hard-discrete-log group of order _q_ . Let _g_ denote a generator
of G. For any _x ∈_ Z _q_, we consider the following 3 types of two-party encodings:


Level 1: “Encryption.” For _x ∈_ Z _q_, we let [ _x_ ] denote _g_ _[x]_, and _x_ _s_ denote ([ _r_ ] _,_ [ _r · s_ + _x_ ]) for a
uniformly random _r ∈_ Z _q_, which corresponds to an ElGamal encryption of � - _x_ with a secret key
_s ∈_ Z _q_ . All level-1 encodings are known to both parties. We let sk _←_ ( _s, −_ 1).


Level 2: “Additive shares.” Let _⟨x⟩_ denote a pair of shares _x_ 0 _, x_ 1 _∈_ Z _q_ such that _x_ 0 = _x_ 1 + _x_,
where each share is held by a different party. We let ⟪ _x_ ⟫ _s_ denote ( _⟨−s · x⟩_ _, ⟨x⟩_ ) = sk _·⟨x⟩∈_ (Z [2] _q_ [)][2][,]
namely each party holds one share of _⟨−s · x⟩_ and one share of _⟨x⟩_ . Note that both types of
encodings are additively homomorphic over Z _q_, namely given encodings of _x_ and _x_ _[′]_ the parties
can locally compute a valid encoding of _x_ + _x_ _[′]_ .


Level 3: “Multiplicative shares.” Let _{x}_ denote a pair of shares _x_ 0 _, x_ 1 _∈_ G such that the
difference between their discrete logarithms is _x_ . That is, _x_ 0 = _x_ 1 _· g_ _[x]_ .


**C.6.2** **Operations on Encodings.**


All types of encodings allow to locally evaluate linear functions (they are additively homomorphic). To evaluate degree-2 polynomials, we define a multiplication algorithm Mult which, given
a level 1 encoding of an inpuy _x_ and a level 2 encoding of an input _y_, outputs additive shares
of _xy_ . To this end, we consider the following two types of operations, performed locally by the
two parties:

1. Pair( _x_ _s,_ ⟪ _y_ ⟫ _s_ ) _�→{xy}_ . This pairing operation exploits the fact that the decryption of an

     -     ElGamal ciphertext _x_ _s_ is computed as a scalar product in the exponent: _g_ _[x]_ = sk _•_ _x_ _s_ .
             -              -              -              Therefore, Pair computes ⟪ _y_ ⟫ _s•_ _x_ _s_ = _⟨y⟩•_ (sk _•_ _x_ _s_ ) = _{xy}_ . Note that we consider ElGamal

                   -                   -                   -                   ciphertexts for the sake of concreteness only; any encryption scheme whose decryption follows
a similar “scalar product in the exponent” structure would suffice.
2. Convert( _{z}, δ_ ) _�→⟨z⟩_, with failure bound _δ_ . The implementation of Convert is also given
an upper bound _M_ on the “payload” _z_ ( _M_ = 1 by default), and its expected running time
grows linearly with _M/δ_ . We omit _M_ from the following notation.


53


The Convert algorithm works as follows. Each party, on input _h ∈_ G, outputs _i_ mod _t_, with
_i_ the minimal integer _i ≥_ 0 such that _h · g_ _[i]_ is “distinguished,” where roughly a _δ_ -fraction of the
group elements are distinguished. Distinguished elements were picked in [BGI16a] by applying
a pseudo-random function to the description of the group element. An optimized conversion
procedure from [BGI17, BCG [+] 17] applies the heuristic of defining a group element to be distinguished if its bit-representation starts with a 1 followed by _d ≈_ log2( _M/δ_ ) leading 0’s. Note
that this heuristic only affects the running time and not security, and thus it can be validated
empirically. Correctness of Convert holds if no group element _between_ the two shares _{z} ∈_ G [2] is
distinguished. Finally, Convert signals that there is a potential failure if there is a distinguished
point in the “danger zone.” Namely, Party _b_ = 0 (resp., _b_ = 1) raises a potential error flag if
_h · g_ _[−][i]_ (resp., _h · g_ _[i][−]_ [1] ) is distinguished for some _i_ = 1 _, . . ., M_ .
The Convert algorithm requires an upper bound _M_ on the multiplicatively shared exponent,
and runs in time proportional to _M_ . Concretely, this means that we only consider inputs coming
from a set Z _t_ where _t_ is polynomial, so that the product between any two (linear combination
of) inputs is polynomially bounded. Note that all operations are performed over Z _q_, where _q_ is
an exponentially large prime; as all inputs are lower than _t_, which is polynomial, no modular
reduction ever occurs, hence the computation of _i_ is performed over the integers; therefore, the
parties obtain additive shares of the product over Z _t_ after the final (local) reduction of _i_ modulo
_t_ . We refer the reader to [BCG [+] 17] for a detailed analysis and further optimizations of the
Convert procedure.
Given the Pair and Convert algorithms, the multiplication algorithm Mult sequentially executes these two operations: Mult( _x_ _c,_ ⟪ _y_ ⟫ _c, δ_ ) _�→⟨xy⟩_, with error _δ_ . Note that the output of the

                  -                  procedure is not a level 1 or a level 2 encoding. Therefore, this _δ_ -failure HSS allows to evaluate
arbitrary bilinear functions _B_ on vectors ( _**x**_ _,_ _**y**_ ) (encodings of level 1 and 2, as well as additive shares, being additively homomorphic) but does not generalize immediately to functions of
higher degree; generalizations to branching programs are presented in [BGI16a,BGI17,BCG [+] 17],
but are several orders of magnitude less efficient.


**C.6.3** **Improved Conversion.**


In a recent paper [DKK18], Dinur _et al._ designed an improved distributed discrete logarithm
procedure. Their elegant algorithm is based on a clever random walk with steps of varying
length, that bears some resemblance with Pollard’s kangaroo method (but requires a considerably more complex and mathematically involved analysis). The improved algorithm requires _T_
multiplications to achieve a failure probability of _O_ ( _M/T_ [2] ), where the constant hidden in the
_O_ ( _·_ ) notation is always upper bounded by 2 [10] _[.]_ [2], and in practice approximately equal to 400
(the authors provide a table with optimal parameters for various choices of _T_, that gives the
exact constant), improving over the _O_ ( _M/T_ ) failure probability of the previous method. Their
paper also proves the optimality of this algorithm. In this work, we will rely on their improved
conversion algorithm, and refer the reader to [DKK18] for further details on this procedure.


**C.7** **The BGN-EG Cryptosystem**


The Boneh-Goh-Nissim cryptosystem (BGN) was introduced in [BGN05]. It is a variant of
the ElGamal cryptosystem over composite-order pairing-friendly elliptic curve, which allows
to homomorphically compute any degree-2 polynomial on encrypted plaintexts, provided that
the output is of polynomial size (as decryption requires computing a discrete logarithm). An
adaptation of BGN to prime-order pairing-friendly elliptic curves was introduced by Freeman
in [Fre10]. As it suffices for our purpose, we will rely in this work on a simplified variant of
Freeman’s cryptosystem, where encryption in any of the pairing-friendly groups will exactly be
ElGamal encryption, and where ciphertexts obtained through homomorphic operations are not
rerandomized.


54


Let BilinearGen denote a PPT algorithm which, on input 1 _[λ]_, outputs a prime _q_, the description
of three cyclic groups (G1 _,_ G2 _,_ G _t_ ), elements ( _g_ 1 _, g_ 2) _∈_ G1 _×_ G2, and a map _e_ such that


**–** the cyclic groups have the same order _q_ = _q_ ( _λ_ );

**–** the map _e_ : G1 _×_ G2 _�→_ G _t_ is an efficiently computable non-degenerate bilinear map, _i.e._,
_∀_ ( _u, v_ ) _∈_ G1 _×_ G2 and ( _a, b_ ) _∈_ Z _p_, _e_ ( _u_ _[a]_ _, v_ _[b]_ ) = _e_ ( _u, v_ ) _[ab]_ ;

**–** _gi_ generates G _i_ for _i ∈{_ 1 _,_ 2 _}_ (and _gt ←_ _e_ ( _g_ 1 _, g_ 2) generates G _t_ ).


Note that this captures groups equipped with an _asymmetric_ pairing. To simplify notations, given
vectors _**x**_ _∈_ G _[n]_ 1 _[,]_ _**[ y]**_ _[ ∈]_ [G] _[n]_ 2 [, we will write] _[ e]_ [(] _**[x]**_ _[,]_ _**[ y]**_ [)][ to denote][ (] _[e]_ [(] _[x][i][, y][j]_ [))] _[i,j][≤][n]_ [. When it happens that]
the components of the vector are vectors themselves (e.g. if _**x**_ _,_ _**y**_ are vectors of ciphertexts, each
ciphertext consisting of several group elements), we apply the notation recursively: _e_ ( _**x**_ _,_ _**y**_ ) =
( _e_ ( _xi, yj_ )) _i,j≤n_ and for every _i, j_, _e_ ( _xi, yj_ ) = ( _e_ ( _xi,i′, yj,j′_ )) _i′,j′_ .
We outline below our simplified variant of Freeman’s adaptation of the BGN cryptosystem,
which we denote BGN-EG.


**–** BGN-EG _._ Setup(1 _[λ]_ ) : output pp = ( _q,_ G1 _,_ G2 _,_ G _t, g_ 1 _, g_ 2 _, e_ ) _←_ $ BilinearGen(1 _λ_ ).

**–** BGN-EG _._ KeyGen(pp) : pick ( _s_ 1 _, s_ 2) _←_ $ Z2 _q_ [, compute][ (] _[h]_ [1] _[, h]_ [2][)] _[ ←]_ [(] _[g]_ 1 _[s]_ [1] _[, g]_ 2 _[s]_ [2][)][. Set][ sk] _[i][ ←]_ [(] _[s][i][,][ −]_ [1)]
for _i_ = 1 _,_ 2, and sk _t_ = ( _s_ 1 _· s_ 2 _, −s_ 1 _, −s_ 2 _,_ 1). Output pk _←_ (pp _, h_ 1 _, h_ 2) and sk _←_ (sk1 _,_ sk2 _,_ sk _t_ ).

**–** BGN-EG _._ Enc _i_ (pk _, m_ ; _r_ ) : on input the public key pk, a message _m ∈_ Z _q_, and a random coin
_r ∈_ Z _q_, output _**c**_ _i ←_ ( _gi_ _[r][, h]_ _i_ _[r][g]_ _i_ _[m]_ [)][ (this corresponds to encryption over][ G] _[i]_ [).]

**–** BGN-EG _._ Dec _i_ (sk _,_ _**c**_ _i_ ): on input the secret key sk and a ciphertext _**c**_ _i_, compute _c ←_ sk _i •_ _**c**_ _i_
and output _m ←_ dlog _gi_ ( _c_ ).


Correctness follows by inspection; security reduces to the decisional Diffie-Hellman assumption
(DDH) in G1 and G2. It is easy to see that the scheme is additively homomorphic over each
of G1 and G2. Furthermore, given an encryption _**c**_ 1 of a message _m_ 1 over G1 and an encryption _**c**_ 2 of a message _m_ 2 over G2, one can homomorphically construct an encryption of _m_ 1 _m_ 2
over G _t_ as follows: compute _**c**_ _t ←_ _e_ ( _**c**_ 1 _,_ _**c**_ 2). The resulting ciphertext has four components and
remains additively homomorphic over G _t_ (addition of plaintext is computed by component-wise
multiplication). Decryption of a ciphertext over G _t_ is performed by computing _c ←_ sk _t •_ _**c**_ _t_, and
outputting _m ←_ dlog _gt_ ( _c_ ), where _gt_ = _e_ ( _g_ 1 _, g_ 2).


**C.8** **Compressible HSS from BGN-EG**


We now show how the group-based HSS of [BGI16a, BGI17, BCG [+] 17] can be modified to get a
compressible HSS. In this section, we will consider compressible HSS over a small (polynomialsize) ring Z _t_ for inputs drawn from the Bernouilli distribution Ber _r_ (Z _t_ ) for some rate _r_ (see
Section 3.3); that is, we will consider inputs with a sparse structure, and show how level 1 and
level 2 encodings of such inputs can be compressed. Let (G1 _,_ G2 _,_ G _t_ ) denote three cyclic groups
of order _q_, and let _e_ : G1 _×_ G2 _�→_ G _t_ denote a pairing. Observe that the ciphertexts in the
target group G _t_ of BGN-EG have a suitable structure to be used as level-1 encodings in the HSS
scheme, as decryption of a ciphertext over G _t_ is performed via a scalar product in the exponent.


**C.8.1** **Modifying the DDH-Based HSS.**


We modify the HSS scheme of the previous section as follows: a level 1 encoding _x_ sk of _x_ is
a BGN-EG encryption of _x_ in the target group G _t_ . A level 2 encoding ⟪ _y_ ⟫sk of a message � - _y_
is a 4-tuple sk _t · ⟨y⟩_ . The Pair algorithm, on input a level 1 encoding _x_ sk and level 2 shares
                                      -                                       ⟪ _y_ ⟫sk, outputs ⟪ _y_ ⟫sk _•_ _x_ sk; a level 3 encoding of a message _z_ is a multiplicative share over
G _t_ of _gt_ _[z]_ [; it follows that] - [ Pair] - [(][�] _[x]_ [�] sk _[,]_ [ ⟪] _[y]_ [⟫] sk [) =] _[ {][xy][}]_ [. Then, the parties can apply the optimized]
Convert procedure of [DKK18] to obtain additive shares of _xy_ . The security of this modified
HSS scheme immediatly reduces to the DDH assumption in G1 and G2, by the same security
analysis as for the HSS of [BGI16a] (note that, because we restrict our attention to HSS for


55


bilinear function, we do not need to use circularly-secure variants of ElGamal to get security
under DDH; a circularly-secure scheme is needed in [BGI16a] because encryptions of the secret
key must be released to allow for the evaluation of more complex functions).


**C.8.2** **Compressing Level 1 Encodings under BGN-EG.**


The modified scheme suggests a natural strategy to reduce the size of level 1 encodings when
the input is sparse, by exploiting the homomorphic properties of BGN-EG ciphertexts. Let _**m**_
be a length- _ℓ_ vector over Z _q_, which has at most _k_ non-zero coordinates. We assume _ℓ_ to be a
square for simplicity. The compression method works as follows: arrange the coordinates of _**m**_ in
_√_ _√_
a _ℓ_ _×_ _ℓ_ matrix _M_ . Decompose _M_ into [�] _[k]_ _[M][i]_ [, where each matrix] _[ M][i]_ [ has a single non-zero]



_√_
_ℓ_ _×_



_i_ =1 _√_

_ℓ_ ] _×_ [



a _ℓ_ _×_ _ℓ_ matrix _M_ . Decompose _M_ into _√_ [�] _i_ _[k]_ =1 _√_ _[M][i]_ [, where each matrix] _[ M][i]_ [ has a single non-zero]

coordinate. For _i_ = 1 to _k_, let ( _ui, vi_ ) _∈_ [ _ℓ_ ] _×_ [ _ℓ_ ] denote the coordinate of the non-zero entry



coordinate. For _i_ = 1 to _k_, let ( _ui, vi_ ) _∈_ [ _ℓ_ ] _×_ [ _ℓ_ ] denote the coordinate of the non-zero entry

of _Mi_ . _√_
Pick 2 _ℓ_ elements ( _αi,j, βi,j_ ) _√_ [of][ Z] _[q]_ [ as follows: for each pair][ (] _[u, v]_ [)] _[ ̸]_ [= (] _[u][i][, v][i]_ [)][, set] _[ α][i,u]_ [ =]



_ℓ_ elements ( _αi,j, βi,j_ ) _j≤√_



Pick 2 _ℓ_ elements ( _αi,j, βi,j_ ) _j≤√ℓ_ [of][ Z] _[q]_ [ as follows: for each pair][ (] _[u, v]_ [)] _[ ̸]_ [= (] _[u][i][, v][i]_ [)][, set] _[ α][i,u]_ [ =]

_βi,v_ = 0, and set _αi,ui_ = 1, _βi,vi_ _√_ = _Mi|u√i,vi_ . Observe that, by construction, it hold _√_ s that _√Mi|u,v_ =
_αi,u · βi,v_ for any pair ( _u, v_ ) _∈_ [ _ℓ_ ] _×_ [ _ℓ_ ]. Therefore, we have for any ( _u, v_ ) _∈_ [ _ℓ_ ] _×_ [ _ℓ_ ]:



_i_ _u√i,_

_ℓ_ ] _×_ [



_vi_ _√_

_ℓ_ ]. Therefore, we have for any ( _u, v_ ) _∈_ [



_√_
_ℓ_ ] _×_ [



_ℓ_ ]:



_M_ _|u,v_ =



_k_


_αi,u · βi,v._

_i_ =1



This shows that for any vector _**m**_ with at most _k_ non-zero entries, one can create a level 1
encoding of _**m**_ as follows: compute the ( _αi,u, βi,u_ ) _i≤k,u≤√ℓ_ [as above, and set the encoding of] _**[ m]**_



_√_
to be _k ·_



_i≤k,u≤_ _ℓ_ _√_

_ℓ_ BGN-EG encryptions of ( _αi,u_ ) _i,u_ over G1, and _k ·_



_ℓ_ [as above, and set the encoding of] _**[ m]**_



to be _k ·_ _ℓ_ BGN-EG encryptions of ( _αi,u_ ) _i,u_ over G1, and _k ·_ _ℓ_ BGN-EG encryptions of ( _βi,u_ ) _i,u_

over G2. Using the homomorphic properties of BGN-EG, any party can then locally reconstruct
a BGN- _√_ EG encryption of _**m**_ = ( [�] _[k]_ _i_ =1 _[α][i,u][ ·][ β][i,v]_ [)] _[u,v]_ [ over][ G] _[t]_ [. The size of the compressed encoding]
is 2 _k ·_ _ℓ_ _·_ ( _|_ G1 _|_ + _|_ G2 _|_ ). Note that this strategy corresponds exactly to using the LPN-based



is 2 _k ·_ _ℓ_ _·_ ( _|_ G1 _|_ + _|_ G2 _|_ ). Note that this strategy corresponds exactly to using the LPN-based

PRG introduced in Section 4.4 to stretch the encoded seed.



**C.8.3** **Compressing Level 2 Encodings using FSS.**

We now turn our attention to level 2 encodings ⟪ _**m**_ ⟫sk = ( _⟨s_ 1 _s_ 2 _·_ _**m**_ _⟩_ _, ⟨−s_ 1 _·_ _**m**_ _⟩_ _, ⟨−s_ 2 _·_ _**m**_ _⟩_ _, ⟨_ _**m**_ _⟩_ ).
Note that if _**m**_ is a sparse vector, so are _s_ 1 _s_ 2 _·_ _**m**_ _, −s_ 1 _·_ _**m**_ _,_ and _−s_ 2 _·_ _**m**_ . We therefore focus
on compressing additive shares of arbitrary sparse vectors over Z _q_ . As was observed recently
in [BCGI18], this type of correlation can be efficiently compressed using function secret sharing
for multi-point functions (MPFSS). We elaborate below.
Let MPFSS = (MPFSS _._ Gen _,_ MPFSS _._ Eval _,_ MPFSS _._ FullEval) be a multi-point function secret sharing. On input a vector _**m**_ _∈_ Z _[ℓ]_ _q_ [with][ HW][ (] _**[m]**_ [)] _[ ≤]_ _[k]_ [, let][ proj] _**m**_ [: [] _[ℓ]_ []] _[ �→]_ [Z] _[q]_ [be the]
function which, on input _i ∈_ [ _ℓ_ ], outputs the _i_ ’th coordinate of _**m**_ . Note that proj _**m**_ is an
( _ℓ, k_ )-multi-point function over Z _q_ . To generate compressed additive shares of _**m**_, compute
( _K_ 0 _, K_ 1) _←_ $ MPFSS _._ Gen(1 _λ,_ proj _**m**_ ). To decompress the string, each party with input _Kσ_ computes MPFSS _._ FullEval( _σ, Kσ_ ), obtaining additive shares of (proj _**m**_ ( _i_ )) _i∈_ [ _ℓ_ ] = _**m**_ . Correctness
immediately follows from the correctness of the underlying MPFSS. Regarding security, we
must show that for any pair ( _**m**_ _,_ _**m**_ _**[′]**_ ) (with HW ( _**m**_ ) _,_ HW ( _**m**_ _**[′]**_ ) _≤_ _k_ ) and any _σ ∈{_ 0 _,_ 1 _}_,
the distribution of (ek _σ, sσ_ ) obtained by sampling (sk _,_ (ek0 _,_ ek1)) _←_ HSS _._ Gen(1 _[λ]_ ), sampling
( _s_ 0 _, s_ 1) _←_ HSS _._ Enc(sk _,_ _**m**_ ) or ( _s_ 0 _, s_ 1) _←_ HSS _._ Enc(sk _,_ _**m**_ _**[′]**_ ), and outputting (ek _σ, sσ_ ), are computationally indistinguishable. This immediately follows from the fact that, by the MPFSS security,
there is a simulator which (given Leak(proj _**m**_ ) = Leak(proj _**m′**_ ), and no further information about
_**m**_ _,_ _**m**_ _**[′]**_ ) can output a simulated key _sσ_ = _Kσ_ whose distribution is indistinguishable from an
honestly generated key.
Using the PRG-based MPFSS of [BGI16b,BCGI18], the size of a compressed encoding using
this method is equal to _k ·_ ( _⌈_ log _ℓ⌉·_ ( _λ_ + 2) + _λ_ + _⌈_ log _q⌉_ ). We refer the reader to [BCGI18] for
further discussions on this method and optimizations of MPFSS tailored to this application.


56


**C.8.4** **Putting the Pieces Together.**


Combining the above techniques, we get


**Theorem 48.** _Assuming the DDH assumption over pairing-friendly elliptic curves, for any in-_
_teger t of polynomial size and any integer k, there exists a_ (Ber _k/ℓ_ (Z _t_ ) _,_ comp( _λ, ℓ, k_ )) _-compressible_
_(Las Vegas, secret-key, degree-_ 2 _) CHSS, with_



_√_
comp( _λ, ℓ, k_ ) = _k ·_



_ℓ_ _·_ poly( _λ_ ) _._



For self-containement, we describe below the full CHSS. It has two sharing algorithms, corresponding to level 1 and level 2 shares respectively. The evaluation procedure allows to compute
(shares of) any bilinear function _B_ ( _**x**_ _,_ _**y**_ ) where _**x**_ is level-1-shared and _**y**_ is level-2-shares between
the parties.


**–** HSS _._ Gen(1 _[λ]_ ): run pp = ( _q,_ G1 _,_ G2 _,_ G _t, g_ 1 _, g_ 2 _, e_ ) _←_ $ BGN-EG _._ Setup(1 _λ_ ), as well as (pk _,_ sk) _←_
BGN-EG _._ KeyGen(pp). Compute _g ←_ _e_ ( _g_ 1 _, g_ 2). Output ek _←_ (pp _,_ pk _, g_ ) and sk.

**–** HSS _._ Share1(sk _,_ _**m**_ ): let _k_ denote an upper bound on the sparsity of _**m**_, and let _√ ℓ_ denote
the length of _**m**_ . Let ( _**α**_ _i,_ _**β**_ _i_ ) _i≤k_ denote the decomposition of _**m**_ in 2 _k_ length- _ℓ_ vectors,

as described in Section C.8. Compute, for _i_ = 1 to _k_, ( _**c**_ _i,_ _**d**_ _i_ ) _←_ $ (BGN-EG _._ Enc1(pk _,_ _**α**_ _i_ ) _,_
BGN-EG _._ Enc2(pk _,_ _**β**_ _i_ )) and output share0 = share1 = ( _**c**_ _i,_ _**d**_ _i_ ) _i≤k_ .

**–** HSS _._ Share2(sk _,_ _**m**_ ): let _k_ denote an upper bound on the sparsity of _**m**_, and let _ℓ_ denote the
length of _**m**_ . Parse sk as (sk1 _,_ sk2 _,_ sk _t_ ) and parse sk _i_ as ( _si, −_ 1) for _i_ = 1 _,_ 2. Let **proj** _**m**_ _,_ sk _←_
(proj _s_ 1 _s_ 2 _**m**_ _,_ proj _−s_ 1 _**m**_ _,_ proj _−s_ 2 _**m**_ _,_ proj _**m**_ ), where proj is defined as in Section C.8.3. Compute


( _**K**_ 0 _,_ _**K**_ 1) _←_ MPFSS _._ Gen(1 _[λ]_ _,_ **proj** _**m**_ _,_ sk) _._


Return share _[′]_ 0 _[←]_ _**[K]**_ [0] [and][ share] _[′]_ 1 _[←]_ _**[K]**_ [1][.]

**–** HSS _._ Eval( _σ,_ ek _,_ share _σ,_ share _[′]_ _σ_ _[, B, δ]_ [)][: On input party index] _[ σ][ ∈{]_ [0] _[,]_ [ 1] _[}]_ [, evaluation key][ ek][, level]
1 share share _σ_ of a size- _ℓ_ input, level 2 share share _[′]_ _σ_ [of a size-] _[ℓ]_ [input, a bilinear function]
_B_ : Z _[ℓ]_ _t_ _[×]_ [Z] _t_ _[ℓ]_ _[�→]_ [Z] _t_ _[m]_ [with] _[ B]_ [(] _**[x]**_ _[,]_ _**[ y]**_ [) = (][�] _i,j_ _[b][i,j,θ][ ·]_ _[x][i][y][j]_ [)] _[θ][≤][m]_ [, and failure probability bound] _[ δ >]_ [ 0][:]

_•_ Parse share _σ_ as ( _**c**_ _i,_ _**d**_ _i_ ) _i≤k_, and compute _ℓ_ ciphertexts ( _e_ 1 _, · · ·, eℓ_ ) _←_ [�] _[k]_ _i_ =1 _[e]_ [(] _**[c]**_ _[i][,]_ _**[ d]**_ _[i]_ [)][.]

_•_ Parse share _[′]_ _σ_ [as] _**[ K]**_ _[σ]_ [. Compute] _**[ K]**_ _σ_ _[′]_ _[←]_ [MPFSS] _[.]_ [FullEval][(] _[σ,]_ _**[ K]**_ _[σ]_ [)][. Note that] _**[ K]**_ _σ_ _[′]_ [is a vector]
of _ℓ_ length-4 vectors _**K**_ _[′]_ _σ,i_ [.]

_•_ For every ( _i, j_ ) _∈_ [ _ℓ_ ] [2], _ri,j ←_ Pair( _ei,_ _**K**_ _[′]_ _σ,j_ [) =] _**[ K]**_ _[′]_ _σ,j_ _[•][ e][i]_ [.]

_•_ For _θ_ = 1 to _m_, let _hθ ←_ ( _bi,j,θ_ ) _i,j •_ ( _ri,j_ ) _i,j_ .

_•_ Output (Convert( _hi, δ/m_ )) _i≤m_, where Convert is run in base _g_ over G _t_ .


Plugging the above HSS in our LPN-based construction of BCG from compressible HSS, we
get:


**Theorem 49.** _Assuming the DDH assumption over pairing-friendly elliptic curves and the_
LPN(( _α −_ 1) _· n, α · n, k/_ ( _αn_ )) _assumption over an integer ring_ Z _t of polynomial size, for a_
_positive constant α >_ 1 _, there exists a δ-failure SBCG with seed size k ·_ ( _α · n_ ) [1] _[/]_ [2] _·_ poly( _λ_ ) _._


**D** **Optimizing the Group-Based PCG**


While the compressible HSS described in Section C leads to a (sanitizable) PCG for bilinear
correlations under the LPN assumption, a direct instantiation from the above group-based CHSS
and LPN would remain computationally heavy. Below, we outline several optimizations to reduce
the cost of group-based PCG, which significantly reduce the computation and size of the PCG
seeds.


57


**D.1** **General Optimizations**



In the construction of BCG from CHSS of Section C.4, two vectors _**z**_ 0 and _**z**_ 1 are sampled and
shared between the parties using HSS _._ Share, and each party gets to know one of these vectors.
Using the group-based CHSS, this means that one party knows both _**z**_ 0 and the level 1 encoding of _**z**_ 0. Therefore, we can trivially observe that revealing the random coins of this level 1
encoding to this party does not compromise the security of the BCG (as BGN-EG is only used
to encrypt vectors that he knows in the clear anyway). Knowing the BGN-EG random coins of
the level 1 encoding allows the party to perform the decompression procedure without computing pairings. To illustrate, consider the task of homomorphically multiplying two ciphertexts
( _g_ 1 _[r]_ [1] _[, h]_ 1 _[r]_ [1] _[g]_ 1 _[m]_ [1][)] _[ ∈]_ [G] 1 [2] [and][ (] _[g]_ 2 _[r]_ [2] _[, h]_ 2 _[r]_ [2] _[g]_ 2 _[m]_ [2][)] _[ ∈]_ [G] 2 [2][. The party who knows][ (] _[m]_ [1] _[, r]_ [1] _[, m]_ [2] _[, r]_ [2][)][ can simply]
have precomputed _e_ ( _g_ 1 _, g_ 2) _, e_ ( _g_ 1 _, h_ 2) _, e_ ( _h_ 1 _, g_ 2), and _e_ ( _h_ 1 _, h_ 2) in a one-time setup phase, and obtain each term directly by computing exponentiations over G _t_ (e.g., _e_ ( _g_ 1 _[r]_ [1] _[, g]_ 2 _[r]_ [2][)][ is computed as]
_e_ ( _g_ 1 _, g_ 2) _[r]_ [1] _[r]_ [2], using the precomputed _e_ ( _g_ 1 _, g_ 2) and the random coins _r_ 1 _, r_ 2 known in the clear).
Therefore, for this party, the cost of decompressing a level 1 encoding (still counting all previous optimizations) is reduced from computing 4 _ℓ_ _pairings_ to computing 4 _ℓ_ _exponentiations_
_over_ G _t_ . Such exponentiations are typically up to an order of magnitude less costly than pairing
computations.
It is relatively straightforward to share equally the benefits of this optimization between
the two parties: instead of computing the BCG seeds as a (compressed) level 1 encoding of _**z**_ 0
and a (compressed) level 2 encoding of _**z**_ 1, we break each vector _**z**_ _i_ in two equal length parts
( _**z**_ [0] _i_ _[,]_ _**[ z]**_ _i_ [1][)][. Then, the seed is now computed as level][ 1][ encodings of both] _**[ z]**_ 0 [0] [and] _**[ z]**_ 1 [1][, and level][ 2]
encodings of both _**z**_ [1] 0 [and] _**[ z]**_ 1 [0][, and each party] _[ P][j]_ [ (for] _[ j]_ [ = 0] _[,]_ [ 1][) receives the random coins of one]
of the two level 1 encodings of half-vectors, and can therefore apply the above optimization to
this half-vector. This reduces the number of pairings computed by each party by a factor 2 (in
exchange for computing exponentiations over G _t_ ), which results in an improvement of almost a
factor two. Note that in a scenario where the parties have very different computational power
(e.g. a client and a server), it is better to use the asymmetric version, where the computationally
weak devices computes only exponentiations instead of pairings.
We can further reduce the size of level 1 encodings by applying a heuristic PRG-based
optimization which was described in [BGI16a]: the algorith _√_ m HSS _._ Share1 picks a random PR _√_ G
seed k for a PRG _G_, and parse _G_ (k) as a sequence of _ℓ_ group elements over G1 and _ℓ_

group elements over G2. Each group element is then interpreted as the first component of an
ElGamal ciphertext. Given a plaintext _m_ and a first component _c_, the second component of an
encryption of _m_ over G _i_ is computed as _c_ _[s][i]_ _·gi_ _[m]_ [.][ HSS] _[.]_ [Share][1][ outputs][ k][ together with the list of all]
second components of ElGamal ciphertexts, which results overall in a factor 2 compression. Note,
however, that this optimization cannot be directly cumulated with the previous optimization,
as HSS _._ Share1 cannot reveal the corresponding random coins to one of the parties.
However, there is another straightforward optimization which does not conflict the optimization based on revealing the random coins to a party: the coins and the plaintexts can be
generated as the output of a PRG _G_ on a short seed k, and the party who gets to learn the coins
and the plaintexts can be given k instead of the list of all plaintexts and random coins, reducing
the storage overhead for this party.
The security of our group-based BCG reduces to the standard LPN assumption, where
the linear code is generated uniformly at random, and the noise is a random sparse vector.
LPN has a long history in cryptography, and it is a common practice to consider variants of
this basic assumption to improve the efficiency of LPN-based primitives (several variants of
LPN are by now standard and well-established assumptions; a typical example is Alekhnovich’s
assumption [Ale03], which underlies his famous LPN-based cryptosystem). Two standard tweaks
that can be applied to LPN are the following:


**–** replacing the random linear code by a code with good properties (e.g. efficient encoding) to
speed-up the computation of noisy codewords;


58


**–** modifying the noise distribution, to adapt it to the constraints of the application.


Below, we analyze both types of modifications of the LPN assumption, showing how using variants of LPN (some well-established, some less standard) leads to improved efficiency
guarantees for the group-based BCG.


**D.2** **Optimizing the Noise Distribution**


In this section, we discuss alternative choice of distributions from which to sample the noise
vector, which are better suited for the encoding algorithms of the group-based BCG.


**D.2.1** **Regular Syndrome Decoding.**


The regular syndrome decoding assumption is a variant of the LPN assumption which was
introduced in [AFS03] as the assumption underlying the security of a candidate for the SHA3 competition, and has been studied at length (see [HOSS18] for a recent survey about the
cryptanalysis of the RSD assumption and a detailed discussion about its security). Roughly,
it states that LPN remains hard, even if the sparse noise vector is _regular_, meaning that it is
divided into _k_ blocks of size _n/k_ each, each block containing a single random 1, and zeroes
everywhere else.
It was shown in [BCGI18] that the RSD can be used to improve the computational effiency
of the FSS-based encoding compression method (which correspond to our level-2 encodings):
with the LPN-based instantiation, the cost of MPFSS _._ FullEval is equal to _k_ times the cost of
the FullEval algorithm of an FSS for point functions, over a domain of size _n_ . The RSD-based
instantiation reduces this cost to _k_ times the cost of the FullEval algorithm of an FSS for point
functions, over a domain of size _n/k_ . We refer the reader to [BCGI18] for further details.
Here, we observe that RSD can also be used to reduce the _size_ of a level-1 encoding. Given
the block structure of the noise pattern, one can simply apply the compression procedure of
Section C.8 separately to each of the _k_ blocks. As each block has length _n/k_ and contains a single

_√_

1, its encoding has size 2 ~~�~~ _n/k_ . Therefore, the total size of the encoding is _k·_ (2 ~~�~~ _n/k_ ) = 2 _n · k_,



_√_
_n/k_ ) = 2



_n/k_ . Therefore, the total size of the encoding is _k·_ (2 ~~�~~



1, its encoding has size 2 _n/k_ . Therefore, the total size of the encoding is _k·_ (2 _n/k_ ) = 2 _n · k_,

as opposed to 2 _[√]_ ~~_n_~~ _· k_ with LPN.



**D.2.2** **Learning Parity with Tensored Noise.**


We now describe a more agressive choice of pattern, which leads to even better efficiency. Note
that unlike LPN or RSD, the assumption that we introduce in this paragraph, although natural,
is new. While we will analyze its resistance to standard attacks, further cryptanalysis is required
to gain confidence in its security. We stress, however, that our assumption as strong connections
to (an can be seen as a natural strenghtening of) well-studied assumptions from the literature;
hence, it appears very plausible.
We focus on compressing level 1 shares in group-based HSS, since they form the bottleneck
of our scheme. Let _⊗_ denote the tensor product between vectors – that is, for length- _n_ vectors
_**a**_ = ( _ai_ ) _i,_ _**b**_ = ( _bi_ ) _i_, _**a**_ _⊗_ _**b**_ denotes the length- _n_ [2] vector with coordinates _aibj_ . We suggest
the following family of distributions for integers _k, n_ (we assume _n_ to be a perfect square for
simplicity):


        - $        - _√_ ~~_n_~~ [�] 2        _Dk,n_ _[⊗]_ [(] _[R]_ [) =] _**x**_ _∈R_ _[n]_ _|_ ( _**a**_ _,_ _**b**_ ) _←_ Ber _k/_ _[√]_ ~~_n_~~ ( _R_ ) _,_ _**x**_ _←_ _**a**_ _⊗_ _**b**_ _._


That is, a sample from _Dk,n_ _[⊗]_ [(] _[R]_ [)][ is the tensor product between two length-] _[√]_ ~~_[n]_~~ [vectors drawn]
from the Bernouilli distribution with rate _k/_ _[√]_ ~~_n_~~ ~~.~~ Such a sample has _k_ [2] non-zero coordinates on
average. Compressing level 1 shares of such samples is straightfoward: the compressed level 1
share simply contains a BGN-EG encryption of _**a**_ over G1 and of _**b**_ over G2. The sample can be


59


reconstructed from the homomorphic properties of BGN-EG by computing the tensor product
_**a**_ _⊗_ _**b**_ over G _t_ . This amounts to a tota _√_ l of 2 _[√]_ ~~_n_~~ BGN-EG ciphertexts, improving over the method of
the previous section by a factor of _k_ . Note, in addition, that this alternative noise distribution

also reduces the number of pairings to be computed by a comparable factor – as it turns out,
in concrete efficiency estimations, the number of pairings is one of the main computational
bottleneck. Therefore, this variants also strongly improves the computational efficiency of the
BCG.
It remains to discuss the security of LPN with noise vectors drawn from this distribution.
Unlike for standard Bernouilli noise, there are specific attacks which are known to apply as
soon as the noise distribution satisfies a low-degree relation (in the present situation, the noise
distribution satisfies a degree-2 relation). To our knowledge, the only attacks which specifically
exploit low-degree relations in the noise distribution are those of Arora and Ge [AG10], which
provide a polynomial-time algorithm solving LPN instances using _N_ _[d]_ samples, where _d_ is the
degree of the relation and _N_ is the dimension. Since we consider much more limited number
of samples ( _O_ ( _N_ )), this attack does not apply in our setting. However, the algebraic structure
of the noise also implies that, unlike standard LPN, this assumption is sensitive to algebraic
attacks (e.g. Gröbner basis attacks); therefore, we will take into account algebraic attacks in
addition to standard attacks on LPN when estimating the concrete security level offered by this
new assumption.


_Relation to MQ and LPN._ If the vector _**x**_ had been sampled from the standard Bernouilli
distribution, the above assumption would be exactly LPN. Furthermore, if the vecto _**x**_ had been
computed as the tensor product of a _uniformly random_ (as opposed to sparse) vector _**a**_ with
itself, this assumption would exactly be the multivariate quadratic (MQ) assumption, a wellstudied assumption [MI88, Wol05, AHI [+] 17] that asserts that it is computationally infeasible to
sove a random system of quadratic equations. Hence, the LPN with tensored noise assumption
can be seen as a natural strengthening of both the MQ assumption and the LPN assumption.


_Cryptanalysis._ Since it shares both the algebraic structure of the MQ assumption, and the sparsity of the LPN assumption, the new assumption introduced above is sensitive to the standard
cryptanalytic attacks that apply to each of these assumptions. We provide an overview of the
existing attacks below.


**–** The most powerful attacks on LPN (in the setting of a limited number of samples and a
low noise rate, which is the case here) are the Gaussian elimination attack (which attempts
to guess a noise-free subset of the coordinates of the vector, and use Gaussian elimination
to invert the corresponding system of equation), the low-weight parity-check attack [Zic17]
(which uses the existence of low-weight codewords in the dual code to establish the existence
of a distinguisher), and the information set decoding (ISD) attack (which uses variants of
Prange’s algorithm [Pra62] to solve the corresponding syndrom decoding problem). We refer
the reader to [BCGI18] for a more detailed overview of these attacks, and bounds on their
computational efficiency. We note that the structure of the noise pattern in our LPN variant
leads to better alternative than the random choice to pick candidate noise-free coordinates of
the vector; we will takes this observation into account when evaluating the cost of the above
attacks. Furthermore, note that the low-weight parity-check attack only applies to LPN over
exponentially large fields (see [Zic17]). Over F2, this attack provably fails.

**–** The most powerful attacks on MQ are the algebraic attacks, such as Gröbner basis attacks.
These attacks exploit the algebraic structure of the system of quadratic equations to generate
many new equations, until sufficient information was gathered to solve the system efficiently.
We note that algebraic attacks such that XL and Gröbner basis attacks do not provide ways
to take advantage of the sparsity of the noise pattern.


Note that we could have alternatively used noise vectors constructed as tensor product
between vectors sampled from the uniform distribution, leading to an MQ-based construction.


60


However, bounding the number of nonzero coefficients (here, by _k_ [2] ) is crucial for the efficiency
of the Convert operation, which relies on an expensive “distributed discrete logarithm” where the
parties must compute a number of multiplications over G _t_ polynomial in the number of nonzero
coefficients of the input vectors.


**D.3** **Changing the Code Matrix**


In this section, we describe alternative choices of code matrices which lead to better computational efficiency for the Expand procedure.


**D.3.1** **Faster Expansion using LDPC Codes.**


Constructing BCG from degree-2 CHSS essentially boils down to using the deg-2 CHSS to
evaluate _N_ [⊺] _BiN_, where _Bi_ is the matrix of the _i_ th output for a target bilinear correlation,
and _N_ is the parity check matrix of an LPN-friendly code. However, this general method has a
downside: in many concrete scenarios, the matrices _Bi_ of the target correlation will be highly
sparse (for example, for building (pseudo)random oblivious transfers, the corresponding matrices
_Bi_ have a single nonzero entry). Yet, _N_ cannot be a sparse matrix: using a code whose parity
check matrix is sparse would render LPN insecure, since this corresponds to decoding an LDPC
code, which can be done in polynomial time. Therefore, the matrices _N_ [⊺] _BiN_ will be dense even
though each _Bi_ might be sparse. This makes the computation wastefull: the computation of
_**z**_ [⊺] 0 _[N]_ [⊺] _[B][i][N]_ _**[z]**_ [1][ requires] _[ O]_ [(] _[n][ ·][ ℓ]_ [) =] _[ O]_ [(] _[α][ ·][ n]_ [2][)][ operations (recall that this is for computing each]
output of the correlation), which becomes quickly inefficient for a large target output size _n_ .
We suggest an alternative approach to bring this computational cost from quadratic to linear.
The main idea is to set _N_ to be the matrix of a low-density parity check code [Gal62, MN96]
(LDPC) instead of a random code. LDPC codes are particularly attractive in our scenario, for
two main reasons.


1. First, the conjectured intractability of LPN instances obtained from the parity check matrix
of an LDPC code (which is a sparse matrix) is a well-established standard assumption, similar
to the assumption made in the seminal work of Alekhnovich [Ale03] on public-key encryption
from LPN.
2. Second, LDPC admit a linear-time, data oblivious encoding algorithm over arbitrary fields [LM10,

KS12], with very good concrete efficiency: encoding with a binary LDPC whose parity-check
matrix has _ℓ_ rows requires at most 4 _·_ _ℓ_ _·_ ( _k_ [¯] _−_ 1) XORs, where _k_ [¯] denotes the row weight of the
parity-check matrix (LPN with highly sparse matrices being conjectured to be intractable,
the value _k_ [¯] can be taken to be very small, say, lower than 10, in practice; see e.g. [ADI [+] 17]).


Of course, LDPC codes are expanding, while we need a compressing matrix; therefore, the
right approach here is to use the transpose _M_ [⊺] of the matrix _M_ of an LDPC code. It might not
be obvious at first sight that the existence of a linear-time algorithm for computing _**x**_ _�→_ _M_ _**x**_
implies the existence of a linear-time algorithm for computing _**x**_ _�→_ _M_ [⊺] _**x**_ . However, this is the
case for linear mappings computed by linear operations: for any such mapping, there is a circuit
of the same size computing the transposed mapping [Bor57, IKOS08], which essentially consists
in reversing the computation while interchanging XORs and fan-out operations.
The second idea is to use the fact that level 1 and level 2 shares of the CHSS of the previous
section directly support homomorphic evaluation of linear functions. Combining the two ideas
gives rise to the following approach for speeding up the Expand procedure of a BCG built out
of this CHSS:


1. Set _N_ to be the transpose of the encoding matrix of an LDPC code whose parity-check
matrix has low row-weight (say, at most 10).


61


2. Given a level 1 encoding _**z**_ 0 sk of a vector _**z**_ 0 (i.e., a BGN-EG encryption of _**z**_ 0 over G _t_ ) and a
                  -                   level 2 encoding ⟪ _**z**_ 1⟫sk of a vector _**z**_ 1 (i.e., sk _t_ _•⟨_ _**z**_ 1 _⟩_ ), homomorphically compute _N_ _**z**_ 0 sk and
                                                       -                                                       ⟪ _N_ _**z**_ 1⟫sk using the transposed version [Bor57] of the linear encoding algorithm of [LM10].
For example, if _R_ = F2 and _k_ [¯] = 5, computing _N_ _**z**_ 0 sk requires 64 _· ℓ_ multiplications over G _t_
                              -                               (16 for each of the 4 components of a BGN-EG ciphertext). The cost of computing ⟪ _N_ _**z**_ 1⟫sk
is negligible in comparison (it involves only additions over Z _q_, which are cheap).
3. Apply the Mult algorithm on _N_ _**z**_ 0 sk and ⟪ _N_ _**z**_ 1⟫sk to compute additive shares of the value
                    -                    ( _N_ _**z**_ 0) [⊺] _Bi_ ( _N_ _**z**_ 1) for each of the matrices _Bi_ . Note that this Mult procedure can now take
advantage of the sparsity of the _Bi_ .


The above alternative method brings down the cost of computing each output of the Expand
procedure from _O_ ( _α · n_ [2] ) to _O_ ( _α · n_ ) in the (classical) situation where the _Bi_ are sparse. As we
will see later in our efficiency estimations for the concrete goal of computing OT correlations,
this easily amounts to an improvement by several orders of magnitude of the cost of this step.


**D.3.2** **Alternative Choices of Code Matrices.**


The choice of LDPC-based codes above is motivated by efficiency considerations. However, alternative choices of code matrices can be envisioned, which lead to different tradeoffs between the
strength of the assumption and the computational efficiency of the matrix-vector multiplication.
(The list given below was taken from [BCGI18])


**–** _MDPC Codes._ A more conservative variant of the above is to rely on MDPC codes (mediumdensity parity-check codes), where the parity-check matrix has row weight _O_ ( _[√]_ ~~_n_~~ ~~)~~ (instead
of constant). MDPC codes have been thoroughly studied, since they are used in optimized
variants of the famous McEliece cryptosystem [MTSB12].

**–** _Quasi-Cyclic Codes._ A second alternative option is to rely on quasi-cyclic codes, which admit
fast (albeit superlinear) encoding algorithms. Quasi-cyclic codes have been recently used to
construct optimized variants of the LPN-based cryptosystem of Alekhnovich and the codebased cryptosystem of McEliece [ABD [+] 16, MBD [+] 18].

**–** _Druk-Ishai Codes._ Another possibility is to rely on the linear-time encodable codes developped by Druk and Ishai in [DI14]. Their construction of linear-time encodable code is essentially a concatenation of good a linear encoding and its transpose, intertwined with random
local mixing. This design strategy leads to codes satisfying the combinatorial properties of
random linear codes (e.g. meeting the Gilbert-Varshamov bound) and do not support efficient decoding, while having a fast (linear-time) encoding algorithm; this makes it a strong
candidate in our scenario.

**–** _Other Codes._ Many other alternatives can be envisioned: since we do not require the code
to have structure, or decoding algorithms. Therefore, any sufficiently good heuristic mixing
strategy (e.g. a strategy based on expander graphs, such as the approach developped by
Spielman in [Spi96]) will likely lead to a secure LPN instance in our setting.


**E** **Group-Based Silent OT/OLE Extension**


In this section, we focus on the task of using PCG to generate (random) oblivious transfer correlations. After motivating the question of computing random OTs with sublinear communication,
which we believe to be a task of fundamental interest, we describe various optimizations of PCG
tailored to this application, perform extensive efficiency estimations, and analyze techniques
to mitigate the inverse-polynomial failure probability of the group-based PCG of the previous
section for this application.


62


**E.1** **Generating ROT-Correlations with Group-Based PCG**


In this section, we study the application of the techniques we developped for the specific (but
fundamental) case of random OT correlations. We provide an extensive efficiency analysis of the
construction.


**E.1.1** **Random Oblivious Transfer.**


A random (bit) oblivious transfer (ROT) is a two party protocol between a sender and a receiver, both with no input. The sender gets as output two uniformly random bits ( _r_ 0 _, r_ 1), and
the receiver gets ( _b, rb_ ), where _b_ is a random bit. Given black-box access to an ROT primitive,
any multiparty functionality can be securely evaluated with information-theoretic security (in
particular, implementing OT from ROT requires exchanging 3 bits), making ROT a core primitive for multiparty computation. One can easily observe that an equivalent formulation of the
ROT functionality is the following: the sender and the receiver both get a respective random
bit ( _s, r_ ), as well as additive shares (over F2) of their product _sr_ . We focus below on the latter
formulation. As ROTs correspond to a degree-2 correlation, they can be generated using a PCG.


**E.1.2** **Optimized Group-Based PCG for ROT Correlations.**


We provide below a self-contained description of the group-based sanitizable PCG of the previous
section, tailored to ROT correlations, using all optimizations that apply in our setting. The
PCG is parametrized with three integers ( _α, k, n_ ), where _α_ is a parameter of the underlying
LPN assumption, _n_ is the target output length, and _k_ is a sparsity parameter. For simplicity, we
assume that _α_ _·_ _n_ is a perfect square. To balance the benefits of optimizations based on revealing
the ElGamal random coins to one of the parties, the parties ( _P_ 0 _, P_ 1) will execute two parallel
instances of the algorithms Gen and Expand below, exchanging their roles in each instance. To
optimize for efficiency, we use an LDPC code matrix, and rely on the LPN with tensored noise
assumption, discussed in Section D.


**– Output.** The two parties get respective outputs ( _**x**_ _,_ _**w**_ 0) _∈_ F [2] 2 _[n]_ and ( _**y**_ _,_ _**w**_ 1) _∈_ F [2] 2 _[n]_ such that
_**w**_ 0 + _**w**_ 1 = _**x**_ _·_ _**y**_, where _·_ denotes the component-wise product over F2.

**–** Setup. Sets pp _[′]_ = ( _q,_ G1 _,_ G2 _,_ G _t, g_ 1 _, g_ 2 _, e_ ) _←_ $ BGN-EG _._ Setup(1 _λ_ ), and compute (pk _,_ sk) _←_
BGN-EG _._ KeyGen(pp _[′]_ ). Compute _gt ←_ _e_ ( _g_ 1 _, g_ 2). Output pp _←_ (pp _[′]_ _,_ pk _, gt_ ) and sk. Let


MPFSS = (MPFSS _._ Gen _,_ MPFSS _._ Eval _,_ MPFSS _._ FullEval)



be a multi-point function secret sharing over Z _q_, and let _G_ be a PRG.

**–** Gen. Set _ℓ_ _←_ _α · n_ . Pick a random seed k0, and _√_ parse _G_ (k0) as (a representation of) a
pair of (pseudo)random sparse vectors ( _**a**_ _,_ _**b**_ ) _∈_ (Z _ℓ_ [)][2][, each with exactly] _[ k]_ [ entries equal]



pair of (pseudo)random sparse vectors ( _**a**_ _,_ _**b**_ ) _∈_ (Z _q_ _ℓ_ [)][2][, each with exactly] _[ k]_ [ entries equal]

_√_ _√_
to 1 and _ℓ_ _−_ _k_ entries equal to 0, together with 2 _ℓ_ (pseudo)random coins ( _**r**_ 1 _,_ _**r**_ 2) _∈_



_q_ _√_

_ℓ_ _−_ _k_ entries equal to 0, together with 2



to _√_ 1 and _ℓ_ _−_ _k_ entries equal to 0, together with 2 _ℓ_ (pseudo)random coins ( _**r**_ 1 _,_ _**r**_ 2) _∈_

(Z _ℓ_ [)][2][. Set] _**[ c]**_ [1] _[←]_ [BGN][-][EG] _[.]_ [Enc][1][(][pk] _[,]_ _**[ a]**_ [;] _**[ r]**_ [1][)] _[,]_ _**[ c]**_ [2] _[←]_ [BGN][-][EG] _[.]_ [Enc][2][(][pk] _[,]_ _**[ b]**_ [;] _**[ r]**_ [2][)][. Pick another ran-]



(Z _q_ _ℓ_ [)][2][. Set] _**[ c]**_ [1] _[←]_ [BGN][-][EG] _[.]_ [Enc][1][(][pk] _[,]_ _**[ a]**_ [;] _**[ r]**_ [1][)] _[,]_ _**[ c]**_ [2] _[←]_ [BGN][-][EG] _[.]_ [Enc][2][(][pk] _[,]_ _**[ b]**_ [;] _**[ r]**_ [2][)][. Pick another ran-]

dom seed k1, and parse the string _G_ (k1) as a (representation of) a (pseudo)random vector _**d**_ 0 _∈_ Z _[ℓ]_ _q_ [with exactly] _[ k]_ [ coordinates equal to 1, and] _[ ℓ]_ _[−]_ _[k]_ [ coordinates equal to 0. We]
denote proj _**x**_ (for any vector _**x**_ _∈_ Z _[n]_ _q_ [) the multi-point function which, on input] _[ i][ ≤]_ _[n]_ [,]
outputs the _i_ ’th coordinate of _**x**_ . Parse sk as (sk1 _,_ sk2 _,_ sk _t_ ) and parse sk _i_ as ( _si, −_ 1) for
_i_ = 1 _,_ 2. Let **proj** _**m**_ _,_ sk _←_ (proj _s_ 1 _s_ 2 _**m**_ _,_ proj _−s_ 1 _**m**_ _,_ proj _−s_ 2 _**m**_ _,_ proj _**m**_ ). Compute ( _**K**_ 0 _,_ _**K**_ 1) _←_
MPFSS _._ Gen(1 _[λ]_ _,_ **proj** _**d**_ 0 _,_ sk). The output of _P_ 0 is (k0 _,_ _**K**_ 0), and the output of _P_ 1 is (k1 _,_ _**c**_ 1 _,_ _**c**_ 2 _,_ _**K**_ 1).

**–** Expand. Let _**d**_ 1 _←_ _**a**_ _⊗_ _**b**_ . _P_ 0 and _P_ 1 expand their respective FSS keys _**K**_ 0 and _**K**_ 1 using
MPFSS _._ FullEval, getting _⟨_ sk _t ·_ _**d**_ 0 _⟩_ (i.e., additive shares over Z _q_ of sk _t ·_ _**d**_ 0).




_• P_ 1 computes _**c**_ _t ←_ _e_ ( _**c**_ 1 _,_ _**c**_ 2) _∈_ G [4] _t_ _[ℓ]_ [.]



63


_• P_ 0 expands k0 into ( _**a**_ _,_ _**b**_ _,_ _**r**_ 1 _,_ _**r**_ 2) using _G_, and computes _**c**_ _t_ directly from _**a**_ _,_ _**b**_ _,_ _**r**_ 1 _,_ _**r**_ 2 as


_**c**_ _t,_ 0 _←_ _e_ ( _g_ 1 _, g_ 2) _**[r]**_ [1] _[⊗]_ _**[r]**_ [2]

_**c**_ _t,_ 1 _←_ _e_ ( _g_ 1 _, h_ 2) _**[r]**_ [1] _[⊗]_ _**[r]**_ [2] _· e_ ( _g_ 1 _, g_ 2) _**[r]**_ [1] _[⊗]_ _**[b]**_

_**c**_ _t,_ 2 _←_ _e_ ( _h_ 1 _, g_ 2) _**[r]**_ [1] _[⊗]_ _**[r]**_ [2] _· e_ ( _g_ 1 _, g_ 2) _**[r]**_ [2] _[⊗]_ _**[a]**_

_**c**_ _t,_ 3 _←_ _e_ ( _h_ 1 _, h_ 2) _**[r]**_ [1] _[⊗]_ _**[r]**_ [2] _· e_ ( _h_ 1 _, g_ 2) _**[r]**_ [1] _[⊗]_ _**[b]**_ _· e_ ( _g_ 1 _, h_ 2) _**[r]**_ [2] _[⊗]_ _**[a]**_ _· e_ ( _g_ 1 _, g_ 2) _**[d]**_ [0]


Note that all pairings involved can be precomputed in a one-time setup phase.

_•_ Let _N ∈_ Z _[ℓ]_ _q_ _[×][n]_ be the transpose of the matrix of a binary LDPC code (each entry of _N_ is
viewed as a 0 or a 1 over Z _q_ ). Both parties locally compute ( _⟨_ sk _t · d_ _[′]_ _i_ _[⟩]_ [)] _[i][≤][n][ ←⟨]_ [sk] _[t][ ·][ N]_ _**[d]**_ [0] _[⟩]_
and homomorphically multiply the plaintext of _**c**_ _t_ by _N_, obtaining a list of _n_ ciphertexts
( _c_ _[′]_ _i_ [)] _[i][≤][n]_ [ over][ G] _t_ [4][. Note that this multiplication by] _[ N]_ [ can be done by homomorphically]
evaluating on _**c**_ _t_ the “transposed version” of the circuit of [LM10], which contains only
XOR gates, interpreting all XOR gates as a modular addition over Z _q_ (as no modular
reduction occurs, the parties will obtain the correct result by locally reducing their final
additive shares modulo 2).

_• P_ 0 locally sets _**x**_ _←_ _N ·_ _**d**_ 0 mod 2, and _P_ 1 expands k1 into _**d**_ 1 and locally sets _**y**_ _←_
_N ·_ _**d**_ 1 mod 2.

_•_ For _i_ = 1 to _n_, the parties compute the Mult algorithm by sequentially evaluating
Pair( _c_ _[′]_ _i_ _[,][ ⟨]_ [sk] _[t][ ·][ d][′]_ _i_ _[⟩]_ [) =] _[ {][g]_ _t_ _[z][i][}]_ [, where] _[ z][i]_ [ is an integer value satisfying] _[ z][i]_ [ =] _[ x][i][ ·][ y][i]_ [ mod 2][, and]
Convert(� _gt_ _[x][i][·][y][i]_    - _, δ_ ) = _⟨zi⟩_ (where the equality holds except with some failure probability
_δ_ independently for each share). Finally, the parties locally convert these integer shares
into F2-shares by reducing _⟨zi⟩_ modulo 2, getting _⟨xi · yi⟩_ mod 2. We denote by _**w**_ _σ_ the
length- _n_ vector of shares obtained by party _Pσ_ .


**E.2** **Efficiency Estimations**


We now estimate the concrete efficiency of the group-based bilinear correlation generator, using
all the optimizations described in the previous section, for generating a large number of (bit)
ROT correlations. Cost estimates for other useful types of correlations (e.g. Beaver triples) can
be easily extrapolated from our detailed estimations. We note that, although we will carefully
evaluate the resistance to known attacks of the assumptions underlying some of our optimizations, these assumptions remain new and deserve further exploration. The efficiency estimations
given in the upcoming sections are based on the concrete parameters designed so that known
attacks take at least 2 [80] steps to break the underlying assumptions; if improved cryptanalytic
methods are discovered, our efficiency estimations should be revised accordingly.


**E.2.1** **Choices of Curve.**


We estimate the costs of sanitizable PCG for random OT using the benchmark numbers of the
Miracl library. [16] All benchmarks are executed on one core of a 2.4 GHz Intel i5 520M processor.
We consider two pairing-friendly elliptic curves for type-3 pairings:


**–** An MNT curve with a 160-bit modulus _q_ and an embedding degree equal to 6. A G1 (resp.
G2 _,_ G _t_ ) element is 160-bit (resp. 320-bit, 960-bit) long. The Miracl documentation reports
the following timings over this curve: 1,9ms for a pairing, and 0,24ms for an exponentiation
over G _t_ = F _q_ 6 (which approximately corresponds to 6 _∗_ 160 _∗_ 1 _._ 5 = 1440 multiplications over
G _t_ ). This curve is conjectured to provide 80 bits of security and is a good choice of curve to
minimize the seed size (as each group element is only 160 bits long).


16 `[https://libraries.docs.miracl.com/miracl-explained/benchmarks](https://libraries.docs.miracl.com/miracl-explained/benchmarks)`


64


**–** A Cocks-Pinch curve with a 512-bit modulus _q_ and an embedding degree equal to 2. A G1
or G2 (resp. G _t_ ) element is 512-bit (resp. 1024-bit) long. The Miracl documentation reports
the following timings over this curve: 1,14ms for a pairing, and 0,12ms for an exponentiation
over G _t_ = F _q_ 2 (which approximately corresponds to 2 _∗_ 512 _∗_ 1 _._ 5 = 1536 multiplications over
G _t_ ). This curve is conjectured to provide 80 bits of security and is a good choice of curve to
minimize the computational overhead (as pairings and exponentiations are respectively 40%
and 50% less expensive than over an MNT curve, for the same security level).


**E.2.2** **Matrix Multiplication and Gaussian Elimination.**


Most attacks on the LPN assumption and its variants require computing matrix multiplications,
and solving systems of linear equations, for large matrices and systems. To estimate properly
the efficiency of these attacks, we overview in this section the state-of-the-art regarding matrix
multiplication and resolution of linear system.
It is well known, and was first shown in [BH74], that solving linear systems of equations is
reducible to matrix multiplication: if _n × n_ matrix multiplication can be computed in _O_ ( _n_ _[ω]_ ),
then solving _A_ _**x**_ = _**y**_ for an _n × n_ matrix _A_ can be done in time _O_ ( _n_ _[ω]_ ). More precisely, if _M_ ( _n_ )
denotes the time for multiplying two _n × n_ matrices, then solving _A_ _**x**_ = _**y**_ for an _n × n_ matrix
_A_ requires less than 2 _· M_ ( _n_ ) operations. Therefore, we focus in this overview on the cost of
multiplying two matrices. We denote by _ω_ the smallest possible value such that the time for
multiplying two _n × n_ matrices is in _O_ ( _n_ _[ω]_ ).
Matrix multiplication in subcubic time was believed to be impossible, until the seminal paper
of Strassen in 1969 [Str69], which described an algorithm using _n_ [log][2][(7)] multiplications. This
result was followed from decades of improvement, culminating with the Coppersmith-Winograd
algorithm [CW90] which established _ω ≤_ 2 _._ 375477, followed by subsequent improvements, with
the current record being held by Le Gall’s algorithm [LG12] ( _ω ≤_ 2 _._ 3728639). However, all
the results starting with the work of Coppersmith-Winograd suffer from the _curse of recursion_ :
they involve complex nested recursive calls, which make the constant term of the algorithms
prohibitively large – so large that no such method has ever be implemented as of today, nor is
believed to provide any concrete speedup for matrices of any realistic size [Pan18]. All known
implementations of subcubic matrix multiplication algorithms rely on the original algorithm of
Strassen, or it’s improvement by Winograd (which reduces the number of additions, but leaves
the asymptotic complexity unchanged) [Fis74].
It is hard to estimate what exactly is the current optimal algorithm for _feasible_ matrix
multiplication, since it largely depends on the specific features of the problem at hand. To
our knowledge, the smallest matrix multiplication exponent for which matrix multiplication
has feasible constants is 2 _._ 7760 [Kap04]. The algorithm of Kaporin [Kap04] was implemented
and compared with the algorithms of Winograd and Strassen (which have exponents log2(7) _≈_
2 _._ 807) for _n × n_ matrices of size up to _n_ = 2 _·_ 10 [5] . At these sizes, Kaporin’s algorithm had a
running time within a factor 1 _._ 05 to that of Strassen and Winograd’s algorithm. It follows that a
sufficiently good upper bound on the running time of a matrix multiplication algorithm is given
by the cost _n_ [log][2][(7)] of Winograd’s algorithm (note that over F2, where additions cost as much
as multiplications, the number of bit operations for Winograd’s algorithm is 5 _· n_ [log][2][(7)] ).
While the previous results establish the best known running time for multiplying two _n × n_
arbitrary matrices, our optimized group-based PCG involves _structured_ matrices – typically,
LDPC matrices, which have a sparse parity-check matrix. Multiplying an LDPC matrix with an
arbitrary matrix can be done faster than through general matrix multiplication: the linear-time
LDPC encoding algorithm of [LM10] allows to compute an LDPC encoding _A_ _**x**_ of a vector _**x**_
with code matrix _A_ in time 4 _d · n_, where _d_ is the maximum number of non-zero elements in the
parity check matrix of _A_ . This directly lead to a matrix multiplication algorithm in time 4 _d · n_ [2] .
While it is not entirely clear wether the linear system solver from matrix multiplication of [BH74]
preserves the LDPC structure of the matrix through the algorithm (since the algorithm involves


65


recursive calls to the matrix multiplication functionality on blocks of _A_ ), it is plausible that
it can be modified to maintain this structure. Therefore, we will conservatively assume below,
when estimating the resistance of our scheme to known attacks, that the cost of solving a system
of linear equations is lower bounded by 4 _d · n_ [2] .


**E.2.3** **Parameters for the LPN with Tensored Noise Assumption.**


We discuss choices of parameters for the LPN with tensored noise assumption, by evaluating
the efficiency of known attacks on this assumption. We consider LPN with tensored noise with
_k_ [2] noisy coordinates, dimension ( _α −_ 1) _n_, and number of samples _αn_ . Note that we use LPN
with tensored noise over F2, therefore the low-weight parity-check attack does _not_ apply to our
setting (see [Zic17]).




**– Gröbner Basis Attack.** We first evaluate the resistance of LPN with tensored noise against
Gröbner basis attacks. These attacks to not directly depend on the number of noisy coordinates, but mainly on the compression factor (recall that we extend _[√]_ ~~_αn_~~ bits to _αn_ bits,
before compressing the output to _n_ bits). Hence, these attacks will allow us to determine the
optimal value of _α_ for a given _n_ .
As is always done to study the complexity of Gröbner basis attacks, we conjecture that the
corresponding system of quadratic equations is semi-regular. This conjecture is supported by
the fact that the proportion of semi-regular systems goes to 1 when the number of unknown
grows [Bar04, Frö85]. By [BFSY05, Theorem 1], the average complexity of a Gröbner basis
attack is given by

             - _t_              - _ω_

_,_

_d_ reg




- _ω_
_,_



where _t_ = _[√]_ ~~_αn_~~ is the number of unknowns in the system, _ω_ is the matrix multiplication
exponent (which we assume equl to 2 _._ 8), and _d_ reg is the regularity degree, which was shown
in [BFSY05] to be upper bounded by



_−n_ + _[t]_




_[t]_ _[t]_

2 [+] 2



2




~~�~~



( _n/t_ ) _·_ ( _n/t_ + 2) _._



2( _n/t_ ) [2] _−_ 10 _n/t −_ 1 + 2( _n/t_ + 2) ~~�~~



Solving the above under the condition that the Gröbner basis attacks requires at least 2 [80]

operations, we get the following:

_•_ For _n <_ 2 [26], the regularity degree _d_ reg is equal to 3, and the smallest value of _α_ which
allows to stretch _[√]_ ~~_αn_~~ bits to _n_ bits is _α_ = 24.

_•_ For _n ≥_ 2 [26], the regularity degree _d_ reg is equal to 2, and the smallest value of _α_ which
allows to stretch _[√]_ ~~_αn_~~ bits to _n_ bits is _α_ = 16.

**– Gaussian Elimination Attack.** For the standard LPN assumption with _k_ noisy coordinates, the Gaussian elimination attack requires on average (1 _/_ (1 _−_ _k/_ ( _αn_ ))) [(] _[α][−]_ [1)] _[n]_ iterations,
where the adversary must invert an (( _α −_ 1) _n_ ) _×_ (( _α −_ 1) _n_ ) matrix, which takes time at
least (( _α −_ 1) _n_ ) [2] _[.]_ [8] using Strassen’s matrix multiplication algorithm. However, since we use
an LDPC code, which admits a linear-time encoding algorithm, the linear system can be
solved more efficiently: the linear-time encoding algorithm of [LM10] gives matrix-vector
multiplication in time (2 _α −_ 1) _· d · n_, where _d_ is the sparsity parameter of the parity-check
matrix of the code, which we denote _d_ ; hence, multiplying and LDPC code matrix with an
arbitrary square matrix takes time at most _α_ (2 _α_ _−_ 1) _·_ _d_ _·_ _n_ [2] . Using the reduction from matrix
multiplication to solving systems of linear equations [BH74], this leads to an algorithm for
solving the system in time lower-bounded by _α_ (2 _α −_ 1) _· d · n_ [2] (see the discussion in the
previous section).
For LPN with tensored noise, which involves a noise vector with _k_ [2] noisy coordinates, there
is a better way to sample the candidate noise-free subvector: as the vector is of the form
_**x**_ = _**a**_ _⊗_ _**a**_ for a _k_ -sparse vector _**a**_, it suffices to divide _**x**_ into _[√]_ ~~_αn_~~ blocks of _[√]_ ~~_αn_~~ coordinates


66


each. Note that each block is either equal to _**a**_ or to the all-0 vector. Hence, the adversary
can simply guess ( _α −_ 1) _n/_ _[√]_ ~~_αn_~~ noise-free blocks (there are _[√]_ ~~_αn_~~ _−_ _k_ such blocks), which
requires on average (1 _/_ (1 _−_ _k/_ _[√]_ ~~_αn_~~ ~~)~~ ) [(] _[α][−]_ [1)] _[n/][√]_ ~~_[αn]_~~ iterations. Therefore, a lower bound on the
bit-security of the LPN with tensored noise instance with respect to the Gaussian elimination
attack is given as



_._



�(( _α−_ 1) _n_ ) _/_ _[√]_ ~~_αn_~~ 
_· α_ (2 _α −_ 1) _· d · n_ [2]



log2



��
1
1 _−_ _k/_ ~~_[√]_~~ ~~_αn_~~




**– Parity-Check Attack.** A noisy codeword can be distinguished from random by multiplying
it with a parity-check vector. Over F2, a random vector will pass the parity-check with
probability exactly 1 _/_ 2. However, a noisy codeword will pass the check with probability 1
conditioned on all the noisy coordinates corresponding to zero-entries of the parity-check
vector, and with probability 1 _/_ 2 otherwise. Therefore, parity-check vectors allows for a nontrivial distinguishing advantage.
Since the dual code has distance at most ( _α −_ 1) _n_ in our setting, there always exists as
parity check vector with at most ( _α −_ 1) _n_ + 1 non-zero coordinates, which is obtained by
writing the dual matrix in systematic form, and using it to encode an arbitrary low-weight
vector. This way, up to _αn −_ ( _α −_ 1) _n −_ 1 = _n −_ 1 coordinates are guaranteed to be zero;
the remaining ( _α −_ 1) _n_ + 1 coordinates being over F2 in our setting, they will contain on
average (( _α −_ 1) _n_ + 1) _/_ 2 zeroes. Therefore, we assume that the adversary can compute at
no cost (since they can be preprocessed given only the code matrix) a list of parity-check
vectors of weight (( _α −_ 1) _n_ + 1) _/_ 2. Under the heuristic that the _k_ [2] noisy coordinates are
randomly spread over the noise vector, a parity-check vector will have only zeroes in positions
corresponding to the noisy coordinates with probability




- _k_ 2
_._




- _αn −_ (( _α −_ 1) _n_ + 1) _/_ 2


_αn_




- _k_ 2 - _αn_ + _n −_ 1
=

2 _αn_



After each iteration, the adversary must compute a parity-check with a vector of weight
(( _α −_ 1) _n_ + 1) _/_ 2, which costs him (( _α −_ 1) _n_ + 1) _/_ 2 arithmetic operations. Therefore, the
(logarithm of the) average computational cost of the parity check attack is given by




- _k_ 2 [�]



log2




( _α −_ 1) _n_ + 1  - _αn_

_·_
2 _αn_ + _n −_ 1



_._



Finally, observe that the heuristic assumption that the noise is randomly spread is clearly
false here: since the noise vector was computed as a tensor product between low-weight
vectors, it satisfies a block structure, where each block is of length _[√]_ ~~_αn_~~ ~~,~~ _k_ blocks are noisy
and the remaining are noise-free, and the noise pattern is the same accross the noisy blocks.
However, to exploit this known structure, the adversary would have to guess the position
of noise-free blocks, and then to find a parity check vector with a large number of non-zero
coordinates belonging to these noise-free blocks. While this can be done in a preprocessing
phase, it requires a prohibitive amount of preprocessing: we estimated that, in our range of
parameters, the adversary would need to compute at least 2 [200] operations when preprocessing
the parity-check vectors to get a noticeable speedup in the online attack. Therefore, we do
not consider speedups from preprocessing parity-check vectors in our estimations, but note
that finding imoproved preprocessing techniques is a possible direction that deserves further
study toward getting a better cryptanalysis of our assumption using parity-check attacks.

**– Information Set Decoding Attack.** We now turn our attention to the ISD attack. Many
variants of the attack have been developed in the past years, and the asymptotic costs
of these attacks are often non-trivial to estimate. However, in our parametter setting, the
noise rate _k_ [2] _/_ ( _αn_ ) is small, and the advantages of the variants of the original algorithm of


67


Prange [Pra62] vanish in this situation, as shown in the analysis of [TS16]. We will therefore
focus on bounding the cost of the original algorithm of Prange; since we will find this attack
to have much worst performances than the Gaussian elimination attack, this leaves a large
security gap. To make conservative estimates, we evaluate the cost of the attack against a
_standard_ LPN instance with _k_ noisy coordinates; that is, we make the assumption that due
to their structure, the _k_ [2] noisy coordinates of LPN with tensored noise do not provide additional security compared to _k_ (random) noisy coordinates. We rely on the detailed concrete
efficiency analysis of ISD given in [HOSS18], which shows that the bit-security of the LPN
instance with respect to Prange’s algorithm is upper-bounded by



log2



�� _αn_ - _k_ _·_ 8 _d ·_ ( _n −_ 1) [2]

~~�~~ _n−_ 1 ~~�~~
_k_



_,_



where 4 _d ·_ ( _n −_ 1) [2] denotes our conservative estimate of the cost of solving a linear system of
equations given by an LDPC code with parity-check matrix of row-weight _d_ (see the discussion
in the previous section).


**E.2.4** **Optimal Parameters.**


We use the above analysis to choose optimal parameters to achieve 80 bits of security against
Gröbner basis attacks, Gaussian elimination, parity checks, and ISD. The optimal parameters
are represented on Table 5.


_n_ 2 [16] 2 [18] 2 [20] 2 [22] 2 [24] 2 [26] 2 [28] 2 [30]


_α_ 24 24 24 24 24 16 16 16
_k_ 25 23 20 17 14 12 9 8


**Table 5.** Optimal parameters _k_ and _α_ for various choices of _n_ . We consider the cost of attacking the LPN with
tensored noise assumption, instantiated with an LDPC code matrix, using either Gaussian elimination, Gröbner
basis attacks, ISD, or parity-check attacks. We set the sparsity parameter of the parity-check matrix to _d_ = 10.


**E.2.5** **Size of the Seeds.**


We estimate below the size of the seeds stored by _P_ 0 and _P_ 1, using the MPFSS of [BCGI18].
For concreteness, we consider an AES-based implementation of the PRGs, and instantiate the
elliptic curve with the two candidates described above. The PRG seeds k0 _,_ k1 are _λ_ -bit long,
while _|_ _**K**_ _√_ 0 _|_ = _|_ _**K**_ 1 _|_ = _k ·_ ( _⌈_ log _ℓ⌉·_ ( _λ_ + 2) + _λ_ + _⌈_ log _q⌉_ ) with _ℓ_ = _α · n_ . Each _**c**_ _i_ for _i_ = 1 _,_ 2 is of
size 2 _·_ _ℓ_ _· |_ G _i|_ . Therefore:


**–** The total size of _P_ 0’s seed is _λ_ + _√ k ·_ ( _⌈_ log _ℓ⌉·_ ( _λ_ + 2) + _λ_ + _⌈_ log _q⌉_ ) bits.

**–** The total size of _P_ 1’s seed is 2 _·_ _ℓ_ _·_ ( _|_ G1 _|_ + _|_ G2 _|_ ) + _λ_ + _k ·_ ( _⌈_ log _ℓ⌉·_ ( _λ_ + 2) + _λ_ + _⌈_ log _q⌉_ ) bits.


Concretely, consider a target number of 2 [27] ROTs, which are computed using two parallel
instances of the above PCG for _n_ = 2 [26] where _P_ 0 and _P_ 1 exchange their roles in the two instances
(to balance the storage load), and set _α_ = 2 (a smaller _α_ would further reduce the storage, but
at the cost of increasing _k_, which has an impact on the computational efficiency of the Convert
procedure). Then, using the MNT curve, each party stores a seed of length 3 _._ 76 Megabytes,
which on average amounts to 4 _._ 3 ROT produced per bit of the seed. Using the Cocks-Pinch
curve, the seed size increases to 8 Megabytes (2 ROT produced per bit stored). We represent on
Table 6 the seed size (in Megabytes) for generating _n_ ROT correlations, for various values of _n_ .


68


_n_ 2 [17] 2 [19] 2 [21] 2 [23] 2 [25] 2 [27] 2 [29] 2 [31]


MNT Curve 0 _._ 16 0 _._ 30 0 _._ 59 1 _._ 16 2 _._ 31 3 _._ 76 7 _._ 50 15 _._ 0
ROT/bit (MNT) 0 _._ 10 0 _._ 21 0 _._ 42 0 _._ 86 1 _._ 73 4 _._ 25 8 _._ 52 17 _._ 1
Cocks-Pinck Curve 0 _._ 33 0 _._ 63 1 _._ 24 2 _._ 47 4 _._ 91 8 _._ 01 16 _._ 0 32 _._ 0
ROT/bit (Cocks-Pinch) 0 _._ 05 0 _._ 10 0 _._ 20 0 _._ 41 0 _._ 81 2 _._ 00 4 _._ 00 8 _._ 00


**Table 6.** Seed size for generating _n_ ROT correlations. We consider a balanced version of the group-based PCG,
where the parties obtain seed of the same length by exchanging their roles in two parallel PCG instances. We
set _λ_ to 128, and choose the values of _α_ and _k_ according to Table 5. We provide the size (in Megabytes) of the
seeds using both an MNT curve and a Cocks-Pinch curve, whose parameters are described at the beginning of
Section E.2. The row ROT/bit (curve) denotes the number of ROT produced per bit of the seed stored, i.e., the
bit size of the seed divided by _n_, using the curve curve.


**E.2.6** **Efficiency of Expand.**


We now estimate the computational cost of each step of the Expand procedure. In this section,
we assume that the column-weight _d_ of the parity-check matrix of _N_ is upper bounded by 10,
which was shown to be reasonable choice in [ADI [+] 17]. With this parameters, computing the map
_**m**_ _�→_ _N ·_ _**m**_ requires 10 _·_ (2 _α −_ 1) _n_ XORs using the linear-time algorithm of [LM10, KS12] (see
e.g. [BCGI18]). For each of the two parallel executions of Expand, the parties do the following
(we ignore some costs which are several orders of magnitude smaller than all other costs, e.g.
computing _**x**_ _←_ _N ·_ _**d**_ 0 and _**y**_ _←_ _N ·_ _**d**_ 1):


1. Both parties execute 4 instances of MPFSS _._ FullEval.
2. _P_ 0 computes 4 _ℓ_ pairings (to build _**c**_ _t_ from _**c**_ 1 _,_ _**c**_ 2).
3. _P_ 1 computes 9 _ℓ_ exponentiations over G _t_ (to build _**c**_ _t_ from ( _**a**_ _,_ _**b**_ _,_ _**r**_ 1 _,_ _**r**_ 2)).
4. Both parties compute 40 _·_ (2 _α −_ 1) _n_ multiplications over G _t_ (to build ( _c_ _[′]_ _i_ [)] _[i][≤][n]_ [ from] _**[ c]**_ _[t]_ [ and]
_N_ ; the XORs are evaluated as homomorphic additions over Z _q_, and each such homomorphic
addition requires the term-by-term product of two ciphertexts, hence 4 multiplications over
G _t_ ).
5. The parties execute _n_ distributed discrete logarithms (the Convert algorithm). The efficiency
of this step depends on the average size of the values _zi_ such that Pair( _c_ _[′]_ _i_ _[,][ ⟨]_ [sk] _[t][ ·][ d][′]_ _i_ _[⟩]_ [) =] _[ {][g]_ _t_ _[z][i][}]_ [.]
Concretely, each _zi_ is the product of the _i_ ’th coordinates of _N ·_ _**d**_ 0 and _N ·_ _**d**_ 1. Assuming
that _N_ has average row-weight _ℓ/_ 2, and since _**d**_ 0 has _k_ non-zero entries (all equal to 1) and
_**d**_ 1 = _**a**_ _⊗_ _**b**_ has _k_ [2] non-zero entries (all equal to 1), the average size of _zi_ is _k_ [3] _/_ 4. Using the
optimized DDLOG of [DKK18] with average payload _k_ [3] _/_ 4, the failure probability _δ_ of the
output is approximately _δ_ = _B_ ( _T_ ) _· k_ [3] _/_ (4 _· T_ [2] ), where _T_ is the number of multiplications
over G _t_ performed by each party, and _B_ ( _T_ ) is a value below 2 [10] _[.]_ [4] (optimal values of _B_ for
various _T_ are given in Table 1 of [DKK18]). We represent on Table 7 the failure _δ_ obtained
for various output lengths _n_ and number of multiplications _T_, using the values _B_ ( _T_ ) from
Table 1 of [DKK18].


_n_ 2 [16] 2 [18] 2 [20] 2 [22] 2 [24] 2 [26] 2 [28] 2 [30]


_T_ = 2 [13] 2 _[−]_ [5] _[.]_ [7] 2 _[−]_ [6] _[.]_ [0] 2 _[−]_ [6] _[.]_ [6] 2 _[−]_ [7] _[.]_ [3] 2 _[−]_ [8] _[.]_ [2] 2 _[−]_ [8] _[.]_ [8] 2 _[−]_ [10] _[.]_ [1] 2 _[−]_ [10] _[.]_ [6]

_T_ = 2 [14] 2 _[−]_ [7] _[.]_ [6] 2 _[−]_ [8] _[.]_ [0] 2 _[−]_ [8] _[.]_ [6] 2 _[−]_ [9] _[.]_ [3] 2 _[−]_ [10] _[.]_ [1] 2 _[−]_ [10] _[.]_ [8] 2 _[−]_ [12] _[.]_ [0] 2 _[−]_ [12] _[.]_ [5]

_T_ = 2 [15] 2 _[−]_ [9] _[.]_ [5] 2 _[−]_ [9] _[.]_ [9] 2 _[−]_ [10] _[.]_ [5] 2 _[−]_ [11] _[.]_ [2] 2 _[−]_ [12] _[.]_ [0] 2 _[−]_ [12] _[.]_ [7] 2 _[−]_ [14] _[.]_ [0] 2 _[−]_ [14] _[.]_ [5]

_T_ = 2 [16] 2 _[−]_ [11] _[.]_ [5] 2 _[−]_ [11] _[.]_ [9] 2 _[−]_ [12] _[.]_ [5] 2 _[−]_ [13] _[.]_ [2] 2 _[−]_ [14] _[.]_ [0] 2 _[−]_ [14] _[.]_ [7] 2 _[−]_ [15] _[.]_ [9] 2 _[−]_ [16] _[.]_ [4]

_T_ = 2 [17] 2 _[−]_ [13] _[.]_ [8] 2 _[−]_ [14] _[.]_ [0] 2 _[−]_ [14] _[.]_ [6] 2 _[−]_ [15] _[.]_ [3] 2 _[−]_ [16] _[.]_ [2] 2 _[−]_ [16] _[.]_ [8] 2 _[−]_ [18] _[.]_ [1] 2 _[−]_ [18] _[.]_ [6]

_T_ = 2 [18] 2 _[−]_ [15] _[.]_ [6] 2 _[−]_ [16] _[.]_ [0] 2 _[−]_ [16] _[.]_ [6] 2 _[−]_ [17] _[.]_ [3] 2 _[−]_ [18] _[.]_ [1] 2 _[−]_ [18] _[.]_ [8] 2 _[−]_ [20] _[.]_ [0] 2 _[−]_ [20] _[.]_ [5]


**Table 7.** Failure probability _δ_ for various choices of _n, T_ and an average size _k_ [3] _/_ 4 of the exponent. The value
_B_ ( _T_ ) is chosen according to Table 1 of [DKK18]. We choose the optimal value of _k_ for each value of _n_ according
to Table 5.


69


We now estimate the average running time of each of the 5 steps outlined above, for both
MNT and Cocks-Pinch elliptic curves, using the benchmark values of the Miracl library (which
are obtained on one core of a 2.4 GHz Intel i5 520M processor).


1. Using the analysis of [BCGI18] for an evaluation of MPFSS _._ FullEval on one core of a standard laptop, using either _α_ = 16 or _α_ = 24, the running time of this step per ROT produced is bounded above by 1 _µs_ . Note that we use a rough upper bound on the estimations
of [BCGI18]; the average cost per ROT of this step being essentially negligible compared to
the total average cost, these imprecise estimates have no significant impact on the overall
estimated running time.

2. A pairing computation takes 1.9ms on an MNT curve, hence the average cost of step 2 is
4 _∗_ 1 _._ 9 _ℓ/n_ = 7 _._ 6 _α_, which amounts to 182 _._ 4ms per ROT for _α_ = 24, and 121 _._ 6 _ms_ per ROT
for _α_ = 16. On a Cocks-Pinch curve, where a pairing takes 1 _._ 14ms, the cost is reduced to
107ms per ROT with _α_ = 24 (resp. 71 _._ 7 _ms_ with _α_ = 16). Note that only one of the parties
performs this step, hence the cost per party is reduced by a factor 2 when balancing over
two parallel instanced of PCG where the parties exchange their roles.
3. An exponentiation over G _t_ takes 0.24ms on an MNT curve (resp. 0.12ms on a Cocks-Pinch
curve), hence the average cost of step 3 is 9 _∗_ 0 _._ 24 _ℓ/n_ = 51 _._ 8ms using _α_ = 24, or 34 _._ 6 _ms_
with _α_ = 16 over an MNT curve (resp. 25 _._ 9ms or 17 _._ 3ms over a Cocks-Pinch curve). As only
_P_ 1 executes this step, the same observation as in the previous step applies, and the average
cost per party can be reduced by a factor 2.
4. An exponentiation amounts to about 1440 multiplications over G _t_ for the MNT curve, and
to about 1536 multiplications over G _t_ for the Cocks-Pinch curve. Therefore, the average cost
of step 4 is (1 _/_ 1440) _∗_ 64 _∗_ 0 _._ 24 _ℓ/n_ = 0 _._ 26ms or 0 _._ 17ms using _α_ = 24 _,_ 16 for the MNT curve,
and 0 _._ 12ms, 0 _._ 08ms for the Cocks-Pinch curve.
5. This step requires _T_ multiplications over G _t_ per party, where the choice of _T_ determines the
failure probability of each ROT (see Table 7). The estimated cost per ROT (in millisecond) of
this step for both the MNT and the Cocks-Pinch curve, for various values of _T_, is represented
on Table 8.


_T_ 2 [13] 2 [14] 2 [15] 2 [16] 2 [17] 2 [18]


MNT 1 _._ 4ms 2 _._ 7ms 5 _._ 5ms 10 _._ 9ms 21 _._ 8ms 43 _._ 7ms
CP 0 _._ 6ms 1 _._ 3ms 2 _._ 6ms 5 _._ 1ms 10 _._ 2ms 20 _._ 4ms


**Table 8.** Running time in milliseconds of the distributed discrete logarithm for various choices of _T_ and an
average size _k_ [3] _/_ 4 of the exponent. The value _B_ ( _T_ ) is chosen according to Table 1 of [DKK18]. We choose the
optimal value of _k_ for each value of _n_ according to Table 5. The running time of exponentiations is taken from the
benchmark of the Miracl library, ran on one core of a 2.4 GHz Intel i5 520M processor. MNT denotes a 160-bit
MNT curve, and CP denotes a 512-bit Cocks-pinch curve.


In Table 9, we represent the total running time per parties (in millisecond) when averaged
over two parallel executions of the PCG (e.g. for a target output size _n_ = 2 [21], the parties execute
two parallel instances of PCG with output size 2 [20], exchanging their roles in each instance). We
set _α_ = 2. We illustrate the cost on an instance for concreteness: to compute 2 [23] ROT, setting
_α_ = 2 and _T_ = 2 [15] gives an average running time of 15ms per party over an MNT curve, where
each ROT is correct except with probability 1 _−_ 2 _[−]_ [9] _[.]_ [4] (hence, one out of 676 ROT will be faulty
on average). The storage overhead (i.e., the size of the seed stored by each party) amounts to
0.35 bits per ROT.


70


_T_ 2 [13] 2 [14] 2 [15] 2 [16] 2 [17] 2 [18]


MNT, _α_ = 24 118.8ms 120.1ms 122.8ms 128.3ms 139.2ms 161.1ms
MNT, _α_ = 16 96.5ms 97.8ms 100.5ms 106ms 116.9ms 138.8ms
CP, _α_ = 24 84.8ms 86.1ms 88.8ms 94.3ms 99.4ms 109.6ms
CP, _α_ = 16 62.9ms 64.2ms 66.9ms 72.4ms 77.5ms 87.7ms


**Table 9.** Average running time per ROT (in milliseconds) of the entire Expand procedure, on one core of a 2.4
GHz Intel i5 520M processor, using the benchmark of the Miracl library. MNT denotes a 160-bit MNT curve,
and CP denotes a 512-bit Cocks-pinch curve.


**E.3** **Extension to OLE over Larger Rings**


Our optimized group-based PCG for OT correlations can be readily used to generate OLE
correlations over larger (polynomial size) rings. Since the dominant cost in the seed size comes
from the _O_ ( _[√]_ ~~_n_~~ ~~)~~ BGN ciphertexts, increasing the ring size (which means increasing the size of
the encrypted plaintexts) does not significantly change the seed size.
However, generalizing to larger rings comes at a cost in terms of computational efficiency.
While the number of pairing operations, which is the main efficiency bottleneck for generating
OT correlations, remains the same, the cost of the distributed discrete logarithm procedure
scales linearly with the increased field size. More precisely, suppose two parties want to generate
an OLE correlation over a ring Z _t_, for some small polynomial _t_, with a failure probability of _δ_
per output. Executing a distributed discrete logarithm on a value of average size _N_ requires _T_ ( _δ_ )
steps, where _T_ ( _δ_ ) is chosen such that _δ_ = _B · N/T_ [2], with _B ≈_ 400 [DKK18]. In the group-based
PCG for OLE correlations, the target value _z_ for the distributed discrete logarithm is of the
form _x · y_, where _x_ is a value computed as the inner product between an arbitrary vector and a
weight- _k_ [2] random vector, and _y_ is a value computed as the inner product between an arbitrary
vector and a weight- _k_ random vector (where all vectors are over Z _t_ ). Therefore, the average size
of _z_ is _N_ = _k_ [3] _·_ ( _p −_ 1) [2] _/_ 4. Hence, the number of steps _T_ to be performed grows as







_B · k_ [3]

_._
4 _δ_



_T_ = ( _p −_ 1) _·_



Let us fix for example a target failure probability of _δ ≈_ 2 _[−]_ [15] per output, and a target number
_n_ = 2 [26] of OLE correlations (hence _k_ = 12 by Table 5). Using an MNT curve (using the Miracl
benchmark to estimate the cost of operations) and solving the above equation for _T_ gives an
estimated running time of ( _t_ _−_ 1) _·_ 12 _._ 5 milliseconds over Z _t_ for the distributed discrete logarithm
procedure. For the same _n, k_ and using _α_ = 16, the estimated running time of expand, ignoring
the distributed discrete logarithm, is about 95 ms. Therefore, the estimated running time to
compute OLE correlations over Z _t_, for _n_ = 2 [26] and with failure probability 2 _[−]_ [15] per output,
grows as
95 + ( _t −_ 1) _·_ 12 _._ 5 milliseconds.


**E.4** **Sanitizing the Output: the Punctured OT Approach**


While the previous sections gives reasonable estimates of the cost of generating _n_ ROT with a
group-based PCG, the ROT computed this way will be faulty, due to the inverse-polynomial
failure probability of the group-based PCG. After computing _n_ instances of ROT correlations
using group-based PCG, it remains for the parties to securely remove on average _δ · n_ faulty
outputs (where _δ_ is the failure probability of the PCG). This failure probability comes from the
imperfect correctness of the distributed discrete logarithm procedure. The DDLOG protocols
of [BGI16a] and [DKK18] both allow a selected party to detect whether there is a risk of error at a
mild cost (e.g. with the scheme of [DKK18], detecting failures requires computing an additional


71


_O_ ( _M_ ) number of multiplications, where _M_ is the bound on the input, independently of the
failure probability). Unfortunately, we cannot simply let the selected party notify his opponent
about the faulty outputs to remove them: knowing that a failure risk was detected would leak
informations to this party. [17] To overcome this issue, the works of [BGI16a] and [BCG [+] 17]
developped different strategies, which we briefly outline below.


**–** Punctured OT [BGI16a]. To allow for secure reconstruction of faulty outputs, the work
of [BGI16a] suggest to use a simple erasure-correction code, and to let one of the parties
obliviously recover all outputs at positions where he did not detect a failure. By the properties
of the erasure code, the recovered outputs suffice to reconstruct the entire output. The core
observation of [BGI16a] is that an all-but-few random OT can be constructed efficiently:
there is a protocol which securely realizes ( _n−t_ )-out-of- _n_ random OT, with a communication
proportional to _t_ and log _n_ only. This protocol relies on a puncturable pseudorandom function.

**–** Leakage-Absorbing Pads [BCG [+] 17]. Alternatively, the work of [BCG [+] 17] suggests to add
some number of level-2 shares of random bits to the BCG seed, and develop methods to
perform the computations on values masked with these random bits. This allows to square
the leakage probability, as a failure will leak information only if two failures occured with
respect to the same random mask. Asymptotically, this strategy has costs comparable to
punctured OT, but leads to a considerably simpler distributed seed generation. However, the
technique can only be used to mask bit inputs, and does not seem to generalize to larger
integers.


Below, we apply the punctured OT approach [BGI16a], which we estimated to be more
efficient in our scenario. We provide a detailed overview of an optimized application of this
approach to our scenario. To implement this approach, we need two ingredient:


**–** an efficient punctured OT protocol, and

**–** a randomized linear code with good erasure-correction properties.


Punctured OT protocols can be built from _t_ -puncturable pseudorandom functions, together with
an appropriate two-party computation protocol. We recall the definition of puncturable PRFs
below, and describe an optimized algorithm to puncture a PRF at _t_ points efficiently.


**E.4.1** **Puncturable Pseudorandom Function.**


We first recall the definition of puncturable pseudorandom functions (pPRFs), as they are the
main primitive involved in the efficient realization of a punctured OT protocol, and describe an
improved construction of a _t_ -pPRF from the GGM PRF.


**Definition 50 (** _t_ **-Puncturable Pseudorandom Function).** _A puncturable pseudorandom_
_function with key space K, domain X_ _, and range Y, is a pseudorandom function F with an addi-_
_tional punctured key space Kp and three probabilistic polynomial-time algorithms_ ( _F._ KeyGen _, F._ Puncture _,_
_F._ Eval) _such that_


**–** _F._ KeyGen(1 _[λ]_ ) _outputs a random key K ∈K,_

**–** _F._ Puncture( _K, x_ ) _, on input a ley K ∈K, and a subset S ⊂X of size t, outputs a punctured_
_key K{S} ∈Kp,_

**–** _F._ Eval( _K{S}, x_ ) _, on input a key K{S} punctured at all points in S, and a point x, outputs_
_F_ ( _K, x_ ) _if x /∈_ _S, and ⊥_ _otherwise,_


_such that no probabilistic polynomial-time adversary wins the experiment_ Exp _-_ s _-_ pPRF _represented_
_on Figure 7 with non-negligible advantage over the random guess._


17 Denoting _**x**_ and _**y**_ the inputs of the parties, and _Ni_ the _i_ th line of the matrix _N_, notifying a party of a risk
of failure for the output _i_ leaks to this party the value ( _Ni_ _**x**_ ) _·_ ( _Ni_ _**y**_ ) over the integers (with high probability).
While ( _Ni_ _**x**_ ) _·_ ( _Ni_ _**y**_ ) mod 2 is pseudorandom under LPN and leaks nothing about _**x**_ _,_ _**y**_, this is not the case for
the product over the integer, and this leakage cannot be allowed in general.


72


**Experiment** Exp **-** s **-** pPRF


**Setup Phase.** The adversary _A_ sends a size- _t_ subset _S_ _[∗]_ _∈X_ to the challenger. When it receives _S_ _[∗]_,
the challenger picks _K_ _←_ $ _F._ KeyGen(1 _λ_ ) and a random bit _b_ _←{_ $ 0 _,_ 1 _}_ .
**Challenge Phase.** The challenger sends _K{S_ _[∗]_ _} ←_ _F._ Puncture( _K, S_ _[∗]_ ) to _A_ . If _b_ = 0, the challenger
additionaly sends ( _F_ ( _K, x_ )) _x∈S_ _[∗]_ to _A_ ; otherwise, if _b_ = 1, the challenger picks _t_ random values
( _yx_ _←Y_ $ for every _x ∈_ _S∗_ ) and sends them to _A_ .


**Fig. 7.** Selective security game for puncturable pseudorandom functions. At the end of the experiment, _A_ sends
a guess _b_ _[′]_ and wins if _b_ _[′]_ = _b_ .


A pPRF can be constructed from any length-doubling pseudorandom generator, using the
celebrated GGM construction [GGM86]. It proceeds as follows: On input a key _K_ and a point _x_,
set _K_ [(0)] _←_ _K_ and perform the following iterative evaluation procedure: for _i_ = 1 to _ℓ_ _←_ log _|x|_,
compute ( _K_ 0 [(] _[i]_ [)] _[, K]_ 1 [(] _[i]_ [)][)] _[ ←]_ _[G]_ [(] _[K]_ [(] _[i][−]_ [1)][)][, and set] _[ K]_ [(] _[i]_ [)] _[ ←]_ _[K]_ _x_ [(] _[i]_ _i_ [)][. Output] _[ K]_ [(] _[ℓ]_ [)][. This procedure creates]
a complete binary tree with edges labeled by keys; the output of the PRF on an input _x_ is the
key labeling the leaf at the end of the path defined by _x_ from the root of the tree.


**–** _F._ KeyGen(1 _[λ]_ ) : output a random seed for _G_ .

**–** _F._ Puncture( _K, z_ ) : on input a key _K ∈{_ 0 _,_ 1 _}_ _[k]_ and a point _x_, apply the above procedure and
return _K{x}_ = ( _K_ 1 [(1)] _−x_ 1 _[, . . ., K]_ 1 [(] _[ℓ]_ _−_ [)] _xℓ_ [)][.]

**–** _F._ Eval( _K{x}, x_ _[′]_ ), on input a punctured key _K{x}_ and a point _x_, if _x_ = _x_ _[′]_, output _⊥_ .
Otherwise, parse _K{x}_ as ( _K_ 1 [(1)] _−x_ 1 _[, . . ., K]_ 1 [(] _[ℓ]_ _−_ [)] _xℓ_ [)][ and start the iterative evaluation procedure]

from the first _K_ 1 [(] _[i]_ _−_ [)] _xi_ [such that] _[ x]_ _i_ _[′]_ [= 1] _[ −]_ _[x][i]_ [.]


To obtain a _t_ -puncturable PRF with input domain [ _n_ ], one can simply run _t_ instances of the
above puncturable PRF and set the output of the PRF to be the bitwise xor of the output of
each instance. With this construction, the length of a key punctured at _t_ points is _tλ_ log _n_, where
_λ_ is the seed size of the PRG. However, in the context of using a pPRF to design a punctured
OT, we observe that we can do better. Intuitively, to obtain a _t_ -puncturable PRF out of the
GGM PRF, it suffices to define a key punctured at a subset _S_ of leaves to be the smallest set
of intermediate PRG values that allows to reconstruct all leaf values indexed by [ _n_ ] _\ S_, and
does not allow to reconstruct the leaf values indexed by _S_ . We represent on Figure 8 a labelling
algorithm which finds the indices of such a subset of the keys. The correctness of the algorithm
follows easily by inspection; with a little more effort, one can also show that this algorithm is
optimal (i.e., it produces the smallest possible punctured key satisfying the constraints). The
worst-case scenario is easily seen to happen when all the punctured leaves are regularly spaces,
with a distance of _n/t_ between every two punctured leaves. This observation allows to upper
bound the length of a key punctured at _t_ points by _tλ_ log( _n/t_ ), improving over the cost _tλ_ log _n_
of the naive approach.


**E.4.2** **Punctured OT.**


A _t_ -out-of- _n_ oblivious transfer (OT) protocol involves a sender, with a database _D_ = ( _d_ 1 _, . . ., dn_ ),
and a receiver holding a subset _S ⊂_ [ _n_ ] of size _|S|_ = _t_ . The receiver should learn all entries ( _di_ ) _i∈S_,
without learning the entries indexed by [ _n_ ] _\ S_, while the sender should not learn which entries
the receiver got. Standard _t_ -out-of- _n_ OT protocols involve _O_ ( _λ ·_ ( _t_ + _n_ )) bits of communication.
In [BGI17], the authors observed that when _t_ is very close to _n_ ( _n −_ _t_ = _o_ ( _n_ )), this primitive
can be implemented more efficiently, using only _n_ + _o_ ( _n_ ) bits of communication. We outline the
construction below; it relies on a general two-party computation protocol (modeled as an oracle
_Π_, which can be implemented with a trusted setup or any standard protocol, such as Yao’s
protocol) and a _t_ -puncturable PRF _F_ with domain [ _n_ ].


73


Algorithm **Puncture-Label**


**Input.** A complete binary tree _T_ with _n_ leaves (indexed by [ _n_ ]), and a size- _t_ subset _S_ of [ _n_ ]. We
denote by _s_ 1 _< s_ 2 _< · · · < st_ the indices of the leaves in _S_ .
**Output.** A labelling _Lt_ of all nodes of _T_, such that all nodes of [ _n_ ] _\ S_, and only them, belong to a
subtree of _T_ whose root belongs to _Lt_ .
**Procedure.** The labelling proceeds in _t_ steps. Given a leave _x_ and a subtree _T_ _[′]_ of _T_ which contains
_x_, we denote by Label( _x, T_ _[′]_ ) the procedure which outputs all nodes of _T_ _[′]_ which have their parent node
in _P_ but are not in _P_ themselves, where _P_ denotes the path from the root of _T_ _[′]_ to _x_ .


**–** In step 1, set _L_ 1 _←_ Label( _s_ 1 _, T_ ).

**–** In step _i_ +1, let _Ti_ +1 denote the smallest subtree of _T_ which contains _si_ +1 and whose root belongs
to _Li_ ( _Ti_ +1 exists by construction), and let _ri_ +1 denote its root. Set _Li_ +1 _←_ ( _Li \ {ri_ +1 _}_ ) _∪_
_{_ Label( _si_ +1 _, Ti_ +1) _}_ .


After all steps are completed, output _Lt_ .


**Fig. 8.** Labelling algorithm to compute the indices of a subset of keys in the GGM PRF construction which
allows to reconstruct the output of the GGM PRF at all points except exactly _t_ .


1. The parties invoke _Π_ on a randomized functionality that, on input _S ⊂_ [ _n_ ] from the receiver,
outputs a random PRF key _K_ to the sender, and the key _K{_ [ _n_ ] _\ S}_ punctured at all points
in [ _n_ ] _\ S_ to the receiver.
2. For _i_ = 1 to _n_, the sender computes and sends _d_ _[′]_ _i_ _[←]_ _[d][i][ ⊕]_ _[F]_ [(] _[K, i]_ [)][.]
3. The receiver outputs ( _i, d_ _[′]_ _i_ _[⊕]_ _[F.]_ [Eval][(] _[K][{][S][}][, i]_ [))][ for all] _[ i][ ∈]_ [[] _[n]_ []] _[ \][ S]_ [.]


Plugging in Yao’s protocol for _Π_, and the GGM construction for _F_, this leads to a protocol
with _n_ +( _n_ _−_ _t_ ) _·_ log _n_ _·_ poly( _λ_ ) bits of communication, which is _n_ + _o_ ( _n_ ) when _n_ _−_ _t_ is sufficiently
small, hence the result.


**E.4.3** **Erasure-Correcting Code.**


The second ingredient we need is a randomized linear code with good erasure-correction properties. Such codes are common in the literature.


**Lemma 51 (Lemma 5.2 from [BGI17]).** _There is a randomized linear encoding function_
_Er_ : _{_ 0 _,_ 1 _}_ _[n]_ _�→{_ 0 _,_ 1 _}_ _[n]_ [+] _[n/λ]_ _that can correct a_ 1 _/λ_ [2] _rate of random erasures, with all but n·_ negl( _λ_ )
_probability._


The encoding of an _n_ -bit input _x_ is obtained by appending _n/λ_ bits _x_ _[′]_ 1 _[,][ · · ·][, x][′]_ _n/λ_ [to] _[ x]_ [, where]
each _x_ _[′]_ _i_ [is the parity of a random subset of] _[ λ]_ [2] _[/]_ [2] _[−]_ [1][ bits of] _[ x]_ [. By a standard Chernoff bound, the]
probability that a given bit of _x_ cannot be recovered (which happens when all subsets containing
this bit contain an erasure) is bounded by _n ·_ 2 _[λ/]_ [3], hence the result.
While the above lemma provides an asymptotic statement, in practice computing the parity
bit of _O_ ( _λ_ [2] ) outputs with the PCG would be too expensive. Instead, we will seek to obtain a
good tradeoff between the cost of computing the parity bits (we obtain better computational
efficiency when each parity bit is the parity of few bits), and the total size of the encoding
(we obtain a smaller size when each parity bit is the parity of many bits). Explicit choices of
parameters a discussed in the section Efficiency Estimations below.


**E.4.4** **Putting the Pieces Together.**


Given a punctured OT and an efficient erasure-correcting code, the following protocol gives
an asymptotically good method to sanitize the faulty outputs of the group-based PCG: first,
instead evaluating the target bilinear correlation _B_ on the input with the PCG, the functionality
is modified to evaluate _E_ ( _B_ ( _·_ )) instead, where _E_ is the encoding function of the above code (note
that _E_ is linear, hence _E ◦_ _B_ is a bilinear function).


74


_Remark 52 (Preprocessing the Sanitizing Phase)._ It would be desirable, in our context, to preprocess the material needed to execute the sanitization phase (i.e., the punctured OT), so as to
include the appropriate material directly in the seed of the PCG. However, the indices of the
faulty outputs are not known when the PCG seed is generated. Nevertheless, the parties can
preprocess the punctured OT on a uniformly random subset _S_ of the appropriate size _t_ (which
adds _λt_ log _n_ bits to the seed). In the sanitization phase, the receiver can first send a permutation _σ_ of [ _n_ ] that maps all faulty outputs to _S_, and the sender applies _σ_ to his output before
executing the step 2. As _S_ is random, this leaks nothing about which outputs failed. However,
this increases the communication of the sanitization phase to _n_ log _n_, superlinear in the number
_n_ of ROT produced.
As observed in [BCG [+] 17], the cost of the sanitization phase can be reduced to _O_ ( _n_ ) by
executing it on _blocks_ of outputs, rather than on individual outputs. Observe that each output
of the GGM PRF is a random-looking _λ_ -bit key; hence, this key can be used to mask up to _λ_
outputs directly (or any larger number of outputs by first feeding this key to a PRG). The parties
partition [ _n_ ] into _N_ = _O_ ( _n/_ log _n_ ) blocks (indexed by [ _N_ ]), each containing _n/N_ outputs, for
some tradeoff parameter _N_ . As there are _t_ faults in total, at most _t_ blocks contain a faulty output.
The parties execute a punctured OT on a random size- _t_ subset _S_ of [ _N_ ]. In the sanitization phase,
the receiver sends a permutation _σ_ of [ _N_ ] that maps the indices of all blocks containing at least
one faulty output to _S_ . Note that exchanging this permutation requires _O_ ( _N_ log _N_ ) = _O_ ( _n_ ) bits
of communication. Note that the erasure code must also be applied directly at the block level.


**E.4.5** **Efficiency Estimations.**


We provide an estimation of the cost of using punctured OT to mitigate the leakage. Consider
the task of computing 2 [26] ROTs using the group-based PCG, setting _α ←_ 16 and _T ←_ 2 [16] .
The probability of a failure event for each individual output with these parameters is 2 _[−]_ [14] _[.]_ [7],
and these events are independent of each other. By a standard Chernoff bound, for any _ε_, the
probability that the number of failures exceeds _n ·_ 2 _[−]_ [14] _[.]_ [7] _·_ (1 + _ε_ ) = 2 [11] _[.]_ [3] (1 + _ε_ ) is bounded by




          - _e_ _[ε]_
Pr[ _X ≥_ 2 [11] _[.]_ [3] (1 + _ε_ )] _≤_

(1 + _ε_ ) [1+] _[ε]_



�211 _._ 3
_,_



solving for the smallest _ε_ such that the above quantity is bounded above by 2 _[−]_ [80] gives _ε ≈_ 0 _._ 217.
Therefore, except with probability _≈_ 2 _[−]_ [80], the total number of failures will be bounded by
_t_ = 1 _._ 217 _·_ 2 [11] _[.]_ [3] _<_ 2 [11] _[.]_ [6] .
We set the number of blocks _N_ to be _n/_ 128 = 2 [19] (hence each block contains 128 consecutive
outputs). The size of a PRF key punctured at _t_ points, for a GGM PRF over domain [ _N_ ], is
upper bounded by _tλ_ log( _N/t_ ) _<_ 2 [11] _[.]_ [6] _·_ 2 [7] _·_ (19 _−_ 11 _._ 6) _<_ 2 [21] _[.]_ [5] bits. As the seed of the groupbased PCG for _n_ = 2 [26] and _α_ = 16 already has size _≈_ 2 [25] bits (for a Cocks-Pinch elliptic curve),
adding the punctured key to the PCG seed does only marginally increase its size.
We now turn our attention to the parameters of the erasure-correcting code. We set the number nb of blocks involved in a parity check to be an arbitrary small number, say, 5 (other choices
of nb would lead to a different tradeoff between computation and communication). Suppose that
we want to ensure that every punctured block can be reconstructed, except with global probability 2 _[−]_ [40] (we stress that this is a statistical success probability, it has no impact on security).
As there is at most 2 [11] _[.]_ [6] punctured blocks (out of 2 [19] blocks in total), this means that every
block must be involved in at least _−_ 40 _/_ log(5 _·_ (2 [11] _[.]_ [6] _/_ 2 [19] )) _≈_ 7 _._ 9 parities to ensure a 1 _−_ 2 [40]

probability of successful reconstruction. By a standard Chernoff bound, this means that the
number of parity-check blocks to be added to the output is approximately 7 _._ 9 _∗_ _n/_ nb _≈_ 1 _._ 58 _n_ .
To apply the error-correcting code as part of the PCG Expand procedure, the parties executes
the steps 1-5 of Expand as previously. Then, for each parity-check block to be computed, the
parties retrieve their multiplicative shares of ( _gt_ _**[b]**_ [1] _[,][ · · ·][, g]_ _t_ _**[b]**_ [5][)][, where] _**[ b]**_ [1] _[ · · ·]_ _**[ b]**_ [5][ correspond to the]


75


nb = 5 blocks of outputs involved in the parity check, homomorphically multiply their shares

�5

(getting multiplicative shares of _gt_ _i_ =1 _**[b]**_ _[i]_ ), compute a DDLOG to recover additive shares of

�5
_i_ =1 _**[b]**_ _[i]_ [, and reduce their shares modulo][ 2][. This adds to the total computation][ 1] _[.]_ [58] _[n]_ [ DDLOGs]
on exponents of average size 5 _·_ ( _k_ [3] _/_ 4) (the cost of the homomorphic multiplications is negligible
compared to the other costs).


**E.4.6** **Running Time and Communication of the Sanitization.**


With these parameters, using again the benchmark numbers of the Miracl library, the average
running time for computing each _sanitized_ ROT on one core of an Intel i5 processor over a
512-bit Cocks-Pinch curve ( _n_ = 2 [26] _, α_ = 16 _, T_ = 2 [16] _,_ nb = 5) is approximately 187ms. The
communication involved in the punctured OT protocol consists in exchanging a permutation of

[ _N_ ] = [ _n/_ 128], and sending _N_ blocks masked by a PRF output, for a total communication of
(1 + 1 _._ 58) _·_ (log( _n/_ 128) + _λ_ ) _· n/_ 128 _<_ 3 _·_ 2 [26] bits, taking _n_ = 2 [26] and _λ_ = 128 (hence on average
3 bits per sanitized ROT). We represent on Table 10 the result of similar calculations for other
choices of _T_ and _n ≥_ 2 [26], with _α_ = 16. The table summarizes the size of the punctured key
(which is added to the seed of the PCG), the estimated running time, and the communication
required to sanitize the output (per sanitized OT correlation produced).
Please note that the running time estimates given in the table do not correspond to measured
running time of an actual implementation, but are estimated from the number of operations
performed, using benchmark data for estimating the running time of each operation. Therefore,
these estimates do not take into account additional costs resulting from, e.g., cache-misses, and
should only be seen as providing a rough indication of the actual running time rather than an
accurate estimation.


( _T, n_ ) (2 [16] _,_ 2 [26] ) (2 [16] _,_ 2 [28] ) (2 [17] _,_ 2 [28] ) (2 [16] _,_ 2 [30] ) (2 [17] _,_ 2 [30] ) (2 [18] _,_ 2 [30] )


Punct. key size 2 [21] _[.]_ [5] 2 [22] _[.]_ [4] 2 [20] _[.]_ [7] 2 [23] _[.]_ [9] 2 [22] _[.]_ [4] 2 [20] _[.]_ [7]

Runtime (est.) 187ms 160ms 148ms 154ms 144ms 151ms
Comm. (bit/ROT) 3 2.6 2.2 2.5 2.2 2.0


**Table 10.** Punctured key size, estimated running time (for the total computation, including the seed extension
plus the sanitization), and communication per sanitized ROT, for various choices of ( _T, n_ ). We use _α_ = 16 and
a Cocks-Pinch curve in the calculations. The security parameter _λ_ is set to 128, and we ensure a statistical
probability of 1 _−_ 2 _[−]_ [40] of producing at least _n_ sanitized OT correlations. The failure probabilities corresponding
to the choice of _T_ are taken from Table 5, and the running time estimates for the non-sanitized OT correlations
are taken from Table 9.


**E.5** **Sanitizing the Output: a New Approach**


In this section, we observe that a much more efficient sanitization procedure can be obtained by
relying on the silent OT extension protocol introduced in Section 5, demonstrating an interesting
and surprising interplay between our techniques for building PCGs. The key idea is that, by
choosing an appropriate failure bound per output, it can be ensured that all but a tiny number of
_blocks_ of output correlation contain a sufficiently small number of faulty outputs. Then, this tiny
number of blocks with too many faults can be safely deleted by simply revealing their position
(recall that the failures are detectable, hence one of the parties can know their position). If the
number of such block is guaranteed to be sufficiently small with overwhelming probability, this
only incurs a leakage of _O_ (1) bits of information about the seed of our group-based PCG. Then,
the security of the construction is maintained under the non-standard but plausible assumption
that the underlying assumption (LPN or a variant of it) is resilient to a constant amount of
leakage. Eventually, since all remaining blocks are guaranteed to contain a sufficient number _t_ of


76


non-faulty outputs, a _t_ -out-of- _m_ oblivious transfer protocol can be used to let one of the parties
securely select the _t_ non-faulty correlations. Using the silent OT extension protocol introduced in
Section 5, these _t_ -out-of- _m_ oblivious transfers can be locally generated from a short seed (which
can be added to the group-based seed with almost no overhead) by the parties. Compared
to the punctured OT approach, this method incurs a slightly larger communication (about 4
bits per sanitized outputs, instead of 3 with punctured OT), but is computationally much more
efficient, and requires much less preprocessing material (which, in particular, should considerably
simplify the task of distributively generate the preprocessing material; note also that our silent
OT extension admits a very efficient distributed setup based on the Doerner-shelat protocol).
We elaborate below.


**E.5.1** **Concrete Instantiation.**


Assume for simplicity that the parties want to generate _n_ = 2 [26] sanitized correlations. The PCG
seed is made of the seed of our group-based PCG, together with two seeds for a 1-out-of-4 silent
OT extension. To generate _n_ sanitized correlations, the parties _P_ 0 and _P_ 1 first generate 2 _n_ faulty
correlation (using e.g. two parallel instances of the group-based PCG with _n_ = 2 [26], exchanging
their roles to balance the cost), setting the parameters so that each output has a probability
bounded by 2 _[−]_ [15] of being faulty (based on our previous estimates, this requires performing
about _T_ = 72 _·_ 10 [3] multiplications for each distributed discrete logarithm, which takes about
12ms using an MNT curve). At the same time, the parties locally generate _n_ random 1-out-of-4
OTs, using the silent OT extension protocol. We assume that _P_ 0 has detected the position of
the potentially faulty outputs.
To sanitize the output, the parties divide the 2 _n_ outputs into _n/_ 2 blocks of 4 outputs. _P_ 0
first indicate to _P_ 1 the position of all blocks that contain at least three faulty outputs; by a
standard Chernoff bound, there will be at most 3 such blocks in total, except with probability
bounded by min _ℓ>_ 0(1 + 2 _[−]_ [15] _·_ ( _e_ _[ℓ]_ _−_ 1)) _[n/]_ [2] _/e_ [4] _[ℓ]_ _<_ 2 _[−]_ [70] (note that this is a statistical security
guarantee). Therefore, under the plausible assumption that LPN with tensored noise is resilient
to 9 bits of _random_ leakage, revealing the position of these blocks does not harm the security of
the protocol. Both parties locally delete the corresponding block.
For all remaining blocks, which are guaranteed to contain at most 2 faulty outputs, the
parties execute two 1-out-of-4 OT protocol using the preprocessed material from the silent OT
extension, where _P_ 1 plays the role of the sender. More precisely, for each 4-tuple of shares
( _u_ 0 _, u_ 1 _, u_ 2 _, u_ 3), _P_ 1 locally generate new shares ( _v_ 0 _, v_ 1), and uses ( _u_ 0 + _v_ 0 _, u_ 1 + _v_ 0 _, u_ 2 + _v_ 0 _, u_ 3 + _v_ 0)
and ( _u_ 0 + _v_ 1 _, u_ 1 + _v_ 1 _, u_ 2 + _v_ 1 _, u_ 3 + _v_ 1) as input to the two 1-out-of-4 OT instances. If the faulty
outputs are at positions 0 and 1 (for example), _P_ 0 will securely retrieve ( _u_ 2 + _v_ 0 _, u_ 3 + _v_ 1),
hence the two parties will now have shares of the non-faulty correlations ( _u_ 3 _, u_ 4). The protocol
involves communicating 2 bits and 8 value per block, hence 4 values and 1 _/_ 2 bit per sanitized
correlation. In terms of computation, the main overhead comes from the need of computing twice
more correlations in the first place, hence a factor-2 overhead compared with the non-sanitized
group-based PCG. Note that this cost has not been optimized: both the communication and
the computation of the sanitized PCG can be reduced by generating less faulty outputs, and
fine-tuning the size of the blocks and the number of outputs to retrieve per block. We leave the
optimization and the fine-tuning of this approach to future work.


**F** **PCG from Lattices**


In this section we give a lattice-based PCG construction for any family of polynomials of bounded
degree over large finite fields, extending the results of the previous sections to more general
correlations. As a use-case we consider the generation of authenticated Beaver triples, that is for
the correlation


_{_ ( _a, b, ab, aα, bα, abα_ ) _| a, b ∈_ Z _p}_


77


for some fixed MAC _α ∈_ Z _p_ . We provide efficiency estimates for joint seed generation (with
security against semi-honest adversaries) and silent expansion.
The assumptions we build on are the sparse MQ-assumption discussed in Section 7.1 and
the ring-version of the learning with errors assumption, recalled in the following.


**Definition 53 (Learning With Errors over Rings (RLWE)).** _Let N ∈_ N _be a power of_
_two q ∈_ N _with q ≥_ 2 _, R_ = Z[ _X_ ] _/_ ( _X_ _[N]_ + 1) _and Rq_ = _R/_ ( _qR_ ) _. Let χ be an error distribution_
_over R. Let s ←_ _χ. The_ RLWE _N,q,χ-assumption states that the following two distributions over_
_R_ [2] _q_ _[are computationally indistinguishable:]_


**–** _Oχ,s: Output_ ( _a, b_ ) _where a ←Rq, e ←_ _χ and b_ = _a · s_ + _e_

**–** _U_ _: Output_ ( _a, u_ ) _←R_ [2] _q_


In the following we instantiate the generic construction from Section 4.4 with variants of
RLWE-based homomorphic secret sharing schemes.


**F.1** **PCG from Somewhat Homomorphic Encryption**


As observed in [DHRW16, BKS19], from a somewhat homomorphic encryption scheme which
supports distributed decryption one can construct a homomorphic secret sharing scheme. In the
following we give a semi-generic definition of properties the underlying encryption scheme has
to satisfy. Note that the definition can be instantiated with a variety of lattice-based encryption
schemes.


**Definition 54 (Depth-** _d_ **Somewhat Homomorphic Encryption w/ Distributed De-**
**cryption).** _Let_ PKE := (PKE _._ Gen _,_ PKE _._ Enc _,_ PKE _._ Dec) _be an IND-CPA secure public-key encryp-_
_tion scheme. We say that_ PKE _is a_ secure depth- _d_ public-key encryption scheme with distributed
decryption _if it further satisfies the following properties:_


**–** Distributed decryption: _Let R_ := Z[ _X_ ] _/_ ( _X_ _[N]_ +1) _, for N a power of two, κ ∈_ N _and the secret_
_key space of_ PKE _contained in R_ _[κ]_ _q_ _[. We say]_ [ PKE] _[ supports distributed decryption, if there exists]_

_an algorithm_ DDec _such that for_ (pk _,_ sk) _←_ PKE _._ Gen(1 _[λ]_ ) _,_ sk0 _←R_ $ _κq_ _[,]_ [ sk][1] [:=][ sk] _[−]_ [sk][0] _[,][ m][ ∈R][p][,]_
_and_ _**c**_ _←_ $ Enc(pk _, m_ ) _it holds_ DDec(sk0 _,_ _**c**_ ) + DDec(sk1 _,_ _**c**_ ) = _m with overwhelming probability._

**–** Depth- _d_ somewhat homomorphic encryption: _There exists a procedure_ PKE _._ Eval _such that_
_for any function f_ : _R_ _[n]_ _→R_ _[m]_ _that can be evaluated by a circuit of depth at most d, for any_
_λ ∈_ N _, for any_ (pk _,_ sk) _in the image of_ Gen(1 _[λ]_ ) _, for all messages m_ 1 _, . . ., mn ∈Rp, for all_
_ciphertexts_ _**c**_ 1 _, . . ._ _**c**_ _n in the image of_ PKE _._ Enc(pk _, m_ 1) _, . . .,_ PKE _._ Enc(pk _, mn_ ) _and for any_ _**c**_
_in the image of_ PKE _._ Eval( _f,_ ( _**c**_ 1 _, . . .,_ _**c**_ _n_ )) _it holds_


PKE _._ Dec(sk _,_ _**c**_ ) = _f_ ( _m_ 1 _, . . ., mn_ ) _._


Notation. _We generalize_ Alg _∈{_ Enc _,_ DDec _,_ Eval _} to vectors of inputs in a straightforward_
_way:_ Alg _is run independently on each entry of the vector (with independent random coins if_
Alg _is randomized)._


Instantiating the generic construction of Section 4.4 with an HSS based on somewhat homomorphic encryption yields a PCG for any degree- _d_ correlation (see Figure 9). As the following
Theorem is a straightforward consequence of Theorem 23, we omit the proof.


**Theorem 55.** _Let R be a ring, ℓ, n, p, q, m ∈_ N _,_ PRG _be a degree-c D_ _[ℓ]_ _-PRG_ PRG : _R_ _[ℓ]_ _p_ _[→R]_ _p_ _[n]_ _[and]_
PKE = (PKE _._ Gen _,_ PKE _._ Enc _,_ PKE _._ Dec) _be a depth-⌈_ log _cd⌉_ _somewhat homomorphic encryption_
_scheme with message space Rp and secret key space contained in R_ _[κ]_ _q_ _[. If]_ [ PKE] _[ additionally support]_
_distributed decryption, then the PCG_ PCG = (PCG _._ Setup _,_ PCG _._ Gen _,_ PCG _._ Expand) _from Figure 9_
_is a PCG for the family of functions F_ := _{f_ : _R_ _[n]_ _p_ _[→R]_ _p_ _[m]_ _[|][ f][ is of degree at most][ d][}][.]_


78


PCG _._ Gen(1 _[λ]_ ) :

**– Generate the encryption keys.** Generate keys (pk _,_ sk) _←_ PKE _._ Gen(1 _[λ]_ ). Choose sk0 _←R_ $ _κq_ [and]
set sk1 := sk _−_ sk0.

**– Choose and encrypt a PRG-seed.** Choose _r ←D_ _[ℓ]_ ( _Rp_ ). Compute


_**c**_ _[r]_ = PKE _._ Enc(pk _, r_ ) _∈_ ( _R_ _[κ]_ _q_ [)] _[ℓ][.]_


**–** Output k0 := (sk0 _,_ _**c**_ _[r]_ ), k1 := (sk1 _,_ _**c**_ _[r]_ ).


PCG _._ Expand( _σ,_ k _σ, f_ ) :


**–** Parse k _σ_ =: (sk _σ,_ _**c**_ _[r]_ ).

**– Evaluate** _f ◦_ PRG **on the encrypted seed.** Compute


_**c**_ _[Y]_ _←_ PKE _._ Eval( _f ◦_ PRG _,_ _**c**_ _[r]_ ) _∈_ ( _R_ _[κ]_ _q_ [)] _[m][.]_


**– Decrypt the result.** Decrypt and output


_Rσ_ _[Y]_ _[←]_ [PKE] _[.]_ [DDec][(][sk] _σ_ _[,]_ _**[ c]**_ _[Y]_ [ )] _[ ∈R][m]_ _p_ _[.]_


**Fig. 9.** PCG for the family of degree- _d_ functions from degree- _c D_ _[ℓ]_ -PRG PRG and depth- _⌈_ log _cd⌉_ somewhat
homomorphic encryption scheme PKE.


_Remark 56._ Note that the key generation of the PCG given in Figure 9 can be sourced out to
the setup phase and the same secret key shares used across many instances.


**Corollary 57.** _Instantiating the PRG in the construction of Figure 9 with the degree-_ 2 _ρ-_
_sparse PRG_ PRGMQ : Z _[ℓ]_ _p_ _[→]_ [Z] _p_ _[n]_ _[from Definition][ 34][ and the somewhat homomorphic encryp-]_
_tion scheme with the BGV encryption scheme of Brakerski et al. [BGV12] (chosing parameters_
_R_ = Z[ _X_ ] _/_ ( _X_ _[N]_ + 1) _, p, q and error distribution χ s.t. evaluation of at least degree-_ 5 _functions/_
_depth-_ 3 _circuits is supported), we obtain a PCG for the generation of authenticated Beaver triples,_
_assuming ρ-sparse M_ ( _ℓ_ [2] _, n, Rp_ ) _-MQ and_ RLWE _N,q,χ._


**F.2** **Efficiency Estimates**


Authenticated Beaver triples are used in multi-party protocols like [DPSZ12] to achieve fast
online computation. Our PCG construction can be used as a plug-in to replace the preprocessing
in such protocols by a short joint seed generation phase (with little communication) followed by
a completely silent expansion phase. As in the described setting a large amount of Beaver triples
has to be generated at once, lattice-based PCG constructions are of practical interest, despite
the overhead introduced by encryption.
Generating many Beaver triples at once we can use ciphertext packing, as first observed
by [SV14].


_Remark 58 (Ciphertext packing, [SV14])._ Let _p_ be a prime and _N ∈_ N a power of 2, such that
the polynomial _X_ _[N]_ + 1 splits over Z _p_ into pairwise different degree-1 polynomials. If _R_ :=
Z[ _X_ ] _/_ ( _X_ _[N]_ + 1) (similar for general cyclotomic polynomials), this implies _Rp_ = ( _[∼]_ Z _p_ ) _[N]_ and
enables “packing” _N_ plaintexts into one ciphertext (by encrypting _Ψ_ ( _z_ ) for some _z ∈_ Z _[N]_ _p_ [, where]
_Ψ_ : (Z _p_ ) _[N]_ _→Rp_ ). In the following we will refer to _Rp_ as _coefficient representation_, and to (Z _p_ ) _[N]_

as _CRT representation_ .


Thus, each ciphertext has room to hold _N_ encryptions. We first consider “naive” ciphertext
packing: We start with _ℓ_ encryptions of each _N_ seeds _r ∈_ Z _[ℓ]_ _p_ [, perform the expansion homomor-]
phically on the ciphertexts (which corresponds to expanding feach of the _N_ seeds in parallel).
This gives an output of _nN_ correlated tuples in total.
In the following we estimate efficiency of the PCG construction given in Corollary 57 with the
above described ciphertext packing. We use the parameters given in [CS16] to support depth-4


79


homomorphic operations (as an upper bound) and plaintext space modulus _≈_ 2 [128] listed in the
following. Here, by _TM_ we denote the time required for multiplication over _Rq_ and by _TC_ the
time for multiplication of a Z _q_ element with an element in _Rq_ .


**–** _Dimension of R (over_ Z _): N ≈_ 13688 (we use _N_ = 2 [14] )

**–** _Ciphertext modulus:_ log _q ≈_ 750 (we use log _q_ = 744)

**–** _Parameter for key switching:_ log _T ≈_ 140

**–** _Cost of key switching: T_ KS _≈_ 2(log _q/_ log _T_ ) _TC_

**–** _Cost of multiplication on ciphertexts: T_ Eval _≈_ 4 _TM_ + _T_ KS

**–** _Cost of multiplication of constant with ciphertext: ≈_ 2 _TC_

**–** _Cost of encryption: T_ Enc _≈_ 2( _TM_ + _TC_ )

**–** _Cost of decryption: T_ Dec _≈_ 2 _TM_


For MQ we use parameters _n_ = _ℓ_ [2] _/_ 24 and _ρ_ = 100. Further, we set _ℓ_ = _c ·_ 2 [9] for _c ≥_ 1.
Later we will see that chosing _c_ = 1 we surpass the breakeven point. In other words, _ℓ_ = 2 [9]

is the smallest choice where the total output size of the correlation generator exceeds the seedlength. Our runtime estimates are based on NFLLib [ABG [+] 16]: A multiplication over _Rq_ requires
time _≈_ 9 _._ 54 ms and a multiplication over _Rq ×_ Z _q_ requires time _≈_ 0 _._ 55 ms. For an overview
of estimated setup computation and communication complexity (i.e. time and communication
required for jointly generating the seed) and estimated expansion times for the described PCG
construction and variants we refer to Table 2 in the main body.


_Distributed seed generation:_ We first describe the setup of the keys and MAC _α ∈_ Z _p_, which can
be reused across many instances. First, the parties jointly generate secret key shares (sk0 _,_ sk1)
and the corresponding public key pk, e.g. by generating secret keys according to a suitable
distribution and exchanging shares as well as the corresponding public keys. Next, both parties
choose a MAC share _ασ_ _←_ $ Z _p_ and define _**α**_ _σ ∈_ Z _Np_ [to be the vector of all] _[ α][σ]_ [entries. Next, the]
parties each compute and exchange _**c**_ _[Ψ]_ [(] _**[α]**_ _[σ]_ [)] := Enc(pk _, Ψ_ ( _**α**_ _σ_ )), and set _**c**_ _[Ψ]_ [(] _**[α]**_ [)] := _**c**_ _[Ψ]_ [(] _**[α]**_ [0][)] + _**c**_ _[Ψ]_ [(] _**[α]**_ [1][)] .
To generate encryptions of _N_ seeds _a_ and _b_ in Z _[ℓ]_ _p_ [, both parties repeat][ 2] _[ℓ]_ [times: Sample]
an element _Rp_ at random (corresponding to _N_ random Z _p_ elements), and as for generating an
encryption of the MAC key, exchange and add up the corresponding encryption.
As computation and communication is dominated by the last step, a rough estimate in
the semi-honest setting are as follows: Generating 2 _ℓ_ encryptions takes about _c ·_ 20 seconds
of computation and exchanging 2 _ℓ_ ciphertexts (each of size 2 _N_ log _q_ bits) requires _c ·_ 3 GB of
communication (per party). We estimate that in the dishonest setting communication complexity
would roughly double.


_Expansion rate:_ We expand 2 _ℓN_ elements in Z _q_ to _nN_ shared authenticated Beaver triples in
Z _p_ (each consisting of 6 Z _p_ elements), which corresponds to expanding roughly _c ·_ 3 GB of seed
material to authenticated Beaver triples of total size _c_ [2] _·_ 17 GB.


_Computational efficiency of expansion:_ The computational costs add up as follows.


**–** _Expanding the seed:_ The complexity to evaluate the PRG homomorphically on 2 _ℓ_ ciphertexts
sums up to 2 _ℓ_ [2] ciphertext multiplications and 4 _nρ_ multiplications of a constant with a
ciphertext.

**–** _Computing the triples:_ Evaluation of _fα_ requires 4 _n_ ciphertexted multiplications.

**–** _Obtaining the output shares:_ To obtain the output we have to decrypt _n_ 6 ciphertexts.


Altogether, the costs sum up to


_≈_ 4 _nρTC_ + 4(2 _ℓ_ [2] + 7 _n_ ) _TM_ + 2( _ℓ_ [2] + 2 _n_ ) _T_ KS _._


This gives a total computation time of around _c_ [2] _·_ 8 _._ 0 hours, which corresponds to an amortized
computations time of roughly 0 _._ 16 ms per authenticated Beaver triple.


80


**F.3** **PCG with Iterative Expansion**


As we choose a sparse matrix distribution (namely only _ρ_ = 100 non-zero entries per row)
to instantiate MQ, we can locally evaluate the PRG and therefore obtain a way to iteratively
generate _N_ Beaver triples at a time. This requires slightly more computational costs (assuming
one wants to discard intermediary products), but allows to generate Beaver triples whenever
needed instead of having to generate all at once. This can be achieved as follows: To generate
shares of _N_ Beaver triples, one needs to compute the scalar product of some _i_ -th column of the
_M_ ( _l_ [2] _, n, Rp_ )-MQ matrix **M** with the vector of encryptions of _r ⊗_ _r_, where _r_ is some seed. As
**M** is sparse by assumption, this requires only to compute a linear combination of _ρ_ products
_ri ·_ _rj_ on encryptions. With the numbers from above to generate _N_ triples this approach inherits
computational costs for expansion of


(4 + 2 _ρ_ ) _T_ Eval + 4 _ρTC_ + 12 _TM_ = 4 _ρTC_ + (28 + 8 _ρ_ ) _TM_ + (4 + 2 _ρ_ ) _T_ KS _._


This corresponds to a computation time of about 10 seconds per iteration (i.e. per _N_ triples of
total size 1 _._ 6 MB generated), which is amortized 0 _._ 57 seconds per triple. Note that this approach
is still limited to a total expansion of _nN_ triples.


**F.4** **PCG with Full Ciphertext Packing**


Note that the above approach limits us to go from _≈_ _ℓN_ elements to _≈_ _ℓ_ [2] _N_ elements (where _N_ is
the degree of the plaintext space over Z _p_ ). As _N_ is generally quite large that leads to a somewhat
limited expansion. To overcome this we investigated into packing more smartly, which allows
going from _≈_ _N_ elements to _≈_ _N_ [2] elements. To do so we build on the techniques of [HS18].
Even though the approach does not look promising in terms of computation due to expensive
key switching operations, we believe that it is an interesting direction for future research.
For simplicity assume that _R_ := Z[ _X_ ] _/_ ( _X_ _[N]_ + 1) such that _X_ _[N]_ + 1 splits completely over
Z _p_ and further, that the Galois group _G_ := Gal(Q( _w_ ) _/_ Q) = _{X �→_ _X_ _[j]_ : _j ∈_ Z _[⋆]_ _m_ _[}]_ [ is cyclic,]
where _w_ is a primitive _N_ -th root of unity. In this case the automorphisms _α ∈_ _G_ act on Z _[N]_ _p_ [by]
rotating the slots. Let _r_ = _Ψ_ ( _**r**_ ) _∈_ _Rp_ be some packed plain text in coefficient representation
corresponding to a vector of _N_ plain texts _**r**_ _∈_ Z _[N]_ _p_ [. As shown in [][LPR10][,][ HS18][], applying an]
automorphism _τ_ to a ciphertext _**c**_ _←_ $ Enc(pk _, Ψ_ ( _**r**_ )) leads to an encryption of _Ψ_ ( _τ_ ( _**r**_ )) which
can be decrypted with _τ_ (sk) (roughly, the reason is that applying an automorphism does not
change the norm of the noise much and therefore one can decrypt with the shifted key to the
shifted plaintext). Thus, by applying an automorphism and introducing a key-switching step, we
can let plaintexts in different slots interact with each other and thereby achieve truly quadratic
expansion.
Again, consider the BGV scheme with depth-4 homomorphic operations and plaintext space
modulus _≈_ 2 [128] . (Note that in order to get exact numbers one would have to make a careful
analysis on the the noise growth introduced by applying the automorphisms. As the numbers we
use support up to depth-4 homomorphic operations, whereas we only need to compute a circuit
of depth-3, we assume that the parameters also apply to the described setting for the following
analysis.)
We apply the matrix multiplication technique of [HS14] and assume to be given **M** _←_ $
_M_ ( _N_ [2] _, N_ [2] _/_ 24 _, Rq_ ) accordingly in CRT-packed form. We can now start with a single ciphertext,
i.e. 2 _N_ elements in Z _q_ . In the following we provide the numbers for obtaining _≈_ _N_ [2] authenticated
Beaver triples. Additional costs are _N_ key switching operations during seed generation, and _N_ [2]

key switching steps during matrix multiplication (because the matrix multiplication technique
requires to permute each part of the vector). Note that one can alternatively only partly expand
the ciphertext to generate less triples at a time and thereby saving in terms of computations (at


81


a time). We obtain the following estimated costs:


2 _NT_ KS + 2 _NT_ Eval + 2 _N_ [2] _T_ KS + 2( _N_ [2] _/_ 24) _ρ_ + 4 _T_ Eval + 6 _T_ Dec
= (8 _N_ + 28) _TM_ + 2( _N_ [2] + 2 _N_ + 2) _T_ KS + 2( _N_ [2] _/_ 24) _ρ._


This adds up to a total expansion time in the order of _c_ [2] _·_ 900 hours and is therefore far from
practical. We leave it as an open question to achieve truly quadratic extension at a reasonable
time.


**F.5** **PCG from Somewhat Homomorphic Encryption with Nearly Linear**
**Decryption**


In this section we consider a hybrid of the HSS based on somewhat homomorphic encryption
and the HSS of Boyle et. al [BKS19] based on encryption schemes which satisfy “nearly linear
decryption”. Roughly, the idea of [BKS19] is to replace multiplications of ciphertexts _**c**_ _[x]_ and
_**c**_ _[y]_, by a distributed decryption of the ciphertext _**c**_ _[x]_ with shares of _y ·_ sk, that is a distributed
decryption of _y_ times the secret key sk. This gives an improvement in terms of computation,
as in practise distributed decryption can be an order of magnitude faster than homomorphic
multiplication.
Our strategy is to replace the last multiplication with an encryption of _ψ_ ( _**α**_ ) by a distributed
decryption of _ψ_ ( _**α**_ ) times the secret key.
In Figure 10 we present the construction for the generation of authenticated Beaver triples for
a fixed MAC _α ∈_ Z _p_ employing naive ciphertext packing. As [BKS19], we require the underlying
scheme to additionally support nearly linear decryption. For details on a suitable choice of
encryption scheme, we refer to [BKS19].
When choosing the parameters of the underlying encryption scheme, one needs to take into
account the noise growth introduced by homomorphic multiplication, as the distributed decryption technique of [BKS19] requires _p/∥e∥∞_ _≪_ _q_, where _e_ is the noise term in the ciphertext. We
estimate that taking the parameters for depth-4 BGV scheme is sufficient in practice. With the
scheme of Figure 10 we can save 3 _n_ evaluation operations compared to the scheme solely based
on somewhat homomorphic encryption, which results in a saving of about _c_ [2] _·_ 0 _._ 4 hours. We
conjecture that an additional efficiency improvement over the previous scheme can be achieved
by choosing the parameters more carefully.
Alternatively, we could employ the techniques of the group-based section building on function
secret sharing for multi-point functions to get a compact sharing of one of the expanded seeds
(i.e. ( _r ⊗_ _r_ ) for one seed _r_ ). This would require switching one PRG to PRGLPN to allow for
a sparse seed. Note though that in this case the MAC _α_ has to be given in encrypted form
again (and the order of multiplication to be switched), due to the structure of [BKS19]: Their
scheme only supports a multiplication of an input value (= encryption) with a memory value
(= secret share), where the output again is a memory value. Thus, for multiplication of a degree
3-polynomial, two of the factors have to be given as encryptions. Also, this results in significantly
larger computation times, as for evaluating the PRG a non-sparse matrix has to be multiplied
with a non-sparse vector (as the automorphism _Ψ_ does not preserve sparseness).
We do not switch to the construction of Boyle et. al [BKS19] completely for the evaluation
of _fα_, even though this would save another _n_ evaluation operations, as to evaluate polynomials
of degree-3 or higher their construction relies on the so-called _modulus-lifting_ technique, which
necessitates the choice of larger parameters for the underlying ring to ensure correctness.


**G** **Multi-Party Simple Bilinear PCG**


We begin with the proof of Theorem 41, providing the general transformation from any programmable 2-party PCG for simple bilinear correlation to a corresponding _M_ -party PCG.


82


PCG _._ Gen(1 _[λ]_ ) :

**– Generate the encryption keys.** Generate keys (pk _,_ sk) _←_ PKE _._ Gen(1 _[λ]_ ). Choose sk0 _←R_ $ _κq_ [and]
set sk1 := sk _−_ sk0.

**– Generate a share of the MAC key.** Choose _α_ _←_ $ Z _p_, define _**α**_ _∈_ Z _Np_ [to be the vector of all] _[ α]_
entries. Choose _**s**_ 0 _←R_ $ _κq_ [and compute]


_**s**_ 1 := _Ψ_ ( _**α**_ ) _·_ sk _−_ _**s**_ 0 _._


**– Choose and encrypt a PRG-seeds.** Choose _ra, rb ←_ _Rp_ _[ℓ]_ [. Compute and output]


_**c**_ _[r][a]_ = PKE _._ Enc(pk _, ra_ ) _,_ _**c**_ _[r][b]_ = PKE _._ Enc(pk _, rb_ ) _∈_ ( _R_ _[κ]_ _q_ [)] _[ℓ][.]_


**–** Output k0 := (sk0 _,_ _**s**_ 0 _,_ _**c**_ _[r][a]_ _,_ _**c**_ _[r][b]_ ), k1 := (sk1 _,_ _**s**_ 1 _,_ _**c**_ _[r][a]_ _,_ _**c**_ _[r][b]_ ).


PCG _._ Expand( _σ,_ k _σ, f_ ) :


**–** Parse k _σ_ =: (sk _σ,_ _**s**_ _σ,_ _**c**_ _[r][a]_ _,_ _**c**_ _[r][b]_ ).

**– Evaluate** PRG **homomorphically on the encrypted seed.** Compute


_**c**_ _[a]_ _←_ PKE _._ Eval(PRG _,_ _**c**_ _[r][a]_ ) _,_ _**c**_ _[b]_ _←_ PKE _._ Eval(PRG _,_ _**c**_ _[r][b]_ ) _∈_ ( _R_ _[κ]_ _q_ [)] _[n][.]_


**– Evaluate** _Fα_ **homomorphically on the encrypted input.** Compute


_**c**_ _[Y]_ _←_ PKE _._ Eval( _Fα,_ _**c**_ _[a]_ _,_ _**c**_ _[b]_ ) _∈_ ( _R_ _[κ]_ _q_ [)][6] _[n][.]_


**– Obtain shares of** _Y_ **via distributed decryption with** sk _σ_ **.** Compute

_Rσ_ _[Y]_ _[←]_ [PKE] _[.]_ [DDec][(] _**[s]**_ _σ_ _[,]_ _**[ c]**_ _[Y]_ [ )] _[ ∈R]_ [6] _p_ _[n][.]_


**– Obtain the output shares over** Z _p_ . Output


_**Ψ**_ _[−]_ [1] ( _R_ _**[Y]**_ ) _∈_ Z [6] _p_ _[nN]_ _._


**Fig. 10.** PCG for authenticated Beaver triples with MAC _α_ from degree-2 PRG PRG : Z _[ℓ]_ _p_ _[→]_ [Z] _p_ _[n]_ [and depth-][2][ some-]
what homomorphic encryption scheme PKE with nearly linear decryption. Here, _Fα_ : Z _[n]_ _p_ _[×]_ [ Z] _p_ _[n]_ _[→]_ [(][Z] _p_ _[n]_ [)][6] _[,]_ [ (] _[a, b]_ [)] _[ �→]_
( _a, b, a ◦_ _b, a ◦_ _α, b ◦_ _α, a ◦_ _b ◦_ _α_ ) corresponds to evaluating _fα_ componentwise on each of the _n_ input tuples ( _◦_
denotes the entrywise product). By _**ψ**_ _[−]_ [1] we denote the map evaluating _ψ_ _[−]_ [1] : _Rp →_ Z _[N]_ _p_ [componentwise.]


_Proof._ We analyze the following _M_ -party PCG construction:


**–** PCG _M_ _._ Gen(1 _[λ]_ ) :

1. Sample random _a_ _[′]_ 1 _[, . . ., a][′]_ _M_ _←{_ $ 0 _,_ 1 _}λ_, _b′_ 1 _[, . . ., b][′]_ _M_ _←{_ $ 0 _,_ 1 _}λ_ as specified by programmability property.
2. For every _i ̸_ = _j ∈_ [ _M_ ]: Run k _[ij]_ 0 _[,]_ [ k] 1 _[ij]_ _[←]_ [PCG][2] _[.]_ [Gen][(1] _[λ][, a]_ _i_ _[′][, b][′]_ _j_ [)][ and sample PRG seed] _[ s][ij]_ _←_ $
_{_ 0 _,_ 1 _}_ _[λ]_

              -              3. For each _i ∈_ [ _M_ ], output k _i_ = _{s_ _[ij]_ _}j_ = _i, {_ k _[ij]_ 0 _[}][j]_ [=] _[i][,][ {]_ [k] _[ji]_ 1 _[}][j]_ [=] _[i]_

**–** PCG _M_ _._ Expand( _i,_ k _i_ ):

1. For every _j ̸_ = _i_, compute


_rij ←_ PRG( _s_ _[ij]_ ) _,_

( _aij, cij_ ) _←_ Expand2(0 _,_ k _[ij]_ 0 [)] _[,]_ [ (] _[b][ji][, d][ji]_ [)] _[ ←]_ [Expand] 2 [(1] _[,]_ [ k] _[ji]_ 1 [)]


2. Output _Ai_ = _aij_, _Bi_ = _bji_ (same for all _j_ ) and
_Ci_ = _−_ [�] _j_ = _i_ _[c][ij]_ [ +][ �] _j_ = _i_ _[d][ji]_ [ +] _[ e]_ [(] _[A][i][, B][i]_ [) + (] _[−]_ [1)][[] _[i<j]_ []] _[r][ij]_ [,]
where [ _i < j_ ] = 1 if _i < j_ and 0 if _j < i_ .


_Correctness:_ By assumption, each expanded output from (PCG2 _._ Gen _,_ PCG2 _._ Expand) is computationally indistinguishable from _C_ 2. In particular, it must hold whp for all _i ̸_ = _j_ : _e_ ( _Ai, Bj_ ) =
_dij −_ _cij_, where (k _[ij]_ 0 _[,]_ [ k] 1 _[ij]_ [)] _[ ←]_ [PCG][2] _[.]_ [Gen][(1] _[λ][, a]_ _i_ _[′][, b][′]_ _j_ [)] _[,]_ [ (] _[a][ij][, c][ij]_ [)] _[ ←]_ [PCG][2] _[.]_ [Expand][(0] _[,]_ [ k] _[ij]_ 0 [)] _[,]_ [ (] _[b][ij][, d][ij][ ←]_


83


PCG2 _._ Expand(1 _,_ k _[ij]_ 1 [)][. This means with overwhelming probability,]







_M_


_e_ ( _Ai, Bi_ ) +

_i_ =1


_M_


_e_ ( _Ai, Bi_ ) +

_i_ =1






 =


=


=



_M_



_i_ =1



_M_


_e_ ( _Ai, Bj_ )

_j_ =1



_e_



_M_

 



_Ai,_

_i_ =1



_M_


_Bj_

_j_ =1



_M_



_i_ =1


_M_



_i_ =1





( _dij −_ _cij_ ) =

_j_ = _i_





_e_ ( _Ai, Bj_ )

_j_ = _i_



_k_


_Ci._

_i_ =1



(Note that for all _i ̸_ = _j_, _rij_ is added and subtracted exactly once in the sum.) Further, by
indistinguishability of the expanded outputs from PCG2 _._ Expand to the target correlation _C_ 2, it
holds that each ( _ai, bj_ ) pair is pseudorandom. Thus, for _M_ independent samples, [�] _ai_ and [�] _bi_
are jointly pseudorandom. Finally, from the pairwise pseudorandom offsets _rij_ (independent of
the _ai_ and _bi_ ), it holds that the _Ci_ are pseudorandom, up to the required constraint. Correctness
follows.
_Security._ We now proceed to prove security of PCG _M_ . Let _T ⊂_ [ _M_ ] corrupted. We wish to
show that given _{_ k _i}i∈T_, the expanded outputs of honest parties ( _Ai, Bi, Ci_ ) _i/∈T_ cannot be distinguished from an independent resampling, conditioned on the _expanded_ values ( _Ai, Bi, Ci_ ) _i∈T_
of the corrupt seeds.
We first observe that due to the pariwise secret pseudorandom offsets _r_ _[ij]_ = PRG( _s_ _[ij]_ ), that
even given _{_ k _i}i∈T_ and ( _Ai, Bi_ ) _i∈T_ the joint distribution of ( _Ci_ ) _i/∈T_ is indistinguishable from
random, up to the preserved sum [�] _i/∈T_ _[C][i]_ [ as required.]
It thus remains to show that given _{_ k _i}i∈T_, the expanded honest values ( _Ai, Bi_ ) _i/∈T_ are
pseudorandom. By a hybrid argument, we may replace the values of honest _Ai_ and _Bi_ one at a
time. It then suffices to adress an extreme case of this step, where all but one party _i ∈_ [ _M_ ] is
corrupted.
We first treat _Ai_ ; the argument for _Bi_ is symmetric. For any _i ∈_ [ _M_ ],

     - $     






( _{_ k _j}j_ = _i,_ ( _Ai, Bi_ ))



(k1 _, . . .,_ k _M_ ) _←_ $ PCG _M_ _._ Gen(1 _λ_ )
����� ( _Ai, Bi, Ci_ ) _←_ $ PCG _M_ _._ Expand( _i,_ k _i_ )






 _[,]_



_≡_









- _{_ k _[ij]_ 1 _[}][j]_ [=] _[i][, f][a]_ [(] _[a][′]_ _i_ [)] _[, X]_
������







_a_ _[′]_ _i_ _[←]_ [$] _[, b]_ _j_ _[′]_ _[←]_ [$] _[ ∀][j][ ̸]_ [=] _[ i]_
(k _[ij]_ 0 _[,]_ [ k] 1 _[ij]_ [)] _[ ←]_ [PKE][2] _[.]_ [Gen][(1] _[λ][, a]_ _i_ _[′][, b][′]_ _j_ [)]
_X ←_ RestOfSeeds( _{b_ _[′]_ _j_ _[}][j]_ [=] _[i]_ [)]



where RestOfSeeds is an efficiently sampleable distribution that samples _b_ _[′]_ _i_ _[←]_ [$] _[, a]_ _j_ _[′]_ _[←]_ [$] _[ ∀][j][ ̸]_ [=] _[ i]_ [,]
executes the remaining (2 _M −_ 1)( _M −_ 1) instances of PCG2 _._ Gen(1 _[λ]_ _, a_ _[′]_ _ℓ_ _[, b]_ _j_ _[′]_ [)][ and outputs]


          -           _{_ k _[jℓ]_ 0 _[}][j]_ [=] _[i,l][∈]_ [[] _[M]_ []] _[,][ {]_ [k] _[ℓj]_ 1 _[}][j]_ [=] _[i,l]_ [=] _[i][, B][i]_ [ =] _[ f][b]_ [(] _[b][′]_ _i_ [)] _._


By a direct sequence of ( _M −_ 1) hybrids over _j ̸_ = _i ∈_ [ _M_ ] we may appeal to the security
of (PCG2 _._ Gen _,_ PCG2 _._ Expand) to iteratively replace the _j_ th key k _[ij]_ 1 [generated by][ (][k] 0 _[ij][,]_ [ k] 1 _[ij]_ [)] _[ ←]_
PCG2 _._ Gen(1 _[λ]_ _, a_ _[′]_ _i_ _[, b][′]_ _j_ [)][ with][ ˜][k] _[ij]_ 1 [generated as][ (˜][k] 0 _[ij][,]_ [ ˜][k] 1 _[ij]_ [)] _[ ←]_ [PCG][2] _[.]_ [Gen][(1] _[λ][,]_ [ ˜] _[a][i][, b]_ _j_ _[′]_ [)][, for independent][ ˜] _[a][i][ ←]_
$.
We thus obtain the above distribution is indistinguishable from











 _[.]_



_≈_




- _{_ [˜] k _[ij]_ 1 _[}][j]_ [=] _[i][, f][a]_ [(] _[a][′]_ _i_ [)] _[, X]_
������







_a_ _[′]_ _i_ _[←]_ [$] _[,]_ [ ˜] _[a][i][ ←]_ [$] _[, b]_ _j_ _[′]_ _[←]_ [$] _[ ∀][j][ ̸]_ [=] _[ i]_
(k _[ij]_ 0 _[,]_ [ k] 1 _[ij]_ [)] _[ ←]_ [PKE][2] _[.]_ [Gen][(1] _[λ][, a]_ _i_ _[′][, b][′]_ _j_ [)]
_X ←_ RestOfSeeds( _{b_ _[′]_ _j_ _[}][j]_ [=] _[i]_ [)]


84


                              -                              However, in this case _Ai_ = _fa_ ( _a_ _[′]_ _i_ [)][ for] _[ a][′]_ _i_ _[←]_ [$][ is completely independent of] _{_ [˜] k _[ij]_ 1 _[}][j]_ [=] _[i][, X]_,

generated now as a function in only ˜ _ai_ (not _a_ _[′]_ _i_ [). The claim, and thus security of the construction,]
follows.


We now explore sample 2-party PCG constructions that support the necessary programmability.


**Proposition 59 (Programmability of 2-party PCGs).** _The following 2-party PCGs are_
programmable _, as per Definition 40._


**–** _The 2-party VOLE generator of [BCGI18], based on DPF and LPN._

**–** _The PCGs for arbitrary simple 2-party bilinear correlations as constructed in this work from_
_somewhat-homomorphic encryption or BGN._


_Proof. M_ _-party VOLE._ Recall the 2-party VOLE generator of [BCGI18] takes the following form
(we describe their “dual” construction). The sender party receives a (short representation of) a
sparse random vector _**y**_ over the field F, the receiver receives a field element _x ∈_ F, and each
receives an FSS share of a multi-point function corresponding to the product _x_ _**y**_ . The scheme is
parameterized by a public matrix _H_ for which the dual-LPN problem is hard (with respect to
sparse noise). The sender expands to output ( _**u**_ _,_ _**v**_ ), and the receiver to ( _x,_ _**w**_ ).
It was already observed in [BCGI18] that the construction was programmable with respect
to the receiver’s output _x_ . We observe that a similar programmability holds also for the output
_**u**_ of the sender, where in particular _**u**_ is the output of compressing the value _**y**_ via the public
matrix _H_ . In both cases, the “programming information” ( _a_ _[′]_ = _**u**_ and _b_ _[′]_ = _x_ ) is anyway given
to the respective party, so the required security notion is directly implied by standard PCG
security.
_General Simple Bilinear via HSS._ One can support 2-party PCG of any simple bilinear
correlation via our PCGs for degree-2 correlations (e.g., obtained from lattices and BGN) by
giving each party a short seed _a_ _[′]_, _b_ _[′]_, respectively, as well as HSS shares of _a_ _[′]_ and _b_ _[′]_ that support
homomorphic evaluation of individual PRG expansion _a_ = PRG( _a_ _[′]_ ) _, b_ = PRG( _b_ _[′]_ ) and then the
multiplication _ab_ . This construction inherently supports programmability, by the initial values
_a_ _[′]_ _, b_ _[′]_ .


85


