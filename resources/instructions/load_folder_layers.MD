# 🗂️ Load Folder Layers — Guia de Uso

Ferramenta para carregar em lote arquivos vetoriais e raster de uma pasta, preservando opcionalmente a estrutura de diretórios como grupos no projeto QGIS.

---

## 🎯 Objetivo

Automatizar o carregamento de grandes volumes de arquivos geoespaciais, evitando duplicação, mantendo organização por grupos e fornecendo feedback contínuo ao usuário.

---

## 🛠️ Como usar

### 1️⃣ Selecione a pasta raiz
Clique no botão `...` ao lado do campo e selecione a pasta que contém os arquivos.

### 2️⃣ Escolha os tipos de arquivo
Marque os tipos desejados (Shapefile, GeoJSON, GeoPackage, TIFF, etc.).

### 3️⃣ Ajuste opções
- `Carregar apenas arquivos ainda NÃO carregados`: evita duplicações
- `Preservar estrutura de pastas`: cria grupos aninhados conforme diretório
- `Não agrupar a última pasta`: útil em conjunto com `Preservar estrutura`
- `Criar backup`: gera backup do projeto (apenas se projeto salvo)

### 4️⃣ Execute
Clique em `Carregar Arquivos`. A operação pode rodar de forma assíncrona se muitos arquivos forem detectados; o progresso será exibido.

---

## 🔎 Detalhes e comportamento

- Busca recursiva por arquivos nas subpastas
- `missing_only` filtra antes de adicionar ao projeto para evitar recarregar camadas já presentes
- Ao preservar estrutura, `ensure_group()` cria grupos aninhados usando `os.sep` para split
- Para grandes volumes, o pipeline assincrono (`AsyncPipelineEngine`) é utilizado para manter a UI responsiva

---

## 🧾 Resultado

- Resumo com contagem de arquivos processados
- Caminho do backup criado (se aplicável)
- Logs detalhados para itens com erro

---

## ✅ Boas práticas

- Teste com uma subpasta pequena antes de rodar o processamento completo
- Verifique permissões de leitura na pasta e espaço em disco
- Ative `Criar backup` quando estiver trabalhando em projetos críticos

---

## 🧩 Observações técnicas

- `FILE_TYPES` deve estar sincronizado com utilitários do `ExplorerUtils`
- `missing_only` precisa filtrar registros antes da adição ao projeto (performance)
- Use threshold razoável para mudar entre modo síncrono/assíncrono

---

## ❤️ Criado por

Matheus A.S. Martinelli
