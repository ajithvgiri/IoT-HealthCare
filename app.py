from flask import Flask, render_template, request, jsonify
import MySQLdb
import Cookie
import os
import cgi, cgitb
import random
import datetime
import time
from time import sleep
import RPi.GPIO as gpio
import serial


db= MySQLdb.connect("localhost","root","root","HealthCare")
cursor = db.cursor()

app = Flask(__name__)

#Cookie
c = Cookie.SimpleCookie()

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
 
receiver_in=17
gpio.setup(receiver_in,gpio.IN)



@app.route('/')
def main():
    return render_template('login.html')

@app.route('/doctors')
def doctors():
    return render_template('doctorsList.html')



@app.route('/signup')
def signup():
    return render_template('register.html')


@app.route('/signup',methods=['POST','GET'])
def register():
    fullname = request.form['fullname']
    email = request.form['email']
    password = request.form['password']
    address = request.form['address']
    gender = request.form['gender']
    sql = "INSERT INTO registration(fullname,email,password,gender,address,status) VALUES ('%s' ,'%s', '%s', '%s','%s', '%d')" %\
                  (fullname,email,password,gender,address,0)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

    return render_template('login.html')
    



@app.route('/tempareture',methods=['POST','GET'])
def readtemperature():
    return render_template('userTemperatures.html',name=c['name'].value,uid=c['id'].value)

@app.route('/heart',methods=['POST','GET'])
def readheart():
    return render_template('userHeartBeats.html',name=c['name'].value,uid=c['id'].value)







@app.route('/login',methods=['POST','GET'])
def login():
    email = request.form['email']
    password = request.form['password']
    if (email == "doctor@gmail.com" and password == "doctor"):
        return doctor() 
    else: 
        sql = "SELECT * FROM registration WHERE email='%s' AND password='%s' AND status='%s'" % \
                  (email,password,'1')
        try:
            cursor.execute(sql)
            #fetch all results
            results = cursor.fetchall()
            for row in results:
                c['id'] = row[0]
                c['id']['max-age']= 600
                c['name'] = row[1]
                c['name']['max-age']=60*60*60*1*30
                return render_template('userHomes.html',name=c['name'].value,uid=c['id'].value)
                                    
        except:
            db.rollback()

    return main()

@app.route('/userHome') 
def userhome():
    return render_template('userHomes.html',name=c['name'].value,uid=c['id'].value)



@app.route('/Zigbee',methods=['POST','GET'])
def zigbee():
    name =c['name'].value
    #ser = serial.Serial ("/dev/ttyAMA0")    #Open named port 
    #ser.baudrate = 9600  #Set baud rate to 9600
    #ser.open()
    #ser.write("2")
    #temps = ser.readline()
    #tempi = int(float(temps))
    tempi = random.randint(34,35)
    temp = tempi * 9.0/5.0 + 32.0
    #ser.close()
    if(temp > 90.8 and temp < 99.8 ):
        status = "Normal"
    elif(temp < 90.8):
        status = "Low"
    else:
        status = "High"
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    today = str(today)
    sql = "INSERT INTO temperature(name,temp,date,status) VALUES ('%s' ,'%s', '%s', '%s')" %\
                  (name,temp,today,status)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    return jsonify(tempa=temp,time=today,status=status)

@app.route('/HeartBeat',methods=['POST','GET'])
def heartrate():
    name =c['name'].value
    #ser = serial.Serial ("/dev/ttyAMA0")    #Open named port 
    #ser.baudrate = 9600                     #Set baud rate to 9600
    #ser.open()
    #ser.write("1")
    #beat = ser.readline()
    beat = random.randint(70,100)
        
    if(beat > 60 and beat < 80 ):
        status = "Normal"
    elif(beat >80):
        status = "High"
    else:
        status = "Not Avail"
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    today = str(today)
    sql = "INSERT INTO heartbeat(name,bpm,date,status) VALUES ('%s' ,'%s', '%s', '%s')" %\
                  (name,beat,today,status)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    return jsonify(beat=beat,time=today,status=status)

'''@app.route('/heart5')
def h():
    start = time.time()
    #end = datetime.datetime().now().strftime("%S")
    while 1:
        return str(start)
       
    return ("Success")'''

@app.route('/bp',methods=['POST','GET'])
def blood():
    return render_template('userBP.html',name=c['name'].value,uid=c['id'].value)

