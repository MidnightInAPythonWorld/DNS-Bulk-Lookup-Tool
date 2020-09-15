#!/usr/bin/env python
__author__ = 'MidnightInAPythonWorld'

# Check for Python3
import sys
if sys.version_info[0] != 3:
    print("[!] This script requires Python 3")
    print("[!] Exiting script")
    exit()


# stdlib import used libraries
import threading, re, queue

#Import DNS Resolver
try:
    import dns.resolver
except:
    print("[!] This script requires DNS Python")
    print("[!] https://github.com/rthalley/dnspython")
    print("[!] pip install dnspython")
    print("[!] Exiting script")
    exit()


def open_domain_file():
    """
    Function will read in text file that has list of domains to be DNS queried.
    Function expects user input to specify text file.
    Function also runs domain names through regex to strip wildcards and check for compliant DNS names.
    """
    data = []
    wildcards = re.compile(r'\*[a-zA-Z0-9_-].+')
    non_compliant = re.compile(r'[*a-zA-Z0-9_-].+')
    print('[-] Reading in domains from file.' )
    with open(input("What is the filename contains the list of DNS to batch query: ")) as domain_file:
        for domain in domain_file:
            domain = domain.strip()
            found_wildcards = wildcards.match(domain)
            found_non_compliant = non_compliant.match(domain)
            if not found_non_compliant:
                print('[!] Non-compliant URL found in input file: ', domain )
            if found_wildcards:
                domain = domain.strip('*')
                data.append(domain)
            else:
                data.append(domain)
    return data


### Below Queuing Technique is used to store results from Threading
### https://stackoverflow.com/questions/50290226/python-how-to-get-multiple-return-values-from-a-threaded-function/50290567#50290567
### PyDocs on Queue: https://docs.python.org/3/library/queue.html#Queue.Queue

my_queue = queue.Queue()

def storeInQueue(f):
  def wrapper(*args):
    my_queue.put(f(*args))
  return wrapper


@storeInQueue
def dns_check(item):
    """
    Function uses DNS Python to find DNS results
    """
    try:
        answers = dns.resolver.query(item, 'A')
        for rdata in answers:
            dns_response = str(rdata)
            data = [item , dns_response]
            return data
    except:
        data = [item , 'query-failed']
        return data


def main():
    domains = open_domain_file()  
    results = [] 
    threads = []
    print('[-] Performing batch DNS lookup...Please wait' )
    for item in domains:
        t = threading.Thread( target=dns_check, args=(item,) )
        t.start()
        threads.append(t)
        my_data = my_queue.get()
        results.append(my_data)
    for x in threads:
        x.join()
    print('[-] Writing results to "results.csv" in current directory' )
    with open('results.csv', 'w') as output_file:
        for item in results:
            output_file.write(item[0] + ',' + item[1] + '\n')




if __name__ == "__main__":
    main()


exit()
