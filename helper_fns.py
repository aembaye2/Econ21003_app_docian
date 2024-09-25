
import streamlit as st
from PIL import Image, UnidentifiedImageError
import io
from io import BytesIO
import base64
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pandas as pd  # pip install pandas
import numpy as np  # pip install numpy
import seaborn as sns  # pip install seaborn
import matplotlib.pyplot as plt  # pip install matplotlib
from streamlit_drawable_canvas import st_canvas
import hmac


def process_canvas(default_drawing_data):
    canvas_width = 700
    canvas_height = 500
    # respectively, x label upper limit, y label upper limit, distance from left limit to the axes as % of canvas_width, distance from bottom to the x-axis
    xlim = 100  # 200 # can changed; and that is what matters which is seen by users
    ylim = 100  # 500
    # as percentage of canvas_width (.225 is from top of canvas to top of rectangle or ylim)
    bottom_margin = 75  # absolute in pixels
    left_margin = 84
    top_margin = 25
    right_margin = 35
    scaleFactors = [xlim, ylim, bottom_margin,
                    left_margin, top_margin, right_margin]

    # if 'saved_state' not in st.session_state or st.session_state.saved_state is None:
    #     # print('NEW SESSION')
    #     if os.path.exists("saved_state.json"):
    #         with open("saved_state.json", "r") as f:
    #             saved_state = json.load(f)
    #     else:
    #         saved_state = {}  # Initialize an empty state if the file doesn't exist
    #         with open("saved_state.json", "w") as f:
    #             json.dump(saved_state, f)  # Create the file
    #     st.session_state['saved_state'] = saved_state
    # else:
    #     # print('OLD SESSION')
    #     saved_state = st.session_state['saved_state']
    saved_state = None
    # bg_image = Image.open(buf)
    bg_image = None

    # Specify canvas parameters in application
    drawing_mode = st.sidebar.selectbox(
        "Drawing tool:", (
            "line",
            "freedraw",
            "coordinate",
            "curve",
            "singlearrowhead",
            "doublearrowhead",
            "text",
            #   "rect",  "point",  # "circle",
            # "polygon",
            "transform"
        )
    )

    stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)

    if drawing_mode == 'point':
        point_display_radius = st.sidebar.slider(
            "Point display radius: ", 1, 25, 3)
    stroke_color = st.sidebar.color_picker("Stroke color hex: ")
    # bg_color = st.sidebar.color_picker("Background color hex: ", "#eee")
    # bg_image = st.sidebar.file_uploader("Background image:", type=["png", "jpg"])

    realtime_update = st.sidebar.checkbox("Update in realtime", True)
    axes_and_labels = st.sidebar.checkbox("axes and labels?", False)
    # axes_and_labels = True

    # Create a canvas component
    canvas_result = st_canvas(
        # Fixed fill color with some opacity
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        # background_color=bg_color,
        # background_image=Image.open(bg_image) if bg_image else None,
        background_image=bg_image,
        update_streamlit=realtime_update,
        axes_and_labels=axes_and_labels,
        width=canvas_width,
        height=canvas_height,
        drawing_mode=drawing_mode,
        # text=label,  # Use the entered label as the text to be drawn
        point_display_radius=point_display_radius if drawing_mode == 'point' else 0,
        scaleFactors=scaleFactors,  # [80, 40],
        initial_drawing=saved_state,  # this the beginning jason data and drawings
        key="canvas",
    )
    # st.write("Canvas data:", canvas_result)

    # Do something interesting with the image data and paths
    # if canvas_result.image_data is not None:
    if canvas_result.image_data is not None:
        # Display the image data
        # to automatically display the image in the streamlit app (kind of duplicate canvas)
        # st.image(canvas_result.image_data)
        # Convert the image data to a PIL Image
        img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        # Save img to a BytesIO object for comparison
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        # # Convert img to a base64 encoded string
        base64_img = base64.b64encode(img_io.getvalue()).decode()
        upload2db = base64_img  # Create a download button for the image

        st.download_button(
            label="Download-canvas-image",
            # data=img_io,
            data=base64_img,
            file_name='image01.png',
            mime='image/png'
        )
        return upload2db

        # # Do something interesting with the JSON data
        # if canvas_result.json_data is not None:
        #     # need to convert obj to str because PyArrow
        #     objects = pd.json_normalize(canvas_result.json_data["objects"])
        #     for col in objects.select_dtypes(include=['object']).columns:
        #         objects[col] = objects[col].astype("str")
        #     st.dataframe(objects)


