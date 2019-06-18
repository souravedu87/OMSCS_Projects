# CEN 598: Programming Assignment - 2: Calculate Complete SOS
# Author: SOURAV SAMANTA
# ASU ID: 1207860455
import re
import sys
  
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


    def calcConsensus(self):
        '''Calculates the Consensus between the Set Of Cubes
        
        Returns
        -------
        socConsensusObj:    "Set Of Cube" Object that contains the Consensus "Cube" Objects
        '''
        sosConsensus = set()
                
        for cubeObjI in self.cubes:
            socObj2 = self.cubes.copy()
            socObj2.remove(cubeObjI)
            
            # Logic: Identify the 'Un-complemented' and 'Complemented' literals of a Cube
            # Then check whether only a single literal appears in un-complemented form in one cube and complemented form in another 
            (setU1, setC1) = calcCompUncompSet(cubeObjI.cube)      
            for cubeObjJ in socObj2:
                count = 0           # "count" variable keeps track of the literals that vary i.e. appears in different forms
                (setU2, setC2) = calcCompUncompSet(cubeObjJ.cube)
           
                if len(setU1) != 0:
                    for literalU1 in setU1:
                        if (literalU1 in setC2):
                            count += 1
                            literalConsensus = set([literalU1, "~"+literalU1])      # literal that appears in both forms
                if len(setC1) != 0:
                    for literalC1 in setC1:
                        if (literalC1 in setU2):
                            count += 1
                            literalConsensus = set([literalC1, "~"+literalC1])       # literal that appears in both forms
                
                # To reconstruct the complement set, add "~" to the literal            
                setC1_Org = set()
                if len(setC1) != 0:
                    for literalC1 in setC1:
                        literalC1_Org = "~" + literalC1
                        setC1_Org.add(literalC1_Org)
                # To reconstruct the complement set, add "~" to the literal   
                setC2_Org = set()
                if len(setC2) != 0:
                    for literalC2 in setC2:
                        literalC2_Org = "~" + literalC2
                        setC2_Org.add(literalC2_Org)  
                
                if count == 1:      # if the value of "count" is 1 then only a single literal varies, so consensus exists otherwise not
                    c = (setU1 | setC1_Org | setU2 | setC2_Org) - literalConsensus
                    if len(c) == 0:
                        sosConsensus.add(frozenset(set(['1'])))
                    else:
                        sosConsensus.add(frozenset(c))
        
        socConsensusObj = Soc([])   # Set Of Consensus Cube object
        for consensusSet in sosConsensus:
            cubeObj = Cube(list(consensusSet))
            socConsensusObj.addCube(cubeObj)
                 
        return socConsensusObj
    
    
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
    
    
    def completeSoc(self):
        '''Calculates the Completeness of a SOS.
        
        Logic:  An SOS is complete if it is reduced and if any two subsets of the SOS have a 
                consensus, then the consensus is included in the SOS.
        '''     
        cubeNull = Cube([])
        
        cubeOne = Cube(['1'])

        # Identify the cubes that are reduced to 0
        reducedCubes = set()
        for cubeObj in self.cubes:
            # Step-0: REDUCE CUBE
            reducedCubeObj = reduceS(cubeObj)       # Call "reduceS" function
            if '0' in reducedCubeObj.cube:
                reducedCubes.add(cubeObj)
        
        # Remove the cubes that are reduced to 0       
        for reducedCubeObj in reducedCubes:
            self.cubes.remove(reducedCubeObj)
        
        iterVar = 1
        # ITERATED CONSENSUS: Steps-1 to 3
        print "\n--------------------- COMPUTATION ---------------------"
        while (True):
            print "\n----------------- Step-%d: -----------------" % iterVar
            # If the Set Of Cube object has no element after reduction, break out from the loop
            if len(self.cubes) == 0:
                cubeObj_0 = Cube(['0'])
                self.cubes = [cubeObj_0]
                break
            
            # Step-1: REDUCE SET OF CUBES
            reducedSocObj = reduceSOS(self)
            print "Reduced SOP:\t" + reducedSocObj.displaySoc()
            
            # Step-2: CALCULATE CONSENSUS BETWEEN CUBES
            consensusSocObj = reducedSocObj.calcConsensus()
            print "Consensus:\t" + consensusSocObj.displaySoc()
            
            # ITERATED CONSENSUS: Terminating Condition 1 - If no Consensus exists among the cubes
            if (cubeNull.cube == consensusSocObj.cubes):
                break
            
            # ITERATED CONSENSUS: Terminating Condition 2 - If the Consensus is included in the Set Of Cubes
            match = 0
            for consensusCubeObj in consensusSocObj.cubes:
                for cubeObj in self.cubes:
                    if (consensusCubeObj.cube.issubset(cubeObj.cube)):
                        match += 1
            
            if match == len(consensusSocObj.cubes):     
                break
            
            # Consensus of {'a', '~a'} = 1: So terminate  
            if (cubeOne.cube == consensusSocObj.cubes):
                self.cubes.clear()
                self.addCube(cubeOne)
                break
            
            # Step-3: ADD THE CONSENSUS TO THE SET OF CUBES  
            for consensusCubeObj in consensusSocObj.cubes:
                self.addCube(consensusCubeObj)
            
            print "Updated SOP:\t" + self.displaySoc()
            iterVar += 1
        print ""
        print "=--="*20


