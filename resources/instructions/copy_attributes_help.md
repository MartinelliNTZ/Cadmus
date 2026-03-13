# 📘 Copiar Atributos — Guia de Uso

Ferramenta para copiar campos (atributos) de uma camada origem para uma camada destino, com seleção de campos e resolução interativa de conflitos.

---

## 🎯 Objetivo

Permitir transferir atributos entre camadas vetoriais de forma controlada, preservando tipos de dados e oferecendo opções para tratar conflitos de nomes/colunas.

---

## 🛠️ Como usar

### 1️⃣ Abrir a ferramenta
Menu → Cadmus → Copiar Atributos

### 2️⃣ Selecionar camadas
- `Camada destino`: a camada que receberá os campos
- `Camada origem`: a camada que fornece os campos

### 3️⃣ Escolher atributos
- Marque `Usar todos os atributos` para copiar todos os campos
- Ou selecione manualmente os campos desejados na lista

### 4️⃣ Executar
Clique em `Executar`. Se houver conflito de nomes, a ferramenta solicitará ação: sobrescrever, renomear ou pular o campo conflitante.

---

## ℹ️ O que acontece por trás

- Os campos selecionados são adicionados à `camada destino` com mapeamento por feição.
- A operação modifica a camada destino em memória (alterações ficam pendentes para salvar ou descartar).
- Conflitos de nomes são tratados via diálogo interativo (`QgisMessageUtil.ask_field_conflict`).

---

## ⚠️ Problemas comuns e soluções

- Conflito de nomes: responda ao diálogo para sobrescrever, renomear ou pular.
- Tipos incompatíveis: alguns valores podem ficar vazios ou truncados — prefira campos com tipos compatíveis.
- Camada destino não editável: verifique permissões e se a camada está desbloqueada.

---

## ✅ Checklist pós-execução

- Campos esperados presentes na camada destino
- Valores amostrados visualmente corretos
- Salvou as alterações se necessário

---

## 🔧 Preferências e logs

- Chave de preferências/logs: `copy_attributes`
- Em caso de erro, veja o log do plugin e reporte: tipo de camada, número de feições, campos selecionados

---

## 💡 Boas práticas

- Faça backup da camada destino antes de operações em massa
- Prefira copiar apenas os campos necessários para evitar inflar o esquema
- Teste em um subconjunto de feições quando possível

---

## ❤️ Criado por

Matheus A.S. Martinelli