def process_image(default_image_data, question_key):
    new_upload = st.file_uploader(
        f"{question_key}", type=["png", "jpg", "jpeg"], label_visibility="hidden")

    if new_upload is None:
        if default_image_data is not None:
            try:
                # Decode the base64 string to bytes if it's not already bytes
                if isinstance(default_image_data, str):
                    default_image_data = base64.b64decode(default_image_data)
                default_image = Image.open(io.BytesIO(default_image_data))
                st.image(
                    default_image, caption="previous upload", width=100)
                buffered = io.BytesIO()
                default_image.save(buffered, format="PNG")
                image_base64 = base64.b64encode(
                    buffered.getvalue()).decode("utf-8")
                new_upload_data = buffered.getvalue()
            except Exception as e:
                # st.error(f"Failed to load default image: {e}")
                default_image, new_upload_data, image_base64 = None, None, None
        else:
            new_upload_data, image_base64 = None, None
    else:
        try:
            # open the uploaded object as image
            uploaded_image = Image.open(new_upload)
            # Specify new width and height
            new_width = 100
            # Calculate new height to maintain aspect ratio
            aspect_ratio = uploaded_image.height / uploaded_image.width
            new_height = int(new_width * aspect_ratio)

            # Resize the image
            resized_image = uploaded_image.resize((new_width, new_height))
            # display it to streamlit app or html
            st.image(uploaded_image, caption='', width=100)
            buffered = io.BytesIO()  # create a memory version of the image
            # eventhough the uploaded image was in other format, now it saves it as .PNG
            uploaded_image.save(buffered, format="PNG")
            new_upload_data = buffered.getvalue()
            image_base64 = base64.b64encode(
                buffered.getvalue()).decode("utf-8")
        except Exception as e:
            # st.error(f"Failed to process uploaded image: {e}")
            uploaded_image, new_upload_data, image_base64 = None, None, None

    # return new_upload_data, image_base64
    # first used for database and second is for directly putting to .html template and pdf conversion
    return new_upload_data, image_base64


def start_assessment():
    st.session_state.quiz_started = True
    st.session_state.current_question_index = 0


def next_question(n=6):
    if st.session_state.current_question_index < n - 1:
        st.session_state.current_question_index += 1


def previous_question():
    if st.session_state.current_question_index > 0:
        st.session_state.current_question_index -= 1


def finish_assessment():
    st.session_state.quiz_started = False
    st.session_state.current_question_index = -1
    st.write("Work finished! Thank you for participating!")


def base64_to_image(base64_string):
    # Decode the base64 string
    img_data = base64.b64decode(base64_string)

    # Convert the bytes data to an image
    try:
        img = Image.open(io.BytesIO(img_data))
        return img
    except UnidentifiedImageError as e:
        # print(f"Failed to identify image: {e}")
        return None

# def base64_to_image(base64_string):
#     # Ensure the input is a string
#     if not isinstance(base64_string, str):
#         base64_string = str(base64_string)

#     # Decode the base64 string
#     img_data = base64.b64decode(base64_string)

#     # Convert the decoded bytes to an image
#     img = Image.open(BytesIO(img_data))
#     return img


def serialize_data(data):
    serialized_data = {}
    for key, value in data.items():
        # Check if the value is bytes, if so, convert to base64 string for JSON serialization
        if isinstance(value, bytes):
            serialized_data[key] = base64.b64encode(value).decode('utf-8')
        else:
            serialized_data[key] = value
    return serialized_data


