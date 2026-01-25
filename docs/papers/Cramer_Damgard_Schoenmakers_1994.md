# Proofs of Partial Knowledge and Simplified Design of Witness Hiding Protocols

**Authors:** Ronald Cramer, Ivan Damgård, Berry Schoenmakers

**Published:** CRYPTO 1994

**URL:** https://link.springer.com/chapter/10.1007/3-540-48658-5_19

---

**In** _**Advances in Cryptology—CRYPTO ’94**_ **, Vol. 839 of** _**Lecture Notes in Computer Science**_ **, Springer-Verlag, 1994. pp. 174-187.**

# **Proofs of Partial Knowledge and Simplified** **Design of Witness Hiding Protocols**


Ronald Cramer, CWI
Ivan Damg˚ard, Aarhus University, Denmark
Berry Schoenmakers, CWI


**Abstract.** Suppose we are given a proof of knowledge _P_ in which a
prover demonstrates that he knows a solution to a given problem instance. Suppose also that we have a secret sharing scheme _S_ on _n_ participants. Then under certain assumptions on _P_ and _S_, we show how
to transform _P_ into a witness indistinguishable protocol, in which the
prover demonstrates knowledge of the solution to some subset of _n_ problem instances out of a collection of subsets defined by _S_ . For example,
using a threshold scheme, the prover can show that he knows at least _d_
out of _n_ solutions without revealing which _d_ instances are involved. If the
instances are independently generated, we get a witness hiding protocol,
even if _P_ did not have this property. Our results can be used to efficiently
implement general forms of group oriented identification and signatures.
Our transformation produces a protocol with the same number of rounds
as _P_ and communication complexity _n_ times that of _P_ . Our results use
no unproven complexity assumptions.


**1** **Introduction**


In this work [1], we assume that we are given an interactive proof where the prover
_P_ convinces the verifier _V_ that _P_ knows some secret. Typically, the secret is the
preimage under some one-way function of a publicly known piece of information.
Thus the secret could be for example a discrete log or an RSA root. Such a
proof is called a proof of knowledge [5], and can be used in practice to design
identification schemes or signature systems.
We assume in the following that the proof of knowledge has a special form
in that the verifier only sends uniformly chosen bits. This is also known as a
_public coin protocol_ . For simplicity, we restrict ourselves to 3-round protocols,
where the prover speaks first (generalization of our results to any number of
rounds is possible). We also assume that the protocol is honest verifier zeroknowledge (HVZK), i.e. the protocol does not reveal anything (for example about
the prover’s secret) to the honest verifier, but it is not necessarily secure against
a cheating verifier.
Numerous protocols are known to satisfy the conditions described above.
Concrete examples are Schnorr’s discrete log protocol [13] and Guillou-Quisquater’s RSA root protocol [8]. None of these protocols are known to be zeroknowledge or even witness hiding. In general, a parallelization of a sequential
zero-knowledge (ZK) proof [7] will often satisfy the conditions.


1 Partly done while visiting Aarhus University.


The second ingredient we need is a secret sharing scheme, i.e. a scheme for
distributing a secret among a set of participants such that some subsets of them
are qualified to reconstruct the secret while other subsets have no information
about it. The collection of qualified subsets is called the access structure. The
secret sharing scheme has to satisfy some properties which will be made more
precise below. Shamir’s secret sharing scheme [14] has the properties we need.
Our main result uses a proof of knowledge _P_, an access structure _Γ_ for _n_
participants, and a secret sharing scheme _S_ for the access structure dual to _Γ_
to build a new protocol, in which the prover shows that he knows solutions to
a subset of _n_ problem instances corresponding to a qualified set in the access
structure of _Γ_ (see Section 3 for details on access structures). The protocol is
witness indistinguishable, i.e. the prover reveals no Shannon information about
which qualified subset of solutions he knows. The new protocol has the same
number of rounds as _P_ and communication complexity roughly _n_ times that of
_P_ . We also show that for some access structures, the new protocol is in fact
witness hiding (WH), i.e. even even a cheating verifier will not learn enough
to be able to compute the prover’s secret. Although WH is a weaker property
than general ZK, it can replace ZK in many protocol constructions, including
identification schemes.
Since a simple 1 out of 2 structure is enough for our result to produce a WH
protocol, we obtain as a corollary a general method simplifying the design of
WH protocols: first build a protocol _P_ with properties as described above - for
security against the verifier only the weak and therefore easy to obtain property
of HVZK is needed. Then apply our result using a 1 out of 2 structure to get a
WH protocol. This new protocol will have complexity equivalent to running _P_
twice in parallel.
After surveying related work, we give in the following two sections more
details on the protocols and the secret sharing schemes we consider. Section 4
then contains the main result and corollaries, and Section 5 describes a nice
application of our results to group oriented identification and signatures.


**1.1** **Related Work**


Our techniques are to some extent related to those of De Santis et al. [11].
The models are quite different, however: [11] considers non-interactive proofs
of membership, while we consider interactive proofs of knowledge. Also, [11]
considers variants of the quadratic residuosity problem, while we consider any
problem that affords a protocol of the right form.
In some independent work, De Santis et al. [12] apply techniques similar to
ours to proofs of membership in random self-reducible languages. This leads to
perfect ZK proofs for monotone Boolean operations over such languages.
In [4], Feige and Shamir introduce the concepts of witness indistinguishable
(WI) and witness hiding (WH) protocols and prove the existence of WH protocols for a large class of problems, including the ones we consider (Corollary
4.4). This was done using general zero-knowledge techniques and the assumption that one-way functions exist. Compared to [4], our result shows that if we


