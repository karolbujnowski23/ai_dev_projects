import csv

fn=r'c:\Users\buyak\Documents\AI_devs\zadania\Z0101\people.csv'
rows=[]
with open(fn,encoding='utf-8') as f:
    reader=csv.DictReader(f)
    for r in reader:
        rows.append(r)

candidates=[r for r in rows if r['gender']=='M' and r['birthPlace']=='Grudzi\u0105dz' and 1986<=int(r['birthDate'][:4])<=2006]
print('candidates', len(candidates))
for r in candidates:
    print(r['name'],r['surname'],r['birthDate'],r['job'])

print('--- likely transport jobs ---')
for r in candidates:
    if any(keyword in r['job'].lower() for keyword in ['transport','towar','ruch']):
        print(r['name'],r['surname'],r['job'])
