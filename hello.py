#Taleed Hamadneh 1220006
#Qasim Batrawi 1220204
#Salah Dawabsheh 1210722

import pymysql
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, DateField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError, EqualTo
from datetime import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager

triptype = 0 # 0 for one way
currentDate = date.today()
currentTime = datetime.now().strftime("%H:%M:%S") 

#one way
from_location = '' #IATA , from for one , to for round
to_location = '' #IATA , to for one, from for round
from_country='' # //
to_country='' # //
departure_date = '2004-1-1' #one way
go_dep_time='00:00:00'
go_arr_time='00:00:00'
flight_number = ""
goflightid=0

#round trip
return_date='2004-1-1' #round
ret_dep_time='00:00:00'
ret_arr_time='00:00:00'
retflightid=0

num_passengers =0
num_Adults=0
num_children=0
filter_flag=0 # if filtered then sorted
selected_price=0.0
selected_duration=0.0
flightPrice=0.0

BigDict={}

myDB = pymysql.connect(host="localhost", user="root", password="120604")
myCursor = myDB.cursor() 

myCursor.execute("use palestinian_airlines")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    
    query = """
        SELECT * FROM User_ u
        WHERE u.user_id = %s
    """
    data = [user_id]
    myCursor.execute(query, data)
    result = myCursor.fetchone()

    if result:
        user_id = result[0]  
        user_firstname = result[1]
        user_lastname = result[2]
        user_dateofbirth = result[3]
        user_email = result[4]
        user_phonenumber = result[5]
        stored_password = result[6]  

        user = User.user_data(id=user_id, firstname=user_firstname, lastname=user_lastname, email=user_email, hashed_password=stored_password, dateofbirth=user_dateofbirth, phonenumber=user_phonenumber)
        
        return user
    
    return None

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

class User(UserMixin):

    def __init__(self, id, firstname, lastname, email, hashed_password, dateofbirth, phonenumber):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.hashed_password = hashed_password
        self.dateofbirth = dateofbirth
        self.phonenumber = phonenumber

    @classmethod
    def user_data(cls, id, firstname, lastname, email, phonenumber, hashed_password, dateofbirth):
        return cls(id, firstname, lastname, email, hashed_password, dateofbirth, phonenumber)
    

class UserForm(FlaskForm):

    Email = StringField(
        "",
        render_kw={"placeholder": "Email: i.e. example@gmail.com"},
        validators=[
            DataRequired(message="Email is required."),
            Regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message="Email must be in the format example@gmail.com.")
        ]
    )

    FirstName = StringField(
        "",
        render_kw={"placeholder": "First Name"},
        validators=[
            DataRequired(message="First name is required."),
            Length(min=2, max=50, message='First name must be between 2 and 50 characters.'),
            Regexp(r'^[A-Za-z]+$', message='First name must contain letters only.')
        ]
    )

    LastName = StringField(
        "",
        render_kw={"placeholder": "Last Name"},
        validators=[
            DataRequired(message="Last name is required."),
            Length(min=2, max=50, message='Last name must be between 2 and 50 characters.'),
            Regexp(r'^[A-Za-z]+$', message='Last name must contain letters only.')
        ]
    )

    PhoneNumber = StringField(
        "",
        render_kw={"placeholder": "Phone Number: i.e. 0595398111"},
        validators=[
            DataRequired(message="Phone number is required."),
            Length(min=10, max=15, message="Phone number must be between 10-15 digits."),
            Regexp(r'^\+?\d{10,15}$', message="Phone number must be between 10 and 15 digits and can optionally start with '+'.")
        ]
    )

    Password = PasswordField(
        "",
        render_kw={"placeholder": "Password"},
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, message="Password must be at least 8 characters long.")
        ]
    )

    ConfirmPassword = PasswordField(
        "",
        render_kw={"placeholder": "Confirm Your Password"},
        validators=[
            DataRequired(message="Password Confirmation is required."),
            EqualTo('Password', message="Passwords must match.")
        ]
    )  
    
    DateOfBirth = DateField(
        "",
        render_kw={"placeholder": "Date Of Birth"},
        validators=[DataRequired('Date of birth is required.')],
    )

    def validate_DateOfBirth(form, field):
        dob = field.data
        today = datetime.now().date()
        eighteen_years_ago = today - timedelta(days=365*18)

        if dob > today:
            raise ValidationError("Invalid date of birth.")
        
        if dob > eighteen_years_ago:
            raise ValidationError("User must be at least 18 years old.")

    Next = SubmitField('SIGN UP')

class UpdateUserForm(FlaskForm):

    FirstName = StringField(
        "First Name",
        render_kw={"placeholder": "First Name"},
        validators=[
            DataRequired(message="First name is required."),
            Length(min=2, max=50, message='First name must be between 2 and 50 characters.'),
            Regexp(r'^[A-Za-z]+$', message='First name must contain letters only.')
        ]
    )

    LastName = StringField(
        "Last Name",
        render_kw={"placeholder": "Last Name"},
        validators=[
            DataRequired(message="Last name is required."),
            Length(min=2, max=50, message='Last name must be between 2 and 50 characters.'),
            Regexp(r'^[A-Za-z]+$', message='Last name must contain letters only.')
        ]
    )

    PhoneNumber = StringField(
        "Phone Number",
        render_kw={"placeholder": "Phone Number: i.e. 0595398111"},
        validators=[
            DataRequired(message="Phone number is required."),
            Length(min=10, max=15, message="Phone number must be between 10-15 digits."),
            Regexp(r'^\+?\d{10,15}$', message="Phone number must be between 10 and 15 digits and can optionally start with '+'.")
        ]
    )

    DateOfBirth = DateField(
        "Birth Date",
        render_kw={"placeholder": "Date Of Birth"},
        validators=[DataRequired('Date of birth is required.')],
    )

    def validate_DateOfBirth(form, field):
        dob = field.data
        today = datetime.now().date()
        eighteen_years_ago = today - timedelta(days=365*18)

        if dob > today:
            raise ValidationError("Invalid date of birth.")
        
        if dob > eighteen_years_ago:
            raise ValidationError("User must be at least 18 years old.")

    Next2 = SubmitField('Update Profile') 

@app.route('/')
def home():

    data = [date.today(), 0]

    query = """
        SELECT
            f.flight_id AS flight_id,
            f.departure_airport_id AS departure_airport_id,
            f.arrival_airport_id AS arrival_airport_id,
            f.price AS price,
            a1.country AS departure_country,
            a2.country AS arrival_country,
            a1.name AS departure_airport_name,
            a2.name AS arrival_airport_name,
            a1.IATA_code AS departure_code,
            a2.IATA_code AS arrival_code,
            f.departure_date AS departure_date  
        FROM
            flight f,
            airport a1,
            airport a2
        WHERE
            f.departure_airport_id = a1.airport_id AND
            f.arrival_airport_id = a2.airport_id AND           
            f.departure_date > %s AND
            f.available_seats > %s
        GROUP BY 
            f.flight_id
        ORDER BY
            f.price
        LIMIT
            4
    """

    myCursor.execute(query, data)
    columns = [column[0] for column in myCursor.description]  # Get column names
    results = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data

    flights = []
    for result in results:
        flight = {
            'price': result['price'],
            'departure_country': result['departure_country'],
            'arrival_country': result['arrival_country'],
            'departure_airport': f"{result['departure_airport_name']} ({result['departure_code']})",
            'arrival_airport': f"{result['arrival_airport_name']} ({result['arrival_code']})",
            'departure_date': result['departure_date']
        }
        flights.append(flight)
    
    return render_template('index.html', user=current_user, flight1=flights[0], flight2=flights[1], flight3=flights[2], flight4=flights[3], today=date.today())

#*********************************************************TALEED********************************************************

@app.route('/search-flights', methods=['POST'])
def search_flights():
    # Get data from the form
    global flight_number, flightPrice, from_location, to_location, departure_date, return_date ,num_passengers
    global from_country,to_country,num_children,num_Adults,currentDate, currentTime, goflightid,triptype
    
    triptype = request.form['tripType']

    if triptype == "oneWay":
        triptype = 0
    else:
        triptype = 1
        
    from_location = request.form['fromLocation'] #airport name
    #split to IATA 
    from_location = from_location.split('(')[-1].strip(')')

    to_location = request.form['toLocation'] #airport name
    #split to IATA
    to_location = to_location.split('(')[-1].strip(')')

    departure_date = request.form['departureDate']
    
    

    return_date = request.form.get('returnDate')  # Using .get() to avoid error if returnDate is not there
    
    if(request.form['NumofChildren']==''):
        num_children=0
    else:
        num_children=int(request.form['NumofChildren'])
        
    num_Adults = int(request.form['NumofAdults'])
    num_passengers = num_Adults + num_children

    flights = show_flights(from_location,to_location,departure_date,return_date) 

    # Calculate the total price for each flight based on the number of passengers and store the informations
    for flight in flights:
        flightPrice = flight['total_price'] * num_passengers
        flight['total_price'] = flight['total_price'] * num_passengers
        from_country= flight['Go_Departure_Country']
        to_country= flight['Go_Arrival_Country']
        goflightid=flight['Goflightid']
          
    return render_template('flights.html', flights=flights) 


