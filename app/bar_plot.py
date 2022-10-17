import pandas as pd  
import plotly.express as px  
import streamlit as st   
import tkinter as ttk
from tkinter import filedialog
from streamlit_option_menu import option_menu
 
# bar de navigation
def menu_bar():
    menu = option_menu(
        menu_title=None,
        options=['Home','Single plot','Multiple plots','Cinetic plot','Custom plot'],
        # icons='house',
        menu_icon='cast',
        default_index=st.session_state['step'],
        orientation='horizontal'
    )
    if menu == 'Home':
        st.session_state['step'] = 0
    if menu == 'Single plot':
        st.session_state['step'] = 1
    if menu == 'Multiple plots':
        st.session_state['step'] = 2
    if menu == 'Cinetic plot':
        st.session_state['step'] = 3
    if menu == 'Custom plot':
        st.session_state['step'] = 4


# Page d'accueil + instructions
def main_page_load_data() -> None:  
    main_container,espace,description_container = st.columns([2,0.5,2]) 
    with main_container: 
        st.header('Choose your source file ')
        st.button('Select source', on_click=choose_file)   

        if 'path_load' in st.session_state:
            st.text(st.session_state['path_load'])
        
        graph_choose = st.radio("Plot graph :", ['One plot','Multiple plot','Cinetic plot', 'Custom plot'],horizontal=True)
        st.session_state['graph_choose'] = graph_choose
        if 'error' in st.session_state:
            st.text('Error : file extension or colunm in your file is missing.\nChoose another file or type of plot please. \nIf an error appends again, contact your admin')
        if 'excel_path' in st.session_state:
            st.button('Confirm', on_click=load_data_frame)

    with description_container:
        st.header('Source file - must have :')
        st.text("Your file has to be an '.xlsx' (excel file)")
        st.text('If you choose one plot-multiple plot, the source file has to have :\n - Gene, condition, QRm')
        st.text('If you choose Cinetic plot, your source file has to have : \n -Probe, Condition, Time ')



# Choose file or directory with tkinter
def choose_file(case='file'):   
    root = ttk.Tk()
    root.withdraw() 
    root.wm_attributes('-topmost', 1)  
    if case == 'file':
        path_file = filedialog.askopenfilename(master=root)
        st.session_state['path_load'] = (f"Check path and file name of your file : \n {path_file}")
        st.session_state['excel_path'] = path_file
        if 'error' in st.session_state:
            del st.session_state['error'] 
    elif case == 'dir':        
        dirname_plot = filedialog.askdirectory(master=root) 
        st.session_state['dirname_plot'] = dirname_plot


# load df with pandas, must be an excel file and check condition for the type of plot
def load_data_frame():
    try:        
        df = pd.read_excel(st.session_state['excel_path'])
        if st.session_state['graph_choose'] in ['One plot', 'Multiple plot']: 
            df[['Condition','Gene','QRm']] 
        elif st.session_state['graph_choose'] == 'Cinetic plot': 
            df[['Probe','Condition','Time']]          
    except KeyError:
        st.session_state['error'] = True
    else:
        st.session_state['df'] = df
        if st.session_state['graph_choose'] == 'One plot':
            st.session_state['step'] = 1
        elif st.session_state['graph_choose'] == 'Multiple plot':
            st.session_state['step'] = 2
        elif st.session_state['graph_choose'] == 'Cinetic plot':
            st.session_state['step'] = 3
        elif st.session_state['graph_choose'] == 'Custom plot':
            st.session_state['step'] = 4


