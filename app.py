from flask import Flask,render_template,request,flash,session,redirect,url_for
import mysql.connector
import razorpay.errors
from otp import genotp
from itemid import itemidotp
from cmail import sendmail
# from adminotp import adotp
import razorpay
RAZORPAY_KEY_ID='rzp_test_gLbokT3TvelR0s'
RAZORPAY_KEY_SECRET='mnVTVZVVh9kh1f90B3WjKWry'
client=razorpay.Client(auth=(RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET))

import os
mydb=mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='ecom'
)
app=Flask(__name__)
app.secret_key='hfbfe78hjefk'
@app.route('/')
def base():
    return render_template('homepage.html')

@app.route('/adminpage')
def adminpage():
    username=session.get('admin')
    if username:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM signup")
        users = cursor.fetchall()
        return render_template('adminpage.html',username=username,users=users)
    return render_template('adminlogin.html')

@app.route('/adminregister',methods=['GET','POST'])
def adminregister():
    if request.method=="POST":
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        password=request.form['password'] 
        cursor=mydb.cursor()
        cursor.execute('select email from admin')
        data=cursor.fetchall()
        cursor.execute('select mobile from admin')
        edata=cursor.fetchall()
        if(mobile,) in edata:
            flash('User already exist')
            return render_template('adminregister.html')
        if(email,)in data:
            flash('Email address already exists')
            return render_template('adminregister.html')
        cursor.close()
        otp=genotp()
        subject='thanks for registering to the application'
        body=f'use this otp to register {otp}'
        sendmail(email,subject,body)
        return render_template('adminotp.html',otp=otp,name=name,mobile=mobile,email=email,password=password)
    else:
        return render_template('adminregister.html')
    
@app.route('/adminotp/<otp>/<name>/<mobile>/<email>/<password>',methods=['GET','POST'])
def adminotp(otp,name,mobile,email,password):
    if request.method=="POST":
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mydb.cursor()
            lst=[name,mobile,email,password]
            query='insert into admin values(%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mydb.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('adminlogin'))
        else:
            flash('Wrong otp')
            return render_template('adminotp.html',otp=otp,name=name,mobile=mobile,email=email,password=password)
@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        cursor=mydb.cursor()
        cursor.execute('select count(*) from admin where name=%s \
        and password=%s',[username,password])
        count=cursor.fetchone()[0]
        print(count)
        if count==0:
            flash('Invalid email or password')
            return render_template('adminlogin.html')
        else:
            session['admin']=username
            if not session.get(username):
                session[username]={}
            return redirect(url_for('adminpage'))
    return render_template('adminlogin.html')
@app.route('/adminlogout')
def adminlogout():
    if session.get('admin'):
        session.pop('admin')
        return redirect(url_for('adminlogin'))
    else:
        flash('already logged out!')
        return redirect(url_for('adminlogin'))

@app.route('/reg',methods=['GET','POST'])
def register():
    if request.method=="POST":
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        address=request.form['address']
        password=request.form['password'] 
        cursor=mydb.cursor()
        cursor.execute('select email from signup')
        data=cursor.fetchall()
        cursor.execute('select mobile from signup')
        edata=cursor.fetchall()
        if(mobile,) in edata:
            flash('User already exist')
            return render_template('register.html')
        if(email,)in data:
            flash('Email address already exists')
            return render_template('register.html')
        cursor.close()
        otp=genotp()
        subject='thanks for registering to the application'
        body=f'use this otp to register {otp}'
        sendmail(email,subject,body)
        return render_template('otp.html',otp=otp,name=name,mobile=mobile,email=email,address=address,password=password)
    else:
        return render_template('register.html')