def show_flights(from_location, to_location, departure_date, return_date=None): #return date = none because its optional, in one way none, in round value
    
    global triptype,currentDate,currentTime,num_passengers
   
    if(triptype==0): #one way trips
        query = """
        SELECT 
        Goflight.flight_id as Goflightid,
        GoFlight.flight_number as GoFlight, 
        GoArr.country AS Go_Arrival_Country, 
        GoDep.country AS Go_Departure_Country, 
        Go.model AS Go_Airplane_model, 
        GoFlight.price as total_price, 
        GoFlight.flight_duration as Go_Duration,
        GoFlight.departure_date as Go_Dep_date, 
        GoFlight.departure_time as Go_dep_time,
        GoFlight.arrival_date as Go_Arr_date , 
        GoFlight.arrival_time As Go_arr_time
    FROM 
        Flight GoFlight, Airport GoDep, Airport  GoArr, Airplane Go
            WHERE 
                GoFlight.departure_airport_id = GoDep.airport_id 
                AND GoFlight.arrival_airport_id =  GoArr.airport_id
                and Go.airplane_id = GoFlight.airplane_id and
                GoDep.IATA_code = %s and  GoArr.IATA_code = %s and GoFlight.departure_date = %s
                and GoFlight.available_seats >= %s 
                and  
                (GoFlight.departure_date > %s or ( GoFlight.departure_date = %s and GoFlight.departure_time > %s ) )
              
        """
        data = [from_location, to_location, departure_date, num_passengers, currentDate, currentDate,currentTime]

        myCursor.execute(query, data) #execute the query
        # Convert the result to a list of dictionaries
        columns = [column[0] for column in myCursor.description]  # Get column names
        result = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data
        
        return result  # Return the result as a list of dictionaries
    

    elif( triptype==1) : #round trip flights
         triptype = 1
         query = """  
        SELECT 
        Goflight.flight_id as Goflightid,
		GoFlight.flight_number as GoFlight,
        GoDep.country as Go_Departure_Country,
        GoArr. country as Go_Arrival_Country,
		GoFlight.flight_duration as Go_Duration,
        GoFlight.departure_date as Go_Dep_date, 
        GoFlight.arrival_date as Go_Arr_date,
        GoFlight.departure_time As Go_dep_time,
        GoFlight.arrival_time As Go_arr_time,

        ReturnFlight.flight_id as Retflightid,
		ReturnFlight.flight_number as ReturnFlight, 
        RetDep.country AS Ret_Departure_Country, 
		RetArr.country AS Ret_Arrival_Country, 
        ReturnFlight.flight_duration as Ret_Duration,
        ReturnFlight.departure_date as Ret_Dep_date, 
        ReturnFlight.arrival_date as Ret_Arr_date ,
        ReturnFlight.departure_time As Ret_dep_time,
        ReturnFlight.arrival_time As Ret_arr_time,
        
		Ret.model AS Ret_Airplane_model,    
		Go.model AS Go_Airplane_model,
        ReturnFlight.price + GoFlight.price as total_price 
        FROM 
        flight ReturnFlight, flight GoFlight , Airport RetDep, Airport RetArr, Airport GoArr, Airport GoDep, Airplane Ret, Airplane Go
            WHERE 
                ReturnFlight.departure_airport_id = RetDep.airport_id 
                AND ReturnFlight.arrival_airport_id = RetArr.airport_id
                and GoFlight.departure_airport_id = GoDep.airport_id
                and GoFlight.arrival_airport_id = GoArr.airport_id
                
                and Ret.airplane_id = ReturnFlight.airplane_id and
                Go.airplane_id = GoFlight.airplane_id and
                ReturnFlight.departure_airport_id = GoFlight.arrival_airport_id
                and
                ReturnFlight.arrival_airport_id = GoFlight.departure_airport_id
                and
                ReturnFlight.departure_date > GoFlight.departure_date
                and 
                ReturnFlight.arrival_date > GoFlight.arrival_date and

                GoDep.IATA_code = %s and GoArr.IATA_code = %s and GoFlight.departure_date = %s 
                and RetDep.IATA_code = %s and RetArr.IATA_code = %s and ReturnFlight.departure_date = %s
                and GoFlight.available_seats >= %s 
                and  
                (GoFlight.departure_date > %s or ( GoFlight.departure_date = %s and GoFlight.departure_time > %s ) )
               
        """

         data = [from_location, to_location, departure_date, to_location, from_location , return_date, num_passengers, currentDate,currentDate, currentTime]
         myCursor.execute(query, data) #execute the query
         # Convert the result to a list of dictionaries
         columns = [column[0] for column in myCursor.description]  # Get column names
         result = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data
         return result  # Return the result as a list of dictionaries

@app.route('/sort-flights', methods=['POST'])
def sort_flights():
        global from_location, to_location, departure_date, return_date, triptype,num_passengers,filter_flag,selected_price,selected_duration,currentDate,currentTime
        sort_by = request.form.get('sortBy')  # Capture the sorting option

        if(triptype==0):
                query = """
                SELECT 
                Goflight.flight_id as Goflightid,
                GoFlight.flight_number as GoFlight, 
                GoArr.country AS Go_Arrival_Country, 
                GoDep.country AS Go_Departure_Country, 
                Go.model AS Go_Airplane_model, 
                GoFlight.price as total_price, 
                GoFlight.flight_duration as Go_Duration,
                GoFlight.departure_date as Go_Dep_date, 
                GoFlight.departure_time as Go_dep_time,
                GoFlight.arrival_date as Go_Arr_date , 
                GoFlight.arrival_time As Go_arr_time
            FROM 
                Flight GoFlight, Airport GoDep, Airport  GoArr, Airplane Go
                    WHERE 
                        GoFlight.departure_airport_id = GoDep.airport_id 
                        AND GoFlight.arrival_airport_id =  GoArr.airport_id
                        and Go.airplane_id = GoFlight.airplane_id and
                        GoDep.IATA_code = %s and  GoArr.IATA_code = %s and GoFlight.departure_date = %s
                        and GoFlight.available_seats >= %s 
                      and  
                (GoFlight.departure_date > %s or ( GoFlight.departure_date = %s and GoFlight.departure_time > %s ) )

                """
                if(filter_flag==1): #if filterd=> sort only the filtered flightes
                    query+=f"and (GoFlight.price * {num_passengers} ) >= {selected_price}"
                    query+=f"and (TIME_TO_SEC(GoFlight.flight_duration) / 3600) >= {selected_duration}" #1:30:000 > 5.0   
                       
                if sort_by == 'duration':
                    query += " ORDER BY GoFlight.flight_duration"
                elif sort_by == 'price':
                   query += f" ORDER BY (GoFlight.price * {num_passengers})"
                elif sort_by == 'departure':
                    query += " ORDER BY GoFlight.departure_time"
                elif sort_by == 'arrival':
                    query += " ORDER BY GoFlight.arrival_time"
                    
                data = [from_location, to_location, departure_date, num_passengers, currentDate, currentDate , currentTime]
            
                myCursor.execute(query, data) #execute the query
                # Convert the result to a list of dictionaries
                columns = [column[0] for column in myCursor.description]  # Get column names
                result = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data
                for flight in result:
                    flight['total_price'] = flight['total_price'] * num_passengers
                    
                
                return render_template('flights.html', flights=result)

        
        elif(triptype==1):
            query = """  
                SELECT 

                Goflight.flight_id as Goflightid,
                GoFlight.flight_number as GoFlight,
                GoDep.country as Go_Departure_Country,
                GoArr. country as Go_Arrival_Country,
                GoFlight.flight_duration as Go_Duration,
                GoFlight.departure_date as Go_Dep_date, 
                GoFlight.arrival_date as Go_Arr_date,
                GoFlight.departure_time As Go_dep_time,
                GoFlight.arrival_time As Go_arr_time,

                ReturnFlight.flight_id as Retflightid,
	        	ReturnFlight.flight_number as ReturnFlight,
                RetDep.country AS Ret_Departure_Country, 
                RetArr.country AS Ret_Arrival_Country, 
                ReturnFlight.flight_duration as Ret_Duration,
                ReturnFlight.departure_date as Ret_Dep_date, 
                ReturnFlight.arrival_date as Ret_Arr_date ,
                ReturnFlight.departure_time As Ret_dep_time,
                ReturnFlight.arrival_time As Ret_arr_time,
                
                Ret.model AS Ret_Airplane_model,    
                Go.model AS Go_Airplane_model,
                ReturnFlight.price + GoFlight.price as total_price 
                FROM 
                flight ReturnFlight, flight GoFlight , Airport RetDep, Airport RetArr, Airport GoArr, Airport GoDep, Airplane Ret, Airplane Go
                    WHERE 
                        ReturnFlight.departure_airport_id = RetDep.airport_id 
                        AND ReturnFlight.arrival_airport_id = RetArr.airport_id
                        and GoFlight.departure_airport_id = GoDep.airport_id
                        and GoFlight.arrival_airport_id = GoArr.airport_id
                        
                        and Ret.airplane_id = ReturnFlight.airplane_id and
                        Go.airplane_id = GoFlight.airplane_id and
                        ReturnFlight.departure_airport_id = GoFlight.arrival_airport_id
                        and
                        ReturnFlight.arrival_airport_id = GoFlight.departure_airport_id
                        and
                        ReturnFlight.departure_date > GoFlight.departure_date
                        and 
                        ReturnFlight.arrival_date > GoFlight.arrival_date and

                        GoDep.IATA_code = %s and GoArr.IATA_code = %s and GoFlight.departure_date = %s 
                        and RetDep.IATA_code = %s and RetArr.IATA_code = %s and ReturnFlight.departure_date = %s
                        and GoFlight.available_seats >= %s
                        and  
                         (GoFlight.departure_date > %s or ( GoFlight.departure_date = %s and GoFlight.departure_time > %s ) )
              
              
        """
            if(filter_flag==1):#if filtered=> sort only the filtered flights
                query+=f"and ( (GoFlight.price + ReturnFlight.price) * {num_passengers} ) >= {selected_price}"
                query+=f"and (TIME_TO_SEC(GoFlight.flight_duration) / 3600) >= {selected_duration}" #1:30:000 > 5.0
                query+=f"and (TIME_TO_SEC(ReturnFlight.flight_duration) / 3600) >= {selected_duration}" #1:30:000 > 5.0           
            if sort_by == 'duration':
                query += " ORDER BY GoFlight.flight_duration, ReturnFlight.flight_duration"
            elif sort_by == 'price':
                query += f" ORDER BY (total_price * {num_passengers})"
            elif sort_by == 'departure':
                query += " ORDER BY GoFlight.departure_time, ReturnFlight.departure_time"
            elif sort_by == 'arrival':
                query += " ORDER BY GoFlight.arrival_time, ReturnFlight.arrival_time"
            
            data = [from_location, to_location, departure_date, to_location, from_location , return_date,num_passengers,currentDate, currentDate ,currentTime]
            myCursor.execute(query, data) #execute the query
            # Convert the result to a list of dictionaries
            columns = [column[0] for column in myCursor.description]  # Get column names
            result = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data
            
            for flight in result:
              flight['total_price'] = flight['total_price'] * num_passengers
              
 
            return render_template('flights.html', flights=result )


