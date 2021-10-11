import time
import json

try:
    import requests
    from bs4 import BeautifulSoup as bs
except ImportError:
    exit()


def p_format(*args):
    ip_address, port, code, country, anonymity, google, https, last_checked = args
    
    return {
        "ip_address": ip_address,
        "port": port,
        "code": code,
        "country": country,
        "anonymity": anonymity,
        "google": google,
        "https": https,
        "last_checked": last_checked
    }

def load_conf():
    with open("conf.json", 'r') as json_data:
        conf = json.load(json_data)
    return conf

def generate_list(length=10, max_ms=500, timeout=1, check_google=True):
    """
    This function returns list of proxyList and returns None
    in case of failure.
    """

    # url of site containing proxyList
    if check_google: url = 'https://google.com'
    else: url = 'https://icanhazip.com/' 

    NUMBER_OF_ATTRIBUTES = 8
    valid = 0
    request_method = 'get'

    try:
        # getting html content of site..
        page = requests.get("https://free-proxy-list.net/")

    except:
        # returns None if unable to get source code of site
        print("\nFailed to get Proxy List :( \nTry Running the script again..")
        return None

    if page.status_code != 200:
        print("\nSomething Went Wrong while Getting Proxy List!\n")
        return None

    soup = bs(page.text, 'html.parser')  # creating soup object
    proxyList = []  # final list of dictionaries each containing proxy info

    table = soup.find('table')
    tbody = table.tbody if table else None  # contains rows of IPs and Stuff

    if tbody:
        infos = tbody.find_all('tr')
        for info in infos:
            if valid >= length:
                break
            # each info is a tr from tbody of table
            # extracting info from table rows
            proxy_data_temp = [i.text for i in info]
            if len(proxy_data_temp) == NUMBER_OF_ATTRIBUTES:
                # after all attributes have been retrieved
                # from a row, it's time to format it properly.
                try:
                    proxy = p_format(*proxy_data_temp)
                    print("Proxy currently being used: {}".format(proxy))

                    response = requests.request(request_method, url, proxies={'https':f"{proxy['ip_address']}:{proxy['port']}"}, timeout=timeout)

                    ms = int(response.elapsed.total_seconds()*100)
                    ms = round(ms, 2)

                    if ms > max_ms:
                        print(f'The response time was too high: {proxy} took {str(ms)}ms to response but {str(max_ms)}ms is required\n')
                        continue
                    else:
                        proxy['ms'] = ms
                        proxyList.append(proxy)
                        print(f'New proxy: {proxy}\n-> {str(ms)}ms latency\n')
                        valid += 1

                except KeyboardInterrupt:
                    print('\nStopping...')
                    if len(proxyList) <= 1:
                        exit()
                    else:
                        break

                except:
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