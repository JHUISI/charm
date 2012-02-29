f = open('DELETEME_INVALID_SIGS_LINEAR.dat', 'w')

for i in range(4950, 75950, 100):
	outputStr = str(i)
	calcValue = (0.00000766368 * float(i)) - 0.116388
	outputStr += " " + str(calcValue)
	outputStr += "\n"
	f.write(outputStr)

f.close()

'''
f = open('invalid_Line_Eq_1.dat', 'w')

for i in range(12950, 47650, 100):
	outputStr = str(i)
	calcValue = (0.00000348582 * float(i)) - 0.0484648
	outputStr += " " + str(calcValue)
	outputStr += "\n"
	f.write(outputStr)

f.close()

f = open('invalid_Line_Eq_2.dat', 'w')

for i in range(47650, 74950, 100):
	outputStr = str(i)
	calcValue = (0.0000121281 * float(i)) - 0.455481
	outputStr += " " + str(calcValue)
	outputStr += "\n"
	f.write(outputStr)

f.close()
'''



'''
m               = 7.66368e-06      +/- 1.508e-08    (0.1967%)
b               = -0.116388        +/- 0.0007161    (0.6153%)
'''
