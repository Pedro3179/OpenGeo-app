import urllib.request, urllib.parse, urllib.error
import http
import sqlite3
import json
import time
import ssl
import sys

# https://py4e-data.dr-chuck.net/opengeo?q=Ann+Arbor%2C+MI
serviceurl = 'https://py4e-data.dr-chuck.net/opengeo?'

# Additional detail for urllib
# http.client.HTTPConnection.debuglevel = 1

conn = sqlite3.connect('opengeo.sqlite')
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS Locais (endereco TEXT, geodata TEXT)')

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Cria um file handle para iterar a lista de endereços
filehandle=open('where.data')
count=0
nofound=0

# Itera os endereços do arquivo where.data
for line in filehandle:
    if count>99:
        print('Você achou 100 localizações. Reinicie para procurar mais.')
        break

# Seleciona o registro da coluna geodata em que o registro da coluna endereco case com o endereço do arquivo 
    address=line.strip()
    print('')
    cur.execute('SELECT geodata FROM Locais WHERE endereco=?', (memoryview(address.encode()), ))

# Tenta retornar o que foi selecionado anteriormente. Se não conseguir prossegue para o urlencode e procura no proxy do GEOAPIFY
    try:
        data=cur.fetchone()[0]
        print('Encontrado no banco de dados:', address)
        continue
    except:
        pass

    parms = dict()
    parms['q'] = address

# Prepara a url para conectar e fazer request (url encode).
    url = serviceurl + urllib.parse.urlencode(parms)

    print('Retrieving', url)
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()
    print('Retrieved', len(data), 'characters')
    count = count + 1

# Dá parse no arquivo json recebido
    try:
        js = json.loads(data)
    except:
        print(data)  # Dar print para verificar se o unicode não causou erros.
        continue
# Debug
    if not js or 'features' not in js:
        print('==== Download error ===')
        print(data)
        break

    if len(js['features']) == 0:
        print('==== Object not found ====')
        nofound = nofound + 1

# Acrescentamos o endereço na coluna endereco e os dados em json na coluna geodata 
    cur.execute ('''INSERT INTO Locais (endereco, geodata)
                 VALUES (?,?)''', (memoryview(address.encode()), memoryview(data.encode())))
    conn.commit() #commit subscreve na coluna o que foi alterado no cursor

# A cada 10 paramos e esperamos alguns segundos para o API não nos dar rate limit 
    if count % 10 == 0 : #% é o operador mod, que retorna o resto da divisão
        print('Pausing for a bit...')
        time.sleep(2)

if nofound > 0:
    print('Número de locais não encontrados:', nofound)

print("Abra geodump.py para ler os dados do banco de dados e vizualiá-los no mapa.")

