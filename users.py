from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import  Column, Integer, String, Boolean, Date, DateTime
import datetime


get_now_date = lambda: datetime.datetime.now().date()
get_now_datetime = lambda: datetime.datetime.now()
    

sqlite_database = "sqlite:///app.db"

engine = create_engine(sqlite_database)
Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    #    userid
    #    profileid
    #    next_billing_date
  
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    mode = Column(Integer, default=0)
    profile_id = Column(Integer)
    current_requests = Column(Integer, default=0)
    limit_requests = Column(Integer, default=100)
    registration_date = Column(Date)
    next_billing_date = Column(Date)
    last_request = Column(DateTime, default=get_now_datetime())

Base.metadata.create_all(bind=engine)



def change_mode_user(user_id):
    with Session(autoflush=False, bind=engine) as db:

        current_user = db.query(User).filter(User.profile_id==user_id).first()

        if (current_user != None):

            if current_user.mode == 0:
                current_user.mode = 1
            else:
                current_user.mode = 0
    
            db.commit() 

            return current_user.mode



# получить режим

def get_usermode(user_id):
    return get_current_user(user_id).mode


# проверка лимитов

def get_user_limit_req(user_id):
    return get_current_user(user_id).limit_requests

def get_user_current_req(user_id):
    return get_current_user(user_id).current_requests

check_user_limit = lambda id: get_user_current_req(id) < get_user_limit_req(id)


# добавить последний запрос для пользователя

def add_user_current_req(user_id, num_req=1):
    with Session(autoflush=False, bind=engine) as db:

        current_user = db.query(User).filter(User.profile_id==user_id).first()

        if (current_user != None):

            current_user.current_requests += num_req

            current_user.last_request = get_now_datetime()
    
            db.commit() 


# получить активных пользователей

def get_active_users():
    with Session(autoflush=False, bind=engine) as db:
        count_active_users = 0

        for user in db.query(User).all():
            if user.last_request != None:
                if (get_now_datetime() - user.last_request).seconds < 300:
                    count_active_users += 1
    
        return count_active_users
    

# получить всех пользователей

def get_all_users():
    with Session(autoflush=False, bind=engine) as db:

        users = db.query(User).all()
        return users


# получить конкретного пользователя

def get_current_user(user_id):
    with Session(autoflush=False, bind=engine) as db:

        try:
            user = db.query(User).filter(User.profile_id==user_id).first()
            return user

        except:
            return None


# добавить пользователя

def add_user(user_name, user_id):

    if get_current_user(user_id=user_id) == None:

        with Session(autoflush=False, bind=engine) as db:

            date_now = get_now_date()
            next_billing_date = date_now + datetime.timedelta(days=-1)

            user = User(name=user_name, profile_id=user_id, registration_date=date_now, next_billing_date=next_billing_date)
            db.add(user)    
            db.commit()





def add_subc_user(user_id, time_delta):
    with Session(autoflush=False, bind=engine) as db:

        current_user = db.query(User).filter(User.profile_id==user_id).first()

        if (current_user != None):

            date_now = get_now_date()

            if date_now < current_user.next_billing_date:
                next_billing_date = current_user.next_billing_date + datetime.timedelta(days=time_delta)
            else:
                next_billing_date = date_now + datetime.timedelta(days=time_delta)
                
            current_user.next_billing_date = next_billing_date
    
            db.commit() 

            return next_billing_date
