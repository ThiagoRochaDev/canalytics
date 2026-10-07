"""Package only reviewed, public-safe media. Never include QA databases or keys."""
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output"; MEDIA=OUT/"media"; PDF=OUT/"pdf"
DELIVERY=OUT/"delivery"
manifest=json.loads((MEDIA/"manifest.json").read_text(encoding="utf-8"))
assert len(manifest["frames"])==44
assert all((MEDIA/f["file"]).is_file() for f in manifest["frames"])
report={"pdf":{},"videos":[],"captures":len(manifest["frames"])}
for file in PDF.glob("*.pdf"):
    pages=len(PdfReader(file).pages)
    assert pages==(8 if "guia" in file.name else 6)
    report["pdf"][file.name]={"pages":pages,"bytes":file.stat().st_size}
video_files=sorted((MEDIA/"videos").glob("*.mp4"))+[MEDIA/"linkedin"/"canalytics-visao-geral.mp4"]
expected=json.loads((MEDIA/"videos.json").read_text(encoding="utf-8"))
expected={Path(m["file"]).name:m["seconds"] for m in expected}
expected["canalytics-visao-geral.mp4"]=30
for file in video_files:
    data=json.loads(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries",
         "stream=codec_name,width,height,r_frame_rate:format=duration","-of","json",str(file)],text=True))
    stream=data["streams"][0]; duration=float(data["format"]["duration"])
    assert stream["codec_name"]=="h264" and abs(duration-expected[file.name])<.1
    subprocess.run(["ffmpeg","-v","error","-i",str(file),"-f","null","NUL" if __import__("os").name=="nt" else "/dev/null"],check=True)
    thumbnail=MEDIA/"render"/(file.stem+"-verified.jpg")
    subprocess.run(["ffmpeg","-y","-v","error","-ss",str(duration/2),"-i",str(file),"-frames:v","1",str(thumbnail)],check=True)
    report["videos"].append({"file":file.relative_to(OUT).as_posix(),"seconds":duration,**stream})
(MEDIA/"verification.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")

# Contact sheets include every final PDF page, for visual review.
for stem in ["guia","linkedin"]:
    pages=sorted((PDF/"review").glob(stem+"-*.png"))
    subsets=[pages[:4],pages[4:]] if stem=="guia" else [pages]
    for n,subset in enumerate(subsets,1):
        cellw=760 if stem=="guia" else 440; cellh=560 if stem=="guia" else 580
        canvas=Image.new("RGB",(cellw*2,cellh*((len(subset)+1)//2)),"#dfe5eb"); draw=ImageDraw.Draw(canvas)
        for i,file in enumerate(subset):
            im=Image.open(file); im.thumbnail((cellw-20,cellh-32))
            x=(i%2)*cellw+10; y=(i//2)*cellh
            canvas.paste(im,(x,y+24)); draw.text((x,y+6),file.name,fill="black")
        canvas.save(PDF/"review"/f"{stem}-contact-{n}.jpg")

selected=[(file,Path("pdf")/file.name) for file in PDF.glob("*.pdf")]
for name in ["index.html","README.md","validacao.md","manifest.json","videos.json","verification.json",
             "historico-teste-youtube.csv","temas-claro-escuro.png"]:
    selected.append((MEDIA/name,Path("media")/name))
for folder,patterns in [("captures",["*.jpg"]),("videos",["*.mp4"]),("linkedin",["*.png","*.mp4","*.md"])]:
    for pattern in patterns:
        for file in (MEDIA/folder).glob(pattern):
            selected.append((file,Path("media")/folder/file.name))
for file in (ROOT/"docs"/"images").glob("*"):
    if file.is_file(): selected.append((file,Path("media")/"images"/file.name))
selected += [(ROOT/"LICENSE",Path("LICENSE")),(ROOT/"NOTICE",Path("NOTICE"))]
DELIVERY.mkdir(parents=True,exist_ok=True)
hashes=[]
for source,target in selected:
    dest=DELIVERY/target; dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,dest)
    hashes.append(hashlib.sha256(source.read_bytes()).hexdigest()+"  "+target.as_posix())
(DELIVERY/"SHA256SUMS.txt").write_text("\n".join(sorted(hashes))+"\n",encoding="utf-8")
(DELIVERY/"LEIA-ME.txt").write_text(
    "Canalytics 0.1.0 - material de demonstracao\n\nAbra media/index.html no navegador.\n"
    "Videos: 8 testes legendados e 1 visao geral para LinkedIn.\n"
    "PDFs: guia de 8 paginas e carrossel de 6 paginas.\n"
    "Dados ficticios. Sem bancos, chaves, sessoes ou logs.\n"
    "Publicado no GitHub: github.com/ThiagoRochaDev/canalytics. Sem homologacao externa ou postagem no LinkedIn.\n",encoding="utf-8")
archive=OUT/"canalytics-midia-documentacao.zip"
allowed={t.as_posix() for _,t in selected}|{"SHA256SUMS.txt","LEIA-ME.txt"}
with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
    for relative in sorted(allowed): z.write(DELIVERY/relative,relative)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert set(z.namelist())==allowed
    assert not any(Path(n).suffix in [".db",".sqlite",".key",".log"] for n in z.namelist())
print(json.dumps({"zip":str(archive),"files":len(allowed),"bytes":archive.stat().st_size,**report},ensure_ascii=False,indent=2))
