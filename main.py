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

def authorited():
    if "username" in session and "session_token" in session:
        if pw_manager.authorized(session["username"],session["session_token"]) == True:
            return True
if __name__ == "__main__":
    application.run(host="0.0.0.0", debug=True, port=5000)
