# Non-Interactive and Information-Theoretic Secure Verifiable Secret Sharing

**Authors:** Torben Pryds Pedersen

**Published:** CRYPTO 1991

**URL:** https://link.springer.com/chapter/10.1007/3-540-46766-1_9

---



## Page 1

Non-Interactive and
Information-Theoretic Secure
Verifiable Secret Sharing
Torben Pryds Pedersen
Computer Science Department
Aarhus University, Denmark
tppedersen@daimi.aau.dk
Abstract
It is shown how to distribute a secret to n persons such that each person can
verify that he has received correct information about the secret without talking
with other persons. Any & of these persons can later find the secret (1 <k <n),
whereas fewer than k persons get no (Shannon) information about the secret. The
information rate of the scheme is
$ and the distribution as well as the verification
requires approximately 2k modular multiplications pr. bit of the secret.
It is also
shown how a number of persons can choose a secret “in the well” and distribute it
verifiably among themselves.
1
Introduction
Secret sharing schemes were introduced independently in [Sha79] and [Bla79] and since
then much work has been put into the investigation of such schemes (see [Sim90] for a list
of references). The verifiable secret sharing schemes constitute a particular interesting
class of these schemes as they allow each receiver of information about the secret (share
of the secret) to verify that the share is consistent with the other shares.
|
Let the dealer be the person who has a secret and distributes it to n shareholders,
|
where n > 0. If the dealer trusts one of the shareholders completely, he could give the
"secret to this person and then avoid the troubles of having a secret sharing scheme. Thus
_
in many applications the dealer does not trust the shareholders completely, and therefore
it should be expected that (some of) the shareholders do not trust the dealer either. For
this reason efficient verifiable secret sharing schemes are necessary in practice.
However, verifiable secret sharing has also turned out to be a useful tool in more the-
oretical work. In [BGW88] and [CCD88] unconditionally secure verifiable secret sharing
schemes are constructed and used to design secure multi-party protocols. Unfortunately,
these schemes are interactive — interaction between the participants is needed in order
to verify the shares. Both of these schemes require that less than % of the shareholders
are dishonest. This is improved in [RB89], where a scheme with the same properties is
presented, except that it allows less than $ dishonest participants. These three schemes
Copyright (c) 1998, Springer-Verlag


## Page 2

130
all have the property that even an all powerful dealer cannot distribute incorrect shares
(in [CCD88] and [RB89] there is an exponentially small error probability however).
In this paper, we are mainly interested in non-interactive verifiable secret sharing. In
such a scheme only the dealer is allowed to send messages — in particular the shareholders
cannot talk with each other or the dealer when verifying a share. This model is very
suitable in practice as it allows distribution by mail for instance.
[Ben87] presented the first non-interactive verifiable secret sharing scheme, but it
relied on the existence of a mutually trusted entity. In [Fel87] this entity is avoided by
letting the dealer publish probabilistic encryptions of the polynomial used to compute
the shares, and due to a homomorphism property of the encryption scheme verification
of the shares is possible. This scheme is quite efficient, but after the distribution, the
privacy of the secret depends on a computational assumption — such as the intractability
of computing discrete logarithms.
The goal of this paper is to construct an efficient non-interactive scheme for verifiable
secret sharing in which no (Shannon) information about the secret is revealed. [Ped9]]
presents a non-interactive verifiable secret sharing scheme which can be used for secrets,
s, for which g* is known, where g is the generator of a group. In this paper the scheme
suggested in [Ped91] is modified in order to remove the assumption that g* is known
beforehand. This results in a secret sharing scheme which is unconditionally secure for the
dealer. However, in this scheme the dealer can succeed in distributing incorrect shares,
if he can solve the discrete logarithm problem (see [BM84] for a formal definition). This
property is inevitable as we shall see that it is impossible to construct a non-interactive
secret sharing scheme in which no information about the secret is revealed and even a
dealer with unlimited computing power cannot cheat. Thus this scheme is in some sense
dual to that of [Fel87] (see Section 4.3).
The new secret sharing scheme is constructed by combining Shamir’s scheme (see
[Sha79]) with a commitment scheme, which is unconditionally secure for the committer
and furthermore allows commitment to many bits simultaneously.
This commitment
scheme is a variant of a scheme proposed in [BCP].
After introducing some notation in Section 2, Section 3 describes the commitment
scheme, and in Section 4 the secret sharing scheme is presented. As an application of
this scheme, Section 5 shows how the shareholders can compute linear combinations of
shared secrets and Section 6 concludes the paper.
2
Notation
Throughout this paper p and q denote large primes such that g divides
p — 1, Gy is the
unique subgroup of Z> of order q, andg is a generator of Gy. It can easily be tested if
an element a € Z> is in G, since
@eG, =
af=l.
“As any element b # 1 in G, generates the group, the discrete logarithm of a
€ G, with
.respect to the base b is defined and it is denoted log,(a).
_
-.: For any integer z the length of the binary representation of z is denoted |z|.
on :
Copyright (c) 1998, Springer-Verlag


