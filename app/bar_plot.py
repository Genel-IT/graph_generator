import os
import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
from pathlib import Path
from tkinter import filedialog
from math import ceil
import tkinter as tk

# Home page with user instructions 
def main_page_load_data():  
    st.title(":bar_chart: Gene PCR graph generator")
    st.markdown("##")
    main_container,space,description_container = st.columns([2,0.5,2])
        
    with main_container: 
        st.header('Select your source file ')        
        excel_file = st.file_uploader('Select a excel or csv file', type=['xlsx','csv'], accept_multiple_files=False)
        if excel_file != None:
            st.session_state['excel_path'] = excel_file
                        
        st.info("Your file has to be an '.xlsx' or '.csv' (excel file)") 
        
        graph_choose = st.radio("Choose your way to generate your graph :", ['One plot','Multiple plot','Cinetic plot', 'Custom plot'],horizontal=True)
        st.session_state['graph_choose'] = graph_choose
        if 'error' in st.session_state:
            st.error('Error : Colunm in your file is missing.\nChoose another file or type of plot please. \nIf an error appends again, contact your admin')
        
        if excel_file != None:  
            st.button('Confirm', on_click=load_data_frame)

    with description_container:
        st.header('Source file - must have :') 
        st.text('If you choose one plot or multiple plot, the source file has to have :\n - Gene, Condition, QRm')
        st.text('If you choose Cinetic plot, your source file has to have : \n -Probe, Condition, Time ')

# Custumize one bar plot (bar group or no)
def bar_graph_plot():
    # ---- SIDEBAR ---- 
    df_selection = sidebar_settings('Gene','Condition') 
    
    main_container = st.container()
    with main_container:   
        left_column, right_column  = st.columns([1,3])        
        
        main_setting_options(left_column,"simple_bar")        
         
        #-----[BAR CHART] ------
        text_auto = False if len(st.session_state['selected_gene']) < 11 else ".2s"
        # try:
        fig_bar_plot = px.bar(
            df_selection,
            x="Condition",
            y='QRm',
            color='Gene',
            orientation="v",  
            error_y=st.session_state['graph_error'],
            title=st.session_state['title_file'], 
            template=st.session_state['template'],
            barmode=st.session_state['bar_type'],  
            text_auto=text_auto,
            labels={"QRm":st.session_state['y_label'],
                    "Condition": st.session_state['x_label'],
                    },
            width=1000,
            height=500
        )            
        size_font = st.session_state['size_font']
        if len(st.session_state['selected_gene']) < 11:
            add_label_and_test_stat(fig_bar_plot, df_selection)
            
        if 'legend_title' not in st.session_state:
            st.session_state['legend_title'] = 'Condition'
        fig_bar_plot.update_layout(xaxis=(dict(showgrid=True)), showlegend=True,legend_title=st.session_state['legend_title'], legend=dict(font=dict(size=size_font)))
        fig_bar_plot.update_xaxes(tickfont_size=size_font, title_font_size=size_font)
        fig_bar_plot.update_yaxes(tickfont_size=size_font, title_font_size=size_font)
        right_column.plotly_chart(fig_bar_plot, use_container_width=True)
        st.session_state['fig_save'] = fig_bar_plot
        # except Exception as e:
        #     right_column.text(e) 
            # right_column.text('Select data to see your graphs') 

