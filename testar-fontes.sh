#!/bin/bash
# Duna Press — teste de feeds candidatos.
# Só entra no jornal o que responder aqui.

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

testar() {
  local nome="$1" url="$2"
  local n
  n=$(curl -s -L --max-time 20 -H "User-Agent: $UA" "$url" 2>/dev/null \
      | grep -c "<item\|<entry" 2>/dev/null || echo 0)
  if [ "$n" -gt 0 ] 2>/dev/null; then
    printf "  ok    %-26s %3s itens\n" "$nome" "$n"
    echo "            (\"$nome\", \"$url\")," >> /tmp/feeds_ok.txt
  else
    printf "  FORA  %-26s\n" "$nome"
  fi
}

rm -f /tmp/feeds_ok.txt
echo "ESPAÇO"
testar "NASA"            "https://www.nasa.gov/news-release/feed/"
testar "NASA Ciência"    "https://science.nasa.gov/feed/"
testar "ESA"             "https://www.esa.int/rssfeed/Our_Activities/Space_News"
testar "ESA Exploração"  "https://www.esa.int/rssfeed/Our_Activities/Human_and_Robotic_Exploration"
testar "Space.com"       "https://www.space.com/feeds/all"
testar "Xinhua Ciência"  "http://www.xinhuanet.com/english/rss/scitechrss.xml"

echo
echo "CIÊNCIA E TECNOLOGIA"
testar "Nature"          "https://www.nature.com/nature.rss"
testar "Science Daily"   "https://www.sciencedaily.com/rss/all.xml"
testar "Phys.org"        "https://phys.org/rss-feed/"
testar "MIT News"        "https://news.mit.edu/rss/feed"
testar "Agência FAPESP"  "https://agencia.fapesp.br/rss/"
testar "ScienceAlert"    "https://www.sciencealert.com/feed"

echo
echo "ECONOMIA E ESTATÍSTICA"
testar "FMI"             "https://www.imf.org/en/News/RSS"
testar "Banco Mundial"   "https://www.worldbank.org/en/news/rss.xml"
testar "OCDE"            "https://www.oecd.org/newsroom/index.xml"
testar "AIE energia"     "https://www.iea.org/rss/news"
testar "OMC comércio"    "https://www.wto.org/library/rss/latest_news_e.xml"
testar "FAO agricultura" "https://www.fao.org/feeds/news/en/"

echo
echo "ESPORTES"
testar "Fórmula 1"       "https://www.formula1.com/content/fom-website/en/latest/all.xml"
testar "Autosport F1"    "https://www.autosport.com/rss/f1/news/"
testar "UEFA"            "https://www.uefa.com/rssfeed/news/rss.xml"
testar "Olympics"        "https://olympics.com/en/news/rss"

echo
echo "SAÚDE E CLIMA"
testar "OMS"             "https://www.who.int/rss-feeds/news-english.xml"
testar "OPAS"            "https://www.paho.org/pt/rss.xml"
testar "ONU Meio Amb."   "https://www.unep.org/rss.xml"
testar "Copernicus"      "https://climate.copernicus.eu/rss.xml"

echo
echo "════════════════════════════════════════════════"
if [ -f /tmp/feeds_ok.txt ]; then
  echo "Feeds que responderam — copie para src/auto_publicar.py:"
  echo
  cat /tmp/feeds_ok.txt
else
  echo "Nenhum feed respondeu. Verifique a conexão."
fi
