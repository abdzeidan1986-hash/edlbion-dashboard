import os, json, secrets
from flask import Flask, request, redirect, session, render_template_string, make_response
from werkzeug.security import check_password_hash

app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY", "")
if not app.secret_key: raise RuntimeError("Set SECRET_KEY in Render environment")
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SECURE=True, SESSION_COOKIE_SAMESITE="Lax", MAX_CONTENT_LENGTH=12*1024*1024)
LOGIN='<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>بوربي - إدلبيون | تسجيل الدخول</title><style>body{background:#071425;color:#e9f3ff;font:16px Tahoma,Arial;display:grid;place-items:center;min-height:95vh}form{background:#10263f;border:1px solid #28435d;border-radius:16px;padding:32px;width:min(390px,90vw)}input,button{display:block;width:100%;padding:13px;margin:15px 0;background:#17314c;color:white;border:1px solid #36536e;border-radius:8px;box-sizing:border-box}button{background:#1374bf;cursor:pointer}p{color:#f2c579}</style><form method="post"><h2>بوربي – إدلبيون</h2><div>لوحة التحكم المالية المحمية</div><input type="password" name="password" placeholder="كلمة المرور" required><button>دخول</button>{% if error %}<p>كلمة المرور غير صحيحة</p>{% endif %}</form></html>'
@app.after_request
def headers(r):
 r.headers['Cache-Control']='no-store'
 r.headers['X-Content-Type-Options']='nosniff'
 r.headers['X-Frame-Options']='DENY'
 r.headers['Referrer-Policy']='no-referrer'
 r.headers['Content-Security-Policy']="default-src 'self' 'unsafe-inline' blob: data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
 return r
@app.route('/login',methods=['GET','POST'])
def login():
 error=False
 if request.method=='POST':
  stored=os.environ.get('DASHBOARD_PASSWORD_HASH','')
  password=request.form.get('password','')
  if stored and check_password_hash(stored,password):
   session.clear();session['authorized']=True
   return redirect('/')
  error=True
 return render_template_string(LOGIN,error=error), (401 if error else 200)
@app.route('/logout',methods=['POST'])
def logout():
 session.clear();return redirect('/login')
@app.route('/')
def index():
 if not session.get('authorized'):return redirect('/login')
 from pathlib import Path
 page=Path(__file__).with_name('dashboard.html').read_text(encoding='utf-8')
 # No financial data is shipped in source. OneDrive server-side integration is a separate step.
 page=page.replace('__SERVER_DATA__','[]')
 page=page.replace('</header>','<form action="/logout" method="post"><button class="btn secondary" type="submit">تسجيل الخروج</button></form></header>',1)
 return make_response(page)
@app.route('/health')
def health():return {'status':'ok'}
