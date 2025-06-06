# UI Guidelines

Este documento descreve a padronização visual do Arkiv, incluindo componentes
reutilizáveis, tokens de estilo e dicas de acessibilidade.

## Componentes

### Cards
- Utilize `.card` com `.shadow-sm` para listar coleções e assets.
- Exemplo de uso:
  ```html
  <div class="card">
    <div class="card-body">Conteúdo</div>
  </div>
  ```

### Modais
- Modais seguem a estrutura padrão Bootstrap.
- O modal de upload é acionado pelo botão **Enviar Arquivos**.

### Formulários
- Campos base em `.form-control` e labels visíveis.
- Validação inline com mensagens abaixo do campo.

## Paleta de Cores

| Token               | Claro           | Escuro          |
| ------------------- | --------------- | --------------- |
| `--color-bg`        | `#ffffff`       | `#121212`       |
| `--color-primary`   | `#0d6efd`       | `#4dabf7`       |
| `--color-secondary` | `#6c757d`       | `#9ca0a4`       |
| `--color-accent`    | `#20c997`       | `#12b886`       |

## Tipografia

- Fonte base **Inter**, fallback sans-serif.
- Tamanhos recomendados:
  - Corpo: `1rem`
  - Cabeçalho h1: `2rem`
  - Cabeçalho h2: `1.5rem`

## Espaçamentos

Tokens de espaçamento em `rem`:

| Token         | Valor |
| ------------- | ----- |
| `--space-xs`  | 0.25  |
| `--space-sm`  | 0.5   |
| `--space-md`  | 1     |
| `--space-lg`  | 1.5   |

## Modo Escuro

- Detecta `prefers-color-scheme`, mas pode ser alternado manualmente
  pelo ícone no cabeçalho.
- Para desativar permanentemente, remova `theme` do `localStorage`.

## Acessibilidade (A11y)

- Utilize `aria-label` em botões e links de ação.
- Mantenha contraste de cores conforme WCAG AA.
- Todos os componentes têm foco visível ao usar `Tab`.

## Workflow de CSS

Os estilos vivem em `static/css/`. Para gerar uma versão otimizada:

```bash
npm run css:purge   # remove classes não usadas
npm run css:minify  # gera arkiv.min.css
```

## Capturas de Tela

As capturas de tela de antes e depois estão em
`docs/screenshots/`. Incluem:

- Lista de bibliotecas
- Galeria de assets
- Modal de upload
- Formulário de pasta
