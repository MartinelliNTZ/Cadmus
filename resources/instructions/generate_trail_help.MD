
# 📘 Gerar Rastro Implemento — Guia Rápido e Intuitivo

Breve: gera o polígono que representa a faixa ocupada por um implemento a partir de uma camada de linhas (trajetória / passadas). 🚜

---

## ▶ Passo a passo (rápido) ✅

1. Abra: Menu → **Cadmus** → **Gerar Rastro Implemento**
2. Selecione a **camada de linhas (INPUT)**. 🗂️
3. Informe o **Tamanho do implemento (metros)** — ex.: 12, 16, 24. 📏
4. (Opcional) Marque **Salvar em arquivo** e escolha o caminho/fomato (recomendado: `.gpkg`). 💾
5. (Opcional) Marque **Aplicar estilo (QML)** e selecione um `.qml`. 🎨
6. Clique em **Executar** ▶️ — o processamento roda em segundo plano e a camada aparece automaticamente ao final.

---

## ℹ️ O que acontece por trás (resumido)

- O valor informado em metros é convertido automaticamente para as unidades da camada.
- O plugin calcula o buffer como **metade** do valor informado: `buffer = tamanho / 2`. ➗
- Pipeline: **Explode → Buffer → Save** — execução assíncrona (não trava a interface). ⚙️

---

## 💡 Dicas rápidas

- Se a camada estiver em graus (EPSG:4326), reprojete para um CRS métrico (ex.: UTM) para resultados precisos. 🌍 → 📐
- Não informe `0` como tamanho (a operação será abortada). ❌
- Prefira `GeoPackage (.gpkg)` ao salvar (mais robusto que Shapefile). 🗄️

---

## ⚠️ Problemas comuns e solução

- Resultado estranho → verifique o CRS e reprojete se estiver em graus. 🔁
- Erro ao salvar → verifique permissões de gravação e extensão do arquivo. 🔐

---

## ✅ Checklist rápido pós-execução

- A camada resultante foi adicionada ao projeto? ✔️
- Geometria com aparência correta (largura esperada)? ✔️
- Atributos e estilo aplicados conforme esperado? ✔️

---

## 🔧 Preferências e suporte

- O plugin lembra: último tamanho, opção de salvar e último QML usado.
- Em caso de erro, abra o painel de logs do plugin e anexe informações sobre a camada e passos executados ao reportar. 🐞

