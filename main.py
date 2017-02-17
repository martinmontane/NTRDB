import smtplib
from email.mime.text import MIMEText
from http.server import HTTPServer, BaseHTTPRequestHandler
from pprint import pprint
from http.cookies import BaseCookie
import pickle
from os.path import exists
import datetime
from urllib.parse import unquote
from json import dumps
import hashlib
from socketserver import ThreadingMixIn
import threading
from subprocess import check_output
import xml.etree.ElementTree as ET
from html import escape
from uuid import uuid4
from urllib.request import urlopen
from validators import url, email
import mailsettings


def computeMD5hash(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()

if exists('plugins.pickle'):
    with open('plugins.pickle', 'rb') as f:
        plugins = pickle.load(f)
else:
    with open('plugins.pickle', 'wb') as f:
        pickle.dump(
            {
                0: None,
            },
            f)
    print(
        "Plugin database wasnt found. The one were created, to apply it please restart NTRDB")
    raise SystemExit
if exists('users.pickle'):
    with open('users.pickle', 'rb') as f:
        users = pickle.load(f)
else:
    print(
        'Looks like you are running NTRDB first time or you removed users.pickle file.')
    print('Please set admin password.')
    pword = computeMD5hash(input())
    with open('users.pickle', 'wb') as f:
        pickle.dump(
            {
                'Admin': [pword, True],
            },
            f)
    print(
        "Please restart NTRDB to apply changes")
    raise SystemExit
with open('resources/favicon.png', 'rb') as f:
    icon = f.read()
with open('html/index.html') as f:
    index = f.read()
with open('html/desc.html') as f:
    desc = f.read()
with open('html/base.html') as f:
    base = f.read()
with open('html/message.html') as f:
    messagehtml = f.read()
with open('html/addfile.html') as f:
    addfile = f.read()
with open('html/links.html') as f:
    links = f.read()
with open('html/nbar_loggedin.html') as f:
    nbar_loggedin = f.read()
with open('html/nbar_login.html') as f:
    nbar_login = f.read()
with open('html/register.html') as f:
    reg_page = f.read()
with open('html/login.html') as f:
    login_page = f.read()
with open('resources/MailRegText.txt') as f:
    actmsg = f.read()
print("Pages loaded, loading 3dsdb")
titles = ET.fromstring(
    str(urlopen('http://3dsdb.com/xml.php').read(), 'utf-8'))
print("3DSDB loaded, optimising it...")
tids = []
for item in titles:
    tids.append([item[1].text, item[8].text])
del titles
print("DONE!")
print("Checking DB for required keys...")
for item in plugins:
    if not item == 0:
        if not 'pic' in plugins[item]:
            plugins[item]['pic'] = ""
        plugins[item]['TitleID'] = plugins[item]['TitleID'].upper()
with open('plugins.pickle', 'wb') as f:
    pickle.dump(plugins, f)
version = str(
    check_output('git log -n 1 --pretty=format:"%h"', shell=True), 'utf-8')
print("Connecting to mail server...")
try:
    mailsrv = smtplib.SMTP_SSL(
        host=mailsettings.smtpserver, port=mailsettings.smtpport)
    print("Logging in...")
    mailsrv.login(mailsettings.user, mailsettings.password)
    print("Logged in!")
except smtplib.SMTPException as e:
    print("There was an error connecting to mail server!")
    raise e
    raise SystemExit

def parseURL(path):
    try:
        data = path.split("?")[1].split("&")
        parsed = {}
        for item in data:
            i = item.split("=")
            parsed[i[0]] = escape(unquote(i[1].replace('+', ' ')))
    except Exception:
        parsed = {}
    finally:
        return parsed


def parseCookie(header):
    if 'Cookie' in header:
        cookies_raw = header["Cookie"].split('; ')
        cookies = {}
        for item in cookies_raw:
            cookie = item.split('=')
            cookies[cookie[0]] = cookie[1].replace('"', '')
        return cookies
    else:
        return {}


def getgamebytid(tid):
    ok = False
    for item in tids:
        if item[1] == tid:
            return item[0]
            ok = True
    if not ok:
        return "Game TitleID hasnt found in 3DSDB :("


class myHandler(BaseHTTPRequestHandler):
    def activate(self):
        args = parseURL(self.path)
        if 'id' in args:
            uid = args['id']
            for user in users:
                user = users[user]
                if user[1] == uid:
                    page = base % (version, "", messagehtml %
                           ('success', 'You successfully activated account!'))
                    user[1] = True
                    succ = True
                    with open('users.pickle', 'wb') as f:
                        pickle.dump(users, f)
                    break
        else:
            succ = False
        if succ:
            page = base % (version, "", messagehtml %
                           ('success', 'You successfully activated account!'))
        else:
            page = base % (version, "", messagehtml %
                               ('danger', 'Looks like you got bad link :('))
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(page, 'utf-8'))

    def description(self):
        parsed = parseURL(self.path)
        if "id" in parsed:
            gid = int(parsed["id"])
            if gid in plugins and not gid == 0:
                item = plugins[gid]
                name = str(item['name'])
                ver = str(item['version'])
                dev = str(item['developer'])
                gamename = str(getgamebytid(item['TitleID']))
                tid = str(item['TitleID'])
                devsite = str(item['devsite'])
                dlink = str(item['plg'])
                descr = str(item['desc'])
                cpb = str(item['compatible'])
                if not str(item['pic']) == "":
                    pic = "<p>Screenshot:</p><img src=\"%s\">" % (
                        str(item['pic']))
                else:
                    pic = ""
                succ = True
        else:
            succ = False
        if succ:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            page = base % (version,
                           desc % (
                               name, cpb, ver, dev, gamename, tid, devsite, dlink, descr, pic)
                           )
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            page = base % (version, messagehtml %
                           ('danger', 'Oops! Looks like you got bad link'))
        self.wfile.write(bytes(page, 'utf-8'))

    def api(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        apidata = {}
        copy = dict(plugins)
        for item in copy:
            if not item == 0:
                plugin = copy[item]
                apidata[item] = plugin
                try:
                    del apidata[item]["__removal_id"]
                except Exception:
                    pass
                else:
                    pass
        self.wfile.write(bytes(dumps(apidata), 'utf-8'))

    def index(self):
        table = ""
        message = ""
        isSearch = False
        path = self.path[1:]
        if not len(path.split("?")) == 1:
            parsed = parseURL(self.path)
            if 'search' in parsed:
                query = str(parsed['search'])
                isSearch = True
                results = []
                for item in plugins:
                    if not item == 0:
                        num = item
                        plugin = plugins[item]
                        plugin['id'] = num
                        if str(plugin['TitleID']).startswith(query) or query.upper() in str(plugin['name']).upper() or query.upper() in str(getgamebytid(plugin["TitleID"])).upper():
                            results.append(plugin)
                for item in results:
                    if not item["TitleID"] == "Not game":
                        name = getgamebytid(item["TitleID"])
                    else:
                        name = ""
                    table = table + links % (
                        name,
                        item["name"],
                        item["compatible"],
                        item["added"],
                        item['plg'],
                        item['devsite'],
                        item['id']
                    )

        if not isSearch:
            for item in plugins:
                if not item == 0:
                    idnum = item
                    item = plugins[item]
                    if not item["TitleID"] == "Not game":
                        name = getgamebytid(item["TitleID"])
                    else:
                        name = ""
                    table = table + links % (
                        name,
                        item["name"],
                        item["compatible"],
                        item["added"],
                        item['plg'],
                        item['devsite'],
                        idnum
                    )
        if 'Auth' in self.cookies:
            nbar = nbar_loggedin
        else:
            nbar = nbar_login
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        page = base % (version, nbar, index % (table))
        self.wfile.write(bytes(page, 'utf-8'))

    def additem(self):
        message = ""
        parsed = parseURL(self.path)
        if 'add' in parsed:
            plgp = parsed["link"]
            titleid = parsed['tid'].upper()
            plugname = parsed['name']
            developer = parsed['developer']
            devsite = parsed['devsite']
            desc = parsed['desc']
            ver = parsed['ver']
            cpb = parsed['ctype']
            pic = parsed['pic']
            badreq = False
            if plgp == "":
                message = "You havent entered path to plg file!"
                badreq = True
                succ = False
            if titleid == "":
                titleid = "Not game"
            elif not len(titleid) == 16:
                message = "You entered bad TitleID!"
                badreq = True
                succ = False
            if plugname == "":
                message = "You havent entered plugin's name!"
                badreq = True
                succ = False
            if not url(plgp) is True or not url(pic) is True or url(devsite):
                message = "You entered bad URL!"
                badreq = True
                succ = False
            plgp = plgp
            for item in plugins:
                if not item == 0:
                    plugin = plugins[item]
                    if plugin['plg'] == plgp and plugin['TitleID'] == titleid and plugin['Compatible'] == cpb and plugin['verion'] == ver:
                        badreq = True
                        succ = False
                        message = "Plugin already exists!"
                        break
            if not badreq:
                now = datetime.datetime.now()
                plugins[max(plugins) + 1] = {'TitleID': titleid,
                                             'name': plugname,
                                             'developer': developer,
                                             'devsite': devsite,
                                             'desc': desc,
                                             'plg': plgp,
                                             'added': now.strftime("%Y-%m-%d %H:%M"),
                                             'timestamp': now.timestamp(),
                                             'version': ver,
                                             'compatible': cpb,
                                             'pic': pic
                                             }
                with open('plugins.pickle', 'wb') as f:
                    pickle.dump(plugins, f)
                message = "Added your plugin!"
                succ = True
            if succ:
                message = messagehtml % ('success', message)
            else:
                message = messagehtml % ('danger', message)
            page = base % (version, message)
        else:
            page = base % (version, addfile)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(page, 'utf-8'))

    def register(self):
        if 'AToken' in self.cookies:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            page = base % (
                version, "", "<META HTTP-EQUIV=\"refresh\" CONTENT=\"1; URL=index\">")
            self.wfile.write(bytes(page, 'utf-8'))
        else:
            parsed = parseURL(self.path)
            if parsed == {}:
                page = base % (version, "", reg_page)
            else:
                pwordh = computeMD5hash(parsed['pword'])
                mail = parsed['email']
                del parsed  # FORGET PASSWORD
                # Btw, it useless, because we cant remove self.path(I think)
                # But it frees some memory so it is good!
                if mail in users:
                    page = base % (
                        version, "", messagehtml % ('danger', "This email is already registered"))
                else:
                    users[mail] = [pwordh, str(uuid4())]
                    msg = MIMEText(actmsg % (mail, users[mail][1]))
                    msg['Subject'] = 'Confirm activation on NTRDB'
                    msg['From'] = mailsettings.user
                    msg['To'] = mail
                    mailsrv.send_message(msg)
                    page = base % (version, "", messagehtml % (
                        'info', "You almost registered! Now please check your email for activation message from ntrdb@octonezd.pw!"))
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(page, 'utf-8'))

    def do_GET(self):
        self.cookies = parseCookie(dict(self.headers))
        pprint(self.cookies)
        try:
            if self.path.startswith('/api'):
                self.api()
            elif self.path.startswith('/additem'):
                self.additem()
            elif self.path.startswith('/description'):
                self.description()
            elif self.path.startswith('/reg'):
                self.register()
            elif self.path.startswith('/activate'):
                self.activate()
            elif self.path.startswith('/favicon'):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(icon)
            elif self.path.startswith('/error'):
                1 / 0
            else:
                self.index()
        except Exception as e:
            print(e)
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            page = base % (version, "", messagehtml %
                           ('danger', 'Oops! An error occured when processing your request!'))
            self.wfile.write(bytes(page, 'utf-8'))


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):

    """Handle requests in a separate thread."""


try:
    # Create a web server and define the handler to manage the
    # incoming request
    server = ThreadedHTTPServer(('', 8080), myHandler)
    print('Started httpserver')

    # Wait forever for incoming htto requests
    server.serve_forever()
except KeyboardInterrupt:
    pass
