f = open('invalidSigsDistro_BatInd', 'w')

for i in range(0, 4):
	f.write("0.0\n")

for i in range(0, 71):
	f.write(str(i * (0.50/71))+"\n")

'''
for i in range(0, 31):
	calc = i * (0.375/31)
	calc += 0.125
	f.write(str(calc) + "\n")
'''

'''
for i in range(0, NUMIT):
	f.write(str(i * (0.50/NUMIT))+"\n")

for i in range(NUMIT, 0, -1):
	f.write(str(i * (0.50/NUMIT))+"\n")
'''
f.close()
