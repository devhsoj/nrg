# nrg
A tool used to easily generate config files for reverse proxying with nginx.

## Examples

**Reverse proxy traffic from http(s)://example.com to http://localhost:3000**
```shell
python nrg.py example.com:3000
```

**Reverse proxy traffic from multiple domains to multiple ports**
```shell
python nrg.py example.com:3000 test.example.com:4000 foobar.example.com:5000
```

## Note
This is brand new and subject to a lot of change, I basically just made it because I was tired of forgetting and looking up how to set up reverse proxying with nginx.

### Todo
- Add support for reverse proxying to a host other than localhost
- Add support for differing cert locations (as of now, it generates letsencrypt cert paths)
- Add support for differing http(s) ports
- Add support for https->https reverse proxying? (as of now just proxies https->http)
- And More...