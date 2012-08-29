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
26:  END :: types
27:  
28:  BEGIN :: func:setup
29:  input := None
30:  g := random(G1)
31:  g_2 := random(G2)
32:  gpk := list{g, g_2}
33:  
34:  output := gpk
35:  END :: func:setup
36:  
37:  BEGIN :: func:authsetup
38:  input := list{gpk, authS}
39:  gpk := expand{g, g_2}
40:  
41:  Y := len(authS)
42:  BEGIN :: for
43:  for{i := 0, Y}
44:  alpha := random(ZR)
45:  y := random(ZR)
46:  z := authS#i
47:  eggalph := e(g, g_2)^alpha
48:  g2y := g_2^y
49:  msk#z := list{alpha, y}
50:  pk#z := list{eggalph, g2y}
51:  END :: for
52:  
53:  output := list{msk, pk}
54:  END :: func:authsetup
55:  
56:  BEGIN :: func:keygen
57:  input := list{gpk, msk, gid, userS}
58:  userSBlinded := userS
59:  gidBlinded := gid
60:  zz := random(ZR)
61:  gpk := expand{g, g_2}
62:  h := H(gidBlinded,G1)
63:  
64:  deleteMeVar := msk#0#0
65:  blindingFactor_deleteMeVarBlinded := random(ZR)
66:  deleteMeVarBlinded := deleteMeVar ^ (1/blindingFactor_deleteMeVarBlinded)
67:  
68:  Y := len(userS)
69:  BEGIN :: for
70:  for{i := 0,Y}
71:  z := userS#i
72:  K#z := ((g^msk#z#0) * (h^msk#z#1))
73:  END :: for
74:  
75:  BEGIN :: forall
76:  forall{y := K}
77:  blindingFactor_KBlinded#y := random(ZR)
78:  KBlinded#y := (K#y^(1 / blindingFactor_KBlinded#y))
79:  END :: forall
80:  sk := list{gidBlinded, userSBlinded, KBlinded, deleteMeVarBlinded}
81:  skBlinded := list{gidBlinded, userSBlinded, KBlinded, deleteMeVarBlinded}
82:  output := list{blindingFactor_deleteMeVarBlinded, blindingFactor_KBlinded, skBlinded}
83:  END :: func:keygen
84:  
85:  BEGIN :: func:encrypt
86:  input := list{pk, gpk, M, policy_str}
87:  gpk := expand{g, g_2}
88:  
89:  policy := createPolicy(policy_str)
90:  attrs := getAttributeList(policy)
91:  egg := e(g,g_2)
92:  R := random(GT)
93:  hashRandM := list{R,M}
94:  s := H(hashRandM,ZR)
95:  s_sesskey := DeriveKey(R)
96:  C0 := (R * (egg^s))
97:  w := 0
98:  s_sh := calculateSharesDict(s, policy)
99:  w_sh := calculateSharesDict(w, policy)
100:  Y := len(s_sh)
101:  
102:  BEGIN :: for
103:  for{y := 0, Y}
104:  r := random(ZR)
105:  k := attrs#y
106:  C1#k := (egg ^ s_sh#k) * (pk#k#0 ^ r)
107:  C2#k := g_2^r
108:  C3#k := (pk#k#1 ^ r) * (g_2 ^ w_sh#k)
109:  T1 := SymEnc(s_sesskey , M)
110:  END :: for
111:  
112:  ct := list{policy_str, C0, C1, C2, C3, T1}
113:  output := ct
114:  END :: func:encrypt
115:  
116:  
117:  # change rule for moving exp into a variable : only if it's a negative exponent! nothing else!
118:  BEGIN :: func:transform
119:  input := list{gpk, skBlinded, ct}
120:  gpk := expand{g, g_2}
121:  ct := expand{policy_str, C0, C1, C2, C3, T1}
122:  skBlinded := expand{gid, userS, K, deleteMeVar}
123:  policy := createPolicy(policy_str)
124:  attrs := prune(policy, userS)
125:  coeff := getCoefficients(policy)
126:  h_gid := H(gid,G1)
127:  Y := len(attrs)
128:  A := (prod{y := attrs#1,Y} on (((C1#y^coeff#y) * e((h_gid^coeff#y),C3#y)) * e((K#y^-coeff#y),C2#y)))
129:  T0 := C0
130:  T2 := A
131:  partCT := symmap{T0, T1, T2}
132:  output := partCT
133:  END :: func:transform
134:  
135:  BEGIN :: func:decout
136:  input := list{partCT, blindingFactor_deleteMeVarBlinded, blindingFactor_KBlinded, egg}
137:  partCT := expand{T0, T1, T2}
138:  R := T0 / (T2^zz)
139:  s_sesskey := DeriveKey( R )
140:  M := SymDec(s_sesskey, T1)
141:  hashRandM := list{R,M}
142:  s := H(hashRandM,ZR)
143:  BEGIN :: if
144:  if { (T0 == (R * (egg ^ s))) and (T2 == (egg ^ (s / zz))) }
145:  output := M
146:  else
147:  error('invalid ciphertext')
148:  END :: if
149:  END :: func:decout
