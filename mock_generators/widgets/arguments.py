import streamlit as st
from constants import *
from models.generator import Generator, GeneratorArg, GeneratorType
import logging
import datetime

def input_type(label: str, type: str, key:str) -> any:
    type = type.lower()
    help = "Default value for the argument that will populate this generator arg when the generator is selected."
    if type == "string":
        return st.text_input(label, key=key, help=help)
    elif type == "int":
        return st.number_input(label, key=key, value = 0, help=help)
    elif type == "float":
        return st.number_input(label, key=key, value = 0.0, help=help)
    elif type == "bool":
        return st.checkbox(label, key=key, help=help)
    elif type == "datetime":
        date = st.date_input(label, key=key, help=help)
        return date.isoformat()
    else:
        raise Exception("Unknown type: " + type)

def generator_arguments(
    selected_generator: Generator,
    key: str) -> GeneratorArg:

    arg_inputs = []

    if selected_generator is None:
        return arg_inputs

    for index, arg in enumerate(selected_generator.args):
        if arg.type == GeneratorType.STRING:
            count_arg = st.text_input(
                label=arg.label, 
                value = arg.default,
                key = f'{key}_{selected_generator.id}_{index}_arg_input'
                )
        elif arg.type == GeneratorType.INT or arg.type == GeneratorType.FLOAT:
            count_arg = st.number_input(
                label= arg.label,
                value= arg.default,
                key = f'{key}_{selected_generator.id}_{index}_arg_input'
                )
        elif arg.type == GeneratorType.BOOL:
            count_arg = st.radio(
                label=arg.label,
                index=arg.default,
                key = f'{key}_{selected_generator.id}_{index}_arg_input'
            )
        elif arg.type == GeneratorType.DATETIME:
            count_arg = st.date_input(
                label=arg.label,
                value=datetime.datetime.fromisoformat(arg.default),
                key = f'{key}_{selected_generator.id}_{index}_arg_input')
        else:
            count_arg = None
        if count_arg is not None:
            if index >= len(arg_inputs):
                arg_inputs.append(count_arg)
            else:
                arg_inputs[index] = count_arg

    return arg_inputs

def new_generator_argument(
    index: int,
    type: str
    ) -> dict:
    # For new generator arguments
    st.write(f"Optional Argument {index + 1}")
    type_input= st.radio("Type", ["String", "Bool", "Int", "Float","Datetime"], key=f"arg_type_{index}_type_input")

    label = st.text_input("Name", key = f"arg_type_{index}_label", help="Name of the argument that will be displayed in the UI. (e.g. 'Name' or 'Age'. Leave blank to skip this argument.")

    default = input_type("Default Value", type_input, key=f"arg_type_{index}_default")

    placeholder = st.text_input("Placeholder", key = f"arg_type_{index}_placeholder", help="Placeholder text that will be displayed in the UI input field as an example of what a user may enter.")

    hint = st.text_input("Optional Hint", key = f"arg_type_{index}_hint", help="Optional hint text that will be displayed in the UI to help the user understand what to enter.")


    if label is not None and label != "":
        return {
            "type": type_input.lower(),
            "label": label,
            "default": default,
            "hint": hint,
            "placeholder": placeholder
        }
    return None