## Page 3

131
3
The Commitment Scheme
This section describes a commitment scheme, which is very similar to that of [BCP]. The
only difference is in the choice of g and h.
Let g and h be elements of G, such that nobody knows log, h. These elements can
either be chosen by a trusted center, when the system is initialized, or by (some of) the
participants using a coin-flipping protocol.
The committer commits himself to an s
€ Zq by choosing t
€ Z, at random and
computing
E(s,t) = g?h'.
Such a commitment can later be opened by revealing s and t. The following theorem is
very easy to prove and shows that E(s,t) reveals no information about s, and that the
committer cannot open a commitment to s as s’ # s unless he can find log, (A).
Theorem 3.1
For any s € Zy and for randomly uniformly chosen t € Z,, E(s,t) is uniformly dis-
tributed in Gy.
If s,s’ € Z, satisfies s # s’ and E(s,t) = E(s’,t’), then
¢ £t! mod q and
log,
h =
$="
mod
og,h= Pog moda.
Even though it will not be used in the following we mention that it is quite easy to
prove one’s ability to open two commitments as the same value without revealing this
value. Let namely
B=E(s,t)
and
# = E(s,t’)
where ¢ # t’. Anyone who knows an r such that £/8' = hr can open # as s if and
only if he can also open fi’ as s. By revealing r = ¢ — t’ it is therefore possible to prove
equality of the contents of two commitments. Furthermore, ¢ — ¢’ does not contain any
information about s. It is not clear how to prove efficiently, that commitments to two
different values really do contain different values. In particular, the proofof [BCC88] that
| two blobs contain different bits given a method of proving equality does not generalize
|
to this commitment scheme.
|
Finally consider the efficiency of the commitment scheme. If p and q are constructed
by first choosing q and then determining p as the first prime congruent to 1 mod q,
heuristics show that p < q(log q)? (see [Wag79]). Thus a commitment to |q| bits requires
at most |q|+2log|q| bits. Furthermore, by first computing the product gh a commitment
to s can be done in less than 2|q| multiplications modulo p or less than two multiplications
pr. bit of s. Thus the commitment scheme is quite efficient with respect to the size of
commitments as well as the computation required.
4
Non-interactive Verifiable Secret Sharing
This section first defines verifiable secret sharing, and then the commitment scheme
described above and the Shamir scheme are combined resulting in a non-interactive
verifiable secret sharing scheme. Finally, the efficiency of the scheme is estimated.
Copyright (c) 1998, Springer-Verlag


## Page 4

