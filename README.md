# robofinder
This script searches for old 'robots.txt' files of the given url on archive.org and returns all the old paths.
# Installation & Usage
```bash
git clone https://github.com/S7r4n6er/robofinder.git
cd robofinder
pip install -r requirements.txt
```
Run the program with the -u flag followed by the URL of the website you want to test.
```bash
python3 robofinder.py -u example.com
```
Save output to results.txt
```bash
python3 robofinder.py -u url -o results.txt
```
Run program in silent mode
```bash
python3 robofinder.py -u url --silent
```
