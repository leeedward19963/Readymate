from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for, \
    abort  # https://m.blog.naver.com/dsz08082/222025157731 - 특정 ip 차단from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import random
import math
import time
from time import localtime, strftime
import json
import numpy as np
import pprint
import requests
import os

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

# client = MongoClient('localhost', 27017)
client = MongoClient('3.37.246.218', 27017, username="readymate", password="readymate1!")
db = client.RM_FLASK


@app.route('/ADMIN')
def admin_home():
    return redirect(url_for("ADMIN_mentor_list"))


@app.route('/ADMINISTER/withdraw_list')
def ADMIN_withdraw_list():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if payload['admin'] == 'yes':
        mynickname = payload['nickname']
        login_time = payload['login_time']

        withdraw_all = db.withdraw.find()

        return render_template('ADMIN_withdraw_list.html', mynickname=mynickname, login_time=login_time,
                               withdraw_all=withdraw_all)
    else:
        return redirect(url_for("login"))


@app.route('/ADMINISTER/mentor_list')
def ADMIN_mentor_list():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print (payload['admin'])

    if payload['admin'] == 'yes':
        mynickname = payload['nickname']
        login_time = payload['login_time']

        mentor_all = db.mentor.find()

        return render_template('ADMIN_mentor_list.html', mynickname=mynickname, login_time=login_time,
                               mentor_all=mentor_all)
    else:
        return redirect(url_for("login"))


@app.route('/proxy_in/<number>', methods=['POST'])
def proxy_in(number):
    find_mentor = db.mentor.find_one({'number': int(number)})
    nickname = find_mentor['nickname']
    id = find_mentor['phone']
    payload = {
        'admin': 'no',
        'number': int(number),
        'id': id,
        'nickname': nickname,
        'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

    return jsonify({'result': 'success', 'token': token})


@app.route('/ADMINISTER/menti_list')
def ADMIN_menti_list():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if payload['admin'] == 'yes':
        mynickname = payload['nickname']
        login_time = payload['login_time']

        menti_all = db.menti.find()

        return render_template('ADMIN_menti_list.html', mynickname=mynickname, login_time=login_time,
                               menti_all=menti_all)
    else:
        return redirect(url_for("login"))


@app.route('/ADMINISTER/confirm/<int:number>', methods=['POST'])
def ADMIN_mentor_confirm(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print(number)
    if payload['admin'] == 'yes':
        univ = request.form['univ']
        major = request.form['major']
        num = request.form['num']

        find_mentor = db.mentor_info.find_one({'number': number})
        univ_arr = [univ]
        major_arr = [major]
        type_arr = ['']
        num_arr = [num]
        verified_arr = ['yes']


        info_doc = {
            'mentor_univ': univ_arr,
            'mentor_major': major_arr,
            'mentor_type': type_arr,
            'mentor_number': num_arr,
            'mentor_verified': verified_arr
        }
        db.mentor_info.update_one({'number': number}, {'$set': info_doc})

        #파일 실제 삭제
        real = db.mentor.find_one({'number':number})['univAttending_file_real']
        os.remove(f'static/{real}')
        doc = {
            "univAttending_file_real": ""
        }

        db.mentor.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("login"))


@app.route('/ADMINISTER/accepted/<number>', methods=['POST'])
def ADMIN_mentor_accepted(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print(number)
    if payload['admin'] == 'yes':
        doc = {
            "univAccepted_file_real": ""
            # 나중에는 실제 path도 지워버려야
        }
        print(doc)
        db.mentor.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("login"))


@app.route('/ADMINISTER/<status>/<nickname>')
def ADMIN_user_view(status, nickname):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if payload['admin'] == 'yes':
        mynickname = payload['nickname']
        login_time = payload['login_time']

        if status == 'mentor':
            mentor_info = db.mentor.find_one({'nickname': nickname})
            mentor_num = int(mentor_info['number'])
            mentorinfo_info = db.mentor_info.find_one({'number': mentor_num})
            recordpaper = db.recordpaper.find_one({'number': mentor_num})
            return render_template('ADMIN_mentor_view.html', mynickname=mynickname, login_time=login_time,
                                   mentor_info=mentor_info, mentorinfo_info=mentorinfo_info, recordpaper=recordpaper)

        else:
            menti_info = db.menti.find_one({'nickname': nickname})
            return render_template('ADMIN_menti_view.html', mynickname=mynickname, login_time=login_time,
                                   menti_info=menti_info)
    else:
        return redirect(url_for("login"))


@app.route('/ADMINISTER/univ_post/<number>', methods=['POST'])
def ADMIN_univ_post(number):
    print(number)
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    if payload['admin'] == 'yes':

        univArray = request.form["univArray_give"]
        majorArray = request.form["majorArray_give"]
        typeArray = request.form["typeArray_give"]
        numArray = request.form["schoolNumArray_give"]
        verifiedArray = request.form["verifiedArray_give"]

        doc = {
            "mentor_univ": univArray.split(','),
            "mentor_major": majorArray.split(','),
            "mentor_type": typeArray.split(','),
            "mentor_number": numArray.split(','),
            "mentor_verified": verifiedArray.split(',')
        }
        print(doc)
        db.mentor_info.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})
    else:
        return redirect(url_for("login"))


@app.route('/ADMINISTER/recordpaper_chart_array/<number>', methods=['POST'])
def recordpaper_chart_array(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if payload['admin'] == 'yes':
        chartJsArray_1 = request.form["chartJsArray_1"].split(',')
        print(chartJsArray_1)
        chartJsArray_2 = request.form["chartJsArray_2"].split(',')
        print(chartJsArray_2)
        chartJsArray_3 = request.form["chartJsArray_3"].split(',')
        print(chartJsArray_3)
        chartJsArray_4 = request.form["chartJsArray_4"].split(',')
        print(chartJsArray_4)
        chartJsArray = [chartJsArray_1, chartJsArray_2, chartJsArray_3, chartJsArray_4]
        print(chartJsArray)

        doc = {
            "chart_js_array": chartJsArray
        }

        db.recordpaper.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("login"))


@app.route('/ADMINISTER/recordpaper_save/<number>', methods=['POST'])
def recordpaper_save(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if payload['admin'] == 'yes':
        awards = request.form["awards"]
        pages = request.form["pages"]
        volunteer_hours = request.form["volunteer_hours"]
        print(awards)
        print(pages)
        print(volunteer_hours)

        doc = {
            "awards": awards,
            "pages": pages,
            "volunteer_hours": volunteer_hours
        }

        db.recordpaper.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("login"))


@app.route('/ADMINISTER/rec_remove/<int:number>', methods=['POST'])
def rec_remove(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print(number)
    if payload['admin'] == 'yes':
        doc = {
            "record_file_real": ""
            # 나중에는 실제 path도 지워버려야
        }
        print(doc)
        db.mentor.update_one({'number': int(number)}, {'$set': doc})
        time_now = datetime.now()
        now_in_form = time_now.strftime('%Y%m%d, %H:%M:%S')
        alert={
            "to_status": "mentor",
            "to_number": number,
            "category": "생활기록부가",
            "which_data": "내",
            "action": "등록되었습니다. 코멘트를 입력해주세요!",
            "when": now_in_form,
            "from_nickname": "레디메이트",
            "from_image": "/favicon.png"
        }
        db.alert.insert_one(alert)
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("login"))


@app.route('/ADMINISTER/idcard_remove/<number>', methods=['POST'])
def idcard_remove(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print(number)
    if payload['admin'] == 'yes':
        doc = {
            "idcard_file_real": ""
            # 나중에는 실제 path도 지워버려야
        }
        print(doc)
        db.mentor.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("login"))


@app.route('/ADMINISTER/mentor/yield/<nickname>')
def ADMIN_mentor_yield(nickname):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if payload['admin'] == 'yes':
        mynickname = payload['nickname']
        login_time = payload['login_time']

        mentor_info = db.mentor.find_one({'nickname': nickname})
        mentor_num = int(mentor_info['number'])
        mentorinfo_info = db.mentor_info.find_one({'number': mentor_num})
        recordpaper = db.recordpaper.find_one({'number': mentor_num})
        print(recordpaper)
        resume = db.resume.find_one({'number': mentor_num})
        print(resume)

        return render_template('ADMIN_mentor_yield.html', mynickname=mynickname, login_time=login_time,
                               mentor_info=mentor_info, mentorinfo_info=mentorinfo_info, recordpaper=recordpaper,
                               resume=resume)
    else:
        return redirect(url_for("login"))


@app.route('/ADMINISTER/carousel')
def ADMIN_carousel():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    if payload['admin'] == 'yes':
        return render_template('ADMIN_carousel.html')
    else:
        return redirect(url_for("login"))


@app.route('/')
def home():
    # token_receive = request.cookies.get('mytoken')
    # try:
    #     payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    #     menti_info = db.menti.find_one({"phone": payload["id"]}) or db.menti.find_one({"email": payload["id"]})
    #     mentor_info = db.mentor.find_one({"phone": payload["id"]}) or db.mentor.find_one({"email": payload["id"]})
    #     return render_template('index.html', menti_info=menti_info, mentor_info=mentor_info)
    # except jwt.ExpiredSignatureError:
    #     return redirect(url_for("index", msg="로그인 시간이 만료되었습니다."))
    # except jwt.exceptions.DecodeError:
    #     return redirect(url_for("index", msg="로그인 정보가 존재하지 않습니다."))
    return redirect(url_for("index"))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/finish_register_menti')
def finish_register_menti():
    msg = request.args.get("msg")
    return render_template('finish_register_menti.html', msg=msg)


@app.route('/finish_register_mentor')
def finish_register_mentor():
    msg = request.args.get("msg")
    return render_template('finish_register_mentor.html', msg=msg)


@app.route('/register')
def register():
    msg = request.args.get("msg")
    return render_template('register.html', msg=msg)