132
4.1
Verification of Shares
Assume that a dealer, D, has a secret
s
€ Z, and wants to distribute it among n parties
P;,..., Pn, such that any & of the shareholders can find s if necessary, but less than
|
shareholders get no (Shannon) information about s (a (k,n)-threshold scheme). Shami
suggested that the dealer could do this by choosing a polynomial f € Z,[z] of degree a
most k —1 such that f(0) = s and then give P, the share f(i). Pj,,..., Pj, can later fin
s from the formula for f:
k
;
2-i;,..
f(z) =]oT)
jai gy EO
as
k
‘.
s=) ([]oF).
jal igg 9"
Our goal is to extend this scheme with a verification protocol, VP, such that any
|
participants, who have (honestly) accepted their shares in VP can find s. More formall
VP must satisfy:
Definition 4.1
A verification protocol, VP, takes place between the dealer and P,,...,P,.
It mus
satisfy the following two requirements:
1. If the dealer follows the distribution protocol and if the dealer and P; both folloy
VP, then P; accepts with probability 1.
2. For all subsets S; and S2 of {1,...,n} of size & such that all parties (P;)ie5, an
(Pi)ies, have accepted their shares in V P the following holds except with negligibl
probability in |q|: If s; is the secret computed by the participants in S; (for 7 = 1,2
then s; = sq.
A share is called correct, if it is accepted in VP.
Even though this definition allows any kind of interaction between the dealer and th
participants we shall only be concerned with non-interactive verification protocols here
In this case the dealer sends extra information to each participant during the distributior
and in the verification protocol P; verifies that his secret share is consistent with thi
extra information.
Definition 4.1 does not refer to the secret when defining the correctness of a share
This is in accordance with the fact that no participant have any information about
.
during the verification and therefore s could be whatever the dealer claims. After th
execution of the verification protocol the secret is defined as the value, which any
|
participants with correct shares will find when combining their shares.
If the deale
succeeds in distributing inconsistent shares, this is not well-defined, but Definition 4.
guarantees that the dealer will be caught almost always when trying to cheat.
4.2
The Scheme
Let g,h € G, be given such that the commitment scheme from Section 3 can be applied
By the fact that Z,
is a field, the dealer can distribute s € Z, as follows:
Copyright (c) 1998, Springer-Verlag


## Page 5

133
1. D publishes a commitment to s: Ey = E(s,t) for a randomly chosen t € Ziq.
2. D chooses F € Z,[z] of degree at most k — 1 satisfying F(0) = s, and computes
s; = F(t) fori=1,...,n.
Let F(z) =s+Fia+...+F,_12*-'. D chooses Gi,...,Gz-1 € Zy at random and
uses G; when committing to to F; fori =1,...,k—1. D broadcasts E; = E(F;, G;)
fori=1,...,k-—1.
3. Let G(z)
=t+ Giz +...+ G,_,2*-! and let t; = G(t) fori =1,...n. Then D
sends (s;,¢;) secretly to P; for
i= 1,2,...,n.
When P, has received his share (s;,t;) he verifies that
kat
E(si,ti)=|][ EY
(x).
7=0
Lemma 4.2
Let SC {1,...,n} be a set of & participants such that (+) holds for these & parties. Then
these & parties can find a pair (s’,t’) such that Ey = g*ht’.
Proof
Let S € {1,...,n} of size k be given. The participants in $ first find the two unique
polynomials F’ and G’ of degree at most k — 1 satisfying
F'(i)
=
Gi)
=
4;
fori € S. Now let h = g?. Then
gf @)+4dG"(4) _ E(si, ti) = git ti
fori € S. Thus (F’ + dG’)(z) is the unique polynomial of degree at most k - 1 mapping
i to 5; + dt;. Let E; = g*i. Then the polynomial
k=1
e(z) = > e;z)
j=0
satisfies e(i) = s; + dt; fori e€ S. Thus
e(z) = (F’ + dG’)(z)
and in particular
Eo = g@(9) _ gf (0)+4G'(0) _ gf OAG'(0),
|
Therefore it is sufficient to put s/ = F’(0) and t/ = G'(0).
a
The members in S do not have to find F’ in order to find the secret.
It is more
efficient to use the formula
t
$=) ais
where
a; =
| Il qo
ES
;
JE€S,j fi
Copyright (c) 1998, Springer-Verlag