start from a proof of knowledge with properties as described above, WH protocols can be constructed much more efficiently and without using computational
assumptions.
In [3], a transformation from HVZK proofs was given for protocols including
the type we consider. That transformation produced ZK protocols, but on the
other hand greatly increased the communication and round complexity so that,
contrary to ours, the practical value of that transformation is quite limited. If the
target is ZK, however, the increased round complexity seems to be unavoidable.


**2** **Proofs of Knowledge**


Let a binary relation _R_ = _{_ ( _x, w_ ) _}_ be given, for which membership can be tested
in polynomial time. For any _x_, its _witness set w_ ( _x_ ) is the set of _w_ ’s, such that
( _x, w_ ) _∈_ _R_ .
In the following, we assume that we are given a protocol _P_, which is a _proof_
_of knowledge_ for _R_, i.e. there is a common input _x_ (of length _k_ bits) to prover
_P_ and verifier _V_ and a private input _w_ to _P_ . The prover tries to convince the
verifier that _w ∈_ _w_ ( _x_ ). Refer to [5] or [4] for a formal definition.
In order for the constructions in the following to work, _P_ needs to satisfy a
few special properties.
First, we will assume that _P_ is a three round public coin protocol (although
the three round restriction can be removed). Conversations in the protocol will
be ordered triples of the form
_m_ 1 _, c, m_ 2


The second message in the protocol is a random bit string _c_ chosen by the verifier.
We refer to this as a challenge, and to the prover’s final message as the answer.
We also assume that completeness holds for _P_ with probability 1, i.e. if indeed
_w ∈_ _w_ ( _x_ ), then the verifier always accepts.
We assume that _P_ satisfies knowledge soundness in the following sense: the
length of _c_ is such that the number of possible _c_ -values is super-polynomial in _k_,
and for any prover _P_ _[∗]_, given two conversations between _P_ _[∗]_ and _V_, ( _m_ 1 _, c, m_ 2)
and ( _m_ 1 _, c_ _[′]_ _, m_ _[′]_ 2 [), where] _[ c][ ̸]_ [=] _[ c][′]_ [, an element of] _[ w]_ [(] _[x]_ [) can be computed in polyno-]
mial time. We call this the _special soundness property_ . It is easily seen to imply
the standard soundness definition, which calls for the existence of a knowledge
extractor, which can extract a witness in polynomial time from any prover that
is successful with non-negligible probability.
Although special soundness is less general than the standard definition, all
known proofs of knowledge have this property, or at least a variant where computation of the witness follows from some small number of correct answers.
Assuming special soundness is therefore not a serious restriction.
Finally, we assume that _P_ is _honest verifier zero-knowledge_ : there is a simulator _S_ that on input _x_ produces conversations that are indistinguishable from real
conversations with input _x_ between the honest prover and the honest verifier.
For simplicity we assume perfect indistinguishability in the following; generalization to other flavors of indistinguishability is easy. Most known honest verifier


zero-knowledge protocols in fact satisfy something stronger, viz. that there is a
procedure that can take any _c_ as input and produce a conversation indistinguishable from the space of all conversations between the honest prover and verifier
in which _c_ is the challenge. We call this _special honest verifier zero-knowledge_ .
We will later need the concepts of _witness indistinguishable_ (WI) and _witness_
_hiding_ (WH) protocols, which were introduced in [4]. Informally, a protocol is
witness indistinguishable if conversations generated with the same _x_ but different
elements from _w_ ( _x_ ) have indistinguishable distributions, i.e. even a cheating
verifier cannot tell which witness the prover is using. If the problem instance
_x_ is generated with a certain probability distribution by a generator _G_ which
outputs pairs ( _x, w_ ) with _w ∈_ _w_ ( _x_ ), we can define the concept of _witness hiding_ .
A protocol is witness hiding over _G_, if it does not help even a cheating verifier to
compute a witness for _x_ with non-negligible probability when the _x_ is generated
by _G_ . We refer to [4] for details.
With respect to the witness indistinguishable property, we can already now
note the following:


**Proposition 1.** _Let P be a three round public coin proof of knowledge for rela-_
_tion R. If P is honest verifier zero-knowledge, then P is witness indistinguishable._


_Proof._ We trivially have WI for conversations with the honest verifier: The use of
any witness _w_ leads to the distribution produced by the simulator. This implies
that the distribution of _m_ 2, given any fixed _m_ 1 and _c_, is independent of _w_ . The
proposition then follows from noting that in conversations with a general verifier,
the distribution of _m_ 1, and hence of _c_, is independent of _w_ .


In many concrete cases, this proposition is not interesting because there
is only one witness, in which case WI is trivial and cannot imply anything.
Nevertheless, Proposition 1 will be needed in the following for technical reasons.


**2.1** **An Example**


As a concrete example of a protocol with the properties we need, we present
Schnorr’s protocol from [13] for proving knowledge of a discrete log in a group _G_
of prime order _q_ . Let _g ̸_ = 1, and let _x_ = _g_ _[w]_ be the common input. _P_ is given _w_
as private input. In the language of the above section, the protocol is a proof of
knowledge for the relation that consists of pairs ( ( _x, g, G_ ) _, w_ ) such that _x_ = _g_ _[w]_

in _G_ . Then the protocol works as follows:


