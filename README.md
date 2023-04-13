# FYP_NTU
FYP Project on ABSA using GPT-3 by OpenAI

## Experiments
All experiemnts can be found under experiments folder.

## WebApp
Flask is used to develop the webapp and Plotly is used for generation of graphs.  

Using the webapp:
1) Download main_app and pip install requirements.txt file. (recommended to set up venv)
2) Add in key for OPENAI to use gpt-3 under absa.py file. 
3) To start the app, in cmd, specify the file directory to app.py and enter py app.py.
4) Name header for reviews in csv file as 'text'

Limitations to note are rate limits and token limits of the GPT-3 so the data size cannot be too large.



## References for code:
1) GPT-3 usage: https://github.com/mpangrazzi/absa_poc_pipeline
2) Loading Screen: https://github.com/3E5F/flask_loading_screen
