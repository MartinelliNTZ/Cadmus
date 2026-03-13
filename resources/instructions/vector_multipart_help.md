# 📘 Converter Multipart — Guia Rápido e Intuitivo

Breve: converte geometrias multipart em singlepart (ou vice-versa), permitindo separar ou unir partes de feições. 🔗

---

## ▶ Passo a passo (rápido) ✅

1. Abra: Menu → **Cadmus** → **Converter Multipart**
2. Selecione a **camada vetorial** (pontos, linhas ou polígonos). 🗂️
3. Decida o escopo:
   - **Apenas selecionadas**: Se houver feições selecionadas, confirme se quer converter só essas. ✂️
   - **Todas**: Se não houver seleção, todas as feições serão convertidas. 🌐
4. Confirme a operação quando solicitado. ✅
5. A camada fica em modo de edição — revise os resultados antes de salvar. 💾

---

## ℹ️ O que acontece por trás (resumido)

- **Multipart para Singlepart**: Geometrias com múltiplas partes são divididas em feições individuais, cada uma com uma parte. 📍
- **Singlepart para Multipart**: Geometrias com apenas uma parte são agrupadas (mais comum em workflows específicos). 🔀
- **Edit Buffer**: A operação roda no edit buffer — suas alterações ficam na memória até você salvar ou descartar. 💾
- **Não salva automaticamente**: Se a camada já estava em edição, as alterações não são salvas automaticamente. ⚠️

---

## 💡 Dicas rápidas

- **Faça backup**: Sempre salve uma cópia de backup da camada original antes de converter. 📦
- **Use seleção**: Para converter apenas parte dos dados, selecione as feições desejadas antes de abrir a ferramenta. ✂️
- **Revise antes de salvar**: Após a conversão, revise visualmente no mapa antes de confirmar as alterações. 👀
- **Camadas Shapefile**: Shapefiles podem ter limitações — considere usar GeoPackage (`.gpkg`) para operações complexas. 🗄️

---

## ⚠️ Problemas comuns e solução

- **"Camada não editável"** → Desbloqueie a camada ou copie para uma nova camada editável. 🔐
- **Muitas novas feições criadas** → Esperado! Multipart → Singlepart cria uma feição por parte. Você pode desfazer (Ctrl+Z). 🔄
- **Atributos duplicados** → Cada nova feição herda os mesmos atributos da feição original. 📋
- **Erro ao salvar após conversão** → Verifique se o formato suporta o número de feições (Shapefile tem limite). 🚨

---

## ✅ Checklist rápido pós-execução

- Feições foram convertidas conforme esperado? ✔️
- Número de feições está correto? ✔️
- Atributos foram preservados? ✔️
- Salvou (ou descartou) as alterações? ✔️

---

## 🔧 Preferências e suporte

- A ferramenta usa a chave interna `vector_multipart` para logs.
- **Desfazer (Ctrl+Z)**: Funciona enquanto a camada estiver em edição.
- **Cancelar operação**: Clique no "X" da barra de progresso durante a operação.
- Em caso de erro, reporte com: tipo de geometria, número de feições e formato do arquivo (`.shp`, `.gpkg`, etc). 🐞