## Page 6

134
Note that they can also find t by the formula
t=) ajt;.
ies
Theorem 4.3
7
Under
the assumption that the dealer cannot find log, A except with negligible probabilit
in |g|, the verification protocol satisfies Definition 4.1.
Proof
It is not hard to see that (+) will be satisfied for all participants if the dealer follows th
protocol.
Let S and S’ be two subsets of {1,...,n} of size k such that all participants in S an
S’
have accepted their shares correctly. According to Lemma 4.2 the members of S an
S" can find pairs (s,t) and (s',t’), respectively, such that Hy = E(s,t) = E(s',t’).
As the shares are consistent if and only if there is a polynomial, f, of degree at mos
k —1 such that
f@ =s;
for?=1,2,...,n
the dealer can find the two sets S and S’ as follows, if the shares are inconsistent:
1, Let f be the unique polynomial of degree at most k — 1 such that f(t) = 5 fo
*#=1,2,...,k.
2. Letei=k+1.
3. If
t > n then stop (all shares are consistent).
If f(z) = s; then put 7 :=i+1
and goto 3.
Otherwise return the sets
S = {1,2,...,k} and S’ = {1,2,...,k—1, 1}.
Thus, if the dealer has succeeded in distributing inconsistent shares, he can find log, h by
first finding S and S’ as described above and then computing log, 4 as in Theorem 3.1
a
As a consequence of Theorem 4.3 all the shares satisfying (*) are consistent unless
the dealer succeeds in finding log,(h) before the last share has been sent.
The following theorem shows, that fewer than & participants get no (Shannon) infor.
mation about the secret. For any subset S$ C {]1,.. .,n}, views denotes the messages.
that the members of 9 see:
views = (Eo, Fi, teey Ex-i, (si, ti)ies)-
Theorem 4.4
For any S C {1,...,n} of size at most k — 1 and any views
Prob[D has secret s
| views] = Prob[D has secret s]
for alls
€ Zy.
Proof
It is sufficient to prove the theorem in the case where S has size k -1. Ifk—1 parties
do not get any information about s then neither does fewer than k — 1 parties.
Copyright (c) 1998, Springer-Verlag


## Page 7

135
Let S = {1,...,4 — 1} and let views = (Eo, Fi,..., Ep—1, (8: ti)izs,...,.k-1)-
For
every s € Z,
there is exactly one t
€ Z, such that Hy = E(s,t) and there is exactly one
polynomial F of degree at most k — 1 satisfying
F(0)
=
s
Fi)
=
5
fort=1,...,k-—1
and exactly one polynomial CG of degree at most k ~— 1 satisfying
G(0)
=
¢
G(ji)
=
t
fori=1,...,k-—1
Let F(z)
= s+ Fyn +...+ Fy_iz*-! and G(x)
= t+ Gye+...+ Gp_iz*-}. In order
to show that views does not contain any information about the secret it must be shown
that F and G
satisfies
E(F;, Gi) = Ej
fori=1,...,k-1,
as this is true for the polynomials chosen by the dealer. As in the proof of Lemma 4.2
this follows from the fact that there is one and only one polynomial, f, of degree at most
k —1
satisfying (so = s, to = t)
fori = 0,1,...,4—1 and the polynomial F + dG satisfies this for d = log, h.
a
4.3
Efficiency and Security
In this section, the computational requirements of the scheme are estimated and the
|
scheme is compared to [Fel87].
|
First consider the size of the secret shares. The information rate (see [BD90]) is
|
size of secret
1
|
size of share
2°
Ignoring the time needed to evaluate F(x) and G(z) (this is reasonable as the polynomi-
als are only evaluated on small arguments), the dealer has to compute & commitments in
order to verify a share. This requires less than 2|¢|k multiplications modulo p or approx-
imately 2k multiplications pr. bit of the secret, if every element in Z, can be chosen as
the secret.
The verification requires
k — 1 exponentiations modulo p and the computation of one
commitment. This can be done in less than (again ignoring the computation of # for
j=l,...,k-1)
2|q|(& — 1) + 2|qi + (& — 1) = (2|q| + 1)k
multiplications. This is however, a pessimistic estimate as many of the exponents in the
exponentiations are rather small (in particular, for P, they all equal 1).
The scheme presented here is in many respects similar to that of [Fel87], which works
for any probabilistic encryption scheme in which a number of bits (say !) are encrypted
Copyright (c) 1998, Springer-Verlag


