import pygame
import numpy as np

class roomObject():
    def __init__(self,
                 color = (0, 0, 255, 1),
                 rect = None, # or (x, y, w, h)
                 circle = None, # or (x, y, r)
                 outline = 0, # is width for circles
                 text = None,
                 objType = "room",
                 footprint = [1, 1]):
        self.color = color
        self.rect = rect
        self.circle = circle
        self.outline = outline
        self.font = pygame.font.Font("Roboto-Regular.ttf", 16)
        self.textColor = (255, 255, 255)
        self.text = text
        self.objType = objType
        self.footprint = footprint

        if text is not None:
            self.text = bytes(str(text), "utf-8")
        if rect is None and circle is None:
            self.rect = [0, 0, 0, 0]
    
    def draw(self, surface):
        if self.rect is None:
            x = self.circle[0]
            y = self.circle[1]
            r = self.circle[2]

            pygame.draw.circle(surface, self.color, (x, y), r, self.outline)
        else:
            x = self.rect[0]
            y = self.rect[1]

            pygame.draw.rect(surface, self.color, self.rect, self.outline)

        if self.text is not None:
            text_surface = self.font.render(self.text, 1, self.textColor)
            surface.blit(text_surface, (x, y))

    def setPos(x, y):
        if self.rect is None:
            self.circle = [x, y, self.circle[2]]
        else:
            self.rect = [x, y] + self.rect[2:]

class gridSpace():
    def __init__(self,
                 color = (200, 200, 200, 1),
                 highlightColor = (210, 210, 210, 1),
                 rect = [0, 0, 50, 50],
                 outline = 1,
                 objectsHere = [],
                 highlighted = False,
                 text = None):
        self.color = color
        self.defaultColor = color
        self.highlightColor = highlightColor
        self.rect = rect
        self.outline = outline
        self.defaultOutline = outline
        self.objectsHere = objectsHere
        self.highlighted = highlighted
        self.font = pygame.font.Font("Roboto-Regular.ttf", 16)
        self.text = text
        if text is not None:
            self.text = bytes(str(text), "utf-8")

    def addObject(self, obj):
        self.objectsHere.append(obj)

    def draw(self, surface):
        if self.text is not None:
            text_surface = self.font.render(self.text, 1, (0, 0, 0))
            surface.blit(text_surface, self.rect)
        pygame.draw.rect(surface, self.color, self.rect, self.outline)

    def getCenter(self):
        return [self.rect[0] + self.rect[2] // 2, self.rect[1] + self.rect[3] // 2]

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
    def __init__(self, width = 5, height = 5, totalWidth = 500, totalHeight = 500, numbers = False, color = (200, 200, 200, 1)):
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
                text = None
                if h == 0:
                    text = w + 1
                elif w == 0:
                    text = h + 1

                self.gridSpaces[w].append(
                    gridSpace(rect=[w * self.spaceDims[0],
                                    h * self.spaceDims[1],
                                    self.spaceDims[0],
                                    self.spaceDims[1]],
                              text = text))

    def addObject(self, obj):
        self.objects.append(obj)
        for w in range(obj.footprint[2]):
            for h in range(obj.footprint[3]):
                if len(self.gridSpaces) > obj.footprint[0] + w:
                    if len(self.gridSpaces[obj.footprint[0] + w]) > obj.footprint[1] + h:
                        self.gridSpaces[obj.footprint[0] + w][obj.footprint[1] + h].addObject(obj)

    def draw(self, surface):
        # Draw grid spaces
        for w in range(self.dims[0]):
            for h in range(self.dims[1]):
                self.gridSpaces[w][h].draw(surface)

        # Draw objects
        for obj in self.objects:
            obj.draw(surface)

    def getCoords(self, spaceCoords, center=False):
        """Returns the rectangle of a space, or the x, y center coords, based on space coordinates"""
        space = self.gridSpaces[spaceCoords[0]][spaceCoords[1]]
        if center:
            return space.getCenter()
        else:
            return space.rect
    
    def getSpace(self, cursorCoords):
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
        self.hoverSpace = list(spaceCoords)

    def lockSpace(self):
        """Locks a space while waiting for text to process"""
        self.lockedSpace = self.hoverSpace

    def removeObject(self, objType, location):
        """Removes the first instance of object with objType that exists at location"""
        smallestObj = None
        for obj in self.gridSpaces[location[0]][location[1]].getObjects():
            if obj.objType == objType or objType == "any":
                # Compare areas - smaller area should get picked
                if smallestObj is None \
                   or (obj.footprint[2] * obj.footprint[3] < smallestObj.footprint[2] * smallestObj.footprint[3]):
                    smallestObj = obj

        if smallestObj is None:
            return False
        else:
            obj = smallestObj
            for w in range(obj.footprint[2]):
                for h in range(obj.footprint[3]):
                    self.gridSpaces[obj.footprint[0] + w][obj.footprint[1] + h].removeObject(obj)
            self.objects.remove(obj)

            return True

    def toggleHighlight(self, spaceCoords, color = (210, 210, 210, 1)):
        """Toggles a space to highlight (or not)"""
        self.gridSpaces[spaceCoords[0]][spaceCoords[1]].toggleHighlight(color)

    def unhighlight(self, spaceCoords):
        """Unhighlights a space"""
        self.gridSpaces[spaceCoords[0]][spaceCoords[1]].unhighlight()

class messageCenter():
    def __init__(self, x, y, text = "Waiting for voice command.", defaultColor = (0, 0, 0), fontSize = 20):
        self.x = x
        self.y = y
        self.defaultColor = defaultColor
        self.font = pygame.font.Font("Roboto-Regular.ttf", 20)
        self.font.set_italic(True)
        self.text = text

    def draw(self, surface, color = None):
        if self.text is not None:
            if color is None:
                color = self.defaultColor

            text_surface = self.font.render(self.text, 1, color)
            surface.blit(text_surface, (self.x, self.y))

    def setText(self, text):
        self.text = text
