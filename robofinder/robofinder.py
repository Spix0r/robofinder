import argparse
import datetime
import re
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from threading import local
import args
import requests
import validators
from requests.sessions import Session
from werkzeug.utils import secure_filename  # Added import for secure_filename

# Colors for terminal output
class Colors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'


def show_banner():
    """Displays the program banner."""
    print(Colors.CYAN + r"""
    ____        __          _____           __         
   / __ \____  / /_  ____  / __(_)___  ____/ /__  _____
  / /_/ / __ \/ __ \/ __ \/ /_/ / __ \/ __  / _ \/ ___/
 / _, _/ /_/ / /_/ / /_/ / __/ / / / / /_/ /  __/ /    
/_/ |_|\____/_____/\____/_/ /_/_/ /_/\____/\___/_/
                                """ + Colors.PURPLE + "github.com/Spix0r\n" + Colors.ENDC)


def logger(debug, message):
    """Logs messages with a timestamp."""
    if debug:
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%H:%M:%S")
        print(Colors.CYAN + f"[{Colors.WARNING}debug{Colors.CYAN}][{formatted_time}] {message}{Colors.ENDC}")


def setup_argparse():
    """Sets up the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Robo Finder")
    parser.add_argument('--silent', '-s', action="store_true", help='Suppress program output')
    if not parser.parse_known_args()[0].silent:
        show_banner()

    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    parser.add_argument('--url', '-u', required=True, help='Target URL')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--threads', '-t', default=10, type=int, help='Number of threads to use')
    parser.add_argument('-c', action="store_true", help='Concatenate paths with site URL')

    return parser.parse_args()


def extract(response):
    """Extracts relevant directives from a robots.txt response."""
    robots = []
    final = []
    regex = r"Allow:\s*\S+|Disallow:\s*\S+|Sitemap:\s*\S+"
    directive_regex = re.compile("(allow|disallow|user-?agent|sitemap|crawl-delay):[ 	]*(.*)", re.IGNORECASE)
    lines = re.findall(regex, response)
    for line in lines:
        d = directive_regex.findall(line)
        robots.append(d)

    for i in robots:
        final.append(i[0][1])
    return final


def get_all_links(args):
    """Fetches all robots.txt files from the Wayback Machine."""
    logger(args.debug, "Sending an HTTP request to fetch all robots.txt paths from the archive.")
    try:
        response = requests.get(
            f"https://web.archive.org/cdx/search/cdx?url={args.url}/robots.txt&output=json&fl=timestamp,original&filter=statuscode:200&collapse=digest").json()
    except requests.RequestException:
        logger(args.debug, "Failed to obtain data from the archive. Exiting...")
        sys.exit(1)

    url_list = [f"https://web.archive.org/web/{i[0]}if_/{i[1]}" for i in response]

    logger(args.debug, f"Received {len(url_list)} robots.txt paths from the archive.")

    if "https://web.archive.org/web/timestampif_/original" in url_list:
        url_list.remove("https://web.archive.org/web/timestampif_/original")

    if not url_list:
        logger(args.debug, "No robots.txt files found. Exiting...")
        sys.exit(1)

    return url_list


thread_local = local()


def get_session() -> Session:
    """Returns a session object for making HTTP requests."""
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session


def concatenate_paths(args, results) -> list:
    """Concatenates paths with the site URL if necessary."""
    concatenated = []
    for path in results:
        if validators.url(path):
            concatenated.append(path)
        else:
            path = path.lstrip('/')
            concatenated.append(f"{args.url}/{path}")
    return concatenated


def fetch_file(url: str) -> str:
    """Fetches the content of a URL with retries."""
    session = get_session()
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = session.get(url)
            logger(args.debug, f"HTTP Request Sent to {url}")
            return response.text
        except (requests.exceptions.RequestException, requests.exceptions.SSLError) as e:
            logger(args.debug, f"Error occurred: {e}. Retrying...")
            time.sleep(1)
            retry_count += 1

    return ""


def handle_sigint(signal_number, stack_frame):
    """Handles keyboard interrupts gracefully."""
    print("Keyboard interrupt detected, stopping processing.")
    raise KeyboardInterrupt()


def start_process(urls, args):
    """Starts the process of fetching all robots.txt files using multiple threads."""
    signal.signal(signal.SIGINT, handle_sigint)
    responses = []
    logger(args.debug, "Sending HTTP requests to fetch robots.txt files.")

    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            for resp in executor.map(fetch_file, urls):
                if resp:
                    responses.append(resp)
    except KeyboardInterrupt:
        logger(args.debug, "Process interrupted by user.")
        sys.exit(1)

    return responses


def main():
    """Main function to execute the program."""
    start = time.time()
    logger(args.debug, "Starting the program.")

    # Fetch the URLs
    url_list = get_all_links(args)

    # Fetch all robots.txt files
    responses = start_process(url_list, args)

    # Extract the paths from the robots.txt files
    results = []
    logger(args.debug, "Extracting paths from robots.txt files.")
    for resp in responses:
        results.extend(extract(resp))

    results = list(set(results))  # Remove duplicates

    if not results:
        logger(args.debug, "No paths found. Exiting...")
        sys.exit(1)

    # Concatenate paths with URL if required
    if args.c:
        logger(args.debug, "Concatenating paths with the site URL.")
        results = concatenate_paths(args, results)

    logger(args.debug, f"Total number of paths found: {len(results)}")

    # Write results to output file if specified
    if args.output:
        try:
            # Sanitize the output path to ensure it's safe using secure_filename
            sanitized_path = secure_filename(args.output)  # Fix applied here
            logger(args.debug, f"Writing the output to {sanitized_path}")

            # Open the sanitized path and write the results to it
            with open(sanitized_path, 'w') as f:
                for path in results:
                    f.write(f"{path}\n")

            logger(args.debug, f"Finished writing the output to {sanitized_path}")
        except ValueError as e:
            # Handle invalid output path (path traversal error)
            logger(args.debug, str(e))
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    args = setup_argparse()
    main()
