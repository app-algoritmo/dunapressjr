/* Duna Press — interface do jornal.
 *
 * O site funciona inteiro sem JavaScript: o HTML já vem pronto do servidor.
 * Este arquivo só acrescenta conforto. Nada aqui é necessário para ler.
 */
(function () {
  "use strict";

  /* Navegação por editorias: em telas estreitas a barra rola na horizontal.
     Centralizamos a editoria corrente para que ela nasça visível. */
  function centrarEditoriaAtual() {
    var barra = document.querySelector(".nav .env");
    if (!barra) return;
    var atual = barra.querySelector("[aria-current]");
    if (!atual || barra.scrollWidth <= barra.clientWidth) return;
    barra.scrollLeft = atual.offsetLeft - (barra.clientWidth - atual.offsetWidth) / 2;
  }

  /* Busca. O índice é um JSON estático gerado no build; não há servidor.
     Carrega sob demanda: quem não busca, não baixa. */
  var indice = null, carregando = null;

  function carregarIndice() {
    if (indice) return Promise.resolve(indice);
    if (carregando) return carregando;
    carregando = fetch("/api/busca.json")
      .then(function (r) { return r.json(); })
      .then(function (d) { indice = d; return d; })
      .catch(function () { return []; });
    return carregando;
  }

  function normalizar(t) {
    return t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  }

  function procurar(termo, dados) {
    var t = normalizar(termo.trim());
    if (t.length < 3) return [];
    var partes = t.split(/\s+/);
    return dados.filter(function (a) {
      var alvo = normalizar(a.t + " " + (a.o || ""));
      return partes.every(function (p) { return alvo.indexOf(p) !== -1; });
    }).slice(0, 12);
  }

  function ligarBusca() {
    var campo = document.getElementById("busca");
    var saida = document.getElementById("busca-resultado");
    if (!campo || !saida) return;

    var espera;
    campo.addEventListener("input", function () {
      clearTimeout(espera);
      var termo = campo.value;
      if (termo.trim().length < 3) { saida.innerHTML = ""; return; }
      espera = setTimeout(function () {
        carregarIndice().then(function (dados) {
          var achados = procurar(termo, dados);
          if (!achados.length) {
            saida.innerHTML = '<p class="olho">Nada encontrado para “' +
              termo.replace(/[<>&]/g, "") + '”.</p>';
            return;
          }
          saida.innerHTML = achados.map(function (a) {
            return '<article class="chamada">' +
              '<span class="chapeu">' + a.e + "</span>" +
              '<h3 class="titulo"><a href="' + a.u + '">' + a.t + "</a></h3>" +
              '<div class="credito">' + a.d + "</div></article>";
          }).join("");
        });
      }, 180);
    });
  }

  /* Ano corrente no rodapé, para o texto não envelhecer sozinho. */
  function atualizarAno() {
    var alvo = document.querySelector("[data-ano]");
    if (alvo) alvo.textContent = String(new Date().getFullYear());
  }

  if (document.readyState !== "loading") iniciar();
  else document.addEventListener("DOMContentLoaded", iniciar);

  function iniciar() {
    centrarEditoriaAtual();
    ligarBusca();
    atualizarAno();
  }
})();
