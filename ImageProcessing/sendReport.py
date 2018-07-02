import requests
import psycopg2
import json
settings = {}

def main():
    with open('settings.json') as jsonData:
      settings = json.load(jsonData)
      print(settings)
      jsonData.close()

    hostname = settings['postgres']['hostname']
    username = settings['postgres']['username']
    password = settings['postgres']['password']
    database = settings['postgres']['database']
    # setup DB
    conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    cursor = conn.cursor()
    cursor.execute("SELECT racknum FROM racks ORDER BY racknum ASC")
    if cursor.rowcount > 0:
        racks = cursor.fetchall()
        for rack in racks:
            url = settings['server']['host']+"/shelves/api/sendreport/0/"+rack[0]
            response = requests.request("GET", url)
            if response.status_code == '200':
                print("Sent Report For :"+rack[0])

    cursor.close()
    conn.close()

# call main function
if __name__ == "__main__":
    main()
