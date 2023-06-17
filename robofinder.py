import requests , os , argparse, time
from colorama import Fore

def logger(silent,message,TYPE):
    if silent != True:
        if TYPE == "error":
            print(Fore.LIGHTCYAN_EX+"["+Fore.LIGHTYELLOW_EX+"✗"+Fore.LIGHTCYAN_EX+"] "+Fore.RED+message+Fore.RESET)
        elif TYPE == "success":
            print(Fore.LIGHTCYAN_EX+"["+Fore.LIGHTYELLOW_EX+"✓"+Fore.LIGHTCYAN_EX+"] "+Fore.LIGHTWHITE_EX+message+Fore.RESET)
        elif TYPE == "pending":
            print(Fore.LIGHTCYAN_EX+"["+Fore.LIGHTYELLOW_EX+"*"+Fore.LIGHTCYAN_EX+"] "+Fore.LIGHTWHITE_EX+message+Fore.RESET)
        time.sleep(0.30)

def setup_argparse():

    parser = argparse.ArgumentParser(description="Robo Finder")
    parser.add_argument("--silent", action="store_true",default=False, help="Make Program Silent")
    parser.add_argument('--url','-u', dest='url', type=str, help='Give me the URL' , required=True)
    parser.add_argument('--output', '-o' , dest='output',default=False, type=str, help='output file path')
    return parser.parse_args()

def getArchives(args):
    try:
        logger(args.silent,"Sending an HTTP request to the archive to obtain all paths for robots.txt files.","pending")
        url = f"https://web.archive.org/cdx/search/cdx?url={args.url}/robots.txt&output=json&fl=timestamp,original&filter=statuscode:200&collapse=digest"
        logger(args.silent,"Got the data as JSON objects.","success")
        response = requests.get(url).json()
        if ['timestamp', 'original'] in response:
            response.remove(['timestamp', 'original'])
        return response

    except Exception as e:
        logger(args.silent,e,"error")

def getrobo(args, datalist):
    try:
        robolist = []
        logger(args.silent,"Sending HTTP requests to obtain old robots.txt files...","pending")
        if datalist != []:
            for data in datalist:
                response = requests.get(f"https://web.archive.org/web/{data[0]}if_/{data[1]}").text
                for i in response.split("\n"):
                        clean_l = i.strip()
                        if len(clean_l) > 0:
                            (tag, value) = i.split(":")
                            tag = tag.strip()
                            value = value.strip()
                            if value != "*":
                                robolist.append(value)
                time.sleep(5)
            logger(args.silent,"Extracting all paths from robots.txt files","pending")
            robolist = list(set(robolist))
            return robolist
        else:
            return []

    except ValueError:
        logger(args.silent,"There is a problem in response.","error")
    except Exception as e:
        logger(args.silent,e,"error")


def saveToFile(args,data,name):
    logger(args.silent,"Saving results to result.txt {}".format(name),"pending")
    __path__ = os.path.dirname(os.path.realpath(__file__))+"/{}".format(name)
    with open(__path__,"w") as f:
        for i in data:
            f.writelines("{}\n".format(i))
    logger(args.silent,"All results saved to {}".format(name),"success")

def main():
    try:
        args = setup_argparse()
        datalist = getArchives(args)
        robo = getrobo(args,datalist)
        if robo != []:
            if args.output:
                saveToFile(args,robo,args.output)
            logger(args.silent,"Results:","success")
            for r in robo:
                print(r)
        else:
            logger(args.silent,"There is no results.","error")
    except KeyboardInterrupt:
        logger(args.silent,"Program terminated by user.","error")

if __name__ == "__main__":
    main()