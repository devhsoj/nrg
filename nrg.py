from time import time_ns
import click


@click.command()
@click.argument('mappings', nargs=-1, required=True)
def main(mappings):
    """
    This script generates an nginx config file used for reverse proxying based on the domains passed.

    MAPPINGS is a variable length amount of arguments consisting of domain name(s) and port(s).

    Example Usage:\n

    # Reverse proxy traffic for the domain example.com to http://localhost:3000\n
    $ python nrg.py example.com:3000

    # Do the above & also route a subdomain to http://localhost:4444\n
    $ python nrg.py example.com:3000 test.example.com:4444
    """

    root_domain = None
    domains = []

    for mapping in mappings:
        domain_map = mapping.split(':')

        if ':' not in mapping or len(domain_map) != 2:
            click.echo(f'Port not specified for the mapping passed ({mapping}). Example usage: example.com:3000')
            exit(1)

        try:
            name = domain_map[0]
            port = int(domain_map[1])

            if port <= 0 or port > 65535:
                click.echo(f'Port number must be between 0 and 65535. You passed {port}.')
                exit(1)

            if not root_domain:
                if len(name.split('.')) > 2:
                    click.echo('Invalid root domain. Did you accidentally pass a subdomain as the first argument?')
                    exit(1)

                root_domain = {
                    'name': name,
                    'port': port,
                    'root': True
                }

                domains.append(root_domain)

                continue

            domains.append({
                'name': name,
                'port': port,
                'root': False
            })
        except ValueError:
            click.echo('Ports for each domain mapping have to be numbers!')
            exit(1)

    timestamp = round(time_ns() / 1_000_000)

    f = open(f'nrg-{root_domain["name"]}-{timestamp}.txt', 'w')
    f.write(f'''
server {{
    listen      80 default_server;
    listen      [::]:80 default_server;
    server_name {root_domain['name']} www.{root_domain['name']} {' '.join([domain['name'] for domain in domains if not domain['root']])};
    
    return 301  https://$host$request_uri;
}}
''')

    for domain in domains:
        f.write(f'''
server {{
    listen      443 ssl;
    listen      [::]:443 ssl;
    server_name {domain['name']}{f' www.{domain["name"]}' if domain["root"] else ''};
    
    ssl_certificate /etc/letsencrypt/live/{root_domain['name']}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{root_domain['name']}/privkey.pem;

    include /etc/nginx/default.d/*.conf;

    location / {{
        proxy_set_header X-Real-IP  $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;

        proxy_pass http://localhost:{domain["port"]};
    }}
}}
''')

    f.close()


if __name__ == '__main__':
    main()
