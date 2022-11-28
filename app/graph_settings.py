import os
import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
from pathlib import Path
from tkinter import filedialog
from math import ceil
import tkinter as tk

# load df with pandas, must be an excel file and check condition for the type of plot
def load_data_frame_and_next_step():
    extension = Path(st.session_state['excel_file'].name).suffix
    try:  
        if extension == '.xlsx':      
            df = pd.read_excel(st.session_state['excel_file'])
        elif extension == '.csv':
            df = pd.read_csv(st.session_state['excel_file'])
            
        if st.session_state['graph_choose'] in [1,2]: 
            df[['Condition','Gene','QRm']] 
        elif st.session_state['graph_choose'] == 3: 
            df[['Probe','Condition','Time']]                          
    except KeyError:
        st.session_state['error'] = True
    else:
        st.session_state['df'] = df         
        st.session_state['step'] = st.session_state['graph_choose']  

# Main settings of graphs
def main_setting_options(container:st.container, graph_type:str):
    graph_settings_option(container, graph_type) 

    if graph_type in {None, 'group'}:
        option_dic = {None : 'Simple','group' : 'Group'}         
        st.session_state['bar_type'] = container.radio(label="Type of bar chart:", options=option_dic.keys(), format_func=lambda x: option_dic.get(x),horizontal=True) 

    if graph_type in {'group',None, 'multi_bar_plot'}:
        setting_test_stat(container)

    if graph_type == 'custom_plot':
        st.session_state['graph_choose']  = container.radio("Plot graph :", ['Bar chart','Line chart'],horizontal=True)

    container.button('Refresh plot')

    setting_save_plot(container,graph_type=graph_type)  

#Setting of the graph - basic 
def graph_settings_option(container, graph_type):    
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
        
    if graph_type in {'group',None}:
        dic_error_y = {'QRe':'Yes', None:'No'}
        st.session_state['graph_error'] = container.radio("Show the error bar y (QRe):", [None,'QRe'], format_func=lambda x: dic_error_y.get(x),horizontal=True, key='te')

# Show the setting for the statitical test
def setting_test_stat(container):
    df = st.session_state['df_selection']
    st.session_state['test_stats'] = container.radio(label="Show statistic test :", options=['No','Yes +', 'Yes +/★'],horizontal=True) 
    if st.session_state['test_stats'] != 'No':
        st.session_state['col_test_stat_pos'] = container.selectbox("Choose the column for the test stats positive (+) :",options=df.columns,index=len(df.columns)-1) 
                
        if st.session_state['test_stats'] == 'Yes +/★':                                       
            st.session_state['col_test_stat_neg'] = container.selectbox("Choose the column for the test stats negative (★) : ",options=df.columns,index=len(df.columns)-1)   
        else:
            st.session_state['col_test_stat_neg'] = 'None'         
            
        if st.session_state.get('error_test_stat',"") != '':
            container.error(st.session_state['error_test_stat'])

# Setting to save your plot(name, directory and info message)
def setting_save_plot(container:st.container,graph_type:str):
    def choose_dir(): 
        root = tk.Tk()
        root.withdraw() 
        root.wm_attributes('-topmost', 1)  
        st.session_state['save_dir'] = filedialog.askdirectory(master = root) 
    
    container.markdown('---')
    container.subheader('Saving settings :')
    st.session_state['name_file'] = container.text_input(label='Enter a file name for your graph :', value='my file name', placeholder='file name')
    container.button('Select directory', on_click=choose_dir)
    
    if st.session_state.get('save_dir',"") == "":
        st.session_state['disabled'] = True
    else:
        st.session_state['disabled'] = False
        container.write(f"path : {st.session_state['save_dir']}") 
    
    if graph_type is None:
        container.button(label='Generate all genes (png)', on_click=generate_png, args = (container, "test"), disabled=st.session_state['disabled'])
         
    container.button(label='Generate Graph (png)', on_click=generate_png, args = (container,), disabled=st.session_state['disabled'])
    if st.session_state.get("plot_generate", "") != "":
        container.info(st.session_state['plot_generate']) 
   
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
                st.session_state['plot_generate'] = ''
                container.info("A graph with the same name already exist, confirm for overwriting or cancel and change the file name")
                overwrite = container.button(label='Overwrite', on_click=save_image, args=(fig,name_file))
                cancel = container.button(label='Cancel')                                                  
                if cancel:
                    del overwrite
                    del cancel
                    return
            else:
                save_image(fig_plot=fig, name=name_file)    
        else:
            st.session_state['plot_generate'] = 'Missing file name'  

