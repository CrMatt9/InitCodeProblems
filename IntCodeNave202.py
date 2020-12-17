class IntCode ():

    #This program translates a standard spaceship IntCode
    def __init__ (self, input, emergencyCode = 0000, desiredValue = None):
        self.sumCte = 1
        self.multCte = 2
        self.endCte = 99

        self.emergencyCode = emergencyCode
        self.desiredValue = desiredValue
        self.value = 0
        self.noun = self.emergencyCode//100
        self.verb = self.emergencyCode-self.noun*100
        self.errors = 0

        dataFrame = open(input, "r")
        self.rawData = dataFrame.read().split(',')
        dataFrame.close()

        self.groupedData = [] #Data grouped in intructions in this case 4 ints so it is a list of ?x4
        self.groupedDataCopy = []
        self.errorMessage = "" #Store all the errors while running the intcode


    def Parse(self):
        self.rawData = [int(x) for x in self.rawData] #convert everything into int

        #splint the int f.e 2562 into 25 , 62 and assing it to posc 1 and 2 respectively
        #We consider that 0000 means that there is no emergencyCode
        if(self.emergencyCode != 0000):
            self.rawData[1] = self.noun
            self.rawData[2] = self.verb

        #separe data into groups of 4 to ease the search, it should be the standard format
        groupPosc = 0;
        while groupPosc <= len(self.rawData):
            diff = len(self.rawData) - groupPosc
            if diff <= 4 :
                self.groupedData.append(self.rawData[len(self.rawData)-diff-1 : len(self.rawData)-1])
                break
            else:
                self.groupedData.append(self.rawData[groupPosc:groupPosc+4])
                groupPosc += 4

        self.groupedDataCopy = self.groupedData


    def RunIntCode(self):
        self.errorMessage = ''
        groups = len(self.groupedData)

        # print(self.groupedData)
        for instr in range(groups):
            instruction = self.groupedData[instr]

            opCode = instruction[0]
            firstOper = instruction[1]
            secondOper = instruction[2]
            storeRes = instruction[3]

            # print("Ejecutando instr {instructions} de {groups} \n".format(instructions=instr, groups=groups))
            # print("Ejecutando OPCode %i" % opCode)

            if opCode == self.sumCte:
                #We make a sum ; elem 1* + elem 2* and we store it in elem3*
                sum1 = self.groupedData[firstOper//4][firstOper%4]
                sum2 = self.groupedData[secondOper//4][secondOper%4]
                #we store it
                self.groupedData[storeRes//4][storeRes%4] = sum1 + sum2

            elif opCode == self.multCte:
                #We make a multiplication ; elem 1* · elem 2* and we store it in elem3*
                mult1 = self.groupedData[firstOper//4][firstOper%4]
                mult2 = self.groupedData[secondOper//4][secondOper%4]
                #we store it
                self.groupedData[storeRes//4][storeRes%4] = mult1 * mult2

            elif opCode == self.endCte:
                #End
                self.value = self.groupedData[0][0]
                break

            else:
                error = "There was an Error on instruction {instruction} with noun {noun} and verb {verb} \n ".format(instruction=instr, noun=self.noun, verb=self.verb)
                print(error)
                self.errors += 1
                #We keep the errors messages to write out on the output.txt
                self.errorMessage += error

    """Find noun and verb to get a desired value. This solution is trying to use a solver that make steps depending on
    the difference of the value gotten and the disired one.
    At the end of the day it cant get the solution.
    """
    def FindVar(self):
        self.RunNoSave()
        lastStep = None
        lastDifference = None

        while(self.desiredValue != self.value):
            #Create the Solver
            solver = Solver(self.desiredValue, self.value, self.noun, self.verb, maxLen=len(self.rawData), lastStep=lastStep, lastDifference=lastDifference, errors = self.errors)
            #Runs it
            self.noun, self.verb, lastStep, lastDifference = solver.Run()
            #We are forced to use the try except due to the error out of range in certain verbs and noun combinations
            try:
                self.RunNoSave()
                print("On the int code we found %i Value" % self.value)
            except:
                pass

        return self.noun, self.verb

    """ Second way to solve this problem is the "dirtiest one, I am just trying all the possible combinations inside the
    possible values (0 to the len(rawData))

    """

    def FindVar2(self):
        results = []
        for noun in range(len(self.rawData)-1):
            self.noun = noun
            for verb in range(len(self.rawData)-1):
                self.verb = verb
                try:
                    self.RunNoSave()
                    print(self.value)
                    if self.value == self.desiredValue:
                        #in case the value is gotten we add it to a list of lists
                        results.append[self.noun,self.verb,self.errors]
                except:
                    pass
        #In this for loop we choose the best solution (the one with less errors)
        for i in range(len(results)):
            if i == 0:
                result = results[0]
            elif result[2]>results[i][2]:
                result = results[i]
        return result


    def StoreResults(self):

        outputFrame = open("output.txt", "w")

        #we generate a flat list to write it easily respecing the input format
        outputList = [item for instr in self.groupedData for item in instr]

        outputFrame.writelines(', '.join([str(elem) for elem in outputList]))
        outputFrame.writelines('\n' + self.errorMessage)
        outputFrame.close()




    def Run(self):
        self.Parse()
        self.RunIntCode()
        self.StoreResults()

    def RunNoSave(self):
        self.Parse()
        self.RunIntCode()


class Solver():

    def __init__(self, desiredValue, actualValue, noun, verb, maxLen, lastStep=None, lastDifference=None, errors=0):

        self.desiredValue = desiredValue
        self.actualValue = actualValue
        self.noun = noun
        self.verb = verb
        self.maxLen = maxLen
        self.errors = errors
        self.step = 1
        self.lastStep = lastStep
        self.lastDifference = lastDifference
        self.distance = self.desiredValue - self.actualValue

        self.suma =  [1, self.maxLen//100, self.maxLen//50, self.maxLen//20, self.maxLen//10, self.maxLen//7, self.maxLen//5, self.maxLen//4, self.maxLen//3,  self.maxLen//2]

    #Set values on first iteration
    def FirstIteration(self):
        if self.distance>10000000:
            self.step = 9
        elif self.distance>1000000:
            self.step = 8
        elif self.distance>500000:
            self.step = 7
        elif self.distance>100000:
            self.step = 6
        elif self.distance>50000:
            self.step = 5
        elif self.distance>10000:
            self.step = 4
        elif self.distance>1000:
            self.step = 3
        elif self.distance>100:
            self.step = 2
        elif self.distance>10:
            self.step = 1
        else:
            self.step = 0

        self.lastStep = self.step
        self.lastDifference = self.distance

    #Manage the differences (positive or negative), manages the step and calls the executer to apply it
    def GetNewValues(self):
        if abs(self.distance) > abs(self.lastDifference):
            if step > 0 :
                self.step -= 1
            else :
                self.step += 7

        if self.distance > 0 :
                self.ApplyStep()

        elif self.disance < 0:
                self.ApplyStep(positive=False)


    def ApplyStep(self, positive=True):
        if positive == True:
                self.noun = self.noun + self.suma[self.step]
                self.verb = self.verb + self.suma[self.step]
        else:
                self.noun = self.noun - self.suma[self.step]
                self.verb = self.verb - self.suma[self.step]

        if self.noun > self.maxLen:
            self.noun = self.maxLen//2
        if self.verb > self.maxLen:
            self.verb = self.maxLen//2

    def Run(self):
        if self.lastDifference==None or self.lastStep==None:
            self.FirstIteration()

        if self.distance != 0 and self.errors != 0:
            self.GetNewValues()
        if self.distance == 0 and self.errors != 0:
            self.step += 1

        print("The error was {error} and last error was {last}".format(error=self.distance, last=self.lastDifference))
        return self.noun, self.verb, self.step, self.distance



testIntCode1 = IntCode("Input.txt", emergencyCode = 1202)
testIntCode1.Run()


testIntCode2 = IntCode("Input.txt", desiredValue = 19690720)
try:
    result = testIntCode2.FindVar2()
    print(result)
except:
    print("No solution found")

#we could use a timer here to just dont let it search for infinite time.
noun, verb = testIntCode2.FindVar()
print(noun, verb)
