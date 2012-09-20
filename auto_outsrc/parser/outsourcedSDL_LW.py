1:  name := lw10
2:  setting := asymmetric
3:  
4:  BEGIN :: types
5:  msk := list
6:  pk1 := list{GT, G2}
7:  pk := list{pk1, None}
8:  sk := list
9:  ct := list
10:  policy_str := str
11:  policy := object
12:  attrs := list
13:  s_sh := list
14:  w_sh := list
15:  coeff := list
16:  share := list
17:  authS := list
18:  userS := list
19:  M := GT
20:  K := list
21:  C1 := list
22:  C2 := list
23:  C3 := list
24:  gid := str
25:  END :: types
26:  
27:  BEGIN :: func:setup
28:  input := None
29:  g := random(G1)
30:  g_2 := random(G2)
31:  gpk := list{g, g_2}
32:  
33:  output := gpk
34:  END :: func:setup
35:  
36:  BEGIN :: func:authsetup
37:  input := list{gpk, authS}
38:  gpk := expand{g, g_2}
39:  
40:  Y := len(authS)
41:  BEGIN :: for
42:  for{i := 0, Y}
43:  alpha := random(ZR)
44:  y := random(ZR)
45:  z := authS#i
46:  eggalph := e(g, g_2)^alpha
47:  g2y := g_2^y
48:  msk#z := list{alpha, y}
49:  pk#z := list{eggalph, g2y}
50:  END :: for
51:  
52:  output := list{msk, pk}
53:  END :: func:authsetup
54:  
55:  BEGIN :: func:keygen
56:  input := list{gpk, msk, gid, userS}
57:  gpk := expand{g, g_2}
58:  h := H(gid, G1)
59:  
60:  deleteMeVar := msk#0#0
61:  
62:  Y := len(userS)
63:  BEGIN :: for
64:  for{i := 0, Y}
65:  z := userS#i
66:  K#z := (g ^ msk#z#0) * (h ^ msk#z#1)
67:  END :: for
68:  
69:  sk := list{gid, userS, K, deleteMeVar}
70:  output := sk
71:  END :: func:keygen
72:  
73:  BEGIN :: func:encrypt
74:  input := list{pk, gpk, M, policy_str}
75:  gpk := expand{g, g_2}
76:  
77:  policy := createPolicy(policy_str)
78:  attrs := getAttributeList(policy)
79:  s := random(ZR)
80:  w := 0
81:  s_sh := calculateSharesDict(s, policy)
82:  w_sh := calculateSharesDict(w, policy)
83:  Y := len(s_sh)
84:  egg := e(g,g_2)
85:  C0 := (M * (egg^s))
86:  
87:  BEGIN :: for
88:  for{y := 0, Y}
89:  r := random(ZR)
90:  k := attrs#y
91:  C1#k := (egg ^ s_sh#k) * (pk#k#0 ^ r)
92:  C2#k := g_2^r
93:  C3#k := (pk#k#1 ^ r) * (g_2 ^ w_sh#k)
94:  END :: for
95:  
96:  ct := list{policy_str, C0, C1, C2, C3}
97:  output := ct
98:  END :: func:encrypt
99:  
100:  BEGIN :: func:decrypt
101:  input := list{gpk, sk, ct}
102:  gpk := expand{g, g_2}
103:  ct := expand{policy_str, C0, C1, C2, C3}
104:  sk := expand{gid, userS, K, deleteMeVar}
105:  
106:  policy := createPolicy(policy_str)
107:  attrs  := prune(policy, userS)
108:  coeff := getCoefficients(policy)
109:  h_gid := H(gid, G1)
110:  
111:  Y := len(attrs)
112:  A := { prod{y := attrs#1, Y} on (((C1#y * e(h_gid, C3#y)) / e(K#y, C2#y))^coeff#y) }
113:  
114:  M := C0 / A
115:  output := M
116:  END :: func:decrypt
117:  
118:  # change rule for moving exp into a variable : only if it's a negative exponent! nothing else!
