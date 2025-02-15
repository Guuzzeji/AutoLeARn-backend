CarInfo = {
    "title": "CarInfo",
    "description": "Information about user's car",
    "type": "object",
    "properties": {
        "make": {
            "type": "string",
            "description": "Car make"
        },
        "model": {
            "type": "string",
            "description": "Car model"
        },
        "year": {
            "type": "integer",
            "description": "Car year"
        },
    },
    "required": ["make", "model", "year"],
}