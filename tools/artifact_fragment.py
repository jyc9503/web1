#!/usr/bin/env python3
"""단일 HTML(doctype·head 포함)을 Artifact 게시용 조각으로 바꾼다.

사용: python3 tools/artifact_fragment.py 입력.html 출력.html
- <title>, 폰트 <link>, <style>, <body> 안쪽만 남긴다.
- 게시 도구가 doctype/head/body를 직접 감싸기 때문이다.
"""
import re
import sys

src = open(sys.argv[1], encoding="utf-8").read()
title = re.search(r"<title>.*?</title>", src, re.S).group(0)
links = "\n".join(re.findall(r'<link rel="stylesheet" href="https://fonts[^>]*>', src))
styles = "\n".join(re.findall(r"<style>.*?</style>", src, re.S))
body = re.search(r"<body[^>]*>(.*)</body>", src, re.S).group(1)
# 게시 환경은 body margin 0 을 이미 적용한다. 조각에서는 body{margin:0} 규칙이 남아도 무해하다.
out = f'{title}\n<meta name="claude:viewport-fit-sides" content="cover">\n{links}\n{styles}\n{body}\n'
open(sys.argv[2], "w", encoding="utf-8").write(out)
print("wrote", sys.argv[2])
