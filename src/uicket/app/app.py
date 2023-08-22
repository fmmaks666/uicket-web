from flask import Flask, request, make_response, render_template
from .api import api
from json import dumps, loads


app = Flask(__name__)
app.register_blueprint(api, url_prefix="/api")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/favorites")
def favorites():
    favorites = request.cookies.get("Favorites")
    if favorites is None or not favorites:
        default_favorites = []
        formatted = dumps(default_favorites)
        response = make_response(render_template("index.html", has_content=False))
        response.set_cookie("Favorites", formatted)
        return response
    return render_template("favorites.html", has_content=bool(loads(favorites)))


if __name__ == "__main__":
    app.run(debug=True)
