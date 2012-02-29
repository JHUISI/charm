NUMIT = 75

f = open('invalidSigsDistro', 'w')
for i in range(0, NUMIT):
	f.write(str(i * (0.30/NUMIT))+"\n")

f.close()
