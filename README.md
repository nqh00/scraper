### ~~sCrApEr~~
![forthebadge](https://forthebadge.com/images/badges/works-on-my-machine.svg)

## Demo
https://user-images.githubusercontent.com/76725656/209461193-a63327aa-1e8b-4318-8e7e-defd47c91c04.mp4

## Requirements
 - [**GIT Bash**](https://github.com/git-for-windows/git/releases/latest) or **CYGWIN** or **MINGW**
 - [**Python**](https://www.python.org/ftp/python/3.9.2/python-3.9.2-amd64.exe)
 - [aria2c](https://github.com/aria2/aria2/releases/latest)
 - [ffmpeg](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z)

## Getting started

1. First, clone this **repo** with `git`:  
```batch
git clone https://github.com/nqh00/scraper.git
```
2. Then `cd` to `scraper`.
3. Install all required dependencies with `pip`:
```batch
pip3 install -r requirements.txt
```
4. The `download.sh` is now support movie, tv show & anime:
```bash
bash download.sh
```

## Details

### vikv.**net**
Encrypt `hdv-user` using `btoa` & `reverse` then send request to backend.
Download all `.ts` file & merge them back with `ffmpeg`.
### twist.moe
Decrypt password from `JavaScript CryptoJS.AES` by implementing OpenSSL's [EVP BytesToKey](https://www.openssl.org/docs/crypto/EVP_BytesToKey.html).
### watchasian.**cc**
Get query parameter of an episode with `lxml` then send request to `ajax`.

## TODO

 - [x] Support asia tv series.
 - [ ] Support us/uk tv series.
