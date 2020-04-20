import pygame
import numpy as np

class roomObject():
    def __init__():
        self.hi = 1

class gridSpace():
    def __init__(self,
                 color = (200, 200, 200, 1),
                 highlightColor = (210, 210, 210, 1),
                 rect = [0, 0, 50, 50],
                 outline = 1,
                 objectsHere = [],
                 highlighted = False):
        self.color = color
        self.defaultColor = color
        self.highlightColor = highlightColor
        self.rect = rect
        self.outline = outline
        self.defaultOutline = outline
        self.objectsHere = objectsHere
        self.highlighted = highlighted

    def addObject(self, obj):
        self.objectsHere.append(obj)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, self.outline)

    def highlight(self, color = None):
        if color is None:
            color = self.highlightColor

        self.setColor(color)
        self.setOutline(0)
        self.highlighted = True

    def getObjects(self):
        return self.objectsHere

    def removeObject(self, obj):
        self.objectsHere.remove(obj)

    def setColor(self, color):
        self.color = color
    
    def setRect(self, rect):
        self.rect = rect

    def setOutline(self, outline):
        self.outline = outline

    def toggleHighlight(self, color = None):
        if self.highlighted:
            self.unhighlight()
        else:
            self.highlight(color = color)

    def unhighlight(self):
        self.setColor(self.defaultColor)
        self.setOutline(self.defaultOutline)
        self.highlighted = False

class grid():
    def __init__(self, width = 5, height = 5, totalWidth = 500, totalHeight = 500, color = (200, 200, 200, 1)):
        self.dims = [width, height]
        self.totalDims = [totalWidth, totalHeight]
        self.spaceDims = [totalWidth // width, totalHeight // height]
        self.hoverSpace = [0, 0]
        self.lockedSpace = [0, 0]

        self.objects = list()
        self.gridSpaces = list()

        for w in range(width):
            self.gridSpaces.append(list())
            for h in range(height):
                self.gridSpaces[w].append(gridSpace(rect=[w * self.spaceDims[0], h * self.spaceDims[1], self.spaceDims[0], self.spaceDims[1]]))

    def draw(self, surface):
        # Draw grid spaces
        for w in range(self.dims[0]):
            for h in range(self.dims[1]):
                self.gridSpaces[w][h].draw(surface)

        # Draw objects
        for obj in self.objects:
            obj.draw()
    
    def get_space(self, cursorCoords):
        """Returns the space coordinates w,h based on cursor coordinates."""
        space = [0, 0]

        # X dimension
        if cursorCoords[0] >= self.spaceDims[0] * self.dims[0]:
            space[0] = self.dims[0] - 1
        elif cursorCoords[0] > 0:
            space[0] = cursorCoords[0] // self.spaceDims[0]
        
        # Y dimension
        if cursorCoords[1] >= self.spaceDims[1] * self.dims[1]:
            space[1] = self.dims[1] - 1
        elif cursorCoords[1] > 0:
            space[1] = cursorCoords[1] // self.spaceDims[1]
            
        return space

    def highlight(self, spaceCoords, exclusive = False, color = (210, 210, 210, 1)):
        """Highlights a space"""
        if exclusive:
            for w in range(self.dims[0]):
                for h in range(self.dims[1]):
                    self.gridSpaces[w][h].unhighlight()

        self.gridSpaces[spaceCoords[0]][spaceCoords[1]].highlight(color)
        self.hoverSpace = spaceCoords

    def lockSpace(self):
        """Locks a space while waiting for text to process"""
        self.lockedSpace = self.hoverSpace

    def toggleHighlight(self, spaceCoords, color = (210, 210, 210, 1)):
        """Toggles a space to highlight (or not)"""
        self.gridSpaces[spaceCoords[0]][spaceCoords[1]].toggleHighlight(color)

    def unhighlight(self, spaceCoords):
        """Unhighlights a space"""
        self.gridSpaces[spaceCoords[0]][spaceCoords[1]].unhighlight()
