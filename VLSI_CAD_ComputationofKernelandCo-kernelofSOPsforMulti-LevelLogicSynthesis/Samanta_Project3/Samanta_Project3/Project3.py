# CEN 598: Programming Assignment - 3:
# Author: SOURAV SAMANTA
# ASU ID: 1207860455
import re
import sys
import numpy as np

loopCount = 0  
class Cube(object):
    """Cube class"""
    
    def __init__(self, literals):
        '''Class Initialization Method.
    
        Parameters
        ----------
        literals:    Literals of the Cube
        '''
        self.cube = set(literals)
    
        
    @property
    def cube(self):
        '''Cube Class property: To retrieve the Cube
        
        Returns
        -------
        self.__cube:    Set containing the elements of a Cube
        '''
        return self.__cube
    
    
    @cube.setter
    def cube(self, literals):
        '''Cube Class property: To set the Cube
        
        Parameters
        ----------
        literals:    Literals of a Cube
        '''
        self.__cube = set(literals)
    
        
    def identityProperty(self):
        '''Checks for Identity property: a.1 = a'''
        if '1' in self.cube and len(self.cube) != 1:
            self.cube = self.cube.difference(set(['1']))
    
    
    def nullProperty(self):
        '''Checks for Null property: a.0 = 0'''
        if '0' in self.cube and len(self.cube) != 1:
            self.cube = set(['0'])


    def complementProperty(self):
        '''Checks for Complement property: a.~a = 0'''
        setU = set()
        setC = set()
        
        # Identify the non-complement and complement literals
        for literal in self.cube:
            if literal[0] == "~":
                setC.add(literal)
            else:
                setU.add(literal)
                       
        for literalC in setC:
            for literalU in setU:
                if (literalC[1] == literalU):
                    self.cube = set(['0'])
    
    
    def isCubeContained(self, cubeOtherObj):
        '''Checks whether a cube is contained in another.
        
        Parameters
        ----------
        cubeOtherObj:    Cube Object
        
        Returns
        -------
        True/False
        '''
        if self.cube.issuperset(cubeOtherObj.cube):
            return True
        else:
            return False
    
    
    def noOfLiterals(self):
        '''Calculates the number of literals in a Cube.
        
        Returns
        -------
        noOfLiterals:    The number of literals
        '''
        (setU, setC) = calcCompUncompSet(self.cube)
        noOfLiterals = len(setU | setC)
        
        return noOfLiterals
    
    
    def reduceS(self):
        '''Reduces a Cube by using making use of Boolean properties.'''
        self.identityProperty()
        self.nullProperty()
        self.complementProperty()
    
               
    def displayCube(self):
        '''Returns the cube in string format.
        
        Returns
        -------
        cubeStr:    String representation of Cube
        '''
        cubeLength = len(self.cube)
        literalCount = 1
        cubeStr = ""
        
        for literal in self.cube:
            if (literalCount < cubeLength):
                cubeStr += str(literal)
                cubeStr += "."
            else:
                cubeStr += str(literal)
            literalCount += 1
        
        return cubeStr

        
