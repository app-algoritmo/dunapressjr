#!/bin/bash
# Duna Press — segunda rodada de feeds candidatos.

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

testar() {
  local nome="$1" url="$2"
  local n
  n=$(curl -s -L --max-time 20 -H "User-Agent: $UA" "$url" 2>/dev/null \
      | grep -c "<item\|<entry" 2>/dev/null || echo 0)
  if [ "$n" -gt 0 ] 2>/dev/null; then
    printf "  ok    %-28s %3s itens\n" "$nome" "$n"
    echo "            (\"$nome\", \"$url\")," >> /tmp/feeds_ok2.txt
  else
    printf "  FORA  %-28s\n" "$nome"
  fi
}

rm -f /tmp/feeds_ok2.txt
echo "REGULAÇÃO BRASIL"
testar "ANVISA"          "https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/RSS"
testar "ANVISA alt"      "https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa@@rss"
testar "gov.br saúde"    "https://www.gov.br/saude/pt-br/assuntos/noticias/RSS"

echo
echo "CHINA"
testar "Xinhua Sci-Tech" "https://english.news.cn/tech/rss.xml"
testar "Xinhua geral"    "https://english.news.cn/rss/world.xml"
testar "Global Times"    "https://www.globaltimes.cn/rss/china.xml"
testar "SCMP Tech"       "https://www.scmp.com/rss/36/feed"
testar "CGTN"            "https://www.cgtn.com/subscribe/rss/section/business.xml"

echo
echo "RÚSSIA"
testar "TASS Ciência"    "https://tass.com/rss/v2.xml"
testar "Sputnik"         "https://sputnikglobe.com/export/rss2/archive/index.xml"
testar "RT Ciência"      "https://www.rt.com/rss/news/"

echo
echo "MUNDO ÁRABE"
testar "Al Jazeera"      "https://www.aljazeera.com/xml/rss/all.xml"
testar "Arab News"       "https://www.arabnews.com/rss.xml"
testar "The National"    "https://www.thenationalnews.com/arc/outboundfeeds/rss/"
testar "Gulf News Tech"  "https://gulfnews.com/rss?generatorName=technology"

echo
echo "IA, ROBÓTICA, AUTOMOTIVO"
testar "IEEE Spectrum"   "https://spectrum.ieee.org/feeds/feed.rss"
testar "IEEE Robótica"   "https://spectrum.ieee.org/feeds/topic/robotics.rss"
testar "MIT Tech Review" "https://www.technologyreview.com/feed/"
testar "Ars Technica"    "https://feeds.arstechnica.com/arstechnica/index"
testar "The Verge"       "https://www.theverge.com/rss/index.xml"
testar "Electrek"        "https://electrek.co/feed/"
testar "InsideEVs"       "https://insideevs.com/rss/articles/all/"
testar "Green Car Rep."  "https://www.greencarreports.com/rss/news"
testar "Robot Report"    "https://www.therobotreport.com/feed/"
testar "VentureBeat IA"  "https://venturebeat.com/category/ai/feed/"
testar "arXiv IA"        "http://export.arxiv.org/rss/cs.AI"
testar "arXiv Robótica"  "http://export.arxiv.org/rss/cs.RO"

echo
echo "════════════════════════════════════════════════"
if [ -f /tmp/feeds_ok2.txt ]; then
  echo "Responderam — copie para src/auto_publicar.py:"
  echo
  cat /tmp/feeds_ok2.txt
else
  echo "Nenhum respondeu. Verifique a conexão."
fi