@app.route('/otp/<otp>/<name>/<mobile>/<email>/<address>/<password>',methods=['GET','POST'])
def otp(otp,name,mobile,email,address,password):
    if request.method=="POST":
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mydb.cursor()
            lst=[name,mobile,email,address,password]
            query='insert into signup values(%s,%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mydb.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,name=name,mobile=mobile,email=email,address=address,password=password)
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        cursor=mydb.cursor()
        cursor.execute('select count(*) from signup where name=%s \
        and password=%s',[username,password])
        count=cursor.fetchone()[0]
        print(count)
        if count==0:
            flash('Invalid email or password')
            return render_template('login.html')
        else:
            session['user']=username
            if not session.get(username):
                session[username]={}
            return redirect(url_for('base'))
    return render_template('login.html')
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('base'))
    else:
        flash('already logged out!')
        return redirect(url_for('login'))
@app.route('/additems', methods=['GET', 'POST'])
def additems():
    if session.get('admin'):
        if request.method == 'POST':
            name=request.form['name']
            discription=request.form['discription']
            quantity=request.form['qty']
            category=request.form['category']
            price=request.form['price']
            image=request.files['image']
            idotp=itemidotp()
            filename=idotp+'.jpg'
            cursor=mydb.cursor()
            cursor.execute('insert into additems(itemid,name,discription,qty,category,price)\
            values(%s,%s,%s,%s,%s,%s)',[idotp,name,discription,quantity,category,price])
            mydb.commit()
            path=os.path.dirname(os.path.abspath(__file__))
            static_path=os.path.join(path,'static')
            image.save(os.path.join(static_path,filename))
            flash('Item added sucessfuly!')
        return render_template('items.html')
    else:
        flash('admin not in login')
        return redirect(url_for('adminlogin'))
@app.route('/dashboardpage')
def dashboardpage():
    cursor=mydb.cursor()
    cursor.execute('select *from additems')
    items=cursor.fetchall()
    print(items)
    return render_template('dashboard.html',items=items)
@app.route('/status')
def status():
    cursor=mydb.cursor()
    cursor.execute('select *from additems')
    items=cursor.fetchall()
    print(items)
    return render_template('status.html',items=items)
@app.route('/updateproducts/<itemid>',methods=['GET','POST'])
def updateproducts(itemid):
    if session.get('admin'):
        cursor=mydb.cursor()
        cursor.execute('select name,discription,qty,category,price\
                    from additems where itemid=%s',[itemid])
        items=cursor.fetchone()
        cursor.close()
        if request.method == 'POST':
            name=request.form['name']
            discription=request.form['discription']
            quantity=request.form['qty']
            category=request.form['category']
            price=request.form['price']
            cursor=mydb.cursor()
            cursor.execute('update additems set name=%s,discription=%s,qty=%s,category=%s,price=%s where itemid=%s',[name,discription,quantity,category,price,itemid])
            mydb.commit()
            cursor.close()
            return redirect(url_for('adminhome'))
        return render_template('updateproducts.html',items=items)
    else:
        return redirect(url_for('adminlogin'))
@app.route('/deleteproducts/<itemid>')
def deleteproducts(itemid):
    cursor=mydb.cursor()
    cursor.execute('delete from additems where itemid=%s',[itemid])
    mydb.commit()
    cursor.close()
    path=os.path.dirname(os.path.abspath(__file__))
    static_path=os.path.join(path,'static')
    filename=itemid+'.jpg'
    os.remove(os.path.join(static_path,filename))
    flash('Deleted Sucessfully!')
    return redirect(url_for('status'))

# @app.route('/add_to_cart',methods=['POST','GET'])
# def add_to_cart():
#     if request.method=='POST':
#         username=request.form['username']
#         productname=request.form['productname']
#         quantity=request.form['quantity']
#         price=request.form['price']
#         totalprice=int(quantity)*int(price)
#         totalprice=str(totalprice)
#         cursor=mydb.cursor()
#         cursor.execute('insert into cart values(%s,%s,%s,%s,%s)',[username,productname,quantity,price,totalprice])
#         mydb.commit()
#         cursor.close()
#     else:
#         return "Data Occured in incorrect way"

# @app.route('/cartpage',methods=['GET'])
# def cartpage():
#     username=request.args.get('username')
#     cursor=mydb.cursor()
#     cursor.execute('select * from cart where username=%s',(username))
#     data=cursor.fetchall()
#     return render_template('cart.html',data=data)