def sidebar_settings(**dict_config:dict):    
    def query_maker(col,select_type):
        if select_type in ['select',None]:
            selected = st.sidebar.selectbox(
                f"Select a {col}:",
                options=df[col].unique(),key=f"a{col}",
                )
            # we need a list for the Query
            selected = [selected]
        elif select_type in ['multi','group']:
            sidebar_container = st.sidebar.container()
            if st.sidebar.checkbox("Select all", key=f"b{col}"):
                selected = sidebar_container.multiselect(
                    f"Select one or more {col}:",        
                    options=df[col].unique(),
                    default=df[col].unique(),key=f"c{col}"
                    )
            else:
                selected = sidebar_container.multiselect(
                    f"Select one or more {col}:",        
                    options=df[col].unique(),key=f"d{col}"
                    )
        query = f"{col} == {selected}"
        return query
      
    df = st.session_state['df']
    query = " and ".join(query_maker(key,value) for key, value in dict_config.items())
    
    df_selection = df.query(query)
    st.session_state['df_selection'] = df_selection   
     
    template_options = ['ggplot2', 'seaborn', 'simple_white', 'plotly',
         'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
         'ygridoff', 'gridon', 'none']
    selected_template = st.sidebar.selectbox(
        "Select a template:",
        options=template_options,
    )
    st.session_state['template'] = selected_template    
     
    st.sidebar.markdown('---')        
    if st.sidebar.button('Back home'):
        st.session_state['step'] = 0
        st.experimental_rerun()
    st.sidebar.markdown('#')  

