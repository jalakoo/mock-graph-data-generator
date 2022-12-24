from enum import Enum, unique
import logging
import sys
import re
import numbers
# TODO: replace with dataclasses
# from dataclasses import dataclass

@unique
class GeneratorType(Enum):
    BOOL = 1,
    INT = 2,
    FLOAT = 3,
    STRING = 4,
    DATETIME = 5,
    ASSIGNMENT = 6
    RELATIONSHIP = 7

    @staticmethod
    def type_from_string(aType: str):
        type = aType.lower()
        if type == "string":
            return GeneratorType.STRING
        elif type == "int" or type == "integer":
            return GeneratorType.INT
        elif type == "float":
            return GeneratorType.FLOAT
        elif type == "datetime":
            return GeneratorType.DATETIME
        elif type == "bool":
            return GeneratorType.BOOL
        elif type == "assignment":
            return GeneratorType.ASSIGNMENT
        elif type == "relationship":
            return GeneratorType.RELATIONSHIP
        else:
            raise TypeError("Type not supported")
    
    def to_string(self):
        if self == GeneratorType.STRING:
            return "String"
        elif self == GeneratorType.INT:
            return "Integer"
        elif self == GeneratorType.FLOAT:
            return "Float"
        elif self == GeneratorType.DATETIME:
            return "Datetime"
        elif self == GeneratorType.BOOL:
            return "Bool"
        elif self == GeneratorType.ASSIGNMENT:
            return "Assignment"
        elif self == GeneratorType.RELATIONSHIP:
            return "Relationship"
        else:
            raise TypeError("Type not supported")


class GeneratorArg():

    @staticmethod
    def from_dict(dict: dict):
        if "type" not in dict.keys():
            raise KeyError("Arg dict missing type key")
        if "label" not in dict.keys():
            raise KeyError("Arg dict missing label key")
        if "default" not in dict.keys():
            default = None
        else: 
            default = dict["default"]
        if "hint" not in dict.keys():
            hint = ""
        else:   
            hint = dict["hint"]
        if "placeholder" not in dict.keys():
            placeholder = ""
        else:
            placeholder = dict["placeholder"]
        # if "description" not in dict.keys():
        #     description = ""
        # else:
        #     description = dict["description"]

        return GeneratorArg(
            type = GeneratorType.type_from_string(dict["type"]),
            label = dict["label"],
            default= default,
            hint = hint,
            placeholder = placeholder
            # description=description
        )

    def __init__(
        self, 
        type: GeneratorType, 
        label: str,
        default: any = None,
        hint : str = None,
        placeholder: str = None
        # description : str = None
    ):
        self.type = type
        self.label = label
        self.default = default
        self.hint = hint
        self.placeholder = placeholder
        # self.description = description

    def __str__(self):
        return f'GeneratorArg: type: {self.type}, label: {self.label}, default: {self.default}, hint: {self.hint}, placeholder: {self.placeholder}'

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            "type": self.type.to_string(),
            "label": self.label,
            "default": self.default,
            "hint": self.hint,
            "placeholder":self.placeholder
        }

    @staticmethod
    def list_from(list: list[dict]):
        return [GeneratorArg.from_dict(item) for item in list]


def generators_from_json(json : dict) -> dict:
    result = {}
    for key in json.keys():
        if key == "README":
            # Special key for embedding notes in the json 
            # Hacky but whatever
            continue
        generator = Generator.from_dict(key, json[key])
        result[key] = generator
    return result

class Generator():

    # TODO: Support pattern generation and property based values
    @staticmethod
    def from_dict(
        id: str,
        generator_dict: dict
    ):
        if 'name' not in generator_dict.keys():
            raise Exception("Generator must have a name")
        if 'type' not in generator_dict.keys():
            raise Exception("Generator must have a type")
        if 'description' not in generator_dict.keys():
            raise Exception("Generator must have a description")
        if 'code_url' not in generator_dict.keys():
            raise Exception("Generator must have code")
        if 'args' not in generator_dict.keys():
            args = []
        else :
            args = GeneratorArg.list_from(generator_dict['args'])
        if 'tags' not in generator_dict.keys():
            tags = []
        else:
            tags = generator_dict['tags']
        
        return Generator(
            id = id,
            type = GeneratorType.type_from_string(generator_dict['type']),
            name = generator_dict['name'],
            description = generator_dict['description'],
            code_url = generator_dict['code_url'],
            args = args,
            tags = tags
        )

    def __init__(
        self, 
        id: str,
        type : GeneratorType, 
        name: str, 
        description: str, 
        code_url: str,
        args: list[GeneratorArg],
        tags: list[str]
        ):
        self.id = id
        self.name = name
        self.description = description
        self.code_url = code_url
        self.args = args
        self.type = type
        self.tags = tags
    
    def import_url(self):
        trimmed = self.code_url.split("/", 1)[1]
        return trimmed.replace("/", ".").replace(".py", "")

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "code_url": self.code_url,
            "args": [arg.to_dict() for arg in self.args],
            "type": self.type.to_string(),
            "tags": self.tags
        }

    def __str__(self):
        return f'Generator: id: {self.id}, name: {self.name}, type: {self.type}, args: {self.args}'

    def __repr__(self):
        return self.__str__()

    def generate(self, args):
        # Args are not the same as the generator args, these are the arg inputs from user
        module = __import__(self.import_url(), fromlist=['generate'])
        try:
            result = module.generate(args)
            return result
        except:
            logging.error(f"Error generating data for generator {self.name}, id {self.id}: {sys.exc_info()[0]}")
            return None


def generators_dict_to_json(dict: dict[str, Generator]) -> str:
    return {key: value.to_dict() for key, value in dict.items()}

def generators_list_to_json(list: list[Generator]) -> str:
    return [generator.to_dict() for generator in list]

# TODO: Move this to a separate recommendation class
def recommended_generator_from(
    string: str, 
    generators: list[Generator]
    ) -> Generator:
    # Naive attempt to break up name into words
    replaced_string = string.lower().replace(" ", "_")
    possible_tags = re.split(r'[_-]', replaced_string)

    # Rank generators by number of tag matches
    highest_score = 0
    recommended_generators = []
    for generator in generators:
        lowered_tags = [tag.lower() for tag in generator.tags]
        score = len([possible_tags.index(i) for i in lowered_tags if i in possible_tags])
        if score > highest_score:
            highest_score = score
            recommended_generators.append({"generator": generator, "score": score})
        
    if len(recommended_generators) == 0:
        return None

    # Else recommend the highest scoring generator
    def sort_by_score(generator_dict):
        return generator_dict["score"]
    
    return sorted(recommended_generators, key=sort_by_score, reverse=True)[0]["generator"]