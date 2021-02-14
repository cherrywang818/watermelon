import connect, psycopg2
print("import done - establishing connection")
conn = psycopg2.connect(dbname=connect.dbname, user=connect.dbuser, \
     password=connect.dbpass, host=connect.dbhost, port=connect.dbport)
print(f"connection done - {conn}")
with conn:
    cur = conn.cursor()
    cur.execute("select * from member limit 5;")
    select_result = cur.fetchall()
    print(select_result)