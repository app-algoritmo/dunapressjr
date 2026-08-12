#!/bin/bash
# Duna Press — terceira rodada: organismos multilaterais.

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

testar() {
  local nome="$1" url="$2"
  local n
  n=$(curl -s -L --max-time 20 -H "User-Agent: $UA" "$url" 2>/dev/null \
      | grep -c "<item\|<entry" 2>/dev/null || echo 0)
  if [ "$n" -gt 0 ] 2>/dev/null; then
    printf "  ok    %-30s %3s itens\n" "$nome" "$n"
    echo "            (\"$nome\", \"$url\")," >> /tmp/feeds_ok3.txt
  else
    printf "  FORA  %-30s\n" "$nome"
  fi
}

rm -f /tmp/feeds_ok3.txt
echo "ECONOMIA E FINANÇAS"
testar "Banco Mundial"       "https://www.worldbank.org/en/news/all.rss"
testar "Banco Mundial alt"   "https://www.worldbank.org/en/rss"
testar "BCE"                 "https://www.ecb.europa.eu/rss/press.html"
testar "BCE pressers"        "https://www.ecb.europa.eu/press/rss/press.xml"
testar "Eurostat"            "https://ec.europa.eu/eurostat/api/dissemination/catalogue/rss/en/news.rss"
testar "Trading Economics"   "https://tradingeconomics.com/rss/news.aspx"
testar "BIS"                 "https://www.bis.org/list/press_rlsegen/index.rss"
testar "FMI blog"            "https://www.imf.org/en/Blogs/rss"

echo
echo "CIÊNCIA"
testar "CERN"                "https://home.cern/api/news/news/feed.rss"
testar "CERN alt"            "https://home.cern/rss.xml"
testar "ESO astronomia"      "https://www.eso.org/public/rss/news/"
testar "Max Planck"          "https://www.mpg.de/rss/institutes"

echo
echo "JUSTIÇA E SEGURANÇA"
testar "TPI"                 "https://www.icc-cpi.int/rss.xml"
testar "TPI alt"             "https://www.icc-cpi.int/news/rss"
testar "Interpol"            "https://www.interpol.int/en/rss.xml"
testar "Interpol alt"        "https://www.interpol.int/rss/news.xml"
testar "Corte Int. Justiça"  "https://www.icj-cij.org/rss/news"
testar "UNODC drogas"        "https://www.unodc.org/unodc/en/frontpage/rss.xml"

echo
echo "════════════════════════════════════════════════"
if [ -f /tmp/feeds_ok3.txt ]; then
  echo "Responderam:"; echo
  cat /tmp/feeds_ok3.txt
else
  echo "Nenhum respondeu."
fi
