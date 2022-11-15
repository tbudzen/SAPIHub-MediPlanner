# Files

icd10_all_basic_desc_put_to_es.sh  - Script puts ICD10 codes with basic description to Elasticsearch
ICD10_part_basic_desc.csv - Csv file which contains selected ICD10 codes
extend-description-of-icd10-code-and-prepare-curl.ipynb - script builds extended description for ICD10 codes and prepares curl commands which put data to Elasticsearch
icd10_part_ext_desc_put_to_es.sh - Script puts ICD10 codes with extended description to Elasticsearch

# Docker run ES

docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:7.6.0

elasticsearch-plugin install analysis-stempel

Restart docker after plugin installation

## Password

### Enable security
https://www.elastic.co/guide/en/elasticsearch/reference/6.8/get-started-enable-security.html

add to elasticsearch.yml line:
xpack.security.enabled: true

### Changing password

https://www.elastic.co/guide/en/elasticsearch/reference/6.8/get-started-built-in-users.html


./bin/elasticsearch-setup-passwords interactive

curl -X POST "54.38.129.3:9200/_security/user/mediplanner" -H 'Content-Type: application/json' -d'
{
  "password" : "__PASS__",
  "roles" : [ "admin" ],
  "full_name" : "Mediplanner"
}'

# Testing analyzer

curl --user elastic:__PASS__ -X DELETE "54.38.129.3:9200/icd10_test"

curl --user elastic:__PASS__ -X PUT "54.38.129.3:9200/icd10_test?pretty" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "analysis": {
      "filter": {
        "autocomplete_filter": {
          "type": "edge_ngram",
          "min_gram": 5,
          "max_gram": 20
        },
        "polish_stop": {
          "type": "polish_stop",
          "stopwords": [
            "_polish_",
            "a","aby","ach","acz","aczkolwiek","aj","albo","ale","alez","ależ","ani","az","aż","bardziej","bardzo","beda","bedzie","bez","deda","będą","bede","będę","będzie","bo","bowiem","by","byc","być","byl","byla","byli","bylo","byly","był","była","było","były","bynajmniej","cala","cali","caly","cała","cały","ci","cie","ciebie","cię","co","cokolwiek","cos","coś","czasami","czasem","czemu","czy","czyli","daleko","dla","dlaczego","dlatego","do","dobrze","dokad","dokąd","dosc","dość","duzo","dużo","dwa","dwaj","dwie","dwoje","dzis","dzisiaj","dziś","gdy","gdyby","gdyz","gdyż","gdzie","gdziekolwiek","gdzies","gdzieś","go","i","ich","ile","im","inna","inne","inny","innych","iz","iż","ja","jak","jakas","jakaś","jakby","jaki","jakichs","jakichś","jakie","jakis","jakiś","jakiz","jakiż","jakkolwiek","jako","jakos","jakoś","ją","je","jeden","jedna","jednak","jednakze","jednakże","jedno","jego","jej","jemu","jesli","jest","jestem","jeszcze","jeśli","jezeli","jeżeli","juz","już","kazdy","każdy","kiedy","kilka","kims","kimś","kto","ktokolwiek","ktora","ktore","ktorego","ktorej","ktory","ktorych","ktorym","ktorzy","ktos","ktoś","która","które","którego","której","który","których","którym","którzy","ku","lat","lecz","lub","ma","mają","mało","mam","mi","miedzy","między","mimo","mna","mną","mnie","moga","mogą","moi","moim","moj","moja","moje","moze","mozliwe","mozna","może","możliwe","można","mój","mu","musi","my","na","nad","nam","nami","nas","nasi","nasz","nasza","nasze","naszego","naszych","natomiast","natychmiast","nawet","nia","nią","nic","nich","nie","niech","niego","niej","niemu","nigdy","nim","nimi","niz","niż","no","o","obok","od","około","on","ona","one","oni","ono","oraz","oto","owszem","pan","pana","pani","po","pod","podczas","pomimo","ponad","poniewaz","ponieważ","powinien","powinna","powinni","powinno","poza","prawie","przeciez","przecież","przed","przede","przedtem","przez","przy","roku","rowniez","również","sam","sama","są","sie","się","skad","skąd","soba","sobą","sobie","sposob","sposób","swoje","ta","tak","taka","taki","takie","takze","także","tam","te","tego","tej","ten","teraz","też","to","toba","tobą","tobie","totez","toteż","totobą","trzeba","tu","tutaj","twoi","twoim","twoj","twoja","twoje","twój","twym","ty","tych","tylko","tym","u","w","wam","wami","was","wasz","wasza","wasze","we","według","wiele","wielu","więc","więcej","wlasnie","właśnie","wszyscy","wszystkich","wszystkie","wszystkim","wszystko","wtedy","wy","z","za","zaden","zadna","zadne","zadnych","zapewne","zawsze","ze","zeby","zeznowu","zł","znow","znowu","znów","zostal","został","żaden","żadna","żadne","żadnych","że","żeby"
          ]
        }
      },
      "analyzer": {
        "autocomplete": { 
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "polish_stem",
            "polish_stop",
            "asciifolding"
          ]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "icd10": {
          "type": "text",
          "analyzer": "standard", 
          "search_analyzer": "standard" 
      },
      "text": {
        "type": "text",
        "analyzer": "autocomplete", 
        "search_analyzer": "autocomplete" 
      }
    }
  }
}'

