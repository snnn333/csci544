from collections import defaultdict
import re

skill_set = {}
skill_freq = {}
each_skills = {}

top_skills = defaultdict(list)

def data_clean(text):
    text = text.lower()

    # remove non-alphabetical characters
    REGEX = re.compile("[^ ^a-zA-Z]")
    text = re.sub(REGEX, ' ', text)

    # remove extra spaces
    wds = text.split()
    text = ' '.join(wds)
    
    text = text.strip()
    return text

def trans_str_map(str_value):
    line_list = eval(str_value)
    return line_list

def add_set(line_list):

    id = line_list[0]["id"]
    _keys = line_list[0]["category"]
    
    for line_map in line_list:
        if (line_map["title"] == "Summary"):
            _keys = line_map["category"]

    sks = set()
    for line_map in line_list:
        if ("skill" in line_map["title"].lower()):
            skills = line_map["content"]
            skills = skills
             
            if _keys in skill_set.keys():

                cset = skill_set[_keys]
                fdict = skill_freq[_keys]
            else:
                cset = set()
                fdict = defaultdict(int)
            for skill in skills:
                skill = skill.split(', ')
                for s in skill:
                    s = data_clean(s)
                    if s != '':
                        cset.add(s)
                        fdict[s] += 1
                        sks.add(s)

            skill_set[_keys] = cset
            skill_freq[_keys] = fdict
    each_skills[id+'_'+_keys] = sks
        


def read_file(path):
    with open(path, "r", encoding='utf-8') as f:
        for line in f:
            line = line[:-1]
            line_list = trans_str_map(line)
            if line_list:
                add_set(line_list)
            
            
def get_top_ski():
    for key, value in each_skills.items():
        
        id, cate = key.split('_')

        n = 0
        for sk in sorted(skill_freq[cate].items(), key=lambda x: x[1], reverse=True):
            if sk in value and n < 3:
                top_skills[id].append(sk)
                n += 1
        if n < 3:
            for sk in value:
                if n < 3:
                    top_skills[id].append(sk)
                    n += 1
        
        
            

def save_data(path, dict):
    with open(path, "w", encoding="utf-8") as f:
        for key, value in dict.items():
            f.write('%s:%s\n' % (key, value))

def save_freq():
    for key, value in skill_freq.items(): 
        path = "output/skill_freq/"+key.lower()+".txt"
        with open(path, "w", encoding="utf-8") as f:
            for skill, freq in sorted(value.items(), key=lambda x: x[1], reverse=True):
                f.write('%s:%s\n' % (skill, freq))
        

if __name__ == "__main__":
    path = "output/resume_content.txt"
    read_file(path)

    get_top_ski()
    
    for key, value in top_skills.items():
        print('%s:%s\n' % (key, value))
        break
    # out_put_skill_set = "output/skill_set.txt"
    # save_data(out_put_skill_set, skill_set)
    # save_freq()

    out_put_top_skill = "output/top_skill.txt"
    save_data(out_put_top_skill, top_skills)

