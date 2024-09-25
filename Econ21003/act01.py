import streamlit as st
import pandas as pd
import numpy as np
import json
import sys
import os
import random
from PIL import Image, UnidentifiedImageError
import io
from io import BytesIO
import base64
from datetime import date, datetime
import pdfkit
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
import time
from time import sleep
from sqlalchemy.sql import text
import sqlite3
import sqlalchemy.exc
from collections import OrderedDict
from helper_fns import start_assessment, next_question, previous_question, finish_assessment, serialize_data, make_ss_user_inputs, make_html_template

# define things that are unique to the assignment/activity
pagetitle = pageheader = "Activity 1"
act_name = "act01"
questions_jsonfile = 'question_set4' + act_name + '.json'
dbtable_file = "db_" + act_name + ".json"
workingdir = st.session_state.wkd

# Define the due date (year, month, day)
# due_date = datetime(2024, 8, 31)
due_date = datetime(2024, 8, 30)

# Get the current date
current_date = datetime.now()

# Check if the due date has passed
if current_date > due_date:
    st.error("Past due.")
else:
    # Ensure the working directory exists
    if not os.path.exists(workingdir):
        os.makedirs(workingdir)

    # Construct the full path to the database file
    full_path_db = os.path.join(workingdir, dbtable_file)
    st.write(f"Your work is saved in: {full_path_db}")

    # Load the questions from the JSON file
    try:
        with open(questions_jsonfile, 'r') as file:
            questions = json.load(file)
    except FileNotFoundError:
        st.error(f"Questions file {questions_jsonfile} not found.")
        questions = []
    except Exception as e:
        st.error(f"An error occurred while loading questions: {e}")
        questions = []

    # Load the default values from the database file
    try:
        with open(full_path_db, "r") as json_file:
            default_vals = json.load(json_file)
    except FileNotFoundError:
        st.warning(
            f"Database file {full_path_db} not found. Setting default values to an empty dictionary.")
        default_vals = {}
    except Exception as e:
        st.error(f"An error occurred while loading default values: {e}")
        default_vals = {}

    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = {}
    if 'inputs4template' not in st.session_state:
        st.session_state.inputs4template = {}

    # Initialize session state variables
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = -1
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'quiz_finished' not in st.session_state:
        st.session_state.quiz_finished = False

    # Display the start button at the top
    if not st.session_state.quiz_started:
        st.button("Start the Assessement", on_click=start_assessment)

    if st.session_state.quiz_started:
        make_ss_user_inputs(questions, default_vals)

        col1, col2, col3 = st.columns([2, 8, 2])  # Adjust the ratio as needed

        if st.session_state.current_question_index > 0:
            with col1:
                st.button("Previous", on_click=previous_question)

        if st.session_state.current_question_index < len(questions) - 1:
            with col3:
                st.button("Next", on_click=next_question)
        else:
            with col3:
                st.button("Finish", on_click=lambda: (finish_assessment(),
                                                      setattr(st.session_state, 'quiz_finished', True)))

    # Display "save your work" and "Generate PDF" buttons only after the quiz is finished
    if st.session_state.quiz_finished:
        # Serialize user_inputs excluding or converting non-serializable data
        serializable_user_inputs = serialize_data(st.session_state.user_inputs)

        # save user entry in .json file
        save_button = st.button(label="save your work", key="save_button")
        if save_button:
            with open(full_path_db, "w") as json_file:
                json.dump(serializable_user_inputs, json_file)
                st.write(
                    f"User input saved as .json file in the file full path: {full_path_db} or {json_file}")

        submit = st.button(
            "Generate PDF", key="generate_button")

        # generate template.html with rendered user_inputs
        template = make_html_template(questions)

        if submit:
            html = template

            local_wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            is_local = os.path.exists(local_wkhtmltopdf_path)

            if is_local:
                config = pdfkit.configuration(
                    wkhtmltopdf=local_wkhtmltopdf_path)
                pdf = pdfkit.from_string(html, configuration=config)
            else:
                pdf = pdfkit.from_string(html, False)

            st.success(
                "🎉 Your PDF file has been generated! Download it below and submit it in gradescope!")

            st.download_button(
                "⬇️ Download pdf",
                data=pdf,
                file_name=f"{st.session_state.username}_{act_name}.pdf",
                mime="application/octet-stream",
            )