# Custumize one simple bar plot
def bar_graph_plot():     
    # ---- SIDEBAR ---- 
    df_selection = sidebar_settings('Gene','Condition')

     # ---- MAINPAGE ----
    main_container = st.container()
    with main_container:   
        left_column, right_column  = st.columns([1,2])
        
        left_column.text("Settings :")
        st.session_state['title_file'] = left_column.text_input(label='Enter title of your graph :', value='Title', placeholder='Type your title of your graph')        
        st.session_state['name_file'] = left_column.text_input(label='Enter the graph name of your file :', value='File name', placeholder='Type your file name of your graph')
        
        left_column.text(f"Place to save your graph : ")        
        if 'dirname_plot' in st.session_state:
            left_column.text(f"Directory chose : \n{st.session_state['dirname_plot']}") 

        left_column.button(label='Choose directory', on_click=lambda: choose_file('dir')) 

        graph_error = left_column.radio("Error y :", ['QRe',None],horizontal=True, key='te')

        option_dic = {
            None : 'Simple',
            'group' : 'Group'
        }
        st.session_state['bar_type'] = left_column.radio(label="Type of bar chart:", options=[None,'group'],format_func=lambda x: option_dic.get(x),horizontal=True) 

        left_column.button(label='Download Graph png', on_click=generate_png)

        #-----[BAR CHART] ------
        fig_bar_plot = px.bar(
            df_selection,
            x="Condition",
            y='QRm',
            color='Gene',
            orientation="v",  
            error_y=graph_error,
            title=st.session_state['title_file'], 
            template=st.session_state['template'],
            barmode=st.session_state['bar_type'],
            text_auto='.2s'
        ) 
        fig_bar_plot.update_layout(
            xaxis=(dict(showgrid=True))
        )

        right_column.plotly_chart(fig_bar_plot, use_container_width=True)
        st.session_state['fig_save'] = fig_bar_plot
    
    st.button('Return', on_click=step_beginning)
    


def generate_png(): 
    fig = st.session_state['fig_save']
    # if 'save_settings'in st.session_state:
    #     settings = st.session_state['save_settings']
    #     if settings == 'multiple':
    #         pass
    #     elif settings == 'one':
    #         pass
    # # st.write('Ne marche pas')
    fig.write_image("test_graph.png") 


def bar_multiplot_graph():
    #-----SIDEBAR-----
    df_selection = sidebar_settings('Gene','Condition')
    
     # ---- MAINPAGE ----
    main_container = st.container()
    with main_container:   
        left_column, right_column  = st.columns([1,2])
        
        left_column.text("Settings :")
        st.session_state['title_file'] = left_column.text_input(label='Enter title of your graph :', value='Title', placeholder='Type your title of your graph')
        #sert a rien pour l'instant

        st.session_state['name_file'] = left_column.text_input(label='Enter the graph name of your file :', value='File name', placeholder='Type your file name of your graph')
        left_column.text(f"Place to save your graph : ")        
        if 'dirname_plot' in st.session_state:
            left_column.text(f"Directory chose : \n{st.session_state['dirname_plot']}")        
        left_column.button(label='Choose directory', on_click=lambda: choose_file('dir'))

        graph_error = left_column.radio("Error y :", ['QRe',None],horizontal=True, key='te')
        option_dic = {
            'one' : 'All gene in one file',
            'multiple' : 'Each gene in separete files'
        } 
        save_settings = left_column.radio("Save settings :", ['one','multiple'], format_func=lambda x: option_dic.get(x),horizontal=True, key=22)
        st.session_state['save_settings']= save_settings
        left_column.button(label='Download Graph png', on_click=generate_png)

        try:
            #-----MULTIBAR CHARTS-----
            fig_multiple_graph = px.bar(
                df_selection, 
                x='Condition', 
                y='QRm', 
                error_y=graph_error,
                title=st.session_state['title_file'], 
                color='Condition', 
                facet_col='Gene', 
                facet_col_wrap=4,
                template=st.session_state['template']
                )
            fig_multiple_graph.update_layout(
                xaxis=(dict(showgrid=True))
            )
            right_column.plotly_chart(fig_multiple_graph, use_container_width=False)
            st.session_state['fig_save'] = fig_multiple_graph

        except:
            right_column.text('Select data to see your graphs') 
        
        if 'error' in st.session_state:
            left_column.text(st.session_state['error'])

    st.button('Return', on_click=step_beginning)


def step_beginning():
    st.session_state['step'] = 0

def plot_cinetic_graph():
    #-----SIDEBAR-----
    df_selection = sidebar_settings('Probe','Condition')
    
     # ---- MAINPAGE ----
    main_container = st.container()
    with main_container:   
        left_column, right_column  = st.columns([1,2])
        
        left_column.text("Settings :")
        # st.session_state['title_file'] = left_column.text_input(label='Enter title of your graph :', value='Title', placeholder='Type your title of your graph')
        left_column.text("Your file has to have this column : \n-Probe\n-Condition\n-Time")
       
        try:
            title = df_selection['Probe'].unique()[0]
            fig = px.line(
                df_selection,
                x='Time',
                y='relative_mean',
                color='Condition', 
                title=title,
                template=st.session_state['template'],
                )
            fig.update_layout(
                    xaxis=(dict(showgrid=True))
                )
            right_column.plotly_chart(fig, use_container_width=False)
            st.session_state['fig_save'] = fig
        except:
            right_column.text('Select data to see your graphs') 
        
        
    st.button('Return', on_click=step_beginning)



