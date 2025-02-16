import json
import os
import re

def main():
    global FILE_DUMP
    FILE_DUMP = "TEMP_SAVE_FOLDER"
    os.makedirs(FILE_DUMP, exist_ok=True)
    # Open and read the JSON file
    with open(f"{FILE_DUMP}/response.json", 'r') as file:
        data = json.load(file)

    if isinstance(data, dict) and "choices" in data:
        text_content = data["choices"][0]["message"]["content"]  # Adjust this based on actual structure
    else:
        text_content = json.dumps(data)  # Convert entire dict to a string



    stuff = extract_json_from_text(text_content)
    print(stuff)

    output_path = f"{FILE_DUMP}/processed_response.json"
    with open(output_path, "w") as file:
        #json.dump(extracted_json, file, indent=4)
        file.write(stuff)

    print(f"Extracted JSON saved to {output_path}")


def extract_json_from_text(text):
    """
    Extracts json content from first { to last }, and returns it

    """

    start = 0
    end = 0
    for i in range(len(text)):
        if text[i] == "{":
            start = i
            break

    for j in range(len(text)):
        if text[j] == "}":
            end = j
    text = text[start:end+1]

    text = text.replace("\\n", "\n")
    text = text.replace("“", "\"")
    text = text.replace("”", "\"")
    text = text.replace("。", ".")
    text = text.replace("：", ":")
    text = text.replace("，", ",")
    text = text.replace("\u00A0", " ")

    return text

if __name__ == "__main__":
    main()