# Show the label of data and test stat result 
def add_label_and_test_stat(fig, df):       
    def get_params(m):
        if m > 10:
            return 0
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

        return dic_temp_val[m]

    def annot_one_bar_simple(text,y_height,font_size, col_stats): 
        df[col_stats] = df[st.session_state[col_stats]].fillna(1).map(significance) 
        for _, s in df.iterrows():           
            fig.add_annotation(text=text * s[col_stats],font=dict(size=font_size),
                x=s['condi_test'], y=s['QRm'] + s['QRe'] + y_height,showarrow=False)
            

    def annot_one_bar_group(text,y_height,font_size,col_stats): 
        df[col_stats] = df[st.session_state[col_stats]].fillna(1).map(significance)
        # dic_param = get_params(nb_gene)            
        for _, s in df.iterrows():           
            fig.add_annotation(text=text * s[col_stats],font=dict(size=font_size),
                x=s['condi_test'] + dic_param[s['gene_test']], y=s['QRm'] + s['QRe'] + y_height,showarrow=False)

    def annot_multiple_bar(text,y_height,font_size, col_stats): 
        x_col=0
        col_graph = 1        
        row = ceil(nb_gene/4)          
        df[col_stats] = df[st.session_state[col_stats]].fillna(1).map(significance) 
        for _, s in df.iterrows():           
            fig.add_annotation(text=text * s[col_stats],font=dict(size=font_size),
                x=s['condi_test'], y=s['QRm'] + s['QRe'] + y_height,showarrow=False, 
                row =row, col= col_graph)         
                      
            x_col += 1
            if nb_col == x_col:
                x_col = 0
                col_graph += 1 
                if col_graph > 4:
                    col_graph = 1
                    row -= 1   
    
    def write_legend(fct_name_annot):
                st.session_state['error_test_stat'] = ''  
                if st.session_state['test_stats'] != 'No':   
                    try:                    
                        if st.session_state['test_stats'] == 'Yes +/★':
                            fct_name_annot(text="★", y_height=0.55, font_size=13, col_stats="col_test_stat_neg")                      
                        fct_name_annot(text="<b>+<b>", y_height=0.4, font_size=16, col_stats="col_test_stat_pos")         
                    except Exception:
                        st.session_state['error_test_stat'] = 'Choose column numeric please'  
                    else:   
                        legend = f"Statistical test : <br> + : {st.session_state['col_test_stat_pos']}<br>"
                        if st.session_state['test_stats'] == 'Yes +/★':
                            legend += f" ★ : {st.session_state['col_test_stat_neg']} <br>"
                        st.session_state['legend_title']  = f"{legend} <br>{st.session_state['x_label']}"
                else:
                    st.session_state['legend_title']  = st.session_state['x_label']     
                    
                    
    # sort the df and add 2 col categories for the gene and condition
    cat_condition = pd.CategoricalDtype(df['Condition'].unique(),ordered = True)
    cat_gene = pd.CategoricalDtype(df['Gene'].unique(),ordered = True)
    df= df.astype({'Condition':cat_condition})
    df= df.astype({'Gene':cat_gene})
    df['condi_test'] = df['Condition'].cat.codes
    df['gene_test'] = df['Gene'].cat.codes
    df = df.sort_values(['Gene','condi_test'])
    
    significance = pd.Series([3,2,1,0], pd.IntervalIndex.from_breaks([0,0.001,0.01,0.05,np.inf],closed = 'left'), name = 'Significance levels')  
    
    font_size = st.session_state['size_font']
    # recuperer hauteur pour afficher au dessus des error_y si presente     
    if  st.session_state['graph_error'] != 'QRe':
       df['QRe'] = 0
    
    nb_col = len(df['Condition'].unique())
    nb_gene = len(df['Gene'].unique()) 
    
    # One plot - Group version
    if st.session_state['step'] == 1:
        if (nb_gene > 1) and (st.session_state['bar_type'] == 'group'): 
            dic_param = get_params(nb_gene)
            for i, s in df.iterrows():        
                fig.add_annotation(text=round(s['QRm'],2),font=dict(size=font_size),
                    x=s['condi_test'] + dic_param[s['gene_test']], y=s['QRm'] + s['QRe'] + 0.2,showarrow=False)
                fig.add_annotation(text=f"{s['Nb_ech']}",font=dict(size=font_size),
                    x=s['condi_test'] + dic_param[s['gene_test']], y=0.10,showarrow=False)

            write_legend(annot_one_bar_group)                       
    
        # One plot - Simple version 
        else:
            for i, s in df.iterrows():  
                fig.add_annotation(text=round(s['QRm'],2),font=dict(size=font_size),
                    x=s['condi_test'], y=s['QRm'] + s['QRe'] + 0.2,showarrow=False)
                fig.add_annotation(text=f"{s['Nb_ech']}",font=dict(size=font_size),
                    x=s['condi_test'] , y=0.10,showarrow=False)
               
            write_legend(annot_one_bar_simple)                       
                 
    # Multiple Plot
    if st.session_state['step'] == 2:
        x_col=0
        col_graph = 1        
        row = ceil(nb_gene/4)          
        for _, s in df.iterrows():      
            fig.add_annotation(text=round(s['Nb_ech'],2),font=dict(size=font_size),
                x=s['condi_test'], y=0.1,showarrow=False,
                row=row, col=col_graph)       
            fig.add_annotation(text=round(s['QRm'],2),font=dict(size=font_size),
                x=s['condi_test'], y=s['QRm'] + s['QRe'] + 0.1,showarrow=False,
                row=row, col=col_graph)
            x_col += 1
            if nb_col == x_col:
                x_col = 0
                col_graph += 1 
                if col_graph > 4:
                    col_graph = 1
                    row -= 1                         
                    
        write_legend(annot_multiple_bar)
        