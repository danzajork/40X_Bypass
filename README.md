# 40X Bypass
This tool attempts to bypass 401/403 responses by manipulating the URL path as well as trying different HTTP headers and verbs.

Check out `https://book.hacktricks.xyz/pentesting/pentesting-web/403-and-401-bypasses` for a list of the different techniques this tool automates.

## 40X Bypass

### Requirements
```sh
Python 3
pip
```

### Installing Python Requirements
```sh
pip install -r requirements.txt
```

### Usage information

```console
% python3 main.py
usage: main.py [-h] [-u URL] [-w WORD_LIST] [-t THREADS]

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     url to target
  -w WORD_LIST, --word-list WORD_LIST
                        custom word list
  -t THREADS, --threads THREADS
                        number of threads
```