def make_ss_user_inputs(questions, default_vals):
    question = questions[st.session_state.current_question_index]
    question_key = f"q{st.session_state.current_question_index+1}"
    thequestion = f"Question {st.session_state.current_question_index+1}: {question['label']}"
    # Use st.radio to display options as radio buttons
    # st.write(thequestion)
    st.write(thequestion)
    if question["qtype"] == "mc_quest":
        previous_option_value = default_vals.get(question_key, "")
        # Initialize a variable to hold the index of the previously selected option
        previous_option_index = None  # Default to 0 or any other default index
        # Check if the previously selected option is in the current options list
        if previous_option_value in question["options"]:
            # Find the index of the previously selected option
            previous_option_index = question["options"].index(
                previous_option_value)
        st.session_state.user_inputs[question_key] = st.radio(
            label=thequestion, options=question["options"],  index=previous_option_index, label_visibility="hidden",  key=question_key)
    elif question["qtype"] == "float_num":
        st.session_state.user_inputs[question_key] = st.number_input(
            label=thequestion, min_value=None, value=float(default_vals.get(question_key, 0)),  label_visibility="hidden", key=question_key)
    elif question["qtype"] == "oneline_text":
        st.session_state.user_inputs[question_key] = st.text_input(
            label=thequestion, value=default_vals.get(question_key, ""),  label_visibility="hidden", key=question_key)
    elif question["qtype"] == "manyline_text":
        st.session_state.user_inputs[question_key] = st.text_area(label=thequestion,
                                                                  value=default_vals.get(question_key, ""), height=200, max_chars=600, label_visibility="hidden",  key=question_key)
    elif question["qtype"] == "upload_quest":
        default_image_data = default_vals.get(question_key, "")
        # st.write(default_image_data)
        st.session_state.user_inputs[question_key], st.session_state.inputs4template[question_key] = process_image(
            default_image_data, question_key)
    elif question["qtype"] == "drawing_quest":
        default_drawing_data = default_vals.get(question_key, "")
        st.session_state.user_inputs[question_key] = process_canvas(
            default_drawing_data)
        # Convert the default_value to an image and display it
        default_img = base64_to_image(default_drawing_data)
        if default_img:
            st.image(default_img, caption="Your previous drawing", width=150)


def make_html_template(questions):
    # Load HTML template
    env = Environment(loader=FileSystemLoader(
        "."), autoescape=select_autoescape())
    username = st.session_state.username
    template = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>Report</title>
    <style>
        .page-break {
            page-break-before: always;
        }
    </style>
    </head>
    <body>
    """

    template += f"""<h2 style='text-align: center;'>FULL NAME: {username}</h2> <br> <br>"""

    for index, (key, value) in enumerate(st.session_state.user_inputs.items()):
        qtype = questions[index]["qtype"] if index < len(
            questions) else "Unknown"
        question_label = questions[index]["label"] if index < len(
            questions) else "Label Unknown"
        question_number = index + 1  # Human-friendly question numbering
        if qtype == "mc_quest":
            template += f"""<h6> Q# {question_number}: {question_label}</h6><div style="width:800px; height:20px; padding:20px; text-align:left; border: 1px solid #787878">
        {value}
    </div>\n <br> <br>  """
        elif qtype == "float_num":
            template += f"""<h6> Q# {question_number}: {question_label}</h6><div style="width:50px; height:20px; padding:20px; text-align:left; border: 1px solid #787878">
        {value}
        </div>\n  <br> <br> """
        elif qtype == "oneline_text":
            template += f"""<h6> Q# {question_number}: {question_label}</h6><div style="width:700px; height:20px; padding:20px; text-align:left; border: 1px solid #787878">
        {value}
        </div>\n  <br> <br> """
        elif qtype == "manyline_text":
            template += f"""<h6> Q# {question_number}: {question_label}</h6><div style="width:800px; height:150px; padding:20px; text-align:left; border: 1px solid #787878">    {value}</div >\n  <br> <br> """
        elif qtype == "upload_quest":
            processed_value = st.session_state.inputs4template[f"q{index+1}"]
            template += f"""<h6> Q# {question_number}: {question_label}</h6><div style="width:500px; height:200px; padding:20px; text-align:center; border: 1px solid #787878">
        <img src="data:image/png;base64,{processed_value}" style="max-width:75%; max-height:75%; object-fit: contain;" />
        </div>\n  <br> <br>   """
        elif qtype == "drawing_quest":
            processed_value = value
            template += f"""<h6> Q# {question_number}: {question_label}</h6><div style="width:700px; height:350px; padding:20px; text-align:center; border: 1px solid #787878">
        <img src="data:image/png;base64, {processed_value}" style="max-width:75%; max-height:75%; object-fit: contain;" />
        </div>\n  <br> <br>   """
        else:
            # Handle other question types
            pass

    template += """
    </body>
    </html>
    """

    return template


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False
