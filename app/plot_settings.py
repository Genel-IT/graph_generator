import plotly.express as px
import streamlit as st
from math import ceil

from app import graph_settings

# Home page with user instructions 
def main_page_load_data():
    st.title(":bar_chart: Gene PCR graph generator")
    st.markdown("##")
    main_container,space,description_container = st.columns([2,0.5,2])
        
    with main_container: 
        st.header('Select your source file ')        
        excel_file = st.file_uploader('Select a excel or csv file', type=['xlsx','csv'], accept_multiple_files=False)
        if excel_file != None:
            st.session_state['excel_file'] = excel_file
                        
        st.info("Your file has to be an '.xlsx' or '.csv' (excel file)") 
        
        option_dic = {1:'One plot',2:'Multiple plot',3:'Cinetic plot',4: 'Custom plot'}          
        graph_choose = st.radio("Choose your way to generate your graph :",  options=option_dic.keys(), format_func=lambda x: option_dic.get(x),horizontal=True) 
        st.session_state['graph_choose'] = graph_choose
        if 'error' in st.session_state:
            st.error('Error : Colunm in your file is missing.\nChoose another file or type of plot please. \nIf an error appends again, contact your admin')
        
        if excel_file != None:  
            st.button('Confirm', on_click=graph_settings.load_data_frame_and_next_step)

    with description_container:
        st.header('Source file - must have :') 
        st.text('If you choose one plot or multiple plot, the source file has to have :\n - Gene, Condition, QRm')
        st.text('If you choose Cinetic plot, your source file has to have : \n -Probe, Condition, Time ')

# Custumize one bar plot (bar group or no)
def bar_graph_plot():    
    graph_settings.sidebar_settings(Gene = st.session_state.get('bar_type',default="select"), Condition = 'multi')
    
    main_container = st.container()
    with main_container:   
        left_column, right_column  = st.columns([1,3])       
        
        graph_settings.main_setting_options(left_column,st.session_state.get('bar_type',None))
        
        #-----[BAR CHART] ------
        df_selection = st.session_state['df_selection']
        nb_gene = len(df_selection['Gene'].unique())
        text_auto = False if nb_gene < 11 else ".2s"
        try:
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
            if nb_gene < 11:
                graph_settings.add_label_and_test_stat(fig_bar_plot, df_selection)
                
            fig_bar_plot.update_layout(xaxis=(dict(showgrid=True)), showlegend=True,legend_title=st.session_state.get('legend_title','Condition'), 
                                       legend=dict(font=dict(size=size_font)))
            fig_bar_plot.update_xaxes(tickfont_size=size_font, title_font_size=size_font)
            fig_bar_plot.update_yaxes(tickfont_size=size_font, title_font_size=size_font)
            right_column.plotly_chart(fig_bar_plot, use_container_width=True)
            st.session_state['fig_save'] = fig_bar_plot
        except Exception as e: 
            # right_column.text(e) 
            right_column.text('Select data to see your graphs') 

# Custumize and generated multiplot in one or multiple files
def bar_multiplot_graph():
    graph_settings.sidebar_settings(Gene = 'multi', Condition = 'multi')
    
    main_container = st.container()
    with main_container:   
        left_column, right_column  = st.columns([1,3])
        
        graph_settings.main_setting_options(left_column, 'multi_bar_plot')         
        
        df_selection = st.session_state['df_selection']
        nb_gene = len(df_selection['Gene'].unique())
        st.session_state['text_auto'] = False if nb_gene < 13 else ".2s"
        m = ceil(nb_gene/4)
        height = (350 * m )if m > 1 else 500
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
                labels={
                    "Condition": st.session_state['x_label'],
                    "QRm":st.session_state['y_label'],
                        },
                width=1400,
                height=height
                )
            
            size_font = st.session_state['size_font']    
            
            if nb_gene < 13:
                graph_settings.add_label_and_test_stat(fig_multiple_graph, df_selection) 
                
            fig_multiple_graph.update_layout(xaxis=(dict(showgrid=True)), showlegend=True,legend_title=st.session_state.get('legend_title','Condition'),
                                             legend=dict(font=dict(size=size_font)))
            fig_multiple_graph.update_xaxes(tickfont_size=size_font, title_font_size=size_font)
            fig_multiple_graph.update_yaxes(tickfont_size=size_font, title_font_size=size_font)
            
            right_column.plotly_chart(fig_multiple_graph, use_container_width=True)
            
            st.session_state['fig_save'] = fig_multiple_graph
        except Exception as e:
            # right_column.text(e) 
            right_column.text('Select data to see your graphs') 

