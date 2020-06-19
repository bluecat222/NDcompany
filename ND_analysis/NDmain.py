# ND 모듈
from NDmodule import DB                 # DB 생성, csv 입력
from NDmodule import Mcrawling          # 크롤링 DB 입력
from NDmodule import Manalysis          # 분석 동순위 전처리

# 분석 용 모듈

from konlpy.tag import Komoran  # 형태소 분석
import pymysql                  # DB 접속
import re                       # 팝송 제거 정규표현식
import pandas as pd
komoran = Komoran()

# 오류 class
class AllZeroError(Exception):
    pass

class FirstSecondSameError(Exception):
    pass


db = pymysql.connect(host='192.168.0.4', port=3306,
                         user='USER53', password='1111',
                         db='mcrawling', charset='utf8')    # DB 연결
cursor = db.cursor()

# DB.csv_input(db, 2015)
# DB.DBcreate(db)
# Mcrawling.day_chart(db, 2020)
Mcrawling.rank_gap(db, 2020, 5, 5) # 순위 격차 

# 분석 기간 입력
start = 20150101
end = 20150102


# DB에서 가사 뽑기

sql = "select * from musicl where date between %s and %s"
cursor.execute(sql, (start, end))
datas = cursor.fetchall()

lyrics_data = pd.DataFrame(datas, columns=['날짜', '순위', '제목', '가수', '가사'])


# DB에서 감정 뽑기

emotion = ['happy', 'enjoy', 'comfort', 'horror', 'angry', 'sad']
emotion_dict = {}

for emo in emotion:     # 각 감정의 keyword 불러오기

    sql = 'select upper(keyword) from keyword where %s = 1' %emo
    cursor.execute(sql)
    keyword = cursor.fetchall()
    values = [i[0] for i in keyword]     # 튜플 형태 -> 리스트
    emotion_dict[emo] = values            # 감정 dict안에 삽입

# 분석 시작
for title, date, ranking, lyrics in lyrics_data[['제목', '날짜', '순위', '가사']].values:
    try:
        if not bool(re.search("[가-힣]", lyrics)):    # 팝송 필터링
           continue

        # 형태소 나누기
        lyrics = lyrics.replace('\n', '')
        words_temp = komoran.morphs(lyrics.upper())

        # 6개의 감정 섹션
        happy = 0
        enjoy = 0
        comfort = 0
        angry = 0
        horror = 0
        sad = 0

        # 가사의 감성 분석
        lyrics_emotion = pd.DataFrame(index=emotion)

        for word in words_temp:
            if word in emotion_dict['happy']: happy += 1
            if word in emotion_dict['enjoy']: enjoy += 1
            if word in emotion_dict['comfort']: comfort += 1
            if word in emotion_dict['angry']: angry += 1
            if word in emotion_dict['horror']: horror += 1
            if word in emotion_dict['sad']: sad += 1

        # 어떤 감성이 더 많이 나왔는지 정렬
        result_emotion = [happy, enjoy, comfort, angry, horror, sad]
        lyrics_emotion[0] = result_emotion
        rating = lyrics_emotion[0].sort_values(ascending=False).index
        rating_values = lyrics_emotion[0].sort_values(ascending=False).values

        ## 감정 순위
        # 모든 감정이 0일 때
        if rating_values[0] == 0:
            raise AllZeroError

        # 1순위와 2순위의 감정 빈도가 같을 때
        if rating_values[0] == rating_values[1]:
            raise FirstSecondSameError

        # 나머지 다~
        sql = 'insert into emoti_test values(%s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (str(date), ranking, rating[0], rating[1], rating[2], rating[3], rating[4], rating[5]))
        db.commit()


    except AllZeroError as err:
        print('모든 수치가 0입니다.')
        print(title, ':', err)
        sql = 'insert into emoti_test values(%s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (str(date), ranking, 0, 0, 0, 0, 0, 0))
        db.commit()

    except FirstSecondSameError as err:
        print('1순위와 2순위가 같습니다.')
        print(title, ':', err)
        sql = 'insert into emoti_test (date, ranking) values(%s, %s)'
        cursor.execute(sql, (str(date), ranking))
        db.commit

    except Exception as err:
        print(err)
        break

Manalysis.samerank(db, emotion_dict)                            # Null값 전처리 파일 출력 - 1,2등 동순위 전처리
Manalysis.preprocess_DB(db, 'data/samepointSong_수정.xlsx')      # 전처리 파일 DB 삽입

db.close()
