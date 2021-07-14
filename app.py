from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('15.164.234.234', 27017, username="readymate", password="readymate1!")
db = client.RM_FLASK


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        menti_info = db.menti.find_one({"number": payload["number"]})
        mentor_info = db.menti.find_one({"number": payload["number"]})
        mentorinfo_info = db.mentor_info.find_one({"number": payload["number"]})
        recordpaper_info = db.recordpaper.find_one({"number": payload["number"]})
        return render_template('user_mentor.html', menti_info=menti_info, mentor_info=mentor_info, mentorinfo_info=mentorinfo_info, recordpaper_info=recordpaper_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


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
    user_info = db.users.find_one({"phone": payload["phone"]})
    return render_template('recordpaper_post.html', user_info=user_info)


@app.route('/mentor_mypage_info')
def mentor_mypage_info():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"phone": payload["phone"]})
    return render_template('mentor_mypage_info.html', user_info=user_info)


@app.route('/index')
def index():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    menti_info = db.users.find_one({"phone": payload["phone"]})
    mentor_info = db.users.find_one({"phone": payload["phone"]})
    return render_template('index.html', menti_info=menti_info, mentor_info=mentor_info)


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
    if "email_receive" is None:
        phone_receive = request.form['id_give']
    else:
        email_receive = request.form['email_give']

    password_receive = request.form['password_give']
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result1 = db.menti.find_one({'phone': phone_receive, 'password': pw_hash} or {'email': email_receive, 'password': pw_hash})
    result2 = db.mentor.find_one({'phone': phone_receive, 'password': pw_hash} or {'email': email_receive, 'password': pw_hash})

    if result1 or result2 is not None:
        if email_receive is not None:
            payload = {
                'id': email_receive,
                'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
            }
        else:
            payload = {
                'id': phone_receive,
                'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
            }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})

    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/register', methods=['POST'])
