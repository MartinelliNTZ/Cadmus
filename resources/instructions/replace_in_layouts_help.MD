# 🧩 Substituir Texto em Layouts — Guia Completo de Uso

Bem-vindo à ferramenta **Substituir Texto em Layouts** do pacote **Cadmus**!  
Ela foi desenvolvida para automatizar substituições de texto em massa dentro dos *Layouts* do QGIS, permitindo atualizar dezenas ou centenas de rótulos em questão de segundos com total segurança, rastreabilidade completa via backup automático e log detalhado de operações.

---

## 🎯 Objetivo da Ferramenta

Esta ferramenta localiza ocorrências de texto dentro de **QgsLayoutItemLabel** (rótulos/textos nos layouts) e substitui automaticamente por outro texto definido pelo usuário.

Use quando precisar:

- Atualizar anos em documentos (ex.: “2023” → “2025”)
- Corrigir nomes de órgãos, clientes, setores ou responsáveis
- Padronizar grafias (“Km” → “KM”)
- Remover textos obsoletos
- Atualizar versões de mapas e plantas
- Fazer substituições repetitivas sem risco de esquecer algum item

---

## 🛠️ Como usar

### 1️⃣ Acessando a Ferramenta
No menu do QGIS:

**Cadmus → Replace Text in Layouts**

A janela principal será exibida com os campos necessários.

---

### 2️⃣ Preenchendo os Campos

- **Texto a buscar**  
  O texto presente nos layouts que você deseja localizar.  
  Exemplo: `SEINFRA 2023`

- **Texto a substituir (novo)**  
  O texto que entrará no lugar do antigo.  
  Exemplo: `SEINFRA 2024`

- **Case Sensitive**  
  - **Marcado:** diferencia letras maiúsculas/minúsculas  
  - **Desmarcado:** ignora diferença (recomenda-se para a maioria dos casos)

- **Modo Chave (opcional)**  
  Quando ativado, substitui **todo o conteúdo do rótulo** se o texto buscado for encontrado, em vez de substituir apenas a parte correspondente.  
  Útil para rótulos com textos completos variáveis.

- **⇅ Botão Inverter**  
  Clique rapidamente para trocar o conteúdo dos campos "Texto a buscar" e "Texto a substituir".  
  Muito útil para reverter uma substituição anterior (manual undo) sem digitar novamente.

---

## 🗄️ Backup Automático e Log de Auditoria

Sempre que você executa uma substituição com o projeto **salvo em disco**, o plugin cria automaticamente:

### 📁 Arquivo de Backup
O backup completo do projeto `.qgz` é armazenado em:

```
📁 [pasta do seu projeto] → 📁 backup → 📄 nome_projeto_YYYYMMDDHHMMSS.qgz
```

Exemplo:
- Seu projeto: `/projetos/mapa_2024.qgz`
- Backup criado: `/projetos/backup/mapa_2024_20260309_110534.qgz`

✅ **Cada execução gera um novo backup** (não sobrescreve o anterior) — você pode reverter para qualquer versão anterior acessando a pasta `/backup/`.

### 📋 Arquivo de Log
Um arquivo de log detalhado com todas as operações é criado:

```
📄 backup/replace_log_YYYYMMDDHHMMSS.txt
```

O log registra:
- 🔍 Número total de layouts analisados
- ✏️ Número total de substituições aplicadas
- 📌 **Lista detalhada** de cada layout alterado
- 🔄 Conteúdo antes e depois de cada substituição
- ⏰ Data, hora e duração da operação
- ⚠️ Qualquer aviso ou erro encontrado

