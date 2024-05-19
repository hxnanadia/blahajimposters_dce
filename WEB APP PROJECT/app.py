import flask
import sqlite3
numOfColumns = 3
extraFilter = ""
search = ""

app = flask.Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if flask.request.method == "GET":
        conn = sqlite3.connect("posts.db")
        #display from largest id to smallest id, so can display newest posts first
        cursor = conn.execute("""SELECT * FROM Post ORDER BY PostID DESC""")
        
    else: #POST
        global extraFilter, search
        if flask.request.form["thesearch"] != search:
            print("search")
            search = flask.request.form["thesearch"]
        else:
            if flask.request.form["thefilter"] == "isPho":
                print("photo")
                extraFilter = ' AND Type = "Photography" '
            if flask.request.form["thefilter"] == "isIll":
                print("illustration")
                extraFilter = ' AND Type = "Illustration" '
            elif flask.request.form["thefilter"] == "isVid":
                print("vid")
                extraFilter = ' AND Type = "Videography" '
            elif flask.request.form["thefilter"] == "all":
                print("b")
                extraFilter = ""

        print(f'{flask.request.form["thefilter"]} search: {flask.request.form["thesearch"]}')
        
        conn = sqlite3.connect("posts.db")
        cursor = conn.execute("""SELECT * FROM Post 
                            WHERE ((Title LIKE ?) OR (Artist LIKE ?) OR (Description LIKE ?)) """
                            + extraFilter +
                            "ORDER BY PostID DESC",
                            ("%"+search+"%","%"+search+"%","%"+search+"%"))
        
    images = [] #images is not just images anymore
    currentPair = []
    for post in cursor:
        if len(currentPair) == numOfColumns: 
            images.append(currentPair)
            currentPair = []
            currentPair.append((post[0], post[4], post[5]))
        else:
            currentPair.append((post[0], post[4], post[5]))
    if len(currentPair) != 0:
        images.append(currentPair)

    conn.close()
    #search = ""
    return flask.render_template("home.html", images=images, qq=search)

@app.route("/post/", methods=["GET","POST"])
def post():
    #GET
    if flask.request.method == "GET":
        return flask.render_template("form.html")
    #POST
    title = flask.request.form["title"]
    artist = flask.request.form["artist"]
    desc = flask.request.form["desc"]
    type = flask.request.form["type"]
    link = flask.request.form[type+"URL"]
    if link == "":
        return flask.redirect(flask.url_for("failed"))
    
    print("link", link)

    if type == "Videography":
        i = link.find("?v=")
        link = link[i+3:]
    
    #insert new post into db
    conn = sqlite3.connect("posts.db")
    conn.execute("""INSERT INTO Post(Title, Artist, Description, Link, Type) 
                    VALUES(?,?,?,?,?)""", (title, artist, desc, link, type))
    conn.commit()
    conn.close()
    #go back to /
    return flask.redirect(flask.url_for("success"))

@app.route("/view/<int:i>", methods=["GET"])
def view(i):
    conn = sqlite3.connect("posts.db")
    cursor = conn.execute("SELECT * FROM Post WHERE PostID = ?", (i,))
    for post in cursor: #only for one post, because there is a return statement
        title = post[1]
        artist = post[2]
        desc = post[3]
        link = post[4]
        type = post[5]
        tags = []
        tags.append(type)

        tagsStr = desc.split(" ")
        for tag in tagsStr:
            if tag[0] == "#":
                tags.append(tag[1:])
        print(tags)

        for tag in tags:
            desc = desc.replace("#"+tag,"")

        return flask.render_template("view.html", title=title,
                                     artist=artist, desc=desc,
                                     link=link, type=type, tags=tags)
    conn.close()

@app.route("/success", methods=["GET"])
def success():
    return flask.render_template("success.html")

@app.route("/failed", methods=["GET"])
def failed():
    return flask.render_template("failed.html")

@app.route("/about", methods=["GET"])
def about():
    return flask.render_template("aboutLumina.html")

if __name__ == "__main__":
    app.run()
