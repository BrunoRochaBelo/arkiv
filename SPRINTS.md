# Plano de Sprints

Este documento detalha as tarefas recomendadas para finalizar o backend do Arkiv e colocá-lo em produção. As sprints estão baseadas nas funcionalidades descritas no `README.md` e em boas práticas de desenvolvimento.

## Sprint 1 – Fundamentos do Backend
- **Modelos e migrações**
  - Finalizar todos os modelos conforme seção "Modelo de Dados Detalhado" do README, incluindo índices e constraints【F:README.md†L392-L557】.
  - Configurar Flask-Migrate e criar migrations iniciais.
- **Autenticação e autorização**
  - Implementar rotas de login, logout e registro usando Flask-WTF e Flask-Login.
  - Utilizar Argon2 para hash de senha e preparar suporte a MFA【F:README.md†L546-L560】.
  - Criar decorator `role_required()` para papéis OWNER/MANAGER/etc.
- **Gestão de organizações**
  - Rotas para criar e editar organizações e membros.
  - Integração inicial com planos (`Plan`) e quotas.
- **Configuração de ambiente**
  - Variáveis listadas no README (SECRET_KEY, DATABASE_URL, etc.) em `.env`.
  - Permitir uso de SQLite em desenvolvimento, mantendo PostgreSQL no deploy.
  - Ajustar `create_initial_data.py` para gerar senha hash e org/usuário demo.

## Sprint 2 – Bibliotecas, Pastas e Assets
- **Módulo Library**
  - CRUD completo de bibliotecas com formulários e templates.
- **Módulo Folder**
  - CRUD de pastas aninhadas respeitando `parent_id` e constraint `uq_folder_name`【F:README.md†L432-L451】.
- **Módulo Asset**
  - Upload com rota `/folders/<id>/assets` e geração de `filename_storage`.
  - Integração com Celery para thumbnail e OCR básico (Tesseract)【F:README.md†L780-L804】.
  - Controle de quota de armazenamento por plano【F:README.md†L557-L558】.

## Sprint 3 – Tags, Busca e API Mobile
- **Módulo Tag**
  - CRUD de tags e associação em `asset_tag`.
- **Módulo Search**
  - Implementar busca com filtros e suporte a full-text do PostgreSQL.
- **API Mobile**
  - Criar todos os endpoints descritos no README sob `/api/v1`【F:README.md†L708-L779】.
  - Autenticação JWT e CORS apenas para rota API.
  - Manter documentação em `docs/api_spec.yaml` sincronizada.

## Sprint 4 – Auditoria, Relatórios e Admin
- **Logs e auditoria**
  - Registrar operações no modelo `AuditLog` conforme seção "Logs, Auditoria & Monitoramento"【F:README.md†L584-L623】.
  - Configurar logs em JSON utilizando `python-json-logger`.
- **Relatórios**
  - Rotas para gerar relatórios em CSV/Excel e agendamento via Celery.
- **Painel administrativo**
  - Funcionalidades para gerenciamento de tenants e planos SaaS.
- **Segurança avançada**
  - Aplicar rate limit com Flask-Limiter em rotas sensíveis【F:README.md†L562-L575】.
  - Adicionar cabeçalhos de segurança e proteção CSRF.

## Sprint 5 – Preparação para Produção
- **Testes automatizados**
  - Cobertura mínima de 80 % nos principais módulos.
  - Testes de API e rotas web usando Flask-Testing/Pytest.
- **Monitoramento e observabilidade**
  - Expor métricas para Prometheus e integrar Sentry para rastreio de erros【F:README.md†L620-L636】.
- **Revisão de deploy**
  - Scripts de seed e migração para PostgreSQL.
  - Documentação final de instalação e uso.
- **Revisão de segurança e performance**
  - Checagem de RLS, políticas de senha e auditoria.
  - Otimizar queries e índices em produção.

