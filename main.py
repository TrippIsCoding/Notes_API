from fastapi import FastAPI, Depends, HTTPException
from auth import auth_router, oauth2_scheme, verify_token
from database import Base, engine, get_db
from sqlalchemy.orm import Session
from models import Message, MessageModel, User

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix='/auth', tags=['auth'])

@app.get('/helloworld')
def hello(token: str = Depends(oauth2_scheme)):
    verify_token(token)
    return {'Hello': 'World!'}

@app.get('/user/messages')
async def show_all_user_messages(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token = verify_token(token=token)
    
    user = db.query(User).filter_by(username=token['sub']).first()
    
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    messages = [{'username': token['sub'], 'message_id': msg.id, 'message': msg.message} for msg in user.messages]

    return {'messages': messages} 

@app.post('/user/create/message')
async def create_message(content: Message, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token = verify_token(token=token)
    
    user = db.query(User).filter_by(username=token['sub']).first()
    
    if not user:
        raise HTTPException(status_code=404, detail='Could not find user')
    
    new_message = MessageModel(
        user_id=user.id,
        message=content.message
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {'message': 'Message created successfully', 'message_id': new_message.id}