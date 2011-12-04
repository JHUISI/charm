import sys, random, os

if __name__ == "__main__":
	if ( (len(sys.argv) != 4) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python generate_messages.py [number of messages to generate] [size in bytes of each message] [name to be prepended to filename of each message]")

	numMessages = int(sys.argv[1])
	messageSize = int(sys.argv[2])
	filenamePrefix = sys.argv[3]

	for index in range(0, numMessages):
		f = open(filenamePrefix + str(index) + "_message", 'wb')
		randomData = os.urandom(messageSize)
		f.write(randomData)
		f.close()
		del f

		'''
		byteArr = bytearray(randomData)
		randomIndex = random.randint(0, (messageSize - 1))
		oldValue = byteArr[randomIndex]
		if (oldValue < 255):
			newValue = oldValue + 1
		else:
			newValue = oldValue - 1
		byteArr[randomIndex] = newValue

		g = open(filenamePrefix + str(index) + "_messageBAD", 'wb')
		g.write(byteArr)
		g.close()
		del g
		'''