1. The prover chooses _z_ at random in [0 _..q_ ), and sends _a_ = _g_ _[z]_ to _V_ .
2. The verifier chooses _c_ at random in [0 _..q_ ), and sends it to _P_ .
3. _P_ sends _r_ = ( _z_ + _cw_ ) mod _q_ to _V_, and _V_ checks that _g_ _[r]_ = _a x_ _[c]_ .


Completeness trivially holds with probability 1. Correct answers to two different _c_ -values give two equations _r_ 1 = _z_ + _wc_ 1 mod _q_ and _r_ 2 = _z_ + _wc_ 2 mod _q_
so we find that _w_ = ( _r_ 1 _−_ _r_ 2) _/_ ( _c_ 1 _−_ _c_ 2) mod _q_ . So special soundness holds also.
Finally, note that by choosing _c_ and _r_ at random, we can make a simulated
conversation ( _g_ _[r]_ _x_ _[−][c]_ _, c, r_ ) between the honest verifier and prover. Since _c_ can be
chosen freely, we even get special honest verifier zero-knowledge.


**3** **Secret Sharing**


A secret sharing scheme is a method by which a secret _s_ can be distributed
among _n_ participants, by giving a _share_ to each participant. The shares are
computed in such a way that some subsets of participants can, by pooling their
shares, reconstruct _s_ . These subsets are called _qualified_ sets. Participants forming
a non-qualified set should be able to obtain no information whatsoever about _s_ .
Such a secret sharing scheme is called _perfect_ .
The collection of qualified sets is called the _access structure_ for the secret
sharing scheme. Clearly if participants in some set can reconstruct _s_, so can any
superset, and therefore in order for the scheme to make sense, it must be the
case that if _A_ is a qualified set, then any set containing _A_ is also qualified. An
access structure with this property is called _monotone_ .
A special case of monotone access structures is structures containing all subsets larger than some threshold value. Such structures are called _threshold struc-_
_tures_ .
Any monotone access structure has a natural dual structure. This concept
was first defined in [15].


**Definition 2.** _Let Γ be an access structure containing subsets of a set M_ _. If_
_A ⊆_ _M_ _, then_ _A_ [¯] _denotes the complement of A in M_ _. Now Γ_ _[∗]_ _,_ the dual access
structure _is defined as follows:_


_A ∈_ _Γ_ _[∗]_ _⇔_ _A_ [¯] _̸∈_ _Γ._


The next propositions follow directly from the definition.


**Proposition 3.** _The dual Γ_ _[∗]_ _of a monotone access structure is monotone as_
_well, and satisfies_
( _Γ_ _[∗]_ ) _[∗]_ = _Γ._


_Furthermore, if Γ is a threshold structure, then so is Γ_ _[∗]_ _._


**Proposition 4.** _Let Γ be monotone. A set is qualified in Γ exactly when it has_
_a non-empty intersection with every qualified set in Γ_ _[∗]_ _._


In the next section, we will assume we are given a protocol of the form described in Section 2. For each input length _k_ we will assume we are given a
monotone access structure _Γ_ ( _k_ ) on _n_ participants, where _n_ = _n_ ( _k_ ) is a polynomially bounded function of _k_ . Thus we have a _family of access structures_


_{Γ_ ( _k_ ) _| k_ = 1 _,_ 2 _, . . .}_ We can then build a new protocol for proving statements
on _n_ problem instances provided we have a perfect secret sharing scheme _S_ ( _k_ )
for _Γ_ ( _k_ ) _[∗]_ satisfying certain requirements to be defined below.
Let _D_ ( _s_ ) denote the joint probability distribution of all shares resulting from
distributing the secret _s_ . For any set _A_ of participants, _DA_ ( _s_ ) denotes the restriction of _D_ ( _s_ ) to shares in _A_ . As _S_ ( _k_ ) is perfect, _DA_ ( _s_ ) is independent from
_s_ for any non-qualified set _A_ . So we will write _DA_ instead of _DA_ ( _s_ ), whenever
_A_ is non-qualified. The requirements then are:


1. All shares generated in _S_ ( _k_ ) have length polynomially related to _k_ .
2. Distribution and reconstruction of a secret can be done in time polynomial
in _k_ .
3. Given secret _s_ and a full set of _n_ shares, one can test in time polynomial in
_k_ that the shares are all consistent with _s_, i.e. that all qualified sets of shares
determine _s_ as the secret.
4. Given any secret _s_, a set of shares for participants in a non-qualified set
_A_ (distributed according to _DA_ ) can always be completed to a full set of
shares distributed according to _D_ ( _s_ ) and consistent with _s_ . This completion
process can be done in time polynomial in _k_ .
5. For any non-qualified set _A_, the probability distribution _DA_ is such that
shares for the participants in _A_ are independent and uniformly chosen.


**Definition 5.** _A perfect secret sharing scheme satisfying requirements 1–4 is_
_called_ semi-mooth _. If, in addition, requirement 5 is satisfied it is called_ smooth _._