class Soc(object):
    """Set Of Cubes class"""
    
    def __init__(self, cubes):
        '''Class Initialization Method.
    
        Parameters
        ----------
        cubes:    Cube Objects
        '''
        self.cubes = set(cubes)
    
        
    @property
    def cubes(self):
        '''Soc Class property: To retrieve the Set Of Cubes
        
        Returns
        -------
        self.__cubes:    Set containing the Cubes
        '''
        return self.__cubes
    
    
    @cubes.setter
    def cubes(self, cubes):
        '''Soc Class property: To set the Cubes in the Set Of Cubes
        
        Parameters
        ----------
        cubes:    Cube Object
        '''
        self.__cubes = set(cubes)
        
        
    def identityProperty(self):
        '''Checks for Identity property: a + 1 = 1'''
        for cubeObj in self.cubes:
            if '1' in cubeObj.cube:
                cubeObj_1 = Cube(['1'])
                self.cubes = [cubeObj_1]
                break


    def nullProperty(self):
        '''Checks for Null property: a + 0 = a'''
        countCube0 = 0
        for cubeObj in self.cubes:
            if '0' in cubeObj.cube:
                cubeObj_0 = cubeObj
                countCube0 += 1
        if countCube0 != 0:
            self.cubes.remove(cubeObj_0)
    

    def complementProperty(self):
        '''Checks for Complement property: a + ~a = 1'''
        singleLiteralCubeList = list()
        
        for cubeObj in self.cubes:
            if cubeObj.noOfLiterals() == 1:
                singleLiteralCubeList.append(list(cubeObj.cube))
        
        for literalI in singleLiteralCubeList:
            if literalI[0][0] == "~":
                for literalJ in singleLiteralCubeList:
                    if literalI[0][1] == literalJ[0]:
                        cubeObj_1 = Cube(['1'])
                        self.cubes = [cubeObj_1]
                        break
    
    
    def addCube(self, cubeObj):
        '''Add Cube Object to the "Set Of Cube" Objects
        
        Parameters
        ----------
        cubeObj:    Cube Object
        '''
        self.cubes.add(cubeObj)
        
    
    def reduceSoc(self):
        '''Reduces a Set Of Cubes'''
        
        self.identityProperty()
        self.nullProperty()
        self.complementProperty()
        
        reducedCubes = set()
        for cubeObj in self.cubes:
            # 
            cubeObj.reduceS()
            if '0' in cubeObj.cube:
                reducedCubes.add(cubeObj)
        
        # Remove the cubes that are reduced to 0       
        for reducedCubeObj in reducedCubes:
            self.cubes.remove(reducedCubeObj)
        
        setToDel = set()
        
        for cubeObjI in self.cubes:
            sosTemp2 = self.cubes.copy()
            sosTemp2.remove(cubeObjI)
            
            for cubeObjJ in sosTemp2:
                # Checks for Cube Containment
                cubeContained = cubeObjI.isCubeContained(cubeObjJ)
                if (cubeContained == True):     # If cube is contained in another, add the cube to deletion set
                    setToDel.add(cubeObjI)
        
        # Delete the cubes that are contained in other cubes
        if len(setToDel) != 0:
            for set1 in setToDel:
                self.cubes.remove(set1)
    
    
    def literalsCubesOfSoc(self):
        '''Returns "List of unique literals of SOP" & "List of list containing cubes of SOP".
        
        Returns
        -------
        uniqueLiteralsList:    List of unique literals of SOP
        totalCubeList:         List of list containing cubes of SOP
        '''
        # Identify the literals of the set of cubes
        totalLiteralsList = list()
        for cubeObj in self.cubes:
            for literal in cubeObj.cube:
                totalLiteralsList.append(literal)
        
        # Remove duplicate literals form the list
        uniqueLiteralsList = sorted(list(set(totalLiteralsList)))
        
        # Arrange the cubes of expression in a list
        totalCubeList = list()
        for cubeObj in self.cubes:
            cubeList = list()
            for literal in cubeObj.cube:
                cubeList.append(literal)
            totalCubeList.append(sorted(cubeList))
        
        return (uniqueLiteralsList, totalCubeList)
    
    
    def displaySoc(self):
        '''Returns the Set of Cubes i.e. SOP in string format.
        
        Returns
        -------
        sopStr:    String representation of SOP
        '''
        socLength = len(self.cubes)
        
        i = 1
        sopStr = ""
        for cubeObj in self.cubes:
            sopStr += cubeObj.displayCube()
            if (i < socLength):
                sopStr += " + "
            i += 1
        
        return sopStr  