# Custumize and generated multiplot in one or multiple files
def bar_multiplot_graph():
    #-----SIDEBAR-----
    df_selection = sidebar_settings('Gene','Condition')

    main_container = st.container()
    with main_container:   
        left_column, right_column  = st.columns([1,3])
        
        main_setting_options(left_column) 
        
        st.session_state['text_auto'] = False if len(st.session_state['selected_gene']) < 13 else ".2s"
        size_font = st.session_state['size_font']        
        m = ceil(len(st.session_state['selected_gene'])/4)
        height = 350*m if m >1 else 500
        try:
            #-----MULTIBAR CHARTS-----
            fig_multiple_graph = px.bar(
                df_selection, 
                x='Condition', 
                y='QRm', 
                error_y=st.session_state['graph_error'],
                title=st.session_state['title_file'], 
                color='Condition', 
                facet_col='Gene', 
                facet_col_wrap=4, 
                template=st.session_state['template'], 
                text_auto=st.session_state['text_auto'],
                labels={"QRm":st.session_state['y_label'],
                        "Condition": st.session_state['x_label'],
                        },
                width=1400,
                height=height
                )
            
            if len(st.session_state['selected_gene']) < 13:
                add_label_and_test_stat(fig_multiple_graph, df_selection) 
                
            if 'legend_title' not in st.session_state:
                st.session_state['legend_title'] = 'Condition'
            fig_multiple_graph.update_layout(xaxis=(dict(showgrid=True)), showlegend=True,legend_title=st.session_state['legend_title'], legend=dict(font=dict(size=size_font)))
            fig_multiple_graph.update_xaxes(tickfont_size=size_font, title_font_size=size_font)
            fig_multiple_graph.update_yaxes(tickfont_size=size_font, title_font_size=size_font)
            
            right_column.plotly_chart(fig_multiple_graph, use_container_width=True)
            
            st.session_state['fig_save'] = fig_multiple_graph
        except Exception as e:
            # right_column.text(e) 
            right_column.text('Select data to see your graphs') 

# Custumize and generated cinetic plot in one file
def plot_cinetic_graph():
    #-----SIDEBAR-----
    df_selection = sidebar_settings('Probe','Condition')

    main_container = st.container()
    with main_container:   
        left_column, right_column  = st.columns([1,2])

        left_column.subheader("Settings :")
        st.session_state['title_file'] = left_column.text_input(label='Enter title of your graph :', value='Title', placeholder='Type your title of your graph')

        setting_save_plot(left_column)  
                
        try: 
            fig = px.line(
                df_selection,
                x='Time',
                y='relative_mean',
                color='Condition', 
                title=st.session_state['title_file'], 
                template=st.session_state['template'],
                )
            
            fig.update_layout(xaxis=(dict(showgrid=True)))
            right_column.plotly_chart(fig, use_container_width=False)            
            st.session_state['fig_save'] = fig
        except Exception:
            right_column.text('Select data to see your graphs') 

