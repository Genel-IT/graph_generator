from streamlit.web import bootstrap

if __name__=='__main__':
    flag_options = flag_options={"global_developmentMode":False, "server_port":8501}
    bootstrap.load_config_options(flag_options=flag_options)
    bootstrap.run('main.py', command_line = 'streamlit run', args = [],flag_options=flag_options)