class CubeLiteralMatrix(object):
    """Matrix class"""
    
    def __init__(self, socObj):
        '''Class Initialization Method.
    
        Parameters
        ----------
        socObj:    'Set of Cubes' object
        '''
        (uniqueLiteralsList, totalCubeList) = socObj.literalsCubesOfSoc()
        self.kernel = list()
        self.uniqueKernel = list()
        self.uniqueCoKernel = list()
        self.uniqueLiteralsList = uniqueLiteralsList
        self.totalCubeList = totalCubeList
        
        print "Unique Literals:\t" + str(uniqueLiteralsList)
        print "Total Cubes:\t\t" + str(totalCubeList)
        
        # Create the 2-D array: Row - Cubes : Column - Literals
        noOfRows = len(totalCubeList)
        noOfColumns = len(uniqueLiteralsList)
        
        self.matrix = np.zeros((noOfRows, noOfColumns), dtype=np.int)
        for cubeI in range(0, len(totalCubeList)):
            for literalJ in range(0, len(uniqueLiteralsList)):
                    if uniqueLiteralsList[literalJ] in totalCubeList[cubeI]:
                        self.matrix[cubeI, literalJ] = 1
                        
    
    def makeCubeFree(self, R, C):
        '''Makes the matrix cube free.
        
        Parameters
        ----------
        R:    Row array
        C:    Column array
        
        Returns
        -------
        R:    Modified Row array after matrix being made cube free
        C:    Modified Column array after matrix being made cube free
        '''
        (noOfRows, noOfColumns) = self.matrix.shape
        rIndex = list()
        cIndex = list()
        
        # Identify the valid indexes of the matrix i.e. skip entries in R and C having 0
        # 1 - unblocked    0 - blocked
        validIndexList = list()
        for i in range(noOfRows):
            if R[i] == 0:           # Skip rows
                continue
            rIndex.append(i)
            for j in range(noOfColumns):
                if C[j] == 0:       # Skip columns
                    continue
                cIndex.append(j)
                validIndexList.append([i,j])
        
        # Check whether the entire column is 1
        rIndex = list(set(rIndex))
        cIndex = list(set(cIndex))
        for c in cIndex:
            countOne = 0
            for r in rIndex:
                if self.matrix[r, c] == 1:
                    countOne += 1
            if countOne == len(rIndex):
                C[c] = 0                    # Block the column having all 1's i.e. made cube free
        
        # To restrict all zeros in R and C
        if np.all(R==0) and np.all(C==0):
            pass
        else:
            RCList = list()
            RCList.append(R.tolist())
            RCList.append(C.tolist())
#             print RCList
            if RCList not in self.kernel:
                self.kernel.append(RCList)      
        return (R, C)
                
    
    def divideByCube(self, R, C, literalIndex):
        '''Divides the matrix by single literal. 
        
        Parameters
        ----------
        R:            Row array
        C:            Column array
        literalIndex: Indicates the index of the literal by which the matrix is to be divided  
        
        Returns
        -------
        R2:    Modified Row array after division operation
        C2:    Modified Column array after division operation
        '''
        # Create a deep copy of R and C otherwise the same R and C will be modified
        R2 = np.array(R, dtype=np.int)
        C2 = np.array(C, dtype=np.int)
        
        C2[literalIndex] = 0
        (noOfRows, noOfColumns) = self.matrix.shape
        for i in range(noOfRows):
            if self.matrix[i, literalIndex] == 0:
                R2[i] = 0

        return (R2, C2)
        
    
    def computeKernel(self, R, C):
        '''Calculates the Kernel.
        
        Parameters
        ----------
        R:    Row array
        C:    Column array
        '''
        # Global variable to keep track of the number of recursive calls
        global loopCount
        loopCount += 1
        
        # Step-1: Make Cube Free
        (R1, C1) = self.makeCubeFree(R, C)
#         print "R1:\t" + str(R1)
#         print "C1:\t" + str(C1)
            
        literalIndex = -1
        for c in C1:
            literalIndex += 1
            if c == 0:
                continue
            # Step-2: Divide by Cube
            (R2, C2) = self.divideByCube(R1, C1, literalIndex)          