# Custumize and generated a graph with custom column in one file
def custom_graph_col():
    #-----SIDEBAR-----    
    df = st.session_state['df']

    st.sidebar.header("Please Filter Here:")
    selected_col_x = st.sidebar.selectbox("Select the column x:", options=df.columns, key=1)         

    sidebar_container = st.sidebar.container()
    if all_x := st.sidebar.checkbox("Select all x"):
        selected_x = sidebar_container.multiselect(
            f"Select One or more {selected_col_x}:",        
            options=df[selected_col_x].unique(),
            default=df[selected_col_x].unique()[:]
            )
    else:
        selected_x = sidebar_container.multiselect(
            f"Select One or more {selected_col_x}:",        
            options=df[selected_col_x].unique()
            )   

    selected_col_y = st.sidebar.selectbox("Select the column y:", options=df.columns, key=2)     

    sidebar_container = st.sidebar.container()
    if all_x := st.sidebar.checkbox("Select all y"):
        selected_y = sidebar_container.multiselect(
            f"Select One or more {selected_col_y}:",        
            options=df[selected_col_y].unique(),
            default=df[selected_col_y].unique()[:],
            key=27
            )
    else:
        selected_y = sidebar_container.multiselect(
            f"Select One or more {selected_col_y}:",        
            options=df[selected_col_y].unique(),
            key=28)  

    selected_col_color = st.sidebar.selectbox("Select the color:", options=df.columns, key=3)

    df_selection = df.query(f"{selected_col_x} == {selected_x} and {selected_col_y} == {selected_y}") 

    template_options = ['ggplot2', 'seaborn', 'simple_white', 'plotly','plotly_white', 'plotly_dark',
        'presentation', 'xgridoff','ygridoff', 'gridon', 'none']
    selected_template = st.sidebar.selectbox(
        "Select the template:",
        options=template_options)
    
    st.session_state['template'] = selected_template

    return_home(sidebar_container._parent) 
    # ---- MAINPAGE ----
    main_container = st.container()
    with main_container:   
        left_column, right_column  = st.columns([1,2])

        left_column.subheader("Settings :")
        st.session_state['title_file'] = left_column.text_input(label='Enter title of your graph :', value='Title', placeholder='Type your title of your graph')
        graph_choose = left_column.radio("Plot graph :", ['Bar chart','Line chart'],horizontal=True)

        setting_save_plot(left_column)
 
        try:
            #-----MULTIBAR CHARTS-----
            if graph_choose == 'Bar chart':
                fig_multiple_graph = px.bar(
                    df_selection, 
                    x=selected_col_x, 
                    y=selected_col_y, 
                    title=st.session_state['title_file'], 
                    color=selected_col_color,  
                    template=st.session_state['template']
                    )
            else:
                fig_multiple_graph = px.line(
                    df_selection, 
                    x=selected_col_x, 
                    y=selected_col_y, 
                    title=st.session_state['title_file'], 
                    color=selected_col_color,  
                    template=st.session_state['template']
                    )
                
            fig_multiple_graph.update_layout(xaxis=(dict(showgrid=True)))
            right_column.plotly_chart(fig_multiple_graph, use_container_width=False)
            st.session_state['fig_save'] = fig_multiple_graph
        except Exception:
            right_column.text('Select data to see your graphs')       

# load df with pandas, must be an excel file and check condition for the type of plot
def load_data_frame():
    extension = Path(st.session_state['excel_path'].name).suffix
    try:  
        if extension == '.xlsx':      
            df = pd.read_excel(st.session_state['excel_path'])
        elif extension == '.csv':
            df = pd.read_csv(st.session_state['excel_path'])
            
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

# Main settings of graphs
def main_setting_options(container, graph_type=""):
    graph_settings_option(container) 
    
    if graph_type ==  'simple_bar':
        option_dic = {None : 'Simple','group' : 'Group'}         
        st.session_state['bar_type'] = container.radio(label="Type of bar chart:", options=[None,'group'],format_func=lambda x: option_dic.get(x),horizontal=True) 
    
    setting_test_stat(container)

    container.button('Refresh plot')

    setting_save_plot(container,number='one-plot')  

#balbal
def graph_settings_option(container):    
    container.subheader("Graph settings :")
    st.session_state['title_file'] = container.text_input(label='Enter the title of your graph :', value='my title', placeholder='Type your title of your graph')     
    st.session_state['x_label'] = container.text_input(label='Enter the X label of your graph :', value='Condition', placeholder='Type your label X of your graph')     
    st.session_state['y_label'] = container.text_input(label='Enter the Y label of your graph :', value='Expression Relative', placeholder='Type your label Y of your graph')     
    st.session_state['taille_legend'] = container.radio(label="Size axes and legend :", options=['small','medium', 'big'],horizontal=True) 

    if st.session_state['taille_legend'] == 'small':
        st.session_state['size_font'] = 12
    elif st.session_state['taille_legend'] == 'medium':
        st.session_state['size_font'] = 16
    elif st.session_state['taille_legend'] == 'big':
        st.session_state['size_font'] = 20
    
    dic_error_y = {'QRe':'Yes', None:'No'}
    st.session_state['graph_error'] = container.radio("Show the error bar y (QRe):", [None,'QRe'], format_func=lambda x: dic_error_y.get(x),horizontal=True, key='te')


