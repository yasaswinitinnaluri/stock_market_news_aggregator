
# Import required libraries
import requests
import re
from bs4 import BeautifulSoup
from transformers import pipeline
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

model = T5ForConditionalGeneration.from_pretrained("t5-small")
tokenizer = T5Tokenizer.from_pretrained("t5-small", use_fast=False)
import json

# replace {your API key} with your actual News API key
def get_news(stock_symbol):
    url = "https://newsapi.org/v2/everything?q=" + stock_symbol + "&apiKey=" + "bc970b8b18184b2faa5470f553c22360"

    # replace {stock symbol} with the actual stock symbol you want to fetch news for
    response = requests.get(url)

    # parse the response JSON
    data = json.loads(response.text)
    l = []
    upper_range = len(data['articles'])
    print(data['articles'][0])
    main_l = []
    for i in range(upper_range):
        d = {}
        d['title'] = data['articles'][i]['title']
        d['url'] = data['articles'][i]['url']
        d['author'] = data['articles'][i]['author']
        d['description'] = data['articles'][i]['description']
        x = """ """
        x += data['articles'][i]['content']
        pattern = r"\[[^\]]*\]"
        replaced_text = re.sub(pattern, "", x)
        replaced_text += data['articles'][i]['description']
        d['text'] = replaced_text
        main_l.append(d)
    main_l = main_l[::-1]
    content = main_l[:4]
    return content


def summarize_text(text):
    preprocess_text = text.strip().replace("\n","")
    t5_prepared_Text = "summarize: "+preprocess_text
    tokenized_text = tokenizer.encode(t5_prepared_Text,max_length=512, return_tensors="pt",truncation=True)
    # set maximum length for the summarized text
    max_len = 100
    # generate summary ids
    summary_ids = model.generate(tokenized_text,
                                    max_length=max_len, 
                                    num_beams=2,
                                    no_repeat_ngram_size=2,
                                    early_stopping=True)
    # decode the summary ids into text
    output = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return output

from flask import Flask
from flask import Flask, request, render_template,url_for,redirect
### WSGI Application
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/mains',methods=['POST'])
def mains():
    return render_template('index.html',output = "")
@app.route('/telugu',methods=['POST'])
def mains_telugu():
    return render_template('index_telugu.html',output = "")
@app.route('/summarize', methods=['POST'])
def summarize():
    print(request.form.values())
    stock_symbol = request.form['stock_symbol']
    finaloutput = ''
    main_l = get_news(stock_symbol)
    print(main_l[0])
    summary = """ """
    for d in main_l:
        finaloutput += '<h4>TITLE :</h4>'
        if d['title'] != "":
            finaloutput += d['title']
            finaloutput += "<br>"
        if d['text'] != "":
            finaloutput += "<h4>SUMMARY :</h4>"
            text = d['text']
            summary = summarize_text(text)
            finaloutput += summary + d['description']
        if d['url'] != "":
            finaloutput += "<br>"
            finaloutput += "<i>for more info</i> " + d['url']     
    return render_template('index.html', output=finaloutput)
@app.route('/summarize_telugu', methods=['POST'])
def summarize_telugu():
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate
    stock_symbol = request.form['stock_symbol']
    finaloutput = ''
    main_l = get_news(stock_symbol)
    print(main_l[0])
    summary = """ """
    for d in main_l:
        finaloutput += '<h4>శీర్షిక :</h4>'
        if d['title'] != "":
            g = d['title']
            transliterated_text = transliterate(g, sanscript.ITRANS, sanscript.TELUGU)    
            finaloutput += transliterated_text
            finaloutput += "<br>"
        if d['text'] != "":
            finaloutput += "<h4>సారాంశం :</h4>"
            text = d['text']
            summary = summarize_text(text)

            temp = summary + d['description']
            transliterated_text = transliterate(temp, sanscript.ITRANS, sanscript.TELUGU)    
            finaloutput += transliterated_text
        if d['url'] != "":
            finaloutput += "<br>"
            finaloutput += "<i>మరింత సమాచారం కోసం</i> " + d['url']
    return render_template('index.html', output=finaloutput)

if __name__ == '__main__':
    app.run(debug=True)