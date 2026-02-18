import os
from dotenv import load_dotenv
from hello import app

load_dotenv()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5010)),
        debug=os.getenv("FLASK_ENV") == "development"
    )
