
# simple example
#>>> a = [1,2,3,4,5]
#>>> dotprod(1, 1, len(a), lambda i,b: (b[i] ** 2), a)
# TODO: support caching of values at each stage of product?

def dotprod(init, skip, n, func, *args):
    prod = init
    i = 0 
    for j in range(i, n):
        if j != skip:
           result = func(j, *args)
           # cache if necessary
           prod *= result
    #print("product =>", prod)
    return prod

def dotprod2(iterator, func, *args):
    prod = 1
    for j in iterator:
        prod *= func(j, *args)
    return prod