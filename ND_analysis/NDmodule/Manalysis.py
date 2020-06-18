
import pandas as pd
from konlpy.tag import Komoran

def samerank(db, emotion_dict):     # Null값 전처리 파일 출력 - 1,2등 동순위 전처리

    komoran = Komoran()

    cursor = db.cursor()

    emotion = ['happy', 'enjoy', 'comfort', 'horror', 'angry', 'sad']


    sql = "SELECT DISTINCT title, artist, lyrics FROM musicl WHERE (DATE, ranking) IN (SELECT DATE, ranking FROM emoti_test WHERE rank1 IS NULL)"
    cursor.execute(sql)
    null_data = cursor.fetchall()
    null_data = pd.DataFrame(null_data, columns=['제목', '가수', '가사'])

    null_data_rating = pd.DataFrame(columns=['제목', '가수', '순위', '수치'])

    for title, singer, lyrics in null_data.values:

        # 형태소 나누기
        lyrics = lyrics.replace('\n', '')
        words_temp = komoran.morphs(lyrics)

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
        value = lyrics_emotion[0].sort_values(ascending=False).values

        null_data_rating = null_data_rating.append({'제목': title.strip(), '가수': singer, '순위': list(rating), '수치': list(value)}, ignore_index=True)

    null_data_rating.to_excel('data/samepointSong.xlsx', encoding = 'utf-8')



def preprocess_DB(db, path):      # 전처리 파일 DB 삽입

    cursor = db.cursor()

    data = pd.read_excel(path)
    data.drop('Unnamed: 0', axis = 1,inplace = True)
    data.head()

    for title, artist, ranking in data.iloc[:, :3].values:
        new_ranking = []

        for i in range(6):
            new_ranking.append(ranking.split("'")[2 * i + 1])

        sql = '''
        UPDATE emoti_test SET rank1 = %s, rank2 = %s, rank3 = %s, rank4 = %s, rank5 = %s, rank6 = %s
        WHERE (date, ranking) in (SELECT date, ranking FROM musicl 
        where title = %s and artist = %s);
        '''
        cursor.execute(sql, (
        new_ranking[0], new_ranking[1], new_ranking[2], new_ranking[3], new_ranking[4], new_ranking[5], title, artist))
        db.commit()