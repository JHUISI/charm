import re, sys, os

"""
Calculate mean and standard deviation of data x[]:
    mean = {\sum_i x_i \over n}
    std = sqrt(\sum_i (x_i - mean)^2 \over n-1)
"""
def meanstdv(x):
    from math import sqrt
    n, mean, std = len(x), 0, 0
    for a in x:
        mean = mean + a
    mean = mean / float(n)
    for a in x:
        std = std + (a - mean)**2
    std = sqrt(std / float(n-1))
    return mean, std


def main(files):
    for f in files:
        file = open(f, 'r')
        line = file.readline()
        i = line.split(',')
        sum = 0
        length = len(i)
        count = 0
        finalList = []
        for j in i:
            if re.match("^\d+?\.\d+?$", j): sum += float(j); count += 1; finalList.append(float(j))    
        print("file =", f, ": avg =", float(sum / count), ": count =", count, "stddev = ", meanstdv(finalList))
        file.close()
            


if __name__ == "__main__":
   if len(sys.argv) < 1:
      sys.exit("python ", sys.argv[0], " [ list of input files ]")
      
   fileList = sys.argv[1:]
   
   main(fileList) 
