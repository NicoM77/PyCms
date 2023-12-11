from flask import Flask, render_template, abort, request, send_from_directory, url_for, redirect, session, send_file, jsonify, Response
import json, requests, datetime, manager, os, random

application = Flask(__name__)
application.secret_key = os.urandom(128).hex()

UPLOAD_FOLDER = 'static/images/upload'
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@application.route("/")
@application.route("/<path:page>")
@application.route("/<path:page>/")
def home(page="home"):
    page_name ,page_route = get_page(page)
    if not page_name == False:
        if not page_name == "Header":
            module_content, pages, module_templates = get_json()
            if page_name in pages.keys():
                module_name = [list(d.keys())[0] for d in pages[page_name]["module"]]
                module_id = [list(d.values())[0] for d in pages[page_name]["module"]]
                
                heder_text_list = [list(d.keys())[0] for d in pages["Header"]["list"]]
                heder_url_list = [list(d.values())[0] for d in pages["Header"]["list"]]
                return render_template("index.html",
                                        module_content = module_content,
                                        page = pages[page_name],
                                        pages =pages,
                                        page_name = page_name,

                                        module_name = module_name,
                                        module_id =module_id,
                                        module_list_len = range(0,len(module_name)),
            
                                        heder_text_list = heder_text_list,
                                        heder_url_list = heder_url_list,
                                        heder_list_len = range(0,len(heder_text_list))
                                    )
    return render_template("404.html")
@application.route("/cms")
@application.route("/cms/")
def cms():
    if authorited():
        module_content, pages, module_templates = get_json()
        return render_template("cms/cms_home.html", user_data = manager.get_user_data(session["username"]), module_content = module_content, pages =pages )
    else:
        return redirect("/login")
@application.route("/cms/<path:page>")
def cms_page(page):
    if authorited():
        page_name ,page_route = get_page(page)
        if not page_name == False and not page_name == "Header":
            module_content, pages, module_templates = get_json()

            if page_name in pages.keys():
                module_name = [list(d.keys())[0] for d in pages[page_name]["module"]]
                module_id = [list(d.values())[0] for d in pages[page_name]["module"]]
            path = "static/images/"
            
            dateien, ordner = liste_dateien_und_ordner("static/images/")

            media = {"home":dateien}
            meida = files_in_dict("",media,ordner)

        return render_template("cms/cms_page.html",
                                user_data = manager.get_user_data(session["username"]),
                                page_route = page_route,
                                module_content = module_content,
                                pages =pages,
                                page_name = page_name,

                                module_name = module_name,
                                module_id = module_id,
                                module_list_len = range(0,len(module_name)),
                                module_templates = module_templates,
                                media = media,
        )
    else:
            return redirect(f"/login?cms/{page}")
@application.route("/cms/create_page", methods=["GET","POST"])
def create_page():
    if authorited():
        module_content, pages, module_templates = get_json()
        if request.method == "POST":
            try:
                data = request.json
                pages_name = data.get("pages_name")
                page_route = data.get("page_route")
                show_header = data.get("show_header")
                show_footer = data.get("show_footer")
                response = manager.create_page(pages_name, page_route, show_header, show_footer)
                if response == 200:
                    return jsonify({"message": "Erfolgreich"}), 200
                return jsonify({"message": "ERROR"}), 400
            except Exception as e:
                return jsonify({"message": str(e)}), 400
        else:
            return render_template("cms/create_page.html", user_data = manager.get_user_data(session["username"]), module_content = module_content, pages =pages)
    else:
         return redirect("/login?cms/create_page")
@application.route("/cms/header", methods=["GET","POST"])
def edit_cms_header():
    if authorited():
        module_content, pages, module_templates = get_json()
        return render_template("cms/header_edit.html", user_data = manager.get_user_data(session["username"]), module_content = module_content, pages =pages)
    else:
        return redirect("/login?cms/header")
@application.route("/cms/media/")
@application.route("/cms/media/<path:pfad>")
def media(pfad="/"):
    if authorited():
        if not pfad == "/":
            pfad = "/" + pfad + "/"
        dateien, ordner = liste_dateien_und_ordner(application.config['UPLOAD_FOLDER'] + pfad)
        module_content, pages, module_templates = get_json()
        return render_template("cms/cms_media.html", user_data = manager.get_user_data(session["username"]), module_content = module_content, pages =pages, files = dateien, folder = ordner, pfad = pfad)
    else:
        if not pfad == "/":
            pfad = "/" + pfad
        return redirect(f"/login?cms/media{pfad}")
