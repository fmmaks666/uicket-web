from flask import Flask, request, make_response, render_template
from api import api
from json import dumps

app = Flask(__name__)
app.register_blueprint(api.api, url_prefix="/api")


@app.route("/")
def index():
    favorites = request.cookies.get("Favorites")
    if favorites is None:
        default_favorites = []
        formatted = dumps(default_favorites)
        response = make_response(render_template("index.html"))
        response.set_cookie("Favorites", formatted)
        return response
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