@app.route('/filter-flights', methods=['POST'])
def filter_flights():
    global from_location, to_location, departure_date, return_date, triptype,num_passengers,filter_flag,selected_price,selected_duration
    selected_price = float(request.form.get('price', 0))
    selected_duration = float(request.form.get('duration', 0))
    filter_flag=1
    if(triptype==0):
        query = """
                SELECT 
                Goflight.flight_id as Goflightid,
                GoFlight.flight_number as GoFlight, 
                GoArr.country AS Go_Arrival_Country, 
                GoDep.country AS Go_Departure_Country, 
                Go.model AS Go_Airplane_model, 
                GoFlight.price as total_price, 
                GoFlight.flight_duration as Go_Duration,
                GoFlight.departure_date as Go_Dep_date, 
                GoFlight.departure_time as Go_dep_time,
                GoFlight.arrival_date as Go_Arr_date , 
                GoFlight.arrival_time As Go_arr_time
            FROM 
                Flight GoFlight, Airport GoDep, Airport  GoArr, Airplane Go
                    WHERE 
                        GoFlight.departure_airport_id = GoDep.airport_id 
                        AND GoFlight.arrival_airport_id =  GoArr.airport_id
                        and Go.airplane_id = GoFlight.airplane_id and
                        GoDep.IATA_code = %s and  GoArr.IATA_code = %s and GoFlight.departure_date = %s
                         and GoFlight.available_seats >= %s
                         and  
                (GoFlight.departure_date > %s or ( GoFlight.departure_date = %s and GoFlight.departure_time > %s ) )
              
              
                """
        query+=f"and (GoFlight.price * {num_passengers} ) >= {selected_price}"
        query+=f"and (TIME_TO_SEC(GoFlight.flight_duration) / 3600) >= {selected_duration}" #1:30:000 > 5.0
        data = [from_location, to_location, departure_date,num_passengers,currentDate,currentDate,currentTime]
            
        myCursor.execute(query, data) #execute the query
        # Convert the result to a list of dictionaries
        columns = [column[0] for column in myCursor.description]  # Get column names
        result = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data
        for flight in result:
            flight['total_price'] = flight['total_price'] * num_passengers
            
        
        return render_template('flights.html', flights=result)
    
    elif(triptype==1):
            query = """  
                SELECT 
                Goflight.flight_id as Goflightid,
                GoFlight.flight_number as GoFlight,
                GoDep.country as Go_Departure_Country,
                GoArr. country as Go_Arrival_Country,
                GoFlight.flight_duration as Go_Duration,
                GoFlight.departure_date as Go_Dep_date, 
                GoFlight.arrival_date as Go_Arr_date,
                GoFlight.departure_time As Go_dep_time,
                GoFlight.arrival_time As Go_arr_time,

                ReturnFlight.flight_id as Retflightid,
                ReturnFlight.flight_number as ReturnFlight, 
                RetDep.country AS Ret_Departure_Country, 
                RetArr.country AS Ret_Arrival_Country, 
                ReturnFlight.flight_duration as Ret_Duration,
                ReturnFlight.departure_date as Ret_Dep_date, 
                ReturnFlight.arrival_date as Ret_Arr_date ,
                ReturnFlight.departure_time As Ret_dep_time,
                ReturnFlight.arrival_time As Ret_arr_time,
                
                Ret.model AS Ret_Airplane_model,    
                Go.model AS Go_Airplane_model,
                ReturnFlight.price + GoFlight.price as total_price 
                FROM 
                flight ReturnFlight, flight GoFlight , Airport RetDep, Airport RetArr, Airport GoArr, Airport GoDep, Airplane Ret, Airplane Go
                    WHERE 
                        ReturnFlight.departure_airport_id = RetDep.airport_id 
                        AND ReturnFlight.arrival_airport_id = RetArr.airport_id
                        and GoFlight.departure_airport_id = GoDep.airport_id
                        and GoFlight.arrival_airport_id = GoArr.airport_id
                        
                        and Ret.airplane_id = ReturnFlight.airplane_id and
                        Go.airplane_id = GoFlight.airplane_id and
                        ReturnFlight.departure_airport_id = GoFlight.arrival_airport_id
                        and
                        ReturnFlight.arrival_airport_id = GoFlight.departure_airport_id
                        and
                        ReturnFlight.departure_date > GoFlight.departure_date
                        and 
                        ReturnFlight.arrival_date > GoFlight.arrival_date and

                        GoDep.IATA_code = %s and GoArr.IATA_code = %s and GoFlight.departure_date = %s 
                        and RetDep.IATA_code = %s and RetArr.IATA_code = %s and ReturnFlight.departure_date = %s
                         and GoFlight.available_seats >= %s 
                         and  
                (GoFlight.departure_date > %s or ( GoFlight.departure_date = %s and GoFlight.departure_time > %s ) )
              
              
        """
            query+=f"and ( (GoFlight.price + ReturnFlight.price) * {num_passengers} ) >= {selected_price}"
            query+=f"and (TIME_TO_SEC(GoFlight.flight_duration) / 3600) >= {selected_duration}" #1:30:000 > 5.0
            query+=f"and (TIME_TO_SEC(ReturnFlight.flight_duration) / 3600) >= {selected_duration}" #1:30:000 > 5.0
            data = [from_location, to_location, departure_date, to_location, from_location , return_date,num_passengers,currentDate,currentDate,currentTime]
                
            myCursor.execute(query, data) #execute the query
            # Convert the result to a list of dictionaries
            columns = [column[0] for column in myCursor.description]  # Get column names
            result = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data
            for flight in result:
                flight['total_price'] = flight['total_price'] * num_passengers
    
            return render_template('flights.html', flights=result)         
        
@app.route('/check-status', methods=['POST'])
def check_status():
    global currentDate,currentTime
    flight_number = request.form.get('flightNumber')  # Get form data

    query="""
        select f.departure_date , f.departure_time, GoDep.country as depcountry, GoArr.country as arrcountry, f.arrival_time
        from flight f, Airport GoDep, Airport  GoArr
        where 
        f.departure_airport_id = GoDep.airport_id 
        AND f.arrival_airport_id =  GoArr.airport_id
        and
        f.flight_number = %s;
    
    """
    data = [flight_number]
        
    myCursor.execute(query, data) #execute the query    
    columns = [column[0] for column in myCursor.description]  # Get column names
    flight = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data
    
    status_message = ""
    if not flight: 
        status_message = "Flight not found. Please check the flight number and try again."
        return status_message

    departure_date = flight[0]['departure_date']
    departure_time = flight[0]['departure_time']
    depcountry = flight[0]['depcountry']
    arrcountry = flight[0]['arrcountry']
    arrival_time = flight[0]['arrival_time']
    
    time_parts = currentTime.split(":")
    current_hours = int(time_parts[0])
    current_minutes = int(time_parts[1])
    current_seconds = int(time_parts[2])

    # Calculate total seconds for currentTime
    current_time_seconds = current_hours * 3600 + current_minutes * 60 + current_seconds

    #calculate seconds for departure and arrival time
    departure_time_seconds = int(departure_time.total_seconds())
    arrival_time_seconds = int(arrival_time.total_seconds())
     
    if departure_date > currentDate:
        status_message = f"The flight will depart from {depcountry} to {arrcountry} on {departure_date} at {departure_time}."
    elif currentDate == departure_date:
        if current_time_seconds > departure_time_seconds and current_time_seconds < arrival_time_seconds:
            status_message = f"The flight is currently in the air from {depcountry} to {arrcountry}. It will arrive at {arrival_time}."
        elif current_time_seconds > arrival_time_seconds:
            status_message = f"The flight has landed today in {arrcountry} at {arrival_time}."
        else:
            status_message = f"The flight will depart from {depcountry} to {arrcountry} today at {departure_time} ."
    else:
        status_message = f"The flight has already departed  from {depcountry} on {departure_date} at {departure_time} to {arrcountry} and arrived on {arrcountry} at {arrival_time}."

    return status_message 

@app.route('/sign_up', methods=['Get','POST'])
def sign_up():

    form = UserForm()

    if form.validate_on_submit():
        first_name = form.FirstName.data
        last_name = form.LastName.data
        email = form.Email.data.lower()
        date_of_birth = form.DateOfBirth.data
        phone_number = form.PhoneNumber.data
        password = generate_password_hash(form.Password.data)

        data = [email]
        query = """
            SELECT * FROM USER_ u
            WHERE u.email = %s
        """
        myCursor.execute(query, data)
        result = myCursor.fetchall()

        if not result:

            data = [first_name, last_name, email, phone_number, date_of_birth, password]
            query = """
                INSERT INTO User_(first_name, last_name, email, phone_number, date_of_birth, hashed_password) VALUES 
                (%s, %s, %s, %s, %s, %s);
            """
            myCursor.execute(query, data)
            myDB.commit()

            flash('You Have Signed Up Succesfully! You Can Sign In To Your Account Now.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Sign Up Failed. The Email {email} Is In Use.', 'danger')
            return render_template('login.html', form=form)

    elif request.method == 'POST':
        flash('Sign Up Failed. Invalid Information', 'danger')
        return render_template('login.html', form=form)

@app.route('/login', methods=['Get','POST'])
def login():

    form = UserForm()

    if request.method == 'POST':
        # Get the data from the form
        email = request.form.get('email')
        password = request.form.get('password')
        query="""
            select u.hashed_password from User_ u
            where u.email like %s
        """
        data=[email]
        myCursor.execute(query,data)
        # Convert the result to a list of dictionaries
        columns = [column[0] for column in myCursor.description]  # Get column names
        result = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data
        
        if not result:
            error="incorrect email.. try again"
            return render_template('login.html', error=error, form=form)
        
        else:
            myCursor.execute(query,data)
            # Convert the result to a list of dictionaries
            columns = [column[0] for column in myCursor.description]  # Get column names
            result = myCursor.fetchone()  # Combine column names with row data

            if not result:
                error="incorrect Password.. try again"
                return render_template('login.html', error=error, form=form)
            
            stored_hashed_password = result[0]

            # Check the entered password against the stored hash
            if not check_password_hash(stored_hashed_password, password):
                error = "Incorrect password. Try again."
                return render_template('login.html', error=error, form=form)
        

        query="""
            select * from User_ u
            where u.email like %s
        """
        data=[email]
        myCursor.execute(query,data)
        result = myCursor.fetchone()

        user_id = result[0]
        user_firstname = result[1]
        user_lastname = result[2]
        user_dateofbirth = result[3]
        user_email = result[4]
        user_phonenumber = result[5]
        user_hashedpassword = result[6]
        
        user = User.user_data(id=user_id, dateofbirth=user_dateofbirth, firstname=user_firstname, lastname=user_lastname, hashed_password=user_hashedpassword, email=user_email, phonenumber=user_phonenumber)
        login_user(user)

        return redirect('/')
    
    return render_template('login.html', form=form)

@app.route('/profile')
@login_required
def profile():
    query=" select * from User_ u where u.email=%s"
    email=current_user.email
    data=email
    myCursor.execute(query,data)
    # Convert the result to a list of dictionaries
    columns = [column[0] for column in myCursor.description]  # Get column names
    result = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data
    for user in result:
        firstname=user['first_name']
        lastname=user['last_name']
        birthdate=user['date_of_birth']
        phone=user['phone_number']

    message = request.args.get('message', '')
    return render_template('profile.html', firstname=firstname,lastname=lastname,birthdate=birthdate,phone=phone, email=email,message=message)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form = UpdateUserForm()

    if form.validate_on_submit():

        firstname = form.FirstName.data
        lastname = form.LastName.data
        birthdate = form.DateOfBirth.data
        phone = form.PhoneNumber.data

        query = "UPDATE User_ SET "
        data = []
        if firstname:
                query += "first_name=%s "
                data.append(firstname)
        if lastname:
                query += ",last_name=%s "
                data.append(lastname)
        if birthdate:
            query += ",date_of_birth=%s "
            data.append(birthdate)
        if phone:
            query += ",phone_number=%s "
            data.append(phone)
            
        query += " WHERE email=%s"
        data.append(current_user.email)
        myCursor.execute(query, tuple(data))
        myDB.commit()
        return redirect(url_for('profile', message="Your profile has been updated successfully!"))
     
    query = "SELECT * FROM User_ WHERE email=%s"
    data = [current_user.email]
    myCursor.execute(query, data)
    columns = [column[0] for column in myCursor.description]  # Get column names
    result = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data

    for user in result:
        firstname=user['first_name']
        lastname=user['last_name']
        birthdate=user['date_of_birth']
        phone=user['phone_number']
    return render_template('edit_profile.html', firstname=firstname,lastname=lastname,birthdate=birthdate,phone=phone,form=form)


