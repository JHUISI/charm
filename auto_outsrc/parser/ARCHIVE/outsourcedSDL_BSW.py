1:  name := bsw07
2:  setting := asymmetric
3:  
4:  BEGIN :: types
5:  policy_str := str
6:  policy := object
7:  attrs := list
8:  sh := list
9:  coeff := list
10:  share := list
11:  S := list
12:  M:= str
13:  Dj := list
14:  Djp := list
15:  Cr := list
16:  Cpr := list
17:  DjBlinded := list
18:  DjpBlinded := list
19:  END :: types
20:  
21:  BEGIN :: func:setup
22:  input := None
23:  g := random(G1)
24:  g2 := random(G2)
25:  alpha := random(ZR)
26:  beta := random(ZR)
27:  
28:  h := g^beta
29:  f := g^(1/beta)
30:  i := g2^alpha
31:  egg := e(g, g2)^alpha
32:  
33:  mk := list{beta, i}
34:  pk := list{g, g2, h, f, egg}
35:  
36:  output := list{mk, pk}
37:  END :: func:setup
38:  
39:  
40:  BEGIN :: func:keygen
41:  input := list{pk, mk, S} 
42:  SBlinded := S
43:  zz := random(ZR)
44:  
45:  r := random(ZR)
46:  p0 := (pk#1^r)
47:  D := ((mk#1 * p0)^(1 / mk#0))
48:  DBlinded := D ^ (1/zz)
49:  
50:  Y := len(S)
51:  BEGIN :: for
52:  for{y := 0,Y}
53:  s_y := random(ZR)
54:  y0 := S#y
55:  Dj#y0 := (p0 * (H(y0,G2)^s_y))
56:  BEGIN :: forall
57:  forall{y := Dj}
58:  DjBlinded#y := Dj#y ^ (1/zz)
59:  END :: forall
60:  Djp#y0 := (g^s_y)
61:  BEGIN :: forall
62:  forall{y := Djp}
63:  DjpBlinded#y := Djp#y ^ (1/zz)
64:  END :: forall
65:  END :: for
66:  
67:  sk := list{SBlinded, DBlinded, DjBlinded, DjpBlinded}
68:  skBlinded := list{SBlinded, DBlinded, DjBlinded, DjpBlinded}
69:  output := list{zz, skBlinded}
70:  END :: func:keygen
71:  
72:  
73:  BEGIN :: func:encrypt
74:  input := list{pk, M, policy_str}
75:  pk := expand{g, g2, h, f, egg}
76:  
77:  policy := createPolicy(policy_str)
78:  attrs := getAttributeList(policy)
79:  R := random(GT)
80:  s := H(list{R,M},ZR)
81:  s_sesskey := DeriveKey(R)
82:  Ctl := (R * (egg^s))
83:  sh := calculateSharesDict(s, policy)
84:  Y := len(sh)
85:  
86:  C    := h ^ s
87:  
88:  BEGIN :: for
89:  for{y := 0, Y}
90:  y1 := attrs#y
91:  share#y1 := sh#y1
92:  Cr#y1 := g ^ share#y1
93:  Cpr#y1 := (H(y1, G2))^share#y1
94:  END :: for
95:  T1 := SymEnc(s_sesskey , M)
96:  
97:  ct := list{policy_str, Ctl, C, Cr, Cpr, T1}
98:  output := ct
99:  END :: func:encrypt
100:  
101:  
102:  BEGIN :: func:transform
103:  input := list{pk, skBlinded, ct}
104:  ct := expand{policy_str, Ctl, C, Cr, Cpr, T1}
105:  skBlinded := expand{S, D, Dj, Djp}
106:  policy := createPolicy(policy_str)
107:  attrs := prune(policy, S)
108:  coeff := getCoefficients(policy)
109:  Y := len(attrs)
110:  A := (prod{y := attrs#1,Y} on (e((Cr#y^-coeff#y),Dj#y) * e((Djp#y^coeff#y),Cpr#y)))
111:  result0 := (e(C,D) * A)
112:  T0 := Ctl
113:  T2 := result0
114:  partCT := list{T0, T1, T2}
115:  output := partCT
116:  END :: func:transform
117:  
118:  BEGIN :: func:decout
119:  input := list{partCT, zz, egg}
120:  partCT := expand{T0, T1, T2}
121:  R := T0 / (T2^zz)
122:  s_sesskey := DeriveKey( R )
123:  M := SymDec(s_sesskey, T1)
124:  hashRandM := list{R, M}
125:  s := H(hashRandM, ZR)
126:  BEGIN :: if
127:  if { (T0 == (R * (egg ^ s))) and (T2 == (egg ^ (s / zz))) }
128:  output := M
129:  else
130:  error('invalid ciphertext')
131:  END :: if
132:  END :: func:decout
