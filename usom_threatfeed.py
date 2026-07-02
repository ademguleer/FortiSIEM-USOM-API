import sys
import csv
import argparse
from fsiem_utils.threatfeed_integration import *

class UsomThreatFeed(ThreatfeedIntegration):
    def getThreatFeedData(self):
        data_list = []
        csv_path = "/opt/phoenix/cache/MalwareIP/usom_temiz.csv"
        
        try:
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data_list.append(row)
            
            if len(data_list) > 0:
                self.saveThreatFeedData(data_list)
                
        except Exception as e:
            print(f"[-] Hata: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='threatfeed integration')
    arg_parser.add_argument('-updateType', default='full', action='store',type=str)
    arg_parser.add_argument('-appUser', default=None, action='store',type=str)
    arg_parser.add_argument('-appPW', default=None, action='store',type=str)
    arg_parser.add_argument('-appHost', default='https://127.0.0.1', action='store',type=str)
    arg_parser.add_argument('-naturalId', required=True, action='store',type=str)
    arg_parser.add_argument('-tfType', required=True, action='store',type=str)
    arg_parser.add_argument('-tfURL', required=True, action='store',type=str)
    arg_parser.add_argument('-tfUser', action='store',type=str)
    arg_parser.add_argument('-tfPW', action='store',type=str)
    arg_parser.add_argument('-sslVerify', default="true", action='store',type=str)
    args = arg_parser.parse_args()

    if args.appUser and args.appPW:
        threatfeed = UsomThreatFeed(updateType=args.updateType, naturalId=args.naturalId, tfType=args.tfType, tfURL=args.tfURL, tfUser=args.tfUser, tfPW=args.tfPW, appUser=args.appUser, appPW=args.appPW, appHost=args.appHost, sslVerify=args.sslVerify)
    else:
        threatfeed = UsomThreatFeed(updateType=args.updateType, naturalId=args.naturalId, tfType=args.tfType, tfURL=args.tfURL, tfUser=args.tfUser, tfPW=args.tfPW, appHost=args.appHost, sslVerify=args.sslVerify)

    threatfeed.getThreatFeedData()
