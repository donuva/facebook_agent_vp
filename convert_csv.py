import json
import pandas as pd 

with open ('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(data['questions'][0].keys())

ques_list = []
credit_card = []
loan = []
general = []

for d in data['questions']:
    #print(d['question'][2:])
    if d['question'][2:] in ques_list:
        continue

    ques_list.append(d['question'][2:])
    credit_card.append(1) if 'credit' in d['labels'] else credit_card.append(0)
    loan.append(1) if 'loan' in d['labels'] else loan.append(0)
    general.append(1) if 'general' in d['labels'] else general.append(0)

dict_csv = {'question':ques_list, 'credit_card':credit_card, 'loan':loan, 'general': general}

pd.DataFrame(dict_csv).to_csv("new_label.csv", index=False)

    
