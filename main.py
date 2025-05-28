from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy #ORM
from datetime import datetime

app = Flask(__name__)

# Create Databse using SQLite and name is journal.db
# file gets created inside instance/ folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///journal.db"

# initialize the database, connecting SQLAlchemy to the Flask app
db = SQLAlchemy(app)

# Create JournalEntry model in database
class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    mood = db.Column(db.String(50), nullable=False)
    entry = db.Column(db.String(150), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    activity = db.Column(db.String(50), nullable=False) 
    private = db.Column(db.Boolean, default=True) 

    #converts JournalEntry object to a dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),
            "mood": self.mood,
            "entry": self.entry,
            "title": self.title,
            "activity": self.activity,
            "private": self.private
        }

# creates table in SQLite database 
with app.app_context():
    db.create_all() 


# Create Routes

# welcome message on home page
@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Journal API!"})

# gets all entries by quering all rows in the table, turns them into json 
@app.route("/entries", methods=["GET"])
def get_entries():
    entries = JournalEntry.query.all() 
    return jsonify([entry.to_dict() for entry in entries])

# getting a specific entry by ID if it exists, otherwise return error not found
@app.route("/entries/<int:entry_id>", methods=["GET"])
def get_entry(entry_id):
    entry = JournalEntry.query.get(entry_id)
    if entry:
        return jsonify(entry.to_dict())
    else: 
        return jsonify({"error": "Entry not found!"}), 404

# POST
# creating a new journal entry, request.get_json() reads data from the frontend
@app.route("/entries", methods=["POST"])
def add_entry():
    data = request.get_json()

    new_entry = JournalEntry(
        title=data["title"], 
        entry=data["entry"],
        mood=data["mood"],
        activity=data["activity"],
        private=data.get("private", True)
    ) 

    db.session.add(new_entry)
    db.session.commit() 

    return jsonify(new_entry.to_dict()), 201

# PUT or update
@app.route("/entries/<int:entry_id>", methods=["PUT"])
def update_entry(entry_id):
    # gets data from frontend
    data = request.get_json() 
    # finds existing entry by ID
    entry = JournalEntry.query.get(entry_id)
    if entry:
        entry.title = data.get("title", entry.title)
        entry.entry = data.get("entry", entry.entry)
        entry.mood = data.get("mood", entry.mood)
        entry.activity = data.get("activity", entry.activity)
        entry.private = data.get("private", entry.private)

        db.session.commit()

        return jsonify(entry.to_dict())
    else: 
        return jsonify({"error": "Entry not found!"}), 404 
    
# DELETE
@app.route("/entries/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    # find general entry in database
    entry = JournalEntry.query.get(entry_id)
    # if found, SQLAlchemy deletes it and save change to db
    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"message":"entry was deleted!"})
    else:
        return jsonify({"error": "Entry not found!"}), 404
    
        



if __name__ == "__main__":
    app.run(debug=True)