from flask import Flask, request, jsonify
import werkzeug
import easyocr
import PIL
from PIL import ImageDraw
import numpy as np
import json
import logging
import pickle
import requests


app = Flask (__name__)

reader = easyocr.Reader(['en'])


@app.route('/upload', methods=["POST"])
def upload():
    if(request.method=="POST"):
        imagefile = request.files ['image']
        filename = werkzeug.utils.secure_filename (imagefile.filename)
        path = "./uplodedimages/"+filename
        imagefile.save("./uplodedimages/" + filename)
        
        bounds = reader.readtext(path, contrast_ths=0.05, adjust_contrast=0.7, add_margin=0.45, width_ths=0.7,decoder='beamsearch')
        
        result = {}
        d = ['Patient Name', 'Age & Sex', 'Haemoglobin', 'Total WBC Count', 'RBC count', 'Neutrophils', 'Lymphocytes',
            'Monocytes', 'Eosinophils', 'Basophils', 'Haematocrit (HCT)', 'MCV', 'MCH', 'MCHC', 'RDW', 'Platelet Count', 'RDW']
        print(bounds)
        new_param = []
        for i in bounds:
            print('working')
            if i[1][0] == '~':
                s = i[1].lstrip('~')
                new_param.append(s)
            elif i[1][0] == '(':
                s = i[1].lstrip('(')
                new_param.append(s)
            elif i[1][0] == '|':
                s = i[1].lstrip('|')
                new_param.append(s)
            elif i[1][0] == '[':
                s = i[1].lstrip('[')
                new_param.append(s)
            elif i[1][0] == '"':
                s = i[1].lstrip('"')
                new_param.append(s)            
            else:
                new_param.append(i[1])
            
        for i in range(0, len(new_param)):
            if new_param[i] in d:
                result[new_param[i]] = new_param[i + 1]
                    # app.logger.info(new_param[i])

        param = ['Haemoglobin', 'RBC count', 'Total WBC Count', 'Neutrophils', 'Lymphocytes', 'Monocytes', 'Eosinophils',
            'Basophils', 'Haematocrit (HCT)', 'MCV', 'MCH', 'MCHC', 'Platelet Count', 'RDW']
        for i in param:
            if result.get(i) is not None:
                pass
            else:
                result[i] = 0

        values = {}
        for i in param:
            values[i] = result[i]

        for k, v in values.items():
            res = isinstance(v, str)
            if res != True:
                continue
            values[k] = v.replace(',', '.')
        
        lst1 = []
        
        for k,v in values.items():
            res = isinstance(v, str)
            print(v)
            if res:
                if (not v[0].isdigit()) and (not v.isalpha()):
                    values[k] = 0 

        for k,v in values.items():
            try:
                values[k] = float(v)
            except:
                values[k] = 0

            lst1.append(values[k])
        print('its here')
        with open('model.pkl', 'rb') as file:
            model = pickle.load(file)
        print(lst1)
        input_values = np.array(lst1)
        input_values = input_values.reshape(1,-1) 
    
        pred = model.predict(input_values)
        print(pred[0])
        values['Output'] = float(pred[0])
        values['Patient Name'] = result['Patient Name']
        for i in d:
            if result.get(i) is not None:
                pass
            else:
                result[i] = 0
        values['Age & Sex'] = result['Age & Sex'].replace('I','/')
        values['Age & Sex'] = result['Age & Sex'].replace('i','/')
        
        json_file = json.dumps(values)
        logging.info('reached till here')
        return json_file

@app.route("/predict")
def predict():
    print('its here')
    with open('model.pkl', 'rb') as file:
        model = pickle.load(file)
    print(lst)
    input_values = np.array(lst)
    lst = []
    input_values = input_values.reshape(1,-1) 
    
    pred = model.predict(input_values)
    print(pred[0])
    # return {'result': result}

@app.route('/', methods=["POST"])
def home():
     return "abcdefg"

if __name__ == "_main_":
    app.run(debug=True,port=5000)
    