@app.route('/recordpaper/<int:number>', methods=['GET'])
def recordpaper(number):

    token_receive = request.cookies.get('mytoken')

    recordpaper_info = db.recordpaper.find_one({"number": number})
    mentorinfo = db.mentor_info.find_one({"number": number})
    mentor = db.mentor.find_one({"number": number})
    if db.recordpaper.find_one({'number': number})['chart_js_array'] != []:
        recordpaper_cnt = 1
    else:
        recordpaper_cnt = 0
    data_number = recordpaper_cnt + db.resume.count({"number": number}) + db.story.count({"number": number})

    following = db.followed.find_one({"number": number})
    mentor_follower = following['follower']

    # other data(resume)
    resume_all = list(db.resume.find({'number': number, 'release': 'sell'}, {'_id': False}))
    # (resume) like-reply count
    resume_array = []
    for resume in resume_all:
        if db.like.find_one({'number': number, 'category': 'resume', 'time': resume['time']}):
            resume_like = len(
                db.like.find_one({'number': number, 'category': 'resume', 'time': resume['time']})['who'])
        else:
            resume_like = 0
        if db.reply.find_one({'number': number, 'category': 'resume', 'time': resume['time']}):
            resume_reply = str(
                db.reply.find_one({'number': number, 'category': 'resume', 'time': resume['time']})[
                    'reply']).count('일')
        else:
            resume_reply = 0
        resume_array.append([resume, resume_like, resume_reply])
    # other data(story)
    story_all = list(db.story.find({'number': number}, {'_id': False}))
    # (story) like-reply count
    story_array = []
    for story in story_all:
        if db.like.find_one({'number': number, 'category': 'story', 'time': story['time']}):
            story_like = len(
                db.like.find_one({'number': number, 'category': 'story', 'time': story['time']})['who'])
        else:
            story_like = 0
        if db.reply.find_one({'number': number, 'category': 'story', 'time': story['time']}):
            story_reply = str(db.reply.find_one({'number': number, 'category': 'story', 'time': story['time']})[
                                  'reply']).count('일')
        else:
            story_reply = 0
        story_array.append([story, story_like, story_reply])

    like_info = db.like.find_one({"number": int(number), "category": "recordpaper"})
    like_count = len(like_info["who"])

    reply_info = db.reply.find_one({"number": int(number), "category": "recordpaper"})
    reply_count = str(reply_info['reply']).count('일')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # me information
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        myFeed = (number == payload["number"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False
        if not myFeed:
            has = request.args.get('has')
            if (has != 'pass') and (has != 'buy'):
                return redirect(url_for("home"))

        if [status, int(me_info['number'])] in mentor_follower:
            followed = 'True'
        else:
            followed = 'False'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number1 in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number1)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number1)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number0 in action_mentor:
            info2 = db.mentor.find_one({"number": int(number0)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number0)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        if payload['number'] in db.like.find_one({"number": number, "category": "recordpaper"})['who']:
            like_check = 'like'
        else:
            like_check = 'unlike'
        # print('like_check: ',like_check)

        if payload['number'] in db.bookmark.find_one({"number": number, "category": "recordpaper"})['who']:
            bookmark_check = 'mark'
        else:
            bookmark_check = 'unmark'
        # print(bookmark_check)

        if not myFeed:
            now = datetime.now()
            now_in_form = now.strftime("%Y/%m/%d, %H:%M:%S")
            now_pay_status = db.menti.find_one({'number':payload['number']})['pass']
            if db.pay.find_one({'client_number':payload['number'], 'number':number, 'category':'recordpaper'}) is not None:
                buy_info = db.pay.find_one({'client_number':payload['number'], 'number':number, 'category':'recordpaper'})
                exp = buy_info['exp_time']
                exp_in_form = datetime.strptime(exp, "%Y-%m-%d %H:%M:%S")

                if exp_in_form > now:
                    buythis = 'yes'
                else:
                    buythis = 'no'
            else:
                buythis = 'no'

            if now_pay_status != '':
                now_pay_status = 'streaming'
            elif buythis == 'yes':
                now_pay_status = 'buy'
            else:
                return redirect(url_for("home"))

            time = db.visit.find_one(
                {"to_number": int(number), "from_number": payload["number"], "category": 'recordpaper'})
            if time is None:
                visit_doc = {
                    "to_number": number,
                    "category": 'recordpaper',
                    "from_number": payload["number"],
                    "current_time": [now_in_form],
                    "current_status":[now_pay_status]
                }
                db.visit.insert_one(visit_doc)
                db.recordpaper.update_one({"number": int(number)}, {"$inc": {'visit': 1}})
            else:
                check = time['current_time']
                recent_time = time["current_time"][-1]
                get_time = datetime.strptime(recent_time, "%Y/%m/%d, %H:%M:%S")
                date_diff = now - get_time
                if date_diff.seconds > 3600:
                    check.append(now_in_form)
                    print(check)
                    db.visit.update_one(
                        {"to_number": int(number), "from_number": payload["number"], "category": 'recordpaper'},
                        {'$set': {"current_time": check, "current_status":now_pay_status}})
                    db.recordpaper.update_one({"number": int(number)}, {"$inc": {'visit': 1}})
        return render_template('recordpaper.html', story_array=story_array, resume_array=resume_array,
                               bookmark_check=bookmark_check, like_check=like_check,
                               like_count=like_count, reply_count=reply_count, status=status, me_info=me_info,
                               mentor_info=mentor,
                               data_num=data_number, record=recordpaper_info, mentorinfo_info=mentorinfo,
                               follower=mentor_follower, followed=followed, token_receive=token_receive,
                               action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array,
                               myFeed=myFeed, my_alert=my_alert)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/resume/<int:number>/<time>', methods=['GET'])
def resume(number, time):
    token_receive = request.cookies.get('mytoken')

    mentorinfo = db.mentor_info.find_one({"number": number})
    mentor = db.mentor.find_one({"number": number})
    if db.recordpaper.find_one({'number': number})['chart_js_array'] != []:
        recordpaper_cnt = 1
    else:
        recordpaper_cnt = 0
    data_number = recordpaper_cnt + db.resume.count({"number": number}) + db.story.count({"number": number})
    following = db.followed.find_one({"number": number})
    mentor_follower = following['follower']

    # resume_info
    resume_info = db.resume.find_one({"number": number, 'time': time})

    # other data(resume)
    resume_all = list(db.resume.find({'number': number, 'release': 'sell'}, {'_id': False}))
    # (resume) like-reply count
    resume_array = []
    for resume1 in resume_all:
        if resume1['time'] != time:
            if db.like.find_one({'number': number, 'category': 'resume', 'time': resume1['time']}):
                resume_like = len(
                    db.like.find_one({'number': number, 'category': 'resume', 'time': resume1['time']})['who'])
            else:
                resume_like = 0
            if db.reply.find_one({'number': number, 'category': 'resume', 'time': resume1['time']}):
                resume_reply = str(
                    db.reply.find_one({'number': number, 'category': 'resume', 'time': resume1['time']})[
                        'reply']).count('일')
            else:
                resume_reply = 0
            resume_array.append([resume1, resume_like, resume_reply])
    print(resume)
    # other data(story)
    story_all = list(db.story.find({'number': number}, {'_id': False}))
    # (story) like-reply count
    story_array = []
    for story in story_all:
        if db.like.find_one({'number': number, 'category': 'story', 'time': story['time']}):
            story_like = len(
                db.like.find_one({'number': number, 'category': 'story', 'time': story['time']})['who'])
        else:
            story_like = 0
        if db.reply.find_one({'number': number, 'category': 'story', 'time': story['time']}):
            story_reply = str(db.reply.find_one({'number': number, 'category': 'story', 'time': story['time']})[
                                  'reply']).count('일')
        else:
            story_reply = 0
        story_array.append([story, story_like, story_reply])

    # other data(recordpaper)
    recordpaper = db.recordpaper.find_one({'number': number, 'release': 'sell'}, {'_id': False})
    # (recordpaper) like-reply count
    record_array = []
    if recordpaper is not None:
        if db.like.find_one({'number': number, 'category': 'recordpaper'}):
            record_like = len(
                db.like.find_one({'number': number, 'category': 'recordpaper'})['who'])
        else:
            record_like = 0
        if db.reply.find_one({'number': number, 'category': 'recordpaper'}):
            record_reply = str(
                db.reply.find_one({'number': number, 'category': 'recordpaper'})[
                    'reply']).count('일')
        else:
            record_reply = 0
        record_array = [recordpaper, record_like, record_reply]
        print(record_array)

    like_info = db.like.find_one({"number": int(number), "category": "resume", "time": time})
    like_count = len(like_info["who"])

    reply_info = db.reply.find_one({"number": int(number), "category": "resume", "time": time})
    reply_count = str(reply_info['reply']).count('일')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # me information
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        myFeed = (number == payload["number"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        has = request.args.get('has')
        if (has != 'pass') and (has != 'buy'):
            return redirect(url_for("home"))

        if [status, int(me_info['number'])] in mentor_follower:
            followed = 'True'
        else:
            followed = 'False'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number0 in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number0)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number0)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number1 in action_mentor:
            info2 = db.mentor.find_one({"number": int(number1)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number1)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        if payload['number'] in db.like.find_one({"number": number, "category": "resume", "time": time})['who']:
            like_check = 'like'
        else:
            like_check = 'unlike'
        # print('like_check: ',like_check)


        if payload['number'] in db.bookmark.find_one({"number": number, "category": "resume", "time": time})['who']:
            bookmark_check = 'mark'
        else:
            bookmark_check = 'unmark'
        # print(bookmark_check)

        if not myFeed:
            now = datetime.now()
            now_in_form = now.strftime("%Y/%m/%d, %H:%M:%S")
            now_pay_status = db.menti.find_one({'number': payload['number']})['pass']

            if db.pay.find_one({'client_number':payload['number'], 'number':number, 'category':'resume','time':time}) is not None:
                buy_info = db.pay.find_one({'client_number':payload['number'], 'number':number, 'category':'recordpaper','time':time})
                exp = buy_info['exp_time']
                exp_in_form = datetime.strptime(exp, "%Y-%m-%d %H:%M:%S")

                if exp_in_form > now:
                    buythis = 'yes'
                else:
                    buythis = 'no'
            else:
                buythis = 'no'

            if now_pay_status != '':
                now_pay_status = 'streaming'
            elif buythis == 'yes':
                now_pay_status = 'buy'
            else:
                return redirect(url_for("home"))

            if now_pay_status != '':
                now_pay_status = 'streaming'
            else:
                now_pay_status = 'buy'
            time1 = db.visit.find_one(
                {"to_number": int(number), "time": time, "from_number": payload["number"], "category": 'resume'})
            if time1 is None:
                visit_doc = {
                    "to_number": number,
                    "category": 'resume',
                    "time": time,
                    "status": has,
                    "from_number": payload["number"],
                    "current_time": [now_in_form],
                    "current_status": [now_pay_status]
                }
                db.visit.insert_one(visit_doc)
                db.resume.update_one({"number": int(number), "time": time}, {"$inc": {'visit': 1}})
            else:
                check = time1['current_time']
                recent_time = time1["current_time"][-1]
                get_time = datetime.strptime(recent_time, "%Y/%m/%d, %H:%M:%S")
                date_diff = now - get_time
                if date_diff.seconds > 3600:
                    check.append(now_in_form)
                    print(check)
                    db.visit.update_one({"to_number": int(number), "time": time, "from_number": payload["number"],
                                         "category": 'resume'}, {'$set': {"current_time": check, "current_status":now_pay_status}})
                    db.resume.update_one({"number": int(number), "time": time}, {"$inc": {'visit': 1}})
        return render_template('resume.html', story_array=story_array, resume_array=resume_array,
                               record_array=record_array, bookmark_check=bookmark_check, like_check=like_check,
                               like_count=like_count, reply_count=reply_count, status=status, me_info=me_info,
                               mentor_info=mentor, my_alert=my_alert,
                               data_num=data_number, resume=resume_info, mentorinfo_info=mentorinfo,
                               follower=mentor_follower, followed=followed, token_receive=token_receive,
                               action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array,
                               myFeed=myFeed)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/story/<int:number>/<time>', methods=['GET'])
def story(number, time):
    token_receive = request.cookies.get('mytoken')

    story_info = db.story.find_one({"number": number, 'time': time})
    print(story_info)
    mentorinfo = db.mentor_info.find_one({"number": number})
    mentor = db.mentor.find_one({"number": number})
    if db.recordpaper.find_one({'number': number})['chart_js_array'] != []:
        recordpaper_cnt = 1
    else:
        recordpaper_cnt = 0
    data_number = recordpaper_cnt + db.resume.count({"number": number}) + db.story.count({"number": number})
    following = db.followed.find_one({"number": number})
    mentor_follower = following['follower']

    # other data(resume)
    resume_all = list(db.resume.find({'number': number, 'release': 'sell'}, {'_id': False}))[:4]
    # (resume) like-reply count
    resume_array = []
    for resume1 in resume_all:
        if db.like.find_one({'number': number, 'category': 'resume', 'time': resume1['time']}):
            resume_like = len(
                db.like.find_one({'number': number, 'category': 'resume', 'time': resume1['time']})['who'])
        else:
            resume_like = 0
        if db.reply.find_one({'number': number, 'category': 'resume', 'time': resume1['time']}):
            resume_reply = str(
                db.reply.find_one({'number': number, 'category': 'resume', 'time': resume1['time']})[
                    'reply']).count('일')
        else:
            resume_reply = 0
        resume_array.append([resume1, resume_like, resume_reply])
    print(resume)
    # other data(story)
    story_all = list(db.story.find({'number': number}, {'_id': False}))[:4]
    # (story) like-reply count
    story_array = []
    for story1 in story_all:
        if story1['time'] != time:
            if db.like.find_one({'number': number, 'category': 'story', 'time': story1['time']}):
                story_like = len(
                    db.like.find_one({'number': number, 'category': 'story', 'time': story1['time']})['who'])
            else:
                story_like = 0
            if db.reply.find_one({'number': number, 'category': 'story', 'time': story1['time']}):
                story_reply = str(db.reply.find_one({'number': number, 'category': 'story', 'time': story1['time']})[
                                      'reply']).count('일')
            else:
                story_reply = 0
            story_array.append([story1, story_like, story_reply])

    story_tag = story_info['story_tag']
    recommend_all = list(db.story.find({'story_tag': story_tag, 'release': 'sell'}, {'_id': False}).sort('time', -1))[
                    :4]
    recommend_array = []
    mentors_array = []
    for recommend in recommend_all:
        if recommend['time'] != time:
            mentor_num = int(recommend['number'])
            product_time = recommend['time']
            db_mentor = db.mentor.find_one({'number': mentor_num},
                                           {'_id': False, 'nickname': True, 'profile_pic_real': True, 'number': True})
            db_mentorinfo = db.mentor_info.find_one({'number': mentor_num},
                                                    {'_id': False, 'mentor_univ': True, 'mentor_major': True,
                                                     'mentor_number': True, 'mentor_type': True})
            if db.like.find_one({'number': mentor_num, 'category': 'story', 'time': product_time}):
                story_like = len(
                    db.like.find_one({'number': mentor_num, 'category': 'story', 'time': product_time})['who'])
            else:
                story_like = 0
            if db.reply.find_one({'number': number, 'category': 'story', 'time': product_time}):
                story_reply = str(db.reply.find_one({'number': number, 'category': 'story', 'time': product_time})[
                                      'reply']).count('일')
            else:
                story_reply = 0
            recommend_array.append([recommend, story_like, story_reply])
            mentors_array.append([mentor_num, product_time, db_mentor['profile_pic_real'], db_mentorinfo['mentor_univ'],
                                  db_mentorinfo['mentor_major'], db_mentorinfo['mentor_number'],
                                  db_mentorinfo['mentor_type']])

    # other data(recordpaper)
    recordpaper = db.recordpaper.find_one({'number': number, 'release': 'sell'}, {'_id': False})
    # (recordpaper) like-reply count
    record_array = []
    if recordpaper is not None:
        if db.like.find_one({'number': number, 'category': 'recordpaper'}):
            record_like = len(
                db.like.find_one({'number': number, 'category': 'recordpaper'})['who'])
        else:
            record_like = 0
        if db.reply.find_one({'number': number, 'category': 'recordpaper'}):
            record_reply = str(
                db.reply.find_one({'number': number, 'category': 'recordpaper'})[
                    'reply']).count('일')
        else:
            record_reply = 0
        record_array = [recordpaper, record_like, record_reply]
        print(record_array)

    like_info = db.like.find_one({"number": int(number), "category": "story", "time": time})
    like_count = len(like_info["who"])

    reply_info = db.reply.find_one({"number": int(number), "category": "story", "time": time})
    reply_count = str(reply_info['reply']).count('일')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # me information
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        myFeed = (number == payload["number"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        if [status, int(me_info['number'])] in mentor_follower:
            followed = 'True'
        else:
            followed = 'False'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number1 in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number1)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number1)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number2 in action_mentor:
            info2 = db.mentor.find_one({"number": int(number2)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number2)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        if payload['number'] in db.like.find_one({"number": int(number), "category": "story", "time": time})['who']:
            like_check = 'like'
        else:
            like_check = 'unlike'
        # print('like_check: ',like_check)

        if payload['number'] in db.bookmark.find_one({"number": int(number), "category": "story", "time": time})['who']:
            bookmark_check = 'mark'
        else:
            bookmark_check = 'unmark'
        # print(bookmark_check)

        if not myFeed:
            now = datetime.now()
            now_in_form = now.strftime("%Y/%m/%d, %H:%M:%S")

            time1 = db.visit.find_one(
                {"to_number": int(number), "time": time, "from_number": payload["number"], "category": 'story'})

            if time1 is None:
                visit_doc = {
                    "to_number": number,
                    "category": 'story',
                    "time": time,
                    "from_status": status,
                    "from_number": payload["number"],
                    "current_time": [now_in_form],
                }
                db.visit.insert_one(visit_doc)
                db.story.update_one({"number": int(number), "time": time}, {"$inc": {'visit': 1}})
            else:
                check = time1['current_time']
                recent_time = time1["current_time"][-1]
                get_time = datetime.strptime(recent_time, "%Y/%m/%d, %H:%M:%S")
                date_diff = now - get_time
                if date_diff.seconds > 3600:
                    check.append(now_in_form)
                    print(check)
                    db.visit.update_one(
                        {"to_number": int(number), "time": time, "from_number": payload["number"], "category": 'story'},
                        {'$set': {"current_time": check}})
                    db.story.update_one({"number": int(number), "time": time}, {"$inc": {'visit': 1}})
        return render_template('story.html', mentors_array=mentors_array, recommend_array=recommend_array,
                               story_array=story_array, resume_array=resume_array, record_array=record_array,
                               bookmark_check=bookmark_check, like_check=like_check,
                               like_count=like_count, reply_count=reply_count, status=status, me_info=me_info,
                               mentor_info=mentor,time=time,
                               data_num=data_number, story=story_info, mentorinfo=mentorinfo, follower=mentor_follower,
                               followed=followed, token_receive=token_receive, action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, myFeed=myFeed, my_alert=my_alert)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('story.html', mentor_info=mentor, story=story_info, mentorinfo=mentorinfo,
                               like_count=like_count, reply_count=reply_count, data_num=data_number,time=time,
                               follower=mentor_follower, story_array=story_array, resume_array=resume_array,
                               record_array=record_array)


@app.route('/recordpaper_post/<int:number>')
def recordpaper_post(number):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentor_info = db.mentor.find_one({"number": payload["number"]})
        me_info = mentor_info
        status = 'mentor'
        recordpaper_info = db.recordpaper.find_one({"number": payload["number"]})
        record_info = db.recordpaper.find_one({"number": payload["number"]})

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)
        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        return render_template('recordpaper_post.html', me_info=me_info, mentor_info=mentor_info,
                               recordpaper_info=recordpaper_info, record_info=record_info,
                               action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array,
                               status=status,
                               my_alert=my_alert, token_receive=token_receive)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index"))


@app.route('/resume_post/<int:number>/<time>')
def resume_post(number, time):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentor_info = db.mentor.find_one({"number": number})
        mentorinfo_info = db.mentor_info.find_one({"number": number})

        me_info = mentor_info
        status = 'mentor'
        if db.resume.find_one({"number": payload["number"], 'time': time}) is not None:
            resume_info = db.resume.find_one({"number": payload["number"], 'time': time})
        else:
            resume_info = {}

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        return render_template('resume_post.html', time=time, me_info=me_info, mentor_info=mentor_info,
                               mentorinfo_info=mentorinfo_info, resume_info=resume_info,
                               action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, status=status,
                               my_alert=my_alert, token_receive=token_receive)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index"))


@app.route('/story_post/<int:number>/<time>')
def story_post(number, time):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        if number == payload['number']:
            me_info = db.mentor.find_one({'number': payload['number']})
            status = 'mentor'
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            mentor_info = db.mentor.find_one({"number": payload["number"]})
            mentorinfo_info = db.mentor_info.find_one({"number": payload["number"]})
            story_info = db.story.find_one({"number": payload["number"], "time": time})

            # follow
            me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
            nonaction_mentor = me_following['nonaction_mentor']
            print(nonaction_mentor)
            nonaction_mentor_array = []
            for number in nonaction_mentor:
                info = db.mentor.find_one({"number": int(number)},
                                          {'_id': False, 'nickname': True, 'profile_pic_real': True})
                # 대학정보도 추가로 가져와야 함
                univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
                info.update({'univ': univ})
                print('infoRenewal:', info)
                nonaction_mentor_array.append(info)
            print(nonaction_mentor_array)
            action_mentor = me_following['action_mentor']
            print(action_mentor)
            action_mentor_array = []
            for number in action_mentor:
                info2 = db.mentor.find_one({"number": int(number)},
                                           {'_id': False, 'nickname': True, 'profile_pic_real': True})
                # 대학정보도 추가로 가져와야 함
                univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
                info2.update({'univ': univ})
                print('infoRenewal:', info2)
                action_mentor_array.append(info2)
            print(action_mentor_array)

            # alert
            my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

            return render_template('story_post.html', me_info=me_info, status=status, mentor_info=mentor_info,
                                   mentorinfo_info=mentorinfo_info, story_info=story_info,time=time,
                                   action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array,
                                   my_alert=my_alert, token_receive=token_receive)
        else:
            return redirect(url_for("index"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index"))


@app.route('/readypass')
def readypass():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        return render_template('readypass.html', me_info=me_info, status=status,
                               action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array,
                               my_alert=my_alert, token_receive=token_receive)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('readypass.html')


@app.route('/menti_mypage_pass/<nickname>')
def menti_mypage_pass(nickname):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    menti_info = db.menti.find_one({"number": payload["number"]})
    me_info = menti_info
    status = 'menti'

    # follow
    me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
    nonaction_mentor = me_following['nonaction_mentor']
    print(nonaction_mentor)
    nonaction_mentor_array = []
    for number in nonaction_mentor:
        info = db.mentor.find_one({"number": int(number)},
                                  {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info.update({'univ': univ})
        print('infoRenewal:', info)
        nonaction_mentor_array.append(info)
    print(nonaction_mentor_array)
    action_mentor = me_following['action_mentor']
    print(action_mentor)
    action_mentor_array = []
    for number in action_mentor:
        info2 = db.mentor.find_one({"number": int(number)},
                                   {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info2.update({'univ': univ})
        print('infoRenewal:', info2)
        action_mentor_array.append(info2)
    print(action_mentor_array)

    # alert
    my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

    ############ pay DB ############
    now = datetime.now()
    my_pay = list(db.pay.find({'client_number': payload['number']}))
    pay_list = []
    name_list = []
    print('my_pay: ', my_pay)
    for pay in my_pay:
        get_time = datetime.strptime(pay['pay_time'], '%Y-%m-%d %H:%M:%S')
        date_diff = now - get_time
        if pay['category'] == 'readypass':
            streaming = db.menti_data.find_one({'number': payload['number'], 'miniTab': 'streaming'})
            if (date_diff.seconds < 604800) and (streaming is None):
                pay['cancel'] = 'ok'
            else:
                pay['cancel'] = ''
        elif pay['category'] == 'recordpaper':
            data_num = pay['number']
            product_name = db.recordpaper.find_one({'number': data_num})
            pay['title'] = product_name['record_title']
            visit = db.visit.find_one({'to_number': data_num, 'category': 'recordpaper', 'from_number': payload['number']})
            if ((visit is None) or ('buy' not in visit['current_status'])) and (date_diff.seconds < 604800):
                pay['cancel'] = 'ok'
            else:
                pay['cancel'] = ''
        else:
            data_num = pay['number']
            product_name = db.resume.find_one({'number': data_num, 'time': pay['time']})
            pay['title'] = product_name['resume_title']
            visit = db.visit.find_one({'to_number': data_num, 'category': 'resume', 'from_number': payload['number'], 'time': pay['time']})
            if ((visit is None) or ('buy' not in visit['current_status'])) and (date_diff.seconds < 604800):
                pay['cancel'] = 'ok'
            else:
                pay['cancel'] = ''
        pay_list.append(pay)
    pprint.pprint(pay_list)
    my_pay = pay_list
    return render_template('menti_mypage_pass.html', menti_info=menti_info, me_info=me_info, my_pay=my_pay,
                           action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array, status=status,
                           my_alert=my_alert, token_receive=token_receive)


@app.route('/menti_mypage_mydata/<nickname>')
def menti_mypage_mydata(nickname):
    i = request.args.get('mt')
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    menti_info = db.menti.find_one({"number": payload["number"]})
    me_info = menti_info
    status = 'menti'

    # follow
    me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
    nonaction_mentor = me_following['nonaction_mentor']
    print(nonaction_mentor)
    nonaction_mentor_array = []
    for number in nonaction_mentor:
        info = db.mentor.find_one({"number": int(number)},
                                  {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info.update({'univ': univ})
        print('infoRenewal:', info)
        nonaction_mentor_array.append(info)
    print(nonaction_mentor_array)
    action_mentor = me_following['action_mentor']
    print(action_mentor)
    action_mentor_array = []
    for number in action_mentor:
        info2 = db.mentor.find_one({"number": int(number)},
                                   {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info2.update({'univ': univ})
        print('infoRenewal:', info2)
        action_mentor_array.append(info2)
    print(action_mentor_array)

    # alert
    my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

    ############# 여기부터는 이 페이지 고유한 데이터를 넘겨주기 위한 내용 #############
    my_recordpaper_all = list(db.menti_data.find({'number': int(payload["number"]), 'category': 'recordpaper'}, {'_id': False}))
    my_resume_all = list(db.menti_data.find({'number': int(payload["number"]), 'category': 'resume'}, {'_id': False}))
    my_data_all = my_recordpaper_all + my_resume_all
    print(my_data_all)
    my_data = []
    for document in my_data_all:
        print('document ', document)
        if document['category'] == 'recordpaper':
            category = 'recordpaper'
            miniTab = document['miniTab']
            title = db.recordpaper.find_one({'number': int(document['mentor_num'])})['record_title']

            if db.like.find_one({'number': int(document['mentor_num']), 'category': 'recordpaper'}) is not None:
                like = len(db.like.find_one({'number': int(document['mentor_num']), 'category': 'recordpaper'})['who'])
            else:
                like = 0

            if db.reply.find_one({'number': int(document['mentor_num']), 'category': 'recordpaper'}) is not None:
                reply = str(db.reply.find_one({'number': int(document['mentor_num']), 'category': 'recordpaper'})[
                                'reply']).count('일')
            else:
                reply = 0

            if db.visit.find_one({'to_number': int(document['mentor_num']), 'category': 'recordpaper',
                                  'from_number': int(payload["number"])}) is not None:
                time = db.visit.find_one({'to_number': int(document['mentor_num']), 'category': 'recordpaper',
                                          'from_number': int(payload["number"])})['current_time'][-1]
            else:
                time = 'no'

            img = db.mentor.find_one({'number': int(document['mentor_num'])})['profile_pic_real']
            univ = db.mentor_info.find_one({'number': int(document['mentor_num'])})['mentor_univ'][0]
            major = db.mentor_info.find_one({'number': int(document['mentor_num'])})['mentor_major'][0]
            student_num = db.mentor_info.find_one({'number': int(document['mentor_num'])})['mentor_number'][0]
            type = db.mentor_info.find_one({'number': int(document['mentor_num'])})['mentor_type'][0]
            price = db.recordpaper.find_one({'number': int(document['mentor_num'])})['record_price']
            if db.pay.find_one({'client_number':int(payload['number']),'number':int(document['mentor_num']),'category':'recordpaper'}):
                exp = db.pay.find_one({'client_number':int(payload['number']),'number':int(document['mentor_num']),'category':'recordpaper'})['exp_time']
            else:
                exp = ''

            doc = {
                'category': category, 'miniTab': miniTab, 'title': title, 'like': like, 'reply': reply, 'time': time,
                'img': img, 'univ': univ, 'major': major, 'student_num': student_num, 'type': type, 'price': price,
                'exp': exp, 'mentor_num': int(document['mentor_num'])
            }
            # print(doc)
            my_data.append(doc)

        elif document['category'] == 'resume':
            category = 'resume'
            miniTab = document['miniTab']
            title = db.resume.find_one({'number': int(document['mentor_num']), 'time': document['time']})[
                'resume_title']

            if db.like.find_one({'number': int(document['mentor_num']), 'category': 'resume',
                                 'time': document['time']}) is not None:
                like = len(db.like.find_one(
                    {'number': int(document['mentor_num']), 'category': 'resume', 'time': document['time']})['who'])
            else:
                like = 0

            if db.reply.find_one({'number': int(document['mentor_num']), 'category': 'resume',
                                  'time': document['time']}) is not None:
                reply = str(db.reply.find_one(
                    {'number': int(document['mentor_num']), 'category': 'resume', 'time': document['time']})[
                                'reply']).count('일')
            else:
                reply = 0

            if db.visit.find_one(
                    {'to_number': int(document['mentor_num']), 'category': 'resume', 'time': document['time'],
                     'from_number': int(payload["number"])}) is not None:
                time = db.visit.find_one(
                    {'to_number': int(document['mentor_num']), 'category': 'resume', 'time': document['time'],
                     'from_number': int(payload["number"])})['current_time'][-1]
            else:
                visit = 'no'

            img = db.mentor.find_one({'number': int(document['mentor_num'])})['profile_pic_real']
            univ = db.resume.find_one({'number': int(document['mentor_num']), 'time': document['time']})['resume_univ']
            major = db.resume.find_one({'number': int(document['mentor_num']), 'time': document['time']})[
                'resume_major']
            student_num = db.resume.find_one({'number': int(document['mentor_num']), 'time': document['time']})[
                'resume_class']
            type = db.resume.find_one({'number': int(document['mentor_num']), 'time': document['time']})['resume_type']
            price = db.resume.find_one({'number': int(document['mentor_num']), 'time': document['time']})[
                'resume_price']
            if db.pay.find_one({ 'time':document['time'],'number':int(document['mentor_num']),'client_num':int(payload["number"]), 'category':'resume'}):
                exp = db.pay.find_one({ 'time':document['time'],'number':int(document['mentor_num']),'client_num':int(payload["number"]), 'category':'resume'})['exp_time']
            else:
                exp = ''

            doc = {
                'category': category, 'miniTab': miniTab, 'title': title, 'like': like, 'reply': reply, 'time': time,
                'img': img, 'univ': univ, 'major': major, 'student_num': student_num, 'type': type, 'price': price,
                'exp': exp, 'mentor_num': int(document['mentor_num']), 'product': document['time']
            }
            # print(doc)
            my_data.append(doc)

    pprint.pprint(my_data)

    return render_template('menti_mypage_mydata.html', param=i, my_data=my_data, menti_info=menti_info, me_info=me_info,
                           action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array, status=status,
                           my_alert=my_alert, token_receive=token_receive)


@app.route('/menti_mypage_mystory/<nickname>')
def menti_mypage_mystory(nickname):
    i = request.args.get('mt')
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    menti_info = db.menti.find_one({"number": payload["number"]})
    me_info = menti_info
    status = 'menti'

    # follow
    me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
    nonaction_mentor = me_following['nonaction_mentor']
    print(nonaction_mentor)
    nonaction_mentor_array = []
    for number in nonaction_mentor:
        info = db.mentor.find_one({"number": int(number)},
                                  {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info.update({'univ': univ})
        print('infoRenewal:', info)
        nonaction_mentor_array.append(info)
    print(nonaction_mentor_array)
    action_mentor = me_following['action_mentor']
    print(action_mentor)
    action_mentor_array = []
    for number in action_mentor:
        info2 = db.mentor.find_one({"number": int(number)},
                                   {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info2.update({'univ': univ})
        print('infoRenewal:', info2)
        action_mentor_array.append(info2)
    print(action_mentor_array)

    # alert
    my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

    ############# 여기부터는 이 페이지 고유한 데이터를 넘겨주기 위한 내용 #############
    my_data_all = list(db.menti_data.find({'number': int(payload["number"]), 'category': 'story'}, {'_id': False}))
    print(my_data_all)
    my_data = []
    for document in my_data_all:
        category = 'story'
        miniTab = document['miniTab']
        title = db.story.find_one({'number': int(document['mentor_num']), 'time': document['time']})['story_title']

        if db.like.find_one({'number': int(document['mentor_num']), 'category': 'story', 'time': document['time']}):
            like = len(db.like.find_one(
                {'number': int(document['mentor_num']), 'category': 'story', 'time': document['time']})['who'])
        else:
            like = 0

        if db.reply.find_one({'number': int(document['mentor_num']), 'category': 'story', 'time': document['time']}):
            reply = str(db.reply.find_one(
                {'number': int(document['mentor_num']), 'category': 'story', 'time': document['time']})['reply']).count(
                '일')
        else:
            reply = 0

        if db.visit.find_one({'to_number': int(document['mentor_num']), 'category': 'story', 'time': document['time'],
                              'from_number': int(payload["number"])}) is not None:
            time = db.visit.find_one(
                {'to_number': int(document['mentor_num']), 'category': 'story', 'time': document['time'],
                 'from_number': int(payload["number"])})['current_time'][-1]
        else:
            time = 'no'

        img = db.mentor.find_one({'number': int(document['mentor_num'])})['profile_pic_real']
        univ = db.mentor_info.find_one({'number': int(document['mentor_num'])})['mentor_univ'][0]
        major = db.mentor_info.find_one({'number': int(document['mentor_num'])})['mentor_major'][0]
        student_num = db.mentor_info.find_one({'number': int(document['mentor_num'])})['mentor_number'][0]
        type = db.mentor_info.find_one({'number': int(document['mentor_num'])})['mentor_type'][0]
        cat = db.story.find_one({'number': int(document['mentor_num']), 'time': document['time']})['story_tag']

        doc = {
            'category': category, 'miniTab': miniTab, 'title': title, 'cat': cat, 'like': like, 'reply': reply,
            'time': time, 'img': img, 'univ': univ, 'major': major, 'student_num': student_num, 'type': type,
            'mentor_num': int(document['mentor_num']), 'product': document['time']
        }
        # print(doc)
        my_data.append(doc)

        pprint.pprint(my_data)

    return render_template('menti_mypage_mystory.html', param=i, my_data=my_data, menti_info=menti_info,
                           me_info=me_info, action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array,
                           status=status, my_alert=my_alert, token_receive=token_receive)


@app.route('/menti_mypage_info/<nickname>')
def menti_mypage_info(nickname):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if nickname == payload["nickname"]:
        menti_info = db.menti.find_one({"nickname": nickname})
        me_info = menti_info
        status = 'menti'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)
        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        return render_template('menti_mypage_info.html', menti_info=menti_info, me_info=menti_info,
                               action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array,
                               status=status, my_alert=my_alert, token_receive=token_receive)

    else:
        return redirect(url_for("index"))


@app.route('/menti_mypage_nickname', methods=['POST'])
def menti_mypage_nickname():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    menti_num = payload['number']
    nickname = request.form['nickname']
    doc = {
        'nickname': nickname
    }
    db.menti.update_one({'number': menti_num}, {'$set': doc})

    return jsonify({'result': 'success'})


@app.route('/menti_withdraw/<number>')
def menti_withdraw(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    menti_info = db.menti.find_one({"number": payload['number']})

    me_info = menti_info
    status = 'menti'

    # follow
    me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
    nonaction_mentor = me_following['nonaction_mentor']
    print(nonaction_mentor)
    nonaction_mentor_array = []
    for number in nonaction_mentor:
        info = db.mentor.find_one({"number": int(number)},
                                  {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info.update({'univ': univ})
        print('infoRenewal:', info)
        nonaction_mentor_array.append(info)
    print(nonaction_mentor_array)
    action_mentor = me_following['action_mentor']
    print(action_mentor)
    action_mentor_array = []
    for number in action_mentor:
        info2 = db.mentor.find_one({"number": int(number)},
                                   {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info2.update({'univ': univ})
        print('infoRenewal:', info2)
        action_mentor_array.append(info2)
    print(action_mentor_array)
    # alert
    my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

    return render_template('menti_withdraw.html', menti_info=menti_info, me_info=menti_info,
                           action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array, status=status,
                           my_alert=my_alert, token_receive=token_receive)


@app.route('/remove_menti/<int:number>', methods=['POST'])
def remove_menti(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    menti_info = db.menti.find_one({"number": payload['number']})

    now = datetime.now()
    now_in_form = now.strftime("%Y/%m/%d, %H:%M:%S")
    print(now_in_form)

    menti_info['withdraw_date'] = now_in_form
    print(menti_info)
    db.withdraw.insert_one(menti_info)
    # 계류장으로 이송

    withdraw_password = hashlib.sha256(('readymate').encode('utf-8')).hexdigest()
    empty_menti_doc = {
        "pass": "",
        "email": str(number),
        "phone": str(number),
        "password": withdraw_password,
        "name": "",
        "birth": "",
        "nickname": "탈퇴한 회원입니다",
        "status": "고3",
        "location": "서울특별시",
        "school_type": "자율형사립고",
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_placeholder_x.png",
        "v": "menti",
        "resetNum": "",
        "numTime": "",
        "withdraw_date": now_in_form
    }
    db.menti.update_one({'number': number}, {'$set': empty_menti_doc})
    # menti db에서 개인정보 날리고 남길정보, 바꿀 정보 바꿔서 저장

    ##########################################################################################
    ###  30일 계류 후에 해야 할 작업!!!!!!!!!!!!!!!!!!! 댓글 제외 실제 이 멘티와 관련된 내용을 삭제해줘야 함  ####
    ##########################################################################################
    # db.alert.deleteMany({'to_status':'menti', 'to_number':number})
    # 이 멘티 알림 지우기
    # db.following.deleteMany({'follower_status':'menti', 'follower_number':number})
    # 이 멘티 팔로잉지우기
    # 이 멘티가 팔로우하는 멘토에서 멘티 지우기 작업 해야 함
    # 이 멘티가 좋아요 한 글에서 멘티 지우기 작업 해야 함
    ##########################################################################################

    return jsonify({'result': 'success'})


@app.route('/finish_menti_withdraw')
def finish_menti_withdraw():
    return render_template('finish_menti_withdraw.html')


@app.route('/mentor_mypage_mydata/<nickname>')
def mentor_mypage_mydata(nickname):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    mentor_info = db.mentor.find_one({"number": payload["number"]})
    mentor_number = int(payload["number"])
    me_info = mentor_info
    status = 'mentor'
    mentor_info = db.mentor.find_one({"nickname": payload["nickname"]})
    mentorinfo_info = db.mentor_info.find_one({"number": mentor_number})

    # follow
    me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
    nonaction_mentor = me_following['nonaction_mentor']
    print(nonaction_mentor)
    nonaction_mentor_array = []
    for number in nonaction_mentor:
        info = db.mentor.find_one({"number": int(number)},
                                  {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info.update({'univ': univ})
        print('infoRenewal:', info)
        nonaction_mentor_array.append(info)
    print(nonaction_mentor_array)
    action_mentor = me_following['action_mentor']
    print(action_mentor)
    action_mentor_array = []
    for number in action_mentor:
        info2 = db.mentor.find_one({"number": int(number)},
                                   {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info2.update({'univ': univ})
        print('infoRenewal:', info2)
        action_mentor_array.append(info2)
    print(action_mentor_array)

    # alert
    my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

    # my data
    recordpaper = db.recordpaper.find_one({'number': mentor_number}, {'_id': False})
    if recordpaper is not None:
        if db.like.find_one({'number': mentor_number, 'category': 'recordpaper'}):
            rec_like = len(db.like.find_one({'number': mentor_number, 'category': 'recordpaper'})['who'])
        else:
            rec_like = 0
        if db.reply.find_one({'number': mentor_number, 'category': 'recordpaper'}):
            rec_reply = str(db.reply.find_one({'number': mentor_number, 'category': 'recordpaper'})['reply']).count('일')
        else:
            rec_reply = 0
        recordpaper['record_like'] = rec_like
        recordpaper['record_reply'] = rec_reply
    else:
        recordpaper = ""
    print(recordpaper)

    resume_array = []
    resume_list = list(db.resume.find({'number': mentor_number}, {'_id': False}))
    for resume in resume_list:
        if db.like.find_one({'number': mentor_number, 'category': 'resume', 'time': resume['time']}):
            resume_like = len(
                db.like.find_one({'number': mentor_number, 'category': 'resume', 'time': resume['time']})['who'])
        else:
            resume_like = 0
        if db.reply.find_one({'number': mentor_number, 'category': 'resume', 'time': resume['time']}):
            resume_reply = str(
                db.reply.find_one({'number': mentor_number, 'category': 'resume', 'time': resume['time']})[
                    'reply']).count('일')
        else:
            resume_reply = 0
        resume_array.append([resume, resume_like, resume_reply])

    return render_template('mentor_mypage_mydata.html', recordpaper=recordpaper, resume_array=resume_array,
                           mentor_info=mentor_info, mentorinfo_info=mentorinfo_info, me_info=me_info,
                           token_receive=token_receive, action_mentor=action_mentor_array,
                           nonaction_mentor=nonaction_mentor_array, my_alert=my_alert, status=status)


@app.route('/mentor_mypage_mystory/<nickname>')
def mentor_mypage_mystory(nickname):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    if nickname == payload['nickname']:
        mentor_info = db.mentor.find_one({"number": payload["number"]})
        mentor_number = int(payload["number"])
        me_info = mentor_info
        status = 'mentor'
        mentor_info = db.mentor.find_one({"nickname": payload["nickname"]})
        mentorinfo_info = db.mentor_info.find_one({"number": mentor_number})

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        # record 유무
        if db.recordpaper.find_one({'number': mentor_number})['record_title']:
            record = 'has'
        else:
            record = ''

        # my story
        story_array = []
        story_list = list(db.story.find({'number': mentor_number}, {'_id': False}))
        for story in story_list:
            if db.like.find_one({'number': mentor_number, 'category': 'story', 'time': story['time']}):
                story_like = len(
                    db.like.find_one({'number': mentor_number, 'category': 'story', 'time': story['time']})['who'])
            else:
                story_like = 0
            if db.reply.find_one({'number': mentor_number, 'category': 'story', 'time': story['time']}):
                story_reply = str(
                    db.reply.find_one({'number': mentor_number, 'category': 'story', 'time': story['time']})[
                        'reply']).count('일')
            else:
                story_reply = 0
            story_array.append([story, story_like, story_reply])

        return render_template('mentor_mypage_mystory.html', story_array=story_array, recordpaper=record,
                               mentor_info=mentor_info, mentorinfo_info=mentorinfo_info, me_info=me_info,
                               token_receive=token_receive, action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, my_alert=my_alert, status=status)

    else:
        return redirect(url_for("index"))


@app.route('/mentor_mypage_dashboard/<nickname>')
def mentor_mypage_dashboard(nickname):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    if nickname == payload['nickname']:
        mentor_info = db.mentor.find_one({"nickname": payload["nickname"]})

        # me information
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        return render_template('mentor_mypage_dashboard.html', mentor_info=mentor_info, me_info=me_info,
                               token_receive=token_receive, action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, my_alert=my_alert, status=status)
    else:
        return redirect(url_for("index"))


@app.route('/mentor_mypage_profit/<nickname>')
def mentor_mypage_profit(nickname):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    if nickname == payload['nickname']:
        mentor_info = db.mentor.find_one({"nickname": payload["nickname"]})

        # me information
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        return render_template('mentor_mypage_profit.html', mentor_info=mentor_info, me_info=me_info,
                               token_receive=token_receive, action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, my_alert=my_alert, status=status)
    else:
        return redirect(url_for("index"))


@app.route('/mentor_mypage_account/<nickname>')
def menti_mypage_account(nickname):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    if nickname == payload['nickname']:
        mentor_info = db.mentor.find_one({"nickname": payload["nickname"]})

        # me information
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        return render_template('mentor_mypage_account.html', mentor_info=mentor_info, me_info=me_info,
                               token_receive=token_receive, action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, my_alert=my_alert, status=status)
    else:
        return redirect(url_for("index"))


@app.route('/mentor_mypage_communication/<nickname>')
def mentor_mypage_communication(nickname):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    if nickname == payload['nickname']:
        mentor_info = db.mentor.find_one({"nickname": payload["nickname"]})

        # me information
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        return render_template('mentor_mypage_communication.html', mentor_info=mentor_info, me_info=me_info,
                               token_receive=token_receive, action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, my_alert=my_alert, status=status)
    else:
        return redirect(url_for("index"))


@app.route('/mentor_mypage_info/<nickname>')
def mentor_mypage_info(nickname):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentor_info = db.mentor.find_one({"number": payload["number"]})
        mentorinfo_info = db.mentor_info.find_one({"number": payload["number"]})

        # me information
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        return render_template('mentor_mypage_info.html', mentor_info=mentor_info, mentorinfo_info=mentorinfo_info,
                               me_info=me_info, action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, status=status, my_alert=my_alert,
                               token_receive=token_receive)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        print('no token')
        return render_template('user_mentor.html', mentor_info=mentor_info, mentorinfo_info=mentorinfo_info)


@app.route('/mentor_mypage_info_accepted', methods=['POST'])
def mentor_mypage_info_accepted():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    my_num = int(payload['number'])
    # find_mentor = db.mentor.find_one({'number':my_num})
    # accepted_files

    file = request.files['file']
    filename_array = db.mentor.find_one({'number': my_num})['univAccepted_file']
    file_path_array = db.mentor.find_one({'number': my_num})['univAccepted_file_real']
    filename = secure_filename(file.filename)
    extension = filename.split(".")[-1]
    file_path = f"univAccepted_files/{my_num}-{filename}.{extension}"
    file.save("./static/" + file_path)

    print(filename_array)
    filename_array.append(filename)
    print(filename_array)
    file_path_array.append(file_path)

    doc = {
        "univAccepted_file": filename_array,
        "univAccepted_file_real": file_path_array,
    }
    db.mentor.update_one({'number': my_num}, {'$set': doc})
    return jsonify({'result': 'success'})


@app.route('/mentor_mypage_info_email', methods=['POST'])
def mentor_mypage_info_email():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    email = request.form['email']
    my_number = payload['number']
    doc = {
        'email': email
    }
    db.mentor.update_one({'number': my_number}, {'$set': doc})
    return jsonify({'result': 'success'})


@app.route('/mentor_mypage_password', methods=['POST'])
def mentor_mypage_password():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    password_receive = request.form['password_give']
    password = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        'password': password
    }
    db.mentor.update_one({'number': payload['number']}, {'$set': doc})
    return jsonify({'result': 'success'})


@app.route('/mentor_mypage_pic', methods=['POST'])
def mentor_mypage_pic():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    number = payload['number']
    doc = {
        "profile_pic": "",
        "profile_pic_real": f"profile_pics/profile_placeholder_{number % 3}.png",
    }
    if 'file_give' in request.files:
        file = request.files["file_give"]
        filename = secure_filename(file.filename)
        extension = filename.split(".")[-1]
        file_path = f"profile_pics/{number}.{extension}"
        file.save("./static/" + file_path)
        doc["profile_pic"] = filename
        doc["profile_pic_real"] = file_path
    db.mentor.update_one({'number': payload['number']}, {'$set': doc})
    return jsonify({'result': 'success'})


@app.route('/menti_mypage_password', methods=['POST'])
def menti_mypage_password():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    password_receive = request.form['password_give']
    password = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        'password': password
    }
    db.menti.update_one({'number': payload['number']}, {'$set': doc})
    return jsonify({'result': 'success'})


@app.route('/user_mentor/<nickname>')
def user_mentor(nickname):
    token_receive = request.cookies.get('mytoken')
    mentor_info = db.mentor.find_one({"nickname": nickname})
    mentor_num = mentor_info['number']
    mentorinfo_info = db.mentor_info.find_one({"number": mentor_num})
    mentor_recordpaper = db.recordpaper.find_one({"number": mentor_num})
    mentor_resume = list(db.resume.find({"number": mentor_num}))
    print(mentor_resume)
    following = db.followed.find_one({"number": mentor_num})
    mentor_follower = following['follower']
    print(mentor_follower)
    user_mentor_chart = db.recordpaper.find_one({'number': mentor_num})['chart_js_array']

    # make recent_resume & record list
    db_mentor3 = db.mentor.find_one({'number': mentor_num},
                                    {'_id': False, 'nickname': True, 'profile_pic_real': True, 'number': True})
    db_mentorinfo3 = db.mentor_info.find_one({'number': mentor_num},
                                             {'_id': False, 'mentor_univ': True, 'mentor_major': True,
                                              'mentor_number': True, 'mentor_type': True})
    mentor_record = []
    record = db.recordpaper.find_one({"number": mentor_num})
    if record['record_title'] != "":
        record_title = record['record_title']
        record_price = record['record_price']
    else:
        record_title = ""
        record_price = ""
    record_release = record['release']

    db_like2 = db.like.find_one({'number': mentor_num, 'category': 'recordpaper'})
    db_reply2 = db.reply.find_one({'number': mentor_num, 'category': 'recordpaper'})
    if db_like2 is not None:
        record_likely = len(db_like2['who'])
    else:
        record_likely = 0
    if db_reply2 is not None:
        record_reply = str(db_reply2['reply']).count('일')
    else:
        record_reply = 0

    if db_mentorinfo3['mentor_number'] == []:
        db_mentorinfo3['mentor_number'] = ['']
        db_mentorinfo3['mentor_univ'] = ['']
        db_mentorinfo3['mentor_major'] = ['']
        db_mentorinfo3['mentor_type'] = ['']

    arr2 = [
        record_title,
        record_price,
        db_mentor3['number'],
        db_mentor3['nickname'],
        db_mentorinfo3['mentor_number'][0],
        db_mentorinfo3['mentor_univ'][0],
        db_mentorinfo3['mentor_major'][0],
        db_mentorinfo3['mentor_type'][0],
        record_likely,
        record_reply,
        record_release
    ]
    mentor_record.append(arr2)
    print(mentor_record)

    if record_release == 'sell':
        sorted_mentor_resume = list(db.resume.find({"number": mentor_num, "release": "sell"}).sort('time', -1))[:3]
    else:
        sorted_mentor_resume = list(db.resume.find({"number": mentor_num, "release": "sell"}).sort('time', -1))[:4]
    print(sorted_mentor_resume)
    product_number = db.recordpaper.count({"number": mentor_num, "release": "sell"}) + db.resume.count(
        {"number": mentor_num, "release": "sell"})

    mentor_resume = []
    for resume in sorted_mentor_resume:
        mentor_num3 = int(resume['number'])
        db_mentor3 = db.mentor.find_one({'number': mentor_num3},
                                        {'_id': False, 'nickname': True, 'profile_pic_real': True, 'number': True})
        db_mentorinfo3 = db.mentor_info.find_one({'number': mentor_num3},
                                                 {'_id': False, 'mentor_univ': True, 'mentor_major': True,
                                                  'mentor_number': True, 'mentor_type': True})

        resume_title = resume['resume_title']
        resume_price = resume['resume_price']
        resume_time = resume['time']
        resume_univ = resume['resume_univ']
        resume_major = resume['resume_major']
        resume_type = resume['resume_type']
        resume_number = resume['resume_class']

        db_like1 = db.like.find_one({'number': mentor_num3, 'category': 'resume', 'time': resume_time})
        db_reply1 = db.reply.find_one({'number': mentor_num3, 'category': 'resume', 'time': resume_time})
        if db_like1 is not None:
            resume_likely = len(db_like1['who'])
        else:
            resume_likely = 0
        resume_reply = str(db_reply1['reply']).count('일')
        if resume['release'] == 'sell':
            arr = [
                resume_title,
                resume_price,
                resume_time,
                resume_univ,
                resume_major,
                resume_type,
                resume_number,
                db_mentor3['number'],
                db_mentor3['nickname'],
                resume_likely,
                resume_reply
            ]
            mentor_resume.append(arr)
    print(mentor_resume)

    # make recent_story list
    sorted_mentor_story = list(db.story.find({"number": mentor_num, "release": "sell"}).sort('time', -1))[:8]
    print(sorted_mentor_story)
    story_number = db.story.count({"number": mentor_num, "release": "sell"})
    mentor_story = []
    for story in sorted_mentor_story:
        mentor_num3 = int(story['number'])
        db_mentor3 = db.mentor.find_one({'number': mentor_num3},
                                        {'_id': False, 'nickname': True, 'profile_pic_real': True, 'number': True})
        db_mentorinfo3 = db.mentor_info.find_one({'number': mentor_num3},
                                                 {'_id': False, 'mentor_univ': True, 'mentor_major': True,
                                                  'mentor_number': True, 'mentor_type': True})
        story_title = story['story_title']
        story_time = story['time']
        db_like3 = db.like.find_one({'number': mentor_num3, 'category': 'story', 'time': story_time})
        db_reply3 = db.reply.find_one({'number': mentor_num3, 'category': 'story', 'time': story_time})
        if db_like3 is not None:
            story_likely = len(db_like3['who'])
        else:
            story_likely = 0
        story_reply = str(db_reply3['reply']).count('일')
        if story['release'] == 'sell':
            arr3 = [
                story_title,
                story_time,
                db_mentor3['number'],
                db_mentor3['nickname'],
                db_mentorinfo3['mentor_number'][0],
                db_mentorinfo3['mentor_univ'][0],
                db_mentorinfo3['mentor_major'][0],
                db_mentorinfo3['mentor_type'][0],
                story_likely,
                story_reply
            ]
            mentor_story.append(arr3)

    story_cnt = len(mentor_story)
    print(story_cnt)
    if story_cnt > 1:
        if story_cnt % 2 == 1:
            mentor_story.pop()
    mentor_story1 = mentor_story[0: 2]
    mentor_story2 = mentor_story[2: 4]
    mentor_story3 = mentor_story[4: 6]
    mentor_story4 = mentor_story[6: 8]
    mentor_story = [mentor_story1, mentor_story2, mentor_story3, mentor_story4]
    print(mentor_story)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print('has token')
        myFeed = (nickname == payload["nickname"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        if [status, int(me_info['number'])] in mentor_follower:
            followed = 'True'
        else:
            followed = 'False'

        # admin
        if payload['admin'] == 'yes':
            admin = 'True'
        else:
            admin = 'False'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        return render_template('user_mentor.html', mentor_record=mentor_record, mentor_resume=mentor_resume,
                               product_number=product_number, story_number=story_number, mentor_story=mentor_story,
                               mentor_info=mentor_info, mentorinfo_info=mentorinfo_info, status=status,
                               chart_array=user_mentor_chart, myFeed=myFeed, resume=mentor_resume,
                               record=mentor_recordpaper, me_info=me_info, follower=mentor_follower, followed=followed,
                               token_receive=token_receive, action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, my_alert=my_alert, admin=admin)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        print('no token')
        return render_template('user_mentor.html', mentor_record=mentor_record, mentor_resume=mentor_resume,
                               product_number=product_number, story_number=story_number, mentor_story=mentor_story,
                               mentor_info=mentor_info, mentorinfo_info=mentorinfo_info,
                               chart_array=user_mentor_chart, resume=mentor_resume,
                               record=mentor_recordpaper, me_info=None,
                               follower=mentor_follower)


@app.route('/index')
def index():
    mentor_out = db.mentor.count_documents({}) - db.mentor.count_documents({"name": ""})

    # make initial list of searchbox mentor list by follower count, limit 30
    mentor_all = db.followed.find()
    print('mentorALl', mentor_all)
    initial_mentor_dic = {}
    for mentor in mentor_all:
        if db.mentor.find_one({'number': mentor['number']})['univAttending_file_real'] == '':
            follower_cnt = len(mentor['follower'])
            initial_mentor_dic[mentor['number']] = follower_cnt
    sorted_list = sorted(initial_mentor_dic.items(), key=lambda x: x[1], reverse=True)[:30]
    initial_search_list = []
    for item in sorted_list:
        mentor_num = int(item[0])
        db_mentor = db.mentor.find_one({'number': mentor_num},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
        db_mentorinfo = db.mentor_info.find_one({'number': mentor_num},
                                                {'_id': False, 'tags': True, 'mentor_univ': True,
                                                 'mentor_major': True, 'mentor_type': True, 'mentor_number': True})
        if db.recordpaper.find_one({'number': mentor_num})['release'] == 'sell':
            record_count = 1
        else:
            record_count = 0
        cnt_mentor_data = record_count + db.resume.find(
            {'number': mentor_num, 'release': 'sell'}).count() + db.story.find(
            {'number': mentor_num, 'release': 'sell'}).count()

        arr = [
            db_mentor['profile_pic_real'],
            item[1],
            cnt_mentor_data,
            db_mentorinfo['tags'],
            db_mentor['nickname'],
            db_mentorinfo['mentor_univ'][0],
            db_mentorinfo['mentor_major'][0],
            db_mentorinfo['mentor_type'][0],
            db_mentorinfo['mentor_number'][0]
        ]
        initial_search_list.append(arr)

    # make new-face mentor list by recent 20
    sorted_new_mentor = list(db.mentor.find({'univAttending_file_real': ''}).sort('number', -1))[:20]
    new_mentor_list = []
    for mentor in sorted_new_mentor:
        mentor_num2 = int(mentor['number'])
        db_mentor2 = db.mentor.find_one({'number': mentor_num2},
                                        {'_id': False, 'nickname': True, 'profile_pic_real': True})
        db_mentorinfo2 = db.mentor_info.find_one({'number': mentor_num2},
                                                 {'_id': False, 'tags': True, 'mentor_univ': True,
                                                  'mentor_major': True, 'mentor_type': True, 'mentor_number': True})
        if db.recordpaper.find_one({'number': mentor_num2})['chart_js_array']:
            record_count2 = 1
        else:
            record_count2 = 0
        cnt_mentor_data2 = record_count2 + db.resume.find(
            {'number': mentor_num2, 'release': 'sell'}).count() + db.story.find(
            {'number': mentor_num2, 'release': 'sell'}).count()

        arr2 = [
            db_mentor2['profile_pic_real'],
            '',
            cnt_mentor_data2,
            db_mentorinfo2['tags'],
            db_mentor2['nickname'],
            db_mentorinfo2['mentor_univ'][0],
            db_mentorinfo2['mentor_major'][0],
            db_mentorinfo2['mentor_type'][0],
            db_mentorinfo2['mentor_number'][0],
        ]
        new_mentor_list.append(arr2)

    # make recent_hot_community list by hot 30
    sorted_new_community = list(db.community.find().sort('_id', -1))[:30]
    print(sorted_new_community)
    hot_community = []
    for community in sorted_new_community:
        mentor_num3 = int(community['number'])
        db_mentor3 = db.mentor.find_one({'number': mentor_num3},
                                        {'_id': False, 'nickname': True, 'profile_pic_real': True})
        db_mentorinfo3 = db.mentor_info.find_one({'number': mentor_num3},
                                                 {'_id': False, 'mentor_univ': True, 'mentor_major': True,
                                                  'mentor_number': True})
        community_title = community['title']
        community_desc = community['desc']
        community_time = community['time']
        community_like = len(
            db.like.find_one({'number': mentor_num3, 'category': 'community', 'time': community_time})['who'])

        arr3 = [
            community_title,
            community_like,
            community_desc,
            db_mentor3['profile_pic_real'],
            db_mentor3['nickname'],
            db_mentorinfo3['mentor_number'][0],
            db_mentorinfo3['mentor_univ'][0],
            db_mentorinfo3['mentor_major'][0],
        ]
        hot_community.append(arr3)
    print(hot_community)

    # make hotest record list by visit count
    sorted_hot_record = list(db.recordpaper.find({'release': 'sell'}).sort('visit', -1))[:16]
    mentor_record = []
    for record in sorted_hot_record:
        mentor_num3 = int(record['number'])
        db_mentor3 = db.mentor.find_one({'number': mentor_num3},
                                        {'_id': False, 'nickname': True, 'profile_pic_real': True, 'number': True})
        db_mentorinfo3 = db.mentor_info.find_one({'number': mentor_num3},
                                                 {'_id': False, 'mentor_univ': True, 'mentor_major': True,
                                                  'mentor_number': True, 'mentor_type': True})
        db_like1 = db.like.find_one({'number': mentor_num3, 'category': 'recordpaper'})
        db_reply1 = db.reply.find_one({'number': mentor_num3, 'category': 'recordpaper'})

        record_title = record['record_title']
        record_price = record['record_price']
        if db_like1 is not None:
            record_likely = len(db_like1['who'])
        else:
            record_likely = 0
        record_reply = str(db_reply1['reply']).count('일')
        if record['release'] == 'sell':
            arr4 = [
                record_title,
                record_price,
                db_mentor3['number'],
                db_mentor3['nickname'],
                db_mentorinfo3['mentor_number'][0],
                db_mentorinfo3['mentor_univ'][0],
                db_mentorinfo3['mentor_major'][0],
                db_mentorinfo3['mentor_type'][0],
                record_likely,
                db_mentor3['profile_pic_real'],
                record_reply
            ]
            mentor_record.append(arr4)
    print(mentor_record)

    mentor_record1 = mentor_record[0: 4]
    mentor_record2 = mentor_record[4: 8]
    mentor_record3 = mentor_record[8: 12]
    mentor_record4 = mentor_record[12: 16]
    mentor_record = [mentor_record1, mentor_record2, mentor_record3, mentor_record4]
    print(mentor_record)

    # make hotest story list by visit count
    sorted_hot_story = list(db.story.find({'release': 'sell'}).sort('visit', -1))[:16]
    mentor_story = []
    for story in sorted_hot_story:
        mentor_num3 = int(story['number'])
        db_mentor3 = db.mentor.find_one({'number': mentor_num3},
                                        {'_id': False, 'nickname': True, 'profile_pic_real': True, 'number': True})
        db_mentorinfo3 = db.mentor_info.find_one({'number': mentor_num3},
                                                 {'_id': False, 'mentor_univ': True, 'mentor_major': True,
                                                  'mentor_number': True, 'mentor_type': True})
        story_title = story['story_title']
        story_time = story['time']

        db_like2 = db.like.find_one({'number': mentor_num3, 'category': 'story', 'time': story_time})
        db_reply2 = db.reply.find_one({'number': mentor_num3, 'category': 'story', 'time': story_time})
        if db_like2 is not None:
            story_likely = len(db_like2['who'])
        else:
            story_likely = 0
        story_reply = str(db_reply2['reply']).count('일')

        arr5 = [
            story_title,
            story_time,
            db_mentor3['number'],
            db_mentor3['nickname'],
            db_mentorinfo3['mentor_number'][0],
            db_mentorinfo3['mentor_univ'][0],
            db_mentorinfo3['mentor_major'][0],
            db_mentorinfo3['mentor_type'][0],
            db_mentor3['profile_pic_real'],
            story_likely,
            story_reply
        ]
        mentor_story.append(arr5)
    print(mentor_story)

    mentor_story1 = mentor_story[0: 4]
    mentor_story2 = mentor_story[4: 8]
    mentor_story3 = mentor_story[8: 12]
    mentor_story4 = mentor_story[12: 16]
    mentor_story = [mentor_story1, mentor_story2, mentor_story3, mentor_story4]
    print(mentor_story)

    # make hotest resume list by visit count
    sorted_hot_resume = list(db.resume.find({'release': 'sell'}).sort('visit', -1))[:16]
    mentor_resume = []
    for resume in sorted_hot_resume:
        mentor_num3 = int(resume['number'])
        db_mentor3 = db.mentor.find_one({'number': mentor_num3},
                                        {'_id': False, 'nickname': True, 'profile_pic_real': True, 'number': True})

        resume_title = resume['resume_title']
        resume_time = resume['time']
        resume_univ = resume['resume_univ']
        resume_major = resume['resume_major']
        resume_type = resume['resume_type']
        resume_class = resume['resume_class']
        resume_price = resume['resume_price']

        db_like3 = db.like.find_one({'number': mentor_num3, 'category': 'resume', 'time': resume_time})
        db_reply3 = db.reply.find_one({'number': mentor_num3, 'category': 'resume', 'time': resume_time})

        if db_like3 is not None:
            resume_likely = len(db_like3['who'])
        else:
            resume_likely = 0
        resume_reply = str(db_reply3['reply']).count('일')

        if resume['release'] == 'sell':
            arr6 = [
                resume_title,
                resume_time,
                resume_univ,
                resume_major,
                resume_type,
                resume_class,
                resume_price,
                db_mentor3['number'],
                db_mentor3['nickname'],
                db_mentor3['profile_pic_real'],
                resume_likely,
                resume_reply
            ]
            mentor_resume.append(arr6)
    print(mentor_resume)

    mentor_resume1 = mentor_resume[0: 4]
    mentor_resume2 = mentor_resume[4: 8]
    mentor_resume3 = mentor_resume[8: 12]
    mentor_resume4 = mentor_resume[12: 16]
    mentor_resume = [mentor_resume1, mentor_resume2, mentor_resume3, mentor_resume4]
    print(mentor_resume)

    try:
        token_receive = request.cookies.get('mytoken')
        print('has token')
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        if payload is None:
            return render_template('index.html', mentor_resume=mentor_resume, mentor_story=mentor_story,
                                   mentor_record=mentor_record, initial_search_list=initial_search_list,
                                   new_mentor_list=new_mentor_list,
                                   hot_community=hot_community, mentor_out=mentor_out)
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            nonaction_mentor_array.append(info)
        action_mentor = me_following['action_mentor']
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            action_mentor_array.append(info2)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))
        return render_template('index.html', mentor_resume=mentor_resume, mentor_story=mentor_story,
                               mentor_record=mentor_record, initial_search_list=initial_search_list,
                               new_mentor_list=new_mentor_list, hot_community=hot_community, mentor_out=mentor_out,
                               me_info=me_info, status=status, token_receive=token_receive,
                               action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array,
                               my_alert=my_alert)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        print('no token')
        return render_template('index.html', mentor_resume=mentor_resume, mentor_story=mentor_story,
                               mentor_record=mentor_record, initial_search_list=initial_search_list,
                               new_mentor_list=new_mentor_list,
                               hot_community=hot_community, mentor_out=mentor_out)


@app.route('/get_mentor', methods=['GET'])
def get_mentor():
    # selectedUnivArray = request.args.get('selectedUnivArray').split(',')[1:]
    selectedUnivArray = request.args.get('selectedUnivArray').split(',')
    if selectedUnivArray == ['']:
        selectedUnivArray = []
    # selectedMajorArray = request.args.get('selectedMajorArray').split(',')[1:]
    selectedMajorArray = request.args.get('selectedMajorArray').split(',')
    if selectedMajorArray == ['']:
        selectedMajorArray = []
    # selectedTypeArray = request.args.get('selectedTypeArray').split(',')[1:]
    selectedTypeArray = request.args.get('selectedTypeArray').split(',')
    if selectedTypeArray == ['']:
        selectedTypeArray = []
    check = request.args.get('check')
    print(selectedUnivArray)
    print(selectedMajorArray)
    print(check)
    print(selectedTypeArray)

    mentor_all = list(db.mentor_info.find({}, {'_id': False, 'number': True, 'mentor_univ': True, 'mentor_major': True,
                                               'mentor_type': True}).sort('_id',-1))
    # make filtered array through univ
    univ_filtered = []
    if selectedUnivArray == []:
        for mentor in mentor_all:
            if db.mentor.find_one({'number':mentor['number']})['univAttending_file_real'] == '' :
                univ_filtered.append(mentor['number'])
        # if there is no selected univ, there is no filtering
    else:
        for mentor in mentor_all:
            if (set(mentor['mentor_univ']) & set(selectedUnivArray)):
                # compare each mentor`s array and selected univ, insert if sth matched
                univ_filtered.append(mentor['number'])
    print('univ_filtered', univ_filtered)
    # array filtered by univ

    # make filtered array through major, !consider case of 'checked'
    univ_major_filtered = []
    if ('전체 학과' in selectedMajorArray) or selectedMajorArray == []:
        univ_major_filtered = univ_filtered
        print('univ_major_filtered', univ_major_filtered)
    else:
        if check == 'on':
            print(selectedMajorArray, '과 어레이')
            # similar major including checked, in order to makr selected array transformed to middleselector
            for major in selectedMajorArray:
                print(major, '--이 과의 중계열을 찾아요')
                middle = db.univ_list.find_one({'학과명': major})['중계열']
                selectedMajorArray.remove(major)
                selectedMajorArray.insert(0, middle)
            print('checked-new', selectedMajorArray)

            for mentor2 in univ_filtered:
                mentor_major_array = db.mentor_info.find_one({'number': int(mentor2)})['mentor_major']
                for major2 in mentor_major_array:
                    if db.univ_list.find_one({'학과명': major2}) is not None:
                        middle2 = db.univ_list.find_one({'학과명': major2})['중계열']
                        mentor_major_array.remove(major2)
                        mentor_major_array.insert(0, middle2)
                        # transformed each mentor_major_array into middle selector
                if set(mentor_major_array) & set(selectedMajorArray):
                    univ_major_filtered.append(mentor2)
            print('univ_major_filtered', univ_major_filtered)
            # array filterd by univ + (checked)major
        else:
            for mentor3 in univ_filtered:
                mentor_major_array = db.mentor_info.find_one({'number': int(mentor3)})['mentor_major']
                if set(mentor_major_array) & set(selectedMajorArray):
                    univ_major_filtered.append(mentor3)
            print('univ_major_filtered', univ_major_filtered)
            # array filterd by univ + (un-checked)major

    # make filtered array through major
    univ_major_type_filtered = []
    if selectedTypeArray == []:
        univ_major_type_filtered = univ_major_filtered
        print('univ_major_type_filtered', univ_major_type_filtered)
    else:
        for mentor4 in univ_major_filtered:
            mentor_type_array = db.mentor_info.find_one({'number': int(mentor4)})['mentor_type']
            for type in mentor_type_array:
                if db.univ_type.find_one({'전형명': type}) is not None:
                    type_cat = db.univ_type.find_one({'전형명': type})['전형유형']
                    mentor_type_array.remove(type)
                    mentor_type_array.insert(0, type_cat)
                    # transformed each mentor_type_array into higher selector
            if set(mentor_type_array) & set(selectedTypeArray):
                # compare each mentor`s type_cat array and selected types, insert if sth matched
                univ_major_type_filtered.append(mentor4)
        print('univ_major_type_filtered', univ_major_type_filtered)

    # make card
    search_result = []
    for mentor_num in univ_major_type_filtered:
        # print('number: ',mentor_num)
        db_mentor = db.mentor.find_one({'number': mentor_num},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
        db_mentorinfo = db.mentor_info.find_one({'number': mentor_num},
                                                {'_id': False, 'tags': True, 'mentor_univ': True, 'mentor_major': True,
                                                 'mentor_type': True, 'mentor_number': True})
        if db.recordpaper.find_one({'number': mentor_num, 'release': 'sell'}):
            record_count = 1
        else:
            record_count = 0
        resume_count = db.resume.find({'number': mentor_num, 'release': 'sell'}).count()
        story_count = db.story.find({'number': mentor_num, 'release': 'sell'}).count()
        cnt_mentor_data = record_count + resume_count + story_count

        if db_mentorinfo['mentor_univ'] == []:
            db_mentorinfo['mentor_univ'] = [""]
        if db_mentorinfo['mentor_major'] == []:
            db_mentorinfo['mentor_major'] = [""]
        if db_mentorinfo['mentor_type'] == []:
            db_mentorinfo['mentor_type'] = [""]
        if db_mentorinfo['mentor_number'] == []:
            db_mentorinfo['mentor_number'] = [""]
        arr = [
            db_mentor['profile_pic_real'],
            len(db.followed.find_one({'number': mentor_num})['follower']),
            cnt_mentor_data,
            db_mentorinfo['tags'],
            db_mentor['nickname'],
            db_mentorinfo['mentor_univ'][0],
            db_mentorinfo['mentor_major'][0],
            db_mentorinfo['mentor_type'][0],
            db_mentorinfo['mentor_number'][0],
            mentor_num,
            record_count,
            resume_count,
            story_count
        ]
        search_result.append(arr)

    return jsonify({'result': 'success', 'filter_result': search_result})


@app.route('/univ', methods=['GET'])
def get_univ():
    univ = list(db.univ_list.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'univ': univ})


@app.route('/univ_type', methods=['GET'])
def get_univ_type():
    univ = list(db.univ_type.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'univ': univ})


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    recent_login_receive = request.form['recent_login_give']
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "recent_login": recent_login_receive
    }

    find_menti = db.menti.find_one({'email': id_receive, 'password': pw_hash}) or db.menti.find_one(
        {'phone': id_receive, 'password': pw_hash})
    find_mentor = db.mentor.find_one({'phone': id_receive, 'password': pw_hash})

    if find_menti or find_mentor is not None:
        print('ip : ', request.remote_addr)
        if find_menti is not None:
            nickname_find = find_menti['nickname']
            payload = {
                'admin': 'no',
                'number': int(find_menti['number']),
                'id': id_receive,
                'nickname': nickname_find,
                'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
            }
            db.menti.update_one({'email': payload['id']}, {'$set': doc}) and db.menti.update_one(
                {'phone': payload['id']}, {'$set': doc})
        else:
            nickname_find = find_mentor['nickname']
            if request.remote_addr in ['218.232.131.116','127.0.0.1','27.1.3.32']:
                print (request.remote_addr, 'admin login')
                payload = {
                    'admin': 'yes',
                    'id': id_receive,
                    'number': int(find_mentor['number']),
                    'nickname': nickname_find,
                    'login_time': recent_login_receive,
                    'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
                }
            else:
                payload = {
                    'admin': 'no',
                    'number': int(find_mentor['number']),
                    'id': id_receive,
                    'nickname': nickname_find,
                    'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
                }
            db.mentor.update_one({'phone': payload['id']}, {'$set': doc})

        print(payload)
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/register/check_dup', methods=['POST'])
def check_dup():
    nickname_receive = request.form['nickname_give']
    # exists_menti = bool(db.menti.find_one({'nickname': nickname_receive}))
    # exists_mentor = bool(db.mentor.find_one({'nickname': nickname_receive}))
    # return jsonify({'result':'success','exists_menti':exists_menti,'exists_mentori':exists_mentor})

    find_menti = db.menti.find_one({'nickname': nickname_receive})
    find_mentor = db.menti.find_one({'nickname': nickname_receive})

    if find_menti or find_mentor is not None:
        return jsonify({'result': 'fail'})
    else:
        return jsonify({'result': 'success'})


@app.route('/register/email_send', methods=['POST'])
def verify_email_send():
    email_receive = request.form['email_give']
    num = str(math.floor(random.random() * 10000))
    mail_msg = '인증번호는 ' + num + ' 입니다.'

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('leeedward19963@gmail.com', 'hldamhxeuphkssss')
    msg = MIMEText(mail_msg)

    msg['Subject'] = 'READYMATE 회원가입 인증번호입니다.'
    s.sendmail("info@readymate.kr", email_receive, msg.as_string())
    s.quit()

    return jsonify({'result': 'success', 'num': num})


@app.route('/register', methods=['POST'])
def sign_up():
    # 회원가
    v = request.form['v_give']
    email_receive = request.form['email_give']
    phone_receive = request.form['phone_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    register_date_receive = request.form['register_date_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    if v == 'menti':
        birth = request.form['birthArray']
        name_receive = request.form['name_give']
        status_receive = request.form['status_give']
        location_receive = request.form['location_give']
        school_type_receive = request.form['school_type_give']
        global number
        number = (db.mentor.count()) + (db.menti.count()) + 1

        menti_doc = {
            "number": number,
            "pass": "",
            "email": email_receive,
            "phone": phone_receive,
            "password": password_hash,
            "name": name_receive,
            "birth": birth,
            "nickname": nickname_receive,
            "status": status_receive,
            "location": location_receive,
            "school_type": school_type_receive,
            "profile_pic": "",
            "profile_pic_real": f"profile_pics/profile_placeholder_{number % 6}.jpeg",
            "v": v,
            "register_date": register_date_receive,
            "recent_login": ""
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{v}_{number}.{extension}"
            file.save("./static/" + file_path)
            menti_doc["profile_pic"] = filename
            menti_doc["profile_pic_real"] = file_path
        db.menti.insert_one(menti_doc)

        following_doc = {
            "follower_status": v,
            "follower_number": number,
            "action_mentor": [],
            "nonaction_mentor": [],
        }
        db.following.insert_one(following_doc)

    else:
        number = (db.mentor.count()) + (db.menti.count()) + 1
        mentor_doc = {
            "number": number,
            "name": "",
            "email": email_receive,
            "phone": phone_receive,
            "password": password_hash,
            "birth": "",
            "nickname": nickname_receive,
            "profile_pic": "",
            "profile_pic_real": f"profile_pics/profile_placeholder_{number % 3}.png",
            "univAccepted_file": [],
            "univAccepted_file_real": [],
            "univAttending_file": "",
            "univAttending_file_real": "univAttending_files/univAttending_placeholder.png",
            "v": v,
            "register_date": register_date_receive,
            "recent_login": "",
            "record_file": "",
            "record_file_real": "",
            "idcard_file": "",
            "idcard_file_real": "",
            "bank": "",
            "account": ""
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{v}_{number}.{extension}"
            file.save("./static/" + file_path)
            mentor_doc["profile_pic"] = filename
            mentor_doc["profile_pic_real"] = file_path

        # if 'acceptedFile_give' in request.files:
        #     file = request.files["acceptedFile_give"]
        #     filename = secure_filename(file.filename)
        #     extension = filename.split(".")[-1]9
        #     file_path = f"univAccepted_files/{number}.{extension}"
        #     file.save("./static/" + file_path)
        #     mentor_doc["univAccepted_file"] = filename
        #     mentor_doc["univAccepted_file_real"] = file_path

        if 'attendingFile_give' in request.files:
            file = request.files["attendingFile_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"univAttending_files/{number}.{extension}"
            file.save("./static/" + file_path)
            mentor_doc["univAttending_file"] = filename
            mentor_doc["univAttending_file_real"] = file_path
        db.mentor.insert_one(mentor_doc)

        tags = request.form["tags"]
        new_doc = {
            "number": number,
            "tags": tags,
            "grade": "",
            "location": "",
            "mentorinfo": ["", "", "", "", ""],
            "school_type": "",
            "activity": [["", "", ""], ["", "", ""], ["", "", ""]],
            "sns": [["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]],
            "mentor_univ": [],
            "mentor_major": [],
            "mentor_type": [],
            "mentor_number": [],
            "mentor_verified": []
        }
        db.mentor_info.insert_one(new_doc)

        record_doc = {
            "number": number,
            "record_title": "",
            "visit": 0,
            "buy": 0,
            "profit": 0,
            "release": "hide",
            "chart_js_array": [],
            "record_info": "",
            "time":""
        }
        db.recordpaper.insert_one(record_doc)

        following_doc = {
            "follower_status": v,
            "follower_number": number,
            "action_mentor": [],
            "nonaction_mentor": [],
        }
        db.following.insert_one(following_doc)

        followed_doc = {
            "number": number,
            "follower": [],
            "recent_action": "",
            "recent_action_time": ""
        }
        db.followed.insert_one(followed_doc)

    return jsonify({'result': 'success', 'msg': '회원가입을 완료했습니다.', 'number': number})


@app.route('/register_accepted', methods=['POST'])
def register_accepted():
    file = request.files['file']
    my_num = int(request.form['number'])
    filename_array = db.mentor.find_one({'number': my_num})['univAccepted_file']
    file_path_array = db.mentor.find_one({'number': my_num})['univAccepted_file_real']
    filename = secure_filename(file.filename)
    extension = filename.split(".")[-1]
    file_path = f"univAccepted_files/{my_num}-{filename}.{extension}"
    file.save("./static/" + file_path)

    print(filename_array)
    filename_array.append(filename)
    print(filename_array)
    file_path_array.append(file_path)

    doc = {
        "univAccepted_file": filename_array,
        "univAccepted_file_real": file_path_array,
    }
    db.mentor.update_one({'number': my_num}, {'$set': doc})
    return jsonify({'result': 'success'})


@app.route('/find_my_id')
def find_my_id():
    return render_template('find_my_id.html')


@app.route('/find_id', methods=['GET'])
def find_id():
    name_receive = request.args.get("name_give")
    birth_receive = request.args.get("birth_give")

    find_menti = db.menti.find_one({'name': name_receive, 'birth': birth_receive})
    find_mentor = db.mentor.find_one({'name': name_receive, 'birth': birth_receive})
    print(find_mentor)
    print(find_menti)

    if find_menti or find_mentor is not None:
        if find_menti is None:
            id = find_mentor['phone']
            print(id)
            return jsonify({'result': 'success', 'id': id})
        else:
            phone = find_menti['phone']
            email = find_menti['email']
            if phone:
                print(phone)
                return jsonify({'result': 'success', 'id': phone})
            else:
                print(email)
                return jsonify({'result': 'success', 'id': email})
    else:
        return jsonify({'result': 'fail'})


@app.route('/find_my_pw')
def find_my_pw():
    return render_template('find_my_pw.html')


@app.route('/send_link', methods=['POST'])
def send_link():
    name_receive = request.form["name_give"]
    id_receive = request.form["id_give"]
    id_type_receive = request.form["id_type_give"]
    find_menti = db.menti.find_one({'name': name_receive, f'{id_type_receive}': id_receive})
    find_mentor = db.mentor.find_one({'name': name_receive, f'{id_type_receive}': id_receive})

    if find_mentor or find_menti is not None:
        if id_type_receive == 'email':
            num = str(math.floor(random.random() * 100000000))
            link = f'http://readymate.kr/resetpassword/{num}'
            mail_msg = link + ' 비밀번호 재설정 링크입니다. 1시간이내로 접속해서 비밀번호를 재설정해주세요'

            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login('leeedward19963@gmail.com', 'hldamhxeuphkssss')
            msg = MIMEText(mail_msg)

            msg['Subject'] = 'READYMATE 비밀번호 재설정 링크'
            s.sendmail("info@readymate.kr", id_receive, msg.as_string())
            s.quit()

            doc = {
                "resetNum": num,
                "numTime": time.time()
            }
            if find_mentor is None:
                db.menti.update_one({f'{id_type_receive}': id_receive}, {'$set': doc})
            else:
                db.mentor.update_one({f'{id_type_receive}': id_receive}, {'$set': doc})

        else:
            print('문자로 링크 발송')

        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail'})


@app.route('/resetpassword/<num>')
def resetpassword(num):
    find_menti = db.menti.find_one({'resetNum': num})
    find_mentor = db.mentor.find_one({'resetNum': num})
    if find_mentor is None:
        name = find_menti['name']
        return render_template('resetpassword.html', Name=name, Num=num)
    else:
        name = find_mentor['name']
        return render_template('resetpassword.html', Name=name, Num=num)


@app.route('/change_pw', methods=['POST'])
def change_pw():
    password_receive = request.form['password_give']
    num_receive = request.form['num_give']
    time_receive = request.form['time_give']
    print(password_receive, num_receive, time_receive)
    # find_menti = db.menti.find_one({'resetNum': num_receive})
    # find_mentor = db.mentor.find_one({'resetNum': num_receive})
    hash_pw = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        'password': hash_pw,
        'resetNum': None,
        'numTime': None
    }
    find_menti = db.menti.find_one({'resetNum': num_receive})
    find_mentor = db.mentor.find_one({'resetNum': num_receive})
    print(((int(time_receive) / 1000) - 3600), find_menti['numTime'])

    if find_mentor is not None:
        if ((int(time_receive) / 1000) - 3600) < int(find_menti['numTime']):
            db.menti.update_one({'resetNum': num_receive}, {'$set': doc})
            return jsonify({'result': 'success', 'msg': '비밀번호가 변경되었습니다! 새 비밀번호로 로그인해주세요'})
        else:
            return jsonify({'result': 'success', 'msg': '유효시간이 만료되었습니다. 다시 시도해 주세요'})
    elif find_menti is not None:
        if ((int(time_receive) / 1000) - 3600) < int(find_menti['numTime']):
            db.mentor.update_one({'resetNum': num_receive}, {'$set': doc})
            return jsonify({'result': 'success', 'msg': '비밀번호가 변경되었습니다! 새 비밀번호로 로그인해주세요'})
        else:
            return jsonify({'result': 'success', 'msg': '유효시간이 만료되었습니다. 다시 시도해 주세요'})
    else:
        return jsonify({'result': 'fail'})


@app.route('/bio_modal_post', methods=['POST'])
def update_profile():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        nickname_receive = request.form["nickname_give"]
        profile_desc_receive = request.form["profile_desc_give"]
        doc = {
            "nickname": nickname_receive,
            "profile_desc": profile_desc_receive
        }
        db.mentor.update_one({'phone': payload['id']}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index"))


@app.route('/tag_update', methods=['POST'])
def tag_update():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        tags = request.form["tags"]
        print(tags)
        doc = {
            "tags": tags
        }
        find_mentor = db.mentor.find_one({'phone': payload['id']})
        mentor_num = int(find_mentor['number'])
        db.mentor_info.update_one({'number': mentor_num}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index"))


@app.route('/save_myaccount', methods=['POST'])
def save_myaccount():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        name_receive = db.mentor.find_one({'number': int(payload['number'])})['name']
        bank_receive = request.form["bank_give"]
        account_receive = request.form["account_give"]
        doc = {
            # "name": name_receive,
            "bank": bank_receive,
            "account": account_receive,
            "idcard_file": "",
            "idcard_file_real": "idcard_files/idcard_placeholder.png",
        }
        if 'idcard_file_give' in request.files:
            file = request.files["idcard_file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"idcard_files/{name_receive}.{extension}"
            file.save("./static/" + file_path)
            doc["idcard_file"] = filename
            doc["idcard_file_real"] = file_path
        db.mentor.update_one({'number': payload['number']}, {'$set': doc})
        return jsonify({"result": "success"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index"))


@app.route('/update_follow', methods=['POST'])
def update_follow():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요 수 변경
        user_info = db.users.find_one({"phone": payload["phone"]})
        post_username_receive = request.form["post_username_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_username": post_username_receive,
            "phone": user_info["phone"],
            "type": type_receive
        }
        if action_receive == "follow":
            db.follows.insert_one(doc)
        else:
            db.follows.delete_one(doc)
        count = db.follows.count_documents({"post_username": post_username_receive, "type": type_receive})
        print(count)
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/mentorinfo_modal_post', methods=['POST'])
def mentorinfo_modal_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentorinfo_1_receive = request.form["mentorinfo_1_give"]
        mentorinfo_2_receive = request.form["mentorinfo_2_give"]
        mentorinfo_3_receive = request.form["mentorinfo_3_give"]
        mentorinfo_4_receive = request.form["mentorinfo_4_give"]
        mentorinfo_5_receive = request.form["mentorinfo_5_give"]
        mentorinfo_6_receive = request.form["mentorinfo_6_give"]
        location_receive = request.form["location_give"]
        school_type_receive = request.form["school_type_give"]
        grade_receive = request.form["grade_give"]
        mentorinfoArray = [mentorinfo_1_receive, mentorinfo_2_receive, mentorinfo_3_receive, mentorinfo_4_receive,
                           mentorinfo_5_receive, mentorinfo_6_receive]
        doc = {
            "mentorinfo": mentorinfoArray,
            "location": location_receive,
            "school_type": school_type_receive,
            "grade": grade_receive
        }

        find_mentor = db.mentor.find_one({'phone': payload['id']})
        mentor_num = int(find_mentor['number'])
        db.mentor_info.update_one({'number': mentor_num}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.', 'mentorinfoArray': mentorinfoArray})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/activity_modal_post', methods=['POST'])
def activity_modal_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        activity_category_1_receive = request.form["activity_category_1_give"]
        activity_category_2_receive = request.form["activity_category_2_give"]
        activity_category_3_receive = request.form["activity_category_3_give"]
        activity_num_1_receive = request.form["activity_num_1_give"]
        activity_num_2_receive = request.form["activity_num_2_give"]
        activity_num_3_receive = request.form["activity_num_3_give"]
        activity_unit_1_receive = request.form["activity_unit_1_give"]
        activity_unit_2_receive = request.form["activity_unit_2_give"]
        activity_unit_3_receive = request.form["activity_unit_3_give"]
        doc = {
            "activity": [[activity_category_1_receive, activity_num_1_receive, activity_unit_1_receive],
                         [activity_category_2_receive, activity_num_2_receive, activity_unit_2_receive],
                         [activity_category_3_receive, activity_num_3_receive, activity_unit_3_receive]]
        }

        find_mentor = db.mentor.find_one({'phone': payload['id']})
        mentor_num = int(find_mentor['number'])
        db.mentor_info.update_one({'number': mentor_num}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sns_modal_post', methods=['POST'])
def sns_modal_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        sns_category_1_receive = request.form["sns_category_1_give"]
        sns_id_1_receive = request.form["sns_id_1_give"]
        sns_link_1_receive = request.form["sns_link_1_give"]

        sns_category_2_receive = request.form["sns_category_2_give"]
        sns_id_2_receive = request.form["sns_id_2_give"]
        sns_link_2_receive = request.form["sns_link_2_give"]

        sns_category_3_receive = request.form["sns_category_3_give"]
        sns_id_3_receive = request.form["sns_id_3_give"]
        sns_link_3_receive = request.form["sns_link_3_give"]

        sns_category_4_receive = request.form["sns_category_4_give"]
        sns_id_4_receive = request.form["sns_id_4_give"]
        sns_link_4_receive = request.form["sns_link_4_give"]

        sns_category_5_receive = request.form["sns_category_5_give"]
        sns_id_5_receive = request.form["sns_id_5_give"]
        sns_link_5_receive = request.form["sns_link_5_give"]

        doc = {
            "sns": [[sns_category_1_receive, sns_id_1_receive, sns_link_1_receive],
                    [sns_category_2_receive, sns_id_2_receive, sns_link_2_receive],
                    [sns_category_3_receive, sns_id_3_receive, sns_link_3_receive],
                    [sns_category_4_receive, sns_id_4_receive, sns_link_4_receive],
                    [sns_category_5_receive, sns_id_5_receive, sns_link_5_receive]]
        }
        print(doc)
        find_mentor = db.mentor.find_one({'phone': payload['id']})
        mentor_num = int(find_mentor['number'])
        db.mentor_info.update_one({'number': mentor_num}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/resume_save/<int:number>/<time>', methods=['POST'])
def resume_save(number, time):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        find_mentor = db.mentor.find_one({'number': payload['number']})
        mentor_num = find_mentor['number']
        resume_title_receive = request.form["resume_title_give"]
        resume_univ_receive = request.form["resume_univ_give"]
        resume_major_receive = request.form["resume_major_give"]
        resume_type_receive = request.form["resume_type_give"]
        resume_number_receive = request.form["resume_number_give"]
        resume_desc_receive = request.form["resume_desc_give"]
        resume_price_receive = request.form["resume_price_give"]
        resume_1_receive = request.form["resume_1_give"]
        resume_2_receive = request.form["resume_2_give"]
        resume_3_receive = request.form["resume_3_give"]
        resume_4_1_receive = request.form["resume_4_1_give"]
        resume_4_2_receive = request.form["resume_4_2_give"]
        resume_4_3_receive = request.form["resume_4_3_give"]
        resume_time_receive = time
        if db.resume.find_one({'number': number, 'time': time}) is not None:
            resume_DB = db.resume.find_one({'number': number, 'time': time})
            if resume_1_receive == resume_DB['resume_number'][0]:
                resume_1_html = resume_DB['resume_info_1']
            else:
                resume_1_html = resume_1_receive

            if resume_2_receive == resume_DB['resume_number'][1]:
                resume_2_html = resume_DB['resume_info_2']
            else:
                resume_2_html = resume_2_receive

            if resume_3_receive == resume_DB['resume_number'][2]:
                resume_3_html = resume_DB['resume_info_3']
            else:
                resume_3_html = resume_3_receive

            if resume_4_3_receive == resume_DB['resume_number'][5]:
                resume_4_html = resume_DB['resume_info_4']
            else:
                resume_4_html = resume_4_3_receive
            doc = {
                "id": payload['id'],
                "number": mentor_num,
                "visit": 0,
                "resume_title": resume_title_receive,
                "resume_univ": resume_univ_receive,
                "resume_major": resume_major_receive,
                "resume_type": resume_type_receive,
                "resume_class": resume_number_receive,
                "resume_desc": resume_desc_receive,
                "resume_number": [resume_1_receive, resume_2_receive, resume_3_receive, resume_4_1_receive,
                                  resume_4_2_receive, resume_4_3_receive],
                "resume_info_1": resume_1_html,
                "resume_info_2": resume_2_html,
                "resume_info_3": resume_3_html,
                "resume_info_4": resume_4_html,
                "resume_price": resume_price_receive,
                "update_time": resume_time_receive,
                "release": "hide",
                "buy" : "",
                "profit" : ""
            }
            db.resume.update_one({'time': time}, {'$set': doc})
            return jsonify({"result": "success", 'msg': '자기소개서 정보를 수정했습니다'})
        else:
            resume_list = list(db.resume.find({'number': number}))
            resume_check_array = []
            for resume0 in resume_list:
                resume_check_array.append([resume0['resume_univ'], resume0['resume_major']])

            if [resume_univ_receive, resume_major_receive] in resume_check_array:
                return jsonify({"result": "success", 'msg': '이미 해당학적으로 작성된 자기소개서가 있습니다'})
            else:
                doc = {
                    "id": payload['id'],
                    "number": mentor_num,
                    "visit": 0,
                    "resume_title": resume_title_receive,
                    "resume_univ": resume_univ_receive,
                    "resume_major": resume_major_receive,
                    "resume_type": resume_type_receive,
                    "resume_class": resume_number_receive,
                    "resume_desc": resume_desc_receive,
                    "resume_number": [resume_1_receive, resume_2_receive, resume_3_receive, resume_4_1_receive,
                                      resume_4_2_receive, resume_4_3_receive],
                    "resume_info_1": resume_1_receive,
                    "resume_info_2": resume_2_receive,
                    "resume_info_3": resume_3_receive,
                    "resume_info_4": resume_4_3_receive,
                    "resume_price": resume_price_receive,
                    "time": resume_time_receive,
                    "update_time": resume_time_receive,
                    "release": "hide"
                }
                db.resume.insert_one(doc)

                doc2 = {
                    "number": mentor_num,
                    "category": "resume",
                    "time": resume_time_receive,
                    "who": []
                }
                db.like.insert_one(doc2)

                doc3 = {
                    "number": mentor_num,
                    "category": "resume",
                    "time": resume_time_receive,
                    "who": []
                }
                db.bookmark.insert_one(doc3)

                doc4 = {
                    "number": mentor_num,
                    "category": "resume",
                    "time": resume_time_receive,
                    "reply": []
                }
                db.reply.insert_one(doc4)
                return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/resume_comment_save', methods=['POST'])
def resume_comment_save():
    data = request.get_json("resume_comment_give")
    resume_comment_receive = data['resume_comment_give']
    resume_time_receive = request.args.get('time')
    print(resume_comment_receive)
    doc = {
        "resume_comment": resume_comment_receive
    }
    db.resume.update_one({'time': resume_time_receive}, {'$set': doc})
    return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})


@app.route('/story_save/<int:mentor_number>/<time>', methods=['POST'])
def story_save(mentor_number, time):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        story_title_receive = request.form["story_title_give"]
        story_category_receive = request.form["story_category_give"]
        story_desc_receive = request.form["story_desc_give"]
        story_time_receive = request.form["story_time_give"]
        find_story = db.story.find_one({'number':mentor_number,'time':time})
        if find_story is not None:
            doc = {
                "number": mentor_number,
                "story_title": story_title_receive,
                "story_tag": story_category_receive,
                "story_desc": story_desc_receive,
                "update_time": story_time_receive,
            }
            db.story.update_one({'time': time,'number':mentor_number}, {'$set': doc})
            return jsonify({"result": "success", 'msg': '수정되었습니다'})
        else:
            doc = {
                "number": mentor_number,
                "visit": 0,
                "release": "sell",
                "story_title": story_title_receive,
                "story_tag": story_category_receive,
                "story_desc": story_desc_receive,
                "time": story_time_receive,
                "update_time": story_time_receive,
            }
            db.story.insert_one(doc)

            doc2 = {
                "number": mentor_number,
                "category": "story",
                "time": story_time_receive,
                "who": []
            }
            db.like.insert_one(doc2)

            doc3 = {
                "number": mentor_number,
                "category": "story",
                "time": story_time_receive,
                "who": []
            }
            db.bookmark.insert_one(doc3)

            doc4 = {
                "number": mentor_number,
                "category": "story",
                "time": story_time_receive,
                "reply": []
            }
            db.reply.insert_one(doc4)

            return jsonify({"result": "success", 'msg': '스토리를 작성했습니다'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/story_sellyes', methods=['POST'])
def story_sellyes():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        sell = request.form["sell"]
        time = request.args.get("time")
        doc = {
            "release": sell
        }
        db.story.update_one({'number': payload['number'], 'time': time}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/resume_sellyes/<int:number>/<time>', methods=['POST'])
def resume_sellyes(number, time):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        date_now = datetime.now()
        sell = request.form["sell"]
        doc = {
            "release": sell,
            "release_modify_date": date_now
        }
        db.resume.update_one({'number': payload['number'], 'time': time}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/recordpaper_sellyes/<int:number>', methods=['POST'])
def recordpaper_sellyes(number):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        date_now = datetime.now()
        sell = request.form["sell"]
        doc = {
            "release": sell,
            "release_modify_date": date_now
        }
        db.recordpaper.update_one({'number': payload['number']}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/save_rec_post', methods=['POST'])
def save_rec_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        record_title_receive = request.form["record_title_give"]
        record_desc_receive = request.form["record_desc_give"]
        record_price_receive = request.form["record_price_give"]
        record_time_receive = request.form["record_time_give"]
        if db.recordpaper.find_one({'number': payload['number']})['time'] != '':
            update_time = record_time_receive
            doc = {
                "record_title": record_title_receive,
                "record_desc": record_desc_receive,
                "record_price": record_price_receive,
                "update_time": update_time,
                "sell": "hide"
            }
            db.recordpaper.update_one({'number': payload['number']}, {'$set': doc})
            return jsonify({"result": "success", 'msg': '생활기록부 정보를 수정했습니다'})
        else:
            doc = {
                "record_title": record_title_receive,
                "record_desc": record_desc_receive,
                "record_price": record_price_receive,
                "time": record_time_receive,
                "update_time": record_time_receive,
                "sell": "hide"
            }
            db.recordpaper.update_one({'number': payload['number']}, {'$set': doc})

            rec_doc = {
                "record_file": "",
                "record_file_real": "record_files/record_file_placeholder.png"
            }
            if 'file_give' in request.files:
                file = request.files["file_give"]
                filename = secure_filename(file.filename)
                file_path = f"record_files/{payload['number']}_{filename}"
                file.save("./static/" + file_path)
                rec_doc["record_file"] = filename
                rec_doc["record_file_real"] = file_path
            db.mentor.update_one({'number': payload['number']}, {'$set': rec_doc})

            doc2 = {
                "number": payload["number"],
                "category": "recordpaper",
                "who": []
            }
            db.like.insert_one(doc2)

            doc3 = {
                "number": payload["number"],
                "category": "recordpaper",
                "who": []
            }
            db.bookmark.insert_one(doc3)

            doc4 = {
                "number": payload["number"],
                "category": "recordpaper",
                "time": "",
                "reply": []
            }
            db.reply.insert_one(doc4)
            return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# @app.route('/save_comment_post', methods=['POST'])
# def save_comment_post():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         data = request.get_json("record_comment_give")
#         record_comment_receive = data['record_comment_give']
#         print(record_comment_receive)
#
#         doc = {
#             "record_comment": record_comment_receive
#         }
#         db.recordpaper.update_one({'number': payload['number']}, {'$set': doc})
#         return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))


@app.route('/mentor_univ_add', methods=['POST'])
def mentor_univ_add():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        univArray = request.form["univArray_give"]
        majorArray = request.form["majorArray_give"]
        typeArray = request.form["typeArray_give"]
        schoolNumArray = request.form["schoolNumArray_give"]
        verifiedArray = request.form["verifiedArray_give"]
        print(univArray, majorArray, typeArray, schoolNumArray, verifiedArray)

        find_mentor = db.mentor_info.find_one({'number': payload['number']})
        mentor_univ = find_mentor['mentor_univ']
        mentor_major = find_mentor['mentor_major']
        mentor_number = find_mentor['mentor_number']
        mentor_type = find_mentor['mentor_type']
        mentor_verified = find_mentor['mentor_verified']
        print(mentor_univ, mentor_major, mentor_number, mentor_type, mentor_verified)

        new_mu = mentor_univ + [univArray]
        new_mm = mentor_major + [majorArray]
        new_mn = mentor_number + [schoolNumArray]
        new_mt = mentor_type + [typeArray]
        new_mv = mentor_verified + [verifiedArray]
        print(new_mu, new_mm, new_mn, new_mt, new_mv)

        doc = {
            "mentor_univ": new_mu,
            "mentor_major": new_mm,
            "mentor_type": new_mt,
            "mentor_number": new_mn,
            "mentor_verified": new_mv
        }
        db.mentor_info.update_one({'number': payload['number']}, {'$set': doc})

        return jsonify({"result": "success", 'msg': '합격 대학이 업데이트되었습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/recordpaper_get', methods=['GET'])
def recordpaper_get():
    number_receive = int(request.args.get('number_give'))
    find_info = db.mentor_info.find_one({'number': number_receive})

    mentor_tag = find_info['tags']
    record_reply = list(db.reply.find({'number': number_receive, 'category': 'recordpaper'}))
    reply_count = str(record_reply[0]['reply']).count('일')

    record_reply_array = []
    for reply in record_reply:
        record_reply_array.append([reply['time'], reply['reply']])
        print('record_reply_array : ', record_reply_array)
    return jsonify(
        {"result": "success", "reply_count": reply_count, "record_reply": record_reply_array, "mentor_tag": mentor_tag})


@app.route('/resume_get', methods=['GET'])
def resume_get():
    number_receive = int(request.args.get('number_give'))
    time_receive = request.args.get('time_give')
    print(time_receive)
    find_resume = db.resume.find_one({'number': number_receive}, {'time': time_receive})
    print(find_resume)
    find_info = db.mentor_info.find_one({'number': number_receive})
    mentor_tag = find_info['tags']

    resume_reply = list(db.reply.find({'number': number_receive, 'category': 'resume', 'time': time_receive}))
    reply_count = str(resume_reply[0]['reply']).count('일')
    # print(community_reply)
    resume_reply_array = []
    for reply in resume_reply:
        resume_reply_array.append([reply['time'], reply['reply']])
    return jsonify(
        {"result": "success", "reply_count": reply_count, "resume_reply": resume_reply_array, "mentor_tag": mentor_tag})


@app.route('/story_get', methods=['GET'])
def story_get():
    number_receive = int(request.args.get('number_give'))
    time_receive = request.args.get('time_give')
    print(number_receive)
    find_story = db.story.find_one({'number': number_receive})
    find_mentor = db.mentor.find_one({'number': number_receive})
    find_info = db.mentor_info.find_one({'number': number_receive})

    mentor_story = find_story['story_desc']
    mentor_title = find_story['story_title']
    mentor_nickname = find_mentor['nickname']
    mentor_tag = find_info['tags']
    mentor_univ = find_info['mentor_univ'][0]
    mentor_major = find_info['mentor_major'][0]
    mentor_number = find_info['mentor_number'][0]
    mentor_type = find_info['mentor_type'][0]

    story_reply = list(db.reply.find({'number': number_receive, 'category': 'story', 'time': time_receive}))
    reply_count = str(story_reply[0]['reply']).count('일')
    story_reply_array = []
    for reply in story_reply:
        story_reply_array.append([reply['time'], reply['reply']])
    return jsonify({"result": "success", "reply_count": reply_count, "story_reply": story_reply_array,
                    "mentor_story": mentor_story,
                    "mentor_title": mentor_title, "mentor_nickname": mentor_nickname, "mentor_tag": mentor_tag,
                    "mentor_univ": mentor_univ, "mentor_major": mentor_major, "mentor_number": mentor_number,
                    "mentor_type": mentor_type})


@app.route('/community_get', methods=["GET"])
def community_get():
    number_receive = int(request.args.get('number_give'))

    mentor_community = list(db.community.find({'number': number_receive}))
    # print(mentor_community)
    community_array = []
    for com in mentor_community:
        community_array.append([com['title'], com['notice'], com['desc'], com['time']])

    mentor_notice = list(db.community.find({'number': number_receive, 'notice': 'on'}))
    # print(mentor_notice)
    notice_array = []
    for notice in mentor_notice:
        notice_array.append([notice['title'], notice['desc'], notice['time']])

    community_like = list(db.like.find({'number': number_receive, 'category': 'community'}))
    # print(community_like)
    community_like_array = []
    for like in community_like:
        community_like_array.append([like['time'], like['who']])

    community_reply = list(db.reply.find({'number': number_receive, 'category': 'community'}))
    # print(community_reply)
    community_reply_array = []
    for reply in community_reply:
        community_reply_array.append([reply['time'], reply['reply']])

    return jsonify({"result": "success", "community": community_array, "notice": notice_array,
                    "community_like": community_like_array, "community_reply": community_reply_array})


@app.route('/mentor_univ_get', methods=['GET'])
def mentor_univ_get():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        find_mentor = db.mentor_info.find_one({'number': payload['number']})
        mentor_univ = find_mentor['mentor_univ']
        mentor_major = find_mentor['mentor_major']
        mentor_type = find_mentor['mentor_type']
        mentor_number = find_mentor['mentor_number']
        mentor_verified = find_mentor['mentor_verified']
        return jsonify(
            {"result": "success", "mentor_univ": mentor_univ, "mentor_major": mentor_major, "mentor_type": mentor_type,
             "mentor_number": mentor_number, "mentor_verified": mentor_verified})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/mentor_univ_represent', methods=['POST'])
def mentor_univ_represent():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        index_receive = request.form["index_give"]
        find_mentor = db.mentor_info.find_one({'number': payload['number']})
        mentor_univ = find_mentor['mentor_univ']
        mentor_major = find_mentor['mentor_major']
        mentor_type = find_mentor['mentor_type']
        mentor_number = find_mentor['mentor_number']

        target_mentor_univ = mentor_univ[int(index_receive)]
        del mentor_univ[int(index_receive)]
        mentor_univ.insert(0, target_mentor_univ)

        target_mentor_major = mentor_major[int(index_receive)]
        del mentor_major[int(index_receive)]
        mentor_major.insert(0, target_mentor_major)

        target_mentor_type = mentor_type[int(index_receive)]
        del mentor_type[int(index_receive)]
        mentor_type.insert(0, target_mentor_type)

        target_mentor_number = mentor_number[int(index_receive)]
        del mentor_number[int(index_receive)]
        mentor_number.insert(0, target_mentor_number)

        doc = {
            "mentor_univ": mentor_univ,
            "mentor_major": mentor_major,
            "mentor_type": mentor_type,
            "mentor_number": mentor_number
        }

        db.mentor_info.update_one({'number': payload['number']}, {'$set': doc})
        return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/mentor_univ_remove', methods=['POST'])
def mentor_univ_remove():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        index_receive = request.form["index_give"]
        find_mentor = db.mentor_info.find_one({'number': payload['number']})
        mentor_univ = find_mentor['mentor_univ']
        mentor_major = find_mentor['mentor_major']
        mentor_type = find_mentor['mentor_type']
        mentor_number = find_mentor['mentor_number']
        mentor_verified = find_mentor['mentor_verified']

        del mentor_univ[int(index_receive)]
        del mentor_major[int(index_receive)]
        del mentor_type[int(index_receive)]
        del mentor_number[int(index_receive)]
        del mentor_verified[int(index_receive)]

        doc = {
            "mentor_univ": mentor_univ,
            "mentor_major": mentor_major,
            "mentor_type": mentor_type,
            "mentor_number": mentor_number,
            "mentor_verified": mentor_verified
        }
        db.mentor_info.update_one({'number': payload['number']}, {'$set': doc})
        return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/community_post', methods=['POST'])
def community_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        community_title_receive = request.form["community_title_give"]
        community_notice_receive = request.form["community_notice_give"]
        community_desc_receive = request.form["community_desc_give"]
        community_time_receive = request.form["community_time_give"]
        likes_receive = request.form["likes_give"]
        reply_receive = request.form["reply_give"]

        find_mentor = db.mentor.find_one({'phone': payload['id']})
        mentor_num = int(find_mentor['number'])

        doc = {
            "number": mentor_num,
            "title": community_title_receive,
            "notice": community_notice_receive,
            "desc": community_desc_receive,
            "time": community_time_receive,
        }
        db.community.insert_one(doc)

        doc2 = {
            "number": mentor_num,
            "category": "community",
            "time": community_time_receive,
            "who": []
        }
        db.like.insert_one(doc2)

        doc3 = {
            "number": mentor_num,
            "category": "community",
            "time": community_time_receive,
            "reply": []
        }
        db.reply.insert_one(doc3)

        my_follower = db.followed.find_one({"number": mentor_num})['follower']
        print('my_follower', my_follower)
        for follower in my_follower:
            print('follower', follower)
            follower_follwing = db.following.find_one(
                {"follower_status": follower[0], "follower_number": int(follower[1])})
            action_array = follower_follwing['action_mentor']
            nonaction_array = follower_follwing['nonaction_mentor']
            if mentor_num in nonaction_array:
                nonaction_array.remove(mentor_num)
                action_array.append(mentor_num)
                doc = {
                    "nonaction_mentor": nonaction_array,
                    "action_mentor": action_array
                }
                db.following.update_one({'follower_number': int(follower[1]), 'follower_status': follower[0]},
                                        {'$set': doc})

        return jsonify({"result": "success"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/remove_community', methods=['POST'])
def remove_community():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        time_receive = request.form["time_give"]
        find_mentor = db.mentor.find_one({'phone': payload['id']})
        mentor_num = int(find_mentor['number'])

        db.community.delete_one({"number": mentor_num, 'time': time_receive})
        db.like.delete_one({"number": mentor_num, 'time': time_receive})
        db.reply.delete_one({"number": mentor_num, 'time': time_receive})

        return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/community_like', methods=['POST'])
def community_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        number_receive = request.form['number_give']
        time_receive = request.form['time_give']
        action_receive = request.form['action_give']

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        else:
            me_info = me_mentor
            status = 'mentor'

        my_number = me_info['number']
        print([status, my_number])

        community_like = db.like.find_one(
            {'number': int(number_receive), 'category': 'community', 'time': time_receive})
        print(community_like)
        who_array = community_like['who']

        if (action_receive == 'like') and (int(number_receive) != payload['number']):
            print('like')
            who_array.append([status, my_number])
            print(who_array)
            db.like.update_one({'number': int(number_receive), 'category': 'community', 'time': time_receive},
                               {'$set': {'who': who_array}})
            title = db.community.find_one({'number': int(number_receive), 'time': time_receive})['title']
            doc = {
                'to_status': 'mentor',
                'to_number': int(number_receive),
                'category': '커뮤니티를',
                'which_data': title,
                'action': '좋아합니다',
                'when': '',
                'from_nickname': payload['nickname'],
                'from_image': me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)
            return jsonify({"result": "success"})

        elif action_receive == 'unlike':
            print('unlike')
            who_array.remove([status, my_number])
            print(who_array)
            db.like.update_one({'number': int(number_receive), 'category': 'community', 'time': time_receive},
                               {'$set': {'who': who_array}})
        return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/story_like', methods=['POST'])
def story_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        number_receive = request.form['number_give']
        time_receive = request.form['time_give']
        action_receive = request.form['action_give']

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        else:
            me_info = me_mentor
            status = 'mentor'

        my_number = me_info['number']
        print(my_number)

        story_like = db.like.find_one({'number': int(number_receive), 'category': 'story', 'time': time_receive})
        print(story_like)
        who_array = story_like['who']

        if action_receive == 'like':
            print('like')
            who_array.append(my_number)
            print(who_array)
            db.like.update_one({'number': int(number_receive), 'category': 'story', 'time': time_receive},
                               {'$set': {'who': who_array}})

            return jsonify({"result": "success"})

        elif action_receive == 'unlike':
            print('unlike')
            who_array.remove(my_number)
            print(who_array)
            db.like.update_one({'number': int(number_receive), 'category': 'story', 'time': time_receive},
                               {'$set': {'who': who_array}})

            return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/story_bookmark', methods=['POST'])
def story_bookmark():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        now = datetime.now()
        now_in_form = now.strftime("%Y/%m/%d, %H:%M:%S")
        number_receive = request.form['number_give']
        category_receive = request.form['category_give']
        time_receive = request.form['time_give']
        action_receive = request.form['action_give']

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
        else:
            me_info = me_mentor

        my_number = me_info['number']
        print(my_number)

        story_bookmark = db.bookmark.find_one(
            {'number': int(number_receive), 'category': 'story', 'time': time_receive})
        print(story_bookmark)
        who_array = story_bookmark['who']

        if action_receive == 'mark':
            print('mark')
            who_array.append(my_number)
            print(who_array)
            db.bookmark.update_one({'number': int(number_receive), 'category': 'story', 'time': time_receive},
                                   {'$set': {'who': who_array}})
            doc = {
                "number": int(my_number),
                "miniTab": 'bookmark',
                "category": category_receive,
                "time": time_receive,
                "mentor_num": int(number_receive),
                "update_time": now_in_form
            }
            db.menti_data.insert_one(doc)
            return jsonify({"result": "success"})

        elif action_receive == 'unmark':
            print('unmark')
            who_array.remove(my_number)
            print(who_array)
            db.bookmark.update_one({'number': int(number_receive), 'category': 'story', 'time': time_receive},
                                   {'$set': {'who': who_array}})
            db.menti_data.delete_one({'number': int(my_number), 'miniTab': 'bookmark', 'category': category_receive, 'mentor_num': int(number_receive), 'time': time_receive})
            return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/resume_like', methods=['POST'])
def resume_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        number_receive = request.form['number_give']
        time_receive = request.form['time_give']
        action_receive = request.form['action_give']

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
        else:
            me_info = me_mentor

        my_number = me_info['number']
        print(my_number)

        resume_like = db.like.find_one({'number': int(number_receive), 'category': 'resume', 'time': time_receive})
        print(resume_like)
        who_array = resume_like['who']

        if action_receive == 'like':
            print('like')
            who_array.append(my_number)
            print(who_array)
            db.like.update_one({'number': int(number_receive), 'category': 'resume', 'time': time_receive},
                               {'$set': {'who': who_array}})

            return jsonify({"result": "success"})

        elif action_receive == 'unlike':
            print('unlike')
            who_array.remove(my_number)
            print(who_array)
            db.like.update_one({'number': int(number_receive), 'category': 'resume', 'time': time_receive},
                               {'$set': {'who': who_array}})

            return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/resume_bookmark', methods=['POST'])
def resume_bookmark():
    token_receive = request.cookies.get('mytoken')
    try:
        now = datetime.now()
        now_in_form = now.strftime("%Y/%m/%d, %H:%M:%S")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        number_receive = request.form['number_give']
        category_receive = request.form['category_give']
        time_receive = request.form['time_give']
        action_receive = request.form['action_give']

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
        else:
            me_info = me_mentor

        my_number = me_info['number']
        print(my_number)

        resume_bookmark = db.bookmark.find_one(
            {'number': int(number_receive), 'category': 'resume', 'time': time_receive})
        print(resume_bookmark)
        who_array = resume_bookmark['who']

        if action_receive == 'mark':
            print('mark')
            who_array.append(my_number)
            print(who_array)
            db.bookmark.update_one({'number': int(number_receive), 'category': 'resume', 'time': time_receive},
                                   {'$set': {'who': who_array}})
            doc = {
                "number": int(my_number),
                "miniTab": 'bookmark',
                "category": category_receive,
                "time": time_receive,
                "mentor_num": int(number_receive),
                "update_time": now_in_form

            }
            db.menti_data.insert_one(doc)
            return jsonify({"result": "success"})

        elif action_receive == 'unmark':
            print('unmark')
            who_array.remove(my_number)
            print(who_array)
            db.bookmark.update_one({'number': int(number_receive), 'category': 'resume', 'time': time_receive},
                                   {'$set': {'who': who_array}})
            db.menti_data.delete_one({"number": int(my_number), 'miniTab': 'bookmark', 'category': category_receive, 'mentor_num': int(number_receive), 'time': time_receive})
            return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/bookmark_remove', methods=['POST'])
def bookmark_remove():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        number_receive = request.form['number_give']
        category_receive = request.form['category_give']
        time_receive = request.form['time_give']

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
        else:
            me_info = me_mentor

        my_number = me_info['number']
        print(my_number)

        if category_receive == 'resume':
            resume_bookmark = db.bookmark.find_one(
                {'number': int(number_receive), 'category': 'resume', 'time': time_receive})
            print(resume_bookmark)
            who_array = resume_bookmark['who']
            who_array.remove(my_number)
            db.bookmark.update_one({'number': int(number_receive), 'category': 'resume', 'time': time_receive},
                                   {'$set': {'who': who_array}})
            db.menti_data.delete_one({"number": int(my_number), 'miniTab': 'bookmark', 'category': category_receive, 'mentor_num': int(number_receive), 'time': time_receive})
        elif category_receive == 'recordpaper':
            record_bookmark = db.bookmark.find_one({'number': int(number_receive), 'category': 'recordpaper'})
            print(record_bookmark)
            who_array = record_bookmark['who']
            who_array.remove(my_number)
            print(who_array)
            db.bookmark.update_one({'number': int(number_receive), 'category': 'recordpaper'},
                                   {'$set': {'who': who_array}})
            db.menti_data.delete_one({'number': int(my_number), 'miniTab': 'bookmark', 'category': category_receive,
                                      'mentor_num': int(number_receive)})
        else:
            story_bookmark = db.bookmark.find_one(
                {'number': int(number_receive), 'category': 'story', 'time': time_receive})
            print(story_bookmark)
            who_array = story_bookmark['who']
            who_array.remove(my_number)
            print(who_array)
            db.bookmark.update_one({'number': int(number_receive), 'category': 'story', 'time': time_receive},
                                   {'$set': {'who': who_array}})
            db.menti_data.delete_one({'number': int(my_number), 'miniTab': 'bookmark', 'category': category_receive,
                                      'mentor_num': int(number_receive), 'time': time_receive})
        return jsonify({"result": "success"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/wishlist_remove', methods=['POST'])
def wishlist_remove():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        number_receive = request.form['number_give']
        category_receive = request.form['category_give']
        time_receive = request.form['time_give']

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
        else:
            me_info = me_mentor

        my_number = me_info['number']
        print(my_number)

        if category_receive == 'resume':
            db.menti_data.delete_one({"number": int(my_number), 'miniTab': 'wishlist', 'category': category_receive, 'mentor_num': int(number_receive), 'time': time_receive})
        else:
            db.menti_data.delete_one({'number': int(my_number), 'miniTab': 'wishlist', 'category': category_receive,
                                      'mentor_num': int(number_receive)})
        return jsonify({"result": "success"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/record_like', methods=['POST'])
def record_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        number_receive = request.form['number_give']
        action_receive = request.form['action_give']

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
        else:
            me_info = me_mentor

        my_number = me_info['number']
        print(my_number)

        record_like = db.like.find_one({'number': int(number_receive), 'category': 'recordpaper'})
        print(record_like)
        who_array = record_like['who']

        if action_receive == 'like':
            print('like')
            who_array.append(my_number)
            print(who_array)
            db.like.update_one({'number': int(number_receive), 'category': 'recordpaper'}, {'$set': {'who': who_array}})

            return jsonify({"result": "success"})

        elif action_receive == 'unlike':
            print('unlike')
            who_array.remove(my_number)
            print(who_array)
            db.like.update_one({'number': int(number_receive), 'category': 'recordpaper'}, {'$set': {'who': who_array}})

            return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/record_bookmark', methods=['POST'])
def record_bookmark():
    token_receive = request.cookies.get('mytoken')
    try:
        now = datetime.now()
        now_in_form = now.strftime("%Y/%m/%d, %H:%M:%S")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        category_receive = request.form['category_give']
        number_receive = request.form['number_give']
        action_receive = request.form['action_give']

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
        else:
            me_info = me_mentor

        my_number = me_info['number']
        print(my_number)

        record_bookmark = db.bookmark.find_one({'number': int(number_receive), 'category': 'recordpaper'})
        print(record_bookmark)
        who_array = record_bookmark['who']

        if action_receive == 'mark':
            print('mark')
            who_array.append(my_number)
            print(who_array)
            db.bookmark.update_one({'number': int(number_receive), 'category': 'recordpaper'},
                                   {'$set': {'who': who_array}})
            doc = {
                "number": int(my_number),
                "miniTab": 'bookmark',
                "category": category_receive,
                "mentor_num": int(number_receive),
                "update_time": now_in_form
            }
            db.menti_data.insert_one(doc)
            return jsonify({"result": "success"})

        elif action_receive == 'unmark':
            print('unmark')
            who_array.remove(my_number)
            print(who_array)
            db.bookmark.update_one({'number': int(number_receive), 'category': 'recordpaper'},
                                   {'$set': {'who': who_array}})
            db.menti_data.delete_one({'number': int(my_number), 'miniTab': 'bookmark', 'category': category_receive, 'mentor_num': int(number_receive)})
            return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/reply', methods=['POST'])
def reply():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentor_num = int(request.form['mentor_num'])
        which_community = str(request.form['which_community'])
        reply_text = str(request.form['reply_text'])
        reply_time = str(request.form['reply_time'])

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        else:
            me_info = me_mentor
            status = 'mentor'

        my_number = me_info['number']
        print([status, my_number])

        row = db.reply.find_one({'number': mentor_num, 'time': which_community})
        reply_array = row['reply']

        my_reply = [[status, my_number], reply_text, reply_time, []]
        reply_array.append(my_reply)
        print(reply_array)

        db.reply.update_one({'number': mentor_num, 'category': 'community', 'time': which_community},
                            {'$set': {'reply': reply_array}})
        if (status != 'mentor') or (int(payload['number']) != mentor_num):
            print('alert insert')
            community_title = db.community.find_one({'time': which_community})['title']
            doc = {
                'to_status': 'mentor',
                'to_number': mentor_num,
                'category': '커뮤니티에',
                'which_data': community_title,
                'action': '댓글을 작성하였습니다',
                'when': reply_time,
                'from_nickname': payload['nickname'],
                'from_image': me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)
        return jsonify({"result": "success", "reply_array": reply_array})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/reply_to_reply', methods=['POST'])
def reply_to_reply():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentor_num = int(request.form['mentor_num'])
        which_community = str(request.form['which_community'])
        which_mother = str(request.form['which_mother'])
        re_reply_text = str(request.form['re_reply_text'])
        re_reply_time = str(request.form['re_reply_time'])

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        else:
            me_info = me_mentor
            status = 'mentor'

        my_number = me_info['number']
        print([status, my_number])

        row = db.reply.find_one({'number': mentor_num, 'time': which_community})
        reply_array = row['reply']

        my_reply = [[status, my_number], re_reply_text, re_reply_time]
        for miniArray in reply_array:
            if miniArray[2] == which_mother:
                miniArray[3].append(my_reply)
                reply_target = miniArray[0]
                print('reply_array:', reply_array)
                print(reply_target)
        # reply_array.append(my_reply)
        # print(reply_array)

        db.reply.update_one({'number': mentor_num, 'category': 'community', 'time': which_community},
                            {'$set': {'reply': reply_array}})

        if int(reply_target[1]) != payload['number']:
            doc = {
                'to_status': reply_target[0],
                'to_number': int(reply_target[1]),
                'category': '댓글에',
                'which_data': '커뮤니티',
                'action': '답글을 작성하였습니다',
                'when': re_reply_time,
                'from_nickname': payload['nickname'],
                'from_image': me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)
        return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/reply_setting', methods=['GET'])
def reply_setting():
    status_array = request.args.get('statusArray').split(',')
    del status_array[0]
    num_array = request.args.get('numArray').split(',')
    del num_array[0]
    print(status_array)
    print(num_array)

    pic_real_array = []
    for status, number in zip(status_array, num_array):
        if status == 'mentor':
            find_person = db.mentor.find_one({'number': int(number)})
            class_name = 'mentor,' + number
        else:
            find_person = db.menti.find_one({'number': int(number)})
            class_name = 'menti,' + number

        pic_real_array.append([class_name, find_person['profile_pic_real'], find_person['nickname']])

    print(pic_real_array)

    return jsonify({"result": "success", "picArray": pic_real_array})


@app.route('/remove_reply', methods=['POST'])
def remove_reply():
    mentor_num = int(request.form['mentor_num'])
    which_community = request.form['which_community']
    which_time = request.form['which_time']

    row = db.reply.find_one({'number': mentor_num, 'time': which_community})
    reply_array = row['reply']
    for reply in reply_array:
        if reply[2] == which_time:
            reply_array.remove(reply)

    print(reply_array)
    db.reply.update_one({'number': mentor_num, 'category': 'community', 'time': which_community},
                        {'$set': {'reply': reply_array}})

    return jsonify({"result": "success"})


@app.route('/remove_re_reply', methods=['POST'])
def remove_re_reply():
    mentor_num = int(request.form['mentor_num'])
    which_community = request.form['which_community']
    which_mother = request.form['which_mother']
    which_time = request.form['which_time']

    row = db.reply.find_one({'number': mentor_num, 'time': which_community})
    reply_array = row['reply']

    for reply in reply_array:
        re_reply_array = reply[3]
        for re_reply in re_reply_array:
            if re_reply[2] == which_time:
                re_reply_array.remove(re_reply)

    db.reply.update_one({'number': mentor_num, 'category': 'community', 'time': which_community},
                        {'$set': {'reply': reply_array}})

    return jsonify({"result": "success"})


@app.route('/follow', methods=['POST'])
def follow():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # received infos
        mentor_num = int(request.form['mentor_num'])
        action = request.form['action']

        # me info
        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        else:
            me_info = me_mentor
            status = 'mentor'

        me_in_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        mentor_in_followed = db.followed.find_one({'number': mentor_num})

        action_mentor_array = me_in_following['action_mentor']
        nonaction_mentor_array = me_in_following['nonaction_mentor']
        mentor_followed_array = mentor_in_followed['follower']

        if action == 'follow':
            print('follow')
            action_mentor_array.append(mentor_num)
            mentor_followed_array.append([status, int(me_info['number'])])

            db.following.update_one({'follower_status': status, 'follower_number': int(me_info['number'])},
                                    {'$set': {'action_mentor': action_mentor_array}})
            db.followed.update_one({'number': mentor_num}, {'$set': {'follower': mentor_followed_array}})
            doc = {
                'to_status': 'mentor',
                'to_number': mentor_num,
                'category': '계정을',
                'which_data': '내',
                'action': '팔로우하였습니다',
                'when': '',
                'from_nickname': payload['nickname'],
                'from_image': me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)
            return jsonify({"result": "success"})

        else:
            if mentor_num in action_mentor_array:
                action_mentor_array.remove(mentor_num)
            else:
                nonaction_mentor_array.remove(mentor_num)
            mentor_followed_array.remove([status, int(me_info['number'])])

            db.following.update_one({'follower_status': status, 'follower_number': int(me_info['number'])}, {
                '$set': {'action_mentor': action_mentor_array, 'nonaction_mentor': nonaction_mentor_array}})
            db.followed.update_one({'number': mentor_num}, {'$set': {'follower': mentor_followed_array}})
            return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/reply_story', methods=['POST'])
def reply_story():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentor_num = int(request.form['mentor_num'])
        which_story = str(request.form['which_story'])
        reply_text = str(request.form['reply_text'])
        reply_time = str(request.form['reply_time'])

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        else:
            me_info = me_mentor
            status = 'mentor'

        my_number = me_info['number']
        print([status, my_number])

        row = db.reply.find_one({'number': mentor_num, 'time': which_story})
        reply_array = row['reply']

        my_reply = [[status, my_number], reply_text, reply_time, []]
        reply_array.append(my_reply)
        print(reply_array)

        db.reply.update_one({'number': mentor_num, 'category': 'story', 'time': which_story},
                            {'$set': {'reply': reply_array}})
        if (status != 'mentor') or (int(payload['number']) != mentor_num):
            print('alert insert')
            doc = {
                'to_status': 'mentor',
                'to_number': mentor_num,
                'category': '스토리에',
                'which_data': reply_text,
                'action': '댓글을 작성하였습니다',
                'when': reply_time,
                'from_nickname': payload['nickname'],
                'from_image': me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)
        return jsonify({"result": "success", "reply_array": reply_array})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/reply_to_reply_story', methods=['POST'])
def reply_to_reply_story():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentor_num = int(request.form['mentor_num'])
        which_story = str(request.form['which_story'])
        which_mother = str(request.form['which_mother'])
        re_reply_text = str(request.form['re_reply_text'])
        re_reply_time = str(request.form['re_reply_time'])

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        else:
            me_info = me_mentor
            status = 'mentor'

        my_number = me_info['number']
        print([status, my_number])

        row = db.reply.find_one({'number': mentor_num, 'time': which_story})
        reply_array = row['reply']

        my_reply = [[status, my_number], re_reply_text, re_reply_time]
        for miniArray in reply_array:
            if miniArray[2] == which_mother:
                miniArray[3].append(my_reply)
                reply_target = miniArray[0]
                print('reply_array:', reply_array)
                print(reply_target)
        # reply_array.append(my_reply)
        # print(reply_array)

        db.reply.update_one({'number': mentor_num, 'category': 'story', 'time': which_story},
                            {'$set': {'reply': reply_array}})
        if int(reply_target[1]) != int(payload['number']):
            doc = {
                'to_status': reply_target[0],
                'to_number': int(reply_target[1]),
                'category': '댓글에',
                'which_data': '스토리',
                'action': '답글을 작성하였습니다',
                'when': re_reply_time,
                'from_nickname': payload['nickname'],
                'from_image': me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)
        return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/reply_setting_story', methods=['GET'])
def reply_setting_story():
    status_array = request.args.get('statusArray').split(',')
    del status_array[0]
    num_array = request.args.get('numArray').split(',')
    del num_array[0]
    print(status_array)
    print(num_array)

    pic_real_array = []
    for status, number in zip(status_array, num_array):
        if status == 'mentor':
            find_person = db.mentor.find_one({'number': int(number)})
            class_name = 'mentor,' + number
        else:
            find_person = db.menti.find_one({'number': int(number)})
            class_name = 'menti,' + number

        pic_real_array.append([class_name, find_person['profile_pic_real'], find_person['nickname']])

    print(pic_real_array)

    return jsonify({"result": "success", "picArray": pic_real_array})


@app.route('/remove_reply_story', methods=['POST'])
def remove_reply_story():
    mentor_num = int(request.form['mentor_num'])
    which_story = request.form['which_story']
    which_time = request.form['which_time']

    row = db.reply.find_one({'number': mentor_num, 'time': which_story})
    reply_array = row['reply']
    for reply in reply_array:
        if reply[2] == which_time:
            reply_array.remove(reply)

    print(reply_array)
    db.reply.update_one({'number': mentor_num, 'category': 'story', 'time': which_story},
                        {'$set': {'reply': reply_array}})

    return jsonify({"result": "success"})


@app.route('/remove_re_reply_story', methods=['POST'])
def remove_re_reply_story():
    mentor_num = int(request.form['mentor_num'])
    which_story = request.form['which_story']
    which_mother = request.form['which_mother']
    which_time = request.form['which_time']

    row = db.reply.find_one({'number': mentor_num, 'time': which_story})
    reply_array = row['reply']

    for reply in reply_array:
        re_reply_array = reply[3]
        for re_reply in re_reply_array:
            if re_reply[2] == which_time:
                re_reply_array.remove(re_reply)

    db.reply.update_one({'number': mentor_num, 'category': 'story', 'time': which_story},
                        {'$set': {'reply': reply_array}})

    return jsonify({"result": "success"})


@app.route('/reply_resume', methods=['POST'])
def reply_resume():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentor_num = int(request.form['mentor_num'])
        which_resume = str(request.form['which_resume'])
        reply_text = str(request.form['reply_text'])
        reply_time = str(request.form['reply_time'])

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        else:
            me_info = me_mentor
            status = 'mentor'

        my_number = me_info['number']
        print([status, my_number])

        row = db.reply.find_one({'number': mentor_num, 'time': which_resume})
        reply_array = row['reply']

        my_reply = [[status, my_number], reply_text, reply_time, []]
        reply_array.append(my_reply)
        print(reply_array)

        db.reply.update_one({'number': mentor_num, 'category': 'resume', 'time': which_resume},
                            {'$set': {'reply': reply_array}})
        if (status != 'mentor') or (int(payload['number']) != mentor_num):
            print('alert insert')
            doc = {
                'to_status': 'mentor',
                'to_number': mentor_num,
                'category': '자기소개서에',
                'which_data': reply_text,
                'action': '댓글을 작성하였습니다',
                'when': reply_time,
                'from_nickname': payload['nickname'],
                'from_image': me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)
        return jsonify({"result": "success", "reply_array": reply_array})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/reply_to_reply_resume', methods=['POST'])
def reply_to_reply_resume():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentor_num = int(request.form['mentor_num'])
        which_resume = str(request.form['which_resume'])
        which_mother = str(request.form['which_mother'])
        re_reply_text = str(request.form['re_reply_text'])
        re_reply_time = str(request.form['re_reply_time'])

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        else:
            me_info = me_mentor
            status = 'mentor'

        my_number = me_info['number']
        print([status, my_number])

        row = db.reply.find_one({'number': mentor_num, 'time': which_resume})
        reply_array = row['reply']

        my_reply = [[status, my_number], re_reply_text, re_reply_time]
        for miniArray in reply_array:
            if miniArray[2] == which_mother:
                miniArray[3].append(my_reply)
                reply_target = miniArray[0]
                print('reply_array:', reply_array)
                print(reply_target)
        # reply_array.append(my_reply)
        # print(reply_array)

        db.reply.update_one({'number': mentor_num, 'category': 'resume', 'time': which_resume},
                            {'$set': {'reply': reply_array}})
        if int(reply_target[1]) != int(payload['number']):
            doc = {
                'to_status': reply_target[0],
                'to_number': int(reply_target[1]),
                'category': '댓글에',
                'which_data': '자기소개서',
                'action': '답글을 작성하였습니다',
                'when': re_reply_time,
                'from_nickname': payload['nickname'],
                'from_image': me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)
        return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/reply_setting_resume', methods=['GET'])
def reply_setting_resume():
    status_array = request.args.get('statusArray').split(',')
    del status_array[0]
    num_array = request.args.get('numArray').split(',')
    del num_array[0]
    print(status_array)
    print(num_array)

    pic_real_array = []
    for status, number in zip(status_array, num_array):
        if status == 'mentor':
            find_person = db.mentor.find_one({'number': int(number)})
            class_name = 'mentor,' + number
        else:
            find_person = db.menti.find_one({'number': int(number)})
            class_name = 'menti,' + number

        pic_real_array.append([class_name, find_person['profile_pic_real'], find_person['nickname']])

    print(pic_real_array)

    return jsonify({"result": "success", "picArray": pic_real_array})


@app.route('/remove_reply_resume', methods=['POST'])
def remove_reply_resume():
    mentor_num = int(request.form['mentor_num'])
    which_resume = request.form['which_resume']
    which_time = request.form['which_time']

    row = db.reply.find_one({'number': mentor_num, 'time': which_resume})
    reply_array = row['reply']
    for reply in reply_array:
        if reply[2] == which_time:
            reply_array.remove(reply)

    print(reply_array)
    db.reply.update_one({'number': mentor_num, 'category': 'resume', 'time': which_resume},
                        {'$set': {'reply': reply_array}})

    return jsonify({"result": "success"})


@app.route('/remove_re_reply_resume', methods=['POST'])
def remove_re_reply_resume():
    mentor_num = int(request.form['mentor_num'])
    which_resume = request.form['which_resume']
    which_mother = request.form['which_mother']
    which_time = request.form['which_time']

    row = db.reply.find_one({'number': mentor_num, 'time': which_resume})
    reply_array = row['reply']

    for reply in reply_array:
        re_reply_array = reply[3]
        for re_reply in re_reply_array:
            if re_reply[2] == which_time:
                re_reply_array.remove(re_reply)

    db.reply.update_one({'number': mentor_num, 'category': 'resume', 'time': which_resume},
                        {'$set': {'reply': reply_array}})

    return jsonify({"result": "success"})


@app.route('/reply_record', methods=['POST'])
def reply_record():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentor_num = int(request.form['mentor_num'])
        which_record = str(request.form['which_record'])
        reply_text = str(request.form['reply_text'])
        reply_time = str(request.form['reply_time'])

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        else:
            me_info = me_mentor
            status = 'mentor'

        my_number = me_info['number']
        print([status, my_number])

        row = db.reply.find_one({'number': mentor_num, 'category': 'recordpaper'})
        reply_array = row['reply']

        my_reply = [[status, my_number], reply_text, reply_time, []]
        reply_array.append(my_reply)
        print(reply_array)

        db.reply.update_one({'number': mentor_num, 'category': 'recordpaper', 'time': which_record},
                            {'$set': {'reply': reply_array}})
        if (status != 'mentor') or (int(payload['number']) != mentor_num):
            print('alert insert')
            doc = {
                'to_status': 'mentor',
                'to_number': mentor_num,
                'category': '생활기록부에',
                'which_data': reply_text,
                'action': '댓글을 작성하였습니다',
                'when': reply_time,
                'from_nickname': payload['nickname'],
                'from_image': me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)
        return jsonify({"result": "success", "reply_array": reply_array})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/reply_to_reply_record', methods=['POST'])
def reply_to_reply_record():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentor_num = int(request.form['mentor_num'])
        which_record = str(request.form['which_record'])
        which_mother = str(request.form['which_mother'])
        re_reply_text = str(request.form['re_reply_text'])
        re_reply_time = str(request.form['re_reply_time'])

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        else:
            me_info = me_mentor
            status = 'mentor'

        my_number = me_info['number']
        print([status, my_number])

        row = db.reply.find_one({'number': mentor_num, 'category': 'recordpaper'})
        reply_array = row['reply']

        my_reply = [[status, my_number], re_reply_text, re_reply_time]
        for miniArray in reply_array:
            if miniArray[2] == which_mother:
                miniArray[3].append(my_reply)
                reply_target = miniArray[0]
                print('reply_array:', reply_array)
                print(reply_target)
        # reply_array.append(my_reply)
        # print(reply_array)

        db.reply.update_one({'number': mentor_num, 'category': 'recordpaper', 'time': which_record},
                            {'$set': {'reply': reply_array}})
        if int(reply_target[1]) != int(payload['number']):
            doc = {
                'to_status': reply_target[0],
                'to_number': int(reply_target[1]),
                'category': '댓글에',
                'which_data': '생활기록부',
                'action': '답글을 작성하였습니다',
                'when': re_reply_time,
                'from_nickname': payload['nickname'],
                'from_image': me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)
        return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/reply_setting_record', methods=['GET'])
def reply_setting_record():
    status_array = request.args.get('statusArray').split(',')
    del status_array[0]
    num_array = request.args.get('numArray').split(',')
    del num_array[0]
    print(status_array)
    print(num_array)

    pic_real_array = []
    for status, number in zip(status_array, num_array):
        if status == 'mentor':
            find_person = db.mentor.find_one({'number': int(number)})
            class_name = 'mentor,' + number
        else:
            find_person = db.menti.find_one({'number': int(number)})
            class_name = 'menti,' + number

        pic_real_array.append([class_name, find_person['profile_pic_real'], find_person['nickname']])

    print(pic_real_array)

    return jsonify({"result": "success", "picArray": pic_real_array})


@app.route('/remove_reply_record', methods=['POST'])
def remove_reply_record():
    mentor_num = int(request.form['mentor_num'])
    which_record = request.form['which_record']
    which_time = request.form['which_time']

    row = db.reply.find_one({'number': mentor_num, 'category': 'recordpaper'})
    reply_array = row['reply']
    for reply in reply_array:
        if reply[2] == which_time:
            reply_array.remove(reply)

    print(reply_array)
    db.reply.update_one({'number': mentor_num, 'category': 'recordpaper', 'time': which_record},
                        {'$set': {'reply': reply_array}})

    return jsonify({"result": "success"})


@app.route('/remove_re_reply_record', methods=['POST'])
def remove_re_reply_record():
    mentor_num = int(request.form['mentor_num'])
    which_record = request.form['which_record']
    which_mother = request.form['which_mother']
    which_time = request.form['which_time']

    row = db.reply.find_one({'number': mentor_num, 'category': 'recordpaper'})
    reply_array = row['reply']

    for reply in reply_array:
        re_reply_array = reply[3]
        for re_reply in re_reply_array:
            if re_reply[2] == which_time:
                re_reply_array.remove(re_reply)

    db.reply.update_one({'number': mentor_num, 'category': 'recordpaper', 'time': which_record},
                        {'$set': {'reply': reply_array}})

    return jsonify({"result": "success"})


@app.route('/click_action_mentor', methods=['POST'])
def click_action_mentor():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        nickname = request.form['nickname']

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        else:
            me_info = me_mentor
            status = 'mentor'

        find_mentor = db.mentor.find_one({'nickname': nickname})
        mentor_num = int(find_mentor['number'])

        me_in_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        action_mentor_array = me_in_following['action_mentor']
        nonaction_mentor_array = me_in_following['nonaction_mentor']

        action_mentor_array.remove(mentor_num)
        nonaction_mentor_array.insert(0, mentor_num)

        db.following.update_one({'follower_status': status, 'follower_number': int(me_info['number'])}, {
            '$set': {'action_mentor': action_mentor_array, 'nonaction_mentor': nonaction_mentor_array}})

        return jsonify({"result": "success"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        print('error')
        return redirect(url_for(f'/user_mentor/{nickname}'))


@app.route('/remove_all_alert', methods=['POST'])
def remove_all_alert():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        me_menti = db.menti.find_one({'nickname': payload['nickname']})
        me_mentor = db.mentor.find_one({'nickname': payload['nickname']})
        if me_menti is not None:
            # me_info = me_menti
            status = 'menti'
        else:
            # me_info = me_mentor
            status = 'mentor'

        db.alert.delete_many({"to_status": status, 'to_number': int(payload['number'])})

        return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/charge/readypass')
def charge_readypass():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    # me information
    me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
    me_menti = db.menti.find_one({"nickname": payload["nickname"]})
    if me_menti is not None:
        me_info = me_menti
        status = 'menti'
    if me_mentor is not None:
        me_info = me_mentor
        status = 'mentor'

    # follow
    me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
    nonaction_mentor = me_following['nonaction_mentor']
    print(nonaction_mentor)
    nonaction_mentor_array = []
    for number in nonaction_mentor:
        info = db.mentor.find_one({"number": int(number)},
                                  {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info.update({'univ': univ})
        print('infoRenewal:', info)
        nonaction_mentor_array.append(info)
    print(nonaction_mentor_array)
    action_mentor = me_following['action_mentor']
    print(action_mentor)
    action_mentor_array = []
    for number in action_mentor:
        info2 = db.mentor.find_one({"number": int(number)},
                                   {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info2.update({'univ': univ})
        print('infoRenewal:', info2)
        action_mentor_array.append(info2)
    print(action_mentor_array)

    # alert
    my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

    product = 'readypass'

    target_info = {}
    target_info['category'] = 'readypass'



    return render_template('charge.html', product=product, me_info=me_info, action_mentor=action_mentor_array,
                           nonaction_mentor=nonaction_mentor_array, status=status, my_alert=my_alert,target_info=target_info,
                           token_receive=token_receive)


@app.route('/charge/product')
def charge_product():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if request.args.get('mt'):
        mentor_number = int(request.args.get('mt'))
        mentor_info = db.mentor.find_one({'number': mentor_number})
        mentorinfo_info = db.mentor_info.find_one({'number': mentor_number})

        time = request.args.get('time')
        if time == '':
            target = db.recordpaper.find_one({'number': mentor_number}, {'record_title': True, 'record_price': True})
            target['category'] = 'recordpaper'
        else:
            target = db.resume.find_one({'number': mentor_number, 'time': time})
            target['category'] = 'resume'
        target['number'] = mentor_number
        target.update(mentor_info)
        target.update(mentorinfo_info)
        print(mentor_number, time, target)
        target_info = target
    else:
        target_info = ''

    # me information
    me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
    me_menti = db.menti.find_one({"nickname": payload["nickname"]})
    if me_menti is not None:
        me_info = me_menti
        status = 'menti'
    if me_mentor is not None:
        me_info = me_mentor
        status = 'mentor'

    # follow
    me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
    nonaction_mentor = me_following['nonaction_mentor']
    print(nonaction_mentor)
    nonaction_mentor_array = []
    for number in nonaction_mentor:
        info = db.mentor.find_one({"number": int(number)},
                                  {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info.update({'univ': univ})
        print('infoRenewal:', info)
        nonaction_mentor_array.append(info)
    print(nonaction_mentor_array)
    action_mentor = me_following['action_mentor']
    print(action_mentor)
    action_mentor_array = []
    for number in action_mentor:
        info2 = db.mentor.find_one({"number": int(number)},
                                   {'_id': False, 'nickname': True, 'profile_pic_real': True})
        # 대학정보도 추가로 가져와야 함
        univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
        info2.update({'univ': univ})
        print('infoRenewal:', info2)
        action_mentor_array.append(info2)
    print(action_mentor_array)

    # alert
    my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

    product = 'product'

    return render_template('charge.html', product=product, target_info=target_info, me_info=me_info,
                           action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array, status=status,
                           my_alert=my_alert, token_receive=token_receive)


@app.route('/search', methods=['GET'])
def search():
    if request.args.get('selectedUnivArray') is not None:
        selectedUnivArray = request.args.get('selectedUnivArray').split(',')
    else:
        selectedUnivArray = []

    if request.args.get('selectedMajorArray') is not None:
        selectedMajorArray = request.args.get('selectedMajorArray').split(',')
    else:
        selectedMajorArray = []

    if request.args.get('selectedTypeArray') is not None:
        selectedTypeArray = request.args.get('selectedTypeArray').split(',')
    else:
        selectedTypeArray = []

    if request.args.get('tag'):
        tag = '#' + request.args.get('tag')
    else:
        tag = ""

    if request.args.get('ft'):
        ft = request.args.get('ft')
    else:
        ft = -1

    if request.args.get('st'):
        st = request.args.get('st')
    else:
        st = '정확도순'

    print('selectedUnivArray_', selectedUnivArray)
    print('selectedMajorArray_', selectedMajorArray)
    print('selectedTypeArray_', selectedTypeArray)
    print('tag_', tag)
    print('ft_', ft)
    print('st_', st)

    try:
        token_receive = request.cookies.get('mytoken')
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        if payload is None:
            return render_template('search.html', selectedUnivArray=selectedUnivArray,
                                   selectedMajorArray=selectedMajorArray,
                                   selectedTypeArray=selectedTypeArray, tag=tag, ft=ft, st=st)
        # me information
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        # print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            # print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        # print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        # print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            # print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        # print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        # make initial list of searchbox mentor list by follower count, limit 30
        # mentor_all = db.followed.find()
        # # print('mentorALl', mentor_all)
        # initial_mentor_dic = {}
        # for mentor in mentor_all:
        #     if db.mentor.find_one({'number': mentor['number']})['univAttending_file_real'] == '':
        #         follower_cnt = len(mentor['follower'])
        #         initial_mentor_dic[mentor['number']] = follower_cnt
        # sorted_list = sorted(initial_mentor_dic.items(), key=lambda x: x[1], reverse=True)[:30]
        # initial_search_list = []
        # initial_mentorNum_list =[]
        #
        # for item in sorted_list:
        #     mentor_num = int(item[0])
        #     initial_mentorNum_list.append(mentor_num)
        #
        #     db_mentor = db.mentor.find_one({'number': mentor_num},
        #                                    {'_id': False, 'nickname': True, 'profile_pic_real': True})
        #     db_mentorinfo = db.mentor_info.find_one({'number': mentor_num},
        #                                             {'_id': False, 'tags': True, 'mentor_univ': True, 'mentor_major': True,
        #                                              'mentor_type': True, 'mentor_number': True})
        #     if db.recordpaper.find_one({'number': mentor_num})['chart_js_array']:
        #         record_count = 1
        #     else:
        #         record_count = 0
        #     resume_count = db.resume.find({'number': mentor_num}).count()
        #     story_count = db.story.find({'number': mentor_num}).count()
        #     cnt_mentor_data = record_count + resume_count + story_count
        #
        #     arr = [
        #         db_mentor['profile_pic_real'],

        #         item[1],
        #         cnt_mentor_data,
        #         db_mentorinfo['tags'],
        #         db_mentor['nickname'],
        #         db_mentorinfo['mentor_univ'][0],
        #         db_mentorinfo['mentor_major'][0],
        #         db_mentorinfo['mentor_type'][0],
        #         db_mentorinfo['mentor_number'][0],
        #         mentor_num,
        #         record_count,
        #         resume_count,
        #         story_count
        #     ]
        #     initial_search_list.append(arr)
        # pprint.pprint(initial_search_list)

        return render_template('search.html', selectedUnivArray=selectedUnivArray, selectedMajorArray=selectedMajorArray,
                               selectedTypeArray=selectedTypeArray, tag=tag, ft=ft, st=st, me_info=me_info,
                               action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, status=status, my_alert=my_alert,
                               token_receive=token_receive)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        print('no token')
        return render_template('search.html', selectedUnivArray=selectedUnivArray, selectedMajorArray=selectedMajorArray,
                               selectedTypeArray=selectedTypeArray, tag=tag, ft=ft, st=st)


@app.route('/get_product', methods=['GET'])
def get_product():
    arr = request.args.get('array_give')
    Arr = arr.split(',')
    print(Arr)
    product_list = []
    for number_str in Arr:
        number = int(number_str)
        img = db.mentor.find_one({'number': number})['profile_pic_real']
        db_mentor_info = db.mentor_info.find_one({'number': number})
        if db_mentor_info['mentor_univ'] == []:
            univ = ""
        else:
            univ = db_mentor_info['mentor_univ'][0]
        if db_mentor_info['mentor_major'] == []:
            major = ""
        else:
            major = db_mentor_info['mentor_major'][0]
        if db_mentor_info['mentor_type'] == []:
            type = ""
        else:
            type = db_mentor_info['mentor_type'][0]
        if db_mentor_info['mentor_number'] == []:
            student_num = ""
        else:
            student_num = db_mentor_info['mentor_number'][0]
        # major = db_mentor_info['mentor_major'][0]
        # type = db_mentor_info['mentor_type'][0]
        # student_num = db_mentor_info['mentor_number'][0]

        if db.recordpaper.find_one({'number': number, 'release': 'sell'}) is not None:
            db_record = db.recordpaper.find_one({'number': number, 'release': 'sell'})

            if db.like.find_one({'number': number, 'category': 'recordpaper'}) is not None:
                like = len(db.like.find_one({'number': number, 'category': 'recordpaper'})['who'])
            else:
                like = 0

            if db.reply.find_one({'number': number, 'category': 'recordpaper'}) is not None:
                reply = str(db.reply.find_one({'number': number, 'category': 'recordpaper'})['reply']).count('일')
            else:
                reply = 0

            rec_doc = {
                'img': img,
                'category': '학교생활기록부',
                'mentor_num': number,
                'univ': univ,
                'major': major,
                'student_num': student_num,
                'type': type,
                'title': db_record['record_title'],
                'time': "",
                'like': like,
                'reply': reply,
                'price': int(db_record['record_price']),
                'visit': db_record['visit']
            }
            product_list.append(rec_doc)

        if db.resume.find({'number': number, 'release': 'sell'}) is not None:
            db_resume = list(db.resume.find({'number': number, 'release': 'sell'}))
            for resume in db_resume:
                time = resume['time']
                if db.like.find_one({'number': number, 'category': 'resume', 'time': time}) is not None:
                    like = len(db.like.find_one({'number': number, 'category': 'resume', 'time': time})['who'])
                else:
                    like = 0

                if db.reply.find_one({'number': number, 'category': 'resume', 'time': time}) is not None:
                    reply = str(
                        db.reply.find_one({'number': number, 'category': 'resume', 'time': time})['reply']).count('일')
                else:
                    reply = 0
                res_doc = {
                    'img': img,
                    'category': '자기소개서',
                    'mentor_num': number,
                    'univ': resume['resume_univ'],
                    'major': resume['resume_major'],
                    'student_num': resume['resume_class'],
                    'type': resume['resume_type'],
                    'title': resume['resume_title'],
                    'time': time,
                    'like': like,
                    'reply': reply,
                    'price': int(resume['resume_price']),
                    'visit': resume['visit']
                }
                product_list.append(res_doc)

        if db.story.find({'number': number, 'release': 'sell'}) is not None:
            db_story = list(db.story.find({'number': number, 'release': 'sell'}))
            for story in db_story:
                time = story['time']
                if db.like.find_one({'number': number, 'category': 'story', 'time': time}) is not None:
                    like = len(db.like.find_one({'number': number, 'category': 'story', 'time': time})['who'])
                else:
                    like = 0

                if db.reply.find_one({'number': number, 'category': 'story', 'time': time}) is not None:
                    reply = str(
                        db.reply.find_one({'number': number, 'category': 'story', 'time': time})['reply']).count('일')
                else:
                    reply = 0
                sto_doc = {
                    'img': img,
                    'category': '스토리',
                    'mentor_num': number,
                    'univ': univ,
                    'major': major,
                    'student_num': student_num,
                    'type': type,
                    'title': story['story_title'],
                    'time': time,
                    'like': like,
                    'reply': reply,
                    'price': 0,
                    'visit': story['visit']
                }
                product_list.append(sto_doc)

    pprint.pprint(product_list)

    return jsonify({"result": "success", "products": product_list})


@app.route('/mentor_tag_is', methods=['GET'])
def mentor_tag_is():
    mentorNum_array = request.args.get('array_give').split(',')
    print(mentorNum_array)
    mentorTag_array = []
    for number in mentorNum_array:
        tags = db.mentor_info.find_one({'number': int(number)})['tags']
        mentorTag_array.append(tags)
    return jsonify({"result": "success", 'tags': mentorTag_array})


@app.route('/mentor_products/<int:mentor_number>')
def mentor_product(mentor_number):
    ft_receive = request.args.get('ft')
    print(ft_receive)

    # this mentor information
    mentor_info = db.mentor.find_one({'number': mentor_number})
    mentorinfo_info = db.mentor_info.find_one({'number': mentor_number})
    following = db.followed.find_one({"number": mentor_number})
    mentor_follower = following['follower']

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # me information
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        myFeed = (mentor_number == payload["number"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        if [status, int(me_info['number'])] in mentor_follower:
            followed = 'True'
        else:
            followed = 'False'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        return render_template('mentor_products.html', ft=ft_receive, mentor_info=mentor_info,
                               mentorinfo_info=mentorinfo_info, myFeed=myFeed, me_info=me_info,
                               action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array,
                               status=status,
                               follower=mentor_follower, followed=followed, my_alert=my_alert, token_receive=token_receive)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        print('no token')
        return render_template('mentor_products.html', ft=ft_receive, mentor_info=mentor_info,
                               mentorinfo_info=mentorinfo_info, me_info=None,
                               follower=mentor_follower)


@app.route('/recordpaper_sell/<int:mentor_number>')
def recordpaper_sell(mentor_number):
    token_receive = request.cookies.get('mytoken')
    # this mentor information
    mentor_info = db.mentor.find_one({'number': mentor_number})
    mentorinfo_info = db.mentor_info.find_one({'number': mentor_number})
    following = db.followed.find_one({"number": mentor_number})
    mentor_follower = following['follower']

    # record_info
    record = db.recordpaper.find_one({'number': mentor_number})
    this_like = len(db.like.find_one({'number': mentor_number, 'category': 'recordpaper'})['who'])
    this_reply = str(db.reply.find_one({'number': mentor_number, 'category': 'recordpaper'})['reply']).count('일')

    # other data(resume)
    resume_all = list(db.resume.find({'number': mentor_number, 'release': 'sell'}, {'_id': False}))
    # (resume) like-reply count
    resume_array = []
    for resume in resume_all:
        if db.like.find_one({'number': mentor_number, 'category': 'resume', 'time': resume['time']}):
            resume_like = len(
                db.like.find_one({'number': mentor_number, 'category': 'resume', 'time': resume['time']})['who'])
        else:
            resume_like = 0
        if db.reply.find_one({'number': mentor_number, 'category': 'resume', 'time': resume['time']}):
            resume_reply = str(
                db.reply.find_one({'number': mentor_number, 'category': 'resume', 'time': resume['time']})[
                    'reply']).count('일')
        else:
            resume_reply = 0
        resume_array.append([resume, resume_like, resume_reply])

    # other data(story)
    story_all = list(db.story.find({'number': mentor_number}, {'_id': False}))
    # (story) like-reply count
    story_array = []
    for story in story_all:
        if db.like.find_one({'number': mentor_number, 'category': 'story', 'time': story['time']}):
            story_like = len(
                db.like.find_one({'number': mentor_number, 'category': 'story', 'time': story['time']})['who'])
        else:
            story_like = 0
        if db.reply.find_one({'number': mentor_number, 'category': 'story', 'time': story['time']}):
            story_reply = str(db.reply.find_one({'number': mentor_number, 'category': 'story', 'time': story['time']})[
                                  'reply']).count('일')
        else:
            story_reply = 0
        story_array.append([story, story_like, story_reply])
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        if record['release'] == 'sell' or (record['release'] == 'hide' and mentor_number == payload['number']):
            # me information
            me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
            me_menti = db.menti.find_one({"nickname": payload["nickname"]})
            if me_menti is not None:
                me_info = me_menti
                status = 'menti'
            if me_mentor is not None:
                me_info = me_mentor
                status = 'mentor'

            myFeed = (mentor_number == payload["number"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

            if [status, int(me_info['number'])] in mentor_follower:
                followed = 'True'
            else:
                followed = 'False'

            # follow
            me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
            nonaction_mentor = me_following['nonaction_mentor']
            print(nonaction_mentor)
            nonaction_mentor_array = []
            for number in nonaction_mentor:
                info = db.mentor.find_one({"number": int(number)},
                                          {'_id': False, 'nickname': True, 'profile_pic_real': True})
                # 대학정보도 추가로 가져와야 함
                univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
                info.update({'univ': univ})
                print('infoRenewal:', info)
                nonaction_mentor_array.append(info)
            print(nonaction_mentor_array)
            action_mentor = me_following['action_mentor']
            print(action_mentor)
            action_mentor_array = []
            for number in action_mentor:
                info2 = db.mentor.find_one({"number": int(number)},
                                           {'_id': False, 'nickname': True, 'profile_pic_real': True})
                # 대학정보도 추가로 가져와야 함
                univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
                info2.update({'univ': univ})
                print('infoRenewal:', info2)
                action_mentor_array.append(info2)
            print(action_mentor_array)

            # alert
            my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

            # 내가 이것을 샀는가 ####### 결제 디비 얹고 수정!
            now = datetime.now()
            if db.pay.find_one({'category': 'recordpaper', 'client_number': me_info['number'], 'number': mentor_number}) is not None:
                exp = db.pay.find_one({'category': 'recordpaper', 'client_number': int(me_info['number']), 'number': mentor_number})['exp_time']
                exp_in_form = datetime.strptime(exp, "%Y-%m-%d %H:%M:%S")
                if exp_in_form > now:
                    buythis = 'yes'
                else:
                    buythis = ""
            else:
                buythis = ""
            # 패스 유저인가
            if status == 'menti' and db.menti.find_one({'number':int(me_info['number'])})['pass'] != '':
                has_pass = 'yes'
            else:
                has_pass = 'no'

            # wishlist
            miniTab_find = db.menti_data.find_one(
                {'number': payload['number'], 'miniTab': 'wishlist', 'category': 'recordpaper',
                 'mentor_num': mentor_number})
            if miniTab_find is not None:
                miniTab_find = 'wishlist'
            else:
                miniTab_find = ''
            return render_template('recordpaper_sell.html', miniTab_find=miniTab_find, mentor_info=mentor_info,
                                   record=record, this_like=this_like, this_reply=this_reply, resume_array=resume_array,
                                   story_array=story_array, mentorinfo_info=mentorinfo_info, myFeed=myFeed, me_info=me_info,
                                   buythis=buythis,has_pass=has_pass, action_mentor=action_mentor_array,
                                   nonaction_mentor=nonaction_mentor_array, status=status, follower=mentor_follower,
                                   followed=followed, my_alert=my_alert, token_receive=token_receive)
        else:
            return redirect(url_for('home'))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        if record['release'] == 'sell':
            return render_template('recordpaper_sell.html', mentor_info=mentor_info, record=record, this_like=this_like,
                                   this_reply=this_reply, resume_array=resume_array, story_array=story_array,
                                   mentorinfo_info=mentorinfo_info, myFeed=False, me_info=None, buythis=None, status=None,
                                   token_receive=token_receive)
        else:
            return redirect(url_for('home'))


@app.route('/resume_sell/<int:mentor_number>/<time>')
def resume_sell(mentor_number, time):
    token_receive = request.cookies.get('mytoken')
    # this mentor information
    mentor_info = db.mentor.find_one({'number': mentor_number})
    mentorinfo_info = db.mentor_info.find_one({'number': mentor_number})
    following = db.followed.find_one({"number": mentor_number})
    mentor_follower = following['follower']

    # resume_info

    if db.resume.find_one({'number': mentor_number, 'time': time}):
        resume = db.resume.find_one({'number': mentor_number, 'time': time})
        this_like = len(db.like.find_one({'number': mentor_number, 'category': 'resume', 'time': time})['who'])
        this_reply = str(
            db.reply.find_one({'number': mentor_number, 'category': 'resume', 'time': time})['reply']).count('일')

        # other data(resume)
        resume_all = list(db.resume.find({'number': mentor_number, 'release': 'sell'}, {'_id': False}))
        # (resume) like-reply count
        resume_array = []
        for resume1 in resume_all:
            if resume1['time'] != time:
                if db.like.find_one({'number': mentor_number, 'category': 'resume', 'time': resume1['time']}):
                    resume_like = len(
                        db.like.find_one({'number': mentor_number, 'category': 'resume', 'time': resume1['time']})[
                            'who'])
                else:
                    resume_like = 0
                if db.reply.find_one({'number': mentor_number, 'category': 'resume', 'time': resume1['time']}):
                    resume_reply = str(
                        db.reply.find_one({'number': mentor_number, 'category': 'resume', 'time': resume1['time']})[
                            'reply']).count('일')
                else:
                    resume_reply = 0
                resume_array.append([resume1, resume_like, resume_reply])
        # other data(story)
        story_all = list(db.story.find({'number': mentor_number}, {'_id': False}))
        # (story) like-reply count
        story_array = []
        for story in story_all:
            if db.like.find_one({'number': mentor_number, 'category': 'story', 'time': story['time']}):
                story_like = len(
                    db.like.find_one({'number': mentor_number, 'category': 'story', 'time': story['time']})['who'])
            else:
                story_like = 0
            if db.reply.find_one({'number': mentor_number, 'category': 'story', 'time': story['time']}):
                story_reply = str(
                    db.reply.find_one({'number': mentor_number, 'category': 'story', 'time': story['time']})[
                        'reply']).count('일')
            else:
                story_reply = 0
            story_array.append([story, story_like, story_reply])

        # other data(recordpaper)
        recordpaper = db.recordpaper.find_one({'number': mentor_number, 'release': 'sell'}, {'_id': False})
        # (recordpaper) like-reply count
        record_array = []
        if recordpaper is not None:
            if db.like.find_one({'number': mentor_number, 'category': 'recordpaper'}):
                record_like = len(
                    db.like.find_one({'number': mentor_number, 'category': 'recordpaper'})['who'])
            else:
                record_like = 0
            if db.reply.find_one({'number': mentor_number, 'category': 'recordpaper'}):
                record_reply = str(
                    db.reply.find_one({'number': mentor_number, 'category': 'recordpaper'})[
                        'reply']).count('일')
            else:
                record_reply = 0
            record_array = [recordpaper, record_like, record_reply]
            print(record_array)

    else:
        resume = None
        this_like = 0
        this_reply = 0
        record_array = []
        resume_array = []
        story_array = []

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        if (payload['number'] != mentor_number) and ((resume is None) or (resume['release'] == 'hide')):
            return redirect(url_for('home'))

        # me information
        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        myFeed = (mentor_number == payload["number"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        if [status, int(me_info['number'])] in mentor_follower:
            followed = 'True'
        else:
            followed = 'False'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        # 내가 이것을 샀는가 ####### 결제 디비 얹고 수정!
        now = datetime.now()
        if db.pay.find_one({'category': 'resume', 'client_number': me_info['number'], 'number': mentor_number, 'time':time}) is not None:
            exp = db.pay.find_one({'category': 'resume', 'client_number': int(me_info['number']), 'number': mentor_number,'time':time})['exp_time']
            exp_in_form = datetime.strptime(exp, "%Y-%m-%d %H:%M:%S")
            if exp_in_form > now:
                buythis = 'yes'
            else:
                buythis = ""
        else:
            buythis = ""

        # 패스 유저인가
        if status == 'menti' and db.menti.find_one({'number': int(me_info['number'])})['pass'] != '':
            has_pass = 'yes'
        else:
            has_pass = 'no'

        # wishlist
        miniTab_find = db.menti_data.find_one(
            {'number': payload['number'], 'miniTab': 'wishlist', 'category': 'resume', 'mentor_num': mentor_number,
             'product_time': time})
        if miniTab_find is not None:
            miniTab_find = 'wishlist'
        else:
            miniTab_find = ''
        return render_template('resume_sell.html', miniTab_find=miniTab_find, mentor_info=mentor_info, resume=resume,
                               time=time, this_like=this_like, this_reply=this_reply, record_array=record_array,
                               resume_array=resume_array, story_array=story_array, mentorinfo_info=mentorinfo_info,
                               myFeed=myFeed, me_info=me_info, buythis=buythis, has_pass=has_pass, action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, status=status, follower=mentor_follower,
                               followed=followed, my_alert=my_alert, token_receive=token_receive)

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('resume_sell.html', mentor_info=mentor_info, resume=resume, time=time,
                               this_like=this_like, this_reply=this_reply, record_array=record_array,
                               resume_array=resume_array, story_array=story_array, mentorinfo_info=mentorinfo_info,
                               myFeed=False, me_info=None, buythis=None, status=None, token_receive=token_receive)


@app.route('/add_wishlist', methods=['POST'])
def add_wishlist():
    now = datetime.now()
    now_in_form = now.strftime("%Y/%m/%d, %H:%M:%S")
    menti_receive = request.form['menti_give']
    category_receive = request.form['category_give']
    number_receive = request.form['number_give']
    time_receive = request.form['time_give']

    doc = {
        "number": int(menti_receive),
        "miniTab": 'wishlist',
        "category": category_receive,
        "mentor_num": int(number_receive),
        "time": time_receive,
        "update_time": now_in_form
    }
    db.menti_data.insert_one(doc)
    return jsonify({"result": "success"})


@app.route('/remove_wishlist', methods=['POST'])
def remove_wishlist():
    menti_receive = request.form['menti_give']
    category_receive = request.form['category_give']
    number_receive = request.form['number_give']
    time_receive = request.form['time_give']

    db.menti_data.delete_one({"number": int(menti_receive), 'miniTab': 'wishlist', 'category': category_receive,
                              'mentor_num': int(number_receive), 'time': time_receive})
    return jsonify({"result": "success"})


@app.route('/add_wishlist_record', methods=['POST'])
def add_wishlist_record():
    now = datetime.now()
    now_in_form = now.strftime("%Y/%m/%d, %H:%M:%S")
    menti_receive = request.form['menti_give']
    category_receive = request.form['category_give']
    number_receive = request.form['number_give']

    doc = {
        "number": int(menti_receive),
        "miniTab": 'wishlist',
        "category": category_receive,
        "mentor_num": int(number_receive),
        "update_time": now_in_form
    }
    db.menti_data.insert_one(doc)
    return jsonify({"result": "success"})


@app.route('/remove_wishlist_record', methods=['POST'])
def remove_wishlist_record():
    menti_receive = request.form['menti_give']
    category_receive = request.form['category_give']
    number_receive = request.form['number_give']

    db.menti_data.delete_one({"number": int(menti_receive), 'miniTab': 'wishlist', 'category': category_receive,
                              'mentor_num': int(number_receive)})
    return jsonify({"result": "success"})


@app.route('/sale_check', methods=['POST'])
def sale_check():
    val = request.form['coupon_give']
    time = request.form['time']
    print(val)
    if db.coupon.find_one({'coupon': val}) is not None:
        if db.coupon.find_one({'coupon': val})['use'] == '':
            doc = {
                'use': time
            }
            sale = db.coupon.find_one({'coupon': val})['sale'].split('%')[0]
            # db.coupon.update_one({'coupon':val},{'$set':doc})
            return jsonify({"result": "success", "sale": sale})
        else:
            return jsonify({"result": "fail"})
    else:
        return jsonify({"result": "fail"})


@app.route('/check_alert', methods=['POST'])
def check_alert():
    status = request.form['status']
    me_number = int(request.form['me_number'])
    category = request.form['category']
    which_data = request.form['which_data']
    from_nickname = request.form['from_nickname']
    print(status, me_number, category, which_data, from_nickname)
    if category == '댓글에':
        from_number = int(db.mentor.find_one({'nickname': from_nickname})['number'])
        if which_data == '커뮤니티':
            url = f'/user_mentor/{from_nickname}'
        elif which_data == '생활기록부':
            url = f'/record_paper/{from_number}'
        elif which_data == '자기소개서':
            url = f'/resume/{from_number}'
        elif which_data == '스토리':
            url = f'/story/{from_number}'
    elif category == '생활기록부가':
        url = f'/recordpaper/{me_number}'
    else:
        me_nickname = db.mentor.find_one({'number': me_number})['nickname']
        url = f'/user_mentor/{me_nickname}'

    db.alert.delete_many({'to_status': status, 'to_number': me_number, 'category': category, 'which_data': which_data})
    return jsonify({"result": "success", "url": url})


@app.route('/save_res_comment/<int:mentor_number>/<time>', methods=['POST'])
def save_res_comment(mentor_number, time):
    resume_info_1 = request.form['resume_info_1']
    resume_info_2 = request.form['resume_info_2']
    resume_info_3 = request.form['resume_info_3']
    resume_info_4 = request.form['resume_info_4']
    resume_comment_array_number = request.form['resume_comment_array_number'].split(',')
    resume_comment_array_text = request.form['resume_comment_array_text'].split('렓^딟')
    print(resume_comment_array_number)
    print(resume_comment_array_text)
    resume_comment_dict = {}
    for number, text in zip(resume_comment_array_number, resume_comment_array_text):
        print(number, text)
        resume_comment_dict[f'{number}'] = str(text)
    pprint.pprint(resume_comment_dict)
    doc = {
        'resume_info_1': resume_info_1,
        'resume_info_2': resume_info_2,
        'resume_info_3': resume_info_3,
        'resume_info_4': resume_info_4,
        'resume_comment_dict': resume_comment_dict,
    }
    pprint.pprint(doc)
    db.resume.update_one({'number': mentor_number, 'time': time}, {'$set': doc})
    return jsonify({"result": "success"})


@app.route('/save_rec_comment/<int:mentor_number>', methods=['POST'])
def save_rec_comment(mentor_number):
    record_info = request.form['record_info']
    record_comment_array_number = request.form['record_comment_array_number'].split(',')
    record_comment_array_text = request.form['record_comment_array_text'].split('렓^딟')
    graph_comment_1 = request.form['graph_comment_1']
    graph_comment_2 = request.form['graph_comment_2']
    graph_comment_3 = request.form['graph_comment_3']
    graph_comment_4 = request.form['graph_comment_4']
    print(record_comment_array_number)
    print(record_comment_array_text)
    print (graph_comment_1)
    record_comment_dict = {}
    for number, text in zip(record_comment_array_number, record_comment_array_text):
        print(number, text)
        record_comment_dict[f'{number}'] = str(text)
    pprint.pprint(record_comment_dict)
    doc = {
        'record_info':record_info,
        'record_comment_dict': record_comment_dict,
        'graph_comment_1':graph_comment_1,
        'graph_comment_2':graph_comment_2,
        'graph_comment_3':graph_comment_3,
        'graph_comment_4':graph_comment_4
    }
    pprint.pprint(doc)
    db.recordpaper.update_one({'number': mentor_number}, {'$set': doc})
    return jsonify({"result": "success"})


@app.route('/coupon_insert', methods=['POST'])
def insert():
    coupon = ''
    coupon_list = coupon.split('/ ')
    for cou in coupon_list:
        doc = {
            'coupon': cou,
            'sale': '30000',
            'date': '2021.8.23',
            'use': '',
            'number': ''
        }
        db.coupon.insert_one(doc)
    return jsonify({"result": "success"})


@app.route('/finish_charge/readypass')
def finish_charge_readypass():
    # me information
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        me_info = db.menti.find_one({"nickname": payload["nickname"]})
        status = 'menti'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        target_info={}
        target_info['category'] = 'readypass'

        product = 'readypass'

        price = request.args.get('prc')
        method = request.args.get('mth')
        receipt_url = request.args.get('rrl')
        return render_template('finish_charge.html', me_info=me_info, action_mentor=action_mentor_array,product=product,target_info=target_info,
                               nonaction_mentor=nonaction_mentor_array, status=status, my_alert=my_alert, token_receive=token_receive, price=price, method=method, receipt_url=receipt_url)

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('login'))


@app.route('/finish_charge/product')
def finish_charge_product():
    # me information
    token_receive = request.cookies.get('mytoken')
    if request.args.get('mt'):
        mentor_number = int(request.args.get('mt'))
        mentor_info = db.mentor.find_one({'number': mentor_number})
        mentorinfo_info = db.mentor_info.find_one({'number': mentor_number})

        time = request.args.get('time')
        if time == '':
            target = db.recordpaper.find_one({'number': mentor_number}, {'record_title': True, 'record_price': True})
            target['category'] = 'recordpaper'
        else:
            target = db.resume.find_one({'number': mentor_number, 'time': time})
            target['category'] = 'resume'
        target['number'] = mentor_number
        target.update(mentor_info)
        target.update(mentorinfo_info)
        print(mentor_number, time, target)
        target_info = target
    else:
        target_info = ''

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        me_info = db.menti.find_one({"nickname": payload["nickname"]})
        status = 'menti'

        # follow
        me_following = db.following.find_one({"follower_status": status, "follower_number": int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array = []
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},
                                      {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info.update({'univ': univ})
            print('infoRenewal:', info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)},
                                       {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number': int(number)})['mentor_univ'][0]
            info2.update({'univ': univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        # alert
        my_alert = list(db.alert.find({'to_status': status, 'to_number': payload["number"]}))

        product = 'product'
        price = request.args.get('prc')
        method = request.args.get('mth')
        receipt_url = request.args.get('rrl')
        return render_template('finish_charge.html', me_info=me_info, action_mentor=action_mentor_array,product=product,target_info=target_info,
                               nonaction_mentor=nonaction_mentor_array, status=status, my_alert=my_alert, token_receive=token_receive, price=price, method=method, receipt_url=receipt_url)

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('/login'))


class BootpayApi:
    base_url = {
        'development': 'https://dev-api.bootpay.co.kr',
        'production': 'https://api.bootpay.co.kr'
    }

    def __init__(self, application_id, private_key, mode='production'):
        self.application_id = application_id
        self.pk = private_key
        self.mode = mode
        self.token = None

    def api_url(self, uri=None):
        print('api_url')
        print(uri)
        if uri is None:
            uri = []
            print(uri)
        print('/'.join([self.base_url[self.mode]] + uri))
        return '/'.join([self.base_url[self.mode]] + uri)

    def get_access_token(self):
        data = {
            'application_id': self.application_id,
            'private_key': self.pk
        }
        response = requests.post(self.api_url(['request', 'token']), data=data)
        result = response.json()
        print(result)
        if result['status'] == 200:
            self.token = result['data']['token']
        return result

    def cancel(self, receipt_id, price=None, name=None, reason=None):
        payload = {'receipt_id': receipt_id,
                   'price': price,
                   'name': name,
                   'reason': reason}
        print('payload :', payload)

        return requests.post(self.api_url(['cancel.json']), data=payload, headers={
            'Authorization': self.token
        }).json()

    def verify(self, receipt_id):
        print('reID: ', receipt_id)
        print(self.token)

        return requests.get(self.api_url(['receipt', receipt_id]), headers={
            'Authorization': self.token
        }).json()

    def subscribe_billing(self, billing_key, item_name, price, order_id, tax_free=0, items=None, user_info=None,
                          extra=None):
        if items is None:
            items = {}
        payload = {
            'billing_key': billing_key,
            'item_name': item_name,
            'price': price,
            'tax_free': tax_free,
            'order_id': order_id,
            'items': items,
            'user_info': user_info,
            'extra': extra
        }
        return requests.post(self.api_url(['subscribe', 'billing.json']), data=json.dumps(payload), headers={
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }).json()

    def subscribe_billing_reserve(self, billing_key, item_name, price, order_id, execute_at, feedback_url, tax_free=0,
                                  items=None):
        if items is None:
            items = []
        payload = {
            'billing_key': billing_key,
            'item_name': item_name,
            'price': price,
            'tax_free': tax_free,
            'order_id': order_id,
            'items': items,
            'scheduler_type': 'oneshot',
            'execute_at': execute_at,
            'feedback_url': feedback_url
        }
        return requests.post(self.api_url(['subscribe', 'billing', 'reserve.json']), data=json.dumps(payload), headers={
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }).json()

    def subscribe_billing_reserve_cancel(self, reserve_id):
        return requests.delete(self.api_url(['subscribe', 'billing', 'reserve', reserve_id]), headers={
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }).json()

    def get_subscribe_billing_key(self, pg, order_id, item_name, card_no, card_pw, expire_year, expire_month,
                                  identify_number, user_info=None, extra=None):
        if user_info is None:
            user_info = {}
        payload = {
            'order_id': order_id,
            'pg': pg,
            'item_name': item_name,
            'card_no': card_no,
            'card_pw': card_pw,
            'expire_year': expire_year,
            'expire_month': expire_month,
            'identify_number': identify_number,
            'user_info': user_info,
            'extra': extra
        }
        return requests.post(self.api_url(['request', 'card_rebill.json']), data=json.dumps(payload), headers={
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }).json()

    def destroy_subscribe_billing_key(self, billing_key):
        return requests.delete(self.api_url(['subscribe', 'billing', billing_key]), headers={
            'Authorization': self.token
        }).json()

    def request_payment(self, payload={}):
        return requests.post(self.api_url(['request', 'payment.json']), data=payload, headers={
            'Authorization': self.token
        }).json()

    def remote_link(self, payload={}, sms_payload=None):
        if sms_payload is None:
            sms_payload = {}
        payload['sms_payload'] = sms_payload
        return requests.post(self.api_url(['app', 'rest', 'remote_link.json']), data=payload).json()

    def remote_form(self, remoter_form, sms_payload=None):
        if sms_payload is None:
            sms_payload = {}
        payload = {
            'application_id': self.application_id,
            'remote_form': remoter_form,
            'sms_payload': sms_payload
        }
        return requests.post(self.api_url(['app', 'rest', 'remote_form.json']), data=payload, headers={
            'Authorization': self.token
        }).json()

    def send_sms(self, receive_numbers, message, send_number=None, extra={}):
        payload = {
            'data': {
                'sp': send_number,
                'rps': receive_numbers,
                'msg': message,
                'm_id': extra['m_id'],
                'o_id': extra['o_id']
            }
        }
        return requests.post(self.api_url(['push', 'sms.json']), data=payload, headers={
            'Authorization': self.token
        }).json()

    def send_lms(self, receive_numbers, message, subject, send_number=None, extra={}):
        payload = {
            'data': {
                'sp': send_number,
                'rps': receive_numbers,
                'msg': message,
                'sj': subject,
                'm_id': extra['m_id'],
                'o_id': extra['o_id']
            }
        }
        return requests.post(self.api_url(['push', 'lms.json']), data=payload, headers={
            'Authorization': self.token
        }).json()

    def certificate(self, receipt_id):
        return requests.get(self.api_url(['certificate', receipt_id]), headers={
            'Authorization': self.token
        }).json()

    def submit(self, receipt_id):
        payload = {
            'receipt_id': receipt_id
        }
        return requests.post(self.api_url(['submit.json']), data=payload, headers={
            'Authorization': self.token
        }).json()

    def get_user_token(self, data={}):
        return requests.post(self.api_url(['request', 'user', 'token.json']), data=data, headers={
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }).json()


@app.route('/pay_check', methods=['POST'])
def pay_check():
    bootpay = BootpayApi(
        "6119f0887b5ba4002352a0d7",
        "az77RPwwgdz+JdQUQzF4w77rpcpRqJ0zfR6oSVVXGV0="
    )
    result = bootpay.get_access_token()
    if result['status'] == 200:
        print('result:', result)
        token = result['data']['token']
        print('token: ',token)
        rec_id = request.args.get('id')
        print('rec_id: ',rec_id)
        print('reIDID', rec_id)
        verify_result = bootpay.verify(f'{rec_id}')
        print('verify_result: ', verify_result)
        if verify_result['status'] == 200:
            # 원래 주문했던 금액이 일치하는가?
            # 그리고 결제 상태가 완료 상태인가?
            category_receive = request.form['category']
            print('category:',category_receive)
            number = int(request.form['number'])
            time = request.form['time']
            if category_receive == 'readypass':
                price = request.form['price']
            elif category_receive == 'recordpaper':
                price = db.recordpaper.find_one({'number': number})['record_price']
            else:
                price = db.resume.find_one({'number': number, 'time': time})['resume_price']

            print('price: ',price)
            print('verify_result: ',verify_result)
            if verify_result['data']['status'] == 1:# and verify_result['data']['price'] == price:
                print('verify_result: ',verify_result)
                category_receive = request.form['category']
                client_number = int(request.form['client_num'])
                pay_time = request.form['pay_time']
                pay_time_in_form = datetime.strptime(pay_time, "%Y-%m-%d %H:%M:%S")
                date_diff_90d = pay_time_in_form + timedelta(days=90)
                date_diff_1y = pay_time_in_form + timedelta(days=365)
                exp_time_90d = date_diff_90d.strftime("%Y-%m-%d %H:%M:%S")
                exp_time_1y = date_diff_1y.strftime("%Y-%m-%d %H:%M:%S")
                if category_receive == 'readypass':
                    exp_time = exp_time_1y
                else:
                    exp_time = exp_time_90d
                price = request.form['price']
                original_price = request.form['original_price']
                card_name = request.form['card_name']
                card_no = request.form['card_no']
                card_quota = request.form['card_quota']
                method_name = request.form['method_name']
                receipt_id = request.form['receipt_id']
                receipt_url = request.form['receipt_url']

                doc = {
                    'category': category_receive,
                    'client_number': client_number,
                    'number': number,
                    'time': time,
                    'pay_time': pay_time,
                    'exp_time': exp_time,
                    'price': price,
                    'original_price': original_price,
                    'card_name': card_name,
                    'card_no': card_no,
                    'card_quota': card_quota,
                    'method_name': method_name,
                    'receipt_id': receipt_id,
                    'receipt_url': receipt_url
                }
                pprint.pprint(doc)
                db.pay.insert_one(doc)

                if category_receive != 'readypass':
                    doc2 = {
                        'number': client_number,
                        'miniTab': 'buy',
                        'category': category_receive,
                        'mentor_num': number,
                        'time': time
                    }
                    db.menti_data.insert_one(doc2)

                    if category_receive == 'recordpaper':
                        before_buy = db.recordpaper.find_one({'number':number})['buy']
                        if before_buy == '':
                            before_buy = 0
                        before_profit = db.recordpaper.find_one({'number':number})['profit']
                        if before_profit == '':
                            before_profit = 0
                        after_buy = int(before_buy) + 1
                        after_profit = int(before_profit) + int(price)
                        doc3 = {
                            'buy': after_buy,
                            'profit': after_profit
                        }
                        db.recordpaper.update_one({'number': number}, {'$set': doc3})
                    else:
                        before_buy = db.resume.find_one({'number': number, 'time': time})['buy']
                        if before_buy == '':
                            before_buy = 0
                        before_profit = db.recordpaper.find_one({'number': number})['profit']
                        if before_profit == '':
                            before_profit = 0
                        after_buy = int(before_buy) + 1
                        after_profit = int(before_profit) + int(price)
                        doc4 = {
                            'buy': after_buy,
                            'profit': after_profit
                        }
                        db.resume.update_one({'number': number, 'time': time}, {'$set': doc4})
                else:
                    doc5 = {
                        'pass': exp_time
                    }
                    db.menti.update_one({'number': client_number}, {'$set': doc5})
    return jsonify({"result": "success"})


@app.route('/pay_cancel/<int:menti_number>', methods=['POST'])
def pay_cancel(menti_number):
    bootpay = BootpayApi(
        "6119f0887b5ba4002352a0d7",
        "az77RPwwgdz+JdQUQzF4w77rpcpRqJ0zfR6oSVVXGV0="
    )

    result = bootpay.get_access_token()
    if result['status'] == 200:
        token = result['data']['token']
        print('token:', token)
        category_receive = request.form['category']
        time = request.form['time']
        number = int(request.form['number'])
        print('number: ',number)
        pay_info = db.pay.find_one({'client_number':menti_number, 'category':category_receive, 'time':time, 'number':number})
        receipt_id = pay_info['receipt_id']
        price = pay_info['price']
        client_number = menti_number
        name = db.menti.find_one({'number': client_number})['name']
        reason = request.form['reason']
        print('reason: ',reason)
        cancel_result = bootpay.cancel(f'{receipt_id}', int(price), f'{name}', f'{reason}')
        print('cancel_result:', cancel_result)
        # 취소 되었다면
        if cancel_result['status'] is 200:
            db.pay.delete_one({'category': category_receive, 'client_number': client_number, 'number': number, 'time': time})
            if category_receive == 'recordpaper':
                db.menti_data.delete_one(
                    {'number': client_number, 'miniTab': 'buy', 'category': category_receive, 'mentor_num': number,
                     'time': time})
                before_buy = db.recordpaper.find_one({'number': number})['buy']
                if before_buy == '':
                    before_buy = 0
                before_profit = db.recordpaper.find_one({'number': number})['profit']
                if before_profit == '':
                    before_profit = 0
                after_buy = int(before_buy) - 1
                after_profit = int(before_profit) - int(price)
                doc = {
                    'buy': after_buy,
                    'profit': after_profit
                }
                db.recordpaper.update_one({'number': number}, {'$set': doc})
            elif category_receive == 'resume':
                db.menti_data.delete_one(
                    {'number': client_number, 'miniTab': 'buy', 'category': category_receive, 'mentor_num': number,
                     'time': time})
                before_buy = db.resume.find_one({'number': number, 'time': time})['buy']
                if before_buy == '':
                    before_buy = 0
                before_profit = db.resume.find_one({'number': number})['profit']
                if before_profit == '':
                    before_profit = 0
                after_buy = int(before_buy) - 1
                after_profit = int(before_profit) - int(price)
                doc2 = {
                    'buy': after_buy,
                    'profit': after_profit
                }
                db.resume.update_one({'number': number, 'time': time}, {'$set': doc2})
            else:
                db.pay.delete_one({'number':client_number, 'category':'readypass'})
                doc3={
                    'pass':''
                }
                db.menti.update_one({'number':client_number},{'$set':doc3})
            return jsonify({"result": "success"})


@app.route('/callback', methods=['POST'])
def callback():
    return 'OK'


#admin record data save route add
@app.route('/ADMINISTER_recordpaper_data_save/mentor/<nickname>', methods=['POST', 'GET'])
def ADMIN_rec_data_save(nickname):
    mentor_number = db.mentor.find_one({'nickname':nickname})['number']
    # record_info = db.recordpaper.find_one({'number':mentor_number})

    data = request.get_json('sector_2_table_input_array')
    sector_2_table_input_array = data['sector_2_table_input_array']
    sector_3_table_array = data['sector_3_table_array']
    sector_4_input_textarea_array = data['sector_4_input_textarea_array']
    sector_5_table_array = data['sector_5_table_array']
    sector_7_input_textarea_array = data['sector_7_input_textarea_array']
    sector_8_1_input_textarea_array = data['sector_8_1_input_textarea_array']
    sector_8_2_input_textarea_array = data['sector_8_2_input_textarea_array']
    sector_8_3_input_textarea_array = data['sector_8_3_input_textarea_array']
    sector_9_textarea_array = data['sector_9_textarea_array']
    doc = {
        'sector_1_li_html' : data['sector_1_li_html'],
        'sector_2_table_input_array' : sector_2_table_input_array,
        'sector_3_table_array' : sector_3_table_array,
        'sector_4_input_textarea_array' : sector_4_input_textarea_array,
        'sector_5_table_array' : sector_5_table_array,
        'sector_6_table_array' : data['sector_6_table_array'],
        'sector_7_input_textarea_array' : sector_7_input_textarea_array,
        'sector_8_1_input_textarea_array' : sector_8_1_input_textarea_array,
        'sector_8_2_input_textarea_array' : sector_8_2_input_textarea_array,
        'sector_8_3_input_textarea_array' : sector_8_3_input_textarea_array,
        'sector_9_textarea_array' : sector_9_textarea_array
    }
    db.recordpaper.update_one({'number':mentor_number},{'$set':doc})
    return jsonify({"result": "success"})


import sys
import imp
@app.route('/account_setting')
def account_setting(LinkID, SecretKey, IsTest, IPRestrictOnOff, UseStaticIP, UseLocalTimeYN):

    return LinkID, SecretKey, IsTest, IPRestrictOnOff, UseStaticIP, UseLocalTimeYN


from popbill import AccountCheckService, PopbillException


@app.route('/checkAccountInfo', methods=['POST'])
def checkAccountInfo():
    LinkID = "READYMATE"

    # 발급받은 비밀키, 유출에 주의하시기 바랍니다.
    SecretKey = "pewjupUbgHcaSB/COkQpR2eL92DMSuD/lZZ0XtrvlZA="

    # 연동환경 설정값, 개발용(True), 상업용(False)
    IsTest = True

    # 인증토큰 IP제한기능 사용여부, 권장(True)
    IPRestrictOnOff = True

    # 팝빌 API 서비스 고정 IP 사용여부(GA), true-사용, false-미사용, 기본값(false)
    UseStaticIP = False

    # 로컬시스템 시간 사용여부, 권장(True)
    UseLocalTimeYN = True

    accountCheckService = AccountCheckService(LinkID, SecretKey)
    accountCheckService.IsTest = IsTest
    accountCheckService.IPRestrictOnOff = IPRestrictOnOff
    accountCheckService.UseStaticIP = UseStaticIP
    accountCheckService.UseLocalTimeYN = UseLocalTimeYN

    '''
    예금주정보 1건을 조회합니다.
    '''

    try:
        # 팝빌회원 사업자번호
        CorpNum = "2928702175"

        # 조회할 계좌 기관코드
        bankCode = request.form["bank_code"]

        # 조회할 계좌번호
        accountNumber = request.form["bank_account"]

        accountInfo = accountCheckService.checkAccountInfo(CorpNum, bankCode, accountNumber)

        holder_name = request.form["holder_name"]
        bank_name = request.form["bank_name"]
        user_number = int(request.form["user_number"])

        if holder_name == accountInfo.accountName:
            doc = {
                'bank': bank_name,
                'account': accountInfo.accountNumber
            }
            db.mentor.update_one({'number': user_number}, {'$set': doc})
            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "fail"})

        print("=" * 15 + " 예금주조회 " + "=" * 15)

        print("bankCode (기관코드) : %s " % accountInfo.bankCode)
        print("accountNumber (계좌번호) : %s " % accountInfo.accountNumber)
        print("accountName (예금주 성명) : %s " % accountInfo.accountName)
        print("checkDate (확인일시) : %s " % accountInfo.checkDate)
        print("resultCode (응답코드) : %s " % accountInfo.resultCode)
        print("resultMessage (응답메시지) : %s " % accountInfo.resultMessage)
        return jsonify({"result": "success"})
    except PopbillException as PE:
        print("Exception Occur : [%d] %s" % (PE.code, PE.message))
        return jsonify({"result": "fail"})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)