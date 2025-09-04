import sqlite3
import json
import codecs

# Connects to the database. If the file doesn't exist, it creates one.
conn = sqlite3.connect('opengeo.sqlite')
cur = conn.cursor()

# Creates and a where.js file and writes into it.
cur.execute('SELECT * FROM Locais')
fhand = codecs.open('where.js', 'w', "utf-8")
fhand.write("myData = [\n")

# Creates a count variable
count = 0

# Iterates through the cursor and parse the data.
for row in cur :
    try: data = row[1].decode()
    except: data = row[1]
    try: js = json.loads(data)
    except: continue

    if len(js['features']) == 0: continue

# Extract the latitude, longitude and address name.
    try:
        lat = js['features'][0]['geometry']['coordinates'][1]
        lng = js['features'][0]['geometry']['coordinates'][0]
        where = js['features'][0]['properties']['display_name']
        where = where.replace("'", "")
    except:
        print('Unexpected format')
        print(js)

# Skips one line and writes the data in the where.js.
    try :
        print(where, lat, lng)

        count = count + 1
        if count > 1 : fhand.write(",\n")
        output = "["+str(lat)+","+str(lng)+", '"+where+"']"
        fhand.write(output)
    except:
        continue

# Skips one line and writes a closing square bracket.
fhand.write("\n];\n")
cur.close()
fhand.close()

# Instructions on how to continue.
print(count, "Registros salvos no arquivo where.js.")
print("Abra where.html para visualizar os locais no navegador.")

