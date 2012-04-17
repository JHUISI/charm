1:  name := dsewaters09
2:  setting := symmetric
3:  
4:  BEGIN :: types
5:  M:= str
6:  C := list
7:  D := list
8:  mpk := list
9:  msk := list
10:  sk := list
11:  ct := list
12:  
13:  DBlinded := list
14:  END :: types
15:  
16:  BEGIN :: func:setup
17:  input := None
18:  g := random(G1)
19:  w := random(G1) 
20:  u := random(G1)
21:  h := random(G1)
22:  v := random(G1)
23:  v1 := random(G1)
24:  v2 := random(G1)
25:  a1 := random(ZR)
26:  a2 := random(ZR) 
27:  b := random(ZR) 
28:  alpha := random(ZR)
29:          
30:  gb := g ^ b
31:  ga1 := g ^ a1
32:  ga2 := g ^ a2
33:  gba1 := gb ^ a1
34:  gba2 := gb ^ a2
35:  tau1 := v * (v1 ^ a1)
36:  tau2 := v * (v2 ^ a2)        
37:  tau1b := tau1 ^ b
38:  tau2b := tau2 ^ b
39:  egga := e(g, g)^(alpha * (a1 * b)) 
40:  galpha := g ^ alpha
41:  galpha_a1 := galpha ^ a1
42:  
43:  mpk := list{g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga}
44:  msk := list{galpha, galpha_a1, v, v1, v2, alpha}
45:  
46:  output := list{mpk, msk}
47:  END :: func:setup
48:  
49:  
50:  BEGIN :: func:keygen
51:  input := list{mpk, msk, id}
52:  idBlinded := id
53:  zz := random(ZR)
54:  mpk := expand{g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga}
55:  msk := expand{galpha, galpha_a1, v, v1, v2, alpha}
56:  
57:  r1 := random(ZR)
58:  r2 := random(ZR)
59:  z1 := random(ZR)
60:  z2 := random(ZR)
61:  tag_k := random(ZR)
62:  tag_kBlinded := tag_k ^ (1/zz)
63:  
64:  r := (r1 + r2)
65:  id_hash := H(idBlinded,ZR)
66:  
67:  D#1 := (galpha_a1 * (v^r))
68:  D#2 := ((g^-alpha) * ((v1^r) * (g^z1)))
69:  D#3 := (gb^-z1)
70:  D#4 := ((v2^r) * (g^z2))
71:  D#5 := (gb^-z2)
72:  D#6 := (gb^r2)
73:  D#7 := (g^r1)
74:  BEGIN :: forall
75:  forall{y := D}
76:  DBlinded#y := (D#y^(1 / zz))
77:  END :: forall
78:  K := ((((u^id_hash) * (w^tag_kBlinded_k)) * h)^r1)
79:  KBlinded := (K^(1 / zz))
80:  
81:  sk := list{idBlinded, DBlinded, KBlinded, tag_kBlinded}
82:  skBlinded := list{idBlinded, DBlinded, KBlinded, tag_kBlinded}
83:  output := list{zz, skBlinded}
84:  END :: func:keygen
85:  
86:  
87:  BEGIN :: func:encrypt
88:  input := list{mpk, M, id}
89:  mpk := expand{g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga}
90:  
91:  s1 := random(ZR) 
92:  R := random(GT)
93:  s2 := H(list{R,M},ZR)
94:  s2_sesskey := SHA1(R)
95:  C#0 := (R * (egga^s2))
96:  t := random(ZR)
97:  tag_c := random(ZR)
98:  s := s1 + s2
99:  id_hash2 := H(id, ZR)
100:          
101:  C#1 := gb ^ s
102:  C#2 := gba1 ^ s1
103:  C#3 := ga1 ^ s1
104:  C#4 := gba2 ^ s2
105:  C#5 := ga2 ^ s2
106:  C#6 := (tau1 ^ s1) * (tau2 ^ s2)
107:  C#7 := (((tau1b ^ s1) * (tau2b ^ s2)) * (w ^ -t))
108:  E1 := (((u ^ id_hash2) * (w ^ tag_c)) * h) ^ t
109:  E2 := g ^ t
110:  T1 := SymEnc(s2_sesskey , M)
111:  
112:  ct := list{C, E1, E2, tag_c, T1}
113:  output := ct
114:  END :: func:encrypt
115:  
116:  BEGIN :: func:transform
117:  input := list{ct, sk}
118:  sk := expand{id, D, K, tag_k}
119:  ct := expand{C, E1, E2, tag_c, T1}
120:  tag := (1 / (tag_c - tag_k))
121:  A1 := (e(C#1,D#1) * (e(C#2,D#2) * (e(C#3,D#3) * (e(C#4,D#4) * e(C#5,D#5)))))
122:  A2 := (e(C#6,D#6) * e(C#7,D#7))
123:  A3 := (A1 / A2)
124:  A4 := (e((E1^tag),D#7) * e((E2^-tag),K))
125:  T2 := (A3 / A4)
126:  T0 := C#0
127:  partCT := list{T0, T1, T2}
128:  output := partCT
129:  END :: func:transform
130:  
131:  BEGIN :: func:decout
132:  input := list{partCT, zz, egga}
133:  partCT := expand{T0, T1, T2}
134:  R := T0 / (T2^zz)
135:  s2_sesskey := SHA1( R )
136:  M := SymDec(s2_sesskey, T1)
137:  s2 := H(list{R, M}, ZR)
138:  BEGIN :: if
139:  if { (T0 == (R * (egga ^ s2))) and (T2 == (R * (egga ^ (s2 / zz)))) }
140:  output := M
141:  else
142:  error('invalid ciphertext')
143:  END :: if
144:  END :: func:decout