def sidebar_settings(select1,select2)-> pd.DataFrame:
    df = st.session_state['df']
    # ---- SIDEBAR ----
    step = st.session_state['step']

    st.sidebar.header("Please Filter Here:")
    sidebar_container = st.sidebar.container()
     
         
    if (step == 1 and ('bar_type' not in st.session_state or(st.session_state['bar_type'] == None))) or (step == 3):   
        selected_gene = st.sidebar.selectbox(
            f"Select the {select1}:",
            options=df[select1].unique(),
            )
    else:
        all_gene = st.sidebar.checkbox("Select all", key=1)
        if all_gene:
            selected_gene = sidebar_container.multiselect(
                f"Select One or more {select1}:",        
                options=df[select1].unique(),
                default=df[select1].unique()[:]
                )
        else:
            selected_gene = sidebar_container.multiselect(
                f"Select One or more {select1}:",        
                options=df[select1].unique()
                )       

    sidebar_container = st.sidebar.container()
    all_condition = st.sidebar.checkbox("Select all", key=2)
    if all_condition:
        selected_condition_type = sidebar_container.multiselect(
        f"Select the {select2}:",
        options=df[select2].unique(),
        default=df[select2].unique()[:],
        )
    else:
        selected_condition_type = sidebar_container.multiselect(
        f"Select the {select2}:",
        options=df[select2].unique(),
        )   
        
    template_options = ['ggplot2', 'seaborn', 'simple_white', 'plotly',
         'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
         'ygridoff', 'gridon', 'none']  
    sidebar_container = st.sidebar.container() 
    selected_template = sidebar_container.selectbox(
        "Select the template:",
        options=template_options,
    )
    st.session_state['template'] = selected_template
    
    df_selection = df.query(f"{select1} == @selected_gene and {select2} == @selected_condition_type")
    return df_selection



def custom_graph_col():
    #-----SIDEBAR-----    
    df = st.session_state['df']

    st.sidebar.header("Please Filter Here:")          
    selected_col_x = st.sidebar.selectbox(
        f"Select the column x:",
        options=df.columns,
        key=1
        )
    selected_col_y = st.sidebar.selectbox(
        f"Select the column y:",
        options=df.columns,
        key=2
        ) 
    selected_col_color = st.sidebar.selectbox(
        f"Select the color:",
        options=df.columns,
        key=3
        )
        
    template_options = ['ggplot2', 'seaborn', 'simple_white', 'plotly','plotly_white', 'plotly_dark',
        'presentation', 'xgridoff','ygridoff', 'gridon', 'none']   
    selected_template = st.sidebar.selectbox(
        "Select the template:",
        options=template_options,
    )
    st.session_state['template'] = selected_template
     
    # ---- MAINPAGE ----
    main_container = st.container()
    with main_container:   
        left_column, right_column  = st.columns([1,2])
        
        left_column.text("Settings :")
        st.session_state['title_file'] = left_column.text_input(label='Enter title of your graph :', value='Title', placeholder='Type your title of your graph')
        graph_choose = left_column.radio("Plot graph :", ['Bar chart','Line chart'],horizontal=True)

        try:
            #-----MULTIBAR CHARTS-----
            if graph_choose == 'Bar chart':
                fig_multiple_graph = px.bar(
                    df, 
                    x=selected_col_x, 
                    y=selected_col_y, 
                    title=st.session_state['title_file'], 
                    color=selected_col_color,  
                    template=st.session_state['template']
                    )
            else:
                fig_multiple_graph = px.line(
                    df, 
                    x=selected_col_x, 
                    y=selected_col_y, 
                    title=st.session_state['title_file'], 
                    color=selected_col_color,  
                    template=st.session_state['template']
                    )

            fig_multiple_graph.update_layout(
                xaxis=(dict(showgrid=True))
            )
            right_column.plotly_chart(fig_multiple_graph, use_container_width=False)
            st.session_state['fig_save'] = fig_multiple_graph

        except:
            right_column.text('Select data to see your graphs')          

        st.button('Return', on_click=step_beginning)
       