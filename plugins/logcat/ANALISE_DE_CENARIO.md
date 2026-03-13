# LOGCAT - ANÁLISE DE CENÁRIOS

**Última Atualização**: 22 de Janeiro de 2026  
**Versão**: 1.0

---

## ÍNDICE

1. [Cenários de Uso](#cenários-de-uso)
2. [Cenários de Erro](#cenários-de-erro)
3. [Cenários de Performance](#cenários-de-performance)
4. [Cenários de Manutenção](#cenários-de-manutenção)

---

## CENÁRIOS DE USO

### Cenário 1: Investigação de Bug em Tempo Real

**Contexto**: Usuário está rodando uma ferramenta (ex: vector_field) e quer ver os logs em tempo real para debugar.

**Fluxo**:
```
1. Abre Logcat (Menu > Cadmus > Logcat)
2. Vê sessão atual já carregada
3. Executa a ferramenta que causa o bug
4. Logs novos aparecem na tabela automaticamente (a cada ~1s)
5. Duplo-clica em linha suspeita
6. Vê traceback completo em LogDetailDialog
7. Identifica o problema (ex: "ValueError: invalid coordinate")
8. Fecha Logcat
9. Corrige código ou dados
```

**Componentes Ativados**:
- ✓ LogSessionManager (discovery)
- ✓ LogLoader (load_all inicial)
- ✓ LogFileWatcher (monitoramento)
- ✓ LogTableModel (display)
- ✓ LogDetailDialog (detalhe)

**Performance Esperada**:
- Abertura: ~500ms
- Update de novo log: ~100ms
- Duplo-clique: instantâneo

**Pontos de Falha Possíveis**:
- Arquivo de log não criado → nada aparece
- Permissões de leitura → erro ao abrir
- Disco muito lento → lag de 1-2s

---

### Cenário 2: Análise de Histórico - Buscar Erro Específico

**Contexto**: Um usuário relata um erro que ocorreu há 2 horas. Dev quer investigar os logs daquele momento.

**Fluxo**:
```
1. Abre Logcat
2. Dropdown de sessão mostra: "logcat_20260122_110000_pid1234", "logcat_20260122_090000_pid5678", etc
3. Seleciona sessão de 2 horas atrás
4. LogLoader carrega arquivo histórico (~5000 logs)
5. Vê tabela com dados daquela sessão
6. Usa "Search" para filtrar: "ValueError"
7. Encontra 3 entradas
8. Duplo-clica em linha 2 (a mais suspeita)
9. Vê traceback completo
10. Analisa, encontra raiz do problema
11. Anota informações e fecha
```

**Componentes Ativados**:
- ✓ LogSessionManager (discovery de múltiplas sessões)
- ✓ LogLoader (load_all de histórico)
- ✓ LogFilterEngine (busca por texto)
- ✓ LogTableModel (display filtrado)
- ✓ LogDetailDialog (análise detalhada)

**Performance Esperada**:
- Mudança de sessão: ~1-2s (load_all)
- Filtro de texto: ~100ms
- Duplo-clique: instantâneo

**Pontos de Falha Possíveis**:
- Sessão deletada → "Session not found"
- Arquivo de log corrompido (JSON inválido) → tolerância via parse-tolerante
- Disco lento → lag de 2-3s

---

### Cenário 3: Filtragem Avançada - Múltiplos Critérios

**Contexto**: Dev quer ver APENAS logs de ERROR do tool "vector_field" de classe "FieldCalculator".

**Fluxo**:
```
1. Abre Logcat
2. Tabela mostra ~2000 entradas
3. Clica "Level" → Popup
4. Desseleciona tudo, seleciona "ERROR"
5. Clica "Tool" → Popup
6. Seleciona "vector_field"
7. Clica "Class" → Popup
8. Seleciona "FieldCalculator"
9. Clica "Clear Filters" (teste)
10. Volta a 2000 entradas
11. Reaplica filtros manualmente
12. Agora vê apenas 3 ERRORs relevantes
```

**Componentes Ativados**:
- ✓ LogFilterEngine (3 filtros aplicados)
- ✓ LogTableModel (update após cada filtro)
- ✓ UI popup filters

**Performance Esperada**:
- Cada filtro: ~100-200ms
- Total 3 filtros: ~500ms

**Pontos de Falha Possíveis**:
- Nenhuma entrada matching → tabela vazia (OK, mensagem de status clara)
- Filtro buggado → nada muda (dev deve debugar LogFilterEngine)

---

### Cenário 4: Export para Análise Externa

**Contexto**: Dev quer exportar 50 logs filtrados para enviarcomo texto para colega revisar.

**Fluxo**:
```
1. Abre Logcat
2. Filtra: Level=WARNING, Tool=rastro
3. Tabela mostra 50 WARNING do rastro
4. Clica "Export Filter"
5. LogMultipleDetailDialog abre
6. Vê aba "Combined": todos 50 mesclados com separadores
7. Seleciona tudo (Ctrl+A)
8. Copia (Ctrl+C)
9. Cola em arquivo de texto ou email
10. Envia para colega
```

**Componentes Ativados**:
- ✓ LogFilterEngine (filtragem)
- ✓ LogMultipleDetailDialog (export)

**Performance Esperada**:
- Export de 50 entradas: ~50ms
- Dialog open: instantâneo

**Pontos de Falha Possíveis**:
- Nenhuma entrada filtrada → warning "No filtered entries"
- Quantidade muito grande (1000+) → peut être lent, mas OK

---

### Cenário 5: Multi-Seleção e Export Customizado

**Contexto**: Dev quer ver detalhes de 3 linhas específicas que ele selecionou manualmente.

**Fluxo**:
```
1. Tabela mostra ~500 entradas
2. Dev clica linha 50 (sem seleção anterior)
3. Dev Ctrl+Click linha 150 (multi-select)
4. Dev Ctrl+Click linha 300 (multi-select)
5. Status bar: "3 rows selected"
6. Clica "Export Selection"
7. LogMultipleDetailDialog abre com as 3 selecionadas
8. Vê abas: "Combined", "Tab 1 of 3", "Tab 2 of 3", "Tab 3 of 3"
9. Review cada uma
10. Copia informações
11. Fecha
```

**Componentes Ativados**:
- ✓ QTableView multi-selection
- ✓ LogMultipleDetailDialog

**Performance Esperada**:
- Multi-select: instantâneo
- Dialog open com 3 entradas: ~10ms

**Pontos de Falha Possíveis**:
- Proxy model index mismatch → entry não encontrado (debugar mapToSource)

---

## CENÁRIOS DE ERRO

### Cenário E1: Parse de JSON Inválido

**Situação**: Arquivo de log tem uma linha com JSON corrompido.

```json
{"ts": "2026-01-22", "level": "INFO", ...}  // OK
{"ts": "2026-01-22", "level": "ERROR"      // Faltam aspas!
{"ts": "2026-01-22", "level": "DEBUG", ... } // OK
```

**Comportamento Esperado**:
```
LogLoader.load_all()
    ├─ Lê linha 1: Parse OK
    ├─ Lê linha 2: JSONDecodeError
    │   └─ LogEntry.from_json_line() → retorna None
    │   └─ Linha ignorada silenciosamente
    └─ Lê linha 3: Parse OK

Resultado: 2 LogEntry criadas (linha 2 descartada)
Sem crash
```

**O que o Dev vê**:
- Tabela com 2 entradas (linha 2 ausente)
- Nada de estranho, comportamento normal

**Solução**: Melhorar logging de erros de parse (adicionar warning em core.config.LogUtils)

---

### Cenário E2: Arquivo de Log é Deletado Enquanto Logcat Está Aberto

**Situação**: 
```
1. Logcat aberto, monitorando arquivo A
2. User deleta arquivo A do SO (ex: via Windows Explorer)
3. LogFileWatcher tenta verificar tamanho
```

**Comportamento Esperado**:
```
LogFileWatcher._check_file()
    ├─ os.path.getsize(path) → FileNotFoundError
    ├─ Try-except captura
    ├─ Log warning
    └─ _stop() é chamado

LogcatDialog._on_file_changed() não é chamado
Tabela continua com dados antigos (OK)
```

**O que o Dev vê**:
- Dados velhos na tabela (não há mais atualizações)
- Se tentar recarregar: "Session not found"

**Solução**: Adicionar notificação ao status bar: "File was deleted"

---

### Cenário E3: Permissões de Leitura Insuficientes

**Situação**: 
```
raiz/log/ tem permissão 000 (nenhuma)
User tenta abrir Logcat
```

**Comportamento Esperado**:
```
LogSessionManager.refresh()
    ├─ os.listdir(log_dir) → PermissionError
    ├─ except PermissionError
    └─ Mensagem de erro ao usuário

LogcatDialog._build_ui()
    └─ Mostra: "Cannot access log directory"
```

**O que o Dev vê**:
- Dialog vazio ou com mensagem de erro clara
- Sem crash

**Solução**: Melhorar mensagem de erro (já implementado)

---

### Cenário E4: Carregamento de Sessão com Arquivo Gigante

**Situação**: Usuário tenta abrir uma sessão com arquivo de 500MB (100k+ linhas JSONL).

**Comportamento Esperado**:
```
1. LogLoader.load_all() começa
2. Itera sobre 100k linhas
3. ~2-3 segundos para parse
4. Retorna List[LogEntry] com 100k objetos
5. table_model.set_entries(entries)
6. QTableView renderiza APENAS linhas visíveis (~20)
7. Performance: smooth!

User vê: "Loading..." → tabela preenchida
Sem congelamento perceptível após primeiros 2-3s
```

**O que o Dev vê**:
- UI pode ficar "congelada" por 2-3s (thread-sensitive)
- Depois funciona normalmente
- Scrolling é smooth

**Solução Possível**: Implementar load_all() em thread com progress bar

---

### Cenário E5: Filtro com Regex Inválido

**Situação**: User digita regex inválido em "Search": `[a-z`

**Comportamento Esperado**:
```
_on_filter_changed()
    ├─ LogFilterEngine.set_text_filter("[a-z")
    ├─ _apply_filters()
    │   ├─ filter_engine.apply()
    │   │   ├─ for entry in entries:
    │   │   │   ├─ re.search("[a-z", entry.msg)
    │   │   │   └─ re.error: unterminated character set
    │   │   └─ except re.error → return []
    │   └─ Tabela vazia (sem crash)
```

**O que o Dev vê**:
- Tabela fica vazia
- Status: "Showing 0/1000 entries"
- Sem erro visível

**Solução**: Adicionar validação de regex com feedback visual

---

## CENÁRIOS DE PERFORMANCE

### Cenário P1: Carregamento Incremental Otimizado

**Situação**: Arquivo teve 50 novas linhas adicionadas (normal durante execução).

**Fluxo Esperado**:
```
LogFileWatcher detects size change
    └─> on_change() callback

LogcatDialog._on_file_changed()
    ├─ LogLoader.load_incremental()
    │   ├─ Seek to offset antigo: ~10MB
    │   ├─ Read apenas últimas 5KB (~50 linhas)
    │   ├─ Parse: ~20ms
    │   └─ Retorna 50 LogEntry
    ├─ all_entries.extend(50)
    ├─ _apply_filters()
    │   └─ Apply to 50 new entries only (~10ms)
    ├─ table_model.append_entries(50)
    │   └─ insertRows (efficient)
    └─ QTableView.updateGeometry()

Total: ~50ms
```

**Observação**: Se arquivo é grande (100MB), seek é O(1) via file offset, não reread.

---

### Cenário P2: Filtro em Arquivo Grande

**Situação**: Arquivo tem 100k linhas, user filtra por "ERROR".

**Fluxo Esperado**:
```
_apply_filters()
    ├─ filter_engine.apply(100k entries)
    │   ├─ for entry in entries:
    │   │   ├─ if entry.level == "ERROR"
    │   │   └─ O(1) check
    │   └─ Total: ~100k × O(1) = ~100-200ms
    ├─ table_model.set_entries(filtered)
    │   └─ layoutChanged (O(1))
    └─ QTableView re-render visible rows (~20ms)

Total: ~150-250ms
```

**Observação**: Model/View garante que apenas ~20 linhas visíveis são renderizadas. Scroll é smooth.

---

### Cenário P3: Múltiplos Filtros Combinados

**Situação**: Level=ERROR + Tool=vector_field + Text="coordinate"

**Fluxo Esperado**:
```
filter_engine.apply(100k)
    ├─ Pass 1: Level filter → 500 entradas
    ├─ Pass 2: Tool filter → 200 entradas
    ├─ Pass 3: Text filter → 5 entradas
    └─ Result: 5 entradas

Performance:
- Single pass: 100k checks × 3 ops = ~300k ops
- Modern CPU: ~1ms
- Total com rendering: ~50ms
```

---

### Cenário P4: Sorting de Grande Volume

**Situação**: User clica header "Timestamp" para ordenar 100k entradas.

**Fluxo Esperado**:
```
table_view.sortByColumn(0, AscendingOrder)
    └─ proxy_model.sort(0, AscendingOrder)
        ├─ QSortFilterProxyModel internamente
        ├─ lessThan() chamado ~n × log(n) vezes
        │   (quicksort)
        ├─ Timestamp comparison (string): O(1)
        ├─ Total: ~100k × log(100k) = ~1.6M ops
        ├─ Modern CPU: ~5-10ms
        └─ layoutChanged emitted

Total: ~100-150ms (primeira vez)
Segue vez: ~10ms (cache)
```

---

### Cenário P5: Cores Cacheadas

**Situação**: 1000 entradas com 50 classes diferentes.

**Fluxo Esperado**:
```
LogTableModel.data(index, ForegroundRole)
    ├─ First class "MyClass"
    │   ├─ ClassColorProvider.get_color("MyClass")
    │   │   ├─ Check cache: MISS
    │   │   ├─ SHA256("MyClass") → compute color
    │   │   ├─ Cache["MyClass"] = "#RRGGBB"
    │   │   └─ Return "#RRGGBB"
    │   └─ Total: ~1ms
    ├─ Next 999 entries
    │   ├─ For each class:
    │   │   ├─ ClassColorProvider.get_color(class)
    │   │   │   ├─ Check cache: HIT
    │   │   │   └─ Return cached "#RRGGBB" (O(1))
    │   │   └─ Total: ~0.001ms × 999 = ~1ms
    │   └─ Total: ~1ms
    └─ Total render: ~2ms
```

---

## CENÁRIOS DE MANUTENÇÃO

### Cenário M1: Adicionar Novo Filtro (Level Avançado)

**Requisito**: Filtrar por múltiplos níveis ao mesmo tempo.

**Implementação**:
```python
# core/filter/log_filter_engine.py
def set_level_filter(self, levels: Set[str]) -> None:
    self.level_filter = levels

def _matches_level(self, entry) -> bool:
    if not self.level_filter:
        return True
    return entry.level in self.level_filter

# ui/logcat_dialog.py
def _on_filter_level_clicked(self):
    # Mostrar popup com checkboxes
    selected = self.filter_engine.level_filter
    # User marca/desmarca
    self.filter_engine.set_level_filter(selected)
    self._apply_filters()
```

**Teste**:
```
1. Aplicar filter Level=[ERROR, CRITICAL]
2. Verificar que apenas ERROR/CRITICAL aparecem
3. Adicionar nova entrada de ERROR
4. Verificar que aparece automaticamente
5. Mude para Level=[INFO]
6. Verificar que ERROR desaparece
```

---

### Cenário M2: Bugfix - Seleção Desaparece ao Filtrar

**Problema Relatado**: Quando user filtra, seleção anterior é perdida.

**Root Cause**: `set_entries()` chamava `beginResetModel()` que limpa seleção.

**Solução**: Usar `layoutChanged.emit()` em vez de `beginResetModel()`.

```python
# Antes:
def set_entries(self, entries):
    self.beginResetModel()
    self._entries = entries
    self.endResetModel()

# Depois:
def set_entries(self, entries):
    self._entries = entries
    self.layoutChanged.emit()  # Preserva seleção!
```

**Teste**:
```
1. Selecionar linha 50
2. Aplicar filtro
3. Verificar que linha 50 continua selecionada (se ainda visível)
4. Se não visível, seleção é mantida para quando reapareça
```

---

### Cenário M3: Feature Request - Export para CSV

**Requisito**: User quer exportar logs para arquivo CSV.

**Implementação**:
```python
# ui/logcat_dialog.py
def _on_export_csv(self):
    # Get filtered entries (same as export_filter)
    filtered_entries = [...]
    
    # Create CSV file
    import csv
    filename = QFileDialog.getSaveFileName(...)[0]
    if not filename:
        return
    
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Level", "Tool", "Class", "Message"])
        for entry in filtered_entries:
            writer.writerow([
                entry.ts,
                entry.level,
                entry.tool,
                entry.class_name,
                entry.msg
            ])
    
    QMessageBox.information(self, "Success", f"Exported {len(filtered_entries)} entries")
```

**Teste**:
```
1. Filtrar para 10 entradas
2. Clica "Export CSV"
3. Salva arquivo
4. Verifica arquivo tem 10 linhas + header
5. Abre em Excel → OK
```

---

### Cenário M4: Upgrade - Colorização Mais Sofisticada

**Requisito**: Cores mais bonitas e legíveis.

**Implementação**:
```python
# core/color/class_color_provider.py
class ClassColorProvider:
    def get_color(self, class_name: str) -> str:
        # Antes: SHA256 simples
        # Depois: HSL com garantia de contraste
        
        hash_val = hashlib.sha256(class_name.encode()).digest()
        h = (hash_val[0] / 256) * 360  # 0-360
        s = 70 + (hash_val[1] / 256) * 20  # 70-90%
        l = 40 + (hash_val[2] / 256) * 20  # 40-60%
        
        # HSL → RGB
        rgb = colorsys.hls_to_rgb(h/360, l/100, s/100)
        r, g, b = [int(x * 255) for x in rgb]
        
        return f"#{r:02x}{g:02x}{b:02x}"
```

**Teste**:
```
1. Compare cores antigas vs novas
2. Verificar que cores novas têm melhor contraste
3. Verificar que cores são determinísticas (mesma classe = mesma cor)
4. Performance não mudou significativamente
```

---

### Cenário M5: Crash - Deadlock em Thread de Monitoramento

**Problema Relatado**: Logcat trava ocasionalmente.

**Root Cause**: Lock em LogFileWatcher não foi liberado.

**Debug**:
```python
# Adicionar logging de thread:
import threading

class LogFileWatcher:
    def _run(self):
        while self._running:
            try:
                with self._lock:
                    print(f"[FileWatcher-{threading.current_thread().name}] Checking...")
                    # Check file
            except Exception as e:
                logger.error(f"FileWatcher error: {e}")
```

**Solução**: Adicionar timeout ao lock.

```python
# Antes:
with self._lock:
    # Pode travar se não liberado

# Depois:
if self._lock.acquire(timeout=1.0):
    try:
        # Check file
    finally:
        self._lock.release()
else:
    logger.warning("FileWatcher lock timeout")
```

---

## CONCLUSÃO

Estes cenários cobrem:
- ✓ Uso normal
- ✓ Casos extremos
- ✓ Erros comuns
- ✓ Performance em larga escala
- ✓ Maintenance tasks
- ✓ Bug fixes
- ✓ Feature requests

A ferramenta é **robusta** e **extensível** para toda a manutenção futura.
