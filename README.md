# Robofinder

**Robofinder** is a powerful Python script designed to search for and retrieve historical `robots.txt` files from Archive.org for any given website. This tool is ideal for security researchers, web archivists, and penetration testers to uncover previously accessible paths or directories that were listed in a site's `robots.txt`.

## Features
- Fetch historical `robots.txt` files from Archive.org.
- Extract and display old paths or directories that were once disallowed or listed.
- Save results to a specified output file.
- **Silent Mode** for unobtrusive execution.
- Multi-threading support for faster processing.
- Option to concatenate extracted paths with the base URL for easy access.
- Debug mode for detailed execution logs.
- Extract old parameters from robots.txt files.

## Installation

### Using `pipx`
Install Robofinder quickly and securely using `pipx`:
```bash
pipx install git+https://github.com/Spix0r/robofinder.git
```

### Manual Installation
To install manually:
```bash
git clone https://github.com/Spix0r/robofinder.git
cd robofinder
pip install -r requirements.txt
```

## Usage

### Basic Command
If installed via `pipx`:
```bash
robofinder -u https://example.com
```

For manual installation:
```bash
python3 robofinder.py -u https://example.com
```

### Options and Examples

- **Save output to a file**:
  ```bash
  robofinder -u https://example.com -o results.txt
  ```

- **Silent Mode** (minimal output to console):
  ```bash
  robofinder -u https://example.com -s
  ```

- **Concatenate paths with the base URL**:
  ```bash
  robofinder -u https://example.com -c
  ```

- **Extract Paramters**:
  ```bash
  robofinder -u https://example.com -p
  ```

- **Enable Debug Mode**:
  ```bash
  robofinder -u https://example.com --debug
  ```

- **Multi-threading** (default: 10 threads):
  ```bash
  robofinder -u https://example.com -t 10
  ```

### Advanced Usage
Combine options for tailored execution:
```bash
robofinder -u https://example.com -t 10 -c -o results.txt -s
```

## Example Output

Running Robofinder on `example.com` with 10 threads, silent mode, and saving just the paramters to the `results.txt`:
```bash
robofinder -u https://example.com -t 10 -o results.txt -s -p
```

## Contributing

Contributions are highly welcome! If you have ideas for new features, optimizations, or bug fixes, feel free to submit a Pull Request or open an issue on the [GitHub repository](https://github.com/Spix0r/robofinder).

---
