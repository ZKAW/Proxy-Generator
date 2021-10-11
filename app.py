print('''Modules:

[0]: https://free-proxy-list.net/
[1]: https://sslproxies.org/
''')

module = int(input('Module index: '))

if module == 0:
    from modules import free_proxy_list
elif module == 1:
    from modules import sslproxies