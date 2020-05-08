# Some helper functions for processing speech commands

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
