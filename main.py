from flask import Flask, render_template, abort, request, url_for, redirect, session, send_file, jsonify, Response
import json, requests, datetime, pw_manager, os, random

application = Flask(__name__)
application.secret_key = os.urandom(128).hex()



@application.route("/")
@application.route("/<page>")
def home(page="home"):
    if not page == "header" or not page == "footer":
        module_content, pages = get_json()
        if page in pages.keys():
            module_name = [list(d.keys())[0] for d in pages[page]["module"]]
            module_id = [list(d.values())[0] for d in pages[page]["module"]]
            
            heder_text_list = [list(d.keys())[0] for d in pages["header"]["list"]]
            heder_url_list = [list(d.values())[0] for d in pages["header"]["list"]]
            return render_template("index.html",
                                    module_content = module_content,
                                    page = pages[page],

                                    module_name = module_name,
                                    module_id =module_id,
                                    module_list_len = range(0,len(module_name)),
        
                                    heder_text_list = heder_text_list,
                                    heder_url_list = heder_url_list,
                                    heder_list_len = range(0,len(heder_text_list))
                                )
        else:
            return render_template("404.html")
    else:
            return render_template("404.html")

@application.route("/cms")
def cms():
    if authorited():
        return "CMS"
    else:
        return redirect("/login")


@application.route("/login",methods = ["GET","POST"])
def login():
    if request.method == "POST":
        data = request.json
        
        if data:
            username = data.get("username")
            password = data.get("password")
            login = pw_manager.login(username,password)
            
            if login == False:
                return jsonify({"message": "Ungültige Anmeldeinformationen"}), 400
            else:
                session_token = os.urandom(128).hex()
                pw_manager.temp_add_hash(username, session_token)
                session["username"] = username
                session["session_token"] = session_token
                return jsonify({"message": "Erfolgreich"}), 200

    else:
        return render_template("login.htm")

@application.route("/base")
def base():
    return render_template("base.html")

@application.route("/api/get_img/<img>")
def get_img(img):
    return send_file(f"static/images/{img}")

@application.errorhandler(404)
def not_found(e):
    return render_template("404.html")
@application.errorhandler(500)
def not_found_500(e):
    return render_template("404.html")


def authorited():
    if "username" in session and "session_token" in session:
        if pw_manager.authorized(session["username"],session["session_token"]) == True:
            return True
def get_json():
    with open("json/module_content.json") as f:
        module_content = json.load(f)
    with open("json/pages.json") as f:
        pages = json.load(f)
    return module_content, pages

if __name__ == "__main__":
    application.run(host="0.0.0.0", debug=True, port=5000)
 