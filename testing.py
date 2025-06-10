from urllib.request import urlopen
from bs4 import BeautifulSoup
html = urlopen('https://search.naver.com/search.naver?where=nexearch&ssc=tab.nx.all&query=%ED%98%84%EC%9E%AC%EC%83%81%EC%98%81%EC%98%81%ED%99%94%EC%88%9C%EC%9C%84&sm=tab_she&qdt=0')
soup = BeautifulSoup(html, 'lxml')
nameList=soup.find_all('strong',{'class' : 'name'})
for name in nameList:
  print(name.get_text())
