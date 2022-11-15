import codecs
import requests

url = 'http://127.0.0.1:8090/mediplanner/nlp/request'

f = codecs.open("input.txt", "r", encoding="utf-8")
s = f.read()
f.close()

x = requests.post(url, data = s.encode("utf-8"))

print(x.text)