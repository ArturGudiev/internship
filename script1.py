import os

from openstack import connection
auth_args = {
    'auth_url': 'http://5.178.85.218/identity',
    'project_name': 'demo',
    'username': 'demo',
    'password': 'secret',
}



def print_info(server):
	print("name: " + server.name)
	s = "addresses: "
	ipaddr = []
	for key in server.addresses: 
		list = server.addresses[key]
		for address in list:
			ipaddr.append( [address[u'version'], address[u'addr'], address[u'OS-EXT-IPS:type'], key])
	s += str(ipaddr)
	print s + "\n"
		

def list_servers(conn):
    print("List Servers:")

    for server in conn.compute.servers():
        if(server.power_state == 1):
		print_info(server)

KEYPAIR_NAME = 'RandomString'
PRIVATE_KEYPAIR_FILE = '~/devstack/keypair.file'		
SSH_DIR = '~/devstack/sshdir/'
SERVER_NAME = 'new-server'

def create_keypair(conn):
    keypair = conn.compute.find_keypair(KEYPAIR_NAME)

    if not keypair:
        print("Create Key Pair:")

        keypair = conn.compute.create_keypair(name=KEYPAIR_NAME)

        print(keypair)

        try:
            os.mkdir(SSH_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e

        with open(PRIVATE_KEYPAIR_FILE, 'w') as f:
            f.write("%s" % keypair.private_key)

        os.chmod(PRIVATE_KEYPAIR_FILE, 0o400)

    return keypair

def create_server(conn):
    print("Create Server:")

    image = conn.compute.find_image('cirros-0.3.5-x86_64-disk')
    flavor = conn.compute.find_flavor('m1.tiny')
    network = conn.network.find_network('private')
    keypair = create_keypair(conn)

    server = conn.compute.create_server(
        name=SERVER_NAME, image_id=image.id, flavor_id=flavor.id,
        networks=[{"uuid": network.id}], key_name=keypair.name)

    server = conn.compute.wait_for_server(server)

    print("ssh -i {key} root@{ip}\n\n".format(
        key=PRIVATE_KEYPAIR_FILE,
        ip=server.access_ipv4))


conn = connection.Connection(**auth_args)

list_servers(conn)
create_server(conn)
list_servers(conn)