@app.route('/Taleedqueries', methods=['GET', 'POST'])
def AvgPrice():
    result = []
    start_date = None
    end_date = None
    error = None
    no_data_message = None  # New variable to store "no data" message

    if request.method == 'POST':
        # Get start_date and end_date from the form
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')


        # Validate dates
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            error = "Invalid date format. Please use YYYY-MM-DD."
            return render_template('all_queries.html', result=result, error=error)

        # Database query
        Tquery1 = """
        SELECT 
            COUNT(p.passenger_ssn) AS passenger_count, 
            arr.country AS arr_country, 
            dep.country AS dep_country
        FROM 
            Passenger p, 
            airport dep, 
            airport arr, 
            flight f, 
            Passenger_Flight_Booking pfb
        WHERE 
            f.flight_id = pfb.flight_id
            AND f.arrival_airport_id = arr.airport_id
            AND f.departure_airport_id = dep.airport_id
            AND p.passenger_ssn = pfb.passenger_ssn
            AND f.departure_date >= %s
            AND f.arrival_date <= %s
        GROUP BY 
            f.departure_airport_id, f.arrival_airport_id
        HAVING 
            AVG(f.price) > (SELECT AVG(price) FROM Flight);
        """

        myCursor.execute(Tquery1, (start_date, end_date))

        columns = [column[0] for column in myCursor.description]  # Get column names
        result = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data
        
        if not result:  # If the result is empty, set the message
            no_data_message = "No passengers in this period."


    # Render the HTML template
    return render_template(
        'all_queries.html', 
        result=result, 
        error=error, 
        start_date=start_date, 
        end_date=end_date,
        no_data_message=no_data_message,  # Pass the no_data_message to the template]

    )
    
@app.route('/Taleedqueries2', methods=['GET', 'POST'])
def NeverFlownTo():
    country = None
    result = []
    message2=None
    error = None
    
    if request.method == 'POST':
        country = request.form.get('country')

        if not country:
            error = "Please select a country."
            return render_template('all_queries.html', result=result, error=error)
        
        Tquery2 = """
        SELECT count(p.passenger_ssn) AS passenger_count
        FROM Passenger p
        WHERE p.passenger_ssn IN (
            SELECT pfb.passenger_ssn
            FROM Passenger_Flight_Booking pfb, flight f
            WHERE f.flight_id = pfb.flight_id
            GROUP BY pfb.passenger_ssn
            HAVING COUNT(pfb.flight_id) > 2
        )
        AND p.passenger_ssn NOT IN (
            SELECT pf.passenger_ssn
            FROM Passenger_Flight_Booking pf, flight f2, airport a
            WHERE f2.flight_id = pf.flight_id
            AND f2.arrival_airport_id = a.airport_id
            AND a.country = %s
        );
        """
        data2=[country]
        myCursor.execute(Tquery2, data2)
        columns = [column[0] for column in myCursor.description]  # Get column names
        result2 = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data

        if not result2:  # If the result is empty, set the message
            message2 = "No passengers found for this country in the first query."
    

    return render_template(
        'all_queries.html', 
        country=country,
        result2=result2,
        message2=message2)
    
    
@app.route('/Taleedquery3', methods=['GET', 'POST'])
def popular_flight_routes():
    result3 = []
    message3 = None

    Tquery3 = """
    SELECT 
        COUNT(*) AS flightCount, 
        dep.country AS depCountry, 
        arr.country AS arrCountry
    FROM 
        Airport dep, 
        Airport arr, 
        Flight f
    WHERE 
        f.arrival_airport_id = arr.airport_id
        AND f.departure_airport_id = dep.airport_id
    GROUP BY 
        dep.country, arr.country
    HAVING COUNT(*) = (
            SELECT MAX(flightCount) 
            FROM (
                SELECT COUNT(*) AS flightCount
                FROM 
                    Airport dep, 
                    Airport arr, 
                    Flight f
                WHERE 
                    f.arrival_airport_id = arr.airport_id
                    AND f.departure_airport_id = dep.airport_id
                GROUP BY 
                    dep.country, arr.country
            ) AS routeCounts
        );
    """
    myCursor.execute(Tquery3)
    columns = [column[0] for column in myCursor.description]  # Get column names
    result3 = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data

    if not result3:  # If the result is empty, set the message
        message3 = "No popular flight routes found."

    return render_template('all_queries.html', result3=result3, message3=message3)  

#*********************************************************************Qasim****************************************************************************************                 
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html' , error=404) , 404

@app.errorhandler(405)
def page_not_found(e):
    return render_template('error.html' , error=405) , 405

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html' , error=500) , 500

class PassengerForm(FlaskForm):
    Gender = RadioField(
        'Gender', 
        choices=[('Male', 'Male'), ('Female', 'Female')], 
        validators=[DataRequired('Gender selection is required.')],
    )

    SSN = StringField(
        "SSN",
        validators=[
            DataRequired(message="SSN is required."),
            Length(min=9, max=9, message='SSN must be 9 digits.'),
            Regexp(r'^\d+$', message='SSN must contain digits only.')
        ]
    )
    
    FirstName = StringField(
        "First Name",
        validators=[
            DataRequired(message="First name is required."),
            Length(min=2, max=50, message='First name must be between 2 and 50 characters.'),
            Regexp(r'^[A-Za-z]+$', message='First name must contain letters only.')
        ]
    )

    LastName = StringField(
        "Last Name",
        validators=[
            DataRequired(message="Last name is required."),
            Length(min=2, max=50, message='Last name must be between 2 and 50 characters.'),
            Regexp(r'^[A-Za-z]+$', message='Last name must contain letters only.')
        ]
    )
    
    DateOfBirth = DateField(
        "Date of birth",
        validators=[DataRequired('Date of birth is required.')],
    )

    def validate_DateOfBirth(form, field):
        dob = field.data
        today = datetime.now().date()
        twilve_years_ago = today - timedelta(days=365*12)

        if dob > today:
            raise ValidationError("Invalid date of birth.")
        
        if BigDict['PassengersDetails']['CounterForPassengers'] > BigDict['PassengersDetails']['NumberOfAdults']:
            if dob <= twilve_years_ago:
                raise ValidationError("Children must be less than 12 years old.")
        else:
            if dob > twilve_years_ago:
                raise ValidationError("Adults must be 12 years or older.")

    Nationality = SelectField(
        'Nationality',
        choices = [
            ('', 'Choose a nationality'),
            ('Palestinian', 'Palestinian'),
            ('Bahraini', 'Bahraini'),
            ('Cypriot', 'Cypriot'),
            ('Egyptian', 'Egyptian'),
            ('Iranian', 'Iranian'),
            ('Iraqi', 'Iraqi'),
            ('Jordanian', 'Jordanian'),
            ('Kuwaiti', 'Kuwaiti'),
            ('Lebanese', 'Lebanese'),
            ('Omani', 'Omani'),
            ('Qatari', 'Qatari'),
            ('Saudi', 'Saudi'),
            ('Syrian', 'Syrian'),
            ('Turkish', 'Turkish'),
            ('Emirati', 'Emirati'),
            ('Yemeni', 'Yemeni'),
        ],
    )

    def validate_Nationality(form, field):
        if field.data == '':
            raise ValidationError("Nationality is required.")

    Next = SubmitField('Next')

class PassengerForm2(FlaskForm):

    FirstName = StringField(
        "First Name",
        validators=[
            DataRequired(message="First name is required."),
            Length(min=2, max=50, message='First name must be between 2 and 50 characters.'),
            Regexp(r'^[A-Za-z]+$', message='First name must contain letters only.')
        ]
    )

    LastName = StringField(
        "Last Name",
        validators=[
            DataRequired(message="Last name is required."),
            Length(min=2, max=50, message='Last name must be between 2 and 50 characters.'),
            Regexp(r'^[A-Za-z]+$', message='Last name must contain letters only.')
        ]
    )
    
    DateOfBirth = DateField(
        "Date of birth",
        validators=[DataRequired('Date of birth is required.')],
    )

    def validate_DateOfBirth(form, field):
        dob = field.data
        today = datetime.now().date()

        if dob > today:
            raise ValidationError("Invalid date of birth.")

    Submit = SubmitField('Save Changes')

@app.route('/flightdetails')
@login_required
def flight_details():
    global flightPrice, go_dep_time, go_arr_time, ret_dep_time, ret_arr_time, retflightid, goflightid
    go_dep_time = request.args.get('go_dep_time')
    go_arr_time = request.args.get('go_arr_time')
    ret_dep_time = request.args.get('ret_dep_time')
    ret_arr_time = request.args.get('ret_arr_time')
    flightPrice = float(request.args.get('flight_price'))
    goflightid = int(request.args.get('go_flight_id'))
    if triptype == 1:
        retflightid = int(request.args.get('ret_flight_id'))

    BigDict['PassengersDetails'] = {
        'CounterForPassengers' : 1,
        'NumberOfPassengers' : num_passengers,
        'NumberOfAdults' : num_Adults,
        'NumberOfInfant' : num_children,
        'Passengers' : [{} for i in range(num_passengers)],
    }

    BigDict['TripDetails'] = {
        "OneWay" : triptype, # if 1 then one way, if 0 then round trip
        "Departure Details" : {
            "Date" : departure_date,
            "From" : from_country,
            "To" : to_country,
            "Departure Airport" : from_location,
            "Arrival Airport" : to_location,
            "Departure Time" : go_dep_time,
            "Arrival Time" : go_arr_time,
        },
        "Return Details" : {
            "Date" : return_date,
            "From" : to_country,
            "To" : from_country,
            "Departure Airport" : to_location,
            "Arrival Airport" : from_location,
            "Departure Time" : ret_dep_time,
            "Arrival Time" : ret_arr_time,
        }
    }

    BigDict['UserDetails'] = {
        "FirstName" : current_user.firstname,
        "LastName" : current_user.lastname,
        "Email" : current_user.email,
        "PhoneNumber" : current_user.phonenumber
    }
    BigDict['flightPrice'] = flightPrice

    return redirect(url_for('insert_passengers_page' , CounterForPassengers=1))

 
