from requests.sessions import Session
from concurrent.futures import ThreadPoolExecutor
from threading import local
import signal,validators,re,datetime,argparse,time,requests


class colors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'

def logger(debug, message):
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S")
    if debug == True:
        print(colors.CYAN + "[" + colors.WARNING + "debug" + colors.CYAN + "][" + colors.ENDC + formatted_time + colors.CYAN + "] " + colors.ENDC + message)

def setup_argparse():
    parser = argparse.ArgumentParser(description="Robo Finder")
    parser.add_argument("--debug", action="store_true", default=False, help="enable debugging mode.")
    parser.add_argument('--url', '-u', dest='url', type=str, help='Give me the URL', required=True)
    parser.add_argument('--output', '-o', dest='output', default=False, type=str, help='output file path')
    parser.add_argument('--threads', '-t', dest='threads', default=10, type=int, help='number of threads to use')
    parser.add_argument('-c',action="store_true", default=False, help='Concatenate paths with site url')
    return parser.parse_args()

def extract(response):
    robots = []
    final = []
    regex = r"Allow:\s*\S+|Disallow:\s*\S+|Sitemap:\s*\S+"
    directive_regex = re.compile("(allow|disallow|user[-]?agent|sitemap|crawl-delay):[ \t]*(.*)", re.IGNORECASE)
    lines = re.findall(regex, response)
    for line in lines:
        d = directive_regex.findall(line)
        robots.append(d)
    if robots != []:
        for i in robots:
            final.append(i[0][1])
    return final

def get_all_links(args) -> list:
    logger(args.debug, "Sending an HTTP request to the archive to obtain all paths for robots.txt files.")
    try:
        obj = requests.get("https://web.archive.org/cdx/search/cdx?url={}/robots.txt&output=json&fl=timestamp,original&filter=statuscode:200&collapse=digest".format(args.url)).json()
    except:
        logger(args.debug, "Failed to obtain data from the archive. Exiting...")
        exit(1)
    url_list = []
    for i in obj:
        url_list.append("https://web.archive.org/web/{}if_/{}".format(i[0],i[1]))

    logger(args.debug, "Got the data as JSON objects.")
    logger(args.debug, "Requests count : {}".format(len(url_list)))
    if "https://web.archive.org/web/timestampif_/original" in url_list:
        url_list.remove("https://web.archive.org/web/timestampif_/original")
    return url_list
thread_local = local()

def get_session() -> Session:
    if not hasattr(thread_local,'session'):
        thread_local.session = requests.Session()
    return thread_local.session

def concatinate(args,results) -> list:
    concatinated = []
    try:
        for i in results:
            if validators.url(i) != True:
                if i != "":
                    if i[0] == "/":
                        concatinated.append(args.url+i)
                    else:
                        concatinated.append(args.url+"/"+i)
            elif validators.url(i) == True:
                concatinated.append(i)
    except Exception as e:
        logger(args.debug, "Error occurred while concatinating paths. {}".format(e))

    return concatinated
           
def fetchFiles(url:str):
    session = get_session()
    max_retries = 3
    retry_count = 0
    response = ""
    while retry_count < max_retries:
        try:
            response =  session.get(url)
            logger(args.debug, "HTTP Request Sent to {}".format(url))
            break

        except requests.exceptions.SSLError:
            time.sleep(1)
            logger(args.debug, "Sending request again to {}".format(url))
            retry_count += 1
        except requests.exceptions.ConnectTimeout:
            logger(args.debug, "Connecttion Timeout occurred. Retrying in 10 seconds...")
            time.sleep(1)
            logger(args.debug, "Sending request again to {}".format(url))
            retry_count += 1

        except requests.exceptions.ConnectionError:
            logger(args.debug, "ConnectionError occurred. Retrying in 10 seconds...")
            time.sleep(1)
            logger(args.debug, "Sending request again to {}".format(url))
            retry_count += 1

        except requests.exceptions.ChunkedEncodingError:
            logger(args.debug, "ChunkedEncodingError occurred. Retrying in 30 seconds...")
            time.sleep(5)
            logger(args.debug, "Sending request again to {}".format(url))
            retry_count += 1

    return response

def handle_sigint(signal_number, stack_frame):
    print("Keyboard interrupt detected, stopping processing.")
    raise KeyboardInterrupt()

def startProccess(urls,args) -> list:
    signal.signal(signal.SIGINT, handle_sigint)
    responses = []
    logger(args.debug, "Sending a bunch of HTTP requests to fetch all robots.txt files.")
    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            for resp in executor.map(fetchFiles,urls):
                responses.append(resp.text)
    except KeyboardInterrupt:
        logger(args.debug,"Keyboard interrupt detected, stopping processing.")
        exit(1)
    return responses

args = setup_argparse()


def main():
    start = time.time()
    logger(args.debug, "Starting the program.")
    url_list = get_all_links(args)
    resps = startProccess(url_list,args)
    results = []
    logger(args.debug, "Extracting all paths from robots.txt files.")
    end = time.time()
    logger(args.debug, "Time taken : {} seconds".format(end-start))
    for resp in resps:
        res = extract(resp)
        results = results + res
    results = list(set(results))
    if args.c == True:
        logger(args.debug, "Concatinating paths with the site url.")
        results = concatinate(args,results)
    logger(args.debug, "Total number of paths found : {}".format(len(results)))
    if args.output != False:
        logger(args.debug, "Writing the output to {}".format(args.output))
        with open(args.output,'w') as f:
            for i in results:
                f.write(i+"\n")
        logger(args.debug, "Done writing the output to {}".format(args.output))
    for i in results:
        print(i)

if __name__ == "__main__":
    main()
