from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date
import json, os, time, secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
DATA_FILE = os.environ.get('DATA_FILE', 'progress.json')
PASS_MARK = 30
POINTS_PER_CORRECT_ANSWER = 10

QUIZZES = {
    'Python': [
        {'question':'Which keyword is used to define a function in Python?','options':['func','define','def','function'],'answer':'def','difficulty':'Easy'},
        {'question':'Which symbol is used for comments in Python?','options':['//','#','/*','<!--'],'answer':'#','difficulty':'Easy'},
        {'question':'Which data type stores True or False?','options':['int','str','bool','list'],'answer':'bool','difficulty':'Easy'},
        {'question':'Which function displays output in Python?','options':['input()','print()','show()','display()'],'answer':'print()','difficulty':'Medium'},
        {'question':'Which brackets are used to create a list?','options':['()','{}','[]','<>'],'answer':'[]','difficulty':'Medium'}],
    'HTML & CSS': [
        {'question':'What does HTML stand for?','options':['Hyper Text Markup Language','High Text Machine Language','Hyper Tool Multi Language','Home Text Markup Language'],'answer':'Hyper Text Markup Language','difficulty':'Easy'},
        {'question':'Which tag is used to create a paragraph?','options':['<h1>','<p>','<br>','<img>'],'answer':'<p>','difficulty':'Easy'},
        {'question':'Which CSS property changes text colour?','options':['font-style','background','color','text-size'],'answer':'color','difficulty':'Easy'},
        {'question':'Which HTML tag creates a hyperlink?','options':['<a>','<link>','<href>','<url>'],'answer':'<a>','difficulty':'Medium'},
        {'question':'Which symbol represents an ID selector in CSS?','options':['.','#','*','&'],'answer':'#','difficulty':'Medium'}],
    'DBMS': [
        {'question':'What does DBMS stand for?','options':['Data Basic Management System','Database Management System','Digital Base Management Service','Data Backup Management System'],'answer':'Database Management System','difficulty':'Easy'},
        {'question':'Which SQL command retrieves data?','options':['GET','OPEN','SELECT','FETCH ALL'],'answer':'SELECT','difficulty':'Easy'},
        {'question':'Which key uniquely identifies each row?','options':['Foreign Key','Primary Key','Duplicate Key','Candidate Value'],'answer':'Primary Key','difficulty':'Easy'},
        {'question':'Which command adds a new row to a table?','options':['UPDATE','INSERT','ALTER','DELETE'],'answer':'INSERT','difficulty':'Medium'},
        {'question':'Which SQL clause filters records?','options':['ORDER BY','GROUP BY','WHERE','JOIN'],'answer':'WHERE','difficulty':'Medium'}],
    'General Knowledge': [
        {'question':'What is the capital of India?','options':['Mumbai','New Delhi','Chennai','Kolkata'],'answer':'New Delhi','difficulty':'Easy'},
        {'question':'Which planet is known as the Red Planet?','options':['Venus','Jupiter','Mars','Mercury'],'answer':'Mars','difficulty':'Easy'},
        {'question':'How many days are there in a leap year?','options':['364','365','366','367'],'answer':'366','difficulty':'Easy'},
        {'question':'Which is the largest ocean?','options':['Atlantic Ocean','Indian Ocean','Arctic Ocean','Pacific Ocean'],'answer':'Pacific Ocean','difficulty':'Medium'},
        {'question':'Which gas do plants absorb?','options':['Oxygen','Nitrogen','Carbon dioxide','Hydrogen'],'answer':'Carbon dioxide','difficulty':'Medium'}]
}
SUBJECTS=list(QUIZZES)
DIFFICULTY_POINTS={'Easy':10,'Medium':15,'Hard':20}
DIFFICULTY_TIME={'Easy':90,'Medium':75,'Hard':60}

def load_data():
    try:
        with open(DATA_FILE, encoding='utf-8') as f:
            data=json.load(f)
        return data if isinstance(data,dict) else {}
    except (OSError, ValueError): return {}
def save_data(data):
    tmp=DATA_FILE+'.tmp'
    with open(tmp,'w',encoding='utf-8') as f: json.dump(data,f,indent=2)
    os.replace(tmp,DATA_FILE)
def current_player():
    if 'username' not in session: return None
    return load_data().get(session['username'])
def login_required(fn):
    @wraps(fn)
    def wrapper(*a,**kw):
        if 'username' not in session: return redirect(url_for('home'))
        return fn(*a,**kw)
    return wrapper
def ensure_player(data, username):
    if username not in data:
        data[username]={'password':'','points':0,'unlocked':['Python'],'completed':[], 'best_scores':{},'history':[], 'achievements':[], 'created':date.today().isoformat()}
    p=data[username]
    p.setdefault('points',0); p.setdefault('unlocked',['Python']); p.setdefault('completed',[])
    p.setdefault('best_scores',{}); p.setdefault('history',[]); p.setdefault('achievements',[])
    return p
