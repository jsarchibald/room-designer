# Some helper functions for processing speech commands

import objects as obj_types

def correct_text(text):
    """Because Google gives English, not commands"""

    text = text.lower()
    text = text.replace("-", " ")
    text = text.split(" ")

    conversions = [
        [["one", "won"], "1"],
        [["to", "too", "two"], "2"],
        [["three", "free"], "3"],
        [["four"], "4"],
        [["five"], "5"],
        [["six"], "6"],
        [["seven"], "7"],
        [["eight", "ate", "hate"], "8"],
        [["nine"], "9"],
        [["ten"], "10"],
        [["+"], "and"],
        [["x"], "by"],
        [["buy"], "by"],
        [["criticize", "play"], "create a size"]
    ]

    for i in range(len(text)):
        for conversion in conversions:
            if text[i] in conversion[0]:
                text[i] = conversion[1]
                
    return text

def either_side(text, delimiter = "and", default = [-1, -1]):
    """Take form 12 AND 15 to return [12, 15] for example"""
    if delimiter in text:
        pos = text.index(delimiter)
        if text[pos - 1].isnumeric() and text[pos + 1].isnumeric():
            return [int(text[pos - 1]), int(text[pos + 1])]
        else:
            return default
    else:
        return default

def get_after(keyword, text):
    """Returns everything after the keyword in the full text provided."""
    return text[text.index(keyword) + 1:]

def get_position(text):
    """Will look for position keywords and returns the first. [-1, -1] if nonexistent."""
    location = [-1, -1]
    if "and" in text:
        location = either_side(text, "and")
        location[0] -= 1
        location[1] -= 1

    return location

def get_positions(text, min=0):
    """Finds all positions. Returns a list thereof."""
    locations = list()
    while "and" in text:
        locations.append(get_position(text))
        text = get_after("and", text)
    while len(locations) < min:
        locations.append([-1, -1])
    
    return locations

def get_size(text):
    """Finds size parameters in text."""
    size = [1, 1]
    if "by" in text:
        size = either_side(text, "by", [1, 1])
    return size

def is_in_objects(text):
    """Will tell you the definitive key of the object_types list to use.
       Or returns None if it's not in the keywords at all."""

    obj_type_int = obj_types.possible.intersection(text)
    if len(obj_type_int) > 0:
        obj = obj_type_int.pop()
        if obj in obj_types.synonyms:
            obj = obj_types.synonyms[obj]

        return obj
    else:
        return None

def select_obj_type(text):
    """If not in objects, calls it "any" """
    obj = is_in_objects(text)
    if obj is None:
        obj_type = "any"
    else:
        obj_type = obj

    return obj_type