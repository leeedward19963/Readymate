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

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'


client = MongoClient('15.164.234.234', 27017, username="readymate", password="readymate1!")
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
        univ_arr = find_mentor['mentor_univ']
        major_arr = find_mentor['mentor_major']
        type_arr = find_mentor['mentor_type']
        num_arr = find_mentor['mentor_number']

        univ_arr.append(univ)
        major_arr.append(major)
        type_arr.append("")
        num_arr.append(num)

        info_doc = {
            'mentor_univ': univ_arr,
            'mentor_major': major_arr,
            'mentor_type': type_arr,
            'mentor_number': num_arr
        }
        db.mentor_info.update_one({'number': number}, {'$set': info_doc})

        doc = {
            "univAttending_file_real": ""
            # 나중에는 실제 path도 지워버려야
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
        html = request.form["rec_html"]
        awards = request.form["awards"]
        pages = request.form["pages"]
        volunteer_hours = request.form["volunteer_hours"]
        print(awards)
        print(pages)
        print(volunteer_hours)

        doc = {
            "record_info": html,
            "awards": awards,
            "pages": pages,
            "volunteer_hours": volunteer_hours
        }

        db.recordpaper.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("login"))


@app.route('/ADMINISTER/rec_remove/<number>', methods=['POST'])
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
            time = db.visit.find_one(
                {"to_number": int(number), "from_number": payload["number"], "category": 'recordpaper'})
            if time is None:
                visit_doc = {
                    "to_number": number,
                    "category": 'recordpaper',
                    "from_status": status,
                    "from_number": payload["number"],
                    "current_time": [now_in_form]
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
                        {'$set': {"current_time": check}})
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
            time1 = db.visit.find_one(
                {"to_number": int(number), "time": time, "from_number": payload["number"], "category": 'resume'})
            if time1 is None:
                visit_doc = {
                    "to_number": number,
                    "category": 'resume',
                    "time": time,
                    "from_status": status,
                    "from_number": payload["number"],
                    "current_time": [now_in_form]
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
                                         "category": 'resume'}, {'$set': {"current_time": check}})
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
                    "current_time": [now_in_form]
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
                               mentor_info=mentor,
                               data_num=data_number, story=story_info, mentorinfo=mentorinfo, follower=mentor_follower,
                               followed=followed, token_receive=token_receive, action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, myFeed=myFeed, my_alert=my_alert)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('story.html', mentor_info=mentor, story=story_info, mentorinfo=mentorinfo,
                               like_count=like_count, reply_count=reply_count, data_num=data_number,
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
                                   mentorinfo_info=mentorinfo_info, story_info=story_info,
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
    # my_pay = list(db.pay.find({'client_num':payload['number']}))
    ########### 디비 구성된 뒤에 꼭 렌더템플릿으로 보내야 함 ###########

    return render_template('menti_mypage_pass.html', menti_info=menti_info, me_info=me_info,
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
    my_recordpaper_all = list(
        db.menti_data.find({'number': int(payload["number"]), 'category': 'recordpaper'}, {'_id': False}))
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
            # exp = db.pay.find_one({ 'time':'','number':int(document['mentor_num']),'client_num':int(payload["number"])})['exp_time']
            exp = "2021년 12월 26일"

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
            # exp = db.pay.find_one({ 'time':document['time'],'number':int(document['mentor_num']),'client_num':int(payload["number"])})['exp_time']
            exp = "2021년 11월 56일"

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
                                               'mentor_type': True}))
    # make filtered array through univ
    univ_filtered = []
    if selectedUnivArray == []:
        for mentor in mentor_all:
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
                'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 6시간 유지
            }
            db.menti.update_one({'email': payload['id']}, {'$set': doc}) and db.menti.update_one(
                {'phone': payload['id']}, {'$set': doc})
        else:
            nickname_find = find_mentor['nickname']
            if request.remote_addr == '218.232.131.116' or '127.0.0.1':
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

    msg['Subject'] = 'READYMATE 회원가입 인증번호'
    s.sendmail("leeedward19963@gmail.com", email_receive, msg.as_string())
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
        #     extension = filename.split(".")[-1]
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
            "record_info": ""
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
            link = f'http://localhost:5000/resetpassword/{num}'
            mail_msg = link + ' 비밀번호 재설정 링크입니다.'

            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login('leeedward19963@gmail.com', 'hldamhxeuphkssss')
            msg = MIMEText(mail_msg)

            msg['Subject'] = 'READYMATE 비밀번호 재설정 링크'
            s.sendmail("leeedward19963@gmail.com", id_receive, msg.as_string())
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
        resume_select_receive = request.form["resume_select_give"]
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
                "resume_select": resume_select_receive,
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
                "release": "hide"
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
                    "resume_select": resume_select_receive,
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