#             print "-"*40
#             print "L I = " + str(literalIndex)
#             print "R2:\t" + str(R2)
#             print "C2:\t" + str(C2)
            
            # Check to prevent unnecessary re-computations/ recursions when kernel and co-kernels have already been computed 
            R2C2List = list()
            R2C2List.append(R2.tolist())
            R2C2List.append(C2.tolist())
#             self.computeKernel(R2, C2)        # Without the check
            
            # Step-3: Recursive call to make cube free and divide by other literals one at a time
            # With recursive check
            if R2C2List not in self.kernel:  
                self.computeKernel(R2, C2)
                
        
    def displayCubeLiteralMatrix(self):
        '''Displays the Cube Literal Matrix.'''
        # Print the rows that corresponds to cubes
        print "."*40
        for itemNo in range(0, len(self.totalCubeList)):
            print "Row %d:\t\t" % (itemNo + 1) + Cube(self.totalCubeList[itemNo]).displayCube()
        
        # Print the columns that corresponds to literals
        print "."*40
        for itemNo in range(0, len(self.uniqueLiteralsList)):
            print "Column %d:\t%s" % (itemNo + 1, self.uniqueLiteralsList[itemNo]) 
        print "."*40
        print "\nCUBE LITERAL MATRIX:"
        print self.matrix
        
        
    def displayKernel_CoKernel(self):
        '''Displays the Kernels and Co-kernels.'''
#         print self.kernel
        (noOfRows, noOfColumns) = self.matrix.shape
        for kernelIndex in range(len(self.kernel)):
            kernelItemList = self.kernel[kernelIndex]
            rKernel = np.asarray(kernelItemList[0])
            cKernel = np.asarray(kernelItemList[1])
#             print str(rKernel) + str(cKernel)
            
            socObj = Soc([])
            for r in range(noOfRows):
                literalsCube = list()
                if rKernel[r] == 0:
                    continue
                for c in range(noOfColumns):
                    if cKernel[c] == 0:
                        continue
                    if self.matrix[r, c] != 0:
                        literalsCube.append(self.uniqueLiteralsList[c])
#                 print literalsCube
                cubeObj = Cube(literalsCube)
                socObj.addCube(cubeObj)
            if len(socObj.cubes) > 1:
#                 print "CO-KERNEL Columns:\t" + str(kernelItemList[1])
                self.uniqueKernel.append(socObj)
                # co-kernel calculation
                
                coKernelLiteralsCube = list()
                count0 = 0
                for coKernelIndex in range(0, len(kernelItemList[1])):
                    if kernelItemList[1][coKernelIndex] == 0:
                        coKernelLiteralsCube.append(self.uniqueLiteralsList[coKernelIndex])
                    else:
                        count0 += 1
                if count0 == len(kernelItemList[1]):
                    coKernelLiteralsCube = [1]
                    
                coKernelCubeObj = Cube(coKernelLiteralsCube)
                self.uniqueCoKernel.append(coKernelCubeObj)
                
        # Displays the total number of Kernel & Co-kernel combinations
        print "=-="*20
        print "#(Kernel-Cokernel combinations): %d\n" % len(self.uniqueKernel)
        
        # Displays the Kernels & Co-kernels
        print "-----------  [KERNELS] & [CO-KERNELS]  ------------"
        for itemNo in range(0, len(self.uniqueKernel)):
            print "[" + self.uniqueKernel[itemNo].displaySoc() + "] & [" + self.uniqueCoKernel[itemNo].displayCube() + "]"


