import flask
from sqlite3 import dbapi2 as sqlite3


DEBUG = True
DATABASE = "/tmp/urlshortener.db"


app = flask.Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar("URLSHORTENER_SETTINGS", silent=True)


def init_database():
    with sqlite3.connect(app.config["DATABASE"]) as connection:
        with app.open_resource("schema.sql", mode="r") as f:
            connection.cursor().executescript(f.read())


def get_database_connection():
    if not hasattr(flask.g, "database_connection"):
        flask.g.database_connection = sqlite3.connect(app.config["DATABASE"])
    return flask.g.database_connection


@app.teardown_appcontext
def close_database_connection(exception):
    if hasattr(flask.g, "database_connection"):
        flask.g.database_connection.close()


@app.route("/", methods=["GET"])
def urlshortener():
    return flask.render_template("urlshortener.html", short_url=None)


@app.route("/", methods=["POST"])
def urlshortener_shorten():
    connection = get_database_connection()

    cursor = connection.execute("update entries set long_url=? where long_url=?",
            [flask.request.form["long_url"], flask.request.form["long_url"]])
    connection.commit()

    if not cursor.rowcount:
        cursor = connection.execute("insert into entries (long_url) values (?)",
                [flask.request.form["long_url"]])
        connection.commit()

    cursor = connection.execute("select short_url from entries where long_url=?",
            [flask.request.form["long_url"]])

    short_url = "{}{}".format(flask.request.url_root, cursor.fetchone()[0])

    return flask.render_template("urlshortener.html", short_url=short_url)


@app.route("/<path:short_url>", methods=["GET"])
def urlshortener_lengthen(short_url):
    connection = get_database_connection()

    cursor = connection.execute("select long_url from entries where short_url=?",
            [short_url])

    long_url = cursor.fetchone()[0]

    return flask.redirect(long_url)


if __name__ == "__main__":
    app.run()
