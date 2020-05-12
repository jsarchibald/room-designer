# These are the objects the user can place in the scene.
obj_types = {
    "cocktail": {
        "shape": "circle",
        "color": (70, 70, 70),
        "outline": 0,
        "text_color": (255, 255, 255),
        "description": "Cocktail table"
    },
    "table": {
        "shape": "rectangle",
        "color": (95, 32, 0),
        "outline": 0,
        "text_color": (255, 255, 255),
        "description": "Table"
    },
    "room": {
        "shape": "rectangle",
        "color": (255, 0, 0),
        "outline": 2,
        "text_color": (0, 0, 0),
        "description": "Room"
    },
    "couch": {
        "shape": "rectangle",
        "color": (154, 0, 130),
        "outline": 0,
        "text_color": (255, 255, 255),
        "description": "Couch"
    }
}

# Allow for use of synonyms -- this is a mapping from synonym to object key above
synonyms = {
    "salon": "room",
    "sofa": "couch"
}

possible = set(obj_types.keys()).union(set(synonyms.keys()))
