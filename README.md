# Robofinder

**Robofinder** is a Python script that allows you to search for and retrieve historical `robots.txt` files for any given website using Archive.org. This tool is particularly useful for security researchers and web archivists to discover previously accessible paths or directories that were once listed in a site's `robots.txt`.

## Features
- Fetch historical `robots.txt` files from Archive.org.
- Extract and display old paths or directories that were once disallowed or listed.
- Option to save the output to a file.
- Silent mode for unobtrusive execution.
- Multi-threading support to speed up the search process.

## Installation

### Using pipx (Recommended)
The easiest way to install Robofinder is using pipx:
```bash
pipx install git+https://github.com/gnomegl/robofinder-pipx.git
```

### Manual Installation
Alternatively, you can install it manually:
```bash
git clone https://github.com/gnomegl/robofinder-pipx.git
cd robofinder
pip install -r requirements.txt
```

## Usage

If installed with pipx, simply run:
```bash
robofinder -u https://example.com
```

If installed manually:
```bash
python3 robofinder.py -u https://example.com
```

### Additional Options

- **Save output to file**:
  ```bash
  robofinder -u https://example.com -o results.txt
  ```
- **Concatenate paths with site URL**:
  ```bash
  robofinder -u https://example.com -c
  ```
- **Run in debug mode**:
  ```bash
  robofinder -u https://example.com --debug
  ```
- **Multi-threading** (default recommended: 10 threads):
  ```bash
  robofinder -u https://example.com -t 10 -c -o results.txt
  ```

## Example

Running Robofinder on `example.com` and saving the result to `results.txt` with 10 threads:
```bash
robofinder -u https://example.com -t 10 -o results.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
