import uuid




tools =  ['hequan2', 'hequan1']
p = ['2', '1']

b = dict(zip(tools,p))
print(b)
a = sorted(b.items(),key=lambda  item:item[1])
print(a)

for i in a:
    print(i[0])

