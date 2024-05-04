import flask
import sqlite3
numOfColumns = 3

app = flask.Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if flask.request.method == "GET":
        conn = sqlite3.connect("posts.db")
        #display from largest id to smallest id, so can display newest posts first
        cursor = conn.execute("""SELECT * FROM Post ORDER BY PostID DESC""")
        cursor2 = conn.execute("""SELECT COUNT(*) FROM Post""")
        
    else: #POST
        search = flask.request.form["thesearch"]
        conn = sqlite3.connect("posts.db")
        cursor = conn.execute("""SELECT * FROM Post 
                            WHERE (Artist LIKE ?) OR (Description LIKE ?) OR (Tags LIKE ?)
                            ORDER BY PostID DESC""",
                            ("%"+search+"%","%"+search+"%","%"+search+"%"))
        cursor2 = conn.execute("""SELECT COUNT(*) FROM Post
                            WHERE (Artist LIKE ?) OR (Description LIKE ?) OR (Tags LIKE ?)""",
                            ("%"+search+"%","%"+search+"%","%"+search+"%"))
    images = []
    currentPair = []
    for post in cursor:
        if len(currentPair) == numOfColumns: 
            images.append(currentPair)
            currentPair = []
            currentPair.append((post[0], post[1]))
        else:
            currentPair.append((post[0], post[1]))
    if len(currentPair) != 0:
        images.append(currentPair)
    print(images)

    for data in cursor2:
        num = data[0]
    num = num%3
    if num == 0:
        num = 3

    conn.close()
    return flask.render_template("home.html", images=images, num=num)

@app.route("/post/", methods=["GET","POST"])
def post():
    #GET
    if flask.request.method == "GET":
        return flask.render_template("form.html")
    #POST
    imgLink = flask.request.form["imgLink"]
    artist = flask.request.form["artist"]
    desc = flask.request.form["desc"]
    tags = flask.request.form["tags"] #not filtered yet. in the db it will remain as one string. when displaying the post then we split and lower and strip

    #insert new post into db
    conn = sqlite3.connect("posts.db")
    conn.execute("""INSERT INTO Post(ImgLink, Artist, Description, Tags) 
                    VALUES(?,?,?,?)""", (imgLink, artist, desc, tags))
    conn.commit()
    conn.close()
    #go back to /
    return flask.redirect(flask.url_for("success"))

@app.route("/view/<int:i>", methods=["GET"])
def view(i):
    conn = sqlite3.connect("posts.db")
    cursor = conn.execute("""SELECT * FROM Post WHERE PostID = ?""", (i,))
    for post in cursor: #only for one post, because there is a return statement
        imgLink = post[1]
        artist = post[2]
        desc = post[3]
        tagsStr = post[4]
        tags = []
        tagsStr = tagsStr.split(",")
        for tag in tagsStr:
            tag = tag.strip()
            tags.append(tag)
        return flask.render_template("view.html", imgLink=imgLink,
                                     artist=artist, desc=desc,
                                     tags=tags)
    conn.close()

@app.route("/success", methods=["GET"])
def success():
    return flask.render_template("success.html")

if __name__ == "__main__":
    app.run()