def sign_up():
    # 회원가
    v = request.form['v_give']
    email_receive = request.form['email_give']
    phone_receive = request.form['phone_give']
    password_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    if v == 'menti':
        name_receive = request.form['name_give']
        year_receive = request.form['year_give']
        month_receive = request.form['month_give']
        date_receive = request.form['date_give']
        status_receive = request.form['status_give']
        register_select1_receive = request.form['register_select1_give']
        register_select2_receive = request.form['register_select2_give']
        global number
        number = (db.menti.count()) + 1

        menti_doc = {
            "number": number,
            "email": email_receive,
            "phone": phone_receive,
            "password": password_hash,
            "name": name_receive,
            "year": year_receive,
            "month": month_receive,
            "date": date_receive,
            "nickname": nickname_receive,
            "status": status_receive,
            "register_select1": register_select1_receive,
            "register_select2": register_select2_receive,
            "profile_pic": "",
            "profile_pic_real": "profile_pics/profile_placeholder.png"
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
        tags = request.form["tags"]
        mentor_doc = {
            "number": number,
            "email": email_receive,
            "phone": phone_receive,
            "password": password_hash,
            "nickname": nickname_receive,
            "tags": tags,
            "profile_pic": "",
            "profile_pic_real": "profile_pics/profile_placeholder.png",
            "univAccepted_file": "",
            "univAccepted_file_real": "univAccepted_files/univAccepted_placeholder.png",
            "univAttending_file": "",
            "univAttending_file_real": "univAttending_files/univAttending_placeholder.png"
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

        number = (db.mentor_info.count()) + 1
        new_doc = {
            "number": number,
            "nickname": nickname_receive,
            "phone": phone_receive,
            "email": email_receive,
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
            "phone": phone_receive,
            "email": email_receive
        }
        db.recordpaper.insert_one(record_doc)
    return jsonify({'result': 'success', 'msg': '회원가입을 완료했습니다.'})


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
        db.users.update_one({'phone': payload['phone']}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


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
        tags = request.form["tags"]
        doc = {
            "mentorinfo_1": mentorinfo_1_receive,
            "mentorinfo_2": mentorinfo_2_receive,
            "mentorinfo_3": mentorinfo_3_receive,
            "mentorinfo_4": mentorinfo_4_receive,
            "mentorinfo_5": mentorinfo_5_receive,
            "mentorinfo_6": mentorinfo_6_receive,
            "location": location_receive,
            "univ_type": univ_type_receive,
            "grade": grade_receive,
            "tags": tags
        }
        db.mentor_info.update_one({'phone': payload['phone']}, {'$set': doc})
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
            "activity_category_1": activity_category_1_receive,
            "activity_category_2": activity_category_2_receive,
            "activity_category_3": activity_category_3_receive,
            "activity_num_1": activity_num_1_receive,
            "activity_num_2": activity_num_2_receive,
            "activity_num_3": activity_num_3_receive,
            "activity_unit_1": activity_unit_1_receive,
            "activity_unit_2": activity_unit_2_receive,
            "activity_unit_3": activity_unit_3_receive
        }
        db.mentor_info.update_one({'phone': payload['phone']}, {'$set': doc})
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
        sns_category_2_receive = request.form["sns_category_2_give"]
        sns_id_2_receive = request.form["sns_id_2_give"]
        sns_category_3_receive = request.form["sns_category_3_give"]
        sns_id_3_receive = request.form["sns_id_3_give"]
        sns_category_4_receive = request.form["sns_category_4_give"]
        sns_id_4_receive = request.form["sns_id_4_give"]
        sns_category_5_receive = request.form["sns_category_5_give"]
        sns_id_5_receive = request.form["sns_id_5_give"]
        doc = {
            "sns_category_1": sns_category_1_receive,
            "sns_id_1": sns_id_1_receive,
            "sns_category_2": sns_category_2_receive,
            "sns_id_2": sns_id_2_receive,
            "sns_category_3": sns_category_3_receive,
            "sns_id_3": sns_id_3_receive,
            "sns_category_4": sns_category_4_receive,
            "sns_id_4": sns_id_4_receive,
            "sns_category_5": sns_category_5_receive,
            "sns_id_5": sns_id_5_receive
        }
        db.mentor_info.update_one({'phone': payload['phone']}, {'$set': doc})
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
        db.recordpaper.update_one({'phone': payload['phone']}, {'$set': doc})
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
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
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
        db.recordpaper.update_one({'phone': payload['phone']}, {'$set': doc})
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
        db.recordpaper.update_one({'phone': payload['phone']}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/add_this', methods=['POST'])
def add_this():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        mentor_univ_1_receive = request.form["mentor_univ_1_give"]
        mentor_univ_2_receive = request.form["mentor_univ_2_give"]
        mentor_univ_3_receive = request.form["mentor_univ_3_give"]
        mentor_univ_4_receive = request.form["mentor_univ_4_give"]
        mentor_univ_5_receive = request.form["mentor_univ_5_give"]
        mentor_univ_6_receive = request.form["mentor_univ_6_give"]
        mentor_univ_7_receive = request.form["mentor_univ_7_give"]
        mentor_univ_8_receive = request.form["mentor_univ_8_give"]
        mentor_univ_9_receive = request.form["mentor_univ_9_give"]
        mentor_univ_10_receive = request.form["mentor_univ_10_give"]
        doc = {
            "mentor_univ_1": mentor_univ_1_receive,
            "mentor_univ_2": mentor_univ_2_receive,
            "mentor_univ_3": mentor_univ_3_receive,
            "mentor_univ_4": mentor_univ_4_receive,
            "mentor_univ_5": mentor_univ_5_receive,
            "mentor_univ_6": mentor_univ_6_receive,
            "mentor_univ_7": mentor_univ_7_receive,
            "mentor_univ_8": mentor_univ_8_receive,
            "mentor_univ_9": mentor_univ_9_receive,
            "mentor_univ_10": mentor_univ_10_receive
        }
        db.mentor_info.update_one({'phone': payload['phone']}, {'$set': doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
