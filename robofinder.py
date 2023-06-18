import requests
import os
import argparse
import time
from colorama import Fore
import concurrent.futures

def logger(silent, message, TYPE):
    if silent != True:
        if TYPE == "error":
            print(Fore.LIGHTCYAN_EX + "[" + Fore.LIGHTYELLOW_EX + "✗" + Fore.LIGHTCYAN_EX + "] " + Fore.RED + message + Fore.RESET)
        elif TYPE == "success":
            print(Fore.LIGHTCYAN_EX + "[" + Fore.LIGHTYELLOW_EX + "✓" + Fore.LIGHTCYAN_EX + "] " + Fore.LIGHTWHITE_EX + message + Fore.RESET)
        elif TYPE == "pending":
            print(Fore.LIGHTCYAN_EX + "[" + Fore.LIGHTYELLOW_EX + "*" + Fore.LIGHTCYAN_EX + "] " + Fore.LIGHTWHITE_EX + message + Fore.RESET)
        time.sleep(0.30)

def setup_argparse():
    parser = argparse.ArgumentParser(description="Robo Finder")
    parser.add_argument("--silent", action="store_true", default=False, help="Make Program Silent")
    parser.add_argument('--url', '-u', dest='url', type=str, help='Give me the URL', required=True)
    parser.add_argument('--output', '-o', dest='output', default=False, type=str, help='output file path')
    parser.add_argument('--threads', '-t', dest='threads', default=1, type=int, help='number of threads to use')
    return parser.parse_args()

def sendRequest(args, url):
    max_retries = 3
    retry_count = 0
    response = ""
    while retry_count < max_retries:
        try:
            response = requests.get(url)
            break

        except requests.exceptions.SSLError:
            #logger(args.silent, "SSL ERROR occurred. Retrying in 10 seconds...", "error")
            time.sleep(10)
            logger(args.silent, "Sending request again to {}".format(url), "pending")
            retry_count += 1
        except requests.exceptions.ConnectTimeout:
            logger(args.silent, "Connecttion Timeout occurred. Retrying in 10 seconds...", "error")
            time.sleep(10)
            logger(args.silent, "Sending request again to {}".format(url), "pending")
            retry_count += 1

        except requests.exceptions.ConnectionError:
            logger(args.silent, "ConnectionError occurred. Retrying in 10 seconds...", "error")
            time.sleep(10)
            logger(args.silent, "Sending request again to {}".format(url), "pending")
            retry_count += 1

        except requests.exceptions.ChunkedEncodingError:
            #logger(args.silent, "ChunkedEncodingError occurred. Retrying in 30 seconds...", "error")
            time.sleep(15)
            logger(args.silent, "Sending request again to {}".format(url), "pending")
            retry_count += 1

    return response

def extract(args, response):
    if response != "":
        response_2 = []
        response_1 = response.split('\n')
        if "\n" not in response:
            for char in response_1:
                r = char.split(' ')
                for i in r:
                    x = r.index(i)
                    if ':' in i:
                        response_2.append(r[x + 1])
            return response_2

        for char in response_1:
            r = char.split(': ')
            if len(r) > 1:
                response_2.append(r[1].strip())
        return response_2

def getArchives(args):
    logger(args.silent, "Sending an HTTP request to the archive to obtain all paths for robots.txt files.", "pending")
    response = sendRequest(args, "https://web.archive.org/cdx/search/cdx?url={}/robots.txt&output=json&fl=timestamp,original&filter=statuscode:200&collapse=digest".format(args.url))

    if response != "":
        response = response.json()
        logger(args.silent, "Got the data as JSON objects.", "success")
        logger(args.silent, "Requests count : {}".format(len(response)),"success")
        if ['timestamp', 'original'] in response:
            response.remove(['timestamp', 'original'])

        if response == [] or response == None:
            return []

    return response

def getRobo(args, data):
    url = "https://web.archive.org/web/{}if_/{}".format(data[0], data[1])
    response = sendRequest(args, url)
    if response != "":
        print(response.text)
        return response.text

    return ""

def findrobo(args, archive):
    try:
        robolist = []
        if archive != []:
            logger(args.silent, "Sending HTTP requests to obtain old robots.txt files...", "pending")
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
                results = [executor.submit(getRobo, args, url) for url in archive]
            logger(args.silent, "Processing responses...", "pending")
            for result in concurrent.futures.as_completed(results):
                response = result.result()
                if response != "":
                    logger(args.silent, "Extracting all paths from robots.txt files.", "pending")
                    extracted = extract(args, response)
                    if extracted != [] and extracted != None:
                        for i in extracted:
                            if i not in robolist and i != "*":
                                robolist.append(i)
            return robolist
        
        else:
            return []

    except Exception as e:
        logger(args.silent, e, "error")

def saveToFile(args, data, name):
    logger(args.silent, "Saving results to result.txt {}".format(name), "pending")
    __path__ = os.path.dirname(os.path.realpath(__file__)) + "/{}".format(name)
    with open(__path__, "a") as f:
        for i in data:
            f.writelines("{}\n".format(i))
    logger(args.silent, "All results saved to {}".format(name), "success")


def main():
    try:
        args = setup_argparse()
        datalist = getArchives(args)
        robo = findrobo(args, datalist)
        if robo != [] and robo != None:
            if args.output:
                saveToFile(args, robo, args.output)
            logger(args.silent, "Results:", "success")
            for r in robo:
                print(r)
        else:
            logger(args.silent, "There is no results.", "error")
    except KeyboardInterrupt:
        logger(args.silent, "Program terminated by user.", "error")


if __name__ == "__main__":
    main()