def setting_test_stat(container):
    df = st.session_state['df_selection']
    st.session_state['test_stats'] = container.radio(label="Show statistic test :", options=['No','Yes +', 'Yes +/★'],horizontal=True) 
    if st.session_state['test_stats'] != 'No':
        st.session_state['col_test_stat_pos'] = container.selectbox("Choose the column for the test stats positive (+) :",options=df.columns,index=len(df.columns)-1) 
                
        if st.session_state['test_stats'] == 'Yes +/★':                                       
            st.session_state['col_test_stat_neg'] = container.selectbox("Choose the column for the test stats negative (★) : ",options=df.columns,index=len(df.columns)-1)   
        else:
            st.session_state['col_test_stat_neg'] = 'None'         
            
        if 'error_test_stat' in st.session_state and st.session_state['error_test_stat'] != '':
            container.error(st.session_state['error_test_stat'])

# Setting to save your plot(name, directory and info message)
def setting_save_plot(container:st.container,number=''):
    def choose_dir(): 
        root = tk.Tk()
        root.withdraw() 
        root.wm_attributes('-topmost', 1)  
        st.session_state['save_dir'] = filedialog.askdirectory(master = root) 
    
    container.markdown('---')
    container.subheader('Saving settings :')
    st.session_state['name_file'] = container.text_input(label='Enter a file name for your graph :', value='my file name', placeholder='file name')
    container.button('Select directory', on_click=choose_dir)
    if 'save_dir' not in st.session_state or st.session_state['save_dir'] == '':
        st.session_state['disabled'] = True
    else:
        st.session_state['disabled'] = False
        container.write(f"path : {st.session_state['save_dir']}") 
    # option desactivé - a voir si necessaire
    if number == 'multiple Wow': 
        option_dic = {
            'one' : 'All gene (one file) ',
            'multiple' : 'Each gene'
        } 
        st.write()
        save_settings = container.radio("Way to save graph :", ['one','multiple'], format_func=lambda x: option_dic.get(x),horizontal=True, key=22)
        container.write("The file name is used only when 'All gene' is selected. If you select 'Each gene' the title and file name will be the gene name")  
        st.session_state['save_settings']= save_settings      
    elif number == 'one-plot':
        container.button(label='Generare all genes (png)', on_click=lambda :generate_png(container, order='test'), disabled=st.session_state['disabled'])
         
    container.button(label='Generare Graph (png)', on_click=lambda :generate_png(container), disabled=st.session_state['disabled'])
    if 'plot_generate' in st.session_state:
        container.info(st.session_state['plot_generate']) 
   
                                          
def return_home(container):
    container.markdown('---')        
    if btn_home := container.button('Back home'):
        st.session_state['step'] = 0
        st.experimental_rerun()
    container.markdown('#')        
        