It is natural to ask if for any family of monotone access structures there is a
family of smooth secret sharing schemes. This question is easy to answer in
case of threshold structures. In that case it is clear that Shamir’s secret sharing
scheme [14] can be used. This scheme is even _ideal_, i.e. the shares are of the same
length as the secret. Given _d_ or more shares, the secret _s_ can be found, whereas
with _d −_ 1 or fewer shares, _s_ is completely unknown.
The following alternative to Shamir’s scheme (which is also ideal) can lead to
more efficient protocols than Shamir’s when used in our construction (Theorem
8) with a threshold structure where _d < n/_ 2.
Again _s ∈_ _GF_ ( _q_ ) is the secret, but the _i_ -th share now is a number _ci ∈_ _GF_ ( _q_ ),
1 _≤_ _i ≤_ _n_, such that _B_ _**c**_ = _s_ _**e**_ **1** . Here, _B_ is a _n −_ _d_ + 1 by _n_ matrix over _GF_ ( _q_ ),
_**c**_ = ( _c_ 1 _, . . ., cn_ ), and _**e**_ **1** = (1 _,_ 0 _, . . .,_ 0) is a vector of length _n −_ _d_ + 1. Matrix
_B_ should be such that any _n −_ _d_ + 1 columns are linearly independent (which
implies that the rank of _B_ is equal to _n −_ _d_ + 1). An appropriate choice for _B_ is
therefore the first _n −_ _d_ + 1 rows of a Vandermonde matrix over _GF_ ( _q_ ), say:








 _[.]_



_B_ =












1 1 _· · ·_ 1
1 2 _· · ·_ _n_
... ... ... ...
1 2 _[n][−][d]_ _· · · n_ _[n][−][d]_



The secret _s_ can be recovered from any _d_ shares as follows. Since _B_ _**c**_ = _s_ _**e**_ **1**,
it follows that _s_ = [�] _i_ _[n]_ =1 _[c][i]_ [. Furthermore, when] _[ d]_ [ entries of] _**[ c]**_ [ are known, the]


remaining _n −_ _d_ entries follow uniquely from the equation _B_ _[′]_ _**c**_ = **0**, where _B_ _[′]_ is
the matrix _B_ with the first row removed and **0** denotes a vector of _n −_ _d_ zeros.
This is true because _B_ _[′]_ is a _n −_ _d_ by _n_ matrix for which any _n −_ _d_ columns are
linearly independent. In case less than _d_ shares are known, the remaining shares
can be chosen such that any secret is matched.
For families of access structures other than threshold ones, the answer to the
question on existence of smooth secret sharing schemes depends on whether the
parameter _n_ is a constant, or is allowed to increase polynomially as a function
of _k_ .
In case _n_ is a constant, there exists a smooth secret sharing scheme for any
monotone access structure. For any minimal qualified set _A_, we do the following:
choose _s_ 1 _, . . ., s|A|_ at random under the condition that _s_ 1 _⊕· · · ⊕_ _s|A|_ = _s_, and
give one _si_ to each participant in _A_ . This scheme was first proposed in [9].
It is easy to check that this scheme is smooth. In particular, the size of shares
and the work needed in this scheme is linear in _k_, but the constant involved
depends of course on _n_ and on the access structure. However, the number of
possible subsets is exponential in _n_, so for non-constant _n_ this scheme will not
necessarily be smooth.
For non-constant _n_, it is an open question whether there are secret sharing
schemes of the kind we need for any sequence of access structures. Benaloh
and Leichter [1] have proposed secret sharing schemes for more general access
structures defined by monotone formulae, i.e. Boolean formulae containing only
AND and OR operators.
Consider a monotone formula _F_ with _n_ variables. Any subset _A_ of _n_ participants corresponds in a natural way to a set of values of the _n_ variables by
assigning a variable to each participant and let each variable be 1 if the corresponding participant is in _A_ and 0 otherwise. We let _F_ ( _A_ ) be the bit resulting
from evaluating _F_ on inputs corresponding to _A_ . Then we can define an access
structure _ΓF_ by
_A ∈_ _ΓF ⇔_ _F_ ( _A_ ) = 1


We let _F_ _[∗]_ denote the _dual formula_, which results from replacing in _F_ all AND
operators by OR’s and vice versa. It is not hard to show the following proposition.


**Proposition 6.** _If F is monotone then ΓF is also monotone. Conversely, for_
_any monotone access structure Γ_ _, there is a monotone formula F_ _, such that_
_Γ_ = _ΓF . We have that_ ( _ΓF_ ) _[∗]_ = _ΓF ∗_ _._


In [1], a generic method is given that, based on any monotone formula _F_,
builds a perfect secret sharing scheme for the access structure _ΓF_ . The formula
_F_ may contain general threshold operators, in addition to simple AND and
OR operators. For a polynomial size formula, it can be shown that the secret
sharing scheme from [1] satisfies all of the above requirements except possibly
requirement 5. This leads to:


**Proposition 7.** _Let {Γ_ ( _k_ ) _} be a family of access structures such that Γ_ ( _k_ ) =
_ΓFk for a family of polynomial size monotone formula {Fk}. Then there exists_
_a family of semi-smooth secret sharing schemes for {Γ_ ( _k_ ) _}._


A final comment before we go on to the main result is that we will need to
distribute secrets of length _t_ = _t_ ( _k_ ) bits, where _t_ is polynomially bounded in _k_ .
This does not impose any restrictions on _S_ ( _k_ ) because any secret sharing scheme
can distribute secrets of any length by running an appropriate number of copies
of the scheme in parallel. We therefore assume that _S_ ( _k_ ) always distributes
secrets of length _t_ . Note that, if _n_ is constant as a function of _k_, only one access
structure and secret sharing scheme are involved.


**4** **Main Result**


