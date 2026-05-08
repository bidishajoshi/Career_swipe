from app import app

def debug():
    with app.app_context():
        uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        # Safety: mask the password
        if "@" in uri:
            display = uri.split("@")[-1]
            print(f"DEBUG: The App is currently using: {display}")
        else:
            print(f"DEBUG: The App is currently using: {uri}")

if __name__ == "__main__":
    debug()
