#!/usr/bin/env python

import json
import yaml
import re

def main():
    stream = open('input/skylake.yaml', 'r')
    data = yaml.safe_load(stream)
    
    #Prints
    print (json.dumps(parser(data), indent=4))

#Parse the .yaml file
def parser(data):
    undefPorts = []
    noRecThro = []
    undefRecThro = []
    resourceUsageList = []


    # Print instruction names
    for instruction in data:

        if instruction['Instruction'] is not None:
            tempInstruction = instruction['Instruction'].replace("\n", "")

        resources = {
                'Instruction' : tempInstruction,
                'Operands' : instruction['Operands'],
                'Resources' : []
                }

        uOps = instruction['Uops each port']
        reciprocalThroughput = instruction['Reciprocal throughput']

        #Check if rec. thro. is none, its needed later in calculations
        if reciprocalThroughput is None:
            noRecThro.append(instruction)
            continue
        #Rec. thro. is defined, but NaN
        if not (isNumber(reciprocalThroughput)):
            undefRecThro.append(instruction)
            continue

        #Check that ports are correctly defined according to custom RegEx
        match = isPortDefined(str(uOps))
        if (not (match is None)) and match.end() - match.start() == len(uOps):
            splitUOps = uOps.split(' ')
            largestCard = 0
            
            #Deal with load/store instructions and remove them from the splitUOps
            for ports in list(splitUOps):
                if isLoadStore(ports):  
                    resource = {
                            'Resource': removePrefix(ports), 
                            'ResourceUsage': getPrefix(ports),
                            'HoldTime': 1
                            }
                    resources['Resources'].append(resource)
                    splitUOps.remove(ports)

            #Calculate remaining ports
            if not (splitUOps is None):
                for ports in splitUOps:
                    cardinality = len(removePrefix(ports)) - 1
                    resourceUsage = float((float(reciprocalThroughput)) * cardinality / getPrefix(ports))
                    resource = {
                            'Resource': removePrefix(ports), 
                            'ResourceUsage': getPrefix(ports),
                            'HoldTime': resourceUsage
                            }
                    resources['Resources'].append(resource)
        # Save all instructions without defined ports
        else:
            undefPorts.append(instruction)

        #Save undefined ports and instructions without througput

        resourceUsageList.append(resources)

    #Some instructions are added twice to some lists, as they brake the same rule twice. Thus we remove all duplicate entries in all lists.
    undefPorts = removeDuplicateEntries(undefPorts)
    noRecThro = removeDuplicateEntries(noRecThro)

    #Format the output
    output = {
    'ResourceUsage' : resourceUsageList,
    'UndefinedPorts': undefPorts,
    'NoReciprocalThrougput': noRecThro,
    'UndefinedReciprocalThrougput': undefRecThro,
    }
    return output

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

#Get the prefix from a group of ports
def getPrefix(ports):
    prefix = ports[0]
    numPrefix = 0
    while isNumber(prefix):
        numPrefix = numPrefix * 10 + int(prefix)
        ports = ports[1:]
        prefix = ports[0]

    return numPrefix if numPrefix != 0 else 1

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
def removeDuplicateEntries(inList):
    #Remove duplicate lines in list of incomplete instructions
    return [dict(t) for t in set([tuple(d.items()) for d in inList])]

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

