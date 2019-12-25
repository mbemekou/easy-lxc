#!/usr/bin/python
import re
from random import * 
import sys
import os
def usage():
	how_to_use= '''

container -m <modele_name> permet de creer une machine modele de nom <modele_name>
container -c <modele_name> permet de creer un reseau basee sur un modele existant

'''
	print how_to_use
	sys.exit(1)
if(len(sys.argv) !=3):
	usage()
	

Modele_lxc='''
lxc.mount.entry = /sys/kernel/debug sys/kernel/debug none bind,optional 0 0
lxc.mount.entry = /sys/kernel/security sys/kernel/security none bind,optional 0 0
lxc.mount.entry = /sys/fs/pstore sys/fs/pstore none bind,optional 0 0
lxc.mount.entry = mqueue dev/mqueue mqueue rw,relatime,create=dir,optional 0 0
lxc.arch = linux64
lxc.rootfs.path = dir:/var/lib/lxc/^name^/rootfs
lxc.uts.name = ^name^'''
Modele_lxc_if='''
lxc.net.0.type = veth
lxc.net.0.link = ^br^
lxc.net.0.flags = up
lxc.net.0.hwaddr = ^zero^:16:3e:ab:^mac^
lxc.net.0.name= eth0
'''
Modele_iface='''
auto eth0
iface eth0 inet static
^address^
^gateway^
'''
def modele_create(modele):
	os.system("apt update && apt install lxc lxc-templates -y")
	os.system("lxc-create "+modele+" -t ubuntu -- -r xenial")
	os.system("lxc-start "+modele)
	os.system("lxc-attach "+modele+" -- apt update && apt install net-tools man tcpdump iptables openssh-server apache2 curl -y")
	os.system("lxc-stop "+modele)

if("-m" in sys.argv[1]):
	modele_create(sys.argv[2])
	sys.exit(2)
elif("-c" in sys.argv[1]):
	configs=[]
	interfaces=[]
	names=[]
	os.system("lxc-stop "+sys.argv[2])
	n=int(raw_input("Entrer le nombre de container que vous voulez creer:   "))
	for i in range(1, n+1):
		Modeleiface=""
		
		container_name=raw_input("Entrer le nom du container"+str(i)+": ")
		names.append(container_name)
		Modelelxc=str.replace(Modele_lxc,"^name^",container_name)
		nmbre_iface=int(raw_input("Entrer le nombre d'interfaces du container "+container_name+": "))
		for j in range(0,nmbre_iface):
			
			a=str(randint(1111,9999))
			mac=a[:2]+":"+a[2:]
			bridge=raw_input("Entrer le bridge auquel est connecte Eth"+str(j)+":  ")
			os.system("brctl addbr "+bridge)
			os.system("ifconfig "+bridge+" up")
			Modelelxcif1=str.replace(Modele_lxc_if,"0",str(j))
			Modelelxcif2=str.replace(Modelelxcif1,"^mac^",mac)
			Modelelxcif1=str.replace(Modelelxcif2,"^br^",bridge)
			Modelelxcif2=str.replace(Modelelxcif1,"^zero^","00")
			Modelelxc=Modelelxc+Modelelxcif2
			
			ip=raw_input("Entrer l'ip de Eth"+str(j)+": ")
			k=str.replace(Modele_iface,"0",str(j))
			Modele_iface=k
			if("dhcp" not in ip):
				gateway=raw_input("Entrer la gateway de Eth"+str(j)+":  ")
				Modeleiface1=str.replace(Modele_iface,"^address^","address "+ip)
				if(len(gateway) !=0):
					
					Modeleiface2=str.replace(Modeleiface1,"^gateway^","gateway "+gateway)
					Modeleiface1=Modeleiface2
				else:
					Modeleiface2=str.replace(Modeleiface1,"^gateway^","")
					Modeleiface1=Modeleiface2
			else:
				Modeleiface1=str.replace(Modele_iface,"static","dhcp")
				Modeleiface2=str.replace(Modeleiface1, "^address^","")
				Modeleiface1=str.replace(Modeleiface2, "^gateway^","")
			Modeleiface=Modeleiface+Modeleiface1
		interfaces.append(Modeleiface)
		configs.append(Modelelxc)

	for i in range(1, n+1):
	
		
		container_name=names.pop(0)
		print "creation de "+container_name
		os.system("lxc-copy "+sys.argv[2]+" -N "+container_name)
		print "[+] conteneur "+container_name+" cree"
		os.system("echo "+container_name+" >/var/lib/lxc/"+container_name+"/rootfs/etc/hostname")
		f1=open("/var/lib/lxc/"+container_name+"/config","w")
		Modelelxc=configs.pop(0)
		f1.write(Modelelxc)
		f1.close()
		Modeleiface=interfaces.pop(0)
		f2=open("/var/lib/lxc/"+container_name+"/rootfs/etc/network/interfaces","w")
		f2.write(Modeleiface)	
		f2.close()
		print "demarrage de "+container_name
		os.system("lxc-start "+container_name)
	os.system("lxc-ls -f |grep 'RUNNING'")
	sys.exit(3)
else:
	usage()

			
			
