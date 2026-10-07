"""Create the two Canalytics delivery PDFs from verified local captures."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output"/"pdf"
OUT.mkdir(parents=True,exist_ok=True)
FONT=Path("C:/Windows/Fonts")
REG=FONT/"segoeui.ttf"; BOLD=FONT/"segoeuib.ttf"
if not REG.exists():
    REG=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    BOLD=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
pdfmetrics.registerFont(TTFont("Canal",str(REG)))
pdfmetrics.registerFont(TTFont("Canal-Bold",str(BOLD)))
BG=colors.HexColor("#f4f6f9"); INK=colors.HexColor("#17212d")
MUTED=colors.HexColor("#576476"); ACCENT=colors.HexColor("#e36d43")
W,H=landscape(A4)
doc=canvas.Canvas(str(OUT/"canalytics-guia-e-validacao.pdf"),pagesize=(W,H))
doc.setTitle("Canalytics - guia e validação 0.1.0")
doc.setAuthor("TGR Technology")
doc.setSubject("Prévia open source, screenshots e cobertura de testes com dados fictícios")

def text(x,y,t,size=11,bold=False,color=INK):
    doc.setFillColor(color); doc.setFont("Canal-Bold" if bold else "Canal",size)
    doc.drawString(x,y,t)

def para(x,y,t,width,size=11,color=INK):
    style=ParagraphStyle("body",fontName="Canal",fontSize=size,leading=size*1.45,textColor=color)
    p=Paragraph(t,style); _,height=p.wrap(width,1000)
    p.drawOn(doc,x,y-height)
    return y-height-12

def start(number,title,sub):
    doc.setFillColor(BG); doc.rect(0,0,W,H,fill=1,stroke=0)
    text(36,H-40,"canalytics.",22,True)
    text(W-244,H-37,"OPEN SOURCE  |  APACHE-2.0",9,True,ACCENT)
    doc.setStrokeColor(colors.HexColor("#dce2e9")); doc.line(36,H-59,W-36,H-59)
    text(36,H-96,title,27,True)
    para(36,H-110,sub,W-72,11,MUTED)
    doc.line(36,45,W-36,45)
    text(36,27,"Prévia 0.1.0  |  07/10/2026  |  Dados fictícios nas imagens",9,color=MUTED)
    text(W-70,27,f"{number}/8",9,color=MUTED)

def image(file,x,y,w,h):
    im=Image.open(file); ratio=min(w/im.width,h/im.height)
    iw,ih=im.width*ratio,im.height*ratio
    doc.setFillColor(colors.white); doc.roundRect(x-3,y-3,w+6,h+6,8,fill=1,stroke=0)
    doc.drawImage(str(file),x+(w-iw)/2,y+(h-ih)/2,width=iw,height=ih)

def blocks(items,x=596,y=450,width=210):
    for title,body in items:
        y=para(x,y,"<b>"+title+"</b>",width,12,INK)
        y=para(x,y+6,body,width,10.5,MUTED)
    assert y>65,("Texto excede a página",y)

DOCS=ROOT/"docs"/"images"; CAP=ROOT/"output"/"media"/"captures"

start(1,"Seu conteúdo, em perspectiva.","Um estúdio de analytics para organizar canais, conteúdos, transmissões e comunidades.")
image(DOCS/"dashboard-dark.jpg",36,105,530,347)
blocks([
 ("A proposta","Canalytics segue a proposta do Observa: código Apache-2.0, instalação própria e dados no servidor do criador."),
 ("O que existe","Interface React/TypeScript, API FastAPI, SQLite, múltiplas áreas, autenticação e sincronização persistente."),
 ("Escopo desta prévia","Um administrador por instalação. A versão ainda não oferece convites, cobrança ou cadastro público de clientes."),
 ("Dados de demonstração","TGR Lab, TGR Live, TGR Community e TGR em 60s são recursos fictícios. As imagens não comprovam homologação externa."),
])
doc.showPage()

start(2,"Analytics com contexto.","Cada métrica mantém sua fonte, período e disponibilidade.")
image(DOCS/"dashboard-light.jpg",36,105,530,347)
blocks([
 ("Histórico diário","YouTube: views, minutos assistidos, inscritos ganhos/perdidos, curtidas, comentários e compartilhamentos."),
 ("Filtros e comparação","7, 28, 90 dias ou datas próprias. A comparação exige dois intervalos completos e base diferente de zero."),
 ("Público e receita","Tráfego, dispositivos e países usam o intervalo de coleta indicado. Receita estimada em USD exige permissão e elegibilidade."),
 ("Snapshots e CSV","Twitch, Discord e TikTok guardam observações de coleta. CSV autenticado preserva dados ausentes; não transforma totais em views do dia."),
])
doc.showPage()

start(3,"Investigue seus conteúdos.","Busca, ordenação e detalhes ajudam a relacionar publicações com a evolução do canal.")
image(DOCS/"contents.jpg",36,105,530,347)
blocks([
 ("Catálogo pesquisável","Ordenação por publicação ou views; contadores acumulados desde a publicação, independentes do filtro do gráfico."),
 ("Retenção do YouTube","Consulta sob demanda para um vídeo pertencente ao canal autorizado. A curva dos vídeos de QA é simulada."),
 ("Cobertura inicial","Até 500 vídeos YouTube, 100 VODs Twitch e 200 vídeos TikTok. O produto informa os limites da coleta."),
 ("Métricas ausentes","Campos indisponíveis continuam sem valor. Não há promessa de equivalência entre as plataformas ou soma de audiência única."),
])
doc.showPage()

start(4,"Conecte seu universo.","Aplicativos configurados pela interface, contas autorizadas pelo provedor e coletas em fila.")
image(DOCS/"connectors.jpg",36,105,530,347)
blocks([
 ("YouTube e Twitch","Adaptadores implementados e testados com respostas simuladas; OAuth e métricas reais ainda precisam ser homologados."),
 ("Discord e TikTok","Experimentais. Discord usa métricas aproximadas de servidor; TikTok usa perfil e contadores autorizados."),
 ("Bilibili","Planejado. O botão fica desabilitado para não sugerir uma integração já disponível."),
 ("Operação","Credenciais criptografadas, renovação de token, novas tentativas e reconexão com preservação de histórico do mesmo canal."),
])
doc.showPage()

start(5,"Organize projetos e aprendizados.","Áreas de trabalho separam recursos; o diário mantém anotações por canal.")
image(CAP/"26-diario-persistencia.jpg",36,154,372,285)
image(CAP/"29-area-vazia.jpg",432,154,372,285)
para(36,126,"<b>Diário do canal</b><br/>A anotação foi salva e continuou disponível após recarregar a página.",370,11)
para(432,126,"<b>Áreas independentes</b><br/>Um novo projeto começou sem dados. Voltar à área original restaurou seus quatro recursos.",370,11)
doc.showPage()

start(6,"Claro, escuro ou seguir o sistema.","A escolha é opcional e permanece salva neste navegador.")
image(ROOT/"output"/"media"/"temas-claro-escuro.png",36,132,W-72,325)
para(36,110,"<b>Controle rápido no topo e preferência nas configurações.</b> Também validado no celular: menu móvel, cards, conectores e largura sem rolagem horizontal. Trocar o tema não altera dados ou métricas.",W-72,11)
doc.showPage()

start(7,"O que foi verificado.","Testes locais, capturas da interface e limites conhecidos da entrega.")
style=ParagraphStyle("table",fontName="Canal",fontSize=10,leading=13,textColor=INK)
rows=[
 ["Verificação","Resultado","Natureza"],
 ["API e autorização","14 testes passaram","Bancos temporários e respostas simuladas"],
 ["Cálculos de analytics","3 testes passaram","Datas ausentes, períodos completos e receita parcial"],
 ["Interface de produção","Build passou","TypeScript e Vite"],
 ["Fluxos visuais","44 capturas; 8 vídeos","UI local com quatro recursos fictícios"],
 ["Exportação","180 registros CSV","API autenticada no QA"],
 ["Temas e celular","Persistência e largura verificadas","Claro, escuro e sistema"],
 ["Docker","Compose válido; engine inativo","Imagem não executada nesta máquina"],
 ["Contas das plataformas","Homologação pendente","Sem OAuth externo ou dados reais validados"],
]
rows=[[Paragraph(c,style) for c in row] for row in rows]
table=Table(rows,colWidths=[178,192,400])
table.setStyle(TableStyle([
 ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e8edf3")),
 ("VALIGN",(0,0),(-1,-1),"TOP"),("BOX",(0,0),(-1,-1),.5,colors.HexColor("#dbe1e8")),
 ("LINEBELOW",(0,0),(-1,-1),.4,colors.HexColor("#dbe1e8")),
 ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
 ("TOPPADDING",(0,0),(-1,-1),9),("BOTTOMPADDING",(0,0),(-1,-1),9),
]))
_,th=table.wrap(770,500); table.drawOn(doc,36,453-th)
para(36,453-th-16,"A suíte cobre isolamento entre áreas, OAuth vinculado à sessão, expiração/replay, reconexão, CSV seguro, exclusão durante coleta e erros sem vazamento de tokens. Exclusão e reconexão usam testes automatizados; o vídeo cancela a remoção. Os MP4 são sequências legendadas de capturas, sem áudio ou gravação contínua.",W-72,10.5,MUTED)
doc.showPage()

start(8,"Execute, explore e contribua.","Instalação local e documentação no repositório.")
text(40,437,"Começar com Docker",15,True)
text(40,405,"docker compose up --build -d",13,True,ACCENT)
para(40,379,"Abra <b>http://localhost:8093</b>. Explore a demonstração ou crie o primeiro administrador. O volume conserva o banco e a chave de criptografia; faça backup dos dois juntos.",365,11)
text(40,277,"Windows sem Docker",15,True)
text(40,245,".\\scripts\\start.ps1 -Install",13,True,ACCENT)
para(40,220,"Python 3.11+ e Node.js 22.6+. Depois da instalação inicial, execute o mesmo script sem -Install. Linux/macOS: <b>sh scripts/start.sh</b>.",365,11)
blocks([
 ("Próxima etapa","Homologar os fluxos oficiais com contas de teste reais, revisar retenção/revogação e ampliar relatórios por vídeo."),
 ("Como contribuir","Leia CONTRIBUTING.md, SECURITY.md e docs/ARQUITETURA.md. Testes usam dados fictícios e não acessam contas de criadores."),
 ("A visão ampliada","Equipes, publicação, moderação, previsões, Reporting API e marketplace de conectores permanecem no roadmap."),
 ("Distribuição","Repositório público: github.com/ThiagoRochaDev/canalytics. Licença Apache-2.0. Downloads na release v0.1.0. Nenhum serviço público da aplicação foi implantado."),
],x=443,y=448,width=357)
doc.showPage()
doc.save()

social=canvas.Canvas(str(OUT/"canalytics-linkedin.pdf"),pagesize=(540,675))
social.setTitle("Canalytics - carrossel LinkedIn")
social.setAuthor("TGR Technology")
for i in range(1,7):
    social.drawImage(str(ROOT/"output"/"media"/"linkedin"/f"{i:02d}-canalytics.png"),0,0,width=540,height=675)
    social.showPage()
social.save()
print("Dois PDFs criados: guia de 8 páginas e carrossel de 6 páginas.")
