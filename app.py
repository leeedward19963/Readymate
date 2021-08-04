from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for, abort #https://m.blog.naver.com/dsz08082/222025157731 - 특정 ip 차단
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import random
import math
import time
import numpy as np

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('localhost', 27017)
# client = MongoClient('15.164.234.234', 27017, username="readymate", password="readymate1!")
db = client.RM_FLASK



@app.route('/ADMIN')
def admin_home():
    return redirect(url_for("ADMIN_mentor_list"))


@app.route('/ADMINISTER/mentor_list')
def ADMIN_mentor_list():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if payload['admin'] == 'yes':
        mynickname = payload['nickname']
        login_time = payload['login_time']

        mentor_all = db.mentor.find()

        return render_template('ADMIN_mentor_list.html', mynickname=mynickname, login_time=login_time,mentor_all=mentor_all)
    else:
        return redirect(url_for("/login"))


@app.route('/proxy_in/<number>', methods=['POST'])
def proxy_in(number):
    find_mentor = db.mentor.find_one({'number':int(number)})
    nickname = find_mentor['nickname']
    id = find_mentor['phone']
    payload = {
        'admin': 'no',
        'number': int(number),
        'id': id,
        'nickname': nickname,
        'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    return jsonify({'result': 'success', 'token': token})



@app.route('/ADMINISTER/menti_list')
def ADMIN_menti_list():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if payload['admin'] == 'yes':
        mynickname = payload['nickname']
        login_time = payload['login_time']

        menti_all = db.menti.find()

        return render_template('ADMIN_menti_list.html', mynickname=mynickname, login_time=login_time, menti_all=menti_all)
    else:
        return redirect(url_for("/login"))


@app.route('/ADMINISTER/confirm/<number>', methods=['POST'])
def ADMIN_mentor_confirm(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print(number)
    if payload['admin'] == 'yes':
        doc={
            "univAttending_file_real":""
            #나중에는 실제 path도 지워버려야
        }
        print(doc)
        db.mentor.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("/login"))


@app.route('/ADMINISTER/accepted/<number>', methods=['POST'])
def ADMIN_mentor_accepted(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print(number)
    if payload['admin'] == 'yes':
        doc={
            "univAccepted_file_real":""
            #나중에는 실제 path도 지워버려야
        }
        print(doc)
        db.mentor.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("/login"))


@app.route('/ADMINISTER/<status>/<nickname>')
def ADMIN_user_view(status, nickname):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if payload['admin'] == 'yes':
        mynickname = payload['nickname']
        login_time = payload['login_time']

        if status == 'mentor':
            mentor_info = db.mentor.find_one({'nickname':nickname})
            mentor_num = int(mentor_info['number'])
            mentorinfo_info = db.mentor_info.find_one({'number':mentor_num})
            recordpaper = db.recordpaper.find_one({'number':mentor_num})
            return render_template('ADMIN_mentor_view.html', mynickname=mynickname, login_time=login_time,mentor_info=mentor_info,mentorinfo_info=mentorinfo_info, recordpaper=recordpaper )

        else:
            menti_info = db.menti.find_one({'nickname':nickname})
            return render_template('ADMIN_menti_view.html', mynickname=mynickname, login_time=login_time,menti_info=menti_info)
    else:
        return redirect(url_for("/login"))


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
        return redirect(url_for("/login"))


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
        chartJsArray = [chartJsArray_1,chartJsArray_2,chartJsArray_3,chartJsArray_4]
        print(chartJsArray)

        doc={
            "chart_js_array":chartJsArray
        }

        db.recordpaper.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("/login"))


@app.route('/ADMINISTER/recordpaper_save/<number>', methods=['POST'])
def recordpaper_save(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if payload['admin'] == 'yes':
        html = request.form["rec_html"]
        print(html)

        doc={
            "record_HTML":html
        }

        db.recordpaper.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("/login"))


@app.route('/ADMINISTER/rec_remove/<number>', methods=['POST'])
def rec_remove(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print(number)
    if payload['admin'] == 'yes':
        doc={
            "record_file_real":""
            #나중에는 실제 path도 지워버려야
        }
        print(doc)
        db.mentor.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("/login"))


