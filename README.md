# README

## GUI

![screenshot](resources/screenshot.png)

## Quick Start

1. Download `tokihunter.exe`
2. Open Windows Terminal 
3. Navigate to the executable
4. Run `tokihunter.exe --captcha`
5. Run `tokihunter.exe https://manatoki469.net/comic/<chapter-id>`

## Version

```
tokihunter.exe --version
```

## CAPTCHA

```
tokihunter.exe --captcha
```

Opens Manatoki’s CAPTCHA page. Once it’s completed, subsequent downloads won’t require CAPTCHA verification.

## Download

```
tokihunter.exe https://manatoki469.net/comic/<chapter-id>
```
You can also run CAPTCHA verification and start the download in a single command:
```
tokihunter.exe --captcha https://manatoki469.net/comic/<chapter-id>
```
```
tokihunter.exe --headless https://manatoki469.net/comic/<chapter-id>
```

## Search

```
tokihunter.exe --search https://manatoki469.net/comic/<title-id>
```
```
tokihunter.exe --search --headless https://manatoki469.net/comic/<title-id>
```

URLs for each chapter will be saved in `searches/<title>.txt`.