f = open('invalidPulsatingDistro', 'w')

for i in range(0, 15):
	f.write("0.15\n")

for i in range(15, 30):
	f.write("0.0\n")

for i in range(30, 45):
	f.write("0.15\n")

for i in range(45, 60):
	f.write("0.0\n")

for i in range(60, 75):
	f.write("0.15\n")

f.close()