@app.route('/ADMINISTER/idcard_remove/<number>', methods=['POST'])
def idcard_remove(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print(number)
    if payload['admin'] == 'yes':
        doc={
            "idcard_file_real":""
            #나중에는 실제 path도 지워버려야
        }
        print(doc)
        db.mentor.update_one({'number': int(number)}, {'$set': doc})
        return jsonify({'result': 'success'})

    else:
        return redirect(url_for("/login"))


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

        return render_template('ADMIN_mentor_yield.html', mynickname=mynickname, login_time=login_time,mentor_info=mentor_info, mentorinfo_info=mentorinfo_info, recordpaper=recordpaper, resume=resume)
    else:
        return redirect(url_for("/login"))


@app.route('/ADMINISTER/carousel')
def ADMIN_carousel():
    if payload['admin'] == 'yes':
        return render_template('ADMIN_carousel.html')
    else:
        return redirect(url_for("/login"))


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


@app.route('/recordpaper_post')
def recordpaper_post():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    mentor_info = db.mentor.find_one({"number": payload["number"]})
    recordpaper_info = db.recordpaper.find_one({"number": payload["number"]})
    return render_template('recordpaper_post.html', mentor_info=mentor_info,recordpaper_info=recordpaper_info)


@app.route('/recordpaper_post_rec/<number>', methods=['GET'])
def recordpaper_post_chart(number):
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    if int(number) == int(payload["number"]):
        print('correct')
        recordpaper_find = db.recordpaper.find_one({"number": int(number)})
        print(recordpaper_find['chart_js_array'])
        return jsonify({'result': 'success', 'chartJsArray':recordpaper_find['chart_js_array'], 'record_HTML':recordpaper_find['record_HTML']})


@app.route('/resume_post')
def resume_post():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    mentor_info = db.mentor.find_one({"phone": payload["id"]})
    return render_template('resume_post.html', mentor_info=mentor_info)


@app.route('/menti_mypage_mydata')
def menti_mypage_mydata():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    menti_info = db.menti.find_one({"phone": payload["id"]}) or db.menti.find_one({"email": payload["id"]})
    return render_template('menti_mypage_mydata.html', menti_info=menti_info)


@app.route('/menti_mypage_mystory')
def menti_mypage_mystory():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    menti_info = db.menti.find_one({"phone": payload["id"]}) or db.menti.find_one({"email": payload["id"]})
    return render_template('menti_mypage_mystory.html', menti_info=menti_info)


@app.route('/menti_mypage_info')
def menti_mypage_info():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    menti_info = db.menti.find_one({"phone": payload["id"]}) or db.menti.find_one({"email": payload["id"]})
    return render_template('menti_mypage_info.html', menti_info=menti_info)


@app.route('/mentor_mypage_mydata')
def mentor_mypage_mydata():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    mentor_info = db.mentor.find_one({"phone": payload["id"]}) or db.mentor.find_one({"email": payload["id"]})
    return render_template('mentor_mypage_mydata.html', mentor_info=mentor_info)


@app.route('/mentor_mypage_mystory')
def mentor_mypage_mystory():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    mentor_info = db.mentor.find_one({"phone": payload["id"]}) or db.mentor.find_one({"email": payload["id"]})
    return render_template('mentor_mypage_mystory.html', mentor_info=mentor_info)


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
        my_alert = db.alert.find({'to_status': status, 'to_number': payload["number"]})

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
        my_alert = db.alert.find({'to_status': status, 'to_number': payload["number"]})

        return render_template('mentor_mypage_profit.html', mentor_info=mentor_info,me_info=me_info, token_receive=token_receive,action_mentor=action_mentor_array,nonaction_mentor=nonaction_mentor_array, my_alert=my_alert, status=status)
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
        my_alert = db.alert.find({'to_status': status, 'to_number': payload["number"]})

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
        my_alert = db.alert.find({'to_status': status, 'to_number': payload["number"]})

        return render_template('mentor_mypage_communication.html', mentor_info=mentor_info, me_info=me_info,
                               token_receive=token_receive, action_mentor=action_mentor_array,
                               nonaction_mentor=nonaction_mentor_array, my_alert=my_alert, status=status)
    else:
        return redirect(url_for("index"))


@app.route('/mentor_mypage_info/<nickname>')
def mentor_mypage_info(nickname):
    token_receive = request.cookies.get('mytoken')
    try :
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
        my_alert = db.alert.find({'to_status': status, 'to_number': payload["number"]})

        return render_template('mentor_mypage_info.html', mentor_info=mentor_info, mentorinfo_info=mentorinfo_info, me_info=me_info,action_mentor=action_mentor_array,nonaction_mentor=nonaction_mentor_array,status=status,my_alert=my_alert,token_receive=token_receive)
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
    filename_array = db.mentor.find_one({'number':my_num})['univAccepted_file']
    file_path_array = db.mentor.find_one({'number':my_num})['univAccepted_file_real']
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
    db.mentor.update_one({'number':my_num }, {'$set': doc})
    return jsonify({'result': 'success'})


@app.route('/mentor_mypage_info_email', methods=['POST'])
def mentor_mypage_info_email():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    email = request.form['email']
    my_number = payload['number']
    doc={
        'email':email
    }
    db.mentor.update_one({'number':my_number}, {'$set': doc})
    return jsonify({'result': 'success'})


@app.route('/mentor_mypage_password', methods=['POST'])
def mentor_mypage_password():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    password_receive = request.form['password_give']
    password = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc={
        'password':password
    }
    db.mentor.update_one({'number':payload['number']}, {'$set': doc})
    return jsonify({'result': 'success'})


@app.route('/user_mentor/<nickname>')
def user_mentor(nickname):
    token_receive = request.cookies.get('mytoken')
    mentor_info = db.mentor.find_one({"nickname": nickname})
    mentor_num = mentor_info['number']
    mentorinfo_info = db.mentor_info.find_one({"number": mentor_num})
    mentor_recordpaper = db.recordpaper.find_one({"number": mentor_num})
    following = db.followed.find_one({"number": mentor_num})
    mentor_follower = following['follower']
    print(mentor_follower)
    user_mentor_chart = db.recordpaper.find_one({'number':mentor_num})['chart_js_array']

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

        if [status,int(me_info['number'])] in mentor_follower:
            followed = 'True'
        else:
            followed = 'False'

        #admin
        if payload['admin']:
            admin = 'True'
        else:
            admin = 'False'

        #follow
        me_following = db.following.find_one({"follower_status": status, "follower_number":int(me_info['number'])})
        nonaction_mentor = me_following['nonaction_mentor']
        print(nonaction_mentor)
        nonaction_mentor_array=[]
        for number in nonaction_mentor:
            info = db.mentor.find_one({"number": int(number)},{'_id':False,'nickname':True, 'profile_pic_real':True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number':int(number)})['mentor_univ'][0]
            info.update({'univ':univ})
            print('infoRenewal:',info)
            nonaction_mentor_array.append(info)
        print(nonaction_mentor_array)
        action_mentor = me_following['action_mentor']
        print(action_mentor)
        action_mentor_array = []
        for number in action_mentor:
            info2 = db.mentor.find_one({"number": int(number)}, {'_id': False, 'nickname': True, 'profile_pic_real': True})
            # 대학정보도 추가로 가져와야 함
            univ = db.mentor_info.find_one({'number':int(number)})['mentor_univ'][0]
            info2.update({'univ':univ})
            print('infoRenewal:', info2)
            action_mentor_array.append(info2)
        print(action_mentor_array)

        #alert
        my_alert = db.alert.find({'to_status':status, 'to_number':payload["number"]})

        return render_template('user_mentor.html', mentor_info=mentor_info, mentorinfo_info=mentorinfo_info,status=status,chart_array=user_mentor_chart,myFeed=myFeed, record=mentor_recordpaper, me_info=me_info, follower=mentor_follower,followed=followed, token_receive=token_receive, action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array, my_alert=my_alert, admin=admin)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        print('no token')
        myFeed = False
        return render_template('user_mentor.html', mentor_info=mentor_info, mentorinfo_info=mentorinfo_info,chart_array=user_mentor_chart,myFeed=myFeed, record=mentor_recordpaper,me_info=None,follower=mentor_follower)


@app.route('/index')
def index():
    token_receive = request.cookies.get('mytoken')
    print(token_receive)
    mentor_out = db.mentor.count_documents({})
    try:
        print('has token')
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        me_mentor = db.mentor.find_one({"nickname": payload["nickname"]})
        me_menti = db.menti.find_one({"nickname": payload["nickname"]})
        if me_menti is not None:
            me_info = me_menti
            status = 'menti'
        if me_mentor is not None:
            me_info = me_mentor
            status = 'mentor'

        # make initial list of searchbox mentor list by follower count, limit 30
        mentor_all = db.followed.find()
        print('mentorALl', mentor_all)
        initial_mentor_dic = {}
        for mentor in mentor_all:
            if db.mentor.find_one({'number':mentor['number']})['univAttending_file_real'] == '':
                follower_cnt = len(mentor['follower'])
                initial_mentor_dic[mentor['number']]=follower_cnt
        sorted_list = sorted(initial_mentor_dic.items(), key=lambda x:x[1], reverse=True)[:30]
        initial_search_list = []
        for item in sorted_list:
            mentor_num = int(item[0])
            db_mentor = db.mentor.find_one({'number':mentor_num},{'_id':False, 'nickname':True, 'profile_pic_real':True})
            db_mentorinfo = db.mentor_info.find_one({'number':mentor_num},{'_id':False, 'tags':True, 'mentor_univ':True, 'mentor_major':True, 'mentor_type':True, 'mentor_number':True})
            if db.recordpaper.find_one({'number':mentor_num})['chart_js_array']:
                record_count = 1
            else:
                record_count = 0
            cnt_mentor_data = record_count + db.resume.find({'number':mentor_num}).count() + db.story.find({'number':mentor_num}).count()

            arr =[
                db_mentor['profile_pic_real'],
                item[1],
                cnt_mentor_data,
                db_mentorinfo['tags'],
                db_mentor['nickname'],
                db_mentorinfo['mentor_univ'][0],
                db_mentorinfo['mentor_major'][0],
                db_mentorinfo['mentor_type'][0],
                db_mentorinfo['mentor_number'][0],
            ]
            initial_search_list.append(arr)

        # make new-face mentor list by recent 20
        sorted_new_mentor = list(db.mentor.find({'univAttending_file_real':''}).sort('number',-1))[:20]
        new_mentor_list=[]
        for mentor in sorted_new_mentor:
            mentor_num2 = int(mentor['number'])
            db_mentor2 = db.mentor.find_one({'number': mentor_num2},{'_id': False, 'nickname': True, 'profile_pic_real': True})
            db_mentorinfo2 = db.mentor_info.find_one({'number': mentor_num2},{'_id': False, 'tags': True, 'mentor_univ': True,'mentor_major': True, 'mentor_type': True, 'mentor_number': True})
            if db.recordpaper.find_one({'number': mentor_num2})['chart_js_array']:
                record_count2 = 1
            else:
                record_count2 = 0
            cnt_mentor_data2 = record_count2 + db.resume.find({'number': mentor_num2}).count() + db.story.find({'number': mentor_num2}).count()

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
        sorted_new_community = list(db.community.find().sort('_id',-1))[:30]
        print(sorted_new_community)
        hot_community=[]
        for community in sorted_new_community:
            mentor_num3 = int(community['number'])
            db_mentor3 = db.mentor.find_one({'number': mentor_num3},{'_id': False, 'nickname': True, 'profile_pic_real': True})
            db_mentorinfo3 = db.mentor_info.find_one({'number': mentor_num3},{'_id': False, 'mentor_univ': True,'mentor_major': True, 'mentor_number': True})
            community_title = community['title']
            community_desc = community['desc']
            community_time = community['time']
            community_like = len(db.like.find_one({'number': mentor_num3,'category':'community','time':community_time})['who'])

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
        #alert
        my_alert = db.alert.find({'to_status': status, 'to_number': payload["number"]})

        return render_template('index.html',initial_search_list=initial_search_list,new_mentor_list=new_mentor_list,hot_community=hot_community, mentor_out=mentor_out, me_info=me_info, status=status, token_receive=token_receive,action_mentor=action_mentor_array, nonaction_mentor=nonaction_mentor_array, my_alert=my_alert)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        print('no token')
        return render_template('index.html',initial_search_list=initial_search_list,new_mentor_list=new_mentor_list,hot_community=hot_community, mentor_out=mentor_out)


@app.route('/get_mentor', methods=['GET'])
def get_mentor():
    selectedUnivArray = request.args.get('selectedUnivArray').split(',')
    selectedMajorArray = request.args.get('selectedMajorArray').split(',')
    selectedTypeArray = request.args.get('selectedTypeArray').split(',')
    check = request.args.get('check')
    print(selectedUnivArray)
    print(selectedMajorArray)
    print(check)
    print(selectedTypeArray)

    mentor_all = list(db.mentor_info.find({},{'_id':False,'number':True,'mentor_univ':True, 'mentor_major':True,'mentor_type':True}))
    # make filtered array through univ
    univ_filtered = []
    if selectedUnivArray == []:
        univ_filtered = db.mentor_info.find()['number']
        # if there is no selected univ, there is no filtering
    else:
        for mentor in mentor_all:
            if (set(mentor['mentor_univ']) & set(selectedUnivArray)):
                #compare each mentor`s array and selected univ, insert if sth matched
                univ_filtered.append(mentor['number'])
    print('univ_filtered', univ_filtered)
    # array filtered by univ

    # make filtered array through major, !consider case of 'checked'
    univ_major_filtered =[]
    if ('전체 학과' in selectedMajorArray) or selectedMajorArray == ['']:
        univ_major_filtered = univ_filtered
    else:
        if check == 'on':
            # similar major including checked, in order to makr selected array transformed to middleselector
            for major in selectedMajorArray:
                middle = db.univ_list.find_one({'학과명': major})['중계열']
                selectedMajorArray.remove(major)
                selectedMajorArray.insert(0, middle)
            print('checked-new', selectedMajorArray)

            for mentor2 in univ_filtered:
                mentor_major_array = db.mentor_info.find_one({'number':int(mentor2)})['mentor_major']
                for major2 in mentor_major_array:
                    if db.univ_list.find_one({'학과명':major2}) is not None:
                        middle2 = db.univ_list.find_one({'학과명':major2})['중계열']
                        mentor_major_array.remove(major2)
                        mentor_major_array.insert(0,middle2)
                        # transformed each mentor_major_array into middle selector
                if set(mentor_major_array) & set(selectedMajorArray):
                    univ_major_filtered.append(mentor2)
            print('univ_major_filtered', univ_major_filtered)
            # array filterd by univ + (checked)major
        else:
            for mentor3 in univ_filtered:
                mentor_major_array = db.mentor_info.find_one({'number':int(mentor3)})['mentor_major']
                if set(mentor_major_array) & set(selectedMajorArray):
                    univ_major_filtered.append(mentor3)
            print('univ_major_filtered', univ_major_filtered)
            # array filterd by univ + (un-checked)major

    # make filtered array through major
    univ_major_type_filtered=[]
    if selectedTypeArray == ['']:
        univ_major_type_filtered = univ_major_filtered
    else:
        for mentor4 in univ_major_filtered:
            mentor_type_array = db.mentor_info.find_one({'number':int(mentor4)})['mentor_type']
            for type in mentor_type_array:
                if db.univ_type.find_one({'전형명':type}) is not None:
                    type_cat = db.univ_type.find_one({'전형명':type})['전형유형']
                    mentor_type_array.remove(type)
                    mentor_type_array.insert(0,type_cat)
                    # transformed each mentor_type_array into higher selector
            if set(mentor_type_array) & set(selectedTypeArray):
                # compare each mentor`s type_cat array and selected types, insert if sth matched
                univ_major_type_filtered.append(mentor['number'])
        print('univ_filtered', univ_major_type_filtered)

    #make card
    search_result=[]
    for mentor_num in univ_major_type_filtered:
        print('number: ',mentor_num)
        db_mentor = db.mentor.find_one({'number': mentor_num}, {'_id': False, 'nickname': True, 'profile_pic_real': True})
        db_mentorinfo = db.mentor_info.find_one({'number': mentor_num},{'_id': False, 'tags': True, 'mentor_univ': True, 'mentor_major': True,'mentor_type': True, 'mentor_number': True})
        if db.recordpaper.find_one({'number': mentor_num})['chart_js_array']:
            record_count = 1
        else:
            record_count = 0
        cnt_mentor_data = record_count + db.resume.find({'number': mentor_num}).count() + db.story.find({'number': mentor_num}).count()

        arr = [
            db_mentor['profile_pic_real'],
            len(db.followed.find_one({'number':mentor_num})['follower']),
            cnt_mentor_data,
            db_mentorinfo['tags'],
            db_mentor['nickname'],
            db_mentorinfo['mentor_univ'][0],
            db_mentorinfo['mentor_major'][0],
            db_mentorinfo['mentor_type'][0],
            db_mentorinfo['mentor_number'][0],
        ]
        search_result.append(arr)

    return jsonify({'result': 'success', 'filter_result':search_result})


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

    find_menti = db.menti.find_one({'email': id_receive, 'password': pw_hash}) or db.menti.find_one({'phone': id_receive, 'password': pw_hash})
    find_mentor = db.mentor.find_one({'phone': id_receive, 'password': pw_hash})

    if find_menti or find_mentor is not None:
        print('ip : ',request.remote_addr)
        if find_menti is not None:
            nickname_find = find_menti['nickname']
            payload = {
                'admin': 'no',
                'number': int(find_menti['number']),
                'id':id_receive,
                'nickname': nickname_find,
                'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
            }
            db.menti.update_one({'email': payload['id']}, {'$set': doc}) and db.menti.update_one({'phone': payload['id']}, {'$set': doc})
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
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

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

    return jsonify({'result': 'success', 'num':num})


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
        number = (db.mentor.count())+(db.menti.count()) + 1

        menti_doc = {
            "number": number,
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
            "profile_pic_real": f"profile_pics/profile_placeholder_{number%3}.png",
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
        number = (db.mentor.count())+(db.menti.count()) + 1
        mentor_doc = {
            "number": number,
            "name":"",
            "email": email_receive,
            "phone": phone_receive,
            "password": password_hash,
            "birth": "",
            "nickname": nickname_receive,
            "profile_pic": "",
            "profile_pic_real": f"profile_pics/profile_placeholder_{number%3}.png",
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
            "bank":"",
            "account":""
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
            "tags":tags,
            "grade":"",
            "location":"",
            "mentorinfo":["","","","",""],
            "school_type":"",
            "activity":[["","",""],["","",""],["","",""]],
            "sns":[["","",""],["","",""],["","",""],["","",""],["","",""]],
            "mentor_univ": [],
            "mentor_major": [],
            "mentor_type": [],
            "mentor_number": [],
            "mentor_verified":[]
        }
        db.mentor_info.insert_one(new_doc)

        record_doc = {
            "number": number,
            "title":"",
            "visit":0,
            "buy": 0,
            "profit":0,
            "release":"hide",
            "chart_js_array":[],
            "record_HTML":""
        }
        db.recordpaper.insert_one(record_doc)

        following_doc = {
            "follower_status": v,
            "follower_number":number,
            "action_mentor":[],
            "nonaction_mentor":[],
        }
        db.following.insert_one(following_doc)

        followed_doc = {
            "number": number,
            "follower": [],
            "recent_action": "",
            "recent_action_time": ""
        }
        db.followed.insert_one(followed_doc)

    return jsonify({'result': 'success', 'msg': '회원가입을 완료했습니다.','number':number})


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
        return jsonify({'result':'fail'})

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
    print(password_receive, num_receive,time_receive)
    # find_menti = db.menti.find_one({'resetNum': num_receive})
    # find_mentor = db.mentor.find_one({'resetNum': num_receive})
    hash_pw = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc={
        'password': hash_pw,
        'resetNum': None,
        'numTime':None
    }
    find_menti = db.menti.find_one({'resetNum': num_receive})
    find_mentor = db.mentor.find_one({'resetNum': num_receive})
    print(((int(time_receive) / 1000) - 3600), find_menti['numTime'])

    if find_mentor is not None:
        if ((int(time_receive) / 1000) - 3600) < int(find_menti['numTime']):
            db.menti.update_one({'resetNum': num_receive}, {'$set': doc})
            return jsonify({'result': 'success', 'msg':'비밀번호가 변경되었습니다! 새 비밀번호로 로그인해주세요'})
        else:
            return jsonify({'result': 'success', 'msg':'유효시간이 만료되었습니다. 다시 시도해 주세요'})
    elif find_menti is not None:
        if ((int(time_receive) / 1000) - 3600) < int(find_menti['numTime']):
            db.mentor.update_one({'resetNum': num_receive}, {'$set': doc})
            return jsonify({'result': 'success', 'msg':'비밀번호가 변경되었습니다! 새 비밀번호로 로그인해주세요'})
        else:
            return jsonify({'result': 'success', 'msg':'유효시간이 만료되었습니다. 다시 시도해 주세요'})
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
        name_receive = db.mentor.find_one({'number':int(payload['number']) })['name']
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


@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        my_username = payload["username"]
        username_receive = request.args.get("username_give")
        if username_receive == "":
            posts = list(db.posts.find({}).sort("date", -1).limit(20))
        else:
            posts = list(db.posts.find({"username": username_receive}).sort("date", -1).limit(20))

        for post in posts:
            post["_username"] = str(post["_username"])

            post["count_heart"] = db.likes.count_documents({"post_username": post["_username"], "type": "heart"})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_username": post["_username"], "type": "heart", "username": my_username}))

        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


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
        mentorinfoArray = [mentorinfo_1_receive, mentorinfo_2_receive, mentorinfo_3_receive, mentorinfo_4_receive,mentorinfo_5_receive, mentorinfo_6_receive]
        doc = {
            "mentorinfo": mentorinfoArray,
            "location": location_receive,
            "school_type": school_type_receive,
            "grade": grade_receive
        }

        find_mentor = db.mentor.find_one({'phone': payload['id']})
        mentor_num = int(find_mentor['number'])
        db.mentor_info.update_one({'number': mentor_num}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.', 'mentorinfoArray':mentorinfoArray})
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
            "activity": [[activity_category_1_receive, activity_num_1_receive, activity_unit_1_receive], [activity_category_2_receive, activity_num_2_receive, activity_unit_2_receive], [activity_category_3_receive, activity_num_3_receive, activity_unit_3_receive]]
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
             "sns": [[sns_category_1_receive, sns_id_1_receive, sns_link_1_receive], [sns_category_2_receive, sns_id_2_receive, sns_link_2_receive], [sns_category_3_receive, sns_id_3_receive, sns_link_3_receive], [sns_category_4_receive, sns_id_4_receive, sns_link_4_receive], [sns_category_5_receive, sns_id_5_receive, sns_link_5_receive]]
        }
        print(doc)
        find_mentor = db.mentor.find_one({'phone': payload['id']})
        mentor_num = int(find_mentor['number'])
        db.mentor_info.update_one({'number': mentor_num}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/rec_desc_save', methods=['POST'])
def rec_desc_save():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        record_title_receive = request.form["record_title_give"]
        doc = {
            "record_title": record_title_receive
        }
        db.recordpaper.update_one({'id': payload['id']}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/rec_detail_save', methods=['POST'])
def rec_detail_save():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        record_desc_receive = request.form["record_desc_give"]
        doc = {
            "record_desc": record_desc_receive
        }
        db.recordpaper.update_one({'phone': payload['phone']}, {'$set': doc})
        db.recordpaper.update_one({'id': payload['id']}, {'$set': doc})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/rec_file_save', methods=['POST'])
def rec_file_save():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        doc = {
            "record_file": "",
            "record_file_real": "record_files/record_file_placeholder.png"
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            file_path = f"record_files/{filename}"
            file.save("./static/" + file_path)
            doc["record_file"] = filename
            doc["record_file_real"] = file_path
        db.mentor.update_one({'id': payload['id']}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/rec_price_save', methods=['POST'])
def rec_price_save():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        record_price_receive = request.form["record_price_give"]
        doc = {
            "record_price": record_price_receive
        }
        db.recordpaper.update_one({'id': payload['id']}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


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
        print(univArray, majorArray, typeArray, schoolNumArray,verifiedArray)

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
        return jsonify({"result": "success", "mentor_univ": mentor_univ, "mentor_major": mentor_major, "mentor_type": mentor_type, "mentor_number": mentor_number, "mentor_verified":mentor_verified})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/mentor_univ_represent', methods=['POST'])
def mentor_univ_represent():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        index_receive = request.form["index_give"]
        find_mentor = db.mentor_info.find_one({'id': payload['id']})
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

        db.mentor_info.update_one({'id': payload['id']}, {'$set': doc})
        return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/mentor_univ_remove', methods=['POST'])
def mentor_univ_remove():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        index_receive = request.form["index_give"]
        print(index_receive)
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
            "number":mentor_num,
            "category":"community",
            "time":community_time_receive,
            "who":[]
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
            follower_follwing = db.following.find_one({"follower_status": follower[0], "follower_number":int(follower[1])})
            action_array = follower_follwing['action_mentor']
            nonaction_array = follower_follwing['nonaction_mentor']
            if mentor_num in nonaction_array:
                nonaction_array.remove(mentor_num)
                action_array.append(mentor_num)
                doc={
                    "nonaction_mentor":nonaction_array,
                    "action_mentor":action_array
                }
                db.following.update_one({'follower_number': int(follower[1]), 'follower_status':follower[0]}, {'$set': doc})

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

        db.community.delete_one({"number": mentor_num, 'time':time_receive})
        db.like.delete_one({"number": mentor_num, 'time':time_receive})
        db.reply.delete_one({"number": mentor_num, 'time':time_receive})

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
        print([status,my_number])

        community_like = db.like.find_one({'number': int(number_receive), 'category':'community', 'time':time_receive})
        print(community_like)
        who_array = community_like['who']

        if action_receive == 'like':
            print('like')
            who_array.append([status, my_number])
            print(who_array)
            db.like.update_one({'number': int(number_receive),'category':'community', 'time':time_receive }, {'$set': {'who':who_array}})

            title = db.community.find_one({'number': int(number_receive), 'time':time_receive })['title']
            doc={
                'to_status' : 'mentor',
                'to_number' : int(number_receive),
                'category' : '커뮤니티를',
                'which_data' : title,
                'action': '좋아합니다',
                'when':'',
                'from_nickname' : payload['nickname'],
                'from_image' : me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)

            return jsonify({"result": "success"})

        elif action_receive == 'unlike':
            print('unlike')
            who_array.remove([status, my_number])
            print(who_array)
            db.like.update_one({'number': int(number_receive), 'category': 'community', 'time': time_receive}, {'$set': {'who': who_array}})
            return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/community_get', methods=["GET"])
def community_get():
    number_receive = int(request.args.get('number_give'))

    mentor_community = list(db.community.find({'number': number_receive}))
    # print(mentor_community)
    community_array=[]
    for com in mentor_community:
        community_array.append([com['title'], com['notice'], com['desc'], com['time']])

    mentor_notice = list(db.community.find({'number': number_receive, 'notice':'on'}))
    # print(mentor_notice)
    notice_array = []
    for notice in mentor_notice:
        notice_array.append([notice['title'], notice['desc'], notice['time']])

    community_like = list(db.like.find({'number': number_receive, 'category':'community'}))
    # print(community_like)
    community_like_array = []
    for like in community_like:
        community_like_array.append([ like['time'], like['who'] ])

    community_reply = list(db.reply.find({'number': number_receive, 'category': 'community'}))
    # print(community_reply)
    community_reply_array = []
    for reply in community_reply:
        community_reply_array.append([reply['time'], reply['reply']])

    return jsonify({"result": "success","community":community_array, "notice":notice_array, "community_like":community_like_array, "community_reply":community_reply_array})


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
        print([status,my_number])

        row = db.reply.find_one({'number': mentor_num, 'time':which_community})
        reply_array = row['reply']

        my_reply = [[status,my_number],reply_text,reply_time,[]]
        reply_array.append(my_reply)
        print(reply_array)

        db.reply.update_one({'number': mentor_num, 'category': 'community', 'time': which_community},{'$set': {'reply': reply_array}})

        if (status != 'mentor') or (int(payload['number']) != mentor_num):
            print('alert insert')
            doc = {
                'to_status': 'mentor',
                'to_number': mentor_num,
                'category': '커뮤니티에',
                'which_data': reply_text,
                'action': '댓글을 작성하였습니다',
                'when': reply_time,
                'from_nickname' : payload['nickname'],
                'from_image' : me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)
        return jsonify({"result": "success", "reply_array":reply_array})

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
        print([status,my_number])

        row = db.reply.find_one({'number': mentor_num, 'time':which_community})
        reply_array = row['reply']

        my_reply = [[status, my_number], re_reply_text, re_reply_time]
        for miniArray in reply_array:
            if miniArray[2] == which_mother:
                miniArray[3].append(my_reply)
                reply_target = miniArray[0]
        print('reply_array:',reply_array)
        print(reply_target)
        # reply_array.append(my_reply)
        # print(reply_array)

        db.reply.update_one({'number': mentor_num, 'category': 'community', 'time': which_community},{'$set': {'reply': reply_array}})

        doc = {
            'to_status': reply_target[0],
            'to_number': int(reply_target[1]),
            'category': '댓글에',
            'which_data': re_reply_text,
            'action': '답글을 작성하였습니다',
            'when': re_reply_time,
            'from_nickname' : payload['nickname'],
            'from_image' : me_info['profile_pic_real']
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

    pic_real_array=[]
    for status, number in zip(status_array, num_array):
        if status == 'mentor':
            find_person = db.mentor.find_one({'number': int(number)})
            class_name = 'mentor,'+number
        else:
            find_person = db.menti.find_one({'number': int(number)})
            class_name = 'menti,'+number

        pic_real_array.append([class_name,find_person['profile_pic_real'],find_person['nickname']])

    print(pic_real_array)

    return jsonify({"result": "success","picArray":pic_real_array})


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
    db.reply.update_one({'number': mentor_num, 'category': 'community', 'time': which_community},{'$set': {'reply': reply_array}})

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

    db.reply.update_one({'number': mentor_num, 'category': 'community', 'time': which_community},{'$set': {'reply': reply_array}})

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

        me_in_following = db.following.find_one({"follower_status": status, "follower_number":int(me_info['number'])})
        mentor_in_followed = db.followed.find_one({'number': mentor_num})

        action_mentor_array = me_in_following['action_mentor']
        nonaction_mentor_array = me_in_following['nonaction_mentor']
        mentor_followed_array = mentor_in_followed['follower']

        if action == 'follow':
            print('follow')
            action_mentor_array.append(mentor_num)
            mentor_followed_array.append([status,int(me_info['number'])])

            db.following.update_one({'follower_status': status, 'follower_number':int(me_info['number'])},{'$set': {'action_mentor': action_mentor_array}})
            db.followed.update_one({'number': mentor_num},{'$set': {'follower': mentor_followed_array}})

            doc = {
                'to_status': 'mentor',
                'to_number': mentor_num,
                'category': '계정을',
                'which_data': '내',
                'action': '팔로우하였습니다',
                'when': '',
                'from_nickname' : payload['nickname'],
                'from_image' : me_info['profile_pic_real']
            }
            db.alert.insert_one(doc)
            return jsonify({"result": "success"})

        else:
            if mentor_num in action_mentor_array:
                action_mentor_array.remove(mentor_num)
            else:
                nonaction_mentor_array.remove(mentor_num)
            mentor_followed_array.remove([status, int(me_info['number'])])

            db.following.update_one({'follower_status': status, 'follower_number':int(me_info['number'])},{'$set': {'action_mentor': action_mentor_array,'nonaction_mentor':nonaction_mentor_array}})
            db.followed.update_one({'number': mentor_num}, {'$set': {'follower': mentor_followed_array}})
            return jsonify({"result": "success"})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('/login'))


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

        find_mentor = db.mentor.find_one({'nickname':nickname})
        mentor_num = int(find_mentor['number'])

        me_in_following = db.following.find_one({"follower_status": status, "follower_number":int(me_info['number'])})
        action_mentor_array = me_in_following['action_mentor']
        nonaction_mentor_array = me_in_following['nonaction_mentor']

        action_mentor_array.remove(mentor_num)
        nonaction_mentor_array.insert(0,mentor_num)

        db.following.update_one({'follower_status': status, 'follower_number':int(me_info['number'])}, {'$set': {'action_mentor': action_mentor_array, 'nonaction_mentor': nonaction_mentor_array}})

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
        return redirect(url_for('/login'))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
