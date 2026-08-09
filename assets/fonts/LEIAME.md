# Fontes

Vazio de propósito. Os `.woff2` não vêm no repositório inicial porque
precisam ser baixados uma vez:

```bash
python3 tools/baixar_fontes.py
```

Depois disso, **versione os arquivos**. A partir daí o site serve as fontes
do próprio domínio: uma conexão externa a menos no caminho crítico, e nenhum
IP de leitor enviado a terceiro — o que importa sob LGPD.

Enquanto os arquivos não existirem, o navegador cai nas fontes de sistema
(Georgia e Helvetica). O jornal continua legível, só perde a identidade
tipográfica.

## Arquivos esperados

```
spectral-600.woff2          manchetes
spectral-700.woff2          manchete principal
spectral-400i.woff2         itálico de citação
source-serif-400.woff2      corpo de texto
source-serif-600.woff2      corpo em negrito
source-serif-400i.woff2     corpo em itálico
libre-franklin-400.woff2    legendas
libre-franklin-600.woff2    assinatura
libre-franklin-700.woff2    chapéu e rótulos
```
