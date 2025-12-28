from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Meeting(Base):
    __tablename__ = 'meetings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String, nullable=False)
    status = Column(String, default="active") # active, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_processed = Column(Boolean, default=False)
    
    messages = relationship("Message", back_populates="meeting", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Meeting(id={self.id}, topic='{self.topic}', status='{self.status}')>"

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    bot_name = Column(String, nullable=False) # Chairman, CTO, CFO, etc. or 'User'
    content = Column(Text, nullable=False)
    round_number = Column(Integer, default=0)
    telegram_message_id = Column(Integer, nullable=True) # To track message IDs for replies
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meeting = relationship("Meeting", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, bot='{self.bot_name}', round={self.round_number})>"
