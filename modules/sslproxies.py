import requests
import webbrowser
import json
import time

from bs4 import BeautifulSoup
from random import choice


def load_conf():
    with open('conf.json', 'r') as json_data:
        conf = json.load(json_data)

    return conf

def proxy_generator():
    response = requests.get("https://sslproxies.org/")
    soup = BeautifulSoup(response.content, 'html5lib')
    proxy = {'https': choice(list(map(lambda x:x[0]+':'+x[1], list(zip(map(lambda x:x.text, soup.findAll('td')[::8]), map(lambda x:x.text, soup.findAll('td')[1::8]))))))}
    
    return proxy

def data_scraper(request_method='get', url='https://icanhazip.com/', **kwargs): # Get page content through proxy server
    while True:
        try:
            proxy = proxy_generator()
            print("Proxy currently being used: {}".format(proxy))
            response = requests.request(request_method, url, proxies=proxy, timeout=5, **kwargs)
            break

        except KeyboardInterrupt:
            print('\nStopping...')
            exit()

        except:
            print("Connection error, looking for another proxy")
            pass

    return response

def generate_list(length=10, max_ms=500, timeout=1, check_google=True, **kwargs):
    if check_google: url = 'https://google.com/'
    else: url = 'https://icanhazip.com/'

    request_method = 'get'
    valid = 0
    proxyList = []

    print(f'Checking proxy with url: {url}\n')

    while valid < length:
        try:
            proxy = proxy_generator() # Fetch a proxy address

            print("Proxy currently being used: {}".format(proxy))
            response = requests.request(request_method, url, proxies=proxy, timeout=timeout, **kwargs)

            ms = int(response.elapsed.total_seconds()*100)
            ms = round(ms, 2)

            proxy['ms'] = ms

            if ms > max_ms: # Set max response time to avoid laggy proxies
                print(f'The response time was too high: {proxy} took {str(ms)}ms to response but {str(max_ms)}ms is required\n')
                continue
            else: # Proxy is ready to work, push it in success list
                proxyList.append(proxy)
                print(f'New proxy: {proxy}\n-> {str(ms)}ms latency\n')
                valid += 1

        except KeyboardInterrupt:
            print('\nStopping...')
            if len(proxyList) <= 1:
                exit()
            else:
                break

        except: # Could not connect to proxy server
            print("Connection error, looking for another proxy\n")
            pass

        print(f'Valid proxy: {str(valid)}/{str(length)}\n')

    # Save results into json file

    if len(proxyList) >= 1:
        current_time = time.strftime("%Y-%m-%d-%H_%M")
        output_dir = f'output\\proxy_{current_time}.json'
        with open(output_dir, 'w') as f:
            json.dump(proxyList, f, sort_keys=True, indent=4)
        print(f'\nFinished processing proxy list. Results saved in {output_dir}\n')

    else:
        print('\nFinished processing proxy list, but no proxy were found.')
  
    return proxyList

conf = load_conf()

print(generate_list(length=conf['length'],
                    max_ms=conf['max_ms'],
                    timeout=conf['timeout'],
                    check_google=conf['check_google']
                    ))