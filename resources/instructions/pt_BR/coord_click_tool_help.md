# Capturar Coordenadas — Guia Rapido

Esta ferramenta permite clicar no mapa e abrir um painel com informacoes detalhadas do ponto selecionado.

No mesmo fluxo de uso, o `CoordClickTool` captura o ponto e o `CoorResultDialog` exibe e atualiza os resultados.

## Como usar

1. Ative `Cadmus > Capturar Coordenadas`.
2. Clique em qualquer ponto do mapa.
3. Veja o dialogo com:
- coordenadas WGS84 em decimal e DMS;
- coordenadas UTM;
- zona, hemisferio e EPSG;
- altitude aproximada;
- endereco aproximado.
4. Use os botoes para copiar os blocos de informacao desejados.
5. Clique novamente no mapa para atualizar o mesmo dialogo com um novo ponto.

## O que o plugin faz de verdade

- Captura a coordenada clicada com snapping quando houver snap valido no canvas.
- Converte o ponto para um conjunto de informacoes geograficas e UTM.
- Abre o dialogo de resultado na primeira vez e depois reutiliza essa mesma janela.
- Inicia uma pipeline assincrona com duas etapas em paralelo:
- geocodificacao reversa;
- consulta de altimetria.
- Se a pipeline falhar, tenta fallback com tarefas separadas.
- Cancela tarefas anteriores quando o usuario clica em outro ponto.

## O que aparece no dialogo

- Latitude e longitude em decimal.
- Latitude e longitude em DMS.
- Easting e Northing em UTM.
- Zona, hemisferio e EPSG.
- Altitude aproximada.
- Municipio, regiao intermediaria, estado, regiao e pais.
- Botoes para copiar WGS84, UTM ou a localizacao completa.

## Comportamento importante

- Coordenadas basicas aparecem primeiro; endereco e altitude podem demorar alguns segundos.
- Sem internet, o dialogo ainda mostra coordenadas, mas pode nao preencher endereco e altitude.
- O dialogo usa o mesmo `ToolKey` da ferramenta de clique, entao a ajuda correta e `coord_click_tool_help.md`.
- O botao de copiar localizacao completa envia um resumo textual para a area de transferencia.

## Quando usar

Use esta ferramenta quando precisar inspecionar rapidamente um ponto do mapa sem criar camada, feicao ou anotacao.

Ela e especialmente util para:

- conferir coordenadas em mais de um sistema;
- obter altitude aproximada do ponto;
- copiar localizacao para relatorios, mensagens ou documentos.

## Cuidados

- A altitude e aproximada e depende de servico externo.
- O endereco depende da cobertura do servico de geocodificacao reversa.
- Cliques sucessivos cancelam as consultas anteriores e passam a priorizar o ponto mais recente.