@app.route('/story_save/<int:number>/<time>', methods=['POST'])
def story_save():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        find_mentor = db.mentor.find_one({'phone': payload['id']})
        mentor_num = find_mentor['number']
        story_title_receive = request.form["story_title_give"]
        story_category_receive = request.form["story_category_give"]
        story_desc_receive = request.form["story_desc_give"]
        story_time_receive = request.form["story_time_give"]

        doc = {
            "id": payload['id'],
            "number": mentor_num,
            "visit": 0,
            "release": "hide",
            "story_title": story_title_receive,
            "story_tag": story_category_receive,
            "story_desc": story_desc_receive,
            "time": story_time_receive,
        }
        db.story.insert_one(doc)

        doc2 = {
            "number": mentor_num,
            "category": "story",
            "time": story_time_receive,
            "who": []
        }
        db.like.insert_one(doc2)

        doc3 = {
            "number": mentor_num,
            "category": "story",
            "time": story_time_receive,
            "who": []
        }
        db.bookmark.insert_one(doc3)

        doc4 = {
            "number": mentor_num,
            "category": "story",
            "time": story_time_receive,
            "reply": []
        }
        db.reply.insert_one(doc4)

        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
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
        sell = request.form["sell"]
        doc = {
            "release": sell
        }
        db.resume.update_one({'number': payload['number'], 'time': time}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/recordpaper_sellyes', methods=['POST'])
def recordpaper_sellyes():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        sell = request.form["sell"]
        doc = {
            "release": sell
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
        if db.recordpaper.find_one({'number': payload['number']})['time'] is not None:
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
                file_path = f"record_files/{filename}"
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

    return render_template('charge.html', product=product, me_info=me_info, action_mentor=action_mentor_array,
                           nonaction_mentor=nonaction_mentor_array, status=status, my_alert=my_alert,
                           token_receive=token_receive)


@app.route('/charge/product')
def charge_product():
    token_receive = request.cookies.get('mytoken')
    try:
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
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


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
        univ = db_mentor_info['mentor_univ'][0]
        major = db_mentor_info['mentor_major'][0]
        type = db_mentor_info['mentor_type'][0]
        student_num = db_mentor_info['mentor_number'][0]

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
        if db.pay.find_one(
                {'category': 'recordpaper', 'client_num': me_info['number'], 'number': mentor_number}) is not None:
            buythis = db.pay.find_one({'category': 'recordpaper', 'client_num': me_info['number'], 'number': mentor_number})[
                'exp_time']
        else:
            buythis = ""

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
                               buythis=buythis, action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, status=status, follower=mentor_follower,
                               followed=followed, my_alert=my_alert, token_receive=token_receive)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('recordpaper_sell.html', mentor_info=mentor_info, record=record, this_like=this_like,
                               this_reply=this_reply, resume_array=resume_array, story_array=story_array,
                               mentorinfo_info=mentorinfo_info, myFeed=False, me_info=None, buythis=None, status=None,
                               token_receive=token_receive)


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
        if db.pay.find_one(
                {'category': 'resume', 'client_num': me_info['number'], 'number': mentor_number}) is not None:
            buythis = db.pay.find_one({'category': 'resume', 'client_num': me_info['number'], 'number': mentor_number})[
                'exp_time']
        else:
            buythis = ""

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
                               myFeed=myFeed, me_info=me_info, buythis=buythis, action_mentor=action_mentor_array,
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
    print(record_comment_array_number)
    print(record_comment_array_text)
    record_comment_dict = {}
    for number, text in zip(record_comment_array_number, record_comment_array_text):
        print(number, text)
        record_comment_dict[f'{number}'] = str(text)
    pprint.pprint(record_comment_dict)
    doc = {
        'record_info': record_info,
        'record_comment_dict': record_comment_dict,
    }
    pprint.pprint(doc)
    db.recordpaper.update_one({'number': mentor_number}, {'$set': doc})
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

        product = 'readypass'
        return render_template('finish_charge.html', me_info=me_info, action_mentor=action_mentor_array,product=product,
                               nonaction_mentor=nonaction_mentor_array, status=status, my_alert=my_alert, token_receive=token_receive)

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


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
        return render_template('finish_charge.html', me_info=me_info, action_mentor=action_mentor_array,product=product,target_info=target_info,
                               nonaction_mentor=nonaction_mentor_array, status=status, my_alert=my_alert, token_receive=token_receive)

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/coupon_insert', methods=['POST'])
def insert():
    coupon = '1AE3-C0CP-QTFM-FGBV/ 1AQ6-4UHJ-P32B-SO75/ 1A8O-MGBO-PSV5-R5O4/ 1AA4-X3OQ-8HF7-IPU7/ 1AT8-77K6-8MJM-8H7C/ 1AJ0-U8P8-AVFV-O63C/ 1ACS-4654-TQ28-C6PD/ 1AMT-53PF-466Y-533E/ 1A3R-C177-40N1-FAI6/ 1A12-A447-O576-1430/ 1AA3-7LJF-GK45-0H63/ 1A7M-N2XE-68B1-5KK6/ 1A37-3513-5B54-L8KM/ 1A2E-JCQO-DS8J-40P2/ 1APW-84E8-86RX-1A8E/ 1A85-40W2-32C5-664T/ 1AN3-25TD-25ID-Q0GL/ 1AXA-VMK8-76L6-NTSQ/ 1ALU-NPN1-IY87-3TWB/ 1A2D-K4KY-284D-E85C/ 1AGF-IM30-K86P-A6DC/ 1AU3-FHU8-YI14-B7LU/ 1AX8-2HG4-XS84-WT10/ 1A31-R7B5-4232-8R7W/ 1AS8-2216-M623-O1A5/ 1ASW-11PO-LD2D-XK55/ 1A1N-8M8H-NV72-3HR2/ 1AWT-E4XM-N3WE-51B0/ 1AHU-R5KN-73A7-1G45/ 1A26-0IF6-V1WM-D413/ 1AF2-2TE6-1ATL-5L42/ 1A0N-762I-LNFW-12S8/ 1AG7-4453-1HV5-0200/ 1A43-38W5-HXRW-4YK2/ 1A8O-EL5B-3IEV-0V14/ 1A2Q-5477-5KMK-G83R/ 1A1V-00Y6-GQ3B-S34V/ 1ABT-7YOG-QS55-6K0A/ 1A28-RREX-B5G8-5B86/ 1A6V-3I8E-3X8W-5JMB/ 1A2U-2160-CE3H-1INR/ 1AA5-I5O3-7153-4YYA/ 1AUL-7EY6-XJEI-3OUC/ 1A4F-4QE8-BA6B-4CW2/ 1ALA-B1N1-W808-1Q74/ 1AHI-CWFU-N4JU-A874/ 1A50-O2O2-C41P-2J8V/ 1AL0-B8GG-6Y8J-YT38/ 1ASG-08X4-AN82-6DY8/ 1AUD-5563-J74I-HP42/ 1AR1-I66U-P25J-N143/ 1AL3-K760-LK76-N5AD/ 1AHN-MVT5-NRVV-86GL/ 1A3Y-00E7-W7C7-7463/ 1A63-201E-VFCF-VTWV/ 1APR-ON0N-6W21-2F5E/ 1A6D-AU0L-AE25-E7CV/ 1AXW-4Q46-2B77-X208/ 1A12-56D8-PE2F-7U83/ 1A0E-2OUH-RM35-071T/ 1AJ8-55JK-6EK1-6O31/ 1AFM-818J-0NLF-44GY/ 1A41-30VX-3D1C-OC8R/ 1AF7-W371-35NR-3QHH/ 1A5H-E1S2-Y13L-HY71/ 1AWN-L1Q2-04AM-6BC3/ 1AP4-R28L-C0S8-J647/ 1AA3-5O6G-SEO1-8WB4/ 1APD-O215-ON7Q-WE6B/ 1AU6-8W5K-L236-AE4P/ 1ADX-7CL8-HHR1-RMF7/ 1AYE-CKQ1-3T14-L8W1/ 1ACT-FPFH-7J3K-4XW2/ 1AVP-G1N6-5L25-Q8I7/ 1AX6-1Q24-0P54-2OP4/ 1ASG-567X-2RA3-5K24/ 1AI3-4I73-I6A2-E455/ 1AX4-ANLS-B542-HMNG/ 1A43-C0EN-7UL0-3D27/ 1A2W-HHKB-OEQ7-2CX8/ 1AU1-JFM1-WXQY-63R7/ 1A15-RGI8-2NQN-L3XA/ 1A3Y-1NY0-GOP0-6213/ 1AU0-T5U0-C3QI-30BQ/ 1A6X-642C-47T0-83OH/ 1AQ7-2Y66-EC6T-UQD0/ 1A2X-K8AW-11KD-2350/ 1A0H-MPC5-N5BI-UEDD/ 1AU7-S7FS-42FL-BD22/ 1AYO-QXXM-S7DT-6P3R/ 1A54-C687-73B4-70R8/ 1A02-HN26-RK68-D4W5/ 1AKD-NWFC-JH8N-73DB/ 1APG-4FQ0-FGE0-Y144/ 1AYN-O42V-25D5-460I/ 1A73-YKNQ-YEH4-H4W3/ 1A1R-0A3C-PL44-VG7J/ 1A8S-J4C6-0B8O-6F7V/ 1AP6-OYN7-1GA8-8W44/ 1AF2-G6R1-5Y8R-73Y6/ 2A22-I312-R2SJ-3HP6/ 2AGU-2T5X-37M3-4X6M/ 2A60-51I8-E206-CQ5R/ 2A5A-762L-8TQC-W714/ 2AE4-44X6-M67W-2P53/ 2ACI-K5CT-2E8D-Q5WO/ 2A2E-7WQX-X8W5-NFKX/ 2AEE-70AW-WQ3S-6M37/ 2ANY-MMW7-3T08-NVM7/ 2AD2-8T4H-XQ77-S13D/ 2AJS-076W-W666-BD64/ 2A5T-TX74-O150-J8DJ/ 2AOO-2877-18MT-2377/ 2A61-BJ2W-U4H6-C076/ 2A6Q-V610-2D8C-L8RR/ 2A32-21J0-DLY3-P2QA/ 2A8C-0L48-SS07-83LC/ 2AU5-U3D1-868E-GB5C/ 2AQ4-6MR5-68I6-Y7MI/ 2A7P-E651-O87T-BJ57/ 2AIQ-1011-UN13-36IW/ 2A1O-WK6P-0247-GB52/ 2API-44K2-BV1S-U58N/ 2A6X-D4MI-N205-02LA/ 2A2T-X33X-57M2-VDM4/ 2AA1-6JB1-3RE1-ISG2/ 2A3Q-0M3E-DL6L-27PX/ 2A66-72HG-CQ65-42FT/ 2A1X-S1S0-FTL7-SP45/ 2AQI-21PX-58US-FT37/ 2A52-P20O-LTBD-U2IF/ 2AT2-XBNX-B36U-71HT/ 2A04-4B0G-OT64-2W7W/ 2AKX-8V6L-0CGU-YB74/ 2AC5-PWF6-RAR1-513H/ 2A26-BL1G-37AB-X320/ 2A0Q-B7W5-32NV-I1RT/ 2A3G-8G5P-76M8-C11E/ 2AU6-8504-S67R-050M/ 2A64-4G1W-VQ5S-6MH1/ 2A1P-P2F8-2257-3P5Q/ 2ALT-LGLI-Q422-L6M5/ 2AR3-CQ10-N6KP-7704/ 2A6X-WA17-TJ8O-211I/ 2AN8-JY3X-U0QD-7563/ 2ACM-UM2B-4M5K-432L/ 2AMV-GF53-4M57-YS3W/ 2AOC-XQ80-88R2-7KPE/ 2A5P-UEJ6-5B10-JG54/ 2ARA-1622-E7OT-67RM/ 2AGM-H5PY-MGYD-8V04/ 2A53-755V-8CM2-2KN6/ 2A4F-X1R6-5D6O-B2OS/ 2ABX-1IU1-HAWE-7XHE/ 2AJV-IB4V-U281-3OR8/ 2A7L-45HQ-VF0R-D341/ 2ATF-82SF-8GBU-8KQ1/ 2AJ4-VQ6N-7IC1-FTG6/ 2A5Q-R34G-6884-1ILX/ 2A6U-S6M5-E11A-8156/ 2A53-2SJ8-02KD-85YN/ 2A1U-2804-FFFM-PW0S/ 2AX6-52DX-IP2M-6UK1/ 2A82-12M1-U7P0-DKSB/ 2AFD-UI7V-DE2O-J3CY/ 2AT4-57RG-G230-5XM6/ 2AGO-H88V-R0XA-5IKN/ 2A3O-1M0K-00PN-4770/ 2AYW-3AV4-ODT1-HV58/ 2AYP-52EP-16WB-T46Q/ 2AN2-138Q-67OA-R80E/ 2AWG-66X1-T4ED-A4QM/ 2AHV-F156-UT6N-M006/ 2AA7-2GCK-VL35-L0NE/ 2AR3-F62N-818Q-UGOJ/ 2A17-YHJG-QQ16-3LMY/ 2A1D-OEE0-3702-4F3L/ 2A3G-6570-0IM4-4TH6/ 2AU8-08PN-8C67-7PCS/ 2A0R-76J4-S528-W5VU/ 2A4V-N527-TIYE-X501/ 2A8T-PKF0-0748-P087/ 2AX6-8RSS-5C66-4WM8/ 2A86-7NE7-C780-WE2C/ 2AR2-1U0H-51IX-8R58/ 2A75-6E0G-66N3-222W/ 2ATY-J0VS-5741-H7Y0/ 2AW5-6511-21RE-0N5S/ 2A8H-6B2L-JVAQ-8102/ 2A83-L6TR-R2YV-48IM/ 2A45-PXI4-7572-73GP/ 2AAX-E7XJ-18P4-7QMW/ 2A00-WT3C-7RSI-6545/ 2A3N-O534-352V-4WCR/ 2AR3-P13X-603F-IOEC/ 2AMA-0R0W-N6I3-28XI/ 2A0V-M4PB-U7H6-CHYH/ 2A1F-7JQJ-4LYI-73PD/ 2A64-8WU4-0RG0-67LF/ 2AVO-4V63-T5LA-632M/ 3ACH-63X7-LELO-2UV3/ 3ASU-WL27-42O7-56O6/ 3A8M-7X63-T2WT-PY0I/ 3AHS-53H6-LU4E-5PBG/ 3ABM-021D-K764-AR63/ 3A6U-BLWC-XJ2H-T21Q/ 3A00-5HHH-J3UB-23U7/ 3AED-DN0L-P608-6H1Y/ 3AYU-C8K4-8QXC-BNY4/ 3AG2-263J-6HBP-4LS1/ 3A7Y-L85M-0036-VK25/ 3AYG-41EJ-3OAC-72B0/ 3AJV-8P20-T7W7-JNIS/ 3AV5-6I47-24T0-1I76/ 3A04-HTJI-2Q0W-583D/ 3A80-7FBG-NVG7-S42A/ 3AN6-6N7I-45KG-SHHC/ 3AQG-7H50-614J-G0TM/ 3AL3-7C8F-P213-ADRR/ 3AUD-0LCJ-FX13-Q0T3/ 3A6B-37P3-1SPB-G0IC/ 3A24-Y54G-15S3-62Q2/ 3A76-F4TC-N5K0-01X7/ 3AL2-T5AN-3JWC-4G41/ 3A07-600V-JIA5-80YH/ 3A4C-5OK3-J666-TXK8/ 3AH8-R5HY-XF41-6U56/ 3A16-856O-63I2-LGQO/ 3AIE-R8M5-38PA-3WE1/ 3AP4-7327-58DY-8A75/ 3A66-N46X-HKUB-A6LS/ 3A17-6YVY-7I2S-6Y01/ 3AU1-51W0-3RKF-6124/ 3AD0-38A6-H5UA-TF87/ 3AVD-K044-5L0V-M2JA/ 3A8O-6G25-E872-0T53/ 3AR2-Q56F-R0M1-8HVM/ 3A23-6X70-PG37-7355/ 3A7C-28O8-3R5R-3D0V/ 3A73-6JKM-W6U2-16F7/ 3A03-3JRI-D016-CKW3/ 3A7B-R18I-337D-M03L/ 3A83-804Q-HMH8-1454/ 3AFK-6H8G-77B8-TYWR/ 3A14-5HUN-5CNH-7XLI/ 3A5E-7XJO-CO6X-25B3/ 3AJ0-P562-M6WG-65FV/ 3A68-2YM1-1V78-LV01/ 3A8A-JMTI-JI4Y-82T1/ 3AA0-50F8-O66U-VS2X/ 3A02-36LC-7D3C-E4F4/ 3AE2-Q1C5-Y87Y-0PB2/ 3A5L-ILP2-0AV7-R0VY/ 3A8F-OU0O-GBTW-G8OU/ 3ALR-C71I-S7Y7-EUL1/ 3AEC-2R78-E2LU-L2SM/ 3A14-R016-A204-7D38/ 3A17-YHN1-121F-7I52/ 3ADD-T615-47RV-708K/ 3A6N-F66P-S3L1-3X37/ 3AY6-P11R-78S0-GM73/ 3AVM-17B6-ARJL-18FE/ 3A77-EHS7-0O7M-D34A/ 3AVY-1BC5-EO02-C50R/ 3AP2-CCRQ-Y3XH-HP86/ 3AK8-25P2-4207-8N04/ 3AEI-T86R-4M14-R2YB/ 3A3J-617X-V164-B1M0/ 3AWC-570S-R767-04D1/ 3A2X-8HDS-WUD7-FD7B/ 3A54-16PB-XW5M-36J4/ 3ADH-YU16-3565-1TVN/ 3ASA-J523-6B8S-M0PB/ 3ALQ-557A-3A82-8QR0/ 3A6F-528U-H8AM-6778/ 3AOX-2JVA-A1A2-4JUM/ 3AQ4-F2X2-A15N-S6E6/ 3AY1-3KWT-81C0-3T4T/ 3A18-5A28-YI7Q-7N88/ 3A4P-V214-0WRO-PBNM/ 3AF5-U655-EI7S-085G/ 3A88-426H-2R53-G70N/ 3AY1-GUSC-F864-KI2K/ 3AEP-280Y-4OP1-1WC7/ 3A00-W67O-U87D-8OIM/ 3AUW-6568-4741-04V6/ 3AFO-005E-1678-3G85/ 3A8C-RC5Y-740Q-A20H/ 3AA7-8F6F-027B-18KO/ 3AJ8-7M68-83SL-4J2K/ 3A62-TD15-2717-7ML2/ 3AW6-183N-4TCS-Q2Q4/ 3AB5-37MB-O20A-Y8U8/ 3AAE-0G3N-55D3-R558/ 3A1X-50X2-035P-M77G/ 3AQ1-RN6A-DYQH-JE2N/ 3AM4-JU67-6XIE-L8IT/ 3A1V-3K23-ST0S-V60O/ 3AA4-M562-F5H0-2S1N/ 3A2M-8680-480G-P26X/ 4A6M-N4UF-ORP8-J4R0/ 4A6F-RBX7-430W-6W48/ 4A36-264D-B110-3L81/ 4AN6-E68N-3DU1-R1TE/ 4A7T-PVX2-2PK3-W64V/ 4A2H-WC68-8G5H-RTE6/ 4AV0-S0BW-12C2-66SQ/ 4A7E-RS85-K3G8-2LXR/ 4AX3-J2UY-77X1-5N2S/ 4AES-F5A1-20SD-RO33/ 4A46-EE8D-A0T3-4RQL/ 4A73-84GO-U6N7-8088/ 4AO4-LI64-5A5S-U56P/ 4A77-YFHO-UK2N-PEC2/ 4AM6-RS7B-4AB6-LEO6/ 4A4I-J5OJ-8B41-M6MA/ 4AUX-E23G-6W43-5LK5/ 4A26-1SR3-O48M-G7D3/ 4A88-45S8-G3I7-FQH4/ 4AWH-2Q13-4IQT-M726/ 4A1Y-10R1-U127-6356/ 4A48-8Q7L-X1HA-15M8/ 4A2I-66NP-W76R-J2D8/ 4A7M-SNQ3-U8L0-S1R2/ 4AL7-66O6-20E2-0DOW/ 4AF8-MEAX-RIKO-3O4D/ 4A36-F515-1KS1-QO01/ 4ABH-5100-30WJ-E7TF/ 4A3E-041F-FJF1-8Q66/ 4AW3-BR77-2VGB-4SFF/ 4AP5-7Y50-4V0I-3QH8/ 4A58-K1L2-25I6-E225/ 4ACR-0688-0843-T00I/ 4A7K-QY4F-VA4T-6471/ 4A8B-7506-142G-15KJ/ 4AVF-E418-2H60-H27F/ 4A3O-1PSQ-4ILR-3ODM/ 4A5B-ELTH-462L-F6I4/ 4A28-2RHU-N480-APC3/ 4A6X-06AI-KR0J-4JM8/ 4AXG-X2PC-36WD-5JDE/ 4A67-N01L-307K-Y175/ 4A3T-2RA2-C67X-18G2/ 4A50-MJTH-802O-J8WU/ 4A36-Q0A6-L722-S0W2/ 4AP1-03F1-86OC-FN0W/ 4A05-S238-4RJ6-P814/ 4A1A-85I2-BS8T-43G6/ 4A8Q-S024-FGSY-CHT2/ 4AU3-AC5U-80BF-K35L/ 4API-EB81-R5W0-1276/ 4A83-XATN-WT6Y-0S8O/ 4ANJ-H20A-U3PU-8C8L/ 4AGG-3JUV-R7ER-6D50/ 4A4G-UK01-CBB2-4HBC/ 4AKI-0MCK-PB7W-S0JA/ 4AVK-50R8-52CU-L2B3/ 4A04-27D3-HV15-RX23/ 4A45-FOD8-1M4L-V7BP/ 4A6D-PH2A-O06Q-55NF/ 4AJ2-61SS-2481-5465/ 4AO0-OAY6-0821-M404/ 4A87-B061-65G7-BD7V/ 4A3D-0AI7-03AI-6LJ4/ 4AW0-A2BX-XE27-H4HN/ 4ATB-1PS3-143M-18D5/ 4A0I-7O3I-G4QI-L35M/ 4A0H-5O4B-E617-T34F/ 4A5C-7AG4-0G41-T62W/ 4A5V-O1X0-582A-A5M7/ 4A6D-6XSJ-T6OQ-D76Y/ 4A6L-73UI-B6S3-6K73/ 4A1R-K8P1-A3M7-N44R/ 4A21-RPE4-3188-3VKF/ 4A13-0B37-B1F6-MDH8/ 4A15-Y77F-7XOJ-564J/ 4A6I-S432-0C34-C05V/ 4A1H-1T86-CJ1P-UE7C/ 4A81-UM61-84BE-63D5/ 4A7H-TG34-7Q61-X2IE/ 4A2P-DI4O-HX5E-OF8U/ 4AN8-JYX0-V5Y1-8HO2/ 4A01-313Q-A225-P3JN/ 4A43-MUY6-6B2H-M7B2/ 4AES-6V2A-1A77-U134/ 4A4A-C085-2AUF-HMUR/ 4A2D-2DCU-811O-41W3/ 4A27-OU3E-IVP0-GU78/ 4A36-B082-3G05-8Y2H/ 4A46-8266-FGS0-20UX/ 4A88-S3U3-JL13-758Q/ 4A01-2Y6X-A5Y3-ENG5/ 4A04-H336-8647-VEC4/ 4A68-80T4-X747-602V/ 4A75-P64Y-2K37-4872/ 4AVT-XF1N-6543-TULN/ 4A78-800S-6FMB-C7MG/ 4A4D-5FI8-70FP-E6VO/ 4AV0-7STM-3OE5-R3RJ/ 4ALI-78N5-5RG4-428O/ 5A64-C2S4-PMH5-62L1/ 5AA1-63QH-26YC-8S8E/ 5AT3-AA56-0IRJ-TNU1/ 5AAD-C8WI-8LN5-548G/ 5AQ8-WUJD-N774-4F6O/ 5A76-J4CI-5122-21D1/ 5A6J-VT4W-31JK-C35W/ 5AWD-G4H4-61BU-HFJ6/ 5A7O-E34U-A51L-5IC6/ 5A64-SH7J-4AO5-Q58C/ 5A3V-Q7UG-0BD2-07KL/ 5AO5-3B05-700H-MQ0X/ 5AF4-8225-47IE-PCKM/ 5AX8-H2FD-CA77-H5MH/ 5ABR-BY73-V603-W1KC/ 5A61-EIHU-S5D1-DWG2/ 5A08-SI3K-S78W-V376/ 5AD0-AQ32-L743-X86F/ 5A61-BRVT-PQDM-6B1E/ 5A25-8D07-7366-85GT/ 5A04-U0AQ-NCO6-H4A6/ 5AY5-7224-66QU-56Y3/ 5AW8-R5OC-7562-2I50/ 5A2G-0ST8-SWUH-3O3B/ 5AP8-5D4T-433P-21Q4/ 5A81-C2VV-I11M-L6L5/ 5A52-5PRK-0448-UO1Q/ 5AMN-7657-EQYI-IDYL/ 5A8R-LK83-6MP6-8O18/ 5A15-0FM4-3144-4P7I/ 5AF6-V6H1-T1HK-KCHG/ 5APB-JA57-HB85-7207/ 5A74-NJ7P-5Y32-1Q0U/ 5AJV-Y34O-8007-0PIR/ 5AJ1-46XB-8366-6XH2/ 5A60-21EV-51H5-12YW/ 5A0Y-338R-LV16-D5HQ/ 5AN4-M438-6R6S-O514/ 5AYT-6S50-R7RL-JV1O/ 5ASC-S415-02RF-8L7S/ 5AF0-442L-75C4-0T33/ 5A3J-NA47-V487-25TG/ 5A5Q-8GD7-U3Y4-E360/ 5AW1-73MQ-2W38-CJOY/ 5A0V-I43Y-030U-JFAV/ 5A2W-E2Y7-6188-T47J/ 5AG5-84M7-3R5O-7V8O/ 5AFV-R638-N2K0-SHA4/ 5A66-KTWF-JMUB-WJO6/ 5AW7-2564-F18E-BKA6/ 5AVP-7256-SFM6-B238/ 5AQS-NR4G-J1N4-GEST/ 5AD1-2M54-1I5Y-L7YU/ 5A0U-271R-R6O7-V717/ 5A85-QABN-50U6-35SC/ 5AOH-U8X3-E5FO-MF0N/ 5AB8-RK1V-MG55-2J42/ 5A08-M6K1-O4UU-L8O8/ 5AB4-B28U-RG4J-HB32/ 5AMM-0B1K-4X57-1QBG/ 5AF1-81H4-3J60-QC38/ 5A68-0JO8-3F84-2MV3/ 5AN8-4A2Q-32KP-RRA6/ 5A72-2UL0-F30I-42DT/ 5AP4-E6CG-A1J3-W316/ 5A4A-7T62-WDJP-1W85/ 5AX4-F47U-41E7-S4W8/ 5A5N-1X3A-C3L2-1NFH/ 5A24-8UO4-C312-53YU/ 5A8U-QW18-EQK3-AH0V/ 5AWC-4LG4-3WP1-R07M/ 5A11-KXL8-VR5W-TN7W/ 5AS7-1268-WL47-GYF4/ 5ASH-1500-484V-27O7/ 5A78-H321-8GO0-6004/ 5AHC-0I1H-IAE5-F514/ 5A30-ASAN-HHB6-P630/ 5A15-C5F6-60U6-BMLX/ 5AY1-DS01-JDBF-LU53/ 5AAM-I0ND-LME1-C051/ 5A0J-P8HT-VXWY-2Y47/ 5AX4-6KAG-N2GC-1222/ 5A40-F4Q5-V67J-I70A/ 5AT6-5X58-4201-J1TS/ 5AMN-378R-N3CA-121K/ 5AI1-7L48-KN6T-UKRV/ 5ATS-C8NN-NKYO-VM8N/ 5AG2-P558-L406-0160/ 5A68-TJWW-I8O1-VI0T/ 5AR1-T7M5-11QN-6Q8Q/ 5A43-5123-W3F7-QKXD/ 5A60-KI44-36IW-60SD/ 5A56-247J-WXTR-KA7H/ 5A3U-U77J-C28K-3737/ 5AX8-Y0HC-8734-7P3R/ 5A5X-7B04-B841-R342/ 5AOA-KOXI-N426-VHT1/ 5A3I-AU1U-1WK0-0EVO/ 5A7C-3X5Q-67E0-P6V4/ 5A2Y-81GK-6TB8-O2HN/ 6AD5-7BYO-0AGO-D83R/ 6AIN-JWTC-GNHC-08V8/ 6A6O-48SK-L2XK-PAKQ/ 6AW8-4DT1-521U-1U8C/ 6A08-0AA8-F3U4-S34H/ 6A8T-K474-AXO0-0K42/ 6A5M-78CN-81SO-7866/ 6A22-H76F-480L-53L3/ 6AL4-74E4-HAI4-O4UG/ 6AKC-HP34-D3T1-H333/ 6ANK-U670-1N4Q-A8WL/ 6AEN-378A-V4C2-P13D/ 6AL3-A686-2333-A0P4/ 6AJ6-15CS-62S2-7237/ 6A63-K1Q3-83UM-I1TF/ 6AL1-8J2N-753I-4647/ 6AT4-HP81-3540-7E81/ 6A6T-D1AV-A26Y-KWWM/ 6A34-JBM0-232O-QBC8/ 6AP2-G5XP-4A3A-EWEU/ 6AW8-J220-B07C-D120/ 6A3Y-3T43-3BE2-0546/ 6A48-T043-2321-21E5/ 6A7K-G06C-5O6S-M884/ 6A3T-HOOX-38GF-A2S8/ 6AJ5-4F6J-N6E8-1F3M/ 6A77-873C-2042-5MVL/ 6ARJ-G00Y-E4B6-G318/ 6A7K-506B-JR13-1V74/ 6A7C-G4VW-M27M-21Q0/ 6A7D-FM6Y-8145-6L47/ 6A4W-DNM5-78G6-070U/ 6A58-3L31-246M-02V4/ 6A0Q-4S35-L3SV-YK57/ 6AK3-63AD-3PY6-B284/ 6ABL-34Y6-1466-XUG1/ 6AUY-6B54-7CDD-4BIQ/ 6AQ7-K1VX-HK0W-2L1H/ 6AY0-V65U-61F0-81J0/ 6A1B-X387-CC14-0NV5/ 6AC6-E7A1-6134-P32W/ 6A74-8B18-J5YL-151D/ 6AVA-RDD4-1X3N-3537/ 6A45-7881-H304-FCAW/ 6AQT-L3E7-W8UF-P3SX/ 6AL6-234D-BK0I-8Y80/ 6AR4-THGK-U0TO-7WRL/ 6AP2-R23I-N2R7-400S/ 6AA0-8LY1-K6X8-NF08/ 6A1F-S41V-X261-B8DT/ 6A36-W063-Q6RF-4CD7/ 6AG0-JGT0-JYMG-IASM/ 6ADK-SL0W-MTR2-B6TH/ 6AQ4-8FFR-K43U-2VF5/ 6A1H-78J7-4M81-GL56/ 6A80-58B7-J41A-61FM/ 6A66-410L-X223-0OF7/ 6A5U-JJT5-6S28-F036/ 6AO4-24C3-U28V-ER3Y/ 6APF-Y1AN-P8QC-S563/ 6A4N-XA71-EXR0-8KW1/ 6A3P-313P-7ENM-D621/ 6AX1-6L60-8U27-KFGK/ 6AM8-XPWS-YOXI-0803/ 6A58-6BGH-HK12-IYMF/ 6AC6-GH74-7176-J028/ 6APO-IN8E-PAE0-M0DY/ 6A63-Q4U5-O15V-047H/ 6AV7-4PVQ-60AG-G4WQ/ 6ABX-V7TT-5ENF-CC16/ 6A7S-E53L-48N1-0852/ 6AC1-UW06-JTMP-C2FL/ 6AMB-N103-R27M-N37P/ 6A63-W322-H6B6-S07M/ 6A30-KP87-4J6G-G8GH/ 6AJH-R65U-CQ0Q-L4FI/ 6A3E-1HUF-87JM-4UXM/ 6A6M-1AAF-OM0G-U7DV/ 6AO7-0D5X-F2EJ-2L3B/ 6AQ6-6CD1-R30Y-BPCM/ 6AGF-O075-W74C-0376/ 6AL8-4F1D-DLH8-XPGR/ 6A4B-N6II-726Y-LV40/ 6AD6-7IKF-M1IG-H2LL/ 6AW0-2IWB-K1F5-PYMU/ 6AD7-36B6-16G4-CO38/ 6AD3-X18L-D1E0-S424/ 6AF1-6053-I8O0-0M05/ 6A12-216J-7212-2BRR/ 6AC6-4V7M-8JPK-4L13/ 6A55-M2Q3-CVUY-KL87/ 6A47-L2TH-HW12-1NH1/ 6AKC-1F2M-BTEM-53AB/ 6A28-60A5-3JGS-AABV/ 6AX6-46W2-PN32-N424/ 6A48-18YG-806P-21DN/ 6AO6-25F6-6W7I-0VPJ/ 6AJD-2O70-068X-A76Q/ 6A4S-OU8F-N7E6-CB76/ 6A1K-055Q-HADT-20U2/ 7AK5-65RF-18R4-6O43/ 7A3X-Y134-T47X-W36H/ 7AAS-P867-7T8Q-5675/ 7A7K-GI3U-P3R8-6Y86/ 7AH6-XE0C-6876-7EWU/ 7AM8-G7S0-WXGM-672G/ 7AS8-V7Y8-LABY-84AM/ 7A3I-1C07-KH61-13BT/ 7AOX-U52Y-R2BJ-213P/ 7A47-WYI7-805F-8UP6/ 7A4K-R8SB-84DL-3GIK/ 7AP3-FFAS-65CW-H7D5/ 7A1N-8HAO-2A62-K2PY/ 7AEW-42L3-I0FJ-GB0S/ 7AA2-K520-7S20-P767/ 7APG-2IDA-A3U6-O117/ 7AF1-8ATW-HYLD-XY88/ 7AOQ-MC0P-HOF7-47GF/ 7A66-5Q60-676S-1U1A/ 7A84-3RT3-6S60-RV1O/ 7AC2-YC38-BY8Q-6613/ 7A64-HPH5-U127-3815/ 7AO0-JMAA-A4Q8-3H03/ 7A3Y-M53G-4Y2A-28RF/ 7A2I-P413-U5H4-QMO5/ 7AH6-7401-15U5-083K/ 7AS4-P78P-1U51-43T5/ 7A6F-S037-RTU2-5467/ 7A77-LTIW-P53M-4B8S/ 7A07-AMC6-C8B7-8H5Q/ 7AD1-566C-F3FT-08X2/ 7A2M-G11G-G43N-B7S2/ 7A7T-BJ5F-R16G-R46P/ 7A1O-KPEY-F614-7S2B/ 7AG5-EA50-4Q33-IF7X/ 7AU0-6148-2481-TY4P/ 7A21-T5H5-8D3L-HIA1/ 7AOM-FP1V-71LF-5YMN/ 7A3K-8521-D04M-6JJG/ 7A0E-A866-O13Q-725N/ 7AF7-536E-XA7I-P6M6/ 7A63-0DXK-48W2-GN1C/ 7AO4-R8NJ-2E61-NI7M/ 7AT3-525V-4753-R1FE/ 7A8E-0JHS-4O0T-WB78/ 7AHR-R282-LE83-2DM6/ 7A87-M12I-3020-762U/ 7AMU-BN0P-J86J-3WA6/ 7AQP-S6U8-V1W6-2ACV/ 7AA5-588O-RIM6-3V6P/ 7A1L-25EQ-68MP-Y11V/ 7AXX-L6KK-76K1-HKEY/ 7AXK-HA6Y-3G08-5564/ 7A41-I7X0-JP3Q-35J2/ 7AVC-0FM4-VA4I-75VK/ 7A4W-8J24-BH3A-13A1/ 7A51-0JKE-3EOD-UFCH/ 7A1K-6DA6-RJ47-IN57/ 7AVI-24D0-551W-SA3N/ 7AHO-V43T-16JP-45PR/ 7AL6-316K-8R5Y-2RR3/ 7AS5-GO36-W8A2-W0E5/ 7A36-LRMC-PV3M-3WQC/ 7AJA-B828-N053-54CX/ 7A7K-S3PP-N2PV-Y181/ 7AX5-1MYE-N8H7-UA86/ 7A52-PB05-LJ1T-BJSE/ 7AXN-U6BE-QC38-7W77/ 7AWC-E77N-Q68T-8HSS/ 7AP1-WD45-40SB-7LC2/ 7A23-716R-GKNI-JT63/ 7AOQ-2V8W-PI53-N5A2/ 7A2R-B5JJ-A16W-303O/ 7AU7-0E1K-PEV5-50SH/ 7A24-OYA3-4Y27-OTN1/ 7A5M-MSW3-8AP4-84H5/ 7AIC-008O-FO41-2202/ 7A7M-J0C0-8PC5-4FXU/ 7A42-J4LT-GB1T-36W1/ 7A00-7GR7-2U24-88D6/ 7A81-C5LQ-5BSM-48L5/ 7A81-1C25-82EH-8V5V/ 7A4R-33H4-2070-H338/ 7AHO-8H3F-8SNB-FVP0/ 7A6N-PBF0-E48F-454M/ 7A3M-6A2G-F61O-VG5U/ 7A40-7DG4-117B-448C/ 7A7J-T012-060B-H453/ 7AC6-442N-YG2I-85O1/ 7AFG-611K-V74C-OXBU/ 7AB1-70UV-0LX4-Y32Y/ 7A0Q-2IK8-KI2E-UU35/ 7AH5-HC08-AD8C-6MR4/ 7A5Q-YBU0-251M-F2X1/ 7A5K-5261-6US4-D5GA/ 7A51-X04D-2UQ4-3B0Y/ 7AV8-OO3B-LE15-1X3O/ 7A25-WOPL-0N48-577D/ 7AV0-37QT-U5NP-1SY5/ 7A51-886U-3451-T2UB/ 8AW7-3HCE-SXE5-25IY/ 8AT6-4N31-7773-WWIM/ 8A3U-T00T-O7RY-G655/ 8A3B-7OUG-YJ7R-KHXQ/ 8AHA-NH58-6XF1-7521/ 8A5M-3387-Y4JD-7O7B/ 8A63-40I3-081R-5065/ 8AR6-234G-25L2-FSE2/ 8A8P-0G64-1HAN-HLW6/ 8AJ5-442Q-0861-YMND/ 8AOU-D3VH-7COM-81AR/ 8A43-50XI-Q75A-6K0R/ 8A0J-1M7P-12I4-F5H0/ 8A5H-7081-IG76-6FXP/ 8A40-8W0P-4X5T-6062/ 8AGN-WKGB-IK0U-WO2U/ 8AU6-QQU4-K07P-7CA1/ 8AA1-651E-2FTW-68TP/ 8AY1-GCYP-4Q7F-HCJS/ 8AIR-4713-A4Y8-162D/ 8A53-54Y2-B8AV-4SOD/ 8AAG-852E-8MBR-68WO/ 8AHW-VOT8-J0F3-S418/ 8AJ6-AL68-A087-W2C5/ 8ACT-A117-5O82-B86S/ 8A5H-5V8D-37CA-5BPQ/ 8AG4-WCA2-C8FU-625T/ 8AK5-4732-2TOX-125B/ 8AX3-178P-84WR-8KTF/ 8AT5-313T-A2AH-DSC4/ 8A08-R58Y-OH88-5E3D/ 8A87-8130-140O-NLV7/ 8A08-8B64-4B3H-205L/ 8A73-F600-3864-FI70/ 8AK3-11E4-QD2G-11I0/ 8ARL-6606-1C2B-J661/ 8AVX-535H-5364-376X/ 8A0B-5XB8-BO57-1N7A/ 8A1S-83UK-43A3-1T27/ 8AEO-3O71-L1S3-2RPW/ 8ARN-DC22-RIMM-XB7G/ 8A7C-8I4B-6J2V-C56L/ 8A42-3KMS-41NS-DP78/ 8A10-N2XO-3PBQ-PUX8/ 8A61-TNN0-33T8-1N02/ 8A76-QRJ4-3783-S7OI/ 8A3P-5B8W-8701-2TNM/ 8A8W-B15B-2O7V-6054/ 8A31-VUC8-67QB-1B0S/ 8A63-23NF-4GST-1E5X/ 8AMQ-Q78G-VK82-NG2L/ 8AHX-1ISU-514N-LLBG/ 8AU3-SYKC-SUDF-VV22/ 8A45-30K0-2IF5-0Y7D/ 8AV0-Q06V-6EH4-M6Y1/ 8AX0-65U1-T0LE-7QF1/ 8A03-V802-600O-07M1/ 8AL1-UP0M-S4JU-H70L/ 8A3H-S1KD-A2X1-8KPT/ 8A78-Q844-EUKV-E118/ 8A7C-X57G-0O2O-K533/ 8AMS-0Y24-8A16-5C6C/ 8AUH-CF0N-K2N8-J08L/ 8A5S-DI51-LIRC-2ABB/ 8A26-243B-OXB5-MH21/ 8A0Q-F54I-R8PR-KN82/ 8API-QUI1-LB01-60AE/ 8AXG-JVU1-3K63-3N54/ 8AJ6-TG5R-NC74-3T77/ 8ALV-OX05-7848-66F5/ 8ARC-R035-6813-VPIE/ 8A3H-S2O7-0BO0-JLJ4/ 8AHB-EK17-E755-7BMC/ 8AB2-31IB-5AA2-88AD/ 8AU0-671U-F3S8-JETY/ 8A51-O2F7-H310-IGQC/ 8A5P-5DVF-5M5W-30RN/ 8A81-2PWS-3HK2-Q1RO/ 8AP7-FD36-BD20-10W3/ 8AI1-0558-H514-R5K4/ 8APM-KEB8-1K43-2AX3/ 8AGF-46YU-8588-5D1O/ 8A12-HGDY-0E5J-5KWF/ 8AYW-3BKV-LYNH-6MBB/ 8AQ2-CKX4-T4EP-101J/ 8AAJ-525M-EPI3-QE84/ 8A8D-K3AP-8YU7-0VR7/ 8ASP-6614-Y683-CE76/ 8AN6-RP73-B133-5AKN/ 8A82-68P8-P50Y-2518/ 8AC1-70TJ-4H0G-45A7/ 8AJE-WAMN-52AV-L7Q8/ 8AK0-6RR3-Q0ON-EU6R/ 8AS3-LEN2-0CK5-510K/ 8A15-552J-2Q86-LN71/ 8A7U-AB62-KNOB-UN6O/ 8A1B-11V0-57G1-0671/ 8AVQ-MO57-N3EQ-WJ03/ 8AX1-0EO6-3Q76-H34F/ 8A2C-NL8L-2F1N-2DBA/ 9A35-TIVV-1V5T-2VYN/ 9A84-IR55-5RW3-1GOJ/ 9AT0-4Q83-3Q35-P77N/ 9A5I-Y0HA-2615-5F16/ 9A4V-RT0B-XQV7-8302/ 9A68-O821-R40W-I044/ 9AEX-J342-GFC3-D875/ 9AQ4-4YF1-230D-WJ1K/ 9A06-3IP4-R8U3-K8RF/ 9AF7-O336-AMEP-P710/ 9A13-G8C5-2400-X2NU/ 9AY6-5C0O-UWUG-0V56/ 9A2Y-5434-QO5J-58NM/ 9ACE-L544-2PK4-338E/ 9AL2-3076-03V0-X531/ 9A0J-6H2D-7HLU-2CLF/ 9A46-CJQ8-I282-01L5/ 9ARD-T4H6-MS0W-OTYE/ 9AEU-6X4Y-5PI0-S8E4/ 9ABX-4DH5-R40C-2530/ 9AL5-O175-124P-1A81/ 9AX3-K6QE-NLQC-5616/ 9A7L-O1O8-U0QA-L02L/ 9AJ3-207K-6FUO-52O5/ 9ADP-7G5B-0BDE-6256/ 9AA8-DNQM-21LD-7MWS/ 9ANT-YV5B-P2T4-0437/ 9A36-86V1-7H21-1L6O/ 9AEW-GT33-V581-MT45/ 9A4E-187W-1U46-14VD/ 9AQ5-Y83F-2TU7-1W8E/ 9A2U-WK42-6554-8TJ6/ 9A18-CSOM-G06N-MILD/ 9A4N-8M13-V554-M4F8/ 9ASN-D717-VM34-47M1/ 9A6Y-GV5S-X68S-K8GS/ 9A58-51MN-HKBV-0I6M/ 9AX3-4H38-RC55-IHE7/ 9AUX-PP72-11TE-05E1/ 9A55-1J63-BE70-66O6/ 9A11-5Q07-L3W1-YVO0/ 9A1U-43KV-3CW0-EDPE/ 9A2N-32U1-2I78-S2TQ/ 9ACM-S34K-S826-1SO8/ 9AN0-5100-845Q-V05Y/ 9AKF-1CPE-EO4X-03N3/ 9AHN-18BX-PLP4-A2G1/ 9ANN-6355-RY4Y-L0G8/ 9APD-12MS-TBRS-68G7/ 9AKU-VMO4-0MS8-SQM2/ 9A63-3IJ8-2RUY-EX08/ 9AX7-A12B-774P-JIMQ/ 9A23-GLJ3-C3LR-PDDG/ 9A05-W3Q2-L36T-MF6J/ 9AB1-3021-D7S3-LDY1/ 9A3Y-8C3P-OF88-CV77/ 9AG1-1846-SVU0-KB2S/ 9AXA-P013-3DSC-3150/ 9A3L-110I-RAEA-1K5H/ 9AR6-JJPV-W0P4-L878/ 9ANB-2D1N-AA60-CNHS/ 9A7T-VS3D-BVPR-4XY7/ 9A70-P6A6-8171-V0CN/ 9AG5-66A4-11F4-7E1U/ 9A8C-80LN-7B5U-MEK4/ 9A0U-2510-3D5I-JGO1/ 9APB-ALN3-NO2C-7Y68/ 9A4J-N5P8-0LT3-KEQ8/ 9A7F-AV33-I413-477N/ 9AIY-PBB2-3G8Y-O554/ 9A7N-63F8-5V7G-JCO6/ 9A16-21PM-24UO-8850/ 9A16-J85D-I5JW-37X3/ 9A45-CP7I-84Y7-6O1M/ 9A26-N6J1-V487-8YUL/ 9AVN-7HPW-15X6-137A/ 9A44-TNNJ-T274-43B4/ 9A0A-1183-HT0V-54RW/ 9A55-PT42-UHB7-DH8W/ 9AQ2-048Y-35UK-77YU/ 9A6Q-K20X-X2U1-JB46/ 9A82-DMWL-0WMD-5P2J/ 9A28-4061-NNW6-P8G6/ 9A15-0QC2-N03S-7RU2/ 9A17-I813-75QI-PQ82/ 9A27-1AQ8-4V43-78F5/ 9API-2P76-UK51-6307/ 9A1Q-M2H7-LT68-4H82/ 9AQ6-552L-270A-5JHK/ 9AA8-61A0-WKQ6-WC0R/ 9APO-Y642-7137-PXV7/ 9AI4-84CQ-4NG5-1WW6/ 9AW1-E686-8EU7-HM26/ 9ACO-3IWK-2YXS-NM03/ 9AGQ-M143-S4AE-8723/ 9AF3-PR24-CQ1B-J6U2/ 9A34-50AI-P3SV-76D6/ 9AF8-3122-7Y76-N46H/ 9AJ1-2TN7-YOT5-6404/ 9A25-00M7-863C-SB0T/ 0A0U-FOK5-07UH-5HCF/ 0A4E-LUL6-U0QK-618V/ 0AE5-M617-I5T2-VI2T/ 0AA2-12N0-5P12-M87H/ 0A13-5G66-C564-4LB5/ 0AIP-73WT-H7K0-HGY7/ 0AHW-1H54-W8I8-EQP3/ 0AE1-XD5T-FH8S-CX66/ 0AV6-2J8F-W21V-L781/ 0A6D-Y2F1-FE41-65U4/ 0A3T-7772-44L6-423C/ 0AC1-2HQB-O2B8-YBSH/ 0A6G-8UGJ-6PGA-KV3N/ 0AHG-208T-560E-07AK/ 0AK5-7O83-23EN-GY0V/ 0AG4-83GW-L241-E06W/ 0A7F-61S4-HBC5-A55S/ 0A5B-0P75-0563-LJ52/ 0AAM-V1I6-67O3-X0A1/ 0AIV-83P0-Q418-RN76/ 0AER-W7BW-QN0O-Y31V/ 0AB8-H30H-R66I-X1M5/ 0A7M-QH8N-34CU-7XVV/ 0A7V-J21R-HN6X-05PL/ 0A7O-MJ2V-STIP-F638/ 0A3J-DP56-45AK-0VD7/ 0AM5-44RX-J1F5-16I3/ 0A6E-86L0-2I13-FCT3/ 0AFE-2M3D-YT63-006H/ 0A5A-0D0T-56D1-5VWK/ 0AF0-0067-2243-3EG6/ 0AX6-83Q6-5748-84L8/ 0ATK-06SG-0WOK-56B3/ 0A05-C22A-AQ5H-SP10/ 0A1M-M2C8-O7VJ-215T/ 0A73-7PI4-53E8-BDBS/ 0AHD-COSS-P634-42AA/ 0A74-C1DG-4KI0-376N/ 0ACA-OVE2-O2OD-1M8D/ 0ARL-4IQ8-0NCJ-V5MG/ 0AW0-70CU-LJWE-0DS4/ 0A00-QQM1-161D-2770/ 0A2X-M23S-S6D4-3P22/ 0AJ3-13FG-7SH0-M1IG/ 0AQJ-63K4-AE16-B7B7/ 0A7H-HE7I-H557-UU51/ 0A26-J8N8-10V7-I5E0/ 0A2Y-FGXS-1J5T-64R4/ 0A3D-77N3-1L52-8QC3/ 0AK2-2754-618Q-53F4/ 0AFP-UAAF-OOA4-6033/ 0AA0-DN37-8308-7GMG/ 0A4N-QBF8-J031-D280/ 0A82-QX4K-83M1-GGFN/ 0ASW-CT61-3UDB-D363/ 0A11-67EH-NE23-7B54/ 0AS1-B884-E6S0-G1IS/ 0A68-QOB7-2Q3F-TK4B/ 0AA1-72KN-EVJ6-8108/ 0AW3-W5PL-QPI6-7KXM/ 0A03-N0E6-BI6C-D31M/ 0AT6-N418-U010-D624/ 0A02-Q67A-GY4D-7W82/ 0AQN-7FJ5-YXVH-6T36/ 0AG5-TKV6-WD62-K757/ 0AR7-61O5-51EC-05A5/ 0AMO-7G8G-QN16-7R64/ 0A14-K2EI-8UW0-O36T/ 0A42-E548-5Y68-KE84/ 0AGA-OB5A-2G0G-1CPG/ 0AM0-2T13-TN0R-4XO8/ 0A82-60R6-2CIW-C6VW/ 0A83-2MM2-287J-CGX7/ 0A47-N368-LQ8T-702C/ 0A48-2245-330C-1627/ 0AW4-1406-74J5-D15D/ 0AB1-Q5U8-364A-EHU5/ 0AG0-H74H-W1B0-O5J2/ 0A21-4PKI-83YK-221G/ 0A7O-RK51-CF3R-8TM0/ 0AQ8-I04M-I8LQ-0QRI/ 0A2Q-SF88-H3M2-612N/ 0AOW-2SS2-ROM3-210U/ 0ALR-2J5G-1784-255P/ 0A47-LH0V-227G-6DIU/ 0AB4-H2MO-A4LJ-T677/ 0AL4-EH85-U870-7VVH/ 0AK2-JJY7-B850-16P5/ 0ASA-158X-Y6IC-0QD6/ 0A7N-65UY-6133-GK34/ 0ACC-1AWC-1XVH-H023/ 0AP3-MI8E-4M2L-2187/ 0A22-12OR-1X07-2X38/ 0A31-EKJS-1KY3-3IO5/ 0AK4-Y8MT-6FDC-728C/ 0ABK-31F7-24P8-631A/ 0AGD-TD28-2EM3-KB44/ 0A31-C80H-824H-34O6/ 0AJ0-O1N4-81M5-67GU/ 0A74-K6BH-64WV-VW5E/'
    coupon_list = coupon.split('/ ')
    for cou in coupon_list:
        doc = {
            'coupon': cou,
            'sale': '30000',
            'date': '2021.8.19',
            'use': '',
            'number': ''
        }
        db.coupon.insert_one(doc)
    return jsonify({"result": "success"})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)