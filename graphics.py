import json
from pathlib import Path
import pygame
from tkinter import filedialog

import objects as object_types
from settings import SCREEN_DIMS, WINDOW_CONST

class roomObject():
    def __init__(self,
                 color = (0, 0, 255, 1),
                 rect = None, # or (x, y, w, h)
                 circle = None, # or (x, y, r)
                 outline = 0, # is width for circles
                 text = None,
                 objType = "room",
                 footprint = [0, 0, 1, 1],
                 textColor = (255, 255, 255),
                 textSize = 16):
        self.color = color
        self.rect = rect
        self.circle = circle
        self.outline = outline
        self.font = pygame.font.Font("fonts/Roboto-Regular.ttf", textSize)
        self.textColor = textColor
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

    def getAttributes(self):
        text = ""
        if self.text != None:
            text = self.text.decode("utf-8")
        
        attributes = {
            "color": self.color,
            "rect": self.rect,
            "circle": self.circle,
            "outline": self.outline,
            "textColor": self.textColor,
            "text": text,
            "objType": self.objType,
            "footprint": self.footprint
        }
        return attributes

    def getPos(self):
        return self.footprint[0:2]

    def setPos(self, x, y, xs, ys, dims):
        if xs + self.footprint[2] > dims[0] or ys + self.footprint[3] > dims[1]:
            return False
        
        if self.rect is None:
            self.circle = [x, y, self.circle[2]]
            self.footprint = [xs, ys] + self.footprint[2:]
        else:
            self.rect = [x, y] + self.rect[2:]
            self.footprint = [xs, ys] + self.footprint[2:]

    def setText(self, text):
        if text is not None:
            self.text = bytes(str(text), "utf-8")