def reduceS(cubeObj):
    '''Reduces a Cube Object.
        
    Parameters
    ----------
    cubeObj:    Non-reduced Cube Object
    Returns
    -------
    cubeObj:    Reduced Cube Object
    '''
    # Boolean Properties
    cubeObj.identityProperty()
    cubeObj.nullProperty()
    cubeObj.complementProperty()
    
    return cubeObj


def reduceSOS(socObj):
    '''Reduces a Set Of Cube Object.
        
    Parameters
    ----------
    socObj:    Non-reduced Set Of Cube Object
    Returns
    -------
    socObj:    Reduced Set Of Cube Object
    '''
    # Boolean Properties
    socObj.identityProperty()
    socObj.nullProperty()
    socObj.complementProperty()
    socObj.reduceSoc()
    
    return socObj


def completeSOS(socObj):
    '''Calculates the Completeness of a Set Of Cube Object.
        
    Parameters
    ----------
    socObj:    Set Of Cube Object
    Returns
    -------
    socObj:    Modified Set Of Cube Object
    '''
    socObj.completeSoc()
    
    return socObj


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

            
def testdebug():
    '''Sets up input to check for various functionalities.'''
    
    # Check for cube identities
    # 1. a.0 = 0
    cubeObj1 = Cube(['b','c','d','0'])
    print "Input Cube:\t\t" + cubeObj1.displayCube()
    rcubeObj1 = reduceS(cubeObj1)
    print "Output Cube:\t\t" + rcubeObj1.displayCube()
    print "- -"*20
    
    # 2. a.1 = a
    cubeObj2 = Cube(['b','c','d','1'])
    print "Input Cube:\t\t" + cubeObj2.displayCube()
    rcubeObj2 = reduceS(cubeObj2)
    print "Output Cube:\t\t" + rcubeObj2.displayCube()
    print "- -"*20
    
    # 3. a.~a = 0    Any cube that contains both forms of the same element is eliminated.
    cubeObj3 = Cube(['b','c','d','~b'])
    print "Input Cube:\t\t" + cubeObj3.displayCube()
    rcubeObj3 = reduceS(cubeObj3)
    print "Output Cube:\t\t" + rcubeObj3.displayCube()
    print "- -"*20
    
    # Non-reduced cube
    cubeObj4 = Cube(['b','c','d'])
    print "Input Cube:\t\t" + cubeObj4.displayCube()
    rcubeObj4 = reduceS(cubeObj4)
    print "Output Cube:\t\t" + rcubeObj4.displayCube()
    print "- -"*20
    
    # 4. a + 0 = a
    socObj1 = Soc([Cube(['a','b','c']), Cube(['0'])])
    print "Input Sop:\t\t" + socObj1.displaySoc()
    rsocObj1 = reduceSOS(socObj1)
    print "Output Sop:\t\t" + rsocObj1.displaySoc()
    print "- -"*20
    
    # 5. a + 1 = 1
    socObj2 = Soc([Cube(['a','b','c']), Cube(['1'])])
    print "Input Sop:\t\t" + socObj2.displaySoc()
    rsocObj2 = reduceSOS(socObj2)
    print "Output Sop:\t\t" + rsocObj2.displaySoc()
    print "- -"*20
    
    # 6. a + ~a = 1
    socObj3 = Soc([Cube(['a']), Cube(['~a'])])
    print "Input Sop:\t\t" + socObj3.displaySoc()
    rsocObj3 = reduceSOS(socObj3)
    print "Output Sop:\t\t" + rsocObj3.displaySoc()
    print "- -"*20
    
    # Check for Consensus
    # Consensus Case 1: There is exactly one element x (consensus element) that appears in one form in one 
    #                   of the subsets and the other form in the other subset.
    socObj4 = Soc([Cube(['a','b','~c']), Cube(['a','b','c','d'])])
    print "Input Sop:\t\t" + socObj4.displaySoc()
    consensusObj4 = socObj4.calcConsensus()
    print "Consensus:\t\t" + consensusObj4.displaySoc()
    print "- -"*20
    
    # Consensus Case 2: No Consensus if more than one element varies
    socObj5 = Soc([Cube(['a','~b','~c']), Cube(['a','b','c','d'])])
    print "Input Sop:\t\t" + socObj5.displaySoc()
    consensusObj5 = socObj5.calcConsensus()
    print "Consensus:\t\t" + consensusObj5.displaySoc()
    print "- -"*20
    
    # Consensus Case 3: No Consensus if no one element varies
    socObj6 = Soc([Cube(['a','b','c']), Cube(['e','b','c','d'])])
    print "Input Sop:\t\t" + socObj6.displaySoc()
    consensusObj6 = socObj6.calcConsensus()
    print "Consensus:\t\t" + consensusObj6.displaySoc()
    print "- -"*20
    
    # Check for Cube Containment
    cubeObj5 = Cube(['b','c','d'])
    cubeObj6 = Cube(['a','b','c','d'])
    print "Input Cubes:\t\t(" + cubeObj5.displayCube() + ") & (" + cubeObj6.displayCube() + ")"
    print "Cube Containment:\tCube (" + cubeObj5.displayCube() + ") contained in Cube (" + cubeObj6.displayCube() + ") ? " + str(cubeObj5.isCubeContained(cubeObj6)) 
    print "Cube Containment:\tCube (" + cubeObj6.displayCube() + ") contained in Cube (" + cubeObj5.displayCube() + ") ? " + str(cubeObj6.isCubeContained(cubeObj5)) 
    print "- -"*20
    
    # Find out Complete SOS
    c1 = Cube(['b','c','d'])
    c2 = Cube(['a','b'])
    c3 = Cube(['~b','c'])
    soc1 = Soc([c1, c2, c3])
    
    print "="*80
    print "Input SOP:\t\t" + soc1.displaySoc()
    csoc1 = completeSOS(soc1)
    print "Complete SOS:\t\t" + csoc1.displaySoc()
    print "="*80


