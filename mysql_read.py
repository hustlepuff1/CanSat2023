import mysql.connector
import pandas as pd

# MySQL 서버에 연결합니다.
cnx = mysql.connector.connect(
    host='bifrost0602.duckdns.org',
    user='TEST',
    port=2024,
    password='1234',
    database='CNUDB'
)

print('접속완료')

# 커서를 생성합니다.
cursor = cnx.cursor()

# SQL 쿼리를 실행하고 결과를 Pandas DataFrame으로 읽어옵니다.
query = 'SELECT * FROM TEST'
df = pd.read_sql(query, cnx)

# DataFrame을 CSV 파일로 저장합니다.
df.to_csv('output.csv', index=False)

# 연결을 닫습니다.
cursor.close()
cnx.close()