class CoKernelCubeMatrix(object):
    """Co-kernel Cube Matrix class"""
    
    def __init__(self, cubeExpressionList, totalKernelSet, totalCoKernelList):
        '''Class Initialization Method.
    
        Parameters
        ----------
        cubeExpressionList:    List of list (SOP specific) containing dictionaries with cubes numbered
        totalKernelSet:        List containing Kernels of SOPs
        totalCoKernelList:     List of list (SOP specific) containing Co-kernels
        '''
        self.cubeExpressionList = cubeExpressionList
        self.totalKernelList = list(totalKernelSet)
        self.totalCoKernelList = totalCoKernelList
        
        # Count the total number of Co-kernels
        coKernelCount = 0
        for item in self.totalCoKernelList:
            for item2 in item:
                coKernelCount += 1
        
        # Create the 2-D matrix: Row - total number of Co-kernels : Column - total number of Kernels
        noOfRows = coKernelCount
        noOfColumns = len(self.totalKernelList)
        self.matrix = np.zeros((noOfRows, noOfColumns), dtype=np.int)         # 2-D Matrix creation
        self.matrixBinary = np.zeros((noOfRows, noOfColumns), dtype=np.int)   # 2-D Binary Matrix creation
        
        # Set the values of the matrix
        rowCount = 0
        for x in range(0, len(self.totalCoKernelList)):
            for r in range(0, len(self.totalCoKernelList[x])):
                for c in range(0, noOfColumns):
                    for cubeExpression in cubeExpressionList[x]:
                        for index, cubeItem in cubeExpression.items():
                            if cubeItem == (self.totalCoKernelList[x][r] | self.totalKernelList[c]):
                                self.matrix[rowCount][c] = index
                                self.matrixBinary[rowCount][c] = 1
                rowCount += 1
                              
                                
    def displayCoKernelCubeMatrix(self):
        '''Displays the Co-kernel Cube matrix.'''
#         print "Total SOPs:\t\t" + str(self.cubeExpressionList)
#         print "Total Co-Kernels:\t" + str(self.totalCoKernelList)
#         print "Total Kernels:\t\t" + str(self.totalKernelList)
        
        print "CO-KERNEL CUBE MATRIX:"
        print self.matrix
        print "\nBINARY CO-KERNEL CUBE MATRIX:"
        print self.matrixBinary   
            

def calcCompUncompSet(setTemp):
    '''Identifies the Complement and Un-complemented Literals of a Cube
        
    Parameters
    ----------
    setTemp:    Non-reduced Set Of Cube Object
    
    Returns
    -------
    setU:    Set containing the Un-complemented Literals of a Cube
    setC:    Set containing the Complemented Literals of a Cube
    '''
    setU = set()
    setC = set()
    
    for literal in setTemp:
        if literal[0] == "~":
            setC.add(literal[1])
        else:
            setU.add(literal)
    
    return (setU, setC)


