#!/usr/bin/python3
import sys
import os
import requests
from argparse import ArgumentParser

BUILT_IN_WORD_LIST = "wordlist/list.txt"

paths = []
headers = {}

def create_paths(path):
    paths.clear()
    paths.append(path)
    
    pairs = [["/", "//"], ["/.", "/./"]]
    
    leadings = ["/%2e"]
    
    trailings = ["/", "..;/", "/..;/", "%20", "%09", "%00", 
                ".json", ".css", ".html", "?", "??", 
                "?test", "#", "#test", "/."]
    
    for pair in pairs:
        paths.append(pair[0] + path + pair[1])
    
    for leading in leadings:
        paths.append(leading + path)
    
    for trailing in trailings:
        paths.append(path + trailing)
    
def create_headers(path):
    headers_overwrite = ["X-Original-URL", "X-Rewrite-URL"]
    
    headers = ["X-Custom-IP-Authorization", "X-Forwarded-For", 
            "X-Forwarded", "Forwarded-For", "X-ProxyUser-Ip",
            "X-Forward-For", "X-Remote-IP", "X-Originating-IP", 
            "Client-IP", "True-Client-IP", "Cluster-Client-IP",
            "X-Remote-Addr", "X-Client-IP", "X-Real-IP",
            "Host"]
        
    values = ["localhost", "localhost:80", "localhost:443", 
            "127.0.0.1", "127.0.0.1:80", "127.0.0.1:443", 
            "10.0.0.0", "10.0.0.1", "172.16.0.0", 
            "172.16.0.1", "192.168.1.0", "192.168.1.1"]
    
    for header in headers:
        for value in values:
            headers.append({header : value})
    
    for header in headers_overwrite:
        headers.append({header : path})

def build_final_paths(words):
    final_paths = []
    words.append("")
    for path in words:
        create_paths(path)

        for new_path in paths:
            final_paths.append(new_path)
    return final_paths

def scan(url, words):
    for path in build_final_paths(words):
        print(path)

def main():
    """
    Main program
    """
    parser = ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", help="url to target")
    parser.add_argument("-w", "--word-list", dest="word_list", help="custom word list")

    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)

    if args.word_list:
        if not os.path.exists(args.word_list):
            print("[!] No word list specified.")
            exit(1)
        else:
            with open(args.word_list, "r") as file:
                words = file.readlines()
    else:
        if not os.path.exists(BUILT_IN_WORD_LIST):
            print("[!] No word list specified.")
            exit(1)
        else:
            with open(BUILT_IN_WORD_LIST, "r") as file:
                words = [line.rstrip() for line in file]

    scan(words)

if __name__ == "__main__":
    main()