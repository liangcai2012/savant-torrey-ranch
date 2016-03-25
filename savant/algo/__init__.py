import os, glob, datetime
import json

def create_res(here, json_str, memo, link):
    parsed = json.loads(json_str)
    parsed["memo"]=memo
    if link!="":
        parsed["link"]=link
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    #here = os.path.dirname(os.path.realpath(__file__))
    path = here+"/"+now+"_M.res"
    with open(path, "w") as res_file:
        res_file.write(json.dumps(parsed, indent=4))

def list_res(here):
    #here = os.path.dirname(os.path.realpath(__file__))
    m_list = glob.glob(here+'/*'+"_M.res")
    t_list = glob.glob(here+'/*'+"_T.res")
    return sorted(m_list), sorted(t_list)

def get_res(name):
    with open(name) as res_file:    
        return json.load(res_file)