class gridSpace():
    def __init__(self,
                 color = (200, 200, 200, 1),
                 highlightColor = (210, 210, 210, 1),
                 rect = [0, 0, 50, 50],
                 outline = 1,
                 objectsHere = None,
                 highlighted = False,
                 text = None,
                 textSize = 16):
        self.color = color
        self.defaultColor = color
        self.highlightColor = highlightColor
        self.rect = rect
        self.outline = outline
        self.defaultOutline = outline
        self.objectsHere = objectsHere
        if objectsHere is None:
            self.objectsHere = set()
        self.highlighted = highlighted
        self.font = pygame.font.Font("fonts/Roboto-Regular.ttf", textSize)
        self.text = text
        if text is not None:
            self.text = bytes(str(text), "utf-8")

    def addObject(self, obj):
        self.objectsHere.add(obj)

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
    def __init__(self,
                 width = 5,
                 height = 5,
                 totalWidth = 500,
                 totalHeight = 500,
                 numbers = False,
                 color = (200, 200, 200, 1),
                 file_name = "__RENAME__",
                 title = "New room",
                 gridTextSize = 16,
                 textSize = 16):

        self.file_name = file_name
        self.title = title
        self.dims = [width, height]
        self.totalDims = [totalWidth, totalHeight]
        self.spaceDims = [totalWidth // width, totalHeight // height]
        self.hoverSpace = [-1, -1]
        self.lockedSpace = [-1, -1]
        self.waitFunction = []
        self.dead = False
        self.gridTextSize = gridTextSize
        self.textSize = textSize

        self.objects = set()
        self.createGridSpaces(width, height)

    def addObject(self, obj):
        self.objects.add(obj)
        for w in range(obj.footprint[2]):
            for h in range(obj.footprint[3]):
                if len(self.gridSpaces) > obj.footprint[0] + w:
                    if len(self.gridSpaces[obj.footprint[0] + w]) > obj.footprint[1] + h:
                        self.gridSpaces[obj.footprint[0] + w][obj.footprint[1] + h].addObject(obj)

    def createGridSpaces(self, width, height):
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
                              text = text,
                              textSize = self.gridTextSize))

    def draw(self, surface):
        # Draw grid spaces
        for w in range(self.dims[0]):
            for h in range(self.dims[1]):
                self.gridSpaces[w][h].draw(surface)

        # Draw objects
        for obj in self.objects:
            obj.draw(surface)

    def export(self, path=None):
        """Export this project to JPG or PNG"""
        save = self.getSaveData()
        roomGrid = grid(self.dims[0], self.dims[1], 2048, 2048, True, gridTextSize=32, textSize=48)
        roomGrid.setData(save)
        
        surface = pygame.Surface((2048, 2048))
        surface.fill((255, 255, 255))
        roomGrid.draw(surface)

        if path is None:
            # Have to make resizable so file dialog appears
            if WINDOW_CONST == pygame.FULLSCREEN:
                pygame.display.set_mode(SCREEN_DIMS, pygame.RESIZABLE)

            path = filedialog.asksaveasfilename(title="Choose a file location and name.", filetypes=[("JPEG", ".jpg"), ("PNG", ".png")], defaultextension=".jpg")

            if WINDOW_CONST == pygame.FULLSCREEN:
                pygame.display.set_mode(SCREEN_DIMS, pygame.FULLSCREEN)

        try:
            pygame.image.save(surface, path)
            return True
        except:
            return False

    def getCoords(self, spaceCoords, center=False):
        """Returns the rectangle of a space, or the x, y center coords, based on space coordinates"""
        space = self.gridSpaces[spaceCoords[0]][spaceCoords[1]]
        if center:
            return space.getCenter()
        else:
            return space.rect

    def getSaveData(self):
        """Returns the save data of this project"""
        save = {
            "meta": {
                "title": self.title,
                "dimensions": self.dims
            },
            "objects": self.saveObjects()
        }

        return save

    def getSmallestAt(self, location, objType):
        """Returns the smallest item at a given gridspace"""

        if location[0] < 0 or location[1] < 0:
            return False

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
            return smallestObj

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

    def moveObject(self, objType, location, to_location):
        """Moves the first instance of object with objType that exists at location"""
        obj = self.getSmallestAt(location, objType)
        
        if obj != False and (len(to_location) == 3 or (to_location[0] > -1 and to_location[1] > -1)) \
           and to_location[0] < self.dims[0] and to_location[1] < self.dims[1]:           
            if len(to_location) == 3 and to_location[2] == "relative":
                orig = obj.getPos()
                to_location = [orig[0] + to_location[0], orig[1] + to_location[1]]

            if to_location[0] < 0 or to_location[1] < 0 or to_location[0] >= self.dims[0] or to_location[1] >= self.dims[1]:
                return False
            
            self.removeObject(objType, location)

            # If circle, use get_coords
            if obj.circle is not None:
                coords = self.getCoords(to_location, True)
                obj.setPos(coords[0], coords[1], to_location[0], to_location[1], self.dims)
            elif obj.rect is not None:
                obj.setPos(to_location[0] * self.spaceDims[0], to_location[1] * self.spaceDims[1], to_location[0], to_location[1], self.dims)

            self.addObject(obj)

            return True
        else:
            return False

    def openFile(self, path):
        """Opens a saved room design. Returns file's name."""
        self.file_name = path
        
        with open(path) as f:
            data = json.load(f)
        
        self.setData(data)

    def removeObject(self, objType, location):
        """Removes the first instance of object with objType that exists at location"""
        obj = self.getSmallestAt(location, objType)
        if obj != False:
            for w in range(obj.footprint[2]):
                for h in range(obj.footprint[3]):
                    self.gridSpaces[obj.footprint[0] + w][obj.footprint[1] + h].removeObject(obj)
            self.objects.remove(obj)

            return True
        else:
            return False

    def renameObject(self, objType, location, text):
        """Renames the first instance of object with objType that exists at location"""
        obj = self.getSmallestAt(location, objType)
        
        if obj != False:
            obj.setText(text)

            return True
        else:
            return False

    def resizeObject(self, objType, location, size):
        """Resizes the first instance of object with objType that exists at location to the size provided."""
        obj = self.getSmallestAt(location, objType)

        if obj != False:
            obj = obj.getAttributes()

            # Circles are always 1x1
            if obj["rect"] is None:
                return False

            self.removeObject(objType, location)

            # Make sure size is positive
            f = obj["footprint"]
            f[2] = abs(size[0])
            f[3] = abs(size[1])

            # If too big, make it as big as possible
            if f[0] + f[2] >= self.dims[0]:
                f[2] = self.dims[0] - f[0]
            if f[1] + f[3] >= self.dims[1]:
                f[3] = self.dims[1] - f[1]
                

            obj["rect"] = [f[0] * self.spaceDims[0],
                           f[1] * self.spaceDims[1],
                           f[2] * self.spaceDims[0],
                           f[3] * self.spaceDims[1]]

            roomObj = roomObject(color=obj["color"],
                                 rect=obj["rect"],
                                 circle=obj["circle"],
                                 outline=obj["outline"],
                                 text=obj["text"],
                                 textColor=obj["textColor"],
                                 objType=obj["objType"],
                                 footprint=obj["footprint"],
                                 textSize=self.textSize)
            self.addObject(roomObj)

            return True
        else:
            return False

    def saveFile(self, screen_dims, path = None):
        """Saves object list as JSON to given path"""
        if path is None:
            path = self.file_name
        if path == "__RENAME__":
            # Have to make resizable so file dialog appears
            if WINDOW_CONST == pygame.FULLSCREEN:
                pygame.display.set_mode(screen_dims, pygame.RESIZABLE)

            path = filedialog.asksaveasfilename(title="Choose a file location and name.", filetypes=[("JSON", ".json")], defaultextension=".json")
            title = Path(path).stem

            if WINDOW_CONST == pygame.FULLSCREEN:
                pygame.display.set_mode(screen_dims, pygame.FULLSCREEN)
        
        self.file_name = path
        self.title = title

        save = getSaveData(self)

        try:
            with open(path, "w") as f:
                json.dump(save, f)
            return True
        except:
            return False

    def saveObjects(self):
        """Saves objects to a list"""
        objects = list()
        for obj in self.objects:
            objects.append(obj.getAttributes())
        
        return objects

    def setData(self, data):
        """Set project data"""
        self.title = data["meta"]["title"]
        self.dims = data["meta"]["dimensions"]
        self.spaceDims = [self.totalDims[0] // self.dims[0], self.totalDims[1] // self.dims[1]]
        self.createGridSpaces(self.dims[0], self.dims[1])
        
        for obj in data["objects"]:
            # Footprint matters here, to adjust for different-sized screens.
            if obj["rect"] is not None:
                f = obj["footprint"]
                obj["rect"] = [f[0] * self.spaceDims[0],
                               f[1] * self.spaceDims[1],
                               f[2] * self.spaceDims[0],
                               f[3] * self.spaceDims[1]]
            if obj["circle"] is not None:
                f = obj["footprint"]
                obj["circle"] = self.getCoords(f[0:2], True) + [self.spaceDims[0] // 2]

            roomObj = roomObject(color=obj["color"],
                                 rect=obj["rect"],
                                 circle=obj["circle"],
                                 outline=obj["outline"],
                                 text=obj["text"],
                                 textColor=obj["textColor"],
                                 objType=obj["objType"],
                                 footprint=obj["footprint"],
                                 textSize=self.textSize)
            self.addObject(roomObj)

    def setFileName(self, name):
        """Set file output path"""
        self.file_name = name

    def setWaitFunction(self, name, params):
        """Set up a waiting function."""
        if name is None:
            self.waitFunction = []
        else:
            self.waitFunction = [name, params]

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
        self.font = pygame.font.Font("fonts/Roboto-Regular.ttf", 20)
        self.text = text

        # Key to objects
        self.objects = list()

        self.spacing = 30
        y_space = 50
        for obj in object_types.obj_types:
            ot = obj
            obj = object_types.obj_types[obj]
            if obj["shape"] == "circle":
                # Shift x and y for radius
                o = roomObject(obj["color"], circle=(self.x + 10, self.y + y_space + 10, 10), objType=ot)
                l = [self.font.render(obj["description"], 1, self.defaultColor), self.x + 70, self.y + y_space]
            else:
                o = roomObject(obj["color"], (self.x, self.y + y_space, 60, 20), objType=ot)
                l = [self.font.render(obj["description"], 1, self.defaultColor),
                     self.x + 70, self.y + y_space]

            self.objects.append(o)
            self.objects.append(l)
            y_space += self.spacing

        self.commands = [pygame.image.load("img/commands.png"), self.x, self.y + y_space]

    def draw(self, surface, color = None):
        # The key to objects
        for obj in self.objects:
            if type(obj) == list:
                surface.blit(obj[0], obj[1:])
            else:
                obj.draw(surface)

        surface.blit(self.commands[0], self.commands[1:])

        # The message text
        if self.text is not None:
            if color is None:
                color = self.defaultColor

            text_surface = self.font.render(self.text, 1, color)
            surface.blit(text_surface, (self.x, self.y))

    def setText(self, text):
        self.text = text
