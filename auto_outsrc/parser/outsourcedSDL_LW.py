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
19:  M:= str
20:  K := list
21:  C1 := list
22:  C2 := list
23:  C3 := list
24:  gid := str
25:  KBlinded := list
26:  blindingFactor_KBlinded := list
27:  END :: types
28:  
29:  BEGIN :: func:setup
30:  input := None
31:  g := random(G1)
32:  g_2 := random(G2)
33:  gpk := list{g, g_2}
34:  
35:  output := gpk
36:  END :: func:setup
37:  
38:  BEGIN :: func:authsetup
39:  input := list{gpk, authS}
40:  gpk := expand{g, g_2}
41:  
42:  Y := len(authS)
43:  BEGIN :: for
44:  for{i := 0, Y}
45:  alpha := random(ZR)
46:  y := random(ZR)
47:  z := authS#i
48:  eggalph := e(g, g_2)^alpha
49:  g2y := g_2^y
50:  msk#z := list{alpha, y}
51:  pk#z := list{eggalph, g2y}
52:  END :: for
53:  
54:  output := list{msk, pk}
55:  END :: func:authsetup
56:  
57:  BEGIN :: func:keygen
58:  input := list{gpk, msk, gid, userS}
59:  userSBlinded := userS
60:  gidBlinded := gid
61:  zz := random(ZR)
62:  gpk := expand{g, g_2}
63:  h := H(gidBlinded,G1)
64:  
65:  deleteMeVar := msk#0#0
66:  blindingFactor_deleteMeVarBlinded := random(ZR)
67:  deleteMeVarBlinded := deleteMeVar ^ (1/blindingFactor_deleteMeVarBlinded)
68:  
69:  Y := len(userS)
70:  BEGIN :: for
71:  for{i := 0,Y}
72:  z := userS#i
73:  K#z := ((g^msk#z#0) * (h^msk#z#1))
74:  END :: for
75:  
76:  BEGIN :: forall
77:  forall{y := K}
78:  blindingFactor_KBlinded#y := random(ZR)
79:  KBlinded#y := (K#y^(1 / blindingFactor_KBlinded#y))
80:  END :: forall
81:  sk := list{gidBlinded, userSBlinded, KBlinded, deleteMeVarBlinded}
82:  skBlinded := list{gidBlinded, userSBlinded, KBlinded, deleteMeVarBlinded}
83:  output := list{blindingFactor_deleteMeVarBlinded, blindingFactor_KBlinded, skBlinded}
84:  END :: func:keygen
85:  
86:  BEGIN :: func:encrypt
87:  input := list{pk, gpk, M, policy_str}
88:  gpk := expand{g, g_2}
89:  
90:  policy := createPolicy(policy_str)
91:  attrs := getAttributeList(policy)
92:  egg := e(g,g_2)
93:  R := random(GT)
94:  hashRandM := list{R,M}
95:  s := H(hashRandM,ZR)
96:  s_sesskey := DeriveKey(R)
97:  C0 := (R * (egg^s))
98:  w := 0
99:  s_sh := calculateSharesDict(s, policy)
100:  w_sh := calculateSharesDict(w, policy)
101:  Y := len(s_sh)
102:  
103:  BEGIN :: for
104:  for{y := 0, Y}
105:  r := random(ZR)
106:  k := attrs#y
107:  C1#k := (egg ^ s_sh#k) * (pk#k#0 ^ r)
108:  C2#k := g_2^r
109:  C3#k := (pk#k#1 ^ r) * (g_2 ^ w_sh#k)
110:  T1 := SymEnc(s_sesskey , M)
111:  END :: for
112:  
113:  ct := list{policy_str, C0, C1, C2, C3, T1}
114:  output := ct
115:  END :: func:encrypt
116:  
117:  
118:  # change rule for moving exp into a variable : only if it's a negative exponent! nothing else!
119:  BEGIN :: func:transform
120:  input := list{gpk, skBlinded, ct}
121:  gpk := expand{g, g_2}
122:  ct := expand{policy_str, C0, C1, C2, C3, T1}
123:  skBlinded := expand{gid, userS, K, deleteMeVar}
124:  policy := createPolicy(policy_str)
125:  attrs := prune(policy, userS)
126:  coeff := getCoefficients(policy)
127:  h_gid := H(gid,G1)
128:  Y := len(attrs)
129:  A := (prod{y := attrs#1,Y} on (((C1#y^coeff#y) * e((h_gid^coeff#y),C3#y)) * e((K#y^-coeff#y),C2#y)))
130:  T0 := C0
131:  T2 := A
132:  partCT := symmap{T0, T1, T2}
133:  output := partCT
134:  END :: func:transform
135:  
136:  BEGIN :: func:decout
137:  input := list{partCT, blindingFactor_deleteMeVarBlinded, blindingFactor_KBlinded, egg}
138:  partCT := expand{T0, T1, T2}
139:  R := T0 / (T2^zz)
140:  s_sesskey := DeriveKey( R )
141:  M := SymDec(s_sesskey, T1)
142:  hashRandM := list{R,M}
143:  s := H(hashRandM,ZR)
144:  BEGIN :: if
145:  if { (T0 == (R * (egg ^ s))) and (T2 == (egg ^ (s / zz))) }
146:  output := M
147:  else
148:  error('invalid ciphertext')
149:  END :: if
150:  END :: func:decout
