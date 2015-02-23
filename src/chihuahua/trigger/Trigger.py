#! /usr/bin/python
import sys
import rpyc
import argparse as ap

def view_symbol(args):
    try:
        symbols = args.symbols
        interval = args.interval
    except NameError:
        print "Incorrect arguments"
        sys.exit(0)
    request = {"mod":"view","cmd":"add","sym":symbols,"interval":interval}
    send_request(request)

def list_queue_items(args):
    request = {"mod":"view","cmd":"list"}
    send_request(request)

def move_queue_item(args):
    try:
        index = args.index
        position = args.position
    except NameError:
        print "Incorrect arguments"
        sys.exit(0)
    request = {"mod":"view","cmd":"move","id":index,"position":position}
    send_request(request)

def remove_queue_item(args):
    try:
        index = args.index
    except NameError:
        print "Incorrect arguments"
        sys.exit(0)
    request = {"mod":"view","cmd":"remove","id":index}
    send_request(request)

def run_strategy(args):
    try:
        name = args.name
    except NameError:
        print "Incorrect arguments"
        sys.exit(0)
    request = {"mod":"str","cmd":"run","name":name}
    send_request(request)

def list_running_strategy(args):
    request = {"mod":"str","cmd":"list"}
    send_request(request)

def stop_strategy(args):
    try:
        index = args.index
    except NameError:
        print "Incorrect arguments"
        sys.exit(0)
    request = {"mod":"str","cmd":"stop","id":index}
    send_request(request)

def send_request(request):
    print request
    host = "localhost"
    conn = rpyc.connect(host,8088)
    conn.root.request(request)
    conn.close()

def main():
    parser = ap.ArgumentParser()
    subparsers = parser.add_subparsers(help="subcommands")

    psr_vi = subparsers.add_parser("vi",help="call Viewer")
    psr_vi.add_argument("symbols",nargs="+",help="symbols to view")
    psr_vi.add_argument("-i","--interval",type=float,default=0.5,help="time interval for plotting tick data")
    psr_vi.set_defaults(func=view_symbol)    

    psr_vl = subparsers.add_parser("vl",help="list all items in the message queue")
    psr_vl.set_defaults(func=list_queue_items)

    psr_vm = subparsers.add_parser("vm",help="relocate item in the message queue")
    psr_vm.add_argument("index",type=int,help="position of the item to be moved")
    psr_vm.add_argument("-p","--position",type=int,default=0,help="target position of the item to be moved")
    psr_vm.set_defaults(func=move_queue_item)

    psr_vd = subparsers.add_parser("vd",help="remove item from the queue")
    psr_vd.add_argument("index",type=int,help="position of the item to be removed")
    psr_vd.set_defaults(func=remove_queue_item)

    psr_ss = subparsers.add_parser("ss",help="run strategy")
    psr_ss.add_argument("name",help="name of the strategy to be run")
    psr_ss.set_defaults(func=run_strategy)

    psr_sl = subparsers.add_parser("sl",help="list running strategies")
    psr_sl.set_defaults(func=list_running_strategy)

    psr_st = subparsers.add_parser("st",help="stop running strategy")
    psr_st.add_argument("index",type=int,help="index of the strategy to be stopped") 
    psr_st.set_defaults(func=stop_strategy)    

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

