def day_chart(db, year, S_month = 1, E_month = 12):

    import calendar  # .monthrange(year, month) : 해당년도, 해당월의 날짜수
    from bs4 import BeautifulSoup  # html 분석
    from selenium import webdriver as wd  # 크롤링 웹 접속

    cursor = db.cursor()


    driver = wd.Chrome(executable_path="NDmodule/chromedriver.exe")
    driver.implicitly_wait(3)

    url = "https://www.genie.co.kr/member/popLogin?page_rfr=https%3A//www.genie.co.kr/"  # 크롤링 웹 로그인 url
    driver.get(url)

    driver.find_element_by_name('gnb_uxd').send_keys('bluecat2222')
    driver.find_element_by_name('gnb_uxx').send_keys('kim1@3$5^')
    # ID, PW 입력

    driver.find_element_by_xpath(
        '//*[@id="f_login_layer"]/input[2]'
    ).click()
    # 로그인 버튼 클릭

    for month in range(S_month, E_month + 1):  # 차트's month
        for day in range(1, calendar.monthrange(year, month)[1] + 1):  # 차트's day

            date = str(year) + '-' + str(month) + '-' + str(day)  # 차트 날짜

            driver.get(
                "https://www.genie.co.kr/chart/top200?ditc=D&rtm=N&ymd=" + str(year) + str(month).zfill(2) + str(
                    day).zfill(2))  # 일별차트 url
            pageString = driver.page_source

            bsObj = BeautifulSoup(pageString, "html.parser")

            listClass = bsObj.find("div", {"class": "chart-date"})

            musicIDList = listClass.findAll("input")[4]["value"]  # 차트 데이터 list raw 데이터 추출

            musicID = musicIDList.split(";")  # 차트 데이터 list 전환

            rank = 1

            for ID in musicID[:1]:
                driver.get("https://www.genie.co.kr/detail/songInfo?xgnm=" + str(ID))  # 노래 url
                pageString = driver.page_source

                bsObj = BeautifulSoup(pageString, "html.parser")

                title = bsObj.find("h2", {"class": "name"}).text  # 제목 크롤링

                artist = bsObj.find("span", {"class": "value"}).text  # 가수 크롤링

                lyrics = bsObj.find("pre", {"id": "pLyrics"}).find("p").text  # 가사 크롤링

                sql = "INSERT INTO musicl VALUES(%s, %s, %s, %s, %s)"

                cursor.execute(sql, (date, rank, title.strip(), artist.strip(), lyrics.strip()))    # 크롤링 데이터 DB에 입력

                db.commit()

                rank += 1