## Page 8

136
as the “hard-core” bits of a one-way function with homomorphic properties. Specifically,
it is suggested to use the function
zig?
forz € Z
and encrypt
| = O(log|q|) bits as g? where the / bits in question are easy to compute
from z. Using this scheme, the computational requirements when distributing an l-bits
secret is very similar to the requirements in our scheme when distributing a \q|-bits secret
(note that |g| + 2!).
With respect to security the two schemes are dual to each other, because the en-
cryption schemes used in {Fel87] only protects the secret under the assumption that the
one-way function cannot be inverted. However, even an infinitely powerful dealer can-
not distribute incorrect shares. In contrast, the new scheme protects the privacy of the
secret unconditionally, but the correctness of the shares depends on a computational
assumption.
Having these two secret sharing schemes it is natural to ask for a non-interactive
scheme in which
e no information about the secret is revealed; and
e even an infinitely powerful dealer cannot compute inconsistent shares.
However, the following shows that such a scheme is impossible in the model which is
used here.
Let namely 6 denote all the information which the dealer broadcasts in a
non-interactive secret sharing scheme, and let s; be the secret share which is sent to F.
Let V(i, b, s;) denote the verification predicate which P; computes in order to verify his
share. Now consider P;,..., Py; and assume that they have received correct shares.
Let S; be the set of shares which P; can receive:
Sx(b) = {sz
| V(k,
5, se) }.
As even an all powerful dealer cannot find inconsistent shares then P,,..., Pr-1, Py will
find the same secret for any sz € Sy. This means that P,,..., P,-1 can find the secret
by guessing a secret share s, € S; and then combine their own shares with s,.
In particular note that S;,(b) is in NP if V can be computed in polynomial time
Therefore does P;,...,P,-1 “only” need nondeterministic polynomial time in order tc
find the secret if the scheme is unconditionally secure for the shareholders. Similarly, ¢
dishonest dealer can distribute inconsistent shares in nondeterministic polynomial tim
if the scheme reveals no information about the secret.
5
Computing on Shared Secrets
As mentioned in the introduction verifiable secret sharing is an important tool in th
construction of secure protocols for multiparty computations.
In particular both th
construction in [BGW88] and [CCD88] utilize the fact that it is easy to compute linea
combinations of shared secrets. In this section we show that this is also true if the secre
sharing scheme presented here is used, and we present an application of this property.
Copyright (c) 1998, Springer-Verlag


## Page 9

