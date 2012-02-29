f = open("IndLine", "w")

for i in range(0, 750):
	f.write(str(i*100 + 50) + " 65\n")

f.close()
