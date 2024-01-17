from flask import render_template, request,session, redirect, url_for
from flask_paginate import Pagination, get_page_args
from app.db import DB
import hashlib, pymysql
from app.service.cust_service import cust_table_service
import logs.loggings as logs

def user_main_service():
    return render_template('/user/main.html')

def user_login_service():
    if request.method=='GET':
        return render_template('/user/login.html')
    else :
        memberid = request.form.get("memberid")
        password = request.form.get("password")
        #password = encrypt_pw(memberid,password)
        name = request.form.get("name")
        SQL = "SELECT * FROM XMEMBER where memberid = '{0}' and password = '{1}'".format(memberid,password)
        conn = DB('dict')
        result = conn.select_all(SQL,None)
        if len(result)==0:
            logs.logger.info(f'{name} 관리자가 로그인 하였습니다.')
            return render_template('/user/login.html')
        else:
            session['userInfo'] = result
            if session['userInfo'][0].get('grade')=='10':
                logs.logger.info(f'{name} 회원이 로그인 하였습니다.')
                return redirect(url_for('driver_page.driver_mytable_service'))
            elif session['userInfo'][0].get('grade')=='20':
                logs.logger.info(f'{name} 고객사가 로그인 하였습니다.')
                return redirect(url_for('cust_page.cust_table_service'))
            else :
                logs.logger.info(f'{name} 관리자가 로그인 하였습니다.')
                return redirect(url_for('user_page.user_manage_service'))

def user_join_service():
    if request.method=='GET':
        return render_template('/user/join.html')
    else:
        memberid=request.form.get("memberid")
        password=request.form.get("password")
        #password = encrypt_pw(memberid,password)
        telphone=request.form.get("telphone")
        name=request.form.get("name")
        info=request.form.get("info")
        carinfo=request.form.get("carinfo")
        grade=request.form.get("grade")
        SQL = '''INSERT INTO XMEMBER 
        (MEMBERID, PASSWORD, TELPHONE, NAME, carinfo, INFO, grade)VALUES
        ('{0}','{1}','{2}','{3}','{4}','{5}','{6}')'''.format(memberid, password, telphone, name, carinfo, info, grade)
        conn = DB('dict')
        groups = conn.save_one(SQL,None)
        logs.logger.info(f'{name} 회원이 가입을 하였습니다.')
        return redirect(url_for('user_page.user_login_service'))

def user_profile_service():
    return render_template('/user/profile.html')

def user_manage_service():
    if '00' == session['userInfo'][0].get('grade'):
        per_page = 10
        page = request.args.get('page', 1, type=int)
        page, _, offset = get_page_args(per_page=per_page)
        dbcon = DB('dict')
        cur = dbcon.cur
        cur.execute("select count(0) as page from XMEMBER")
        total = cur.fetchone().get('page')
        cur.execute(
            "SELECT * FROM XMEMBER" 
            " LIMIT %s OFFSET %s;", 
            (per_page, offset),
        )
        posts = cur.fetchall()
        cur.close()

        SQL = "SELECT * FROM XMEMBER LIMIT %s OFFSET %s"
        conn = DB('dict')
        result = conn.select_all(SQL,(per_page, (page-1)*per_page))
        return render_template('/user/manage.html' ,users=posts, pagination=Pagination(
                page=page,
                total=total,
                per_page=per_page,
                prev_label="<<",
                next_label=">>",
                format_total=True,
            ),
            search=True
                            )
    else:
        return '불가능한 접근입니다'

def user_logout_service():
    session.pop('userInfo', None)
    return redirect(url_for('user_page.user_login_service'))

#def encrypt_pw(id, password):
    #password = password+id
    #password = hashlib.sha256(password.encode()).hexdigest()
    #return password