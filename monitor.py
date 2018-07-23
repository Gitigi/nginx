import sys,docker,socket,re,os

cli = docker.Client(base_url='unix://var/run/docker.sock')

hostnames = []
nginx_conf = '/etc/nginx/conf.d/default.conf'
reg = re.compile(r'#\[%((.|\n)*)#%\]')
image = os.getenv('MONITOR_IMAGE','')
def update_nginx_conf():
    stream = ''
    txt = ''
    for h in hostnames:
        stream += 'server unix:/var/tmp/%s.sock;\n' % (h,);
    with open(nginx_conf,'r') as conf:
        txt = str(conf.read())
    txt = reg.sub('#[%\n'+stream+'#%]\n',txt)
    with open(nginx_conf,'w') as conf:
        conf.write(txt)
    os.system('nginx -s reload')

def register(id):
    hostname = cli.inspect_container(id)['Config']['Hostname']
    if hostname not in hostnames:
        hostnames.append(hostname)
        update_nginx_conf()
    with open('containers.txt','a') as l:
        l.write(hostname)
        l.write('\n')
    
def unregister(id):
    hostname = cli.inspect_container(id)['Config']['Hostname']
    if hostname in hostnames:
        hostnames.remove(hostname)
        update_nginx_conf()
        os.system('rm /var/tmp/%s.sock'%(hostname))
        with open('containers.txt','w') as l:
            for h in hostnames:
                l.write(h+'\n')

def start(cli,event):
    register(event['id'])
        
def die(cli,event):
    unregister(event['id'])
    
thismodule = sys.modules[__name__]

container = cli.inspect_container(socket.gethostname())
node_id = container['Config']['Labels']['com.docker.swarm.node.id']

events = cli.events(decode=True)

with open('monitor.txt','w') as l:
    l.write('starting \n\n')
    
for cont in cli.containers():
    try:
        if node_id == cont['Labels']['com.docker.swarm.node.id']:
            if cont['State'] == 'running' and cont['Image'].split('@')[0] == image:
                register(cont['Id'])
    except Exception:
        with open('monitor_error.txt','w') as l:
            l.write("cont['Labels']['com.docker.swarm.node.id'] not found in \n")
            l.write(str(cont))
            l.write("\n\n\n")
            
for event in events:
    try:
        if node_id == event['Actor']['Attributes']['com.docker.swarm.node.id']:
            if event['from'].split('@')[0] == image:
                with open('monitor.txt','a') as l:
                    l.write(str(event))
                    l.write("\n\n\n")
                if(hasattr(thismodule,event['Action'])):
                    getattr(thismodule,event['Action'])(cli,event)
    except Exception:
        pass
    
    
with open('monitor.txt','w') as l:
    l.write('ending\n')