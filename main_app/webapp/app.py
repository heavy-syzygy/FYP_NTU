
from flask import Flask, render_template, render_template_string, request, session, redirect, url_for
from flask_navigation import Navigation
import pandas as pd
import os
from werkzeug.utils import secure_filename
import json

import plotly
import plotly.express as px

import absa

#*** Flask configuration

# Define allowed files
ALLOWED_EXTENSIONS = {'csv'}

# Define folder to save uploaded files to process further
app = Flask(__name__, template_folder='templateFiles', static_folder='staticFiles')

# Set config for secret key and uploaded data folder
app.config.from_pyfile('config.py')
# app.secret_key = 'This is your secret key to utilize session in Flask'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config["SESSION_PERMANENT"] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/',  methods=("POST", "GET"))
def uploadFile():
    if request.method == 'POST':
        # upload file flask
        uploaded_df = request.files['uploaded-file']
        if uploaded_df.filename != '':
            # Extracting uploaded data file name
            data_filename = secure_filename(uploaded_df.filename)

            # flask upload file to database (defined uploaded folder in static path)
            uploaded_df.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))
            # Storing uploaded file path in flask session
            session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
        else:
            return render_template_string("""
            {% block content %}
            <p style="color:darkred; font-size:35px;">No file detected, please upload one.</p>
            <p style="font-size:35px;"> Click to direct to Home: <a href="{{ url_for('index') }}">Link</a></p
            {% endblock %}""")

        return redirect(url_for('index'))

@app.route('/show_data')
def showData():
    # Retrieving uploaded file path from session
    try:
        data_file_path = session.get('uploaded_data_file_path', None)

        # read csv file in python flask (reading uploaded csv file from uploaded server location)
        uploaded_df = pd.read_csv(data_file_path)
        uploaded_df = uploaded_df.head(10)
        # pandas dataframe to html table flask
        uploaded_df_html = uploaded_df.to_html()
        return render_template('show_csv_data.html', data_var = uploaded_df_html)
    except:
        return render_template_string("""
        {% block content %}
        <p style="color:darkred; font-size:35px;">No file detected, please upload one.</p>
        <p style="font-size:35px;"> Click to direct to Home: <a href="{{ url_for('index') }}">Link</a></p
        {% endblock %}""")

@app.route('/settings', methods=['POST','GET'])
def settings():
    if request.method == 'POST':
    # Customise example for GPT
        firstList = []
        secList = []
        thirdList = []
        finalList = []
        for key, val in request.form.items(""):
            if val or val !='':
                if key.startswith("First"):
                    firstList.append(val)
                if key.startswith("Sec"):
                    secList.append(val)
                if key.startswith("Third"):
                    thirdList.append(val)
        if len(firstList) == 5 or len(firstList) == 9 or len(firstList) == 13:
            finalList.append(firstList)
        if len(secList) == 5 or len(secList) == 9 or len(secList) == 13:
            finalList.append(secList)
        if len(thirdList) == 5 or len(thirdList) == 9 or len(thirdList) == 13:
            finalList.append(thirdList)
        if len(finalList) != 0:
            session['gpt_input']=finalList
        else:
            session.pop('gpt_input', None)
            return render_template_string("""
            {% block content %}
            <p style="color:darkred; font-size:35px;">If all fields were empty, else, invalid inputs detected. Default prompt applied for both cases. </p>
            <p style="font-size:35px;"> Click to direct to Home: <a href="{{ url_for('index') }}">Link</a></p
            {% endblock %}""")
        return redirect(url_for('showData'))
    else:
        return render_template('settings.html')

@app.route('/loading', methods=['POST'])
def loading():
    return render_template('loading.html')

@app.route('/analysis', methods=['GET'])
def analysis():
    # Run data on GPT and obtain output
    if request.method == 'GET':
        data_file_path = session.get('uploaded_data_file_path', None)
        user_prompt = session.get('gpt_input', None)
        df_2, df_c, df_t, df_t_c = absa.gpt(data_file_path, user_prompt)
        df_c = df_c.to_dict('list')
        df_t = df_t.to_dict('list')
        df_t_c = df_t_c.to_dict('list')
        session['df_cat'] = df_c
        session['df_terms'] = df_t
        session['df_terms_cat'] = df_t_c
        return redirect(url_for('graphPol'))


# ---------------- functions to plot graphs below --------------------------

