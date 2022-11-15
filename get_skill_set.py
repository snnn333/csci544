
skill_set = {}

def trans_str_map(str_value):
    line_list = eval(str_value)
    return line_list

def add_set(line_list):
    _keys = -1
    for line_map in line_list:
        if (line_map["title"] == "Summary"):
            _keys = line_map["category"]

    for line_map in line_list:
        # print(line_map)
        if (line_map["title"] == "Skills"):
            skills = line_map["content"]
            skills = skills
            # print(skills)
            if _keys!=-1:
                if _keys in skill_set.keys():

                    cset = skill_set[_keys]
                else:
                    cset = set()
                for skill in skills:
                    skill = skill.split(', ')
                    for s in skill:
                        if s != '':
                            cset.add(s)
                skill_set[_keys] = cset


def read_file(path):
    with open(path, "r", encoding='utf-8') as f:
        for line in f:
            line = line[:-1]
            line_list = trans_str_map(line)
            add_set(line_list)


def save_data(path):
    with open(path, "w", encoding="utf-8") as f:
        print(skill_set, file=f)


if __name__ == "__main__":
    path = "resume_content.txt"
    read_file(path)

    out_put = "skill_set.txt"
    save_data(out_put)

