import os, sys
from savant.algo import * 
import argparse

here = os.path.dirname(os.path.realpath(__file__))
#Change me here before call the function, or change the latest file created in the path
modeler_sample_res = '''
{"memo":"", "filter_param":{"T1_F1":"1w", 
                         "RP_T1_F1": 0.03,
                         "P_F1_MAX": "inf",
                         "P_F1_MIN": 10.0,
                         "V_F1_MAX": "inf",
                         "V_F1_MIN": 800000},
                "param":{"T2_F1":"5m",
                         "RP_T2_F1": 0.0,
                         "RP_S": "0.1",
                         "RV_S": "1.5",
                         "T_F2": "5m",
                         "RP_F2":"0.03"}
}
'''

trigger_sample_res = '''
{"memo":"", link:"", "param":{}
}
'''

#                "out":[{"sym":"AAPL", "range":"xxxxx:xxxx", "expanded_range":"xxxxxxxxx:xxxxxxxxx", 
#                        "rp_t1_f1": 0.17, "p_f1_h": 45.23, "p_f1_l":44.18, "v_f1": 1023452, 
#                        "rp_t2_f1": 0, "rp_s":0.13, "rv_s": 3.75, "rp_f2": 0.01}]

def create_cmd(args):
    if args.type !='m' and args.type != 't':
        print "invalid res type:", args.type
    if args.memo == "":
        print "memo cannot be empty"
    if args.type == 't' and args.link == "":
        print "modeler link cannot be empty when creating trigger res file"
    if args.type == 'm' and args.link != '':
        print 'link must be empty when creating modeler res file'

    if args.type == 'm':
        create_res(here, modeler_sample_res, args.memo, args.link) 
    else:
        create_res(here, trigger_sample_res, args.memo, args.link) 
        

def list_cmd(args):
    list_m = list_t = True
    if args.type !='m' and args.type != 't' and args.type != 'b':
        print "invalid res type:", args.type
    if args.type == 't':
        list_m = False
    if args.type == 'm':
        list_t = False
    mres, tres = list_res(here)
    if list_m:
        print "Modelers:"
        for i in range(1, 1+ min(len(mres), args.range)):
            print -i,'\t',
            print mres[-i].split('/')[-1], '\t',
            print get_res(mres[-i])["memo"]
    if list_t:
        print "Triggers:"
        for i in range(1, 1+ min(len(tres), args.range)):
            print -i,'\t',
            print tres[-i].split('/')[-1], '\t',
            print get_res(tres[-i])["memo"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="subcommands")
    
    psr_res = subparsers.add_parser("c",help="create a new res file")
    psr_res.add_argument("-t", "--type", type=str, default="m", help="res file type. m (modeler) by default or t (trigger)")
    psr_res.add_argument("-m","--memo",type=str, default="", help="memo string such as how it is different from the previous one. Cannot be empty")
    psr_res.add_argument("-l","--link",type=str, default="", help="modeler res file to be linked if this is to create a trigger res. Cannot not be empty" )
    psr_res.set_defaults(func=create_cmd)
    #psr_get.set_defaults(func=get_trade_data)

    psr_res = subparsers.add_parser("l",help="list the most recent res files")
    psr_res.add_argument("-t", "--type", type=str, default="b", help="res file type. m (modeler) or t (trigger) or b(both) by default")
    psr_res.add_argument("-r", "--range", type=int, default=20, help="number of files to list")
    psr_res.set_defaults(func=list_cmd)

    args = parser.parse_args()
    args.func(args)
