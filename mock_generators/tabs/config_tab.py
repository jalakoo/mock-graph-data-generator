import streamlit as st
from constants import *
from file_utils import load_json, load_string
from models.generator import Generator, generators_from_json
import os
import sys
import logging
from widgets.folder_files import folder_files_expander

def config_tab() -> list[Generator]:

    col1, col2 = st.columns([1,11])
    with col1:
        st.image("mock_generators/media/options.gif")
    with col2:
        st.write(f"Optional Configuration Options.\n\nSkip to Design tab if not needing to change any default folder paths.")
    st.markdown("--------")

    # Import/Export configurations

    # Import Path
    ci1, ci2 = st.columns([1,2])
    with ci1:
        new_imports_path = st.text_input("Import Path", value=st.session_state[IMPORTS_PATH], help="Path to import previously uploaded JSON files from.")
        if new_imports_path != st.session_state[IMPORTS_PATH]:
            st.session_state[IMPORTS_PATH] = new_imports_path
    with ci2:
        st.write(f'Files in Import Path:')
        folder_files_expander(
            folder_path=st.session_state[IMPORTS_PATH],
            specific_extension=".json")

    # Generated Files path
    ce1, ce2 = st.columns([1,2])
    with ce1:
        new_exports_filepath = st.text_input("Generated Files folder path", st.session_state[EXPORTS_PATH], help="Folder path where generated files are placed. The final .zip file for data-importer use will zip all non-hidden files from this folder.")
        if new_exports_filepath != st.session_state[EXPORTS_PATH]:
            st.session_state[EXPORTS_PATH] = new_exports_filepath
    with ce2:
        st.write(f'Files in Generated Files Path:')
        folder_files_expander(
            folder_path=st.session_state[EXPORTS_PATH])

    # Export Zips path
    cz1, cz2 = st.columns([1,2])
    with cz1:
        new_zips_path = st.text_input("Zip Archives folder path", value=st.session_state[ZIPS_PATH], help="Folder path where generated files are zipped and placed. This .zip file can be uploaded directly to Neo4j's data-importer")
        if new_zips_path != st.session_state[ZIPS_PATH]:
            st.session_state[ZIPS_PATH] = new_zips_path
    with cz2:
        st.write(f'Files in Zip Exports Path:')
        # TODO: Why does this work in the export tab but not here?
        folder_files_expander(
            folder_path=st.session_state[ZIPS_PATH])

    # Load new generator template file
    cc1, cc2 = st.columns([1,2])
    with cc1:
        new_template_filepath = st.text_input("Generator Code Template file", st.session_state[CODE_TEMPLATE_FILE], help='File path to the generator code template file. This file is used as a starting point to generate new generator code files.')
        if new_template_filepath != st.session_state[CODE_TEMPLATE_FILE]:
            st.session_state[CODE_TEMPLATE_FILE] = new_template_filepath
        with open(st.session_state[CODE_TEMPLATE_FILE], "r") as file:
            code_template = file.read()
    with cc2:
        st.write("Loaded code template file")
        with st.expander("Generator Code Template"):
            st.code(code_template)


    # Load generators
    gc1, gc2 = st.columns([1,2])
    with gc1:
        new_spec_filepath = st.text_input("Generators Spec filepath", st.session_state[SPEC_FILE], help="File path to the generators spec file. This file contains the specifications for all generators as JSON file.")
        if new_spec_filepath != st.session_state[SPEC_FILE]:
            st.session_state[SPEC_FILE] = new_spec_filepath
    with gc2:
        generators = st.session_state[GENERATORS]
        try:
            with open(new_spec_filepath) as input:
                generators_file = input.read()
                generators_json = load_json(new_spec_filepath)
                new_generators = generators_from_json(generators_json)
                if generators != new_generators:
                    st.session_state[GENERATORS] = new_generators

        except FileNotFoundError:
            st.error('File not found.')
        st.write("Loaded spec file")
        with st.expander("Generators Spec JSON"):
            st.code(generators_file)

    # Load generators code
    cc1, cc2 = st.columns([1,2])
    with cc1:
        new_code_filepath = st.text_input("Generators Code folder path", st.session_state[CODE_FILE], help="Folder path to all generator code files. These Python files are loaded and ran during the data generation process.")
        if new_code_filepath != st.session_state[CODE_FILE]:
            st.session_state[CODE_FILE] = new_code_filepath
    files = ""
    with cc2:
        st.write(f'Code Files in path: {st.session_state[CODE_FILE]}')
        folder_files_expander(folder_path = st.session_state[CODE_FILE], specific_extension= ".py")

    
    # TODO: Verify export path is available

    # TODO: Add resest


    st.markdown("Images by Freepik from [Flaticon](https://www.flaticon.com/)")