@app.route('/passenger_<int:CounterForPassengers>', methods=['GET', 'POST'])
@login_required
def insert_passengers_page(CounterForPassengers):

    global triptype

    form = PassengerForm()

    IsAdult=1
    if CounterForPassengers <= BigDict['PassengersDetails']['NumberOfAdults']:
        IsAdult=1
    else:
        IsAdult=0
    BigDict['PassengersDetails']['CounterForPassengers'] = CounterForPassengers
    if request.method == 'POST' and form.validate_on_submit():
        Data = {
            'Gender': form.Gender.data,
            'FirstName': form.FirstName.data,
            'LastName': form.LastName.data,
            'DateOfBirth': form.DateOfBirth.data.strftime("%Y-%m-%d"),
            'Nationality': form.Nationality.data,
            'SSN': form.SSN.data,
        }

        BigDict['PassengersDetails']['Passengers'][CounterForPassengers - 1] = Data
        BigDict['PassengersDetails']['CounterForPassengers'] = CounterForPassengers + 1
        
        if BigDict['PassengersDetails']['CounterForPassengers'] > BigDict['PassengersDetails']['NumberOfPassengers']:
            return redirect(url_for('payment_page'))
        else:
            return redirect(url_for('insert_passengers_page', CounterForPassengers=CounterForPassengers+1))

    return render_template('insert_passengers.html', 
                           UserFirstName=BigDict['UserDetails']['FirstName'],
                           UserLastName=BigDict['UserDetails']['LastName'],
                           UserEmail=BigDict['UserDetails']['Email'],
                           UserPhoneNumber=BigDict['UserDetails']['PhoneNumber'],
                           OneWay=BigDict['TripDetails']['OneWay'],
                           DepartureDetails=BigDict['TripDetails']['Departure Details'],
                           ReturnDetails=BigDict['TripDetails']['Return Details'],
                           CounterForPassengers=CounterForPassengers,
                           NumberOfPassengers=BigDict['PassengersDetails']['NumberOfPassengers'],
                           TotalPrice=BigDict['flightPrice'],
                           TicketPrice=BigDict['flightPrice']/(BigDict['PassengersDetails']['NumberOfPassengers']*2 if triptype == 1 else 1),
                           IsAdult=IsAdult,
                           form=form)


@app.route('/manage_flight' , methods=['POST' , 'GET'])
@login_required
def manage_flight_page():

    sortBy = request.form.get('sortOptions', '')
    AscDesc = request.form.get('AscDesc', '')
    searchBy = request.form.get('searchBy', '')
    searchInput = request.form.get('searchInput', '')

    GroupBy = """
        GROUP BY
            b.booking_id, f.flight_id, f.flight_number, a1.country, a2.country, a1.name, a2.name, f.departure_date, f.departure_time, f.flight_duration
    """
    
    query = """
        SELECT
            b.booking_id AS Booking_ID,
            f.flight_id AS Flight_ID, 
            f.flight_number AS Flight_Number,
            a1.country AS Departure_Country,
            a2.country AS Arrival_Country,
            a1.name AS Departure_Airport,
            a2.name AS Arrival_Airport,
            f.departure_date AS Departure_Date,
            f.departure_time AS Departure_Time,
            f.flight_duration AS Flight_Duration,
            count(p.passenger_ssn) AS Number_Of_Passengers,
            b.total_amount AS Total_Price
        FROM 
            passenger p, 
            flight f, 
            booking b, 
            Passenger_Flight_Booking pfb, 
            user_ u, 
            Passenger_User pu, 
            airport a1, 
            airport a2,
            bill bi
        WHERE 
            p.passenger_ssn = pfb.passenger_ssn AND
            f.flight_id = pfb.flight_id AND
            b.booking_id = pfb.booking_id AND
            u.user_id = pu.user_id AND
            p.passenger_ssn = pu.passenger_ssn AND
            f.departure_airport_id = a1.airport_id AND
            f.arrival_airport_id = a2.airport_id AND
            bi.flight_id = f.flight_id AND
            bi.user_id = u.user_id AND
            pfb.is_deleted = 0 AND 
            bi.booking_id = b.booking_id AND
            b.booking_status LIKE 'Active' AND
            f.departure_date > %s AND
            u.user_id = %s
    """
    today_date = date.today()

    data = [today_date, current_user.id]

    if searchInput:
        if searchBy == 'departure_country':
            data.append('%' + searchInput + '%')
            query += ' AND a1.country LIKE %s '
        elif searchBy == 'arrival_country':
            data.append('%' + searchInput + '%')
            query += ' AND a2.country LIKE %s '
        elif searchBy == 'departure_airport':
            data.append('%' + searchInput + '%')
            query += ' AND a1.name LIKE %s '
        elif searchBy == 'arrival_airport':
            data.append('%' + searchInput + '%')
            query += ' AND a2.name LIKE %s '
        elif searchBy == 'flight_number':
            data.append('%' + searchInput + '%')
            query += ' AND f.flight_number LIKE %s '

    query += GroupBy

    if sortBy == 'departure_date_and_time':
        query += ' ORDER BY Departure_Date '
        query += 'ASC' if AscDesc == 'ascending' else 'DESC'
        query += ', Departure_Time '
        query += 'ASC' if AscDesc == 'ascending' else 'DESC'
    elif sortBy == 'total_price':
        query += ' ORDER BY Total_Price '
        query += 'ASC' if AscDesc == 'ascending' else 'DESC'
    elif sortBy == 'flight_duration':
        query += ' ORDER BY Flight_Duration '
        query += 'ASC' if AscDesc == 'ascending' else 'DESC'
    elif sortBy == 'number_of_passengers': 
        query += ' ORDER BY Number_Of_Passengers '
        query += 'ASC' if AscDesc == 'ascending' else 'DESC'
    else: # sort by date and time ascending aby default
        query += ' ORDER BY Departure_Date '
        query += 'ASC'
        query += ', Departure_Time '

    myCursor.execute(query , data)

    # Convert the result to a list of dictionaries
    columns = [column[0] for column in myCursor.description]  # Get column names
    result = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data

    return render_template('manage_flight.html', flights=result, sortBy=sortBy, AscDesc=AscDesc, searchBy=searchBy)

@app.route('/passengers_details', methods=['POST' , 'GET'])
@login_required
def passengers_details():

    booking_id = request.args.get('booking_id')
    flight_id = request.args.get('flight_id')
    flight_number = request.args.get('flight_number')
    booking_id = int(request.args.get('booking_id'))

    today_date = date.today()

    data = [today_date, flight_id, current_user.id,booking_id]

    # Query to fetch the passenger details based on the flight_id
    query = """
        SELECT
            p.passenger_ssn AS Passenger_SSN,
            p.first_name AS First_Name,
            p.last_name AS Last_Name,
            p.nationality AS Nationality,
            p.date_of_birth AS Date_Of_Birth,
            p.gender AS Gender
        FROM passenger p, 
            flight f, 
            booking b, 
            Passenger_Flight_Booking pfb, 
            user_ u, 
            Passenger_User pu, 
            airport a1, 
            airport a2,
            bill bi
        WHERE 
            p.passenger_ssn = pfb.passenger_ssn AND
            f.flight_id = pfb.flight_id AND
            b.booking_id = pfb.booking_id AND
            u.user_id = pu.user_id AND
            p.passenger_ssn = pu.passenger_ssn AND
            f.departure_airport_id = a1.airport_id AND
            f.arrival_airport_id = a2.airport_id AND
            bi.flight_id = f.flight_id AND
            bi.user_id = u.user_id AND
            bi.booking_id = b.booking_id AND
            b.booking_status LIKE 'Active' AND
            pfb.is_deleted = 0 AND
            f.departure_date > %s AND
            f.flight_id = %s AND
            u.user_id = %s AND
            b.booking_id = %s
    """

    myCursor.execute(query, data)

    columns = [column[0] for column in myCursor.description]  # Get column names
    result = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data


    return render_template('passengers_details.html', passengers=result, flight_id=flight_id, flight_number=flight_number, booking_id=booking_id)


@app.route('/edit_passenger/', methods=['Get', 'POST'])
@login_required
def edit_passenger():

    current_ssn = int(request.args.get('ssn'))
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    gender = request.args.get('gender')
    nationality = request.args.get('nationality')
    date_of_birth_str = request.args.get('date_of_birth')
    date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%d")
    flight_id = request.args.get('flight_id')
    flight_number = request.args.get('flight_number')
    booking_id = request.args.get('booking_id')

    form = PassengerForm2()

    if request.method == 'POST' and form.validate_on_submit():
        new_first_name = form.FirstName.data
        new_last_name = form.LastName.data
        new_nationality = request.form.get('nationality')
        new_gender = request.form.get('gender')
        new_date_of_birth = form.DateOfBirth.data.strftime("%Y-%m-%d")

        today_date = date.today()

        data = [today_date, flight_id, current_user.id]

        query = """
            SELECT
                p.passenger_ssn AS SSN,
                p.date_of_birth AS Date_Of_Birth
            FROM passenger p, 
                flight f, 
                booking b, 
                Passenger_Flight_Booking pfb, 
                user_ u, 
                Passenger_User pu
            WHERE 
                p.passenger_ssn = pfb.passenger_ssn AND
                f.flight_id = pfb.flight_id AND
                b.booking_id = pfb.booking_id AND
                u.user_id = pu.user_id AND
                p.passenger_ssn = pu.passenger_ssn AND
                b.booking_status LIKE 'Active' AND
                pfb.is_deleted = 0 AND
                f.departure_date > %s AND
                f.flight_id = %s AND
                u.user_id = %s
        """

        myCursor.execute(query, data)
        results = myCursor.fetchall()

        passenger_details = []

        for result in results:
            SSN = int(result[0])
            date_of_birth = result[1]

            if isinstance(date_of_birth, str):
                date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")

            if SSN == current_ssn:
                date_of_birth = new_date_of_birth
            
            if isinstance(date_of_birth, str):
                date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
            
            today = datetime.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            age = int(age)
            SSN = int(SSN)
            passenger_details.append({'SSN': SSN, 'Age': age})
        
        adult=0
        child=0
        for passenger in passenger_details:
            AGE = passenger['Age']
            if AGE >= 12:
                adult+=1
            elif AGE < 12:
                child+=1

        if adult == 0 and child > 0:
            flash("Update failed. Flight must have at least one adult passenger.", "danger")
            return redirect(url_for('passengers_details', flight_id=flight_id, flight_number=flight_number,booking_id=booking_id))
        else:
            return redirect(url_for('update_passenger', ssn=current_ssn, new_first_name=new_first_name, new_last_name=new_last_name, new_nationality=new_nationality, new_gender=new_gender, new_date_of_birth=new_date_of_birth, flight_id=flight_id, flight_number=flight_number, booking_id=booking_id))

    return render_template('edit_passenger.html', form=form, ssn=current_ssn, first_name=first_name, last_name=last_name, nationality=nationality, date_of_birth=date_of_birth_str, gender=gender, flight_id=flight_id, flight_number=flight_number, booking_id=booking_id)

