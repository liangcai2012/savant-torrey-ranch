import os, glob, datetime
import json

def create_res(json_str, here):
    parsed = json.loads(json_str)
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
