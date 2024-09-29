from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import hashlib



app = Flask(__name__)



def hash_string(input_string):
    # Tạo một đối tượng băm SHA-256
    hash_object = hashlib.sha256()
    
    # Cập nhật đối tượng băm với đầu vào đã được mã hóa thành bytes
    hash_object.update(input_string.encode('utf-8'))
    
    # Trả về giá trị băm dưới dạng chuỗi hex
    return hash_object.hexdigest()
def find_substring(S1, S2):
    M = len(S1)
    N = len(S2)

    # Iterate through S2
    for i in range(N - M + 1):
        
        # Check for substring match
        j = 0
        while j < M and S2[i + j] == S1[j]:
            j += 1
        
        # If we completed the inner loop, we found a match
        if j == M:
            return i

    # No match found
    return -1



app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Hoan3101'
app.config['MYSQL_DB'] = 'geeklogin'



# Configure upload folder
UPLOAD_FOLDER = 'static/uploads/'  # Ensure it's in the static directory
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


mysql = MySQL(app)




@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']  # Change from 'username' to 'email'
        password = request.form['password']
        hashed_pass = hash_string(password)
        print('login', hashed_pass)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s', (email, hashed_pass))  # Use email in the query
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']  # You can still store the username if needed
            session['user_type'] = account['user_type']  # Store user_type in session
            
            # Redirect based on user_type
            if account['user_type'] == 'user':
                return redirect(url_for('index_user'))  # Redirect to user index
            elif account['user_type'] == 'customer':
                return redirect(url_for('index_customer'))  # Redirect to customer index
        else:
            msg = 'Incorrect email / password!'  # Update message to reflect email usage

    return render_template('login.html', msg=msg)


@app.route('/index_user')
@app.route('/index_user')
def index_user():
    if 'loggedin' in session:
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch pets
        cursor.execute('SELECT * FROM pets WHERE user_id = %s', (user_id,))
        pets = cursor.fetchall()

        return render_template('index_user.html', pets=pets)
    return redirect(url_for('login'))


@app.route('/index_customer')
def index_customer():
    if 'loggedin' in session:
        return render_template('index_customer.html')  # Trang cho customer
    return redirect(url_for('login'))



@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'user_type' in request.form:
        username = request.form['username']
        password = request.form['password']
        hashed_pass = hash_string(password)
        print(hashed_pass)
        
        email = request.form['email']
        user_type = request.form['user_type']  # Lấy giá trị user_type từ form

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not user_type:
            msg = 'Please fill out the form!'

        else:
            # Chèn giá trị bao gồm cả user_type vào bảng accounts
            cursor.execute('INSERT INTO accounts (username, password, email, user_type) VALUES (% s, % s, % s, % s)', (username, hashed_pass, email, user_type))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    msg = ''
    if request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        
        if account:

            token = os.urandom(24).hex()
            reset_url = url_for('reset_password', token=token, _external=True)
            

            send_reset_email(email, reset_url)
            msg = 'A password reset link has been sent to your email.'
        else:
            msg = 'Email address is not registered!'
    
    return render_template('forgot_password.html', msg=msg)


def send_reset_email(to_email, reset_url):
    from_email = "your-email@gmail.com"  # Thay bằng email của bạn
    subject = "Password Reset Request"
    
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject

    body = f"Please click the link below to reset your password: {reset_url}"
    message.attach(MIMEText(body, "plain"))

    try:
        # Kết nối đến server SMTP của Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()  # Khởi tạo kết nối
        server.starttls()  # Bắt đầu phiên TLS bảo mật
        server.ehlo()  # Xác nhận lại kết nối sau khi bật TLS

        # Đăng nhập vào Gmail với mật khẩu ứng dụng hoặc mật khẩu thông thường
        email_password = os.getenv("EMAIL_PASSWORD")
        if not email_password:
            raise Exception("EMAIL_PASSWORD environment variable not set.")
        
        server.login(from_email, email_password)  # Thay bằng App Password nếu có
        
        # Gửi email
        text = message.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")  # In lỗi chi tiết


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    msg = ''
    if request.method == 'POST' and 'password' in request.form:
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('UPDATE accounts SET password = %s WHERE reset_token = %s', (password, token))
        mysql.connection.commit()
        msg = 'Your password has been reset successfully!'
    
    return render_template('reset_password.html', msg=msg, token=token)


@app.route('/pets')
def pets_page():
    if 'loggedin' in session:
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pets WHERE user_id = %s', (user_id,))
        pets = cursor.fetchall()
        return render_template('pets.html', pets=pets)
    return redirect(url_for('login'))


