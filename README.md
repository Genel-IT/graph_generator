# graph_generator

In order to build the application several things must be done:
* Add a wrapper python script that launches the server. This script points to the main.py file. This script also contains the flag parameters (global_developmentMode and server_port).
* Add the hook-streamlit file (necessary for the streamlit import to work). The hooks dir must be given in the spec file.
* Add the streamlit.static module to the datas of the application (in spec file)
* Add the main.py script to the datas AND hidden import of the spec file. (In the data for streamlit to find it, in the imports to be sure that all necessary module are found by pyinstaller).
* A template spec file can be obtained from the command: pyi-makespec GenGraph.py



To build the application:
pyinstaller .\GenGraph.spec --clean