def award_achievements(player):
    checks=[('first_quiz','First Steps','Complete your first quiz',len(player['history'])>=1),('perfect_score','Perfect Run','Score 100% in a quiz',any(h['score']==100 for h in player['history'])),('quiz_explorer','Quiz Explorer','Complete all four subjects',len(player['completed'])==len(SUBJECTS)),('point_collector','Point Collector','Earn 100 points',player['points']>=100),('daily_player','Daily Challenger','Complete a daily challenge',any(h.get('daily') for h in player['history']))]
    for key,title,desc,ok in checks:
        if ok and key not in player['achievements']: player['achievements'].append(key)
    return [{'title':t,'description':d,'earned':k in player['achievements']} for k,t,d,_ in checks]

@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='POST':
        username=request.form.get('username','').strip()
        password=request.form.get('password','')
        action=request.form.get('action','login')
        if not username or not password:
            flash('Enter both username and password.','error')
        elif len(username)>24 or len(password)<4:
            flash('Username must be under 25 characters and password at least 4 characters.','error')
        else:
            data=load_data()
            if action=='register':
                if username in data: flash('That username already exists. Please log in.','error')
                else:
                    p=ensure_player(data,username); p['password']=generate_password_hash(password); save_data(data)
                    session['username']=username; return redirect(url_for('dashboard'))
            elif username in data and data[username].get('password') and check_password_hash(data[username]['password'],password):
                session['username']=username; return redirect(url_for('dashboard'))
            else: flash('Login details are incorrect. If new, choose Create account.','error')
    if session.get('username'): return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    data=load_data(); p=ensure_player(data,session['username']); save_data(data)
    achievements=award_achievements(p); save_data(data)
    total=len(p['history']); avg=round(sum(h['score'] for h in p['history'])/total) if total else 0
    today=date.today().isoformat(); daily_done=any(h.get('daily') and h.get('date')==today for h in p['history'])
    return render_template('dashboard.html',name=session['username'],player=p,subjects=SUBJECTS,achievements=achievements,total=total,avg=avg,daily_done=daily_done)

@app.route('/quiz/<subject>')
@login_required
def quiz(subject):
    data=load_data(); p=data.get(session['username'],{})
    if subject not in QUIZZES or subject not in p.get('unlocked',[]): flash('Complete the previous quiz to unlock this one.','error'); return redirect(url_for('dashboard'))
    level=request.args.get('level','Easy')
    if level not in DIFFICULTY_POINTS: level='Easy'
    qs=[q for q in QUIZZES[subject] if q['difficulty']==level]
    if len(qs)<2: qs=QUIZZES[subject][:]
    session['quiz_started']=time.time(); session['quiz_subject']=subject; session['quiz_level']=level
    session['quiz_daily']=request.args.get('daily')=='1'
    return render_template('quiz.html',subject=subject,questions=qs,level=level,time_limit=DIFFICULTY_TIME[level],daily=session['quiz_daily'])

@app.route('/result',methods=['POST'])
@login_required
def result():
    subject=session.pop('quiz_subject',None); level=session.pop('quiz_level','Easy'); daily=session.pop('quiz_daily',False)
    started=session.pop('quiz_started',None)
    if subject not in QUIZZES or started is None: return redirect(url_for('dashboard'))
    data=load_data(); p=data.get(session['username'])
    if not p or subject not in p.get('unlocked',[]): return redirect(url_for('dashboard'))
    qs=[q for q in QUIZZES[subject] if q['difficulty']==level]
    if len(qs)<2: qs=QUIZZES[subject][:]
    elapsed=int(time.time()-started); expired=elapsed>DIFFICULTY_TIME[level]
    review=[]; correct_count=0
    for i,q in enumerate(qs):
        selected=request.form.get(f'q{i}','Not answered')
        ok=(selected==q['answer'] and not expired)
        if ok: correct_count+=1
        review.append({'question':q['question'],'selected':selected,'correct':q['answer'],'is_correct':ok})
    score=round(correct_count/len(qs)*100) if qs else 0
    earned=correct_count*DIFFICULTY_POINTS[level]
    passed=score>=60 and not expired
    # points are awarded for each attempt; repeated quizzes remain useful practice
    p['points']+=earned
    if passed and subject not in p['completed']: p['completed'].append(subject)
    if passed:
        idx=SUBJECTS.index(subject)
        if idx+1<len(SUBJECTS) and SUBJECTS[idx+1] not in p['unlocked']: p['unlocked'].append(SUBJECTS[idx+1])
    p['best_scores'][subject]=max(score,p['best_scores'].get(subject,0))
    p['history'].append({'subject':subject,'level':level,'score':score,'earned':earned,'date':date.today().isoformat(),'daily':bool(daily)})
    achievements=award_achievements(p); save_data(data)
    return render_template('result.html',subject=subject,score=score,earned=earned,points=p['points'],passed=passed,review=review,expired=expired,achievements=achievements)

@app.route('/leaderboard')
def leaderboard():
    data=load_data(); rows=[]
    for name,p in data.items(): rows.append({'name':name,'points':p.get('points',0),'completed':len(p.get('completed',[])),'best':max(p.get('best_scores',{}).values(),default=0)})
    rows.sort(key=lambda x:(x['points'],x['completed'],x['best']),reverse=True)
    return render_template('leaderboard.html',rows=rows[:20])
@app.route('/profile')
@login_required
def profile():
    p=current_player(); return render_template('profile.html',name=session['username'],player=p)
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('home'))
@app.route('/health')
def health(): return {'status':'ok'}
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)),debug=False)