@app.route('/update_passenger', methods=['GET', 'POST'])
@login_required
def update_passenger():

    ssn = request.args.get('ssn') 
    new_first_name = request.args.get('new_first_name')
    new_last_name = request.args.get('new_last_name')
    new_nationality = request.args.get('new_nationality')
    new_gender = request.args.get('new_gender')
    new_date_of_birth = request.args.get('new_date_of_birth')
    flight_id = request.args.get('flight_id')
    flight_number = request.args.get('flight_number')
    booking_id = request.args.get('booking_id')

    query = """
        UPDATE 
            passenger
        SET 
            first_name = %s,
            last_name = %s,
            nationality = %s,
            gender = %s,
            date_of_birth = %s
        WHERE 
            passenger_ssn = %s;
    """

    data = [new_first_name, new_last_name, new_nationality, new_gender, new_date_of_birth, ssn]

    myCursor.execute(query , data)
    myDB.commit()

    flash("The passenger details has been updated successfully.", "success")
    return redirect(url_for('passengers_details', flight_id=flight_id, flight_number=flight_number,booking_id=booking_id))

@app.route('/delete_passenger_reservation' , methods=['POST' , 'GET'])
@login_required
def delete_passenger_reservation():

    current_ssn = int(request.args.get('ssn'))
    flight_id = int(request.args.get('flight_id'))
    flight_number = request.args.get('flight_number')
    booking_id = int(request.args.get('booking_id'))

    today_date = date.today()

    data = [today_date, flight_id, current_user.id, booking_id]

    query = """
        SELECT
            p.passenger_ssn AS SSN,
            p.date_of_birth AS Date_Of_Birth
        FROM 
            passenger p, 
            flight f, 
            booking b, 
            Passenger_Flight_Booking pfb, 
            user_ u, 
            Passenger_User pu
        WHERE 
            p.passenger_ssn = pfb.passenger_ssn AND
            f.flight_id = pfb.flight_id AND
            b.booking_id = pfb.booking_id AND
            u.user_id = pu.user_id AND
            p.passenger_ssn = pu.passenger_ssn AND
            b.booking_status LIKE 'Active' AND
            pfb.is_deleted = 0 AND
            f.departure_date > %s AND
            f.flight_id = %s AND
            u.user_id = %s AND
            b.booking_id = %s
    """

    myCursor.execute(query, data)
    results = myCursor.fetchall()

    passenger_details = []

    for result in results:
        ssn = result[0]
        date_of_birth = result[1]
        
        today = datetime.today()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        age = int(age)
        ssn = int(ssn)
        passenger_details.append({'SSN': ssn, 'Age': age})
    
    adult=0
    child=0
    NumberOfPassengers=0
    for passenger in passenger_details:
        SSN = passenger['SSN']
        AGE = passenger['Age']
        NumberOfPassengers+=1
        if SSN != current_ssn and AGE >= 12:
            adult+=1
        elif AGE < 12:
            child+=1
    
    
    if adult == 0 and child > 0:
        flash("The flight must have at least one adult passenger.", "danger")
        return redirect(url_for('passengers_details', flight_id=flight_id, flight_number=flight_number,booking_id=booking_id))
    else:

        data = [today_date, flight_id, current_ssn, booking_id]
        query = """
            UPDATE 
                booking b, passenger p, flight f, passenger_flight_booking pfb
            SET 
                pfb.is_deleted = 1
            WHERE
                b.booking_id = pfb.booking_id
                AND f.flight_id = pfb.flight_id
                AND p.passenger_ssn = pfb.passenger_ssn
                AND f.departure_date > %s
                AND f.flight_id = %s
                AND p.passenger_ssn = %s
                AND b.booking_id = %s;
        """
        myCursor.execute(query, data)
        myDB.commit()

        data = [NumberOfPassengers, booking_id]
        query = """
            UPDATE 
                booking
            SET 
                total_amount = total_amount - (total_amount/%s)
            WHERE
                booking_id = %s
        """
        myCursor.execute(query, data)
        myDB.commit()


        data = [flight_id]
        query = """
            UPDATE 
                flight f
            SET 
                f.available_seats = f.available_seats + 1
            WHERE
                f.flight_id = %s
        """
        myCursor.execute(query, data)
        myDB.commit()


        query = """
            SELECT pfb.flight_id FROM PASSENGER_FLIGHT_BOOKING pfb
            WHERE pfb.booking_id = %s AND pfb.flight_id != %s AND pfb.passenger_ssn = %s
        """
        data = [booking_id, flight_id, current_ssn]
        myCursor.execute(query, data)
        results = myCursor.fetchall()
        if results:

            return_flight_id = [result[0] for result in results]

            data = [today_date, return_flight_id, current_ssn, booking_id]
            query = """
                UPDATE 
                    booking b, passenger p, flight f, passenger_flight_booking pfb
                SET 
                    pfb.is_deleted = 1
                WHERE
                    b.booking_id = pfb.booking_id
                    AND f.flight_id = pfb.flight_id
                    AND p.passenger_ssn = pfb.passenger_ssn
                    AND f.departure_date > %s
                    AND f.flight_id = %s
                    AND p.passenger_ssn = %s
                    AND b.booking_id = %s
            """
            myCursor.execute(query, data)
            myDB.commit()

            data = [NumberOfPassengers, booking_id]
            query = """
                UPDATE 
                    booking
                SET 
                    total_amount = total_amount - (total_amount/%s)
                WHERE
                    booking_id = %s
            """
            myCursor.execute(query, data)
            myDB.commit()

            data = [return_flight_id]
            query = """
                UPDATE 
                    flight f
                SET 
                    f.available_seats = f.available_seats + 1
                WHERE
                    f.flight_id = %s
            """
            myCursor.execute(query, data)
            myDB.commit()



        data = [booking_id, today_date, flight_id, current_user.id]
        query = """
            SELECT
                count(p.passenger_ssn)
            FROM 
                passenger p, 
                flight f, 
                booking b, 
                Passenger_Flight_Booking pfb, 
                user_ u, 
                Passenger_User pu
            WHERE 
                p.passenger_ssn = pfb.passenger_ssn AND
                f.flight_id = pfb.flight_id AND
                b.booking_id = pfb.booking_id AND
                u.user_id = pu.user_id AND
                p.passenger_ssn = pu.passenger_ssn AND
                b.booking_status LIKE 'Active' AND
                pfb.is_deleted = 0 AND
                b.booking_id = %s AND
                f.departure_date > %s AND
                f.flight_id = %s AND
                u.user_id = %s
        """
        myCursor.execute(query, data)
        myDB.commit()
        results = myCursor.fetchall()
        count = -1
        for result in results:
            count = result[0] # number of non deleted passengers in this booking
        
        if count == 0:
            data = [booking_id]
            query = """
                UPDATE 
                    booking
                SET 
                    booking_status = "Cancelled"
                WHERE
                    booking_id = %s
            """
            myCursor.execute(query, data)
            myDB.commit()

        flash("The passenger reservation has been cancelled successfully.", "success")
        return redirect(url_for('passengers_details', flight_id=flight_id, flight_number=flight_number,booking_id=booking_id))

@app.route('/delete_reservation' , methods=['POST' , 'GET'])
@login_required
def delete_reservation():
    
    flight_id = request.args.get('flight_id')
    booking_id = request.args.get('booking_id')

    today_date = date.today()

    data = [today_date, flight_id, current_user.id, booking_id]

    query = """
        SELECT 
            COUNT(p.passenger_ssn) 
        FROM 
            passenger p, 
            flight f, 
            booking b, 
            Passenger_Flight_Booking pfb, 
            user_ u, 
            Passenger_User pu
        WHERE 
            p.passenger_ssn = pfb.passenger_ssn AND
            f.flight_id = pfb.flight_id AND
            b.booking_id = pfb.booking_id AND
            u.user_id = pu.user_id AND
            p.passenger_ssn = pu.passenger_ssn AND
            b.booking_status LIKE 'Active' AND
            pfb.is_deleted = 0 AND
            f.departure_date > %s AND
            f.flight_id = %s AND
            u.user_id = %s AND
            b.booking_id = %s
    """
    myCursor.execute(query, data)
    NumberOfPassengers = myCursor.fetchone()[0]

    while NumberOfPassengers > 0:
        data = [flight_id]
        query = """
            UPDATE 
                flight f
            SET 
                f.available_seats = f.available_seats + 1
            WHERE
                f.flight_id = %s
        """
        myCursor.execute(query, data)
        myDB.commit()
        NumberOfPassengers-=1


        data = [booking_id, NumberOfPassengers]
        query = """
            UPDATE 
                booking
            SET 
                total_amount = total_amount - (total_amount/%s)
            WHERE
                booking_id = %s
        """
        myCursor.execute(query, data)
        myDB.commit()


        data = [today_date, flight_id, booking_id]
        query = """
            UPDATE 
                booking b, passenger p, flight f, passenger_flight_booking pfb
            SET 
                pfb.is_deleted = 1
            WHERE
                b.booking_id = pfb.booking_id
                AND f.flight_id = pfb.flight_id
                AND p.passenger_ssn = pfb.passenger_ssn
                AND f.departure_date > %s
                AND f.flight_id = %s
                AND b.booking_id = %s
        """
        myCursor.execute(query, data)
        myDB.commit()


        query = """
            SELECT distinct pfb.flight_id FROM PASSENGER_FLIGHT_BOOKING pfb
            WHERE pfb.booking_id = %s AND pfb.flight_id != %s
        """
        data = [booking_id, flight_id]
        myCursor.execute(query, data)
        results = myCursor.fetchall()
        
        if results:
            return_flight_id = [result[0] for result in results]

            data = [today_date, return_flight_id, booking_id]
            query = """
                UPDATE 
                    booking b, passenger p, flight f, passenger_flight_booking pfb
                SET 
                    pfb.is_deleted = 1
                WHERE
                    b.booking_id = pfb.booking_id
                    AND f.flight_id = pfb.flight_id
                    AND p.passenger_ssn = pfb.passenger_ssn
                    AND f.departure_date > %s
                    AND f.flight_id = %s
                    AND b.booking_id = %s
            """
            myCursor.execute(query, data)
            myDB.commit()
            
            data = [return_flight_id]
            query = """
                UPDATE 
                    flight f
                SET 
                    f.available_seats = f.available_seats + 1
                WHERE
                    f.flight_id = %s
            """
            myCursor.execute(query, data)
            myDB.commit()


    data = [today_date, booking_id, current_user.id]

    query = """
        UPDATE
            USER_ u, Passenger p, Flight f, booking b, Passenger_User pu, Passenger_Flight_Booking pfb
        SET
            b.booking_status = "Cancelled"
        WHERE
            p.passenger_ssn = pu.passenger_ssn AND
            u.user_id = pu.user_id AND
            b.booking_id = pfb.booking_id AND
            f.flight_id = pfb.flight_id AND
            p.passenger_ssn = pfb.passenger_ssn AND
            f.departure_date > %s AND
            b.booking_id = %s AND
            u.user_id = %s
    """

    myCursor.execute(query, data)
    myDB.commit()

    flash("The reservation has been cancelled successfully.", "success")
    return redirect(url_for('manage_flight_page'))


