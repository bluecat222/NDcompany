def DBcreate(db):

    cursor = db.cursor()

    sql1 = """
            CREATE TABLE IF NOT EXISTS Musicl(
                date    datetime,
                ranking    int,
                title   VARCHAR(100),
                artist  VARCHAR(130),
                lyrics  text,
                CONSTRAINT pk_id PRIMARY KEY (date, ranking)
            )default charset=utf8;
    """       # 가사 DB


    sql2 = """
            CREATE TABLE IF NOT EXISTS keyword(
                keyword  varchar(30)   not null,
                happy    int,
                enjoy    int,
                comfort  int,
                horror   int,
                angry    int,
                sad      int
            )default charset=utf8;
    """      # 감정 키워드 DB


    sql3 = """
            CREATE TABLE IF NOT EXISTS emoti(
              date    datetime,
              ranking   int,
              rank1     varchar(10),
              rank2     varchar(10),
              rank3     varchar(10),
              rank4     varchar(10),
              rank5     varchar(10),
              rank6     varchar(10),
              CONSTRAINT fk_musicl FOREIGN KEY(date, ranking) REFERENCES musicl(date, ranking)
            )default charset=utf8;
    """       # 분석 DB

    cursor.execute(sql1)
    cursor.execute(sql2)
    cursor.execute(sql3)

    db.commit()



def csv_input(db, year):
    import csv

    cursor = db.cursor()

    file = csv.reader(open("M_" + str(year) + ".csv"))
    # print(file)

    for data in file:
        sql = "INSERT INTO musicl VALUES(%s, %s, %s, %s, %s)"
        cursor.execute(sql, data)

        db.commit()