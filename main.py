from app.bar_plot import main_page_load_data, bar_graph_plot, bar_multiplot_graph, plot_cinetic_graph, menu_bar, custom_graph_col
import streamlit as st

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

#define session state 
if 'step' not in st.session_state:
    st.session_state['step'] = 0
    
step = st.session_state['step']    
if step != 0:
    menu_bar()

st.title(":bar_chart: Gene PCR graph generator")
st.markdown("##")

# st.write( st.session_state)

step = st.session_state['step']
if step == 0:
    main_page_load_data() 
elif step == 1:
    bar_graph_plot() 
elif step == 2:
    bar_multiplot_graph()
elif step == 3:
    plot_cinetic_graph()
elif step == 4:
    custom_graph_col()
    



# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)