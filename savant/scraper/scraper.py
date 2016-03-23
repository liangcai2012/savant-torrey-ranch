import argparse as ap
import savant.fetcher.traverse as traverse

def second_bar(args):
    traverse.generate_secboot_for_existing_trade(args.report)

def daily(args):
    print "daily"
    print args.report

if __name__ == "__main__":
    parser = ap.ArgumentParser()
    subparsers = parser.add_subparsers(help="subcommands")

    psr_secbar = subparsers.add_parser("secbar",help="create second bar data for any tick data fetched if not already done." )
    psr_secbar.add_argument("-r","--report", action='store_true', help="report only")
    psr_secbar.set_defaults(func=second_bar)

    psr_daily = subparsers.add_parser("daily", help="update daily table for any data with tick data fetched if not already done.")
    psr_daily.add_argument("-r","--report", action='store_true', help="report only")
    psr_daily.set_defaults(func=daily)


# ipo, including ipo_scoop, underwriter if needed, finance
# company
# report missing ticks

   # psr_company = subparser.add_parser

    args = parser.parse_args()
    args.func(args)