def computeCoKernelCubeMatrix(inputExpList):
    '''Stepwise preparation of Co-kernel Cube Matrix.
    
    Parameters
    ----------
    inputExpList:    List of SOP objects
    '''
    kernelList = list()
    coKernelList = list()
    
    sopCount = 0
    sopExpressionDisplayList = list()           # List containing the SOPs to be displayed
    for sopExpression in inputExpList:
        sopCount += 1
        print "Input SOP %d:\t\t" % (sopCount) + sopExpression.displaySoc()
        sopExpression.reduceSoc()
        sopExpressionDisplayList.append(sopExpression)
        
        # Create the CubeLiteralMatrix object
        M = CubeLiteralMatrix(sopExpression)
        (noOfRows, noOfColumns) = M.matrix.shape
    
        # Create the R and C arrays of all 1's
        R = np.ones(noOfRows, dtype=np.int)
        C = np.ones(noOfColumns, dtype=np.int)
        
        # Calculate the Kernel and Co-kernel
        M.computeKernel(R, C)
        
        # Displays the 'Cube Literal Matrix' and Kernel & Co-kernels 
        M.displayCubeLiteralMatrix()
        M.displayKernel_CoKernel()
        
        # Add the computed Kernels and Co-kernels to the Total list of kernels and co-kernels
        kernelList.append(M.uniqueKernel)
        coKernelList.append(M.uniqueCoKernel)
        print "Global Loop Count: %d" % loopCount
        print "*"*40
    
   
    # Step-1: Assign a distinct index to each cube in each node
    cubeExpressionTotalList = list()
    totalCubeCount = 0
    for sopExpression_SocObj in inputExpList:
        cubeExpressionList = list()
        cubeExpressionDict = {}         # Create a dictionary with index as the cube number 
        for cubeObj in sopExpression_SocObj.cubes:
            totalCubeCount += 1
            keyDict = totalCubeCount
            cubeExpressionDict.update({keyDict: cubeObj.cube})
        cubeExpressionList.append(cubeExpressionDict)
        cubeExpressionTotalList.append(cubeExpressionList)
    
    # Prepare Row: Co-kernels without 1
    totalCoKernelList = list()
    CKLoopCounter = 0
    CKLoopCounterList = list()
    for coKernelListExp in coKernelList:
        totalCoKernelExpList = list()       # Expression specific
        for coKernelCubeObj in coKernelListExp:
            CKLoopCounter += 1
            if not 1 in coKernelCubeObj.cube:
                totalCoKernelExpList.append(coKernelCubeObj.cube)
            else:
                CKLoopCounterList.append(CKLoopCounter)     # Identifies the count corresponding to Co-kernel 1
        totalCoKernelList.append(totalCoKernelExpList)
   
    # Prepare Column: Identify Kernel cubes and assign to column
    totalKernelSet = set()
    KLoopCounter = 0
    for kernelListExp in kernelList:
        for kernelSocObj in kernelListExp:
            KLoopCounter += 1
            if KLoopCounter in CKLoopCounterList:
                continue
            for cubeObj in kernelSocObj.cubes:
                totalKernelSet.add(frozenset(cubeObj.cube))
    
    # Create the Co-Kernel Cube Matrix Object
    coKernelCubeMatrixObj = CoKernelCubeMatrix(cubeExpressionTotalList, totalKernelSet, totalCoKernelList)
    
    # Display the Results
    displayResults(sopExpressionDisplayList, coKernelCubeMatrixObj)


def displayResults(sopExpressionDisplayList, coKernelCubeMatrixObj):
    '''Displays the Results.
    
    Parameters
    ----------
    sopExpressionDisplayList:    List of SOP expressions
    coKernelCubeMatrixObj:       Co-kernel Cube Matrix Object
    '''
    print "\n------------------ RESULTS ------------------\n"
    # Display SOPs
    print "SOPs:"
    count = 0
    for sopExpressionObj in sopExpressionDisplayList:
        count += 1
        print "Input SOP %d:\t" % count + str(sopExpressionObj.displaySoc())
        
        for index, cubeItem in coKernelCubeMatrixObj.cubeExpressionList[count-1][0].items():
            print str(index) + ":\t\t"+ Cube(list(cubeItem)).displayCube()
        print "-"*40
    print "."*40
    
    # Display Rows: Co-kernels for each SOP
    rCount = 0
    sopCount = 0
    for coKernelItemList in coKernelCubeMatrixObj.totalCoKernelList:
        sopCount += 1
        for coKernelItem in coKernelItemList:
            rCount += 1
            print "SOP: %d Row %d:\t" % (sopCount, rCount) + Cube(list(coKernelItem)).displayCube()
    print "."*40
    
    # Display Columns: Cubes of Kernels
    cCount = 0
    for kernelItem in coKernelCubeMatrixObj.totalKernelList:
        cCount += 1
        print "Column %d:\t" %cCount + Cube(list(kernelItem)).displayCube()
    print "."*40
    
    # Displays the Co-kernel Cube Matrix
    coKernelCubeMatrixObj.displayCoKernelCubeMatrix()
    print "=-="*20
    

