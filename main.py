from app import bar_plot
import streamlit as st

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

if 'step' not in st.session_state:
    st.session_state['step'] = 0

step = st.session_state['step']
if step == 0:
    bar_plot.main_page_load_data() 
elif step == 1:
    bar_plot.bar_graph_plot() 
elif step == 2:
    bar_plot.bar_multiplot_graph()
elif step == 3:
    bar_plot.plot_cinetic_graph()
elif step == 4:
    bar_plot.custom_graph_col()

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# import streamlit as st

# if __name__ == '__main__':
#     st.header("Hello world")