StepsTutorial = {
    "title": "Steps Tutorial",
    "description": "Step by step break down of how to fix a car issue",
    "type": "object",
    "properties": {
        "sources": {
            "type": "array",
            "description": "List of sources used. Can be empty",
            "items": {
                    "type": "string",
                    "description": "website link"
                }
            },
        "steps": {
            "type": "array",
            "description": "Detailed step-by-step breakdown of the process. Each step should be clear and concise.",
            "items": {
                "type": "object",
                "description": "Detailed description of each step",
                "properties": {
                    "step_number": {
                        "type": "integer",
                        "description": "Step number"
                    },
                    "step_description": {
                        "type": "string",
                        "description": "Step description, for example: Remove the red wire from the car battery."
                    },
                    "is_current_step": {"type": "boolean", "description": "Is this the current step the user is on."},
                },
                "required": ["step_number","step_description"]
            }
        },
        "additional_context": {
            "type": "string",
            "description": "Essential details that the user must know, including tools required for and safety precautions. This field should ensure that all critical information is conveyed clearly."
        }
    },
    "required": ["sources", "steps", "additional_context"],
}