1:  name := ibeckrs09 
2:  setting := asymmetric
3:  
4:  BEGIN :: types
5:  n := ZR
6:  l := ZR
7:  M := GT
8:  mpk := list
9:  sk := list
10:  ct := list
11:  hl := list
12:  gl := list
13:  #c := list
14:  #d := list
15:  z := list
16:  #testList := list
17:  id := str
18:  transformOutputList := list
19:  END :: types
20:  
21:  BEGIN :: func:setup
22:  input := list{n, l}
23:  alpha := random(ZR)
24:  t1 := random(ZR)
25:  t2 := random(ZR)
26:  t3 := random(ZR)
27:  t4 := random(ZR)
28:  g := random(G1) 
29:  #h := random(G1)
30:  h := random(G2)
31:  omega := e(g, h)^(t1 * (t2 * alpha))
32:  BEGIN :: for
33:  for{y := 0, n}
34:  z#y := random(ZR) # n of these
35:  gl#y := g ^ z#y
36:  hl#y := h ^ z#y
37:  END :: for
38:  
39:  v1 := g ^ t1
40:  v2 := g ^ t2
41:  v3 := g ^ t3
42:  v4 := g ^ t4
43:  
44:  mpk := list{omega, g, h, gl, hl, v1, v2, v3, v4, n, l}
45:  msk := list{alpha, t1, t2, t3, t4}
46:  
47:  output := list{mpk, msk}
48:  END :: func:setup
49:  
50:  
51:  BEGIN :: func:extract
52:  input := list{mpk, msk, id}
53:  blindingFactord0Blinded := random(ZR)
54:  blindingFactord1Blinded := random(ZR)
55:  blindingFactord2Blinded := random(ZR)
56:  blindingFactor0Blinded := random(ZR)
57:  blindingFactor1Blinded := random(ZR)
58:  idBlinded := id
59:  zz := random(ZR)
60:  mpk := expand{omega, g, h, gl, hl, v1, v2, v3, v4, n, l}
61:  msk := expand{alpha, t1, t2, t3, t4}
62:  
63:  r1 := random(ZR)
64:  r2 := random(ZR)
65:  hID := strToId(mpk, id)
66:  hashIDDotProd := (prod{y := 0,n} on (hl#y^hID#y))
67:  hashID := (hl#0 * hashIDDotProd)
68:  
69:  
70:  d0 := (h^((r1 * (t1 * t2)) + (r2 * (t3 * t4))))
71:  d0Blinded := d0 ^ (1/blindingFactord0Blinded)
72:  
73:  halpha := (h^-alpha)
74:  hashID2r1 := (hashID^-r1)
75:  
76:  
77:  
78:  d1 := ((halpha^t2) * (hashID2r1^t2))
79:  d1Blinded := d1 ^ (1/blindingFactord1Blinded)
80:  
81:  
82:  d2 := ((halpha^t1) * (hashID2r1^t1))
83:  d2Blinded := d2 ^ (1/blindingFactord2Blinded)
84:  
85:  hashID2r2 := (hashID^-r2)
86:  
87:  
88:  d3 := (hashID2r2^t4)
89:  d3Blinded := d3 ^ (1/blindingFactor0Blinded)
90:  
91:  
92:  d4 := (hashID2r2^t3)
93:  d4Blinded := d4 ^ (1/blindingFactor1Blinded)
94:  
95:  
96:  
97:  
98:  
99:  
100:  
101:  sk := list{idBlinded, d0Blinded, d1Blinded, d2Blinded, d3Blinded, d4Blinded}
102:  skBlinded := list{idBlinded, d0Blinded, d1Blinded, d2Blinded, d3Blinded, d4Blinded}
103:  output := list{blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor0Blinded, blindingFactor1Blinded, blindingFactor1Blinded, skBlinded}
104:  END :: func:extract
105:  
106:  
107:  BEGIN :: func:encrypt
108:  input := list{mpk, M, id}
109:  mpk := expand{omega, g, h, gl, hl, v1, v2, v3, v4, n, l}
110:  
111:  s := random(ZR)
112:  s1 := random(ZR)
113:  s2 := random(ZR)
114:  
115:  hID1 := strToId(mpk, id) # list <-: strToId(list, str)
116:  hashID1DotProd := (prod{y := 0, n} on { gl#y ^ hID1#y })
117:  hashID1 := gl#0 * hashID1DotProd
118:  
119:  cpr := (omega ^ s) * M
120:  c0 := hashID1 ^ s
121:  c1 := v1 ^ (s - s1)
122:  c2 := v2 ^ s1
123:  c3 := v3 ^ (s - s2)
124:  c4 := v4 ^ s2
125:  
126:  ct := list{c0, c1, c2, c3, c4, cpr}
127:  output := ct
128:  END :: func:encrypt
129:  
130:  BEGIN :: func:transform
131:  input := list{sk, ct}
132:  sk := expand{id, d0, d1, d2, d3, d4}
133:  ct := expand{c0, c1, c2, c3, c4, cpr}
134:  transformOutputList#0 := e(c0,d0)
135:  transformOutputList#1 := e(c1,d1)
136:  transformOutputList#2 := e(c2,d2)
137:  transformOutputList#3 := e(c3,d3)
138:  transformOutputList#4 := e(c4,d4)
139:  output := transformOutputList
140:  END :: func:transform
141:  
142:  BEGIN :: func:decout
143:  input := list{sk, ct, transformOutputList, blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor0Blinded, blindingFactor1Blinded, blindingFactor1Blinded}
144:  sk := expand{id, d0, d1, d2, d3, d4}
145:  ct := expand{c0, c1, c2, c3, c4, cpr}
146:  result := (transformOutputList#0 ^ (blindingFactord0Blinded) ) * (transformOutputList#1 ^ (blindingFactord1Blinded) ) * (transformOutputList#2 ^ (blindingFactord2Blinded) ) * (transformOutputList#3 ^ (blindingFactor0Blinded) ) * (transformOutputList#4 ^ (blindingFactor1Blinded) )
147:  M := (cpr * result)
148:  output := M
149:  END :: func:decout

