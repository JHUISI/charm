
'''
:Authors:    Fan Zhang(zfwise@gwu.edu), supported by GWU computer science department
:Date:       3/2013
:Note: Matrix operations over finite fields
'''
def GaussEliminationinGroups(m):
    #The code was original found at: http://ine.scripts.mit.edu/blog/2011/05/gaussian-elimination-in-python/
    #Here is an example: suppose you have A= [[1,2],
    #                                        [3,4]]
    #and you want AX = I.
    #if X = [[x1,x2],[x3,x4]] and I = [[1,0],[0,1]]
    #GaussEliminationinGroups([1,2,1],[3,4,0])-->[x1,x3]
    #GaussEliminationinGroups([1,2,0],[3,4,1])-->[x2,x4]
    #then X = MatrixTransGroups[[x1,x3],[x2,x4]]
    
    #eliminate columns
    for col in range(len(m[0])):
        for row in range(col+1, len(m)):
            r = [(rowValue * (-(m[row][col] / m[col][col]))) for rowValue in m[col]]
            m[row] = [ (pair[0]+pair[1]) for pair in zip(m[row], r)]
    #now backsolve by substitution
    ans = []
    m.reverse() #makes it easier to backsolve
    for sol in range(len(m)):
            if sol == 0:
                ans.append(m[sol][-1] / m[sol][-2])
            else:
                inner = 0
                #substitute in all known coefficients
                for x in range(sol):
                    inner += (ans[x]*m[sol][-2-x])
                #the equation is now reduced to ax + b = c form
                #solve with (c - b) / a
                ans.append((m[sol][-1]-inner)/m[sol][-sol-2])
    ans.reverse()
    return ans

def MatrixMulGroups(matrix1,matrix2):
    # Matrix multiplication
    if len(matrix1[0]) != len(matrix2):
        # Check matrix dimensions
        print('Matrices must be m*n and n*p to multiply!')
    else:
        # Multiply if correct dimensions
        new_matrix = [[0 for row in range(len(matrix2[0]))] for col in range(len(matrix1))]
        for i in range(len(matrix1)):
            for j in range(len(matrix2[0])):
                for k in range(len(matrix2)):
                    new_matrix[i][j] += matrix1[i][k]*matrix2[k][j]
    return new_matrix

def MatrixAddGroups(matrix1,matrix2):
    # Matrix Addition
    if (len(matrix1[0]) != len(matrix2[0]) or len(matrix1) != len(matrix2)):
        # Check matrix dimensions
        print('Matrices must be m*m and m*m to Add!')
    else:
        # Add if correct dimensions
        rows = len(matrix1)
        columns =len(matrix1[0])
        result = [[matrix1[row][col] + matrix2[row][col] for col in range(columns)] for row in range(rows)]
    return result

def MatrixScalarMulGroups(lamda , matrix):
    # Matrix Scalar Mul
    rows = len(matrix)
    columns =len(matrix[0])
    result = [[matrix[row][col] * lamda for col in range(columns)] for row in range(rows)]
    return result

def MatrixTransGroups(matrix):
    # Matrix transpose, 
    result = [[r[col] for r in matrix] for col in range(len(matrix[0]))]
    return result

