import sqlite3
import json
import codecs

conn = sqlite3.connect('opengeo.sqlite')
cur = conn.cursor()

cur.execute('SELECT * FROM Locais')
fhand = codecs.open('where.js', 'w', "utf-8")
fhand.write("myData = [\n")
count = 0
for row in cur :
    try: data = row[1].decode()
    except: data = row[1]
    try: js = json.loads(data)
    except: continue

    if len(js['features']) == 0: continue

    try:
        lat = js['features'][0]['geometry']['coordinates'][1]
        lng = js['features'][0]['geometry']['coordinates'][0]
        where = js['features'][0]['properties']['display_name']
        where = where.replace("'", "")
    except:
        print('Unexpected format')
        print(js)

    try :
        print(where, lat, lng)

        count = count + 1
        if count > 1 : fhand.write(",\n")
        output = "["+str(lat)+","+str(lng)+", '"+where+"']"
        fhand.write(output)
    except:
        continue

fhand.write("\n];\n")
cur.close()
fhand.close()
print(count, "Registros salvos no arquivo where.js.")
print("Abra where.html para visualizar os locais no navegador.")

