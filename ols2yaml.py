#!/usr/bin/env python

import yaml
import re

def main():
    stream = open('skylake_formated_clean.yaml', 'r')
    data = yaml.safe_load(stream)
    
    #Prints
    print (parser(data))

#Parse the .yaml file
def parser(data):
    undefPorts = "Undefined ports: \n"
    noRecThro = "No reciprocal throughput defined: \n"
    incompleteList = "Inc. list: \n"
    resourceUsageList = "Instructions - Operands - [Resource - Resoure Usage - Hold-time] \n"

    # Print instruction names
    for instruction in data:

        resources = str(instruction['Instruction']) + " - " + str(instruction['Operands']) + " - " + "["

        uOps = instruction['Uops each port']
        reciprocalThroughput = instruction['Reciprocal throughput']
        resourceUsage = []

        #Check if rec. thro. is none here, its needed later in calculations
        if reciprocalThroughput is None:
            noRecThro += str(instruction) + "\n"
            continue

        #Check that ports are correctly defined according to custom RegEx
        match = isPortDefined(str(uOps))
        if (not (match is None)) and match.end() - match.start() == len(uOps):
            splitUOps = uOps.split(' ')
            largestCard = 0
            
            #Deal with load/store instructions and remove them from the splitUOps
            for ports in list(splitUOps):
                if isLoadStore(ports):  
                    resources += str(ports) + " - 1 - " + "1, " 
                    splitUOps.remove(ports)

            #Check largest cardinality of ports
            if(splitUOps):
                cardinality = largestCardinality(splitUOps)
                print("UOps :" + str(splitUOps))
                print("Largest card:" + str(cardinality))

            #Make the throughput calculations
            # for ports in splitUOps:
                # #Check if first character defines parallel ports on the form of "2p0156"
                # prefix = ports[0]
                # #Standard prefix
                # if (prefix == 'p'):
                    # #Instruction uses LD, STA, or STD (load/store Uop)
                    # if ports == "p23" or ports == "p237" or ports == "p4":
                    # #Instruction is not a load/store
                    # # else:

                # #Numerical prefix
                # elif isNumber(prefix):
                    # ports = ports[1:]
                    # #cardinality = len(ports) - 1 / int(prefix)
                # #Undefined prefix
                # else:
                    # undefPrefix += str(instruction) + "\n"

        # Save all instructions without defined ports
        else:
            undefPorts += str(instruction) + "\n"

        #Save undefined ports and instructions without througput

        resourceUsageList += resources[:-2] + "]" "\n"


    #Some instructions are added twice to some lists, as they brake the same rule twice. Thus we remove all duplicate entries in all lists.
    undefPorts = removeDuplicateEntries(undefPorts)
    noRecThro = removeDuplicateEntries(noRecThro)

    #Print the list
    print (resourceUsageList + undefPorts + noRecThro)

#Find the largest cardinality in a string of port-definitions
def largestCardinality (ports):
    largestCard = 0
    for port in ports:
        #Remove numerical prefix
        port = removePrefix(port)

        #Check cardinality
        if largestCard < len(port) - 1:
            largestCard = len(port) - 1
        
    return largestCard

#Removes the numerical prefix (if existent) in front of ports
def removePrefix(ports):
    prefix = ports[0]
    #Remove numerical prefix
    while isNumber(prefix):
        ports = ports[1:]
        prefix = ports[0]

    return ports

#Receive a single group of ports (p237) and see if they are used for load or store operations
def isLoadStore(port):
    #Remove numerical prefix
    prefix = port[0]
    while isNumber(prefix):
        port = port[1:]
        prefix = port[0]
    if port == "p23" or port == "p237" or port == "p4":
        return True
    
    else:
        return False

#Check if an instruction solely consists of load/store ports
def isExclusivelyLoadStore(ports):
    exclusive = True
    for port in ports:
        if not isLoadStore(port):
            exclusive = False
    
    return exclusive

#Remove duplicate lines in a string
def removeDuplicateEntries(listString):
    #Remove duplicate lines in list of incomplete instructions
    return '\n'.join(sorted(set(listString.split("\n")))) 

#Check if a given instructions ports are defined
def isPortDefined(ports):
    #Regular expression for prefix_opt-'p'-ports-opt_whitespace, all repeated at least once
    regEx = re.compile('([\d]*[p][\d]+[\s]{0,1})+')
    regMatch = regEx.match(ports)
    return regMatch

#Check if parameter is a number
def isNumber(a):
    try:
        int(a)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    main()
