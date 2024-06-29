# -*- coding: utf-8 -*-

import re
import numpy as np
from collections import namedtuple
from math import ceil, sqrt

Point2D = namedtuple('Point2D', 'x y')
GCodeLine = namedtuple('GCodeLine', 'x y z e f')

#################   USER INPUT PARAMETERS   #########################

INPUT_FILE_NAME = "tall_skinny_carry_on.gcode"
OUTPUT_FILE_NAME = "E_SCALED_" + INPUT_FILE_NAME 
#LAYER_HEIGHT = 0.3 #Layer height of the sliced gcode

DISCRETIZATION_LENGTH = 10 #discretization length for an extrusion move

#################   USER INPUT PARAMETERS END  #########################

def parseGCode(currentLine: str) -> GCodeLine: #parse a G-Code line
    thisLine = re.compile('(?i)^[gG][0-3](?:\s+x(?P<x>-?[0-9.]{1,15})|\s+y(?P<y>-?[0-9.]{1,15})|\s+z(?P<z>-?[0-9.]{1,15})|\s+e(?P<e>-?[0-9.]{1,15})|\s+f(?P<f>-?[0-9.]{1,15}))*')
    lineEntries = thisLine.match(currentLine)
    if lineEntries:
        return GCodeLine(lineEntries.group('x'), lineEntries.group('y'), lineEntries.group('z'), lineEntries.group('e'), lineEntries.group('f'))

def writeLine(G, X, Y, Z, F = None, E = None): #write a line to the output file
    X = round(float(X),5)
    Y = round(float(Y),5)
    outputSting = "G" + str(int(G)) + " X" + str(X) + " Y" + str(Y)
    if Z is not None:
        outputSting = outputSting + " Z" + str(round(float(Z),5))
    if E is not None:
        outputSting = outputSting + " E" + str(round(float(E),5))
    if F is not None:
        outputSting = outputSting + " F" + str(int(float(F)))
    outputFile.write(outputSting + "\n")

relativeMode = False
prevLineCommands = None

with open(INPUT_FILE_NAME, "r") as gcodeFile, open(OUTPUT_FILE_NAME, "w+") as outputFile:
        for currentLine in gcodeFile:
            if currentLine[0] == ";":   #if NOT a comment
                outputFile.write(currentLine)
                continue
            currentLineCommands = parseGCode(currentLine)
            if currentLineCommands is not None: #if current comannd is a valid gcode
                if currentLineCommands.z is not None: #if there is a z height in the command
                    currentZ = float(currentLineCommands.z)
                    
                if currentLineCommands.x is None or currentLineCommands.y is None: #if command does not contain x and y movement it#s probably not a print move
                    if currentLineCommands.z is not None: #if there is only z movement (e.g. z-hop)
                        outputFile.write("G1 Z" + str(currentZ))
                        if currentLineCommands.f is not None:
                            outputFile.write(" F" + str(currentLineCommands.f))
                        outputFile.write("\n")
                        continue
                    outputFile.write(currentLine)
                    continue

                if currentLineCommands.e is not None: #if this is a line with extrusion
                    """if float(currentLineCommands.e) < 0.0:
                        print("Retraction")"""
                    currentF = None
                    if currentLineCommands.f is not None:
                        currentF = currentLineCommands.f
                    scaleFactor = (1-(float(currentLineCommands.x)/300))
                    extrusionAmount = float(currentLineCommands.e) * scaleFactor
                    writeLine(1, currentLineCommands.x, currentLineCommands.y, currentLineCommands.z, currentF, extrusionAmount)
                else:
                    currentF = None
                    if currentLineCommands.f is not None:
                        currentF = currentLineCommands.f
                    extrusionAmount = None                    
                    writeLine(1, currentLineCommands.x, currentLineCommands.y, currentLineCommands.z, currentF, extrusionAmount)

            else:
                outputFile.write(currentLine)
print("GCode extrusion scaling finished!")