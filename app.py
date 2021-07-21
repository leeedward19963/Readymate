from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import random
import math
import time

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('localhost', 27017)
# client = MongoClient('15.164.234.234', 27017, username="readymate", password="readymate1!")
db = client.RM_FLASK

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
    mentor_info = db.mentor.find_one({"phone": payload["id"]})
    recordpaper_info = db.recordpaper.find_one({"phone": payload["id"]})
    return render_template('recordpaper_post.html', mentor_info=mentor_info, recordpaper_info=recordpaper_info)


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


@app.route('/mentor_mypage_dashboard')
def mentor_mypage_dashboard():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    mentor_info = db.mentor.find_one({"phone": payload["id"]}) or db.mentor.find_one({"email": payload["id"]})
    return render_template('mentor_mypage_dashboard.html', mentor_info=mentor_info)


@app.route('/mentor_mypage_profit')
def mentor_mypage_profit():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    mentor_info = db.mentor.find_one({"phone": payload["id"]}) or db.mentor.find_one({"email": payload["id"]})
    return render_template('mentor_mypage_profit.html', mentor_info=mentor_info)


@app.route('/mentor_mypage_account')
def menti_mypage_account():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    mentor_info = db.mentor.find_one({"phone": payload["id"]}) or db.mentor.find_one({"email": payload["id"]})
    return render_template('mentor_mypage_account.html', mentor_info=mentor_info)


@app.route('/mentor_mypage_info')
def mentor_mypage_info():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    mentor_info = db.mentor.find_one({"phone": payload["id"]}) or db.mentor.find_one({"email": payload["id"]})
    mentorinfo_info = db.mentor_info.find_one({"id": payload["id"]})
    return render_template('mentor_mypage_info.html', mentor_info=mentor_info, mentorinfo_info=mentorinfo_info)


@app.route('/user_mentor')
def user_mentor():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    mentor_info = db.mentor.find_one({"phone": payload["id"]}) or db.mentor.find_one({"email": payload["id"]})
    mentorinfo_info = db.mentor_info.find_one({"id": payload["id"]})
    return render_template('user_mentor.html', mentor_info=mentor_info, mentorinfo_info=mentorinfo_info)


