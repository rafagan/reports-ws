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
import re
from datetime import timedelta

from server.db import fetch_visitor, insert_visitor, insert_visitor_visit
from server.model import Visitor, VisitorVisit


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
                'datetime': entry.request_time,
                'datetime_str': entry.request_time.strftime("%Y/%m/%d, %H:%M:%S"),
                'agent': user_agent,
                'agent_checksum': hashlib.md5(user_agent.encode('utf-8')).hexdigest() if user_agent is not None else None,
                'request': entry.request_line
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
# Agentes se repetindo em horários próximos com IPs diferentes são considerados o mesmo
# Quando não existe host, o log é ignorado (Google, Hacks)
# Será considerado 30 minutos como tempo de sessão, sendo extendido em 30 minutos toda vez que o
def process_user_trails(entries):
    results = []

    # Agrupa por host
    host_groups = group_data(entries, 'host')
    for host_group in host_groups.values():
        # Entradas sem host serão ignoradas (google, hackers)
        if host_group[0]['ip'] is None:
            continue

        # Dentro do host, agrupa por agent
        agent_groups = group_data(host_group, 'agent_checksum')
        for agent_group in agent_groups.values():
            if agent_group[0]['agent'] is None:
                continue

            visitor_trail = []
            last_index = len(agent_group) - 1

            for i in range(last_index):
                visitor_trail.append(agent_group[i])
                is_session_time_exceeded_30_min = agent_group[i]['datetime'] + timedelta(minutes=30) < agent_group[i + 1]['datetime']
                is_last_one = i == last_index

                if is_session_time_exceeded_30_min or is_last_one:
                    results.append(visitor_trail)
                    visitor_trail = []

    return results


# Para cada trail
# 1- Verificar se visitante já existe
# 2- Se não existe, adicionar a Visitor e pegar registro
# 3- Se existe, pegar registro e adicionar VisitorVisit:
# a) date deve ser o primeiro horário
# b) durationSecs deve ser o tempo em segundos entre a primeira e última data
# c) isNew é descoberto a partir da existência prévia de Visitor
# d) visitorId já é conhecido
def process_visitors(trails):
    for trail in trails:
        first = trail[0]
        last = trail[-1]
        visitor_id = first['agent_checksum']
        visitor = fetch_visitor(visitor_id)
        is_new = visitor is None
        duration_secs = (last['datetime'] - first['datetime']).seconds

        if duration_secs < 15:
            continue

        if is_new:
            visitor = Visitor(id=visitor_id)
            print(f'Inserting Visitor: {visitor}')
            insert_visitor(visitor)

        visitor_visit = VisitorVisit(
            date=first['datetime'],
            duration_secs=(last['datetime'] - first['datetime']).seconds,
            is_new=is_new,
            host=first['host'],
            visitor_id=visitor_id
        )
        print(f'Inserting VisitorVisit: {visitor_visit}')
        insert_visitor_visit(visitor_visit)


# 4- Filtrar entradas contendo "produto={id}" e opcional: /api/produto/{nome}/calendario
# a) Se conseguir encontrar o nome do produto, verificando requests do mesmo grupo ou do cache salva
# b) name: Verifica se produto existe para pegar nome, senao tentar descobrir
# c) activity_type: impossivel saber
# d) Pegar data e salvar em ProductVisit
def process_products(trails):
    def crawl_product_id(request):
        result = re.match(r'\*?produto=(\d+)&\*?', request)
        return result.group(1) if result else None

    for trail in trails:
        trail = list(filter(lambda entry: 'produto' in entry['request'], trail))
        if len(trail) == 0:
            continue

        for entry in trail:
            request = entry['request']
            if 'produto=' in request:
                product_id = crawl_product_id(request)


def run():
    entries = parse_apache_log('logs/2021-09-15.log')
    trails = process_user_trails(entries)
    process_visitors(trails)
    # process_products(trails)


run()