# Generate the graph into png
def generate_png(container, order=""):
    def create_dir(path): 
        if not os.path.exists(path):
            os.mkdir(path)
            return path
        else:
            n = 1
            while os.path.exists(f"{path}{n}"):
                n +=1
            os.mkdir(f"{path}{n}") 
            return (f"{path}{n}")
            
    # save plot into png in the directory  
    def save_image(fig_plot, name, multiple=False):  
        path = st.session_state['path_multiple_image'] if multiple else st.session_state['save_dir']         
        try: 
            fig_plot.write_image(f"{path}/{name}.png")
        except Exception:
            st.session_state['plot_generate'] = "Generation failed"
        else:
            if 'nb_plots_generated' not in st.session_state:
                st.session_state['nb_plots_generated'] = 1
            else:
                st.session_state['nb_plots_generated'] +=1
            st.session_state['plot_generate'] = f"Success : {st.session_state['nb_plots_generated']}  plot(s) generated ! \n Plot is here : {path}"
    
    if order == 'test':        
        df_selec = st.session_state['df_selection']        
        df = st.session_state['df']
        genes = df['Gene'].unique() 
        df = df.loc[df['Condition'].isin(df_selec['Condition'])]
               
        path = st.session_state['save_dir']
        path += "\images"
        st.session_state['path_multiple_image'] = create_dir(path=path)  
        
        for i in genes:            
            df_temp = df.loc[df['Gene'] == i]
            temp_fig = px.bar(
                df_temp,
                x="Condition",
                y='QRm',
                color='Gene',
                orientation="v",  
                error_y=st.session_state['graph_error'],
                title=i, 
                template=st.session_state['template'],
                barmode=st.session_state['bar_type'],   
                labels={"QRm":st.session_state['y_label'],
                        "Condition": st.session_state['x_label'],
                        }                                
                ) 
            add_label_and_test_stat(temp_fig,df[df['Gene'] == i])
            save_image(fig_plot=temp_fig, name=i, multiple=True)
                    
        
    #plot graph for each gene selected       
    elif  ('save_settings' in st.session_state) and (st.session_state['save_settings'] == 'multiple'):
        df = st.session_state['df_selection']        
        genes = df['Gene'].unique()        
        path = st.session_state['save_dir']
        path += "\images"
        st.session_state['path_multiple_image'] = create_dir(path=path) 
        
        for i in genes:
            temp_fig = px.bar(
                    df[df['Gene'] == i],
                    x="Condition",
                    y='QRm', 
                    color='Gene',
                    error_y=st.session_state['graph_error'],
                    title=i,
                    orientation="v",   
                    template=st.session_state['template'],                    
                ) 
            add_label_and_test_stat(temp_fig,df[df['Gene'] == i])
            save_image(fig_plot=temp_fig, name=i, multiple=True)
    #plot one graph
    else:
        if 'fig_save' not in st.session_state:
            st.session_state['plot_generate'] = 'No graph, no download'
            return

        fig = st.session_state['fig_save']
        if st.session_state['name_file'] != '' and ('save_dir' in st.session_state):
            name_file = st.session_state['name_file']            
            path = st.session_state['save_dir']
            
            if os.path.exists(f"{path}/{name_file}.png"): 
                st.session_state['plot_generate'] = 'A graph with the same name already exist, confirm for overwriting or cancel and change the file name'
                overwrite = container.button(label='Overwrite', on_click=lambda :save_image(fig_plot=fig, name=name_file))
                cancel = container.button(label='Cancel')                                  
                if cancel:
                    del overwrite
                    del cancel
                    return
            else:
                save_image(fig_plot=fig, name=name_file)    
        else:
            st.session_state['plot_generate'] = 'Missing file name'  

# Commum sidebar settings
def sidebar_settings(select1,select2) -> pd.DataFrame:
    df = st.session_state['df']
    # ---- SIDEBAR ----
    step = st.session_state['step']

    st.sidebar.header("Please Filter Here:")
    sidebar_container = st.sidebar.container()


    if step == 1 and ('bar_type' not in st.session_state or st.session_state['bar_type'] is None) or step == 3:   
        selected_gene = st.sidebar.selectbox(
            f"Select a {select1}:",
            options=df[select1].unique(),
            )
    elif all_gene := st.sidebar.checkbox("Select all", key=1):
        selected_gene = sidebar_container.multiselect(
            f"Select one or more {select1}:",        
            options=df[select1].unique(),
            default=df[select1].unique()[:]
            )
    else:
        selected_gene = sidebar_container.multiselect(
            f"Select one or more {select1}:",        
            options=df[select1].unique()
            )
    st.session_state['selected_gene'] = selected_gene 


    sidebar_container = st.sidebar.container()
    if all_condition := st.sidebar.checkbox("Select all", key=2):
        selected_condition_type = sidebar_container.multiselect(
        f"Select one or more {select2}:",
        options=df[select2].unique(),
        default=df[select2].unique()[:],
        )
    else:
        selected_condition_type = sidebar_container.multiselect(
        f"Select one or more {select2}:",
        options=df[select2].unique(),
        )
    st.session_state['selected_condition'] = selected_condition_type 

    template_options = ['ggplot2', 'seaborn', 'simple_white', 'plotly',
         'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
         'ygridoff', 'gridon', 'none']
    sidebar_container = st.sidebar.container()
    selected_template = sidebar_container.selectbox(
        "Select a template:",
        options=template_options,
    )
    st.session_state['template'] = selected_template

    df_selection = df.query(f"{select1} == @selected_gene and {select2} == @selected_condition_type")
    st.session_state['df_selection'] = df_selection    
     
    return_home(sidebar_container) 
    return df_selection


