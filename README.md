<properties LandingPageTags="Python,webscraping,webcrawling" />

# Crawlerino- 一個簡單的 Python 3 網頁爬蟲
　
Crawlerino 是一個python 3 的網頁爬蟲，它的設計理念是方便的讓你客制化來完成各種可能需要網頁爬蟲的任務  
因此，要注意，它被設計成”容易維護及擴充”，而不是”高效”　

以下說明crawlerino不處理什麼:

* 它不處理架構的問題
* 它不會因為偽裝的需要而加工你的headers.如果有需要，你完全可以自已處理 requests.
* 它忽略robots.txt.
cd 
它使用 ```requests``` 及 ```Beautiful Soup (bs4)```組件，讓程式碼看上去更清爽


## 安裝
crawlenino 並沒有包裝成python組件，不過，這並不會影響你使用它，它只依賴了兩個組件，所以你大可自已安裝它們，當然python 3.x是必要的，再來你只要按照正常方式安裝requests及Beautiful即可

```
c:\myfolder> pip install requests
c:\myfolder> pip install beautifulsoup4
```
接下來你只要執行以下指令```python crawlerino.py```, 你就會看到輸出結果如下圖所示:

![screenshot](images/testrun.png)

## 客制化
crawlerino只是單純的下載網頁，並沒有對內容進行任何的剖析，當然你不會希望只是這樣，你可以從程式碼的第38行開始動手對網頁進行剖析，這裏對應到下面流程圖中的 **step 3**  
在這段程式中，你可以存取```response``` (來至 requests.get) 或 ```soup```　（可想而知，這是Beautiful Soup的剖析物件).


在某些情況下，你可以需要遞迴來處理你的連結，或者是忽略特定的連結網站、網站授權要求等等，你可以在**step 4** 處理這些有關連結的過濾(程式碼第 42-50 行)　
你只要記得 ```links``` 就是當前頁面的所有連結，而且即將被放進爬蟲的queue 裏面，你可以在它們被放到queu前加工它們（第55行程式碼）.

![flowchart](images/flowchart.png)

更多資訊請看原作都的部落格文章，我們感激他[Crawling the web with Python 3.x](http://mahugh.com/2015/12/12/crawling-the-web-with-python-3-x/).
