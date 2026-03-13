## 📦 Bibliotecas necessárias
# 🧾 Export All Layouts — Guia de Uso

ExportAllLayouts é uma ferramenta do pacote **Cadmus** para exportar todos os layouts do projeto em PDF e/ou PNG, com opções adicionais de união de arquivos e controle de sobrescrita.

---

## 🎯 Objetivo

Automatizar a exportação em lote de layouts, oferecendo:
- Exportação por layout em PDF e/ou PNG
- União dos PDFs gerados em um único arquivo final
- Conversão/união de PNGs em PDF final (opcional)
- Controle de sobrescrita de arquivos existentes
- Persistência das preferências do usuário

---

## 🛠️ Como usar

### 1️⃣ Abra a ferramenta
Menu → Cadmus → Export All Layouts

### 2️⃣ Defina formatos
Marque `Exportar PDF` e/ou `Exportar PNG`.

### 3️⃣ Ajuste opções extras
- `Unir PDFs`: mescla os PDFs gerados em um único arquivo
- `Unir PNGs`: gera PNGs e os converte/une em PDF
- `Substituir arquivos existentes`: controla sobrescrita (se desmarcado, sufixos serão adicionados)
- `Max Width`: largura máxima para PNGs quando unidos em PDF

### 4️⃣ Escolha a pasta de saída
Informe manualmente, selecione via seletor ou use a pasta do projeto (`.../exports/`). A pasta será criada se não existir.

### 5️⃣ Execute
Clique em `Exportar`. O diálogo exibirá progresso, permitirá cancelar e mostrará um resumo ao final.

---

## 🔎 Dependências

Algumas funcionalidades exigem bibliotecas externas:
- `PyPDF2`: necessária para unir PDFs
- `Pillow`: necessária para trabalhar com PNG → PDF

Se estiverem ausentes, a ferramenta oferece instalação assistida (scripts em `lib/`); reinicie o QGIS após instalar.

---

## 🧾 Logs e resultado

- Logs detalhados por layout (nome, formato, destino, status)
- Resumo final com contagem de layouts processados e arquivos gerados

---

## ✅ Boas práticas

- Verifique espaço em disco antes de executar em grandes projetos
- Teste com alguns layouts antes de exportar tudo
- Se pedir união de PDFs/PNGs, prefira uma pasta de saída vazia para evitar confusão com arquivos antigos

---

## 🧩 Chave de preferências

`export_all_layouts`

---

## ❤️ Criado por

Matheus A.S. Martinelli

