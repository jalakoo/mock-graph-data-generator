import uuid
from file_utils import save_file, save_json
import logging
import sys
from models.generator import Generator, GeneratorArg, GeneratorType, generators_dict_to_json

def createGenerator(
    spec_filepath: str,
    code_filepath: str,
    existing: dict,
    type: str,
    name: str,
    description: str,
    code: str,
    args: list[dict],
    tags: list[str]
) -> bool:
    # Save generator entry to generators.json

    #  Generate new id
    id = str(uuid.uuid4())[:8]
    while id in existing.keys():
        id = str(uuid.uuid4())[:8]

    # Save code file to code folder
    filename = f"{code_filepath}/{id}.py"
    save_file(filename, code)

    new_generator = Generator(
        id = id,
        type = GeneratorType.type_from_string(type),
        name = name,
        description = description,
        code_url = filename,
        args = GeneratorArg.list_from(args),
        tags=tags
    )

    # Update generators.json in memory
    existing[id] = new_generator
    json = generators_dict_to_json(existing)

    # Update saved generators.json - should probably just reload after instead
    try:
        save_json(spec_filepath, json)
        return True
    except:
        logging.error(f"Could not save generators.json: {sys.exc_info()[0]}")
        return False