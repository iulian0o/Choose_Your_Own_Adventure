from app import db
from datetime import datetime

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    pages = db.relationship('Page', backref='story', lazy=True, foreign_keys='Page.story_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'start_page_id': self.start_page_id,
            'illustration': self.illustration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_ending = db.Column(db.Boolean, default=False)
    
    choices = db.relationship(
        'Choice', 
        backref='page', 
        lazy=True, 
        cascade='all, delete-orphan'
    )
    
    def to_dict(self, include_choices=True):
        data = {
            'id': self.id,
            'story_id': self.story_id,
            'text': self.text,
            'is_ending': self.is_ending,
            'ending_label': self.ending_label,
            'illustration': self.illustration
        }
        if include_choices:
            data['choices'] = [choice.to_dict() for choice in self.choices]
        return data

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    next_page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'page_id': self.page_id,
            'text': self.text,
            'next_page_id': self.next_page_id
        }