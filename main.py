from app import plot_settings
import streamlit as st

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

if 'step' not in st.session_state:
    st.session_state['step'] = 0

step = st.session_state['step']
if step == 0:
    plot_settings.main_page_load_data() 
elif step == 1:
    plot_settings.bar_graph_plot() 
elif step == 2:
    plot_settings.bar_multiplot_graph()
elif step == 3:
    plot_settings.plot_cinetic_graph()
elif step == 4:
    plot_settings.custom_graph_col()

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)