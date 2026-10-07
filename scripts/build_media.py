"""Build reviewable media from real, verified Canalytics UI captures.

No provider requests, synthetic UI or continuous screen recording.
Requires Pillow and FFmpeg. Run: python scripts/build_media.py
"""
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "media"
WORK = OUT / "render"
VIDEOS = OUT / "videos"
SOCIAL = OUT / "linkedin"
DOCS = ROOT / "docs" / "images"
for path in (WORK, VIDEOS, SOCIAL):
    path.mkdir(parents=True, exist_ok=True)

FONT_DIR = Path("C:/Windows/Fonts")
REG = FONT_DIR / "segoeui.ttf"
BOLD = FONT_DIR / "segoeuib.ttf"
if not REG.exists():
    REG = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
BG = "#10151d"
PANEL = "#1a212b"
INK = "#eff3f8"
MUTED = "#a7b2c1"
ORANGE = "#f47b50"

def font(size, bold=False):
    return ImageFont.truetype(str(BOLD if bold else REG), size)

def wrap(draw, text, f, width):
    lines, line = [], ""
    for word in text.split():
        candidate = (line + " " + word).strip()
        if draw.textlength(candidate, font=f) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines

def words(draw, text, x, y, size, width, color=INK, bold=False, gap=1.3):
    f = font(size, bold)
    for line in wrap(draw, text, f, width):
        draw.text((x, y), line, font=f, fill=color)
        y += int(size * gap)
    return y

def brand(draw, x, y, size=40):
    side = int(size * 1.2)
    draw.rounded_rectangle((x, y+3, x+side, y+side+3), 12, fill=ORANGE)
    draw.polygon([(x+side*.37,y+side*.28),(x+side*.37,y+side*.79),(x+side*.77,y+side*.54)], fill="#ffffff")
    draw.text((x+side+14,y), "canalytics.", font=font(size, True), fill=INK)

def image_into(canvas, file, rect):
    source = Image.open(file).convert("RGB")
    fitted = ImageOps.contain(source, (rect[2]-rect[0],rect[3]-rect[1]), Image.Resampling.LANCZOS)
    x = rect[0]+(rect[2]-rect[0]-fitted.width)//2
    y = rect[1]+(rect[3]-rect[1]-fitted.height)//2
    canvas.paste(fitted,(x,y))

GROUPS = {
 "01-analytics": ("Analytics e histórico", "Períodos, métricas, comparação, CSV e público."),
 "02-conteudos": ("Biblioteca e retenção", "Busca, ordenação, detalhes e retenção por vídeo."),
 "03-canais": ("Canais e comunidades", "YouTube, Twitch, Discord e TikTok em áreas próprias."),
 "04-conexoes": ("Conexões e sincronização", "Configuração, permissões e fila persistente."),
 "05-organizacao": ("Diário e áreas de trabalho", "Anotações duráveis e projetos separados."),
 "06-temas": ("Claro, escuro e sistema", "Aparência opcional com preferência persistente."),
 "07-mobile": ("Experiência no celular", "Menu, conectores e temas em uma tela pequena."),
 "08-autenticacao": ("Entrada e saída da conta", "Sessão local com usuário exclusivo de teste."),
}
manifest = json.loads((OUT/"manifest.json").read_text(encoding="utf-8"))

def video_frame(group, caption, screenshot=None, step=None, total=None):
    canvas = Image.new("RGB",(1920,1080),BG)
    d = ImageDraw.Draw(canvas)
    brand(d,42,26,36)
    d.text((1410,37),"QA LOCAL | DADOS FICTÍCIOS",font=font(22,True),fill=ORANGE)
    d.line((42,94,1878,94),fill="#303a47",width=2)
    if screenshot:
        d.rounded_rectangle((38,120,1400,1013),18,fill=PANEL)
        image_into(canvas,screenshot,(48,130,1390,1003))
        y = words(d,GROUPS[group][0],1440,156,42,425,bold=True)
        d.text((1440,y+35),f"ETAPA {step:02d} / {total:02d}",font=font(24,True),fill=ORANGE)
        words(d,caption,1440,y+98,32,422,gap=1.42)
        words(d,"Interface real. Respostas externas simuladas.",1440,838,23,420,MUTED)
        d.rounded_rectangle((1440,982,1874,990),4,fill="#333e4c")
        d.rounded_rectangle((1440,982,1440+int(434*step/total),990),4,fill=ORANGE)
    else:
        d.text((92,248),"CANALYTICS 0.1.0",font=font(25,True),fill=ORANGE)
        y=words(d,GROUPS[group][0],92,312,78,1510,bold=True)
        y=words(d,caption,96,y+36,37,1400,MUTED)
        words(d,"Sequência de capturas dos fluxos testados, com legendas. Sem áudio.",96,875,25,1500,MUTED)
    d.text((42,1035),"Apache-2.0  |  Instalação própria  |  Testes com fixtures  |  07/10/2026",font=font(21),fill=MUTED)
    return canvas