@app.route('/bloodpressure',methods=['POST','GET'])
def bp():
    name =c['name'].value
    #ser = serial.Serial ("/dev/ttyAMA0")    #Open named port 
    #ser.baudrate = 9600                     #Set baud rate to 9600
    #ser.open()
    #ser.write("3") 
    #x1 = ser.readline()
    x1 = random.randint(90,140)
    x2 = random.randint(60,90)
    if(x1 < 120 and x2 < 60):
        status = "Low"
    elif(x1 < 140 or x1 >120 and x2 >60 or x2 < 90):
        status = "Normal"
    elif(x1 > 140 and x2 > 90 ):
        status = "High"
    else:
        status = ""
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    today = str(today)
    bp1 = str(x1)
    bp2 = str(x2)
    bp = bp1+"Hg/"+bp2+"Hg"
    sql = "INSERT INTO bp(name,bpm,date,status) VALUES ('%s' ,'%s', '%s', '%s')" %\
                  (name,bp,today,status)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    return jsonify(beat=bp,time=today,status=status)

@app.route('/doctor')
def doctor():
    sql = "SELECT * FROM registration WHERE status=1 "
    try:
        cursor.execute(sql)
        #fetch all results
        results = cursor.fetchall()
    except:
        db.rollback()
    return render_template('doctorHome.html',users=results)


@app.route('/alert')
def alert():
    sql = "INSERT INTO temperature(name,temp,date,status) VALUES ('%s' ,'%s', '%s', '%s')" %\
                  (name,temp,today,status)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    return render_template('doctorAlert.html')

@app.route('/userRequest')
def userreq():
    sql = "SELECT * FROM registration WHERE status=0 "
    try:
        cursor.execute(sql)
        #fetch all results
        results = cursor.fetchall()
    except:
        db.rollback()
            
    return render_template('userRequest.html',users = results)

@app.route('/alertDoc')
def docalert():
    name = c['name'].value
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    now = str(now)
    if(name != ""):
        sql = "SELECT * FROM alert WHERE name='%s' AND date='%s' AND status='%s' OR status='%s' " % \
               (name,now,"High","Low")
        try:
            cursor.execute(sql)
            #fetch all results
            results = cursor.fetchall()
            for result in results:
                temp = result[0]
                time = result[1]
                status= result[2]
        except:
            db.rollback()           
    return jsonify(name=name,tempa = temp,time =time,status=status)



    
@app.route('/approveUser',methods=['GET','POST'])
def approveuser():
    id=request.args.get('id')
    sql = "UPDATE registration SET status=1 WHERE id='%s'" %\
                  (id)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    return userreq()


@app.route('/viewDetails',methods=['GET','POST'])
def viewdetails():
    name = request.args.get('name')
    sql = "SELECT * FROM heartbeat WHERE name='%s'" % \
          (name)   
    try:
        cursor.execute(sql)
        #fetch all results
        results = cursor.fetchall()
    except:
        db.rollback()
    return render_template('userDetails.html',results = results, value="Temperature")

@app.route('/viewTempe',methods=['GET','POST'])
def viewtemp():
    name = request.args.get('name')
    sql = "SELECT * FROM temperature WHERE name='%s'" % \
          (name)
    try:
        cursor.execute(sql)
        #fetch all results
        temp = cursor.fetchall()
    except:
        db.rollback()
    return render_template('userDetails.html',results=temp,value="Heart Beat")

@app.route('/viewResult',methods=['POST','GET'])
def viewresult():
    name = c['name'].value
    sql = "SELECT * FROM temperature WHERE name='%s'" % \
          (name)
    try:
        cursor.execute(sql)
        #fetch all results
        results = cursor.fetchall()
    except:
        db.rollback()
    return render_template('userResult.html',temperatures=results,name=c['name'].value,uid=c['id'].value)

@app.route('/404')
def error(): 
    return render_template('404.html')

@app.route('/testResult')
def testResult():
    name = c['name'].value
    sql = "select temperature.temp,temperature.status,heartbeat.bpm,heartbeat.status,bp.bpm,bp.status from temperature inner join heartbeat on temperature.name = heartbeat.name inner join bp on heartbeat.name = bp.name WHERE temperature.name='%s' order by temperature.id LIMIT 1" % \
          (name)
    try:
        cursor.execute(sql)
        #fetch all results
        results = cursor.fetchall()
        for result in results:
            temp = result[0]
            tstatus = result[1]
            beat= result[2]
            beatstatus = result[3]
            bp = result[4]
            bpstatus = result[5]
            if(tstatus != "Normal" or beatstatus !="Normal" or bpstatus !="Normal"):
                finalst = "Please Consult your Doctor"
            else:
                finalst = "The result is Normal"
    except:
        db.rollback()
    return render_template('testResults.html',temps = temp,tstatuss = tstatus,hb=beat,hbs=beatstatus,bpm=bp,bpms=bpstatus,fs=finalst,name=c['name'].value,uid=c['id'].value)
    


if __name__ == '__main__':
    app.run(debug=True,host='192.168.1.7')
