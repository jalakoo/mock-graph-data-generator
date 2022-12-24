import csv
import random
import sys

# Do not change function name or arguments
def generate(args: list[any]):
    filepath = args[0]
    field = args[1]
    result = []
    try:
        with open(filepath, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                result.append(row[field])
    except:
        raise Exception(f'Generator could not read file {filepath}. {sys.exc_info()[0]}')
    return random.choice(result)