def encode(stills, output):
    listing = output.with_suffix(".frames.txt")
    rows=[]
    for path,seconds in stills:
        # Paths are authored locally; FFmpeg concat uses forward slashes.
        rows += ["file '"+path.as_posix().replace("'","'\\''")+"'", "duration "+str(seconds)]
    rows.append("file '"+stills[-1][0].as_posix()+"'")
    listing.write_text("\n".join(rows)+"\n",encoding="utf-8")
    subprocess.run([shutil.which("ffmpeg") or "ffmpeg","-y","-hide_banner","-loglevel","error",
                    "-f","concat","-safe","0","-i",str(listing),"-t",str(sum(s for _,s in stills)),
                    "-vf","fps=24","-c:v","libx264","-preset","veryfast","-crf","23",
                    "-pix_fmt","yuv420p","-movflags","+faststart",str(output)],check=True)
    listing.unlink()

metadata=[]
for group,(title,description) in GROUPS.items():
    frames=[f for f in manifest["frames"] if f["group"]==group]
    stills=[]
    cover=WORK/(group+"-cover.png")
    video_frame(group,description).save(cover)
    stills.append((cover,3))
    for i,frame in enumerate(frames,1):
        path=WORK/(group+f"-{i:02d}.png")
        video_frame(group,frame["caption"],OUT/frame["file"],i,len(frames)).save(path)
        stills.append((path,frame.get("duration",5)))
    ending=WORK/(group+"-end.png")
    video_frame(group,"Fluxo verificado no QA. Homologação com contas reais permanece pendente.").save(ending)
    stills.append((ending,3))
    video=VIDEOS/(group+".mp4")
    encode(stills,video)
    metadata.append({"file":"videos/"+video.name,"title":title,"seconds":sum(s for _,s in stills),"steps":len(frames)})
    print(video.name,metadata[-1]["seconds"],"segundos",flush=True)

CARDS = [
 ("Seu conteúdo,\nem perspectiva.", "Um estúdio de analytics aberto para criadores, canais e comunidades.", "dashboard-light.jpg",
  "Prévia funcional 0.1.0. Interface capturada com dados fictícios."),
 ("Entenda a evolução.", "Histórico, filtros, comparação e exportação por canal.", "dashboard-dark.jpg",
  "Relatórios diários e snapshots têm significados diferentes."),
 ("Investigue os conteúdos.", "Busca, contadores acumulados e retenção por vídeo do YouTube.", "contents.jpg",
  "Retenção depende de autorização e da disponibilidade oficial."),
 ("Conecte suas plataformas.", "YouTube e Twitch implementados. Discord e TikTok experimentais.", "connectors.jpg",
  "OAuth real ainda será homologado. Bilibili está no roadmap."),
 ("Escolha seu tema.", "Claro, escuro ou seguir o sistema. Também no celular.", None,
  "Preferência salva no navegador; nenhuma métrica é alterada."),
 ("Aberto por natureza.", "Apache-2.0. Instalação própria. Seus dados no seu servidor.", "channels.jpg",
  "Código e demonstração: github.com/ThiagoRochaDev/canalytics. Contribua com os próximos relatórios."),
]
cards=[]
for i,(title,sub,file,foot) in enumerate(CARDS,1):
    canvas=Image.new("RGB",(1080,1350),BG)
    d=ImageDraw.Draw(canvas)
    brand(d,64,54,44)
    d.text((936,70),f"{i:02d}/06",font=font(23,True),fill=MUTED)
    y=154
    for line in title.split("\n"):
        y=words(d,line,64,y,62,950,bold=True,gap=1.13)
    words(d,sub,66,y+20,30,943,MUTED,gap=1.35)
    d.rounded_rectangle((54,408,1026,1082),20,fill=PANEL)
    if file:
        image_into(canvas,DOCS/file,(65,420,1015,1070))
    else:
        image_into(canvas,DOCS/"mobile-light.jpg",(94,426,520,1066))
        image_into(canvas,DOCS/"mobile-dark.jpg",(560,426,986,1066))
    words(d,foot,66,1120,28,940,INK,gap=1.38)
    d.line((66,1254,1014,1254),fill="#303a47",width=2)
    d.text((66,1280),"CANALYTICS | OPEN SOURCE | PRÉVIA 0.1.0",font=font(21,True),fill=ORANGE)
    path=SOCIAL/f"{i:02d}-canalytics.png"; canvas.save(path); cards.append(path)
