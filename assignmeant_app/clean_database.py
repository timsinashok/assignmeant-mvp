# reset_db.py
from app import db, create_app

# Create the app using your app factory function
app = create_app()

# Run database commands within the app context
with app.app_context():
    # Drop all tables in the database
    db.drop_all()
    print("All tables have been dropped.")

    # Recreate all tables in the database
    db.create_all()
    print("All tables have been recreated.")