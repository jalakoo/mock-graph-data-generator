import streamlit as st
from constants import *
import json
import logging
from widgets.node_row import nodes_row
from widgets.relationship_row import relationship_row
from widgets.property_row import property_row

def mapping_tab():

    col1, col2 = st.columns([1,11])
    with col1:
        st.image("mock_generators/media/shuffle.gif")
    with col2:
        st.write("Create and edit mock data generation options. \n\nNodes and relationships are default INCLUDED from mapping, meaning data will be generated for all imported nodes and relationships.  Expand options for each node or relationship > Edit labels > Edit property names > Assign generator functions to create desired mock data.\n\nAdditional Global, for all Nodes, and for all Relationship properties can also be set.")
    uploaded_file = st.session_state[IMPORTED_FILE]
    # if uploaded_file is not None:
    #     with st.expander("Imported File"):
    #         st.text(uploaded_file)
    st.markdown("--------")

    # Default options
    # Matching arrows.json dict format
    nodes = [
        {
        "id": "n0",
        "position":{
            "x": 0,
            "y": 0
        },
        "caption": "Person",
        "labels": [],
        "properties": {
            "uuid": "string",
            "name": "string",
        }
    },
    {
        "id": "n1",
        "position":{
            "x": 200,
            "y": 200
        },
        "caption": "Company",
        "labels": [],
        "properties": {
            "uuid":"string",
            "name": "string",
        }
    }]
    relationships = [{
        "id": "n0",
        "type": "WORKS_AT",
        "fromId": "n0",
        "toId": "n1",
        "properties": {
        }
    }]

    # Convert uploaded file (if available) to json
    # Supporting arrows 0.5.4
    if uploaded_file is not None:
        try:
            json_file = json.loads(uploaded_file)
            nodes = json_file["nodes"]
            relationships = json_file["relationships"]
            
        except json.decoder.JSONDecodeError:
            st.error('JSON file is not valid.')

    st.write("**GLOBALS:**")
    g1, g2, g3 = st.columns(3)
    should_expand = False
    with g1:
        num_global_properties = st.number_input("Number of Global Properties", min_value=0, value=0, help="Properties to add to ALL nodes and relationships to be generated.")
    with g2:
        include_globals = st.checkbox("Include Global Properties", value=True, help="Include global properties in data generation. These will currently overwrite any node local properties with the same property name.")
    with g3:
        should_expand = st.checkbox("Expand All Rows", value=False, help="Automatically expand all row details")
    all_global_properties = []
    if include_globals == True:
        for i in range(num_global_properties):
            global_property = property_row(
                type="global",
                id = f'',
                index = i,
                properties = []
            )
            all_global_properties.append(global_property)

    st.markdown("--------")
    st.write("**NODES:**")
    # TODO: Add ability to add ALL NODES ONLY properties
    num_nodes = st.number_input("Number of nodes", min_value=1, value=len(nodes), key="mapping_number_of_nodes")
    for i in range(num_nodes):
        if i < len(nodes):
            nodes_row(
                nodes[i], 
                should_start_expanded=should_expand,
                additional_properties=all_global_properties)
        else:
            nodes_row(None)

    st.markdown("--------")
    st.write("**RELATIONSHIPS:**")
    # TODO: Add ability to add ALL RELATIONSHIPS ONLY properties
    num_relationships = st.number_input("Number of relationships", min_value=1, value=len(relationships), key="mapping_number_of_relationships")
    for i in range(num_relationships):
        if i < len(relationships):
            relationship_row(
                relationships[i],
                should_start_expanded=should_expand,
                additional_properties=all_global_properties)
        else:
            relationship_row(None)