@application.route("/logout")
def logout():
    if "username" in session and "session_token" in session:
        username = session["username"]
        session["username"] = ""
        session["session_token"] = ""
        
        manager.temp_add_hash(username, "logout")
        return redirect("/")
    return redirect("/")
@application.route("/login",methods = ["GET","POST"])
def login():
    if request.method == "POST":
        data = request.json
        
        if data:
            username = data.get("username")
            password = data.get("password")
            login = manager.login(username,password)
            
            if login == False:
                return jsonify({"message": "Ungültige Anmeldeinformationen"}), 400
            else:
                session_token = os.urandom(128).hex()
                manager.temp_add_hash(username, session_token)
                session["username"] = username
                session["session_token"] = session_token
                return jsonify({"message": "Erfolgreich"}), 200

    else:
        return render_template("login.htm")
@application.route("/base")
def base():
    return render_template("base.html")
@application.route("/api/get_img/<path:img>")
def send_image(img):
    if img =="upload/img":
        img = "hero_default_background.jpg"
    teile = img.split("/")
    if "home" in teile:
        teile.remove("home")
        img = "/".join(teile)
    images_folder = "static/images/"
    requested_path = os.path.abspath(os.path.join(images_folder, img))

    if os.path.isfile(requested_path) and requested_path.startswith(os.path.abspath(images_folder)) and os.path.splitext(requested_path)[1].lower() in [".mp4", ".png", ".jpg",".webp",".jpeg"]:
        return send_file(requested_path)
    else:
        print("Datei nicht gefunden oder nicht erlaubter Pfad.")
        return "Datei nicht gefunden oder nicht erlaubter Pfad."
@application.route("/api/header_change/", methods=["POST"])
def api_header_change():
    module_content, pages, module_templates = get_json()
    try:
        data = request.json
        daten = data.get("data")
        if len(daten) > 0:
            pages["Header"]["list"] = daten
            with open("json/pages.json", "w") as f:
                json.dump(pages, f, indent=2)
            return jsonify({"message": "Erfolgreich","redirect":"/cms"}), 200
        
        
        return jsonify({"message": "ERROR"}), 400
    except Exception as e:
         return jsonify({"message": str(e)}), 400