def interactive():
    '''Accepts the input from user in Interactive mode
    
    Parameters
    ----------
    Returns
    -------
    '''
    print "Sample SOP format:\tc.b.d + a.b + ~b.c"
    
    # Accept Input SOP
    inputSOP = raw_input("Enter SOP:\t\t")
    print "="*80
    #inputSOP = "c.b.d + a.b + ~b.c"
    #inputSOP = "x.~y.~z + ~x.y + ~x.~y.~z + ~x.y.z"
    #inputSOP = "x.~y + ~x.~z.t + x.y.z.~t + ~x.~y.z.~t"
    #inputSOP = "x.y.z.t + x.y.~z.~t + x.~z.~t + ~x.~y.~z + ~x.y.~z.t"
    #inputSOP = "x.y.z + ~x.~z + x.y.~z + ~x.~y.z + ~x.y.~z"
    #inputSOP = "x.~y + x.y.~z + ~x.y.~z"
    #inputSOP = "x.y + ~y.t + ~x.y.~z + x.~y.z.~t"
    
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
    
    # Check whether the SOP is complete
    print "Input SOP:\t" + socObj.displaySoc()   
    sosObj = completeSOS(socObj)
    print "--------------------- RESULTS ---------------------\n"     
    print "Complete SOS:\t" + sosObj.displaySoc()
    print "="*80
    

def main():
    '''Main Method.'''
    print "-"*80
    print "Option 1:\tTest Mode"
    print "Option 2:\tInteractive Mode"
    print "-"*80
    
    # Options for User Input
    try:
        option = int(raw_input("Enter Option:\t"))
        print "-"*80
        
        if option == 1:     # Test mode
            testdebug()
        elif option == 2:   # Interactive mode
            interactive()
        else:
            print "Sorry. Invalid option!!!"
            sys.exit()
    except Exception:
        print "="*80
        print "Oops! There was an Error."
        sys.exit()
        
        
if __name__ == '__main__':
    main()