def batchMode():
    '''Reads the input in Batch mode from 'input.txt' file containing SOP expressions.
    
    Parameters
    ----------
    Returns
    -------
    '''
    inputExpList = list()
    try:
        fileHandle = open('input.txt', 'r')
    except Exception:
        print "="*80
        print "ERROR: 'input.txt' file was missing."        # Issue error if valid file is missing 
        sys.exit()
    
    # Reads the file
    for line in fileHandle:
        line = line.rstrip()

        if not re.match("^[a-zA-Z 01+.~=]*$", line):
            print "Only a-z A-Z + . ~ 0 1 allowed."
            sys.exit()
        
        inputSOP = re.findall('^\w+\s+\=\s+([\w\.~\s\+]+)', line)
#         print inputSOP[0]
        
        setOfCube = re.sub(r'\s', '', inputSOP[0]).split('+')
        
        socObj = Soc([])                            # Instantiate SetofCube Object
        for cube in setOfCube:
            setOfLiteral = re.split('\.', cube)
    
            # Check for invalid arrangement of literals in cube i.e. abc is invalid. Correct form: a.b.c
            for literal in setOfLiteral:
                if len(literal) > 1:
                    if len(literal) == 2 and literal[0] == "~":
                        pass
                    else:
                        print "\'" + literal + "\' is an Invalid Input!!!"
                        sys.exit()
            cubeObj = Cube(list(setOfLiteral))     # Instantiate Cube Object
            socObj.addCube(cubeObj)                 # Add the cube to the SetofCube object
        
        inputExpList.append(socObj)
        
    # Print the input SOPs
#     for itemObj in inputExpList:
#         print itemObj.displaySoc()
    
    # Compute Co-Kernel Cube Matrix
    computeCoKernelCubeMatrix(inputExpList)
    

def interactiveMode():
    '''Accepts the input from user in Interactive mode
    
    Parameters
    ----------
    Returns
    -------
    '''
    print "Sample SOP format:\tc.b.d + a.b + ~b.c"
    
    sopCount = 0
    inputExpList = list()
    
    # Do-while
    while True:
        sopCount += 1
        # Accept Input SOP
        inputSOP = raw_input("Enter SOP %d:\t\t" % sopCount)
        print "="*80

        # Parse the Input
        # Check for Invalid characters. Allow only Only a-z A-Z + . ~ 0 1
        if not re.match("^[a-zA-Z 01+.~]*$", inputSOP):
            print "Only a-z A-Z + . ~ 0 1 allowed."
            sys.exit()
        
        setOfCube = re.sub(r'\s', '', inputSOP).split('+')
        
        socObj = Soc([])                            # Instantiate SetofCube Object
        for cube in setOfCube:
            setOfLiteral = re.split('\.', cube)
    
            # Check for invalid arrangement of literals in cube i.e. abc is invalid. Correct form: a.b.c
            for literal in setOfLiteral:
                if len(literal) > 1:
                    if len(literal) == 2 and literal[0] == "~":
                        pass
                    else:
                        print "\'" + literal + "\' is an Invalid Input!!!"
                        sys.exit()
            cubeObj = Cube(list(setOfLiteral))      # Instantiate Cube Object
            socObj.addCube(cubeObj)                 # Add the cube to the SetofCube object
        
        inputExpList.append(socObj)
        # Terminating condition
        continueOption = raw_input("Do you want to continue (Y/N)?\t")
        print "="*80
        if continueOption.lower() != "y":
            break
    
    # Compute Co-Kernel Cube Matrix
    computeCoKernelCubeMatrix(inputExpList)
    

def main():
    '''Main Method.'''
    print "-"*80
    print "Option 1:\tBatch Mode"
    print "Option 2:\tInteractive Mode"
    print "-"*80
    
    # Options for User Input
    try:
        option = int(raw_input("Enter Option:\t"))
        print "-"*80
        
        if option == 1:     # Batch mode
            batchMode()
        elif option == 2:   # Interactive mode
            interactiveMode()
        else:
            print "Sorry. Invalid option!!!"
            sys.exit()
    except Exception:
        print "="*80
        print "Oops! There was an Error."
        sys.exit()

        
if __name__ == '__main__':
    main()