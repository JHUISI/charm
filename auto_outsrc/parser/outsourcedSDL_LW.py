1:  name := bls
2:  # number of signatures in a batch
3:  N := 100
4:  setting := asymmetric
5:  
6:  # types for variables used in verification.
7:  # all other variable types are inferred by SDL parser
8:  BEGIN :: types
9:  h := G1
10:  sig := G1
11:  g := G2
12:  pk := G2
13:  M := str
14:  END :: types
15:  
16:  BEGIN :: func:init
17:  input := None
18:  tempVar := random(G2)
19:  output := None
20:  END :: func:init
21:  
22:  # description of key generation and signing algorithms
23:  BEGIN :: func:keygen
24:  input := None
25:   g := random(G2)
26:   x := random(ZR)
27:   pk := g^x
28:   sk := x
29:  output := list{pk, sk, g}
30:  END :: func:keygen
31:  
32:  BEGIN :: func:sign
33:  input := list{sk, M}
34:   sig := (H(M, G1))^sk
35:  output := sig
36:  END :: func:sign
37:  
38:  BEGIN :: func:verify
39:   input := list{pk, M, sig, g}
40:   h := H(M, G1)
41:   verify := {e(h, pk) == e(sig, g)}
42:   output := verify 
43:  END :: func:verify
44:  
45:  BEGIN :: func:main
46:  input := None
47:  tempVar2 := random(ZR)
48:  output := None
49:  END :: func:main
50:  
51:  constant := g
52:  public :=  pk
53:  signature :=  sig
54:  message :=  h
55:  
56:  # single signer
57:  BEGIN :: count
58:  message_count := N
59:  public_count := one
60:  signature_count := N
61:  END :: count
62:  
63:  # variables computed before each signature verification
64:  BEGIN :: precompute
65:    h := H(M, G1)
66:  END :: precompute
67:  
68:  # individual verification check
69:  verify := {e(h, pk) == e(sig, g)}
