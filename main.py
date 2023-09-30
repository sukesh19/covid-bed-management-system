from ast import While
import code
from distutils.util import execute
import email
from ensurepip import bootstrap
from logging import warning
from pickle import GET
from tabnanny import check
from unicodedata import name
from urllib import response
from flask import Flask, json,redirect,render_template,flash,request
from flask.globals import request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
import razorpay
from flask_mail import Mail
import json


# mydatabase connection
local_server=True
app=Flask(__name__)
app.secret_key="sukesh"


with open('config.json','r') as c:
    params=json.load(c)["params"]


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)





# this is for getting the unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databsename'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/coviddbms'
db=SQLAlchemy(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or Hospitaluser.query.get(int(user_id)) 


class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))



class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(50),unique=True)
    dob=db.Column(db.String(1000))


class Hospitaluser(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20),unique=True)
    hemail=db.Column(db.String(100),unique=True)
    hpassword=db.Column(db.String(1000))


class Hospitaldata(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20),unique=True)
    hname=db.Column(db.String(100),unique=True)
    haddress=db.Column(db.String(1000))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)

class Trig(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)
    querys=db.Column(db.String(50))
    date=db.Column(db.String(50))



class Bookingpatient(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(50),unique=True)
    bedtype=db.Column(db.String(100))
    hcode=db.Column(db.String(20))
    haddress=db.Column(db.String(100))
    spo2=db.Column(db.Integer)
    pname=db.Column(db.String(100))
    pphone=db.Column(db.String(100))
    paddress=db.Column(db.String(100))



@app.route("/learn")
def learn():
   
    return render_template("learn.html")



@app.route("/contact")
def contact():
   
    return render_template("contact.html")


@app.route("/")
def home():
   
    return render_template("index.html")



@app.route("/trigers")
def trigers():
    query=Trig.query.all() 
    return render_template("trigers.html",query=query)


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        srfid=request.form.get('srf')
        email=request.form.get('email')
        dob=request.form.get('dob')

        # print(srfid,email,dob)
        
        encpassword=generate_password_hash(dob)
        user=User.query.filter_by(srfid=srfid).first()
        emailUser=User.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or srif is already taken","warning")
            return render_template("usersignup.html")
        new_user=db.engine.execute(f"INSERT INTO `user` (`srfid`,`email`,`dob`) VALUES ('{srfid}','{email}','{encpassword}') ")
        mail.send_message('COVID CARE CENTER',sender=params['gmail-user'],recipients=[email],body=f"Welcome to covid care center and thanks for choosing our service\nYour have successfully signed up and your Credentials Are:\n srfid : {srfid}\n dob: {dob}\n\n Do not share your password\n\n\nThank You...\n with regards..." )
        flash("SignUp Success Please Login","success")
        return render_template("userlogin.html")

    return render_template("usersignup.html")


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        srfid=request.form.get('srf')
        dob=request.form.get('dob')
        user=User.query.filter_by(srfid=srfid).first()
        if user and check_password_hash(user.dob,dob):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")


    return render_template("userlogin.html")

@app.route('/hospitallogin',methods=['POST','GET'])
def hospitallogin():
    if request.method=="POST":
        email=request.form.get('hemail')
        password=request.form.get('hpassword')
        user=Hospitaluser.query.filter_by(hemail=email).first()
        if user and check_password_hash(user.hpassword,password):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("hospitallogin.html")


    return render_template("hospitallogin.html")