@app.route('/average_time', methods=['POST', 'GET'])
def average_time():
        
    result7=None
    firstCountry=None
    secondCountry=None

    if request.method == 'POST':
        firstCountry = request.form.get('country1')
        secondCountry = request.form.get('country2')
        if firstCountry and secondCountry:
            query7 = """
                SELECT SEC_TO_TIME(FLOOR(AVG(TIME_TO_SEC(f.flight_duration)))) AS Average_Time
                from flight f, airport a1 , airport a2
                where f.departure_airport_id = a1.airport_id and f.arrival_airport_id = a2.airport_id
                and a1.country LIKE %s and a2.country LIKE %s;
            """
            data7=[firstCountry, secondCountry]
            myCursor.execute(query7, data7)
            result7=myCursor.fetchone()
            if result7 and result7[0]:
                hh_mm_ss = str(result7[0])
                hh, mm, _ = hh_mm_ss.split(":")
                result7 = f"{int(hh)} hours and {int(mm)} minutes"
                print(result7)
            else:
                result7 = 'Invalid'

    return render_template('all_queries.html', result7=result7,country1=firstCountry,country2=secondCountry)


@app.route('/airplane_earnings', methods=['POST', 'GET'])
def airplane_earnings():

    start_date=None
    end_date=None
    results8=None
    error8=None
    
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        current_date = datetime.now()
        if start_date and end_date:
            if datetime.strptime(start_date, "%Y-%m-%d") > current_date:
                error8="Start date cannot be in the future."
            
            if datetime.strptime(end_date, "%Y-%m-%d") > current_date:
                error8="End date cannot be in the future."

            if datetime.strptime(end_date, "%Y-%m-%d") <= datetime.strptime(start_date, "%Y-%m-%d"):
                error8="End date must be greater than the start date."
            
            query8="""
                select a.airplane_id AS Airplane_ID, a.model AS Model, sum(b.total_amount) AS Earnings
                from airplane a, flight f, booking b, passenger_flight_booking pfb
                where a.airplane_id = f.airplane_id and f.flight_id = pfb.flight_id and b.booking_id = pfb.booking_id
                and f.departure_date > %s and f.departure_date < %s
                group by a.airplane_id, a.model 
                having sum(b.total_amount) >= (
                    select avg(b2.total_amount)
                    from airplane a2, flight f2, booking b2, passenger_flight_booking pfb2
                    where a2.airplane_id = f2.airplane_id and f2.flight_id = pfb2.flight_id and b2.booking_id = pfb2.booking_id
                    and f2.departure_date > %s and f2.departure_date < %s
                );
            """
            data = [start_date, end_date, start_date, end_date]
            myCursor.execute(query8, data)
            columns = [column[0] for column in myCursor.description]  # Get column names
            results8 = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data
            if not results8:
                results8 = 'Invalid'

    return render_template('all_queries.html', results8=results8,error8=error8,start_date=start_date,end_date=end_date)

@app.route('/cancelled_flights', methods=['POST', 'GET'])
def cancelled_flights():

    start_date=None
    end_date=None
    results9=None
    error9=None
    
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        current_date = datetime.now()
        if start_date and end_date:

            if datetime.strptime(end_date, "%Y-%m-%d") <= datetime.strptime(start_date, "%Y-%m-%d"):
                error9="End date must be greater than the start date."
            
            query9="""
                select a.airplane_id AS Airplane_ID, a.model AS Model, count(*) AS Number_Of_Cancellation 
                from airplane a, flight f, booking b, passenger_flight_booking pfb
                where a.airplane_id = f.airplane_id and f.flight_id = pfb.flight_id and b.booking_id = pfb.booking_id
                and b.booking_status LIKE "Cancelled" and f.departure_date > %s and f.departure_date < %s
                group by a.airplane_id, a.model
                having count(*) = (
                    select max(Cancelled_count)
                    from (
                        select count(*) AS Cancelled_count
                        from airplane a2, flight f2, booking b2, passenger_flight_booking pfb2
                        where a2.airplane_id = f2.airplane_id and f2.flight_id = pfb2.flight_id and b2.booking_id = pfb2.booking_id
                        and b2.booking_status LIKE "Cancelled" and f2.departure_date > %s and f2.departure_date < %s
                        GROUP BY a2.airplane_id, a2.model
                    ) AS Qasim
                );
            """
            data = [start_date, end_date, start_date, end_date]
            myCursor.execute(query9, data)
            columns = [column[0] for column in myCursor.description]  # Get column names
            results9 = [dict(zip(columns, row)) for row in myCursor.fetchall()]  # Combine column names with row data
            if not results9:
                results9 = 'Invalid'

    return render_template('all_queries.html', results9=results9,error9=error9,start_date=start_date,end_date=end_date)

    
#***********************************************************************Salah****************************************************************
def add_passenger(Passenger):

    passenger_ssn = Passenger['SSN']
    first_name = Passenger['FirstName']
    last_name = Passenger['LastName']
    nationality = Passenger['Nationality']
    gender = Passenger['Gender']
    date_of_birth = Passenger['DateOfBirth']

    data = [first_name, last_name, nationality, date_of_birth, gender, passenger_ssn]

    query = """
        UPDATE 
            Passenger
        SET
            first_name = %s,
            last_name = %s,
            nationality = %s,
            date_of_birth = %s,
            gender = %s
        WHERE
            passenger_ssn = %s ;
    """

    myCursor.execute(query, data)
    myDB.commit()

    data = [passenger_ssn, first_name, last_name, date_of_birth, nationality, gender, passenger_ssn]

    query = """
        INSERT INTO PASSENGER (passenger_ssn, first_name, last_name, date_of_birth, nationality, gender)
        SELECT %s, %s, %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT *
            FROM PASSENGER p1
            WHERE p1.passenger_ssn = %s
        );
    """

    myCursor.execute(query, data)
    myDB.commit()

    data = [passenger_ssn, current_user.id, passenger_ssn, current_user.id]
    query = """
        INSERT INTO PASSENGER_USER (passenger_ssn, user_id)
        SELECT %s, %s
        WHERE NOT EXISTS (
            SELECT *
            FROM PASSENGER_USER pu
            WHERE pu.passenger_ssn = %s AND pu.user_id = %s
        );
    """
    myCursor.execute(query, data)
    myDB.commit()


def issue_tickets(passengers):

    global flightPrice, departure_date, goflightid, retflightid, triptype

    assigned_tickets = []

    #  Find the next available ticket ID from DB
    query_max = "SELECT MAX(ticket_id) FROM Passenger_Flight_Booking;"
    myCursor.execute(query_max)
    row = myCursor.fetchone()  

    if row and row[0] is not None:
        ticket_id = row[0] + 1
    else:
        ticket_id = 100000  # start from 100000 if no tickets


    for passenger in passengers:
        add_passenger(passenger)
    

    query_max = "SELECT MAX(booking_id) FROM Booking"
    myCursor.execute(query_max)
    row = myCursor.fetchone()
    booking_id = row[0]


    if triptype == 0:
        insert_query = """
        INSERT INTO Passenger_Flight_Booking (
            passenger_ssn,
            flight_id,
            booking_id,
            ticket_id
        )
        VALUES (%s, %s, %s, %s)"""
        for p in passengers:
            ssn = p.get('SSN')
            myCursor.execute(insert_query ,(ssn, goflightid, booking_id, ticket_id))
            assigned_tickets.append(ticket_id)
            myDB.commit() 
            ticket_id += 1
    else:
        insert_query = """
        INSERT INTO Passenger_Flight_Booking (
            passenger_ssn,
            flight_id,
            booking_id,
            ticket_id
        )
        VALUES (%s, %s, %s, %s)"""
        for p in passengers:
            ssn = p.get('SSN')
            myCursor.execute(insert_query ,(ssn, goflightid, booking_id, ticket_id))
            assigned_tickets.append(ticket_id)
            myDB.commit() 
            ticket_id += 1

        insert_query = """
        INSERT INTO Passenger_Flight_Booking (
            passenger_ssn,
            flight_id,
            booking_id,
            ticket_id
        )
        VALUES (%s, %s, %s, %s)"""
        for p in passengers:
            ssn = p.get('SSN')
            myCursor.execute(insert_query ,(ssn, retflightid, booking_id, ticket_id))
            assigned_tickets.append(ticket_id)
            myDB.commit() 
            ticket_id += 1


    return assigned_tickets

##############################3
@app.route('/payment')
@login_required
def payment_page():
    
    global flightPrice
    user_details = BigDict.get('UserDetails', {})
    passengers_info = BigDict.get('PassengersDetails', {})
    passenger_list = passengers_info.get('Passengers', [])

    
    return render_template(
        'payment.html',
        user=user_details,            
        passengers=passenger_list,    # a list of dicts each with
        flight_price=flightPrice     # from BigDict
    )


