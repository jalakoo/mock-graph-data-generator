import streamlit as st
from constants import *
# from models.mapping import Mapping
from logic.generate_csv import generate_csv
from logic.generate_data_import import generate_data_importer_json
import os
import logging
import sys
import zipfile
from widgets.folder_files import folder_files_expander
from datetime import datetime
import json

def generate_tab():
    col1, col2 = st.columns([1,11])
    with col1:
        st.image("mock_generators/media/fireworks.gif")
    with col2:
        st.write("Generate mock graph data.\n\nBe sure you're happy with the mocking options in the Mapping tab before running.\n\nWhen finished, proceed to the Export tab to review and download the generated data.")
    st.markdown("--------")

    mapping = st.session_state[MAPPINGS]
    export_folder = st.session_state[EXPORTS_PATH]
    zips_folder = st.session_state[ZIPS_PATH]
    imported_filename = st.session_state[IMPORTED_FILENAME]

    # TODO: Implement better filename cleaning
    # TODO: Breaks when using a copy and pasted file
    export_zip_filename = f'{imported_filename}'.lower()
    export_zip_filename = export_zip_filename.replace(".json", "")
    export_zip_filename.replace(" ", "_")
    export_zip_filename.replace(".", "_")

    g1, g2, g3, g4 = st.columns(4)

    with g1:
        st.write('MAPPING DATA:')
        if MAPPINGS not in st.session_state:
            # Why hasn't mappings been preloaded by now?
            st.error(f'Mappings data was not preloaded')
        elif st.session_state[MAPPINGS] is None:
            st.error(f'Mappping option not valid for generation. Please configure mapping options below.')
        elif st.session_state[MAPPINGS].is_empty() == True:
            st.error(f'No data currently mapped. Please configure in Mapping tab.')
        elif st.session_state[MAPPINGS].is_valid() == False:
            st.error(f'Mappping option not valid for generation. Please configure in Mapping tab.')
        else:
            st.success(f'Mappping options valid for generation.')

        # For the curious
        with st.expander("Raw Mapping Data"):
            st.json(mapping.to_dict())

        # should_clear = st.checkbox("Delete all files in export folder with each Generate run", value=True)

    with g2:
        st.write(f'READY FOR GENERATION:')
        st.write(f'     - {len(mapping.nodes)} Nodes')
        st.write(f'     - {len(mapping.relationships)} Relationships')
    with g3:
        st.write(f'GENERATE DATA:')
        if st.button('FOR DATA-IMPORTER', key=f'generate_data_button'):

            # Stop if no mapping data available
            if len(mapping.nodes) == 0:
                st.error('No nodes to generate data for. Map at least one noded.')
                st.stop()
                return

            for key, node in mapping.nodes.items():
                # logging.info(f'Generating data for node: {node}')
                if len(node.properties) == 0:
                    st.error(f'Node {node.caption} has no properties. Add at least one property to generate data.')
                    st.stop()
                    return

            # Delete all files in export folder first
            dir = export_folder
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))

            # Data Importer Options
            success = generate_csv(
                mapping, 
                export_folder=export_folder)

            # Check that data was generated
            if success == False:
                st.error('Error generating data. Check console for details.')
                # st.stop()
                # return

            success = generate_data_importer_json(
                mapping,
                export_folder=export_folder,
                export_filename=DEFAULT_DATA_IMPORTER_FILENAME)

            # Check that data-import data was generated
            if success == False:
                st.error('Error generating data-import json. Check console for details.')
                # st.stop()
                # return

            # Only attempt to zip files if data generation was successful
            if success:
                try:
                    # Create zip file, appended with time created
                    now = str(datetime.now().isoformat())
                    zip_path = f'{zips_folder}/{export_zip_filename}_{now}.zip'
                    logging.info(f'generate_tab: Creating zip file: {zip_path}')
                    with zipfile.ZipFile(f'{zip_path}', 'w', zipfile.ZIP_DEFLATED) as zipf:
                        # zipdir(export_folder, zipf)
                        path = export_folder
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                if file[0] =='.':
                                    # Skip hidden files
                                    continue
                                zipf.write(os.path.join(root, file), 
                                        os.path.relpath(os.path.join(root, file), 
                                                        os.path.join(path, '..')))
                except:
                    st.error(f'Error creating zip file: {sys.exc_info()[0]}')
                    # st.stop()
                    return

            if success == True:
                st.success('Data generated successfully.')

    with g4:
        st.write(f'GENERATED DATA SUMMARY:')
        # TODO: Why do these disappear when returning to tab?
        nodes = st.session_state[MAPPINGS].nodes
        for _, node in nodes.items():
            values = node.generated_values
            if values is not None:
                st.write(f'     - {len(node.generated_values)} {node.caption} nodes generated')

        relationships = mapping.relationships
        for _, relationship in relationships.items():
            values = relationship.generated_values
            if values is not None:
                st.write(f'     - {len(relationship.generated_values)} {relationship.type} relationships generated')
