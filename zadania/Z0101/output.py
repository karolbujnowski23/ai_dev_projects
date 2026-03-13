import csv, json
fn=r'c:\Users\buyak\Documents\AI_devs\zadania\Z0101\people.csv'
rows=[]
with open(fn,encoding='utf-8') as f:
    reader=csv.DictReader(f)
    for r in reader:
        rows.append(r)

candidates=[r for r in rows if r['gender']=='M' and r['birthPlace']=='Grudzi\u0105dz' and 1986<=int(r['birthDate'][:4])<=2006]
transport_candidates=[]
for r in candidates:
    job=r['job'].lower()
    if 'towar' in job or 'transport' in job:
        transport_candidates.append(r)

output=[]
for r in transport_candidates:
    output.append({
        "name": r['name'],
        "surname": r['surname'],
        "gender": r['gender'],
        "born": int(r['birthDate'][:4]),
        "city": r['birthPlace'],
        "tags": ["transport"]
    })
print(json.dumps({
    "apikey":"tutaj-twój-klucz-api",
    "task":"people",
    "answer": output
}, ensure_ascii=False, indent=2))