curl --user elastic:__PASS__ -X POST "54.38.129.3:9200/icd10_test/_analyze?pretty" -H 'Content-Type: application/json' -d'
{
  "field": "text",
  "text": "Wrodzona wada serca pod postacią przerwanego łuku aorty, ubytku w przegrodzie międzykomorowej i miedzyprzedsionkowej oraz przetrwałego przewodu tętniczego. Prawa tętnica podobojczykowa błądząca (arteria lusoria)"
}
'

# Testing analyzer and filter with sample data

curl -X DELETE "54.38.129.3:9200/test_index" -H 'Content-Type: application/json'

curl -X PUT "54.38.129.3:9200/test_index?pretty" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "analysis": {
      "filter": {
        "autocomplete_filter": {
          "type": "edge_ngram",
          "min_gram": 1,
          "max_gram": 20
        }
      },
      "analyzer": {
        "autocomplete": { 
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "polish_stem",
            "polish_stop",
            "asciifolding",
            "autocomplete_filter"
          ]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "icd10": {
          "type": "text",
          "analyzer": "standard", 
          "search_analyzer": "standard" 
      },
      "text": {
        "type": "text",
        "analyzer": "autocomplete", 
        "search_analyzer": "autocomplete" 
      }
    }
  }
}'

curl -X POST "54.38.129.3:9200/test_index/_doc/?pretty" -H 'Content-Type: application/json' -d '{ "icd10": "A05.2", "text": "Zatrucie pokarmowe wywołane przez laseczkę clostridium perfringens (clostridium welchii)"}'

curl -X POST "54.38.129.3:9200/test_index/_doc/?pretty" -H 'Content-Type: application/json' -d '{ "icd10": "A06.4", "text": "Pełzakowy ropień wątroby"}'

curl -X POST "54.38.129.3:9200/test_index/_doc/?pretty" -H 'Content-Type: application/json' -d '{ "icd10": "A40.0", "text": "Posocznica wywołana przez paciorkowce grupy a"}'


curl -X GET "54.38.129.3:9200/test_index/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "text": {
        "query": "CCS", 
        "operator": "and"
      }
    }
  }
}
'

curl -X GET "54.38.129.3:9200/icd10_index/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "text": {
        "query": "Zespół preekscytacji", 
        "operator": "and"
      }
    }
  }
}
'

# Algorithm of replacing signs and creating curl requests to put  ICD10 codes to ES
ICD10 code list: http://jgp.uhc.com.pl/doc/27.5/icd10/index.html 

1. Changing "'" to empty string
'

2. Changing '"' to empty string
"

3. Changing new line
From: \n
To: \ncurl -X POST "54.38.129.3:9200/icd10_index/_doc/?pretty" -H 'Content-Type: application/json' -d '{ "icd10": "

2. Changing signs bettwen ICD10 code and description
From: "	"
To: ", "text": "

3. Changing new line
From: \n
To: "}'\n


# Znaczenie liter w kodach icd 10:

A; B- niektóre choroby zakaźne i pasożytnicze,
C - nowotwory,
D - choroby krwi i narządów krwiotwórczych, niektóre choroby autoimmunologiczne,
E - zaburzenia wydzielenia wewnętrznego, stanu odżywienia i przemiany metabolicznej,
F - zaburzenia psychiczne i zachowania,
G - choroby układu nerwowego,
H - choroby oka, ucha i wyrostków sutkowych,
I - choroby układu krążenia,
J - choroby układu oddechowego,
K - choroby układu trawiennego,
L - choroby skóry i tkanki podskórnej,
M - choroby układu kostno-mięśniowego i tkanki łącznej,
N - choroby układu moczowo-płciowego,
O - ciąża, poród, połóg,
P - schorzenia stanu okołoporodowego,
Q - wady rozwojowe wrodzone,
R - objawy, cechy chorobowe, nieprawidłowe wyniki badań nie klasyfikowane gdzie indziej,
S; T - urazy, zatrucia i inne skutki działania czynników zewnętrznych,
V; W; X; Y - zewnętrzne przyczyny zachorowania i zgonu,
Z - czynniki wpływające na stan zdrowia i kontakt ze służbą zdrowia,
U - kody specjalne. 