@application.route("/api/change/", methods=["POST"])
def api_change():
    module_content, pages, module_templates = get_json()
    try:
        data = request.json
        where = data.get("where")
        page = data.get("page")
        key = data.get("key")
        value = data.get("value")
        if where == "pages.json":
            if page == "Header":
                if key in pages[page].keys():
                    pages[page][key] = value
                    with open("json/pages.json", "w") as f:
                        json.dump(pages, f, indent=2)
                    return jsonify({"message": "Erfolgreich"}), 200
            elif page in pages.keys():
                if key in pages[page].keys():
                    pages[page][key] = value
                    with open("json/pages.json", "w") as f:
                        json.dump(pages, f, indent=2)
                    return jsonify({"message": "Erfolgreich"}), 200
                if key == "page_name":
                    data = pages
                    data[value] = pages[page]
                    del data[page]
                    with open("json/pages.json", "w") as f:
                        json.dump(data, f, indent=2)
                    return jsonify({"message": "Erfolgreich"}), 200   
        elif where == "content.json":
            if page in module_content.keys():
                if key in module_content[page].keys():
                    module_content[page][key] = value
                    with open("json/module_content.json", "w") as f:
                        json.dump(module_content, f, indent=2)
                    return jsonify({"message": "Erfolgreich"}), 200

        return jsonify({"message": "ERROR"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 400
@application.route("/api/create", methods=["POST"])
def api_create():
    module_content, pages, module_templates = get_json()
    try:
        data = request.json
        key = data.get("key")
        page_name = data.get("page")
        name = data.get("name")
        if key == "module":
            if name in module_templates.keys():
                if page_name in pages.keys():
                    module_id = str(modules_id_counter())
                    pages[page_name]["module"].append({str(name):module_id})
                    module_content[module_id] = module_templates[name]

                    with open("json/pages.json", "w") as f:
                        json.dump(pages, f, indent=2)
                    with open("json/module_content.json", "w") as f:
                        json.dump(module_content, f, indent=2)
                    return jsonify({"message": "Erfolgreich"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 400
@application.route("/api/delete", methods=["POST"])
def api_delete():
    module_content, pages, module_templates = get_json()
    try:
        data = request.json
        what = data.get("what")
        page_name = data.get("page_name")
        module_id = data.get("module_id")
        if what == "Module":
            if page_name in pages.keys():
                for module in range(0,len(pages[page_name]["module"])):
                    for module_key in pages[page_name]["module"][module].keys():
                        if str(module_id) == pages[page_name]["module"][module][module_key]:
                            del pages[page_name]["module"][module]
                            with open("json/config.json") as f:
                                config = json.load(f)
                            config["delted_modules"].append(int(module_id))
                            config["delted_modules"] = sorted(config["delted_modules"])
                            with open("json/config.json", "w") as f:
                                json.dump(config, f, indent=2)
                            with open("json/pages.json", "w") as f:
                                json.dump(pages, f, indent=2)
                            return jsonify({"message": "Erfolgreich","redirect":"reload"}), 200
        elif what == "Page":
            print(1)
            if page_name in pages.keys():
                print(pages[page_name]["route"])
                print(module_id)
                if pages[page_name]["route"] == module_id:
                    print(1)
                    del pages[page_name]
                    with open("json/pages.json", "w") as f:
                        json.dump(pages, f, indent=2)
                    return jsonify({"message": "Erfolgreich","redirect":"/cms"}), 200


        return jsonify({"message": "ERROR"}), 400
    except Exception as e:
         return jsonify({"message": str(e)}), 400
@application.route("/api/properties", methods = ["GET","POST"])
def api_reload():
    module_content, pages, module_templates = get_json()
    to_edit = []
    for page in pages:
        if not "Header" == page:
            for module in range(0, len(pages[page]["module"])):
                for module_name in pages[page]["module"][module].keys():
                    module_id = pages[page]["module"][module][module_name]
                    for properties in module_templates[module_name]:
                        if not properties in module_content[module_id]:
                            to_edit.append({module_id: properties})
    for modul in range(0, len(to_edit)):
        for modul_id in to_edit[modul]:
            propertie = to_edit[modul][modul_id]
            module_content[modul_id][propertie] = "nothing"
            with open("json/module_content.json", "w") as f:
                json.dump(module_content, f, indent=2)
    return to_edit
@application.route('/api/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        path = request.form['path']
        if 'file' not in request.files:
            return jsonify({"message": "ERROR: No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "ERROR: No selected file"}), 400
        print(file.filename.rsplit('.', 1)[1].lower() in {"png", "jpg", "mp4"})
        if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in {"png", "jpg", "mp4"}:
            file.save(os.path.join(application.config['UPLOAD_FOLDER']+ path, file.filename))
            return jsonify({"message": "successful"}), 200
        else:
            return jsonify({"message": "ERROR: File type not allowed"}), 400
@application.route("/console")
def console():
    return redirect("/404")
@application.route("/restart")
def restart():
    open("restart", "w")
    return "Erfolgreich Gestartet"
@application.errorhandler(404)
def not_found(e):
    return render_template("404.html")
@application.errorhandler(500)
def not_found_500(e):
    return render_template("404.html")
def authorited():
    if "username" in session and "session_token" in session:
        if manager.authorized(session["username"],session["session_token"]) == True:
            return True
def get_page(input_route):
    with open("json/pages.json") as f:
        pages = json.load(f)
    for page in pages.keys():
        if pages[page]["route"] == "/" + str(input_route):
            return page, pages[page]["route"]
        
    return False, False
def get_json():
    with open("json/module_content.json") as f:
        module_content = json.load(f)
    with open("json/pages.json") as f:
        pages = json.load(f)
    with open("json/config.json") as f:
        module_templates = json.load(f)
        module_templates = module_templates["module_templates"]



    return module_content, pages, module_templates
def modules_id_counter():
    with open("json/module_content.json") as f:
        module_content = json.load(f)
    repeat = True
    counter = 0
    while repeat == True:
        counter = counter + 1 
        if not str(counter) in module_content.keys():
            
            repeat = False
        
    return counter
def create_full_path(relative_path):
    current_directory = os.getcwd()  # Aktuelles Arbeitsverzeichnis
    full_path = current_directory  + relative_path
    return full_path
def liste_dateien_und_ordner(pfad):
    dateien = []
    ordner = []

    for element in os.listdir(pfad):
        element_pfad = os.path.join(pfad, element)
        if os.path.isfile(element_pfad):
            dateien.append(element)
        elif os.path.isdir(element_pfad):
            ordner.append(element)

    return dateien, ordner
def files_in_dict(path, media, dict):
    for ordner_one in dict:
        if ordner_one != "user_profile":
            dateien, ordner = liste_dateien_und_ordner("static/images"+path+"/"+ordner_one)
            if path == "":
                media[ordner_one] = dateien
            else:
                media[path[1:] +"/"+ ordner_one] = dateien
            if not len(ordner) == 0:
                media = files_in_dict(path +"/"+ ordner_one, media, ordner)
            else:
                return media
    return media


if __name__ == "__main__":
    application.run(host="0.0.0.0", debug=True, port=5000)
 