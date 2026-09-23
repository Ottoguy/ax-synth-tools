import sys, pypdf, pathlib
out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
for p in sys.argv[3:]:
    r = pypdf.PdfReader(p)
    name = pathlib.Path(p).stem.replace(" ", "_")
    with open(out / f"{name}.txt", "w", encoding="utf-8") as f:
        for i, pg in enumerate(r.pages, 1):
            f.write(f"\n\n===== PAGE {i} =====\n")
            f.write(pg.extract_text() or "")
    print(p, len(r.pages), "pages")
