
# conda activate cenv311
# streamlit run app.py
# if packages updated run "pip freeze > requirements.txt "
# # If not installed, tar.gz file install from GITHUB: pip install https://github.com/abelembaye/drawable_package/raw/master/streamlit-drawable-canvas-0.9.3.10.tar.gz  # just try to see the URL of the .tar.gz file as outsider and add /raw/ before the branch name, tricky
import hmac
import streamlit as st
# from helper_fns import check_password
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("Econ 21003: Online Activity")

if "course" not in st.session_state:
    st.session_state.course = None

if "username" not in st.session_state:
    st.session_state.username = None

if "wkd" not in st.session_state:
    st.session_state.wkd = None

COURSES = [None, "Econ21003"]  # , "Econ3333"]


# if not check_password():
#     st.stop()

def login():
    st.header("Log in")
    # course is take from this selection; course can be replaced by password
    course = st.selectbox("Choose your Course", COURSES)
    lastname = st.text_input("Enter your last name")
    wkd = st.text_input(
        r"Please enter your working directory so that your work is saved and uploaded when you comeback to the same assessment. In my PC with windows OS, on of my folders is (change this to yours!), C:\\Users\\myusername\\Documents")
    if st.button("Log in"):
        st.session_state.course = course
        st.session_state.username = lastname  # "lastname"
        st.session_state.wkd = wkd
        # st.session_state.wkd = ''
        # st.session_state.wkd = "C:/Users/aembaye/Documents"

        st.rerun()


def logout():
    st.session_state.course = None
    st.session_state.username = None
    st.rerun()


course = st.session_state.course

# logout() function as a page
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

# this is just an example of page outside of folder
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

act01 = st.Page(
    "Econ21003/act01.py",
    title="Activity 01: Comp Adv",
    icon=":material/healing:",
)

# quiz_02 = st.Page(
#     "Econ21003/quiz_02.py", title="Quiz 02", icon=":material/handyman:"
# )

act03_GDP = st.Page(
    "Econ21003/act03_GDP.py",
    title="Activity 03: GDP",
    icon=":material/healing:",
    # default=(course == "Econ21003"),
)

act04_testcorrections = st.Page(
    "Econ21003/act04_testcorrect.py",  # exactly as it is in the folder Econ 21003
    # Test Corrections Assignment",  # This is what apears to the user
    title="Activity 04: Unemployment",
    icon=":material/healing:",
    default=(course == "Econ21003"),
)

account_pages = [logout_page, settings]

Econ21003_pages = [act01, act03_GDP, act04_testcorrections]  # , quiz_02]
# the list here must be unique than the above
# Econ3333_pages = [quiz_01x, quiz_02x]


# st.title("Econ 21003: Online Activity")

st.logo("images/horizontal_blue.png",  icon_image="images/icon_blue.png")

page_dict = {}

if st.session_state.course in ["Econ21003"]:  # ["Requester", "Admin"]
    page_dict["Econ21003"] = Econ21003_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)

else:
    pg = st.navigation([st.Page(login)])

pg.run()