# Custumize and generated cinetic plot in one file
def plot_cinetic_graph():
    graph_settings.sidebar_settings(Probe = 'select',Condition ='multi')

    main_container = st.container()
    with main_container:   
        left_column, right_column  = st.columns([1,3])

        graph_settings.main_setting_options(left_column, 'cinetic_plot')  
                
        df_selection = st.session_state['df_selection']
        try: 
            fig = px.line(
                df_selection,
                x='Time',
                y='relative_mean',
                color='Condition', 
                title=st.session_state['title_file'], 
                template=st.session_state['template'],
                labels={"Time":st.session_state['x_label'],
                        "relative_mean": st.session_state['y_label'],
                        },
                width=1400,
                height=500
                )
                
            size_font = st.session_state['size_font']    
                
            fig.update_layout(xaxis=(dict(showgrid=True)), showlegend=True,legend=dict(font=dict(size=size_font)))
            fig.update_xaxes(tickfont_size=size_font, title_font_size=size_font)
            fig.update_yaxes(tickfont_size=size_font, title_font_size=size_font)
            
            right_column.plotly_chart(fig, use_container_width=True)   
                     
            st.session_state['fig_save'] = fig
        except Exception:
            right_column.text('Select data to see your graphs') 

# Custumize and generated a graph with custom column in one file
def custom_graph_col():
    #-----SIDEBAR-----    
    df = st.session_state['df']
    st.sidebar.text("Please choose your columns")
    selected_col_x = st.sidebar.selectbox("Select the column x:", options=df.columns, key="d")          
    selected_col_y = st.sidebar.selectbox("Select the column y:", options=df.columns, key="e")  
    selected_col_color = st.sidebar.selectbox("Select the color:", options=df.columns, key="c")
    
    st.sidebar.text("Edit your value")
    
    dico_sidebar_settings = {
        selected_col_x: 'multi',
        selected_col_color: 'multi', 
    }
    graph_settings.sidebar_settings(**dico_sidebar_settings) 
    
    # ---- MAINPAGE ----
    main_container = st.container()
    with main_container:   
        left_column, right_column  = st.columns([1,2])

        graph_settings.main_setting_options(left_column, "custom_plot")        
        
        df_selection = st.session_state['df_selection']
        try:
            #-----MULTIBAR CHARTS-----
            if st.session_state['graph_choose'] == 'Bar chart':
                fig_multiple_graph = px.bar(
                    df_selection, 
                    x=selected_col_x, 
                    y=selected_col_y, 
                    orientation="v", 
                    title=st.session_state['title_file'], 
                    color=selected_col_color,  
                    template=st.session_state['template'],
                    labels={selected_col_x:st.session_state['x_label'],
                            selected_col_y: st.session_state['y_label'],
                            },
                    width=1000,
                    height=500
                        )                
            else:
                fig_multiple_graph = px.line(
                    df_selection, 
                    x=selected_col_x, 
                    y=selected_col_y, 
                    title=st.session_state['title_file'], 
                    color=selected_col_color,  
                    template=st.session_state['template'],
                    labels={selected_col_x:st.session_state['x_label'],
                            selected_col_y: st.session_state['y_label'],
                            },
                    width=1000,
                    height=500,
                    )
                
            size_font = st.session_state['size_font']    
            fig_multiple_graph.update_layout(xaxis=(dict(showgrid=True)), showlegend=True,legend=dict(font=dict(size=size_font)))
            fig_multiple_graph.update_xaxes(tickfont_size=size_font, title_font_size=size_font)
            fig_multiple_graph.update_yaxes(tickfont_size=size_font, title_font_size=size_font)
              
            right_column.plotly_chart(fig_multiple_graph, use_container_width=True)
            st.session_state['fig_save'] = fig_multiple_graph
        except Exception:
            right_column.text('Select data to see your graphs')       
 