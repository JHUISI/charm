import re, sys, os


def main(files):
    for f in files:
        file = open(f, 'r')
        line = file.readline()
        i = line.split(',')
        sum = 0
        length = len(i)
        count = 0
        for j in i:
            if re.match("^\d+?\.\d+?$", j): sum += float(j); count += 1    
        print("file =", f, ": avg =", float(sum / count), ": count =", count)
        file.close()
            


if __name__ == "__main__":
   if len(sys.argv) < 1:
      sys.exit("python ", sys.argv[0], " [ list of input files ]")
      
   fileList = sys.argv[1:]
   
   main(fileList) 
