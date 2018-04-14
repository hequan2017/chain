a =  {'hostname': 'SDF1', 'data': 'Aegis-<Guid(5A2C30A2-A87D-490A-9281-6765EDAD7CBA)>\nansible_19xkmz1l\nansible_5c31w637\nansible_w6p4y54e\nchain\n_config.yml\ndb.sqlite3\nLICENSE\nmanage.py\nREADME.md\nrequirements.txt\nshell.sh\nsystemd-private-92a8135b7e8c4a7290ed5adf81e91c2b-ntpd.service-8G1GuO'}



b =a['data']

b.replace('\n',"--")
print(b)
out = "  ".join(b.split())
print(out)