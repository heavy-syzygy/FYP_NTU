from random import choice
# from tqdm.notebook import tqdm
from json import loads
from pprint import pprint
from textwrap import dedent
import re

from collections import Counter
import seaborn as sb
import matplotlib.pyplot as plt

import pandas as pd

import os
import logging
import sys

import openai

from gptConfig import analyze, prompt

# Setup OPENAI_API_KEY
# Spliitng key so that OpenAI cannot detect when debug mode is off
# Note: Input your own openAI key or contact me for a key
key1 = ""
key2 = ""

# os.environ["OPENAI_API_KEY"] = f"{key1}{key2}" #only for debug=True
openai.api_key = f"{key1}{key2}"

# Setup logging
log = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)

# Update sys.path (or use PYTHONPATH)
sys.path.insert(0, '..')

def fixJSON(jsonStr):
    try:
        jsonStr = re.sub(r'\\', '', jsonStr)

        jsonStr = re.sub(r'{"', '{\"', jsonStr)
        jsonStr = re.sub(r'{ "', '{"', jsonStr)
        jsonStr = re.sub(r'"}', '\"}', jsonStr)
        jsonStr = re.sub(r'" }', '\"}', jsonStr)

        jsonStr = re.sub(r'":"', '\":\"', jsonStr)
        jsonStr = re.sub(r'" : "', '\":\"', jsonStr)
        jsonStr = re.sub(r'":', '\":', jsonStr)
        jsonStr = re.sub(r'" :', '\":', jsonStr)
        jsonStr = re.sub(r':"', ':\"', jsonStr)
        jsonStr = re.sub(r': "', ':\"', jsonStr)

        jsonStr = re.sub(r'","', '\",\"', jsonStr)
        jsonStr = re.sub(r'" , "', '\",\"', jsonStr)
        jsonStr = re.sub(r'",', '\",', jsonStr)
        jsonStr = re.sub(r'" ,', '\",', jsonStr)
        jsonStr = re.sub(r',"', ',\"', jsonStr)
        jsonStr = re.sub(r', "', ',\"', jsonStr)

        jsonStr = re.sub(r'\["', '\[\"', jsonStr)
        jsonStr = re.sub(r'"\]', '\"\]', jsonStr)

        split_1 = jsonStr.split('[')
        split_1 = '['+split_1[1]
        split_2 = split_1.split(']')
        split_2 = split_2[0]+']'

        jsonStr = split_2

        return loads(jsonStr)
    except Exception as e:
        log.error(f"Failed to parse '{jsonStr}' -> {e}")
        return []

logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)

def gpt(df,user_prompt):
    analysis_results = []
    extra_prompts = []
    df = pd.read_csv(df)
    df=df.dropna(subset=["text"])
    for i in range(len(df)):
        text = df.loc[i, "text"]

        log.info(f"Analyzing feedback - \nText: {text}\n")

        user_input = prompt(user_prompt)

        extra_prompt = choice(extra_prompts) if extra_prompts else ""

        res = analyze(
            text=text,
            prompt_text=user_input,
            extra_prompt="",
            max_tokens=2048,
            temperature=0.1,
            top_p=1,
        )

        raw_json = res["choices"][0]["text"].strip()

        try:
            json_data = loads(raw_json)
            analysis_results.append(json_data)
            log.debug(f"JSON response: {pprint(json_data)}")
            extra_prompts.append(f"\n{text}\n{raw_json}")
        except Exception as e:
            log.error(f"Failed to parse '{raw_json}' -> {e}")
            analysis_results.append(fixJSON(raw_json))

    df["analysis"] = analysis_results

    def save_data(df):
        df.to_csv("./staticFiles/downloads/gpt_output.csv", index=False)
        annotations = []
        for i, entry in enumerate(analysis_results):
            for a in entry:
                a["review_id"] = i
                annotations.append(a)
        analysis_df = pd.DataFrame(annotations)
        analysis_df.to_csv("./staticFiles/downloads/analysis.csv", index=False)

    save_data(df)


    def format_output(analysis):
        term = []
        pol = []
        seg = []
        cat = []
        for i in analysis:
            term.append(i["aspect"])
            cat.append(i["category"])
            pol.append(i["sentiment"])
            seg.append(i["segment"])
        return pd.Series([term, cat, pol, seg])

    df[["term", "cat", "pol", "seg"]] = df.apply(lambda x: format_output(x["analysis"]), axis=1)

    list_term = []
    list_pol = []
    list_cat = []

    def terms_pol(term, cat, pol):
        for i in range(0, len(term)):
            list_term.append(term[i])
            list_cat.append(cat[i])
            list_pol.append(pol[i])
    _ = df.apply(lambda x: terms_pol(x["term"], x["cat"], x["pol"]), axis=1)

    df2 = pd.DataFrame({'terms': list_term, 'cat': list_cat, 'pol': list_pol})

    df_cat = df2.groupby(['cat','pol']).size().reset_index(name='counts')
    df_terms = df2.groupby(['terms','pol']).size().reset_index(name='counts')
    df_terms_cat = df2.groupby(['cat','terms']).size().reset_index(name='counts')

    return df2, df_cat, df_terms, df_terms_cat
