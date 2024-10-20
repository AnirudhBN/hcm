import csv
import mysql.connector as sql

def process_upload(file_name):
    f=open(file_name,'r')
    r=csv.reader(f)
    mycon=sql.connect(host='localhost',user='root',password='1234',database='hcm')
    cur=mycon.cursor()
    k=['first_name','last_name','date_of_birth','date_of_joining','manager_id','date_of_leaving','status_code','marital_status_code','phone_number']
    for i in r:
        l1=[]
        ind=[]
        l=i
        l[0]=l[0].strip()
        l[1]=l[1].strip()
        lk=l[2].split('-')
        s=''
        for i in range(len(lk)-1,-1,-1):
            if i==0:
                s+=lk[i]
            else:
                s+=lk[i]
                s+='-'
        l[2]=s
        print(l[2])
        ls=l[3].split('-')
        s1=''
        for i in range(len(ls)-1,-1,-1):
            if i==0:
                s1+=ls[i]
            else:
                s1+=ls[i]
                s1+='-'
        l[3]=s1
        l[6]=int(l[6])
        l[7]=int(l[7])
        if l[8]!='':
            l[8]=l[8].strip()
        print('l:',l)
        ln=len(l)
        for i in range(ln):
            if l[i]!='':
                l1.append(l[i])
                ind.append(i)
        print(l1)
        print(ind)
        nk=''
        for i in ind:
            if ind.index(i)!=len(ind)-1:
                nk+=k[i]
                nk+=','
            elif ind.index(i)==len(ind)-1:
                nk+=k[i]
            
        print(nk)
        s="insert into employees("+nk+")values%r"%(tuple(l1),)
        cur.execute(s)
        mycon.commit()
    f.close()
    mycon.close()