@app.route('/graphCAT')
def graphCat():
    try:
        df_cat = session.get('df_cat', None)

        df_ct = pd.DataFrame(df_cat)
        fig = px.pie(df_ct, values='counts', names='cat', title='Categories Count')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('graphs.html', graphJSON=graphJSON)
    except:
       return render_template_string("""
       {% block content %}
       <p style="color:darkred; font-size:35px;">No data detected, please analyse data first.</p>
       <p style="font-size:35px;"> Click to direct to Home: <a href="{{ url_for('index') }}">Link</a></p
       {% endblock %}""")

@app.route('/graphTERM')
def graphTerm():
    try:
        df_term = session.get('df_terms', None)

        df_t = pd.DataFrame(df_term)
        fig = px.pie(df_t, values='counts', names='terms', title='Terms Count')

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('graphs.html', graphJSON=graphJSON)
    except:
       return render_template_string("""
       {% block content %}
       <p style="color:darkred; font-size:35px;">No data detected, please analyse data first.</p>
       <p style="font-size:35px;"> Click to direct to Home: <a href="{{ url_for('index') }}">Link</a></p
       {% endblock %}""")

@app.route('/graphCATPOL')
def graphCatPol():
    try:
        df_cat = session.get('df_cat', None)

        df_ct = pd.DataFrame(df_cat)
        fig = px.bar(
           df_ct,
           x="cat",
           y="counts",
           color="pol",
           barmode="stack",
           color_discrete_map={
               "positive": "#52AC5E",
               "negative": "#e34a2d",
               "neutral": "gray",
           },
           title="Categories vs Polarity",
           template="plotly_white",
        )
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('graphs.html', graphJSON=graphJSON)
    except:
        return render_template_string("""
        {% block content %}
        <p style="color:darkred; font-size:35px;">No data detected, please analyse data first.</p>
        <p style="font-size:35px;"> Click to direct to Home: <a href="{{ url_for('index') }}">Link</a></p
        {% endblock %}""")

@app.route('/graphTermPOL')
def graphTermPol():
    try:
        df_term = session.get('df_terms', None)

        df_t = pd.DataFrame(df_term)
        fig = px.bar(
           df_t,
           x="terms",
           y="counts",
           color="pol",
           barmode="stack",
           color_discrete_map={
               "positive": "#52AC5E",
               "negative": "#e34a2d",
               "neutral": "gray",
           },
           title="Aspect Terms vs Polarity",
           template="plotly_white",
        )
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('graphs.html', graphJSON=graphJSON)
    except:
        return render_template_string("""
        {% block content %}
        <p style="color:darkred; font-size:35px;">No data detected, please analyse data first.</p>
        <p style="font-size:35px;"> Click to direct to Home: <a href="{{ url_for('index') }}">Link</a></p
        {% endblock %}""")

@app.route('/graphCATTERM')
def graphCatTerm():
    try:
        df_terms_cat = session.get('df_terms_cat', None)

        df_ct = pd.DataFrame(df_terms_cat)
        fig = px.bar(
           df_ct,
           x="cat",
           y="counts",
           color="terms",
           barmode="stack",
           color_discrete_map={
               "positive": "#52AC5E",
               "negative": "#e34a2d",
               "neutral": "gray",
           },
           title="Categories vs Aspect Terms",
           template="plotly_white",
        )

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('graphs.html', graphJSON=graphJSON)
    except:
        return render_template_string("""
        {% block content %}
        <p style="color:darkred; font-size:35px;">No data detected, please analyse data first.</p>
        <p style="font-size:35px;"> Click to direct to Home: <a href="{{ url_for('index') }}">Link</a></p
        {% endblock %}""")

@app.route('/graphPol')
def graphPol():
    try:
        df_cat = session.get('df_cat', None)

        df_ct = pd.DataFrame(df_cat)
        fig = px.pie(df_ct, values='counts', names='pol', title='Polarity Count')

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('graphs.html', graphJSON=graphJSON)
    except:
        return render_template_string("""
        {% block content %}
        <p style="color:darkred; font-size:35px;">No data detected, please analyse data first.</p>
        <p style="font-size:35px;"> Click to direct to Home: <a href="{{ url_for('index') }}">Link</a></p
        {% endblock %}""")

if __name__=='__main__':
    # app.run(debug = True)
    app.run(debug = False)
