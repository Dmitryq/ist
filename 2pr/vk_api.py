import requests
import concurrent.futures
import json
from api_token import *

token = api_token
inputDict = {}

headers = {
    "Content-Type": "application/x-www-form-encoded",
}

rootUsers = ["134389972", "192371383"]

def getUserInfo(token, user):
    url = f"https://api.vk.ru/method/users.get?access_token={token}&user_ids={user}&v=5.199"
    response = requests.post(url, headers=headers)
    try:
        return response.json().get('response')
    except:
        pass

def getUserGroups(token, user):
    url = f"https://api.vk.ru/method/users.getSubscriptions?access_token={token}&user_id={user}&v=5.199&extended=1"
    response = requests.post(url, headers=headers)
    try:
        return response.json().get('response').get('items')
    except:
        pass


def getUserFriends(token, user):
    url = f"https://api.vk.ru/method/friends.get?access_token={token}&user_id={user}&v=5.199"
    response = requests.post(url, headers=headers)
    try:
        return response.json().get('response').get('items')
    except:
        pass


def getAllUsers(output, token, userList, depth):
    if depth == 0:
        return output
    if userList != None:
        for user in userList:
                output[user] = {}
                output[user]["info"] = getUserInfo(token, user)
        for user in userList:
                print("current ->>>>>>>>>>>>>", user)
                output[user]["friends"] = getAllUsers({}, token, getUserFriends(token, user), depth - 1)
    return output #КРАСИВО НО ООООЧЕНЬ ДОЛГО
   

def simpleParse(token, users):
    output = []
    for user in users:
        friends = getUserFriends(token, user)
        if friends != None:
            output.extend(friends)
            for friend in friends:
                friendFriends = getUserFriends(token, friend)
                if friendFriends != None:
                    output.extend(friendFriends)
    return output


def fetch_user_data(token, user):
    user_data = {}
    user_data["info"] = getUserInfo(token, user)
    user_data["groups"] = getUserGroups(token, user)
    return user, user_data

def userInfoGroups(token, users):
    output = {}
    length = len(users)
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_user = {executor.submit(fetch_user_data, token, user): user for user in users}
        counter = 0
        for future in concurrent.futures.as_completed(future_to_user):
            user = future_to_user[future]
            try:
                user, user_data = future.result()
                output[user] = user_data
                counter += 1
                print(f"current ->>>> {user}")
                print(f"{counter} / {length}")
            except Exception as e:
                print(f"Error fetching data for {user}: {e}") #40МИНУТ
    return output


out = userInfoGroups(token, simpleParse(token, rootUsers))


with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=4)