|
137
§.1
Linear Combinations
Assume that two secrets s’ and s” have been distributed as described in Chapter 4.
In particular let (s/,t/) and (s/,t/’) be P,’s share of s’ and s”, respectively, and let
(Ei, Ei,...,B4_,) and (£4, EY,...,E¥_,) be the broadcasted messages when the two
secrets were distributed.
.
Each P; can compute (Eo, £1,..., £1) corresponding to a verifiable distribution of
s = s'+s" modq as
EB; =E;EY
forg=0,1...k-1.
Furthermore, P;’s secret share, (s;,¢;), of s is given by
s;
=
s+
modg
t;
=
t+t/ modgq
By insertion it is easy to see that if both (sj,
t/) and (s/’,t/') are correct shares (satisfy
(*)) then (s;,t;) is also a correct share of s; i.e.
Si
pts
i
ie-}
g ih ‘= Eo ky... Eee
.
If, instead, s is computed as s = as’ mod q for some a € Z}, then PF, can compute his
share (s;,t;) and (Eo, £i,..., #,~1) as follows
E;
=
&}
forj7=0,1,...,k-1
Ss;
=
as;modg
t;
=
atimodg
Again, it is easy to see that
Sipts
i
ka)
ght} = Bok... Ey_y.
In both of the above cases Lemma 4.2 implies that any & shareholders who have accepted
their shares of s’ and s” can find a pair (s,¢) such that
g’ ht = Eo.
Furthermore, it is an immediate consequence of Theorem 4.4 that fewer than & persons
have no information about s if s’ and s” are distributed correctly.
5.2
Choosing an Anonymous Shared Secret
In [IS91] it was shown how to set up a secret sharing scheme without a mutually trusted
authority, who knows the secret and distributes it.
In this section we show how to
achieve the same goal with verifiable secret sharing by demonstrating how n participants
can select a secret so that nobody knows it and distribute it verifiably among themselves
in a (k,n) secret sharing scheme. It is not hard to generalize the proposed method to let
l person (k <1 <n) select and distribute the secret.
Let P;,...,.P, be the n persons who want to choose a secret and distribute it among
themselves and assume that each P, can make digital signatures. The protocol for P, 1s
Copyright (c) 1998, Springer-Verlag


## Page 10

138
1. Choose sjo
€ Z, at random.
2. Distribute sjo verifiably among P,,..., Ph.
Furthermore P; signs each secret share and sends the signature with the share.
3. Verify all the received shares. If a share is incorrect, P; publishes the share and its
signature. Then P; stops.
4. Compute the share (s;,tj) of
s = 819 + 520 + Sno and the corresponding public
information (£o, £1,..., £1) as described in Subsection 5.1.
It follows from the arguments in the previous subsection that
e (s;,t;) is a correct share of s if P; has accepted all shares correctly; and
e any é participants can find a pair (s’,t’) such that Eo = E(s’,t’).
We now show thats is uniformly distributed in Z,, and that fewer than k participants
have no information about s.
Theorem 5.1
If P; chooses sjo9 € Z, uniformly at random and at most k — 1 of the other parties
cooperate, then s is uniformly distributed in Z,.
Proof
Follows from the fact that no set of at most k — 1 participants (excluding P;) get any
information about s;9. This implies that if at least one of the participants chooses sjq at
random then
§= Sipn t+ Sao +.--+
Sno
is uniformly chosen in Z,.
a
As before let views be the messages, which the participants in a subset S of {1,...,n}
see,
Theorem 5.2
For any S C {1,...,n} of size at most
k — 1 and any views
Prob{s is chosen | views] = :
for all
s € Zz, if the participants not in S follow the protocol.
Proof sketch
Under the assumptions in the theorem it follows from Theorem 5.1 that each s € Z, is
chosen with probability ;
Given S C {l,...,n} of size
k ~1 and views.
For any
s € Z, there exists
gr (k-1)—-1 = gn-* values of (sjo)j¢s such that s = jet sjo, and as in the proof of
Theorem 4.4 for each for these values of sjo (j ¢ S) there is exactly one value of tjo
which gives the same messages from P;.
7
Copyright (c) 1998, Springer-Verlag


## Page 11