encode([(p,5) for p in cards],SOCIAL/"canalytics-visao-geral.mp4")

comparison=Image.new("RGB",(1600,700),BG)
d=ImageDraw.Draw(comparison); brand(d,38,23,36)
d.text((1100,38),"CLARO / ESCURO",font=font(24,True),fill=ORANGE)
image_into(comparison,DOCS/"dashboard-light.jpg",(24,95,792,660))
image_into(comparison,DOCS/"dashboard-dark.jpg",(808,95,1576,660))
comparison.save(OUT/"temas-claro-escuro.png")

(OUT/"videos.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
html=["<!doctype html><html lang='pt-BR'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Canalytics - pacote de demonstração</title><style>body{margin:0;background:#10151d;color:#eff3f8;font:17px/1.65 system-ui}main{max-width:1120px;margin:auto;padding:40px 24px}h1{font-size:42px}h2{margin-top:45px}a{color:#ffad8b}video,img{width:100%;border-radius:12px;background:#1a212b}p{max-width:900px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:24px}.card{background:#1a212b;padding:20px;border-radius:14px}small{color:#a7b2c1}.tag{color:#ffad8b}</style><main><p class='tag'>CANALYTICS 0.1.0 | APACHE-2.0</p><h1>Seu conteúdo, em perspectiva.</h1><p>Oito vídeos legendados dos fluxos testados. São sequências de capturas reais da interface, sem áudio e sem gravação contínua do cursor. Os canais TGR são fictícios; sincronização e retenção usam respostas simuladas. OAuth em plataformas reais ainda precisa de homologação.</p><p><a href='../pdf/canalytics-guia-e-validacao.pdf'>Guia e validação em PDF</a> · <a href='../pdf/canalytics-linkedin.pdf'>Carrossel em PDF</a> · <a href='linkedin/postagem.md'>Texto para LinkedIn</a> · <a href='historico-teste-youtube.csv'>CSV de teste</a></p><img src='temas-claro-escuro.png' alt='Temas claro e escuro'>"]
html.append("<h2>Vídeos dos testes</h2><div class='grid'>")
for m in metadata:
    html.append(f"<section class='card'><h3>{m['title']}</h3><video controls preload='metadata' src='{m['file']}'></video><p><a href='{m['file']}'>Abrir MP4</a> · {m['steps']} etapas · {m['seconds']} s</p></section>")
html.append("</div><h2>Material para LinkedIn</h2><p>Seis artes 1080 × 1350, PDF para postagem como documento e vídeo de 30 segundos. Material disponível na release v0.1.0 do GitHub; nenhuma postagem foi enviada ao LinkedIn.</p><video controls preload='metadata' src='linkedin/canalytics-visao-geral.mp4'></video><div class='grid'>")
for p in cards: html.append(f"<a href='linkedin/{p.name}'><img src='linkedin/{p.name}' alt='Slide {p.stem}' loading='lazy'></a>")
html.append("</div><h2>Cobertura e limites</h2><p>14 testes Python e 3 testes de cálculo TypeScript passaram. Build de produção passou. Exportação autenticada com 180 registros verificada pela API. Exclusão local e reconexão têm testes automatizados; o diálogo de remoção foi cancelado no vídeo. A autorização em provedores externos não foi gravada.</p><p>Docker Compose foi validado; a imagem não foi executada localmente porque o engine não estava ativo. O código atende uma instalação com administrador e várias áreas, ainda sem convites ou cobrança.</p></main></html>")
(OUT/"index.html").write_text("\n".join(html),encoding="utf-8")
print("Pacote de mídia renderizado.",flush=True)