@app.route('/process_payment', methods=['POST'])
@login_required
def process_payment():


    from datetime import datetime
    from flask import flash, redirect, url_for

    global flightPrice

    # Retrieve form data
    cardType = request.form.get('cardType', '').strip()
    cardNumber = request.form.get('cardNumber', '').strip()
    expiryMonth = request.form.get('expiryMonth', '').strip()
    expiryYear = request.form.get('expiryYear', '').strip()
    cvv = request.form.get('cvv', '').strip()
    cardholderName = request.form.get('cardholderName', '').strip()

    # Initialize validation flags
    is_valid = True
    error_message = ''

    # Validate Card Type
    if not cardType:
        is_valid = False
        error_message = 'Please select a card type.'

    # Validate Card Number (16 digits)
    elif not cardNumber.isdigit() or len(cardNumber) != 16:
        is_valid = False
        error_message = 'Invalid card number. Must be 16 digits.'

    # Validate CVV (3 or 4 digits)
    elif not cvv.isdigit() or len(cvv) not in [3, 4]:
        is_valid = False
        error_message = 'Invalid CVV. Must be 3 or 4 digits.'

    # Validate Expiry Month
    elif not expiryMonth.isdigit() or not (1 <= int(expiryMonth) <= 12):
        is_valid = False
        error_message = 'Invalid expiry month. Must be between 01 and 12.'

    # Validate Expiry Year
    elif not expiryYear.isdigit() or len(expiryYear) != 4:
        is_valid = False
        error_message = 'Invalid expiry year. Must be 4 digits.'
    else:
        now = datetime.now()
        month = int(expiryMonth)
        year = int(expiryYear)
        if year < now.year or (year == now.year and month < now.month):
            is_valid = False
            error_message = 'Card expiry is in the past.'

    # Validate Cardholder Name
    if is_valid and len(cardholderName) < 2:
        is_valid = False
        error_message = 'Please enter a valid cardholder name.'

    # If any validation fails, flash the error and redirect back to payment page
    if not is_valid:
        flash(error_message, 'error')
        return redirect(url_for('payment_page'))

    # All validations passed, proceed with payment processing

    # Retrieve flight price from BigDict
    # flight_price = BigDict.get('flightPrice', 0.0)

    query = """
    INSERT INTO Booking (booking_date, payment_status, total_amount)
    VALUES (%s, %s, %s)
    """
    data = [date.today(), "Paid", flightPrice]
    myCursor.execute(query, data)
    myDB.commit() 

    payment_date = now.date()
    payment_time = now.time()
    payment_method = cardType
    amount = flightPrice
    print(flightPrice)

    query_max = "SELECT MAX(booking_id) FROM Booking"
    myCursor.execute(query_max)
    row = myCursor.fetchone()
    booking_id = row[0]

    global goflightid, retflightid, triptype

    if triptype == 0:
        query = """
            INSERT INTO Bill (
                booking_id, user_id, flight_id,
                payment_date, payment_time, payment_method, amount,
                card_type, card_number, expiry_month, expiry_year, cvv, cardholder_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        data = [
            booking_id, current_user.id, goflightid,
            payment_date, payment_time, payment_method, amount,
            cardType, cardNumber, month, year, cvv, cardholderName
        ]
        print(data)
        myCursor.execute(query, data)
        myDB.commit()
    else:
        query = """
            INSERT INTO Bill (
                booking_id, user_id, flight_id,
                payment_date, payment_time, payment_method, amount,
                card_type, card_number, expiry_month, expiry_year, cvv, cardholder_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        data = (
            booking_id, current_user.id, goflightid,
            payment_date, payment_time, payment_method, amount/2,
            cardType, cardNumber, month, year, cvv, cardholderName
        )
        myCursor.execute(query, data)
        myDB.commit()

        query = """
            INSERT INTO Bill (
                booking_id, user_id, flight_id,
                payment_date, payment_time, payment_method, amount,
                card_type, card_number, expiry_month, expiry_year, cvv, cardholder_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,  %s, %s, %s);
        """
        print(retflightid)
        data = (
            booking_id, current_user.id, retflightid,
            payment_date, payment_time, payment_method, amount/2,
            cardType, cardNumber, month, year, cvv, cardholderName
        )
        myCursor.execute(query, data)
        myDB.commit()

    # If we have multiple passengers, you might want to subtract the # of passengers
    num_passengers = BigDict.get('PassengersDetails', {}).get('NumberOfPassengers', 1)
    
    if triptype == 0:
        update_seats_query = """
            UPDATE Flight
                SET available_seats = available_seats - %s
                WHERE flight_id = %s
        """
        seat_data = (num_passengers, goflightid)
        myCursor.execute(update_seats_query, seat_data)
        myDB.commit()
    else:
        update_seats_query = """
            UPDATE Flight
                SET available_seats = available_seats - %s
                WHERE flight_id = %s
        """
        seat_data = (num_passengers, goflightid)
        myCursor.execute(update_seats_query, seat_data)
        myDB.commit()

        update_seats_query = """
            UPDATE Flight
                SET available_seats = available_seats - %s
                WHERE flight_id = %s
        """
        seat_data = (num_passengers, retflightid)
        myCursor.execute(update_seats_query, seat_data)
        myDB.commit()

    passengers = BigDict['PassengersDetails']['Passengers']  

    #  Issue tickets
    assigned_tickets = issue_tickets(
        passengers=passengers
    )

    # Store them somewhere to display
    BigDict['AssignedTickets'] = assigned_tickets

    return redirect(url_for('ticket_interface'))

#################
@app.route('/ticket')
@login_required
def ticket_interface():
   
    from datetime import date
    
    # Example data from BigDict
    user = BigDict.get('UserDetails', {})
    passengers = BigDict.get('PassengersDetails', {}).get('Passengers', [])
    assigned_tickets = BigDict.get('AssignedTickets', [])

    passenger_tickets = list(zip(passengers, assigned_tickets))

    # flight details
    flightPrice = BigDict.get('flightPrice', 0.0)
    flightDate = BigDict.get('TripDetails', {}).get('Departure Details', {}).get('Date')
    departureTime = BigDict.get('TripDetails', {}).get('Departure Details', {}).get('Departure Time')
    arrivalTime = BigDict.get('TripDetails', {}).get('Departure Details', {}).get('Arrival Time')
    fromCountry = BigDict.get('TripDetails', {}).get('Departure Details', {}).get('From')
    toCountry   = BigDict.get('TripDetails', {}).get('Departure Details', {}).get('To')

    # date of issue
    doc_issue_date = date.today().strftime("%d %b %Y") 

    return render_template(
        'ticket_interface.html',
        doc_issue_date=doc_issue_date,
        user=user,
        passengers=passengers,
        passenger_tickets=passenger_tickets,
        assigned_tickets=assigned_tickets,
        flightPrice=flightPrice,
        flightDate=flightDate,
        departureTime=departureTime,
        arrivalTime=arrivalTime,
        fromCountry=fromCountry,
        toCountry=toCountry
    )


##############################################################################
# My Reservations Section 
##############################################################################
@app.route('/myReservations')
@login_required  # Ensure the user is logged in
def myReservations():
    """
    Display user reservations, separated into Upcoming, Past, and Deleted.
    Reservations are sorted by the flight's departure date.
    """
    
    query = """
        SELECT 
            B.booking_id,
            B.booking_date,
            B.payment_status,
            B.total_amount,
            B.booking_status,
            F.departure_date
        FROM Booking AS B
        JOIN Bill AS L ON B.booking_id = L.booking_id
        JOIN Flight AS F ON L.flight_id = F.flight_id
        WHERE L.user_id = %s
        ORDER BY F.departure_date DESC
    """
    
    try:
        # Execute the query with the current user's ID
        myCursor.execute(query, (current_user.id,))
        reservations = myCursor.fetchall()
    except pymysql.MySQLError as e:
        # Handle database errors gracefully
        flash('An error occurred while fetching reservations. Please try again later.', 'error')
        print(f"Database Error: {e}")
        return redirect(url_for('index'))
    
    # Initialize lists to categorize reservations
    upcoming_reservations = []
    past_reservations = []
    deleted_reservations = []

    today = date.today()

    for r in reservations:
        booking_id = r[0]
        booking_date = r[1]       # Booking date
        payment_status = r[2]
        total_amount = r[3]
        booking_status = r[4]
        departure_date = r[5]     # Flight's departure date

        if booking_status.lower() == 'deleted':
            deleted_reservations.append(r)
        else:
            if departure_date >= today:
                upcoming_reservations.append(r)
            else:
                past_reservations.append(r)

    return render_template(
        'myReservations.html',
        upcoming=upcoming_reservations,
        past=past_reservations,
        deleted=deleted_reservations
    )

########################################

@app.route('/statistics', methods=['GET', 'POST'])
def show_all_queries():
    

    ##########################Salah's#############################################

    # For "Cheapest from" search
    from_airport_cheapest = None
    cheapest_flight = None

    # For "Average from" search
    from_airport_avg = None
    avg_price = None


    if request.method == 'POST':
        # 1) "Cheapest from" form
        from_airport_cheapest = request.form.get('airport_cheapest', '').strip().upper()
        if from_airport_cheapest:
            query_cheap = """
                SELECT 
                    f.flight_number,
                    aDep.country AS departure_country,
                    aArr.country AS arrival_country,
                    f.departure_date,
                    f.departure_time,
                    f.price
                FROM Flight f
                JOIN Airport aDep ON f.departure_airport_id = aDep.airport_id
                JOIN Airport aArr ON f.arrival_airport_id = aArr.airport_id
                WHERE 
                  aDep.IATA_code = %s
                  AND (
                      f.departure_date > CURDATE()
                      OR (f.departure_date = CURDATE() AND f.departure_time > CURTIME())
                  )
                ORDER BY f.price ASC
                LIMIT 1
            """
            myCursor.execute(query_cheap, (from_airport_cheapest,))
            row = myCursor.fetchone()
            if row:
                cheapest_flight = {
                    'flight_number': row[0],
                    'departure_country': row[1],
                    'arrival_country': row[2],
                    'departure_date': row[3],
                    'departure_time': row[4],
                    'price': row[5],
                }
            else:
                cheapest_flight = None

        # 2) "Average from" form
        from_airport_avg = request.form.get('airport_avg', '').strip().upper()
        if from_airport_avg:
            query_avg = """
                SELECT 
                    AVG(f.price) AS avg_price
                FROM Flight f
                JOIN Airport aDep ON f.departure_airport_id = aDep.airport_id
                WHERE 
                    aDep.IATA_code = %s
                    AND (
                        f.departure_date > CURDATE()
                        OR (f.departure_date = CURDATE() AND f.departure_time > CURTIME())
                    )
            """
            myCursor.execute(query_avg, (from_airport_avg,))
            row = myCursor.fetchone()
            if row and row[0] is not None:
                avg_price = row[0]
            else:
                avg_price = None

    #
    # Q1 (example): Cheapest flight overall
    #
    query1 = """
        SELECT flight_number, MIN(price) AS min_price
        FROM Flight
        GROUP BY flight_number
        ORDER BY min_price ASC
        LIMIT 1
    """
    myCursor.execute(query1)
    q1_result = myCursor.fetchone()  # e.g. (flight_number, min_price)

    #
    # Q2 (example): Busiest flights
    #
    query2 = """
        SELECT f.flight_number, COUNT(pfb.passenger_ssn) AS passenger_count
        FROM Flight f
        JOIN Passenger_Flight_Booking pfb ON f.flight_id = pfb.flight_id
        GROUP BY f.flight_number
        ORDER BY passenger_count DESC
        LIMIT 5
    """
    myCursor.execute(query2)
    q2_results = myCursor.fetchall()

    #
    # Q3: Flights in next 7 days
    #
    query3 = """
        SELECT 
            departure_date, 
            COUNT(*) as flight_count
        FROM Flight
        WHERE departure_date BETWEEN CURDATE() AND (CURDATE() + INTERVAL 7 DAY)
        GROUP BY departure_date
        ORDER BY departure_date
    """
    myCursor.execute(query3)
    rows_for_q3 = myCursor.fetchall()
    flights_next_7 = []
    for row in rows_for_q3:
        flights_next_7.append({
            'date': row[0].strftime("%Y-%m-%d"),
            'count': row[1],
        })



    


    # Return everything to all_queries.html
    return render_template(
        'all_queries.html',
        q1=q1_result, 
        q2=q2_results, 
        flights_next_7=flights_next_7,

        # For partial_cheapest_form.html
        from_airport_cheapest=from_airport_cheapest,
        cheapest_flight=cheapest_flight,

        # For partial_average_from.html
        from_airport_avg=from_airport_avg,
        avg_price=avg_price,
    )

if __name__ == "__main__":
    app.run(debug=True)