139
6
Conclusion
We have presented a non-interactive verifiable (k,n)-threshold scheme which is at least
as efficient as earlier proposals. Unlike the schemes in [BGW88], [CCD88] and [RB89]
this scheme protects the secret to be distributed unconditionally for any value of k
(1 < k <n), but the correctness of the shares depends on the assumption that the
dealer cannot find discrete logarithms before the distribution has been completed. This
result is optimal because in any non-interactive verifiable secret sharing scheme, which
reveals no information about the secret, it is possible for a dishonest dealer to distribute
inconsistent shares in nondeterministic polynomial time.
The information rate of the presented scheme is $ and the distribution of a secret in
Z, as well as the verification of a share requires at most 2|q|k multiplications modulo p.
It was shown that it is very easy to compute linear combinations of shared secrets,
and in particular it was demonstrated how,
| persons, P;,...,P;, can select a secret
democratically (without knowing the secret) and distribute it verifiably to P,,...,
F,
Pi41,..-,Pp in a (k,n)-threshold scheme.
References
|
[BCC88]
G. Brassard, D. Chaum, and C. Crépeau. Minimum disclosure proofs of knowl-
edge. Journal of Computer and System Sciences, 37:156-189, 1988.
[BCP]
J. Bos, D. Chaum, and G. Purdy. A voting scheme. Preliminary draft.
[BD90]
_E. F. Brickell and D. M. Davenport. On the classification of ideal secret sharing
schemes. In Advances in Cryptology - proceedings of CRYPTO 89, pages 278
— 285, 1990.
[Ben87]
J. C. Benaloh.
Secret sharing homomorphisms: Keeping shares of a secret
secret. In Advances in Cryptology - proceedings of CRYPTO 86, Lecture Notes
in Computer Science, pages 251-260. Springer-Verlag, 1987.
[Bla79]
G.R. Blakley. Safeguarding cryptographic keys. In Proceedings AFIPS 1979
Nat. Computer Conf., pages 313 - 319, 1979.
[BM84]
M. Blum and S. Micali. How to generate cryptographically strong sequences
of pseudo-random bits. SIAM Journal of Computation, 13:850-864, 1984.
[BGW88] M. Ben-Or, S. Goldwasser, and A. Widgerson.
Completeness theorems for
non-cryptographic fault-tolerant distributed computation. In Proceedings of
the Twentieth Annual ACM Symposium on Theory of Computing, pages 1-10,
1988.
[(CCD88]
D. Chaum, C. Crépeau, and I. Damgard. Multiparty unconditionally secure
protocols. In Proceedings of the Twentieth Annual ACM Symposium on Theory
of Computing, pages 11-19, 1988.
[Fel87]
 P. Feldman. A practical scheme for non-interactive verifiable secret sharing.
In Proceedings of the 28th IEEE Symposium on the Foundations of Computer
Sctence, pages 427 — 437, 1987.
Copyright (c) 1998, Springer-Verlag


## Page 12

140
{1S91]
I. Ingemarsson and G. J. Simmons. A protocol to set up shared secret schemes
without the assistance of a mutually trusted party. In Advances in Cryptology
- proceedings of EUROCRYPT 90, Lecture Notes in Computer Science, pages
266 — 282. Springer-Verlag, 1991.
.
[Ped91]
T.P. Pedersen. Distributed provers with applications to undeniable signatures,
1991. To appear in the proceedings of Eurocrypt’91.
[RB89]
TT. Rabin and M. Ben-Or. Verifiable secret sharing and multiparty protocols
with honest majority. In Proceedings of the 21st Annual ACM Symposium on
the Theory of Computing, pages 73 — 85, 1989.
[Sha79]
A. Shamir. How to share a secret. Communications of the ACM, 22:612-613,
1979.
[Sim90]
 G. J. Simmons. How to (really) share a secret. In Advances in Cryptology -
proceedings of CRYPTO 88, Lecture Notes in Computer Science, pages 390 -
448. Springer-Verlag, 1990.
[Wag79]
S.S. Wagstaff Jr. Greatest of the least primes in arithmetic progression having
a given modulus.
Mathematics of Computation, 33(147):1073 - 1080, July
1979.
Copyright (c) 1998, Springer-Verlag
