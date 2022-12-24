import streamlit as st
from constants import *
import logging
from models.generator import Generator, GeneratorType, recommended_generator_from
from models.property_mapping import PropertyMapping
import datetime
import sys

def property_row(
    type: str,
    pid: str,
    index: int, 
    properties: list[dict],
    ) -> PropertyMapping:

    # Create a new propertyMapping for storing user selections

    existing_name = ""
    recommended_generator = None

    pc1, pc2, pc3, pc4, pc5, pc6 = st.columns(6)
    
    # Property name
    with pc1:

        if index < len(properties):
            # Get key of uploaded property
            existing_name = properties[index][0]
            # TODO: Find away to pass in node labels and relationship types to this string
            recommended_generator = recommended_generator_from(existing_name, st.session_state[GENERATORS].values())
            if recommended_generator is None:
                logging.info(f'No recommended generator for property {existing_name}')
        name = st.text_input("Property Name",value=existing_name, key=f"{type}_{pid}_property_{index}_name")
        if name is None or name == "":
            st.error("Property name cannot be empty")
        # if name[0] == "_":
        #     st.error("Property names cannot start with an underscore")
        #     name = None

    # Property type
    with pc2:
        type_selections = ["String", "Bool", "Integer", "Float", "Datetime"]
        recommended_type_index = 0
        if recommended_generator is not None:
            recommended_type_index = type_selections.index(recommended_generator.type.to_string())
        generator_type_string = st.selectbox("Type", type_selections, index=recommended_type_index, key=f"{type}_{pid}_property_{index}_type")

    # Generator to create property data with
    with pc3:



        recommended_generator_index = 0
        # TODO: Hot reloading breaks here - unable to properly filter generators by type anymore - have to do a hard refresh - WHY?

        # possible_generators =  [generator for generator in st.session_state[GENERATORS].values() if generator.type == generator_type]

        possible_generators = []
        for generator in st.session_state[GENERATORS].values():
            if generator.type.to_string() == generator_type_string:
                possible_generators.append(generator)

        def sort_by_name(generator: Generator):
            return generator.name
        possible_generators.sort(key=sort_by_name)

        if possible_generators is None or len(possible_generators) == 0:
            generators_by_type = [{"id":generator.id, "type":generator.type} for generator in st.session_state[GENERATORS].values()]
            logging.error(f'property_row.py: No generators found for type {generator_type_string}. List of generators by type: {generators_by_type}')
            return PropertyMapping.empty()
        possible_generator_names = [generator.name for generator in possible_generators]

        if recommended_generator is not None:
            try:
                recommended_generator_index = possible_generator_names.index(recommended_generator.name)
            except:
                logging.error(f'property_row.py: Unexpected error while trying to find recommended generator: {recommended_generator.name} from possible names: {possible_generator_names} from possible generators: {possible_generators}: {sys.exc_info()[0]}')
        selected_generator_name = st.selectbox("Generator", possible_generator_names, index=recommended_generator_index, key=f"{type}_{pid}_property_{index}_generator", help="See the Generators Tab for more details on a given generator.")

        selected_generators = [generator for generator in possible_generators if generator.name == selected_generator_name]
        if len(selected_generators) == 0:
            st.error(f'No generator found for {selected_generator_name}')
            selected_generator = None
        else:
            selected_generator = selected_generators[0]


    # Optional Property Generator arguments, if any
    with pc4:
        # TODO: replace with generator_args widget
        args = []
        if selected_generator is not None:
            for p_index, arg in enumerate(selected_generator.args):
                if arg.type == GeneratorType.STRING:
                    arg_input = st.text_input(
                        label=arg.label, 
                        value = arg.default,
                        key = f'{type}_{pid}_property_{name}_generator_{selected_generator.id}_{arg.label}',
                        help = f'{arg.hint}',
                        placeholder = f'{arg.placeholder}'
                        )
                elif arg.type == GeneratorType.INT or arg.type == GeneratorType.FLOAT:
                    arg_input = st.number_input(
                        label= arg.label,
                        value= arg.default,
                        key = f'{type}_{pid}_property_{name}_generator_{selected_generator.id}_{arg.label}',
                        help = f'{arg.hint}'
                        )
                elif arg.type == GeneratorType.BOOL:
                    arg_input = st.radio(
                        label=arg.label,
                        index=arg.default,
                        key = f'{type}_{pid}_property_{name}_generator_{selected_generator.id}_{arg.label}',
                        help = f'{arg.hint}'
                    )
                    # arg_inputs.append()
                elif arg.type == GeneratorType.DATETIME:
                    arg_input = st.date_input(
                        label=arg.label,
                        value=datetime.datetime.fromisoformat(arg.default),
                        key = f'{type}_{pid}_property_{name}_generator_{selected_generator.id}_{arg.label}',
                        help = f'{arg.hint}'
                        )
                else:
                    raise Exception(f'property_row.py: Unknown argument type {arg.type} from generator {selected_generator}')
                    
                args.append(arg_input)

        generator_type = GeneratorType.type_from_string(generator_type_string)

        property_map = PropertyMapping(
            pid=f'{type}_{pid}_property_{index}',
            name=name,
            type=generator_type,
            generator=selected_generator,
            args=args
        )


    # Display sample data
    with pc5:
        if selected_generator is not None:
            result = selected_generator.generate(property_map.args)
            st.write(f'Sample')
            st.text(f'{result}')
    
    with pc6:
        st.write("Options")
        should_ignore = st.checkbox("Exclude/ignore", value=False,  key=f"{type}_{pid}_property_{index}__ignore")

    # TODO: Update to fail validation if any property items failed (ie empty name)
    if should_ignore == True:
        return PropertyMapping.empty()
        
    return property_map