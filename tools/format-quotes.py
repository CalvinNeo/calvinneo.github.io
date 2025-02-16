
with open("../_posts/from-ym.md", "r", encoding='utf-8') as f:
    txt = f.read()
    txt = txt.replace("‘", "'")
    txt = txt.replace("’", "'")
    with open("../_posts/1--from-ym.md", "w") as fw:
        fw.write(txt)