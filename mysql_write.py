import mysql.connector

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

#테스트 테이블 초기화
query='DELETE FROM TEST'
cursor.execute(query)
cnx.commit()

# SQL 쿼리를 실행합니다.
for i in range(100):
    query = 'INSERT INTO TEST (num) VALUES('+str(i)+')'
    cursor.execute(query)

# 변경사항을 데이터베이스에 반영 (인설트, 딜리트 등 변경사항이 있는 쿼리실행시 필수!)
cnx.commit()

# 연결을 닫습니다.
cursor.close()
cnx.close()