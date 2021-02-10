# Fshare scraper
[![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)](http://forthebadge.com)
# Important
**Application for vip accounts only**
## Getting started  
- First, clone this `fshare-scrape` with `git`:  
	``` git
	git clone https://github.com/nqh00/fshare-scrape
	```  
- Then `cd` to `fshare-scrape`.
- Run your code with `python`.

**Example code**  
``` python
from fshare import fshare

URL = 'https://www.fshare.vn/folder/ABCDEFG'

# V.I.P accounts only
bot = fshare(email="Your email", password="Your password")

bot.login()

# Download single fshare link
bot.download()
```
**Result**  
```
http://download014.fshare.vn/dl/+kYq54+P2Bo6rwx6JmSMDKSdbogsya8dlRPiwxIs6RK2mQ90VCgOv2fgsLyXkA5fBu9XALh6tmmZAmOF/Silicon.Valley.S01.720p.HDTV.E008-PhimVIPvn.net.mp4
```  
## Requirements  
* Python 3.5+
* [requests](https://github.com/request/request)
* [aiohttp](https://github.com/aio-libs/aiohttp)
# Twist.moe
- Get an encrypted string with `request()`.
- Decrypt `CryptoJS AES` with `decrypt()`.
- Extract the `url` with `extract()`. This is your `$i`.
- Download with `curl`:
	``` cmd
	curl -L -o $name -C - $i -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36" -H "Referer: https://twist.moe/"
	```