#This will read /var/log/auth.log and do some anylysis with it, and then it will save it as an html file on /var/www/html/index.html so that idiots can see it.

import re

logfile = '/var/log/auth.log'


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

def find_good_ips():
    f = open(logfile,'r')
    contents = f.readlines()
    f.close()
    good_ips = set()
    for line in contents:
        if 'sshd' in line:
            if 'accepted' in line.lower():
                print(find_ip(line)[0])
                good_ips.add(find_ip(line)[0])
                
    return good_ips


def find_bad_ips(): #return dict of bad ips and count of attempts
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
            
    #outputs!
    print(ip_d)
    for w in sorted(ip_d, key=ip_d.get, reverse=True):
        print(w, ip_d[w])  
        
    return ip_d


def find_bad_users(): #return dict of attempted user logins and count of attempts
    f = open(logfile,'r')
    contents = f.readlines()
    f.close()
    users = {}
    usernames = []
    for line in contents:
        if 'sshd' in line:
            if 'failed' in line.lower():
                usernames.append(find_user(line)[0])
    for username in usernames:
        if not username in users:
            users[username] = 1
        else:
            users[username] += 1
            
    #outputs!        
    print(users)
    for w in sorted(users, key=users.get, reverse=True):
        print(w, users[w])
    return users


def find_fun_msgs(): #Return a UNIQUE list of disconnect messages
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
                    
    
    print(messages)
    return messages

bad_ips = find_bad_ips()
bad_users = find_bad_users()
bad_msgs = find_fun_msgs()

html = '''
<html>

<h1>Attempted username logins:<h1>
<table>
<tr><td>Username</td><td>Attempts</td></tr>
'''
bad_users_string = ''
for w in sorted(bad_users, key=bad_users.get, reverse=True):
    bad_users_string += '<tr><td>' + str(w) + '</td><td>' + str(bad_users[w]) + '</td></tr>\n'
    #print(w, bad_users[w])

html += bad_users_string
html += '</table>'
html += '''
<h1>IP's and attempts to login:</h1>
<table>
<tr><td>IP</td><td>Attempts</td></tr>
'''
bad_ips_string = ''
for w in sorted(bad_ips, key=bad_ips.get, reverse=True):
    bad_ips_string += '<tr><td>' + str(w) + '</td><td>' + str(bad_ips[w]) + '</td></tr>\n'
html += bad_ips_string
html += '</table>'

html+= '''
<h1>List of disconnect messages:</h1>
<table>
'''
messages = ''
for msg in bad_msgs:
    messages += '<tr><td>' + str(msg) + '</td></tr>\n'
    
html += messages
html += '</table>'
html += '</html>'


#Write HTML file
f = open('script.html','w')
f.write(html)
f.close()