The next theorem describes the construction of a proof of knowledge from a basic
proof of knowledge _P_ for a relation _R_ and a family of secret sharing schemes.
In the constructed proof of knowledge both prover and verifier are probabilistic
polynomial time machines, using the prover and verifier of _P_, respectively, as
subroutines.
For the statement of the result we need some notation. Let _Γ_ = _{Γ_ ( _k_ ) _}_ be a
family of access structures on _n_ ( _k_ ) participants. Then _RΓ_ is a relation defined
by the following condition: (( _x_ 1 _, ..., xm_ ) _,_ ( _w_ 1 _, ..., wm_ )) _∈_ _RΓ_ iff all _xi_ ’s are of the
same length, say, _k_ bits, _m_ = _n_ ( _k_ ), and the set of indices _i_ for which ( _xi, wi_ ) _∈_ _R_
corresponds to a qualified set in _Γ_ ( _k_ ). In a proof of knowledge for relation _RΓ_
the prover thus proves to know witnesses to a set of the _xi_ ’s corresponding to a
qualified set in _Γ_ ( _k_ ).


**Theorem 8.** _Let P be a three round public coin, honest verifier zero-knowledge_
_proof of knowledge for relation R, which satisfies the special soundness property._
_Let Γ_ = _{Γ_ ( _k_ ) _} be a family of monotone access structures and let {S_ ( _k_ ) _} be a_
_family of smooth secret sharing schemes such that the access structure of S_ ( _k_ )
_is Γ_ ( _k_ ) _[∗]_ _. Then there exists a three round public coin, witness indistinghuisable_
_proof of knowledge for relation RΓ ._


_Proof._ To improve readability we drop in the following the dependency on _k_ from
the notation, and write _S_ = _S_ ( _k_ ), _Γ_ = _Γ_ ( _k_ ) and _n_ = _n_ ( _k_ ). We will distribute
secrets of length _t_ in _S_ . If the length of any share resulting from this is larger
than _t_, we will replace _P_ by a number of parallel executions of _P_ to make sure
that a challenge is at least as long as any share. [2] Note that this does not violate
the honest verifier zero-knowledge nor the special soundness property. A basic
idea in the following will be to interpret a challenge as a share. If challenges are
longer than shares, we will simply take the first appropriate number of bits of
the challenge to be the corresponding share. If _c_ is a challenge, _share_ ( _c_ ) will
denote the corresponding share.
The following now describes the new protocol, in which _A ∈_ _Γ_ denotes the
set of indices _i_ for which _P_ knows a witness for _xi_ :


2 For some secret sharing schemes, there is a lower bound on the length of shares in
terms of _n_ . For Shamir’s scheme, the length of shares is at least log2( _n_ + 1). If _t_ is
smaller than this bound, we can again replace _P_ by a number of parallel executions.


1. For each _i ∈_ _A_, _P_ runs simulator _S_ on input _xi_ to produce conversations
( _m_ _[i]_ 1 _[, c][i][, m][i]_ 2 [). For each] _[ i][ ∈]_ _[A]_ [,] _[ P]_ [ determines] _[ m][i]_ 1 [as what the prover in] _[ P]_
would send as _m_ 1 given a witness for input _xi_ . _P_ then sends the values
_m_ _[i]_ 1 _[, i]_ [ = 1] _[, . . ., n]_ [ to] _[ V]_ [ .]
2. _V_ chooses a _t_ -bit string _s_ at random and sends it to _P_ .
3. Consider the set of shares _{share_ ( _ci_ ) _|i ∈_ _A}_ that correspond to the _ci_ from
the simulation in Step 1. As _A_ is non-qualified in _Γ_ _[∗]_, requirement 4 guarantees that _P_ can complete these shares to a full set of shares consistent with _s_ .
_P_ then forms challenges _ci_ for indices _i ∈_ _A_, such that _share_ ( _ci_ ) equals the
share produced in the completion process. This is done by simply copying
the bits of the shares and padding with random bits if necessary. In Step 1,
_S_ has produced a final message _m_ _[i]_ 2 [in] _[ P]_ [ for] _[ i][ ∈]_ _[A]_ [. For] _[ i][ ∈]_ _[A]_ [,] _[ P]_ [ knows a]
witness for _xi_, and can therefore find a valid _m_ _[i]_ 2 [for] _[ m]_ 1 _[i]_ [and] _[ c][i]_ [by running]
the prover’s algorithm from _P_ . Finally, _P_ sends the set of messages _ci_, _m_ _[i]_ 2 [,]
_i_ = 1 _, . . ., n_ to _V_ .
4. _V_ checks that all conversations ( _m_ _[i]_ 1 _[, c][i][, m][i]_ 2 [) now produced would lead to]
acceptance by the verifier in _P_, and that the shares _share_ ( _ci_ ) are consistent
with secret _s_ . He accepts if and only if these checks are satisfied.