@app.route('/admin',methods=['POST','GET'])
def admin():
 
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if(username==params['user'] and password==params['password']):
            session['user']=username
            flash("login success","info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials","danger")

    return render_template("admin.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))

@app.route('/morecontrols')
def morecontrols():
        
  return render_template("newadmin.html")


@app.route('/addHospitalUser',methods=['POST','GET'])
def hospitalUser():
   
    if('user' in session and session['user']==params['user']):
      
        if request.method=="POST":
            hcode=request.form.get('hcode')
            email=request.form.get('hemail')
            password=request.form.get('hpassword')        
            encpassword=generate_password_hash(password)  
            hcode=hcode.upper()      
            emailUser=Hospitaluser.query.filter_by(hemail=email).first()
            if  emailUser:
                flash("Email  is already taken","warning")
         
            db.engine.execute(f"INSERT INTO `hospitaluser` (`hcode`,`hemail`,`hpassword`) VALUES ('{hcode}','{email}','{encpassword}') ")

            # my mail starts from here if you not need to send mail comment the below line
           
            mail.send_message('COVID CARE CENTER',sender=params['gmail-user'],recipients=[email],body=f" Welcome and thanks for choosing us \n Your Login Credentials Are: \n Email Address: {email} \n Password: {password} \n Hospital Code {hcode} \n Do not share your Credentials \n\n\nThank You...\n With Regards" )

            flash("Data Sent and Inserted Successfully","warning")
            return render_template("addHosUser.html")
    else:
        flash("Login and try Again","warning")
        return render_template("addHosUser.html")
    

# testing wheather db is connected or not  
@app.route("/test")
def test():
    try:
        a=Test.query.all()
        print(a)
        return f'MY DATABASE IS CONNECTED'
    except Exception as e:
        print(e)
        return f'MY DATABASE IS NOT CONNECTED {e}'


@app.route("/logoutadmin")
def logoutadmin():
    session.pop('user')
    flash("You are logout admin", "primary")

    return redirect('/admin')



@app.route("/addhospitalinfo",methods=['POST','GET'])
def addhospitalinfo():
    email=current_user.hemail
    posts=Hospitaluser.query.filter_by(hemail=email).first()
    code=posts.hcode
    postsdata=Hospitaldata.query.filter_by(hcode=code).first()

    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        haddress=request.form.get('haddress')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        huser=Hospitaluser.query.filter_by(hcode=hcode).first()
        hduser=Hospitaldata.query.filter_by(hcode=hcode).first()
        if hduser:
            flash("Data is already Present you can update it..","primary")
            return render_template("hospitaldata.html")
        if huser:            
            db.engine.execute(f"INSERT INTO `hospitaldata` (`hcode`,`hname`,`haddress`,`normalbed`,`hicubed`,`icubed`,`vbed`) VALUES ('{hcode}','{hname}','{haddress}','{nbed}','{hbed}','{ibed}','{vbed}')")
            flash(f"Data Is Added \n\n please go back to home page","primary")
        else:
            flash("Hospital Code not Exist","warning")

    return render_template("hospitaldata.html",postsdata=postsdata)



@app.route("/hedit/<string:id>",methods=['POST','GET'])
@login_required
def hedit(id):
    posts=Hospitaldata.query.filter_by(id=id).first()
  
    if request.method=="POST":
        hcode=request.form.get('hcode')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        db.engine.execute(f"UPDATE `hospitaldata` SET `hcode` ='{hcode}',`normalbed`='{nbed}',`hicubed`='{hbed}',`icubed`='{ibed}',`vbed`='{vbed}' WHERE `hospitaldata`.`id`={id}")
        flash("Slot Updated","info")
        return redirect("/addhospitalinfo")

    # posts=Hospitaldata.query.filter_by(id=id).first()
    return render_template("hedit.html",posts=posts)


@app.route("/hdelete/<string:id>",methods=['POST','GET'])
@login_required
def hdelete(id):
    db.engine.execute(f"DELETE FROM `hospitaldata` WHERE `hospitaldata`.`id`={id}")
    flash("Data Deleted","danger")
    return redirect("/addhospitalinfo")


@app.route("/dhos",methods=['POST','GET'])
def dhos():
    if request.method=="POST":
        id=request.form.get('id')
        dh=Hospitaluser.query.filter_by(id=id).first()
        if dh:
             db.engine.execute(f"DELETE  FROM `Hospitaluser` WHERE `Hospitaluser`.`id`={id}")
             db.engine.execute(f"DELETE  FROM `Hospitaldata` WHERE `Hospitaldata`.`id`={id}")

             flash("hospital is Deleted","danger")
             return redirect("/newadmin")
             pass
        else:
                flash("hospital id does not exist","danger")
             
    return render_template("dhos.html")




@app.route("/duser",methods=['POST','GET'])
def duser():
    if request.method=="POST":
        id=request.form.get('id')
        dh=User.query.filter_by(id=id).first()
        if dh:
             db.engine.execute(f"DELETE  FROM `User` WHERE `User`.`id`={id}")
             flash("user is Deleted","danger")
             return redirect("/newadmin")
        else:
                flash("user id does not exist","danger")
             
    return render_template("duser.html")

@app.route("/pdetails",methods=['GET'])
@login_required
def pdetails():
    code=current_user.srfid
    print(code)
    data=Bookingpatient.query.filter_by(srfid=code).first()
   
    
    return render_template("detials.html",data=data)


@app.route("/slotbooking",methods=['POST','GET'])
@login_required  
def slotbooking():
    query=db.engine.execute(f"SELECT * FROM `hospitaldata` ")
    if request.method=="POST":
        srfid=request.form.get('srfid')
        email=request.form.get('email')
        bedtype=request.form.get('bedtype')
        hcode=request.form.get('hcode')
        haddress=request.form.get('haddress')
        spo2=request.form.get('spo2')
        pname=request.form.get('pname')
        pphone=request.form.get('pphone')
        paddress=request.form.get('paddress')  
        check2=Hospitaldata.query.filter_by(hcode=hcode,haddress=haddress).first()
        if not check2:
            flash("Hospital Code or Hospital address does not match","warning") 
            flash("Please provide valid Hospital code and same Hospital address","danger") 

            return render_template("booking.html",query=query)    
        else:
            code=hcode
            haddress=haddress
            dbb=db.engine.execute(f"SELECT * FROM `hospitaldata` WHERE `hospitaldata`.`hcode`='{code}' ")        
            bedtype=bedtype
        if bedtype=="NormalBed":     
            for d in dbb:
                seat=d.normalbed
                print(seat)
            if seat<=0 :
                flash(f"No beds available on your selection try other hospitals ","warning")
                pass
            else:
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.normalbed=seat-1 
                db.session.commit()

        elif bedtype=="HICUBed":      
            for d in dbb:
                seat=d.hicubed
                print(seat)
            if seat<=0 :
                flash(f"No beds available on your selection try other hospitals ","warning")
                pass

            else:
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.hicubed=seat-1
                db.session.commit()
    
        elif bedtype=="ICUBed":     
            for d in dbb:
                seat=d.icubed
                print(seat)
            if seat<=0 :
                flash(f"No beds available on your selection try other hospitals ","warning")
                pass

            else:
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.icubed=seat-1
                db.session.commit()
    

        elif bedtype=="VENTILATORBed": 
            for d in dbb:
                seat=d.vbed
            if seat<=0 :
                flash(f"No beds available on your selection try other hospitals ","warning")
                pass
            
            else:
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.vbed=seat-1 
                db.session.commit()
        else:
            pass

        check=Hospitaldata.query.filter_by(hcode=hcode).first()
        if seat<0 and check :
            query=db.engine.execute(f"SELECT * FROM `hospitaldata` ")
            flash(f"try again","danger")
            pass

        check3=Bookingpatient.query.filter_by(srfid=srfid).first()
        if  check3:
            flash("booking exist","warning") 
            return render_template("booking.html",query=query)  
           

        elif(seat>0 and check):
            res=Bookingpatient(srfid=srfid,email=email,bedtype=bedtype,hcode=hcode,haddress=haddress,spo2=spo2,pname=pname,pphone=pphone,paddress=paddress)
            db.session.add(res)
            db.session.commit()
            mail.send_message('COVID CARE CENTER',sender=params['gmail-user'],recipients=[email],body=f" Thanks for choosing us \n Your booking  is confirmed \n Patient's  details : {email} \n Your Booking id : {res} \n Your srfid :{srfid} \n Bedtype :{bedtype} \n Hospital code :{hcode} \n Hospital Address :{haddress} \n spo2 :{spo2} \n Your Name :{pname} \n Your Address :{paddress} \n\n show this E-mail when you visit the Hospital...\n\n\nThank You...\nWith Regards" )
            flash(f"Slot is Booked kindly Visit Hospital for Further Procedure \n \n booking details  are sent to your registered email-id ","success")
            flash(f"Please visit the hospital with valid id-card for Verification","warning")
        else:
        
            flash(f"Try again","danger")
            pass
            
    return render_template("booking.html",query=query)


@app.route("/availbed",methods=['POST','GET'])
@login_required
def availbeds():
    query=db.engine.execute(f"SELECT * FROM `hospitaldata` ")
    if request.method==['POST','GET']:
        srfid=request.form.get('srfid')
        email=request.form.get('email')
        bedtype=request.form.get('bedtype')
        hcode=request.form.get('hcode')
        haddress=request.form.get('haddress')
        spo2=request.form.get('spo2')
        pname=request.form.get('pname')
        pphone=request.form.get('pphone')
        paddress=request.form.get('paddress')  
        check2=Hospitaldata.query.filter_by(hcode=hcode).first()
        if not check2:
            pass

        code=hcode
        dbb=db.engine.execute(f"SELECT * FROM `hospitaldata` WHERE `hospitaldata`.`hcode`='{code}' ")        
        bedtype=bedtype
        if bedtype=="NormalBed":     
            for d in dbb:
                seat=d.normalbed
                print(seat)
            if seat<=0 :
                flash(f"No beds available on your selection try other hospitals ","warning")
                pass
            else:
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.normalbed=seat-1 
                db.session.commit()

        elif bedtype=="HICUBed":      
            for d in dbb:
                seat=d.hicubed
                print(seat)
            if seat<=0 :
                flash(f"No beds available on your selection try other hospitals ","warning")
                pass

            else:
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.hicubed=seat-1
                db.session.commit()
    
        elif bedtype=="ICUBed":     
            for d in dbb:
                seat=d.icubed
                print(seat)
            if seat<=0 :
                flash(f"No beds available on your selection try other hospitals ","warning")
                pass

            else:
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.icubed=seat-1
                db.session.commit()
    

        elif bedtype=="VENTILATORBed": 
            for d in dbb:
                seat=d.vbed
            if seat<=0 :
                flash(f"No beds available on your selection try other hospitals ","warning")
                pass
            
            else:
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.vbed=seat-1 
                db.session.commit()
        else:
            pass

            db.session.commit()
        
    
    return render_template("availbeds.html",query=query)




app.run(debug=True)