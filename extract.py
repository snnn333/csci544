from ast import literal_eval
import json
import re
import torch
from transformers import BertForQuestionAnswering
from transformers import BertTokenizer

#Model
model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
#Tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
def data_clean(text):
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    # remove non-alphabetical characters
    REGEX = re.compile("[^ ^a-zA-Z]")
    text = re.sub(REGEX, ' ', text)

    # remove extra spaces
    wds = text.split(' ')
    text = ' '.join(wds)
    
    text = text.strip()
    return text
def bert_model(question, context):
    
    encoding = tokenizer.encode_plus(text=question,text_pair=context, max_length = 512, truncation = True)
    inputs = encoding['input_ids']  #Token embeddings
    sentence_embedding = encoding['token_type_ids']  #Segment embeddings
    tokens = tokenizer.convert_ids_to_tokens(inputs) #input tokens

    output = model(input_ids=torch.tensor([inputs]), token_type_ids=torch.tensor([sentence_embedding]))
    start_index = torch.argmax(output.start_logits)

    end_index = torch.argmax(output.end_logits)

    answer = ' '.join(tokens[start_index:end_index+1])

    corrected_answer = ''

    for word in answer.split():
    
        #If it's a subword token
        if word[0:2] == '##':
            corrected_answer += word[2:]
        else:
            corrected_answer += ' ' + word
    

    return corrected_answer

def extract_edu(cont_file):
    # edu_out = open(path+"output/education.txt", 'w+')
    # edu_out = open("output/education.txt", 'w+')
    edu_out = open("/scratch2/chiyuwei/544/output/education.txt", 'w+')
    edu_info = {}
    with open(cont_file, 'r') as f:
        for line in f:
            resu = list(literal_eval(line))
            if len(resu) == 0:
                break
            id = resu[0]['id']
            category = resu[0]['category'].lower()
            
            for sec in resu:

                title = sec['title'].lower()

                if "education" in title :

                    ques_college = "what is your college?"
                    ques_major = "what is your major?"
                    ques_degree = "what is your degree"

                    context = ' '.join(sec['content'])
                    college = data_clean(bert_model(ques_college, context))
                    major = data_clean(bert_model(ques_major, context))
                    degree = data_clean(bert_model(ques_degree, context))

#                     print('{}, {}, {},{}, [{}]\n'.format(id, college, major, degree, context))
                    edu_out.write('{} | {} | {} | {} | [{}]\n'.format(id, college, major, degree, context))
                    edu_info[id] = '{} | {} | {}'.format(college, major, degree)
            
    return edu_info

def extract_expr(expr_file):
    # exp_out = open(path+"output/exp_summary.txt", 'w+')
    # exp_out = open("output/exp_summary.txt", 'w+')
    exp_out = open("/scratch2/chiyuwei/544/output/exp_summary.txt", 'w+')
    expr_info = {}
    with open(expr_file, 'r') as f:

        for line in f:
            exps_list = json.loads(line)

            id = exps_list['id']
            exps = exps_list['experiences']
            if exps:
                wkex = "I have "+str(len(exps))+ " work experiences. "
                for exp in exps:
                    jobtitle = exp['jobtitle']
                    if jobtitle:
                        wkex = "As a "+jobtitle+", "

                    startsdate = exp['startsdate']
                    endsdate = exp['endsdate']

                    if endsdate:
                        wkex += "I worked from " + startsdate + " to " + endsdate + ". "
                    elif startsdate:
                        wkex += "I worked from " + startsdate + " to now."

                    jobduty = '. '.join(exp['jobduty'])
                    if jobduty:
                        wkex += "And my major duty is "+jobduty
            else:
                wkex = "I have no experiences."

            exp_out.write("{}|{}\n".format(id, wkex))
            expr_info[id] = wkex
            
    return expr_info

def extract_skill(skil_file):
    skil_info = {}
    with open(skil_file, 'r') as f:
        for line in f:
            id, skil = line.split(":")
            skil_info[id] = list(literal_eval(skil))
            
    return skil_info

def generate_intro(edu_info, expr_info, skil_info):
    
    all_intros = {}
#     I got my ____(bachelor/master/PhD) degree in _____(major) from ______ (college).
#     As a ___, I work from ___ (to ____), my major duty is __________.
#     I’m proficient at _____(extract from skills).

    for key in skil_info.keys():
        intro = ""
        if edu_info[key]:
            college, major, degree = edu_info[key].split('|')
            intro += "I got my "+ degree + " in "+ major + " from "+college + ". "
        
        if expr_info[key]:
            intro += expr_info[key] + " "

        if len(skil_info[key]) >= 3:
            intro += "I'm proficient at " + skil_info[key][0] + ", " + skil_info[key][1] + ", and " + skil_info[key][2] + '.'
        if len(skil_info[key]) == 2:
            intro += "I'm proficient at " + skil_info[key][0] + "and " + skil_info[key][1] + '.'
        if len(skil_info[key]) == 1:
            intro += "I'm proficient at " + skil_info[key][0] + '.'
        
        
        all_intros[key] = intro
        
    return all_intros

def save_intro(out_intro_file, intros):
    with open(out_intro_file, "w", encoding='utf-8') as f:
        for key, value in intros.items():
            f.write('%s, [%s]\n' % (key, value))

if __name__ == "__main__":
    # cont_file = path+"output/resume_content.txt"
    # expr_file = path+"output/experiences.txt"
    # skil_file = path+"output/top_skill.txt"

    # cont_file = "output/resume_content.txt"
    # expr_file = "output/experiences.txt"
    # skil_file = "output/top_skill.txt"

    cont_file = "/scratch2/chiyuwei/544/output/resume_content.txt"
    expr_file = "/scratch2/chiyuwei/544/output/experiences.txt"
    skil_file = "/scratch2/chiyuwei/544/output/top_skill.txt"
    
    edu_info = extract_edu(cont_file)
    expr_info = extract_expr(expr_file)
    skil_info = extract_skill(skil_file)
    
    intros = generate_intro(edu_info, expr_info, skil_info)

    # out_intro_file = path+"output/intros.txt"
    # out_intro_file = "output/intros.txt"
    out_intro_file = "/scratch2/chiyuwei/544/output/intros.txt"
    
    save_intro(out_intro_file, intros)