@app.route('/addcart/<itemid>/<name>/<category>/<price>/<quantity>/',methods=['GET','POST'])
def addcart(itemid, name, category, price, quantity):
    if not session.get('user'):
        return redirect(url_for('login'))
    
    user_cart = session.setdefault(session['user'], {})
    
    if itemid not in user_cart:
        user_cart[itemid] = [name, price, int(quantity), f'{itemid}.jpg', category]
        flash(f'{name} added to cart')
    else:
        user_cart[itemid][2] += int(quantity)
        flash(f'{name} quantity increased in the cart')
    
    session.modified = True
    return '<h2>Item updated in the cart</h2>'

@app.route('/viewcart')
def viewcart():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    
    user_cart=session.get(session.get('user'))
    if not user_cart:
        items='empty'
    else:
        items=user_cart
    if items=='empty':
        return '<h3>Your Cart is empty</h3>'
    return render_template('addcart.html',items=items)

@app.route('/cartpop/<itemid>')
def cartpop(itemid):
    print(itemid)
    if session.get('user'):
        session[session.get('user')].pop(itemid)
        session.modified=True
        flash('item removed')
        return redirect(url_for('viewcart'))
    else:
        return redirect(url_for('login'))


@app.route('/category/<category>',methods=['GET','POST'])
def category():
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select * from additems where category=%s',[category])
        data=cursor.fetchall()
        return render_template('categories.html',data=data)
    else:
        return redirect(url_for('login'))
#itemid,name,price

@app.route('/pay/<itemid>/<name>/<int:price>', methods=['POST','GET'])
def pay(itemid, name, price):

    try:
        # Get the quantity from the form
        qty = request.form['qyt']

        # Calculate the total amount in paise (price is in rupees)
        total_price = int(price) * qty  # Ensure integer multiplication

        print(itemid,total_price,name)
        # print(f"Creating payment for Item ID: {itemid}, Name: {name}, Total Price: {total_price}")
        # Create Razorpay order
        order = client.order.create({
            'amount': total_price,
            'currency': 'INR',
            'payment_capture': '1'
        })

        print(f"Order created: {order}")
        return render_template('pay.html', order=order, itemid=itemid, name=name, price=total_price, qty=qty)
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        return str(e), 400



@app.route('/success',methods=['POST'])

def success():
    if session.get('user'):
        payment_id=request.form.get('razorpay_payment_id')
        order_id=request.form.get('razorpay_order_id')
        signature=request.form.get('razorpay_signature')
        name=request.form.get('name')
        itemid=request.form.get('itemid')
        total_price=request.form.get('total_price')
        qyt=request.form.get('qyt')

        if not qyt or not qyt.isdigit():
            flash('Invalid quantity provided!')
            return 'Invalid Quantity'
        qyt=int(qyt)


        params_dict={
            'razorpay_order_id':order_id,
            'razorpay_payment_id':payment_id,
            'razorpay_signature':signature
        }
        try:
            client.utility.verify_payment_signature(params_dict)
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into orders(itemid,item_name,total_price,user,qty) values(%s,%s,%s,%s,%s)',[itemid,name,total_price,session.get('user'),qyt])
            mydb.commit()
            cursor.close()
            flash('Order Placed Sucessfully')
            return redirect(url_for('orders'))
        except razorpay.errors.SignatureVerificationError:
            return 'Payment verification failed!',400
    else:
        return redirect(url_for('login'))


@app.route('/orders')
def orders():
    if session.get('user'):
        user=session.get('user')
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select * from orders where user=%s',[user])
        data=cursor.fetchall()
        cursor.close()
        return render_template('orderdisplay.html',data=data)
    else:
        return redirect(url_for('login'))
    

@app.route('/search',methods=['GET','POST'])
def search():
    if request.method=='POST':
        name=request.form['search']
        print(name)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select * from additems where name = %s',[name])
        data=cursor.fetchall()
        return render_template('dashboard.html',items=data)
    

@app.route('/contactus.html')
def contactus():
    return render_template('contactus.html')
    

app.run(debug=True,use_reloader=True)