It is clear from the assumptions on _S_ that _P_ and _V_ need only poly-time and
access to the prover and verifier of _P_ . It therefore remains to be seen that the
protocol is a proof of knowledge and that it is witness indistinguishable.
_Completeness_ is trivially seen to hold by inspection of the protocol. For _sound-_
_ness_, assume that some prover _P_ _[∗]_ for a given first message _{m_ _[i]_ 1 _[|][ i]_ [ = 1] _[, . . ., n][}]_
can answer correctly a non-negligible fraction of the possible choices of _s_ . This
means that by rewinding _P_ _[∗]_, we can efficiently get correct answers to two different values, say _s_ and _s_ _[′]_ . [3] Let the shares of _s_ and _s_ _[′]_ sent in the protocol be
_share_ ( _ci_ ) and _share_ ( _c_ _[′]_ _i_ [)] _[, i]_ [ = 1] _[, . . ., n]_ [, respectively. Then for every qualified set]
_B ∈_ _Γ_ _[∗]_, there must be an _i ∈_ _B_, such that _share_ ( _ci_ ) _̸_ = _share_ ( _c_ _[′]_ _i_ [) since other-]
wise it would follow that _s_ = _s_ _[′]_ . But then we also have that _ci ̸_ = _c_ _[′]_ _i_ [and so by]
assumption on _P_, we can compute a witness for _xi_ . So _P_ _[∗]_ knows a witness in
every qualified set of _Γ_ _[∗]_ . On account of Proposition 4 the set of witnesses we
thus extract is a qualified set in the access structure _Γ_ .
As for _witness indistinguishability_, we have to show that the distribution of
the conversation is independent of which qualified set _A ∈_ _Γ_ the prover uses.
First observe that the distribution of each _m_ _[i]_ 1 [depends only on] _[ x][i]_ [and equals the]
distribution of the prover’s first message in an execution of _P_ with _xi_ as input.
This follows from Proposition 1, using that _P_ is honest verifier zero-knowledge.
In particular, the joint distribution of the _m_ _[i]_ 1 [’s, and hence the verifier’s choice]
of _s_, is independent of _A_ .
Since the set _{share_ ( _ci_ ) _}_ is constructed by completing a set of uniformly distributed shares in a non-qualified set of _S_, the joint distribution of the _share_ ( _ci_ )’s
is simply _D_ ( _s_ ). Since the _ci_ ’s are constructed from the shares by possibly padding
with random bits, the joint distribution of the _ci_ ’s is independent of _A_ . Fi
3 There are 2 _t_ possible _s_ -values which is super-polynomial in _k_, whence any polynomial
fraction of these contain at least 2 values for all large enough _k_ .


nally, Proposition 1 implies that the distribution of each _m_ _[i]_ 2 [depends only on]
_xi, m_ _[i]_ 1 [and] _[ c][i]_ [, and is therefore also independent of] _[ A]_ [.]


_Remark._ If the secret sharing schemes are ideal, the communication complexity
of the protocol in Theorem 8 is at most _t_ bits plus _n_ times that of _P_ . Note
that instead of taking several instances of the same proof of knowledge, it is
also possible to combine different proofs of knowledge. In this way, one may
for instance prove knowledge of either a discrete log or an RSA root without
revealing which.


**Theorem 9.** _As Theorem 8, but with P_ special _honest verifier zero-knowledge_
_and S_ ( _k_ ) semi- _smooth._


_Proof._ In this case the protocol from Theorem 8 is changed as follows. In Step 1,
the prover uses _S_ to distribute an arbitrary secret, and discards all shares in _A_ .
The remaining shares are distributed according to ~~_D_~~ _A_ ~~.~~ He then runs the special
simulator on the corresponding challenges. Note that the completion process can
still be performed on account of requirement 4, and as before, the honest prover
can counter any challenge _s_ by the verifier. Soundness is proven in the same way
as before. Therefore, the modified scheme still constitutes a proof of knowledge
for relation _RΓ_ .
As for witness indistinguishability, we only have to note that the distribution
of any _m_ _[i]_ 1 [generated by the (special) simulator is the same for any particular]
challenge value _ci_ used, because _m_ _[i]_ 1 [in a real execution of] _[ P]_ [ is independent of]
the challenge. Therefore the joint distribution of the _m_ _[i]_ 1 [’s is the same as in the]
case of Theorem 8. The rest of the proof is therefore the same as for Theorem 8.


The witness indistinguishable property of the protocol from Theorem 8 leads
us to a generalization of Theorem 4.3 of [4]. To state the result, we need to
introduce the concept of an _invulnerable generator G_ for a relation _R_ . Such
generators were first introduced in [6] and later used in slightly modified form in

[4]. Such a generator is a probabilistic polynomial time algorithm which outputs
a pair ( _x, w_ ) _∈_ _R_ . The generator is invulnerable if no probabilistic polynomial
time enemy given only _x_ can compute an element in _w_ ( _x_ ) with non-negligible
probability, taken over the coin flips of both _G_ and the enemy.

Thus, asserting the existence of an invulnerable generator for a relation is
a way of stating that it is feasible to generate hard, solved instances of the
underlying computational problem.
For any generator _G_, we let _G_ _[n]_ denote the generator that produces an _n_  tuple of pairs in _R_ by running _G_ independently _n_ times in parallel. We will also
need some notation for access structures: for a monotone access structure _Γ_, we
let the sets in _Γ_ correspond to subsets of the index set _N_ = _{_ 1 _, ..., n}_ . Now let
the set _IΓ ⊆_ _N_ be defined by: _i ∈_ _IΓ_ iff _i_ is contained in every qualified set in
_Γ_ . It is easy to see by monotonicity of _Γ_ that _i ∈_ _IΓ_ precisely if _N \ {i}_ is not
qualified (using Proposition 4).


**Theorem 10.** _Let P be a witness indistinguishable proof of knowledge for the_
_relation RΓ, where Γ_ = _{Γ_ ( _k_ ) _} is a family of monotone access structures on_
_n_ ( _k_ ) _participants, and R is a binary relation. If for all k, Γ_ ( _k_ ) _contains at least_
_two different minimal qualified sets, and there is an invulnerable generator G for_
_R, then P is witness hiding over G_ _[n]_ [(] _[k]_ [)] _._


_Proof._ We follow the line of reasoning from Thm. 4.3 of [4]. Suppose we are given
an probabilistic polynomial time enemy _A_ that has non-negligible probability of
computing a witness, using the honest prover in the scheme from Theorem 8 as a
subroutine. We show that _A_ can be compiled into an algorithm that solves with
non-negligible probability random instances _x_ generated by _G_, thus contradicting
the invulnerability of the generator (see [4]).
From the assumption on _Γ_ ( _k_ ) = _Γ_ (at least two minimal qualified sets)
it follows that _N \ IΓ_ must contain at least two elements, and that _IΓ_ is not
qualified.
Our compilation now works as follows:


1. Recall that our input is a problem instance _x_ generated by _G_ . We now form
an _n_ tuple of instances ( _x_ 1 _, ..., xn_ ) as follows: choose at random _j ∈_ _N_, and
let _xj_ = _x_ . For all other indices _i_, run _G_ to produce a solved instance _xi_ and
save the witness _wi_ .
2. Give _x_ 1 _, ..., xn_ as input to _A_ . When _A_ needs to interact with the prover, we
simply simulate the prover’s algorithm in _P_ . If _j ̸∈_ _IΓ_, this can be done,
since then _N \ {j}_ is qualified and we know witnesses of all instances except
_xj_ . If _j ∈_ _IΓ_, we fail and stop.
3. If _A_ is successful, it outputs a witness for the relation _RΓ_ which by definition
is a set of witnesses _{wi}_ corresponding to a qualified set _A_ in _Γ_ . If _j ∈_ _A_,
we have success and can output _wj_ . Else output something random.


We now show that this compilation finds a witness for _x_ with non-negligible
probability. It is sufficient to show that we find a witness with non-negligible
probability given that _j ̸∈_ _IΓ_ since this happens with probability at least 2 _/n_ .
Now note that the joint distribution of the _xi_ ’s we give to _A_ is the same as
in an ordinary interaction with the prover. Therefore _A_ is successful with nonnegligible probability by assumption. We therefore only have to bound the probability that _j_ is in _A_, the set of witnesses we get from _A_ . Since _IΓ_ is not qualified,
_A_ must contain at least one index not in _IΓ_ . By witness indistinguishability, _A_
has no information about which _j_ in _N \ IΓ_ we have chosen, and so the probability that _j ∈_ _A_ is at least 1 _/|N \ IΓ |_ . Hence if _A_ has success probability _ϵ_, our
success probability given that _j ̸∈_ _IΓ_ is at least _ϵ/n_, which is non-negligible.


Note that an access structure has at least two minimal qualified sets exactly when the corresponding minimal CNF-formula contains at least one ORoperator.
Note also that this result only shows that an enemy cannot compute a complete qualified set of witnesses. It does not rule out that the protocol could help
him to compute a small, non-qualified set. Ideally, we would like to prove that


the enemy cannot compute even a single witness. With a stronger assumption
on the access structure, this can be done:


**Corollary 11.** _Let P be a witness indistinguishable proof of knowledge for the_
_relation RΓ, where Γ_ = _{Γ_ ( _k_ ) _} is a family of monotone access structures on_
_n_ ( _k_ ) _participants, and R is a binary relation. Suppose that for all k the set_
_IΓ_ ( _k_ ) _is empty. Suppose finally that there is an invulnerable generator G for R,_
_and that inputs for P are generated by G_ _[n]_ [(] _[k]_ [)] _. Then no probabilistic polynomial_
_time enemy interacting with the honest prover can with non-negligible probability_
_compute a witness for any of the xi in the input to the protocol._


_Proof._ Since _IΓ_ ( _k_ ) is non qualified, there are at least two minimal sets, and
therefore the proof is the same as for Theorem 10, except that it follows from
the assumption that the index _j_ is always chosen among all indices. Hence if the
enemy outputs at least one correct witness, there is a non-negligible probability
of at least 1 _/n_ that this is the witness we are looking for.


A certain special case of Theorem 8 is interesting in its own right:


**Corollary 12.** _Let P be a three round public coin, honest verifier zero-knowledge_
_proof of knowledge for relation R, which satisfies the special soundness property._
_Then for any n, d there is a protocol with the same round complexity as P in_
_which the prover shows that he knows d out of n witnesses without revealing_
_which d witnesses are known._


_Proof._ Use Theorem 8 with, for example, Shamir’s secret sharing scheme for _S_
and a threshold value of _n −_ _d_ + 1.


**Corollary 13.** _Consider the protocol guaranteed by Corollary 12, let n_ = 2 _and_
_d_ = 1 _, i.e. the prover proves that he knows at least 1 out of 2 solutions. For any_
_generator G generating pairs in R, this protocol is witness hiding over G_ [2] _._


_Proof._ Since protocols constructed from Theorem 8 are always witness indistinguishable, we can use Theorem 4.2 of Feige and Shamir[4].


Note that for this corollary, we do not need the assumption that _G_ is invulnerable, as in Theorem 10.
To build the protocol of Corollary 13, we need a 2 out of 2 threshold scheme.
Such a scheme can be implemented by choosing random shares _c_ 1 _, c_ 2 such that
_c_ 1 _⊕_ _c_ 2 equals the secret. Therefore, in the simple case of Corollary 13, the
protocol constructed by Theorem 8 simply becomes a game where the verifier
chooses a random _s_, and the prover shows that he can answer correctly a pair
of challenges _c_ 1 _, c_ 2, such that _s_ = _c_ 1 _⊕_ _c_ 2. In the prover’s final message, he
only has to send _c_ 1 because the verifier can then compute _c_ 2 himself. Hence
the communication complexity of the new protocol is exactly twice that of _P_,
whence the new protocol is just as practical as _P_ .