**Exemplo de log:**
```
=================== REPLACE LOG ===================
Data/Hora: 2026-03-09 11:05:34
Duração: 1.234s

Projeto: mapa_2024.qgz
Busca: "2023"
Substituição: "2024"
Case Sensitive: Não
Modo Chave (full replace): Não

Layouts analisados: 5
Substituições aplicadas: 15

Detalhes por layout:
─────────────────────
[Layout 1] Mapa Principal
  - Rótulo "Ano de referência": "2023" → "2024"
  - Rótulo "Mapa de 2023": "2023" → "2024"

[Layout 2] Resumo Técnico
  - Rótulo "Data": "Ago 2023" → "Ago 2024" ❌ (parcial, contém "2023")
  - ... (mais substituições)

Backup criado: mapa_2024_20260309_110534.qgz
Status: ✅ Operação concluída com sucesso
================================================
```

### ⚠️ Se o Projeto Não Estiver Salvo
Se você tentar realizar uma substituição em um projeto **novo ou ainda não salvo**, o plugin avisará:

> ⚠️ **"Projeto não salvo. Continuar sem backup?"**

Você terá **duas opções:**
- **Sim**: Continua a substituição SEM criar backup (não recomendado).
- **Não**: Cancela a operação (recomendado — salve o projeto primeiro).

💡 **Dica**: Sempre **salve seu projeto** (`File → Save`) antes de usar a ferramenta para preservar seu histórico completo de backups.

Esse registro é essencial para auditoria e rastreabilidade.

## 🔧 Preferências e Memória de Estado

A ferramenta **lembra automaticamente** de suas preferências de uso:

- ✍️ **Último texto buscado** — campo "Texto a buscar" preenchido com valor anterior
- ✏️ **Último texto de substituição** — campo "Texto a substituir (novo)" preenchido
- ☑️ **Opções marcadas** — estado de "Case Sensitive" e "Modo Chave" preservado
- 📏 **Tamanho da janela** — a ferramenta abre com o tamanho que você definiu última vez

**Onde ficam armazenadas:**
- 📁 `~/.qgis3/` (pasta oculta do QGIS no seu perfil do Windows)
- 🗂️ Arquivo: `plugins/Cadmus_prefs.json` (ou similar, conforme versão)

Essas preferências são **carregadas automaticamente** ao abrir a ferramenta novamente, economizando tempo em operações repetitivas.

---

## 🔄 Desfazendo uma Substituição

Se você fez uma substituição e precisa **reverter**, existem três opções:

### ✅ Opção 1: Usar o Botão "⇅ Inverter" (Rápido!)
1. A ferramenta ainda tem os valores da última execução em memória
2. Clique no botão **⇅ Inverter** 
3. Os campos são trocados automaticamente:
   - Texto a buscar: "2024" (o novo texto)
   - Texto a substituir: "2023" (o antigo)
4. Clique em "Executar" — operação inversa executa em segundos

✨ **Isso é um manual undo rápido e seguro!**

### ✅ Opção 2: Restaurar do Backup (Mais Seguro)
Se você fez múltiplas substituições ou quer voltar completamente:

1. Acesse: 📁 `[pasta do seu projeto]/backup/`
2. Selecione o arquivo `.qgz` anterior ao desejado (compare datas)
3. Copie o arquivo para a pasta principal
4. Renomeie para o nome do projeto
5. Abra o projeto no QGIS

📋 O log de cada backup mostra exatamente que alterações foram feitas — você pode escolher qual versão restaurar.

### ✅ Opção 3: Edição Manual (Se Necessário)
Se as opções anteriores não funcionarem:

1. Abra o projeto no QGIS
2. Clique duplo em cada rótulo para editar manualmente
3. Corrija o conteúdo conforme necessário
4. Salve o projeto

---

## 🚀 Boas práticas de uso

Para garantir substituições seguras e previsíveis:

- Salve o projeto antes de usar a ferramenta  
- Use buscas específicas para evitar substituições indesejadas  
- Evite termos muito genéricos (ex.: “KM”)  
- Prefira expressões completas (“KM 123+500”)  
- Revise o log após a execução para confirmar todas as alterações  
- Utilize o modo chave apenas quando realmente necessário

---

## ❤️ Criado por

**Matheus A.S. Martinelli**  
Ferramentas práticas para acelerar fluxos reais de cartografia e geoprocessamento no QGIS.
