# Robofinder

**Robofinder** is a Python script that allows you to search for and retrieve historical `robots.txt` files for any given website using Archive.org. This tool is particularly useful for security researchers and web archivists to discover previously accessible paths or directories that were once listed in a site's `robots.txt`.

## Features
- Fetch historical `robots.txt` files from Archive.org.
- Extract and display old paths or directories that were once disallowed or listed.
- Option to save the output to a file.
- Silent mode for unobtrusive execution.
- Multi-threading support to speed up the search process.

## Installation

Clone the repository and install the required dependencies:
```bash
git clone https://github.com/S7r4n6er/robofinder.git
cd robofinder
pip install -r requirements.txt
```

## Usage

Run the program by providing a URL with the `-u` flag:
```bash
python3 robofinder.py -u https://example.com
```

### Additional Options

- **Save output to file**:
  ```bash
  python3 robofinder.py -u https://example.com -o results.txt
  ```
- **Concatenate paths with site URL**:
  ```bash
  python3 robofinder.py -u https://example.com -c
  ```
- **Run in silent mode** (no console output):
  ```bash
  python3 robofinder.py -u https://example.com --silent
  ```
- **Multi-threading** (default recommended: 10 threads):
  ```bash
  python3 robofinder.py -u https://example.com -t 10 -c -o results.txt
  ```

## Example

Running Robofinder on `example.com` and saving the result to `results.txt` with 10 threads:
```bash
python3 robofinder.py -u https://example.com -t 10 -o results.txt
```
