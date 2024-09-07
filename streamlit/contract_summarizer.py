import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth


# import streamlit.components.v1 as html
from PIL import Image


import streamlit.components.v1 as components
import base64
from tempfile import NamedTemporaryFile
from datetime import datetime
from functools import partial
from streamlit_text_rating.st_text_rater import st_text_rater

import json
import re
import os
import io
import openai
import requests

import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login(location='main', fields={'Login': 'Login'})
if authentication_status:

    # add current endpoint URL
    # a default URL can be attached if needed
    NGROK_web_address_f = os.getenv("OCR_END_POINT", "http://ocr_service:8000")
    openai.organization = os.getenv("OI_ORG", "")
    openai.api_key = (
        os.getenv("OI_KEY","")
    )


    def get_OCR_text(file_name, encoded_object):
        request_url_full_pdf = NGROK_web_address_f + "/get_text"
        payload ={"filename": file_name, "filedata": encoded_object}
        result = requests.post(request_url_full_pdf, data=payload)
        result_str = json.loads(result.content)
        result_text = result_str["result"]
        return result_text

    def get_digiPDF_text(file_name, encoded_object):
        request_url_full_pdf = NGROK_web_address_f + "/get_text_pdf"
        payload ={"filename": file_name, "filedata": encoded_object}
        result = requests.post(request_url_full_pdf, data=payload)
        result_str = json.loads(result.content)
        result_text = result_str["result"]
        return result_text
    

    def get_contract_summary(doc_text, english_var):
        if english_var:
            language = "in English"
        else:
            language = "by keeping the source language (German)"
        fields_txt = ", ".join(st.session_state["starting_options"])
        user_msg = (
                        'Given the text below, provide me with a summary of the most important information in the contract regarding the following topics: '+fields_txt+'. Formulate your answers '+language+' in a json format in the following way: {"topic1_key": "topic1_value", "topic2_key": "topic2_value", ...}. You leave topics you don\'t know blank. You only provide json!\n\nText:\n\n'
                        + doc_text[:8000] + "\nResult: "
                    )
        
        try:
            response = openai.Completion.create(
                engine="gpt-3.5-turbo-instruct",
                prompt=user_msg,
                temperature=0.1,
                max_tokens=512,
            )
            fills = response["choices"][0]["text"]
            fills = fills[fills.find("{") :]
            fills = fills[: fills.find("}") + 1]
            fills_dict = json.loads(fills)
            result_text = ""
            result_arr = []
            for key, value in fills_dict.items():
                if value!="":
                    result_arr.append(f"**{key}**: {value}")
        except:
            result_arr = ["**Unprocessable, please try again later.**"]
        fields_txt = ", ".join(st.session_state["starting_options"])

        return result_arr




    def submit_result():
        if len(st.session_state["starting_options"])<st.session_state["options_max"] and st.session_state["input_text"] not in st.session_state["starting_options"]:
            st.session_state["starting_options"].append(st.session_state["input_text"])
            st.session_state["input"] = ""

    if "options_max" not in st.session_state:
        st.session_state["options_max"] = 10

    if "starting_options" not in st.session_state:
        st.session_state["starting_options"] = ["Start of employment", "Working hours", "Responsibilities", "Short-time work", "Remuneration", "Travel expenses", "Expenses"]

    if "clauses_only" not in st.session_state:
        st.session_state["clauses_only"] = []
        
    if "scanned" not in st.session_state:
        st.session_state["scanned"] = False


    with st.sidebar:
        page = option_menu(
            None,
            ["Home", "Contact"],
            icons=[
                "house",
                "bar-chart-line",
                "file-slides",
                "app-indicator",
                "person lines fill",
            ],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#262730"},
                "icon": {"color": "#FF2EFE", "font-size": "25px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#666666",
                },
                "nav-link-selected": {"background-color": "#080000"},
            },
        )

    if page == "Home":
        topic = option_menu(
            None,
            ["Check contract"],
            icons=["book"],
            menu_icon="list",
            default_index=0,
            styles={
                "icon": {"color": "#FF2EFE", "font-size": "20px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#666666",
                },
                "nav-link-selected": {"background-color": "#080000"},
            },
            orientation="horizontal",
        )

        if topic == "Check contract":
            with st.container():
                st.subheader("Add a preference")
                st.session_state["input_text"] = st.text_input("", "", key="input")
                if len(st.session_state["input_text"])>6:
                    st.button('Submit preference',key='ans',on_click=submit_result)
                options = st.multiselect(
                    '',
                    st.session_state["starting_options"],
                    st.session_state["starting_options"])
                with st.form("invalid_clauses"):
                    field_names = []
                    uploaded_file = st.file_uploader(
                        "##### Choose a work contract", accept_multiple_files=False, type=["pdf"]
                    )
                    if uploaded_file is not None:
                        bytes_data = uploaded_file.read()
                        my_string = base64.b64encode(uploaded_file.getbuffer())

                    st.session_state["scanned"] = st.checkbox('###### Use scanned documents')
                    english_var = st.checkbox('###### Translate to English')

                    if st.form_submit_button(label="Get contract summary"):
                        st.write("### Summary")
                        try:
                            if st.session_state["scanned"]:
                                st.session_state["doc_text"] = get_OCR_text(uploaded_file.name, my_string)
                            else:
                                st.session_state["doc_text"] = get_digiPDF_text(uploaded_file.name, my_string)
                            summary_text = get_contract_summary(st.session_state["doc_text"], english_var)
                            for chunk in summary_text:
                                st.write(chunk)         
                        except:
                            st.write("There is a problem with the server.")

        
        if page == "Contact":
            with st.form("form1", clear_on_submit=True):
                st.header("Contact Us")
                name = st.text_input("Name")
                email = st.text_input("Email")
                message = st.text_area("Message")
                submit_button = st.form_submit_button(label="Submit")
                if submit_button:
                    st.write("Thank you for your message!")        
        
        hide_streamlit_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    .stDeployButton {display:none;}
                    footer {visibility: hidden;}
                    </style>
                    """
        # MainMenu {visibility: hidden;}
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)
