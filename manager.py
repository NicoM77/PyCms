import json, hashlib

def login(name, pw):
    with open("json/login_daten.json") as f:
       data = json.load(f)
    if name in data["login"].keys():
        if data["login"][name]["pw"] == hash_password(data["login"]["prefix"]+"_"+pw+"_"+data["login"][name]["token"]):
            return True
        else:
            return False
    return False
def temp_add_hash(username, hash):
    with open("json/config.json") as f:
       data = json.load(f)
    data["temp"][username] = hash
    with open("json/config.json", "w") as f:
        json.dump(data, f, indent=2)
def create_page(page_name:str, page_route:str, show_header:bool, show_footer:bool):
    try:
        with open("json/pages.json") as f:
            pages = json.load(f)
        if not page_name in pages.keys():
            pages[page_name] = {
                "route":page_route,
                "icon":"fa-regular fa-clock",
                "show_header": show_header,
                "show_footer": show_footer,
                "module":[]
            }
            with open("json/pages.json", "w") as f:
                json.dump(pages, f, indent=1)
            return 200
        return 404
    except Exception as e:
        return 404
def authorized(username, hash):
    with open("json/config.json") as f:
       data = json.load(f)
    if username in data["temp"].keys():
        if data["temp"][username] == hash:
            return True    
    return False
def get_user_data(username):
    with open("json/login_daten.json") as f:
        data = json.load(f)
    if username in data["login"].keys():
        user = data["login"][username]
        user["username"] = username
        del user["pw"]
        return user
def hash_password(password):
    password_bytes = password.encode('utf-8')
    hashed = hashlib.sha256(password_bytes).hexdigest()
    while len(hashed) < 2048:
        hashed += hashlib.sha256(hashed.encode('utf-8')).hexdigest()
    hashed = hashed[:2048]    
    return hashed
# def permissions(name,site):
#     with open("json/login_daten.json") as f:
#        data = json.load(f)
#     if site in data["permissions"]["sites"].keys() and name in data["login"].keys():
#         if data["permissions"]["sites"][site] <= data["login"][name]["permissions"]:
#             return True
#         else:
#             return None
#     else:
#         return None
# def permissions_get(name):
#     with open("json/login_daten.json") as f:
#        data = json.load(f)
#     if name in data["login"].keys():
#         return {
#             "user":data["login"][name]["permissions"]}
#     else:
#         return None