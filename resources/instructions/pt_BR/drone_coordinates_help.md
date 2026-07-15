# Coordenadas de Drone — Guia Rapido

Esta ferramenta le arquivos MRK de drone e gera uma camada de pontos com as posicoes registradas no voo.

Ela tambem pode criar uma linha de trajeto a partir desses pontos, cruzar os registros com metadados das fotos e salvar os resultados em arquivo.

## Como usar

1. Abra `Cadmus > Coordenadas de Drone`.
2. Escolha a pasta que contem os arquivos MRK.
3. Ajuste as opcoes, se necessario:
- `Vasculhar subpastas`: procura MRKs dentro das subpastas.
- `Cruzar com metadados das fotos`: tenta enriquecer os pontos com informacoes das imagens JPG.
4. Se quiser, configure o salvamento dos pontos e do rastro em arquivo.
5. Se quiser, selecione arquivos QML para aplicar estilo aos pontos e ao rastro.
6. Execute a ferramenta.

## O que o plugin faz de verdade

- Inicia uma pipeline assincrona com `MrkParseStep`.
- Cria uma camada de pontos chamada `MRK_Pontos` a partir dos registros lidos.
- Se a opcao de fotos estiver ativa, executa tambem `PhotoMetadataStep`.
- Pode adicionar campos extras com nome do arquivo, datas, dimensoes da imagem, camera, ISO, abertura e outros metadados.
- Gera uma camada de linha conectando os pontos por grupos de `mrk_path` e `mrk_file`.
- Adiciona as camadas geradas ao projeto.
- Pode salvar pontos e rastro em arquivo com renomeacao automatica se o destino ja existir.
- Pode aplicar estilos QML aos pontos e ao rastro quando essa opcao estiver habilitada.

## Comportamento importante

- A ferramenta trabalha a partir de uma pasta, nao de uma camada ja carregada.
- O cruzamento com fotos depende de haver imagens compativeis nas pastas relacionadas ao MRK.
- Se os metadados das fotos nao forem encontrados, os pontos ainda podem ser gerados sem esse enriquecimento.
- O processamento principal roda em background.
- Os pontos sao sempre gerados primeiro; o rastro e derivado desses pontos.

## Saidas geradas

- Pontos MRK em camada de memoria ou arquivo.
- Rastro do voo em camada de memoria ou arquivo.
- Estilo opcional aplicado separadamente para pontos e linha.

## Quando usar

Use esta ferramenta quando quiser transformar arquivos MRK em produtos espaciais que possam ser visualizados e analisados no QGIS.

Ela e especialmente util para:

- mapear posicoes das fotos do voo;
- reconstruir o trajeto do drone;
- enriquecer os pontos com dados tecnicos das imagens.

## Cuidados

- Confirme que a pasta selecionada realmente contem arquivos MRK validos.
- Se for usar cruzamento com fotos, mantenha a organizacao das pastas consistente com o voo.
- Se quiser persistir os resultados, prefira salvar em `gpkg`.
