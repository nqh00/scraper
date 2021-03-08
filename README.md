### ~~sCrApEr~~
![forthebadge](https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg)![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)

***Supported website:***
|                |       |
|----------------|-------|
|fshare          | **x** |
|google drive    |       |
|vikv            | **x** |
|twist.moe       | **x** |
|freetutsdownload| **x** |

**Requirements**
 - [**CygWin**](https://cygwin.com/setup-x86_64.exe) or [Git Bash](https://github.com/git-for-windows/git/releases/latest)
 - [**Python**](https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe)
 - [aria2c](https://github.com/aria2/aria2/releases/latest)
 - [ffmpeg](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z)
 
**Getting started**
1. First, clone this **repo** with `git`:  
```batch
git clone https://github.com/nqh00/scraper.git
```
2. Then `cd` to `scraper`.
3. Install all required dependencies with `pip`:
```batch
pip3 install -r requirements.txt
```
4. The `download.sh` is now support both movie & anime:
```bash
bash download.sh
```
### fshare.**vn**
> *This application for vip accounts only*

Login to `fshare` [API](https://www.fshare.vn/api-doc) with **public** `app_key` and `user-agent`.
Get `download.fshare` link by using asynchronous `asyncio` to send request.
### vikv.**net**
Encode `hdv-user` using `btoa` & `reverse` then send request to `vikv` backend.
Download all `.ts` file & merge them back with `ffmpeg`.
### twist.moe
Decrypt password from `JavaScript CryptoJS.AES` by implementing OpenSSL's [EVP BytesToKey](https://www.openssl.org/docs/crypto/EVP_BytesToKey.html).
### freetutsdownload.**net**
Get all `freetus` available courses with `keyword`.