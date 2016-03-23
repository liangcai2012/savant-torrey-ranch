import os, sys
from savant.algo import * 
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

#                "out":[{"sym":"AAPL", "range":"xxxxx:xxxx", "expanded_range":"xxxxxxxxx:xxxxxxxxx", 
#                        "rp_t1_f1": 0.17, "p_f1_h": 45.23, "p_f1_l":44.18, "v_f1": 1023452, 
#                        "rp_t2_f1": 0, "rp_s":0.13, "rv_s": 3.75, "rp_f2": 0.01}]



print list_res(here)
exit()

if __name__ == "__main__":
    args = sys.argv
    if len(args) !=2 or not (args[1]=='m' or args[1]=='t'):
        print "Usage: create_res m|t"
    elif args[1]=='m':
        create_res(modeler_sample_res, here) 
    else:
        create_res(trigger_sample_res,here) 
   
