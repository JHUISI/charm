import sys

def main(prefixName):
	print(prefixName)

if __name__ == '__main__':
	if ( (len(sys.argv) != 2) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + str(sys.argv[0]) + " [PREFIX OF OUTPUT FILES]")

	main(sys.argv[1])