**Corollary 14.** _Let {Γ_ ( _k_ ) = _ΓFk_ _} be a family of monotone access structure on_
_n_ ( _k_ ) _participants defined by a polynomial size family of formulas {Fk}, and let_
_P be a three round public coin,_ special _honest verifier zero-knowledge proof of_
_knowledge for relation R, which satisfies the special soundness property. Then_
_there exists a witness-indistinguishable proof of knowledge for relation RΓ_ ( _k_ ) _._
_Let M_ ( _k_ ) _be the maximal number of occurrences of a variable in F_ ( _k_ ) _. Then the_
_communication complexity of the new protocol is at most nM_ ( _k_ ) _times that of_
_P plus t bits._

_Proof._ By Proposition 3, _Γ_ ( _k_ ) _[∗]_ = _ΓFk_ _[∗]_ [, and since the size of] _[ F][ ∗]_ _k_ [is the same as]
that of _Fk_, we can use the secret sharing scheme guaranteed by Proposition 7
when we do the construction of Theorem 8. The statement on the communication
complexity follows from the fact that the shares of the secret sharing scheme
constructed in [1] from _F_ ( _k_ ) have maximal size _tM_ ( _k_ ) bits, so that we have to
use _M_ ( _k_ ) parallel executions of _P_ in the construction of Theorem 8.


**5** **Application to Identification and Signatures**


Suppose we have _n_ users, for example employees of a company, such that the
_i_ -th user has a public key _xi_ and secret key _wi ∈_ _w_ ( _xi_ ). Suppose also that
certain subsets of users are qualified in the sense that they are allowed to initiate
certain actions, sign letters on behalf of the company, etc. This defines an access
structure on the set of users. Theorem 8 now gives a way in which a subset
of users can collaborate to identify themselves as a qualified subset, without
revealing anything else about their identities. This makes good sense, if they are
to assume responsibility on behalf of the company, rather than personally.
This also extends to digital signatures, since by using a hash function, any
three round proof of knowledge as the one produced by Theorem 8 can be turned
into a signature scheme by computing the challenge as a hash value of the message to be signed and the prover’s first message (this technique was introduced
in [5]). By this method, a signature can be computed which will show that a
qualified subset was present, without revealing which subset was involved. This
is a generalization of the results from e.g. [10] and also of the group signature
concept, introduced by Chaum and Van Heyst [2]. One aspect of group signatures which is missing here, however, is that it is not possible later to “open”
signatures to discover the identities of users involved.
Note also that our method allows participants to form groups completely
freely, using the same keys in all groups. For example, two participants who
normally use Schnorr signatures individually can go together and form a “1 out
of 2” signature without changing their keys or the basic algorithms in which
they are used.


**6** **Open Problems**


Two obvious open problems remain. First, can Theorem 8 be proved assuming
ordinary soundness of _P_, and not special soundness? And secondly, can it be
generalized to other types of protocols than public coin protocols?


_Acknowledgement_ We thank Douglas Stinson for helping us with information
about results on secret sharing schemes, and Matthew Franklin for useful discussions and comments on the presentation.


**References**


1. J. Benaloh and J. Leichter: _Generalized Secret Sharing and Monotone Functions_,
Proc. of Crypto 88, Springer Verlag LNCS series, 25–35.
2. D. Chaum and E. van Heyst: _Group Signatures_, Proc. of EuroCrypt 91, Springer
Verlag LNCS series.
3. I. Damg˚ard: _Interactive Hashing can Simplify Zero-Knowledge Protocol Design_
_Without Complexity Assumptions_, Proc. of Crypto 93, Springer Verlag LNCS series.
4. U. Feige and A. Shamir: _Witness Indistinguishable and Witness Hiding Protocols_,
Proc. of STOC 90.
5. U. Feige, A. Fiat and A. Shamir: _Zero-Knowledge Proofs of Identity_, Journal of
Cryptology 1 (1988) 77–94.
6. M. Abadi, E. Allender, A. Broder, J. Feigenbaum and L. Hemachandra: _On Gen-_
_erating Solved Instances of Computational Problems_, Proc. of Crypto 88, Springer
Verlag LNCS series.
7. S. Goldwasser, S. Micali and C. Rackoff: _The Knowledge Complexity of Interactive_
_Proof Systems_, SIAM Journal on Computing 18 (1989) 186–208.
8. L. Guillou and J.-J. Quisquater: _A Practical Zero-Knowledge Protocol fitted to_
_Security Microprocessor Minimizing both Transmission and Memory_, Proc. of EuroCrypt 88, Springer Verlag LNCS series.
9. M. Ito, A. Saito, and T. Nishizeki: _Secret Sharing Scheme Realizing any Access_
_Structure_, Proc. Glob.Com. (1987).
10. T.Pedersen: _A Threshold Cryptosystem without a Trusted Third Party_, Proc. of
EuroCrypt 91.
11. A. De Santis, G. Di Crescenzo and G. Persiano: _Secret Sharing and Perfect Zero-_
_Knowledge_, Proc. of Crypto 93, Springer Verlag LNCS series.
12. A. De Santis, G. Persiano, M. Yung: _Formulae over Random Self-Reducible Lan-_
_guages: The Extended Power of Perfect Zero-Knowledge_, manuscript.
13. C.P. Schnorr: _Efficient Signature Generation by Smart Cards_, Journal of Cryptology 4 (1991) 161–174.
14. A. Shamir: _How to Share a Secret_, Communications of the ACM 22 (1979) 612–613.
15. G.J. Simmons, W.A. Jackson and K. Martin: _The Geometry of Shared Secret_
_Schemes_, Bulletin of the Institute of Combinatorics and its Applications 1 (1991)
71–88.


