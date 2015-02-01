#! /usr/bin/python

import argparse as ap

def main():
    parser = ap.ArgumentParser()
    subparsers = parser.add_subparsers(help="subcommands")

    psr_v = subparsers.add_parser("v",help="call Viewer")
    psr_v.add_argument("symbols",nargs="+",help="symbols to view")
    psr_v.add_argument("-i","--interval",type=float,default=0.5,help="time interval for plotting tick data")

    psr_vl = subparsers.add_parser("vl",help="list all items in the message queue")

    psr_vm = subparsers.add_parser("vm",help="relocate item in the message queue")
    psr_vm.add_argument("index",type=int,help="position of the item to be moved")
    psr_vm.add_argument("-p","--position",type=int,dest="target_index",default=0,help="target position of the item to be moved")

    psr_vd = subparsers.add_parser("vd",help="remove item from the queue")
    psr_vd.add_argument("index",type=int,help="position of the item to be removed")

    psr_s = subparsers.add_parser("s",help="run strategy")
    psr_s.add_argument("name",help="name of the strategy to be run")

    psr_sl = subparsers.add_parser("sl",help="list running strategies")

    psr_ss = subparsers.add_parser("ss",help="stop running strategy")
    psr_ss.add_argument("id",help="id of the strategy to be stopped") 
    
    args = parser.parse_args()
    print args


if __name__ == "__main__":
    main()

