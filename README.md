# Robofinder
This script searches for old 'robots.txt' files of the given url on archive.org and returns all the old paths.
# Installation & Usage
```bash
git clone https://github.com/S7r4n6er/robofinder.git
cd robofinder
pip install -r requirements.txt
```
Run the program with the -u flag followed by the URL of the website you want to test.
```bash
python3 robofinder.py -u https://example.com
```
Save output to results.txt
```bash
python3 robofinder.py -u https://example.com -o results.txt
```
Concatenate paths with site url
```bash
python3 robofinder.py -u https://example.com -c
```
Run program in silent mode
```bash
python3 robofinder.py -u https://example.com --silent
```
You can run it with threads. My suggested number of threads is 10.
```bash
python3 robofinder.py -u https://example.com -t 10 -c -o results.txt
```