@app.route('/add_pet', methods=['POST'])
def add_pet():
    if 'loggedin' in session:
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        pet_age = request.form['pet_age']
        pet_birthday = request.form['pet_birthday']  
        pet_gender = request.form['pet_gender']     
        pet_color = request.form['pet_color']        
        user_id = session['id']

        # Handle the image upload
        pet_image = request.files['pet_image']
        pet_image_filename = pet_image.filename
        pet_image_path = os.path.join(app.config['UPLOAD_FOLDER'], pet_image_filename)
        pet_image.save(pet_image_path)

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO pets (user_id, pet_name, pet_type, pet_age, pet_birthday, pet_gender, pet_color, pet_image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
                       (user_id, pet_name, pet_type, pet_age, pet_birthday, pet_gender, pet_color, pet_image_filename))
        mysql.connection.commit()
        cursor.close()  # Close the cursor
        return redirect(url_for('pets_page'))
    return redirect(url_for('login'))

@app.route('/edit_pet/<int:pet_id>', methods=['GET', 'POST'])
def edit_pet(pet_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if request.method == 'POST':
            pet_name = request.form['pet_name']
            pet_type = request.form['pet_type']
            pet_age = request.form['pet_age']
            pet_birthday = request.form['pet_birthday']
            pet_gender = request.form['pet_gender']
            pet_color = request.form['pet_color']
            pet_image = request.files.get('pet_image')  # Get the uploaded image

            # Prepare the update query
            update_query = '''
                UPDATE pets 
                SET pet_name = %s, pet_type = %s, pet_age = %s, pet_birthday = %s, 
                    pet_gender = %s, pet_color = %s
            '''
            params = [pet_name, pet_type, pet_age, pet_birthday, pet_gender, pet_color]

            if pet_image:  # Check if a new image was uploaded
                pet_image_filename = pet_image.filename
                pet_image_path = os.path.join(app.config['UPLOAD_FOLDER'], pet_image_filename)
                pet_image.save(pet_image_path)  # Save the new image
                update_query += ', pet_image = %s'  # Add image update to query
                params.append(pet_image_filename)

            update_query += ' WHERE id = %s AND user_id = %s'
            params.append(pet_id)
            params.append(session['id'])

            # Execute the update query
            cursor.execute(update_query, params)
            mysql.connection.commit()
            return redirect(url_for('pets_page'))
        else:
            cursor.execute('SELECT * FROM pets WHERE id = %s AND user_id = %s', (pet_id, session['id']))
            pet = cursor.fetchone()
            return render_template('pets.html', editing_pet=pet)  # Update to your actual template
    return redirect(url_for('login'))

@app.route('/delete_pet/<int:pet_id>')
def delete_pet(pet_id):
    print('tao neduma')
    print('pet id', pet_id)
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM pets WHERE id = %s AND user_id = %s', (pet_id, session['id']))
        mysql.connection.commit()
        return redirect(url_for('pets_page'))
    return redirect(url_for('login'))

@app.route('/veterinarian_contact')
def veterinarian_contact():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM veterinarian_contacts WHERE user_id = %s', (session['id'],))
        contacts = cursor.fetchall()
        return render_template('veterinarian_contact.html', contacts=contacts)
    return redirect(url_for('login'))


@app.route('/add_contact', methods=['POST'])
def add_contact():
    if 'loggedin' in session:
        contact_name = request.form['contact_name']
        contact_gender = request.form['contact_gender']  # New field
        contact_language = request.form['contact_language']  # New field
        contact_phone = request.form['contact_phone']
        user_id = session['id']
        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO veterinarian_contacts (user_id, contact_name, contact_gender, contact_language, contact_phone) VALUES (%s, %s, %s, %s, %s)', 
                       (user_id, contact_name, contact_gender, contact_language, contact_phone))
        mysql.connection.commit()
        return redirect(url_for('veterinarian_contact'))
    return redirect(url_for('login'))


@app.route('/edit_contact/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            contact_name = request.form['contact_name']
            contact_gender = request.form['contact_gender']
            contact_language = request.form['contact_language']
            contact_phone = request.form['contact_phone']
            
            cursor.execute('UPDATE veterinarian_contacts SET contact_name = %s, contact_gender = %s, contact_language = %s, contact_phone = %s WHERE id = %s AND user_id = %s', 
                           (contact_name, contact_gender, contact_language, contact_phone, contact_id, session['id']))
            mysql.connection.commit()
            return redirect(url_for('veterinarian_contact'))
        else:
            cursor.execute('SELECT * FROM veterinarian_contacts WHERE id = %s AND user_id = %s', (contact_id, session['id']))
            contact = cursor.fetchone()
            return render_template('veterinarian_contact.html', editing_contact=contact)
    return redirect(url_for('login'))



@app.route('/delete_contact/<int:contact_id>')
def delete_contact(contact_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM veterinarian_contacts WHERE id = %s AND user_id = %s', (contact_id, session['id']))
        mysql.connection.commit()
        return redirect(url_for('veterinarian_contact'))
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True)