@app.route('/index')
def index():
    token_receive = request.cookies.get('mytoken')
    mentor_out = db.mentor.count()
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        menti_info = db.menti.find_one({"phone": payload["id"]}) or db.menti.find_one({"email": payload["id"]})
        mentor_info = db.mentor.find_one({"phone": payload["id"]}) or db.mentor.find_one({"email": payload["id"]})
        if mentor_info is not None:
            status = 'mentor'
            return render_template('index.html', mentor_out=mentor_out, mentor_info=mentor_info, menti_info=menti_info, status=status, token_receive=token_receive)
        else:
            status = 'menti'
            return render_template('index.html', mentor_out=mentor_out, mentor_info=mentor_info, menti_info=menti_info, status=status, token_receive=token_receive)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('index.html', mentor_out=mentor_out)


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
    # menti_email_receive = db.menti.find_one({'email': id_receive})
    # mentor_email_receive = db.mentor.find_one({'email': id_receive})
    # menti_phone_receive = db.menti.find_one({'phone': id_receive})
    # mentor_phone_receive = db.mentor.find_one({'phone': id_receive})
    find_menti = db.menti.find_one({'email': id_receive, 'password': pw_hash}) or db.menti.find_one({'phone': id_receive, 'password': pw_hash})
    find_mentor = db.mentor.find_one({'phone': id_receive, 'password': pw_hash})

    if find_menti or find_mentor is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 2)  # 로그인 2시간 유지
            }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256') #.decode('utf-8')있었

        if find_mentor is None:
            db.menti.update_one({'email': payload['id']}, {'$set': doc}) and db.menti.update_one({'phone': payload['id']}, {'$set': doc})
        else:
            db.mentor.update_one({'phone': payload['id']}, {'$set': doc})
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
        number = (db.menti.count()) + 1

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
            "profile_pic_real": "profile_pics/profile_placeholder.png",
            "v": v,
            "register_date": register_date_receive,
            "recent_login": ""
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{number}.{extension}"
            file.save("./static/" + file_path)
            menti_doc["profile_pic"] = filename
            menti_doc["profile_pic_real"] = file_path
        db.menti.insert_one(menti_doc)

    else:
        number = (db.mentor.count()) + 1
        mentor_doc = {
            "number": number,
            "email": email_receive,
            "phone": phone_receive,
            "password": password_hash,
            "nickname": nickname_receive,
            "profile_pic": "",
            "profile_pic_real": "profile_pics/profile_placeholder.png",
            "univAccepted_file": "",
            "univAccepted_file_real": "univAccepted_files/univAccepted_placeholder.png",
            "univAttending_file": "",
            "univAttending_file_real": "univAttending_files/univAttending_placeholder.png",
            "v": v,
            "register_date": register_date_receive,
            "recent_login": ""
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{number}.{extension}"
            file.save("./static/" + file_path)
            mentor_doc["profile_pic"] = filename
            mentor_doc["profile_pic_real"] = file_path

        if 'acceptedFile_give' in request.files:
            file = request.files["acceptedFile_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"univAccepted_files/{number}.{extension}"
            file.save("./static/" + file_path)
            mentor_doc["univAccepted_file"] = filename
            mentor_doc["univAccepted_file_real"] = file_path

        if 'attendingFile_give' in request.files:
            file = request.files["attendingFile_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"univAttending_files/{number}.{extension}"
            file.save("./static/" + file_path)
            mentor_doc["univAttending_file"] = filename
            mentor_doc["univAccepted_file_real"] = file_path
        db.mentor.insert_one(mentor_doc)

        tags = request.form["tags"]
        new_doc = {
            "number": number,
            "id":email_receive,
            "tags":tags,
            "mentor_univ_1": "",
            "mentor_univ_2": "",
            "mentor_univ_3": "",
            "mentor_univ_4": "",
            "mentor_univ_5": "",
            "mentor_univ_6": "",
            "mentor_univ_7": "",
            "mentor_univ_8": "",
            "mentor_univ_9": "",
            "mentor_univ_10": "",
            "mentorinfo_1": "",
            "mentorinfo_2": "",
            "mentorinfo_3": "",
            "mentorinfo_4": "",
            "mentorinfo_5": "",
            "mentorinfo_6": "",
            "location": "",
            "univ_type": "",
            "grade": "",
            "rec_prize": "",
            "rec_page": "",
            "rec_hour": "",
            "activity_category_1": "",
            "activity_num_1": "",
            "activity_category_2": "",
            "activity_num_2": "",
            "activity_category_3": "",
            "activity_num_3": "",
            "activity_unit_1": "",
            "activity_unit_2": "",
            "activity_unit_3": "",
            "sns_category_1": "",
            "sns_id_1": "",
            "sns_category_2": "",
            "sns_id_2": "",
            "sns_category_3": "",
            "sns_id_3": "",
            "sns_category_4": "",
            "sns_id_4": "",
            "sns_category_5": "",
            "sns_id_5": ""
        }
        db.mentor_info.insert_one(new_doc)

        number = (db.recordpaper.count()) + 1
        record_doc = {
            "number": number,
            "id":email_receive
        }
        db.recordpaper.insert_one(record_doc)
    return jsonify({'result': 'success', 'msg': '회원가입을 완료했습니다.'})


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
        db.mentor.update_one({'email': payload['id']}, {'$set': doc}) and db.mentor.update_one({'phone': payload['id']}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index"))


@app.route('/tag_update', methods=['POST'])
def tag_update():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        tags = request.form["tags"]
        doc = {
            "tags": tags
        }
        db.mentor_info.update_one({'id': payload['id']}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("index"))


@app.route('/save_myaccount', methods=['POST'])
def save_myaccount():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        name_receive = request.form["name_give"]
        bank_receive = request.form["bank_give"]
        account_receive = request.form["account_give"]
        doc = {
            "name": name_receive,
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
        db.mentor.update_one({'email': payload['id']}, {'$set': doc}) and db.mentor.update_one({'phone': payload['id']}, {'$set': doc})
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
        univ_type_receive = request.form["univ_type_give"]
        grade_receive = request.form["grade_give"]
        doc = {
            "mentorinfo": [mentorinfo_1_receive, mentorinfo_2_receive, mentorinfo_3_receive, mentorinfo_4_receive,mentorinfo_5_receive, mentorinfo_6_receive],
            "location": location_receive,
            "univ_type": univ_type_receive,
            "grade": grade_receive
        }
        db.mentor_info.update_one({'id': payload['id']}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
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
        db.mentor_info.update_one({'id': payload['id']}, {'$set': doc})
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
        db.mentor_info.update_one({'id': payload['id']}, {'$set': doc})
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
        db.recordpaper.update_one({'id': payload['id']}, {'$set': doc})
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
        print(univArray, majorArray, typeArray, schoolNumArray)

        find_mentor = db.mentor_info.find_one({'id': payload['id']})
        mentor_univ = find_mentor['mentor_univ']
        mentor_major = find_mentor['mentor_major']
        mentor_number = find_mentor['mentor_number']
        mentor_type = find_mentor['mentor_type']
        print(mentor_univ, mentor_major, mentor_number, mentor_type)

        new_mu = mentor_univ + [univArray]
        new_mm = mentor_major + [majorArray]
        new_mn = mentor_number + [schoolNumArray]
        new_mt = mentor_type + [typeArray]

        print(new_mu, new_mm, new_mn, new_mt)

        doc = {
             "mentor_univ": new_mu,
            "mentor_major": new_mm,
            "mentor_type": new_mt,
            "mentor_number": new_mn
        }
        db.mentor_info.update_one({'id': payload['id']}, {'$set': doc})

        return jsonify({"result": "success", 'msg': '합격 대학이 업데이트되었습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/mentor_univ_get', methods=['GET'])
def mentor_univ_get():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        find_mentor = db.mentor_info.find_one({'id': payload['id']})
        mentor_univ = find_mentor['mentor_univ']
        mentor_major = find_mentor['mentor_major']
        mentor_type = find_mentor['mentor_type']
        mentor_number = find_mentor['mentor_number']
        return jsonify({"result": "success", "mentor_univ": mentor_univ, "mentor_major": mentor_major, "mentor_type": mentor_type, "mentor_number": mentor_number})
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
        find_mentor = db.mentor_info.find_one({'id': payload['id']})
        mentor_univ = find_mentor['mentor_univ']
        mentor_major = find_mentor['mentor_major']
        mentor_type = find_mentor['mentor_type']
        mentor_number = find_mentor['mentor_number']

        del mentor_univ[int(index_receive)]

        del mentor_major[int(index_receive)]

        del mentor_type[int(index_receive)]

        del mentor_number[int(index_receive)]

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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
