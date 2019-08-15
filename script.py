#This will read /var/log/auth.log and do some anylysis with it, and then it will save it as an html file on /var/www/html/index.html so that idiots can see it.

import re

logfile = 'logfile'
output = 'script.html'


def find_ip(str):
    ip_pattern = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s')
    ip = re.findall(ip_pattern, str)
    return ip

def find_user(line):
    if 'invalid' in line:
        user = line.split('invalid user ')
    else:
        user = line.split('password for ')
    user = user[1].split(' ')
    return user

def find_good_ips(): #return html list of connected ips
    f = open(logfile,'r')
    contents = f.readlines()
    f.close()
    good_ips = set()
    for line in contents:
        if 'sshd' in line:
            if 'accepted' in line.lower():
                good_ips.add(find_ip(line)[0])

    #Create html
    html = '<h1>List of IPs that have connected:</h1>\n<ul>\n'
    for ip in good_ips:
        html += '<li>' + str(ip) + '</li>\n'
    html += '</ul>\n'
                
    return html


def find_bad_ips(): #return table of bad IP's and attempt count
    f = open(logfile,'r')
    contents = f.readlines()
    f.close()
    bad_ips = []
    ip_d = {}
    for line in contents:
        if 'sshd' in line:
            if 'failed' in line.lower():
                bad_ips.append(find_ip(line)[0])
    for ip in bad_ips:
        if not ip in ip_d:
            ip_d[ip] = 1
        else:
            ip_d[ip] += 1
            
    #Create html
    html = '<h1>Attempted IP Logins:</h1>\n<table>\n<th>IP</th><th>Attempts</th>\n'
    for w in sorted(ip_d, key=ip_d.get, reverse=True):
        html += '<tr><td>' + str(w) + '</td><td>' + str(ip_d[w]) + '</td></tr>\n'
    html += '</table>' 
        
    return html


def find_bad_users(): #return table of failed usernames and counts
    f = open(logfile,'r')
    contents = f.readlines()
    f.close()
    user_d = {}
    usernames = []
    for line in contents:
        if 'sshd' in line:
            if 'failed' in line.lower():
                usernames.append(find_user(line)[0])
    for username in usernames:
        if not username in user_d:
            user_d[username] = 1
        else:
            user_d[username] += 1
            
    #Create html
    html = '<h1>Attempted Username Logins:</h1>\n<table>\n<th>Username</th><th>Attempts</th>\n'
    for w in sorted(user_d, key=user_d.get, reverse=True):
        html += '<tr><td>' + str(w) + '</td><td>' + str(user_d[w]) + '</td></tr>\n'
    html += '</table>'

    return html


def find_fun_msgs(): #Return an html list of unique disconnect messages
    f = open(logfile,'r')
    contents = f.readlines()
    f.close()
    messages = set()
    for line in contents:
        if 'sshd' in line:
            #print(line)
            if 'received disconnect' in line.lower():
                line = line.split(':')[5]
                line = line.split('[preauth]')[0]
                if line.upper().isupper():
                    messages.add(line)
    html = '<h1>List of Disconnect Messages</h1>\n<ul>\n'
    for msg in messages:
        html += '<li>' + str(msg) + '</li>\n'
    html += '</ul>\n'
                    
    return html



#Run html generators
bad_ips = find_bad_ips()
bad_users = find_bad_users()
fun_msgs = find_fun_msgs()
good_ips = find_good_ips()

#Create html page from generators
html = '<html>\n'
html += bad_users + bad_ips + fun_msgs + good_ips
html += '</html>'

#Write HTML file
f = open(output,'w')
f.write(html)
f.close()

print('Done!')
