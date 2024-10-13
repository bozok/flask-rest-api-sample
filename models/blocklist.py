from db import db

class BlockList(db.Model):
    __tablename__ = 'blocklist'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)