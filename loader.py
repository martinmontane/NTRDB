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
with open('html/edit.html') as f:
    editpage = f.read()
with open('html/manage.html') as f:
    managepage = f.read()
print("Pages loaded, loading 3dsdb")
