######

# 1. Objetivo: Mostrar informações sobre visitações do ecommerce

# a) Acesso por mês (mm/yyyy)
# Histórico de visitas agrupadas por dia
# Total de visitas no mês
# Total de novos usuários
# Tempo médio de engajamento
# Receita total

# b) Acesso por produto
# Filtro por tipo de atividade
# Histórico dos 7 produtos mais acessados

######

# 2. Estudando os dados

# https://github.com/jwodder/apachelogs
# https://apachelogs.readthedocs.io/en/stable/directives.html
# http://httpd.apache.org/docs/current/mod/mod_log_config.html

# vendas.ecotrilhasserracatarinense.com:443 189.6.235.31 - - [15/Sep/2021:00:00:33 -0300] "GET /carrinho/9885 HTTP/2.0" 200 5665 "https://vendas.ecotrilhasserracatarinense.com/carrinho/9885" "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
# vendas.ecotrilhasserracatarinense.com:443 189.6.235.31 - - [15/Sep/2021:00:00:33 -0300] "GET /theme/default/assets/css/styles.css?8 HTTP/2.0" 304 56 "https://vendas.ecotrilhasserracatarinense.com/carrinho/9885" "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
# 54.189.230.128 - - [15/Sep/2021:00:05:12 -0300] "GET / HTTP/1.1" 301 512 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0"

# remote_host: %h:
# vendas.ecotrilhasserracatarinense.com:443
# vendas.ecotrilhasserracatarinense.com:443
#

# remote_logname: %l
# 189.6.235.31
# 189.6.235.31
# 54.189.230.128

# remote_user: %u
# - -
# - -
# - -

# request_time: %t
# [15/Sep/2021:00:00:33 -0300]
# [15/Sep/2021:00:00:33 -0300]
# [15/Sep/2021:00:05:12 -0300]

# request_line: "%r"
# GET /carrinho/9885 HTTP/2.0
# GET /theme/default/assets/css/styles.css?8 HTTP/2.0
# GET / HTTP/1.1

# final_status: %>s

# bytes_sent: %b

# headers_in:
# Referer: "%{Referer}i"
# User-Agent: "%{User-Agent}i"

#####

# 3. Modelagem dos dados

# Usuário: id
# Visita: data, visita_nova, duração
# Visita Produto: produto
# Produto: id, tipo_atividade
# Venda: valor

#####


def parse_apache_log(path):
    import hashlib
    entries = []

    from apachelogs import LogParser
    with open(path) as file:
        parser = LogParser("%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"")
        for entry in parser.parse_lines(file):
            user_agent = entry.headers_in['User-Agent']

            entries.append({
                'host': entry.remote_host,
                'ip': entry.remote_logname,
                # 'datetime': entry.request_time,
                'datetime_str': entry.request_time.strftime("%Y/%m/%d, %H:%M:%S"),
                # 'agent': user_agent,
                'agent_checksum': hashlib.md5(user_agent.encode('utf-8')).hexdigest() if user_agent is not None else None,
                # 'request': entry.request_line
            })

    return entries


# Conclusão: Existem ips diferentes para hosts iguais
def validate_hosts(entries):
    host_groups = {}
    for entry in entries:
        h = entry['host']
        host_groups[h] = host_groups.get(h, [])
        host_groups[h].append({
            'host': h,
            'ip': entry['ip'],
            'datetime': entry['datetime_str'],
            'checksum': entry['agent_checksum']
        })

    for host_group in host_groups.values():
        has_different_ip = len(list(filter(lambda e: host_group[0]['ip'] != e['ip'], host_group))) > 0
        if has_different_ip:
            for v in host_group:
                print(v)
            print('xxxxxxxxxxxxxxxxxxxxx')


def group_data(entries, key):
    groups = {}
    for entry in entries:
        v = entry[key]
        groups[v] = groups.get(v, [])
        groups[v].append(entry)
    return groups


# Validações:
# O log se trata de apenas um dia, então só há como identificar novos usuários
# O fato de um user agent se repetir entre dias não significa que é um antigo usuário
# Agentes se repetindo em horários muito intervalados devem significar visitas diferentes
# Agentes se repetindo em horários próximos com IPs diferentes devem ser considerados o mesmo?
# Agentes se repetindo em horários mais distantes com IPs iguais devem ser considerados o mesmo?
# Verificar situações com inexistência de host (ip None)
# Demonstrar possível tentativa de hack nos logs
def process_log_entries(entries):
    host_groups = group_data(entries, 'host')

    for host_group in host_groups.values():
        agent_group = group_data(host_group, 'agent_checksum')
        for values in agent_group.values():
            for v in values:
                print(v)
        print('xxxxxxxxxxxxx')

    # Verificar se remote_host e remote_logname é o mesmo
    # Verificar se User-Agent é o mesmo
    # Verificar se intervalo de tempo é maior que 15 minutos


def run():
    entries = parse_apache_log('logs/2021-09-15.log')
    process_log_entries(entries)


run()
