import json

def login(name, pw):
    with open("json/login_daten.json") as f:
       data = json.load(f)
    if name in data["login"].keys():
        if data["login"][name]["pw"] == pw:
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
        print(username)
        user = data["login"][username]
        user["username"] = username
        del user["pw"]
        return user



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