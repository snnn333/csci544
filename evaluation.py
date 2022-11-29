# !pip install bert_score

from ast import literal_eval
from collections import defaultdict

def combine_resume_content(cont_file):
    resumes = defaultdict(list)
    with open(cont_file, 'r') as f:
        for line in f:
            resu = list(literal_eval(line))
            if resu:
                id = resu[0]['id']
                category = resu[0]['category'].lower()
            
                cont = ""
                for sec in resu:
                    cont += ' '.join(sec['content'])
            
                resumes["{}_{}".format(id, category)].append(cont)
            
            
    return resumes

from bert_score import score

def get_bert_score(predictions, references):

    P, R, F1 = score(predictions, references, lang="en", verbose=True)

    return F1.mean()

def get_intro(intro_file):
    intros = defaultdict(list)
    with open(intro_file, 'r') as f:
        for line in f:
            id, intro = line.split(", [")
            intros[id].append(intro.replace(']', ''))
    return intros

def save_score(score_file, resumes, intros):
    out = open(score_file, 'w+')
    for key in resumes.keys():
        id, category = key.split('_')
        
        if intros[id]:
            predictions = intros[id]
            references = resumes[key]
            score = get_bert_score(predictions, references)
            out.write("{}, {}, {}\n".format(id, category, format(score, '.4f')))

if __name__ == "__main__":

    # cont_file = path+"output/resume_content.txt"
    # intro_file = path+"output/intros.txt"

    cont_file = "output/resume_content.txt"
    intro_file = "output/intros.txt"


    resumes = combine_resume_content(cont_file)
    intros = get_intro(intro_file)

    
    # score_file = path+"result/score.txt"
    score_file = "result/score.txt"

    save_score(score_file, resumes, intros)