def add_label_and_test_stat(fig, df):   
    def get_params():
        n = len(st.session_state['selected_condition'])
        m = len(st.session_state['selected_gene']) 
        if m > 10:
            return 0,n,m
        dic = {0:0,1:1, 2:0.2,3:.3, 4:0.1, 5:0.15, 6:0.12, 7:0.12, 8:0.05,9:9,10:10}
        dic_temp_val = {
            0:0,
            1:1,
            2: [-dic[m], dic[m]],
            3: [-dic[m], 0, dic[m]],
            4: [-dic[m]*3, -dic[m], dic[m], dic[m]*3],
            5: [-dic[m]*2, -dic[m], 0, dic[m], dic[m]*2],
            6: [-0.34, -0.2, -0.08, 0.08, 0.2, 0.35], 
            7: [-dic[m]*3, -dic[m]*2, -dic[m], 0, dic[m], dic[m]*2, dic[m]*3],         
            8: [-0.35,-0.25,-0.15,-0.05,0.05,0.15,0.25,0.35],            
            9: [-0.35,-0.28,-0.18,-0.08,0,0.08,0.18,0.28,0.35],         
            10: [-0.37,-0.28,-0.2,-0.12,-0.04,0.04,0.12,0.2,0.28,0.37],            
            } 

        return dic_temp_val[m],n,m

    def annot_one_bar_simple(text,y_height, col_stats): 
        significance = pd.Series([3,2,1,0], pd.IntervalIndex.from_breaks([0,0.001,0.01,0.205,np.inf],closed = 'left'), name = 'Significance levels')
        col_stat = df[st.session_state[col_stats]].map(significance)        
        for k,(i,j,l) in enumerate(zip(QRe_tab,QRm_tab,col_stat)): 
            fig.add_annotation(
                text=text * l, font=dict(size=font_size),
                x=k, y=i + j + y_height, showarrow=False)
            

    def annot_one_bar_group(text,y_height,col_stats): 
        significance = pd.Series([3,2,1,0], pd.IntervalIndex.from_breaks([0,0.001,0.01,0.205,np.inf],closed = 'left'), name = 'Significance levels')
        col_stat = df[st.session_state[col_stats]].map(significance)
        tour = 0  
        x_col=0 
        dic_param,nb_col,_ = get_params()
        for i,j, k in zip(QRe_tab,QRm_tab, col_stat): 
            fig.add_annotation(
                text=text * k, font=dict(size=font_size),
                x=x_col + dic_param[tour], y=i + j + y_height, showarrow=False)
            x_col += 1            
            if nb_col == x_col:
                x_col = 0
                tour += 1

    def annot_multiple_bar(text,y_height, col_stats): 
                significance = pd.Series([3,2,1,0], pd.IntervalIndex.from_breaks([0,0.001,0.01,0.205,np.inf],closed = 'left'), name = 'Significance levels')
                col_stat = df[st.session_state[col_stats]].fillna(1).map(significance)
                _, nb_col, nb_gene = get_params()
                x_col=0
                col_graph = 1        
                n_row = ceil(nb_gene/4)  
                for i,j, x in zip(QRe_tab,QRm_tab, col_stat):       
                    fig.add_annotation(
                        text=text*x, font=dict(size=font_size-2),
                        x=x_col, y= i +j +y_height, showarrow=False,
                        row=n_row, col=col_graph)        
                    x_col += 1
                    if nb_col == x_col:
                        x_col = 0
                        col_graph += 1           
                        if col_graph > 4:
                            col_graph = 1
                            n_row -= 1
    
    def write_legend(fct_name_annot):
                if st.session_state['test_stats'] != 'No':   
                    try:                    
                        if st.session_state['test_stats'] == 'Yes +/★':
                            fct_name_annot(text="<b>★<b>", y_height=0.6,  col_stats="col_test_stat_neg")                      
                        fct_name_annot(text="<b>+<b>", y_height=0.4,  col_stats="col_test_stat_pos")         
                    except Exception:
                            st.session_state['error_test_stat'] = 'Choose column numeric please'  
                    else:   
                        legend = f"Statistical test : <br> + : {st.session_state['col_test_stat_pos']}<br>"
                        if st.session_state['test_stats'] == 'Yes +/★':
                            legend += f" ★ : {st.session_state['col_test_stat_neg']} <br>"
                        st.session_state['legend_title']  = f"{legend} <br>{st.session_state['x_label']}"
                else:
                    st.session_state['legend_title']  = st.session_state['x_label']     
                    
    font_size = st.session_state['size_font']
    # recuperer hauteur pour afficher au dessus des error_y si presente    
    QRm_tab = df['QRm'].copy()
    QRe_tab = df['QRe'].copy()
    if  st.session_state['graph_error'] != 'QRe':
        QRe_tab[:] = 0 

    # One plot - Group version
    if st.session_state['step'] == 1:
        if (len(st.session_state['selected_gene']) > 1) and (st.session_state['bar_type'] == 'group'): 
            dic_param,nb_col,_ = get_params()
            x_col = 0
            t = 0
            for k,(i,j) in enumerate(zip(QRe_tab,QRm_tab)):
                fig.add_annotation(text=round(j,2),font=dict(size=font_size),
                    x=x_col + dic_param[t],y=i + j + 0.2,showarrow=False)
                fig.add_annotation(text=f"{df['Nb_ech'].values[k]}",font=dict(size=font_size),
                    x=x_col + dic_param[t],y=0.15,showarrow=False)                
                x_col += 1
                if nb_col == x_col:
                    x_col = 0
                    t += 1

            write_legend(annot_one_bar_group)                       
    
        # One plot - Simple version 
        elif st.session_state['bar_type'] is None:
            for k,(i,j) in enumerate(zip(QRe_tab,QRm_tab)):
                fig.add_annotation(text=round(j,2), font=dict(size=font_size),
                    x = k, y = i + j + 0.2, showarrow=False) 
                fig.add_annotation( 
                    text=f"{df['Nb_ech'].values[k]}", font=dict(size=font_size),
                    x = k, y = 0.15, showarrow=False)
               
            write_legend(annot_one_bar_simple)                       
                 
    # Multiple Plot
    if st.session_state['step'] == 2:
        _,nb_col,nb_gene = get_params()
        x_col=0
        col_graph = 1        
        row = ceil(nb_gene/4) 
        for k,(i,j) in enumerate(zip(QRe_tab,QRm_tab)): 
            fig.add_annotation(
                text=round(j,2), font=dict(size=font_size),
                x=x_col, y=i + j + 0.2, showarrow=False,
                row=row, col=col_graph)  
            fig.add_annotation(
                text=str(df['Nb_ech'].values[k]), font=dict(size=font_size),
                x=x_col, y=0.15, showarrow=False,
                row=row, col=col_graph)               
            x_col += 1
            if nb_col == x_col:
                x_col = 0
                col_graph += 1 
                if col_graph > 4:
                    col_graph = 1
                    row -= 1     
        write_legend(annot_multiple_bar)