CarInfo = {
    "title": "CarInfo",
    "description": "Information about user's car",
    "type": "object",
    "properties": {
        "make": {
            "type": "string",
            "description": "Car make use \"unknown\" if not known or nothing was given,",
        },
        "model": {
            "type": "string",
            "description": "Car model use \"unknown\" if not known or nothing was given.",
        },
        "year": {
            "type": "integer",
            "description": "Car year use \"-1\" if unknown or nothing was given.",
        },
        "issue_with_car": {
            "type": "string",
            "description": "Issue with car use \"unknown\" if not known or nothing was given.",
        }
    },
    "required": ["make", "model", "year"],
}