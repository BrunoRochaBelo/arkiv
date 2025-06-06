# Arkiv – Arquivo Digital Inteligente

**Centralize, catalogue e encontre suas imagens com segurança empresarial e usabilidade moderna.**

---

## 📑 Sumário

1. [Visão geral](#visão-geral)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Suporte a Multi-inquilinos](#suporte-a-multi-inquilinos)
4. [Arquitetura de Módulos e Arquivos Principais](#arquitetura-de-módulos-e-arquivos-principais)
5. [Modelo de Dados Detalhado](#modelo-de-dados-detalhado)
6. [Segurança & Conformidade](#segurança--conformidade)
7. [Logs, Auditoria & Monitoramento](#logs-auditoria--monitoramento)
8. [Usabilidade & Acessibilidade](#usabilidade--acessibilidade)
9. [Relatórios](#relatórios)
10. [Integração com App Mobile (MAUI)](#integração-com-app-mobile-maui)
11. [Como Rodar](#como-rodar)
12. [Roadmap](#roadmap)
13. [Contribua](#contribua)

> **Observação**: Por enquanto não usamos Docker nem configuramos testes automatizados no back-end. Se em algum momento for muito indicado, podemos reavaliar a inclusão, mas focamos em manter tudo simples e direto.

---

## 🚀 Visão geral

| Aspecto           | Stack                                       | Justificativa                                                                               |
| ----------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **Backend**       | Flask 3 + Blueprints modulares              | Monolito coeso com separação lógica clara, fácil de manter e escalar por módulos.           |
| **Banco**         | PostgreSQL 16                               | JSONB, full-text nativo, pg\_trgm para busca avançada e particionamento em tabelas grandes. |
| **Armazenamento** | Local (dev) / S3-compatible (prod)          | Flexibilidade para mudar backend sem refatorar; CDN opcional (CloudFront, Cloudflare R2).   |
| **Assíncrono**    | Celery 6 + Redis                            | Geração de thumbnails, OCR, IA de tags e relatórios agendados sem travar a request.         |
| **Front**         | Bootstrap 5.3, HTMX, Alpine.js, Dropzone.js | Experiência reativa e leve no web, sem necessidade de SPA completo.                         |
| **Observability** | Prometheus + Grafana, Sentry                | Métricas e rastreamento de erros em produção, mesmo sem Docker.                             |

---

## Estrutura do Projeto

```plaintext
arkiv/                              # Raiz do repositório
├── .env.example                    # Variáveis de ambiente de exemplo
├── .gitignore                      # Arquivos e pastas ignorados pelo Git
├── requirements.txt                # Dependências Python (congeladas)
├── run.py                          # Ponto de entrada para rodar localmente
├── manage.py                       # CLI personalizada (migrations, shell, etc.)
├── README.md                       # Documentação principal (este arquivo)
├── migrations/                     # Scripts de migração do banco (Flask-Migrate/Alembic)
│   └── versions/                   # Arquivos de versão gerados automaticamente
│
├── arkiv_app/                      # Código-fonte principal da aplicação
│   ├── __init__.py                 # Criação do app, registro de blueprints, inicializações
│   ├── config.py                   # Classes de configuração (Dev, Prod)
│   ├── extensions.py               # Instanciação de db, migrate, login_manager, limiter, etc.
│   ├── utils/                      # Funções utilitárias (email, seed de dados, etc.)
│   │   ├── email_sender.py         # Envio de e-mails (boas-vindas, recuperação, relatórios)
│   │   └── create_initial_data.py  # Script para criar org/demo + usuário OWNER
│   │
│   ├── auth/                       # Módulo de autenticação e autorização
│   │   ├── __init__.py
│   │   ├── routes.py               # /login, /logout, /profile, /reset-password, /mfa
│   │   ├── forms.py                # Flask-WTF para login, registro, recuperação de senha
│   │   └── templates/auth/         # Templates Jinja2: login.html, register.html, etc.
│   │
│   ├── organization/               # Gestão de organizações, planos e membros
│   │   ├── __init__.py
│   │   ├── routes.py               # /org/create, /org/settings, /org/members, /org/billing
│   │   ├── forms.py                # Flask-WTF para criar/editar org, convidar membros
│   │   ├── services.py             # Lógica de trial, integração Stripe, cota de armazenamento
│   │   └── templates/organization/ # Templates Jinja2: create_org.html, members.html, billing.html
│   │
│   ├── library/                    # CRUD de bibliotecas (coleções top-level)
│   │   ├── __init__.py
│   │   ├── routes.py               # /libraries, /libraries/<id>/edit, /libraries/<id>/delete
│   │   ├── forms.py                # Flask-WTF para criar/editar biblioteca
│   │   └── templates/library/      # Templates: libraries.html, edit_library.html
│   │
│   ├── folder/                     # CRUD de pastas aninhadas dentro de bibliotecas
│   │   ├── __init__.py
│   │   ├── routes.py               # /folders/<id>/view, /folders/<id>/create, etc.
│   │   ├── forms.py                # Flask-WTF para criar/editar pasta
│   │   └── templates/folder/       # Templates: folder_view.html, folder_form.html
│   │
│   ├── asset/                      # Upload, gerenciamento, versão e download de assets
│   │   ├── __init__.py
│   │   ├── routes.py               # /assets/<id>, /folders/<f>/upload, /assets/<id>/download
│   │   ├── forms.py                # Flask-WTF para formulários de upload (se necessário)
│   │   ├── models.py               # Extensões específicas (Ex.: AssetVersion, se houver)
│   │   └── templates/asset/        # Templates: asset_details.html, upload_modal.html
│   │
│   ├── tag/                        # CRUD e gerenciamento de tags por organização
│   │   ├── __init__.py
│   │   ├── routes.py               # /tags, /tags/<id>/edit, /assets/<id>/tags
│   │   ├── forms.py                # Flask-WTF para nova tag, edição
│   │   └── templates/tag/          # Templates: tags.html, tag_form.html
│   │
│   ├── search/                     # Busca global com filtros (facets)
│   │   ├── __init__.py
│   │   ├── routes.py               # /search, /api/search/autocomplete
│   │   ├── forms.py                # (opcional) WTForms para filtros avançados
│   │   └── templates/search/       # Templates: search_results.html
│   │
│   ├── dashboard/                  # Indicadores gerais da organização
│   │   ├── __init__.py
│   │   ├── routes.py               # /dashboard
│   │   └── templates/dashboard/    # Templates: dashboard.html
│   │
│   ├── reports/                    # Relatórios com filtros e exportações
│   │   ├── __init__.py
│   │   ├── routes.py               # /reports/assets, /reports/scheduled
│   │   ├── forms.py                # WTForms para filtros de relatório
│   │   └── templates/reports/      # Templates: report_form.html, report_preview.html
│   │
│   ├── admin/                      # Super-admin do SaaS (operação das tenants)
│   │   ├── __init__.py
│   │   ├── routes.py               # /admin/tenants, /admin/plans, /admin/stats
│   │   └── templates/admin/        # Templates: tenants.html, plans.html
│   │
│   ├── api/                        # **NOVO** – Endpoints RESTful para App Mobile
│   │   ├── __init__.py
│   │   ├── routes.py               # /api/v1/auth, /api/v1/libraries, /api/v1/assets, etc.
│   │   └── schemas.py              # Marshmallow schemas para serialização/validação
│   │
│   ├── templates/                  # Templates globais e layouts
│   │   ├── base.html               # Layout principal (navbar, footer, scripts)
│   │   ├── error/                  # Páginas de erro (404, 500, etc.)
│   │   │   ├── 404.html
│   │   │   └── 500.html
│   │   └── components/             # Partials reaproveitáveis (navbar, footer, modals)
│   │       ├── navbar.html
│   │       ├── footer.html
│   │       └── modals.html
│   │
│   ├── static/                     # Recursos estáticos (CSS, JS, imagens)
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   ├── app.js              # Inicialização de scripts (HTMX, Alpine.js)
│   │   │   └── helpers.js
│   │   └── imgs/
│   │       └── logo.png
│   │
│   └── __pycache__/                # Cache do Python
│
└── docs/                           # Documentação adicional (diagramas, guias)
    ├── architecture.drawio
    ├── er_diagram.png
    └── api_spec.yaml               # Especificação OpenAPI/Swagger para o módulo API
```

> **Observação**: O diretório `api/` é crucial para atender ao App Mobile em MAUI. Nele, criamos rotas RESTful separadas das páginas web, garantindo que o mobile possa consumir JSON de forma simples.

---

## Suporte a Multi-inquilinos

1. **Isolamento Lógico**

   * Todas as tabelas possuem coluna `organization_id` ou referenciam indiretamente via `library_id`, `asset_id` etc.
   * Cada consulta usa `current_org_id` obtido no login do usuário.
   * **Row-Level Security** (RLS) pode ser habilitado no PostgreSQL para reforçar que nenhuma consulta acesse dados de outra organização.

2. **Armazenamento**

   * Objetos em S3/MinIO organizados por prefixo:

     ```
     <bucket>/
       org-slug-123/
         library-7/
           folder-42/
             arquivo1.jpg
     ```
   * Facilita gerenciar cota e limpar dados de uma organização sem afetar as demais.

3. **Domínios Customizados** (opcional)

   * Cada organização pode apontar um CNAME para `org.arkiv.app`.
   * Isso passa confiança para clientes corporativos e órgãos públicos.

4. **Gestão de Planos e Quotas**

   * **Planos** definem `storage_quota_gb`, preço e recursos (IA tagging, OCR, SSO) no JSON `features`.
   * Antes de permitir upload, o `storage_service` soma o tamanho de todos os assets ativos da organização e checa contra a cota.

5. **RBAC (Controle de Acesso por Papéis)**

   * Tabela `Membership` guarda papéis:

     * **OWNER**: controle total, gerencia cobrança, quotas, usuários.
     * **MANAGER**: cria/edita bibliotecas, gerencia usuários e configurações.
     * **EDITOR**: faz upload, edita tags, move assets.
     * **CONTRIBUTOR**: apenas upload em pastas designadas.
     * **VIEWER**: somente leitura (útil para compliance/auditoria).
   * Decorators `@role_required("EDITOR")` em rotas sensíveis garantem que só usuários com papel adequado acessem.

---

## Arquitetura de Módulos e Arquivos Principais

### 1. Arquivos e Configurações na Raiz

* **`.env.example`**:

  ```dotenv
  FLASK_ENV=development
  SECRET_KEY=troque_aqui
  DATABASE_URL=postgresql+psycopg2://arkiv_user:senha@localhost:5432/arkiv
  REDIS_URL=redis://localhost:6379/0
  STORAGE_TYPE=local      # ou "s3"
  S3_BUCKET_NAME=arkiv-bucket
  S3_REGION=us-east-1
  S3_ACCESS_KEY_ID=AKIA...
  S3_SECRET_ACCESS_KEY=...
  STRIPE_SECRET_KEY=sk_test_...
  STRIPE_PUBLIC_KEY=pk_test_...
  CORS_ORIGINS=http://localhost:5000,https://meuappmobile.com  # Origens autorizadas para API
  ```

  > O desenvolvedor copia para `.env` e preenche com as chaves reais.

* **`run.py`**:

  ```python
  from arkiv_app import create_app

  app = create_app()

  if __name__ == "__main__":
      # Habilitar CORS para rotas da API
      from flask_cors import CORS
      CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"].split(",")}})
      app.run(host="0.0.0.0", port=5000)
  ```

* **`manage.py`**:
  CLI que expõe comandos como `flask db upgrade`, `flask shell` e `python manage.py create-user`.

* **`requirements.txt`** (resumido):

  ```text
  Flask==3.0.2
  Flask-SQLAlchemy==3.0.2
  Flask-Migrate==4.0.4
  Flask-Login==0.6.2
  Flask-WTF==1.1.1
  psycopg2-binary==2.9.7
  boto3==1.26.24
  celery==6.0.0
  redis==4.5.1
  pillow==9.4.0
  exifread==3.0.0
  python-dotenv==1.0.0
  Flask-Limiter==2.9.1
  Flask-Mail==0.9.1
  pdfkit==1.0.0
  openpyxl==3.1.2
  pandas==2.0.1
  sentry-sdk==1.11.0
  Flask-Cors==4.0.0
  Flask-RESTful==0.3.9
  marshmallow==3.19.0
  marshmallow-sqlalchemy==0.29.0
  ```

* **`.gitignore`**:

  ```text
  __pycache__/
  *.pyc
  .env
  venv/
  .vscode/
  ```

---

### 2. `arkiv_app/__init__.py` e Configurações

* **`arkiv_app/__init__.py`**:

  ```python
  import os
  from flask import Flask
  from .extensions import db, migrate, login_manager, limiter
  from .config import config_by_name

  def create_app(config_name=None):
      app = Flask(__name__, instance_relative_config=False)
      config_name = config_name or os.getenv("FLASK_ENV", "development")
      app.config.from_object(config_by_name[config_name])

      # Inicializa extensões
      db.init_app(app)
      migrate.init_app(app, db)
      login_manager.init_app(app)
      limiter.init_app(app)

      # Registro de Blueprints
      from .auth.routes import auth_bp
      from .organization.routes import org_bp
      from .library.routes import library_bp
      from .folder.routes import folder_bp
      from .asset.routes import asset_bp
      from .tag.routes import tag_bp
      from .search.routes import search_bp
      from .dashboard.routes import dashboard_bp
      from .reports.routes import reports_bp
      from .admin.routes import admin_bp
      from .api.routes import api_bp

      app.register_blueprint(auth_bp, url_prefix="/auth")
      app.register_blueprint(org_bp, url_prefix="/org")
      app.register_blueprint(library_bp, url_prefix="/libraries")
      app.register_blueprint(folder_bp, url_prefix="/folders")
      app.register_blueprint(asset_bp, url_prefix="/assets")
      app.register_blueprint(tag_bp, url_prefix="/tags")
      app.register_blueprint(search_bp, url_prefix="/search")
      app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
      app.register_blueprint(reports_bp, url_prefix="/reports")
      app.register_blueprint(admin_bp, url_prefix="/admin")
      app.register_blueprint(api_bp, url_prefix="/api/v1")

      # Erros customizados (404, 500)
      from .errors import register_error_handlers
      register_error_handlers(app)

      return app
  ```

* **`arkiv_app/config.py`**:

  ```python
  import os

  class BaseConfig:
      SECRET_KEY = os.getenv("SECRET_KEY", "troque_me")
      SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
      SQLALCHEMY_TRACK_MODIFICATIONS = False
      REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
      STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")
      S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
      S3_REGION = os.getenv("S3_REGION")
      S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
      S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
      STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
      STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
      CELERY_BROKER_URL = REDIS_URL
      CELERY_RESULT_BACKEND = REDIS_URL
      RATELIMIT_STORAGE_URL = REDIS_URL
      LOG_LEVEL = "INFO"
      CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")  # Para API

  class DevelopmentConfig(BaseConfig):
      ENV = "development"
      DEBUG = True

  class ProductionConfig(BaseConfig):
      ENV = "production"
      DEBUG = False

  config_by_name = {
      "development": DevelopmentConfig,
      "production": ProductionConfig,
  }
  ```

* **`arkiv_app/extensions.py`**:

  ```python
  from flask_sqlalchemy import SQLAlchemy
  from flask_migrate import Migrate
  from flask_login import LoginManager
  from flask_limiter import Limiter
  from flask_limiter.util import get_remote_address
  import logging

  db = SQLAlchemy()
  migrate = Migrate()
  login_manager = LoginManager()
  login_manager.login_view = "auth.login"
  limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

  # Configurar logging (pode integrar com Sentry ou Loki)
  logger = logging.getLogger(__name__)
  ```

---

## Modelo de Dados Detalhado

```python
from datetime import datetime
from .extensions import db

class Organization(db.Model):
    __tablename__ = "organization"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    members = db.relationship("Membership", back_populates="organization")
    libraries = db.relationship("Library", back_populates="organization")


class Plan(db.Model):
    __tablename__ = "plan"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    storage_quota_gb = db.Column(db.Integer, nullable=False)
    price_monthly = db.Column(db.Numeric(10, 2), nullable=False)
    features = db.Column(db.JSONB)  # Ex.: {"ocr": True, "ia_tagging": False}


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    mfa_enabled = db.Column(db.Boolean, default=False)

    memberships = db.relationship("Membership", back_populates="user")
    uploads = db.relationship("Asset", back_populates="uploader")


class Membership(db.Model):
    __tablename__ = "membership"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organization.id"), primary_key=True)
    role = db.Column(db.String(15), nullable=False)  # OWNER, MANAGER, EDITOR, …

    user = db.relationship("User", back_populates="memberships")
    organization = db.relationship("Organization", back_populates="members")


class Library(db.Model):
    __tablename__ = "library"
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organization = db.relationship("Organization", back_populates="libraries")
    folders = db.relationship("Folder", back_populates="library")


class Folder(db.Model):
    __tablename__ = "folder"
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey("library.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("folder.id"), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    library = db.relationship("Library", back_populates="folders")
    parent = db.relationship("Folder", remote_side=[id], backref="children")
    assets = db.relationship("Asset", back_populates="folder")

    __table_args__ = (
        db.UniqueConstraint("library_id", "parent_id", "name", name="uq_folder_name"),
    )


class Asset(db.Model):
    __tablename__ = "asset"
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey("library.id"), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey("folder.id"), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    filename_orig = db.Column(db.String(255), nullable=False)
    filename_storage = db.Column(db.String(255), nullable=False, unique=True)
    mime = db.Column(db.String(50), nullable=False)
    size = db.Column(db.BigInteger, nullable=False)  # bytes
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    checksum_sha256 = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete

    folder = db.relationship("Folder", back_populates="assets")
    uploader = db.relationship("User", back_populates="uploads")
    tags = db.relationship("Tag", secondary="asset_tag", back_populates="assets")


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    color_hex = db.Column(db.String(7), default="#CCCCCC")  # Ex.: #FF5733
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organization = db.relationship("Organization")
    assets = db.relationship("Asset", secondary="asset_tag", back_populates="tags")

    __table_args__ = (
        db.UniqueConstraint("org_id", "name", name="uq_tag_per_org"),
    )


class AssetTag(db.Model):
    __tablename__ = "asset_tag"
    asset_id = db.Column(db.Integer, db.ForeignKey("asset.id"), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), primary_key=True)


class AuditLog(db.Model):
    __tablename__ = "audit_log"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    action = db.Column(db.String(50), nullable=False)       # ex.: "CREATE_ASSET", "DELETE_TAG"
    entity = db.Column(db.String(50), nullable=False)       # ex.: "Asset", "Tag"
    entity_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))                   # IPv4 ou IPv6
    payload = db.Column(db.JSONB)                            # Dados extras (antes/depois)

    __table_args__ = (
        db.Index("idx_audit_org_time", "org_id", "timestamp"),
    )
```

> **Observações importantes**:
>
> * **Índices**:
>
>   * `GIN` full-text em `Asset.filename_orig` e `Tag.name` (para busca).
>   * `pg_trgm` para pesquisa por similaridade em nomes de arquivos e tags.
>   * Particionamento de `AuditLog` por mês (é possível usar `pg_partman`).
> * **Verificação de Quota**: no momento do upload, o `storage_service` checa a soma do `size` de todos os assets ativos na organização e compara com `storage_quota_gb` do plano.

---

## Segurança & Conformidade

1. **Autenticação**

   * Hash de senha com **Argon2** (via `argon2-cffi`) para máxima segurança.
   * 2FA/TOTP opcional (via `pyotp`), caso o cliente queira reforçar login.
   * Políticas de senha: min. 8 caracteres, combinação de letras, números e símbolos.

2. **Autorização**

   * Decorator customizado `@role_required("EDITOR")` verifica `current_user.membership.role`.
   * **Row-Level Security** (RLS) no PostgreSQL (opcional) para garantir que todas as queries estejam limitadas ao `current_org_id`.

3. **Criptografia em Trânsito e em Repouso**

   * HTTPS obrigatório (TLS 1.3) configurado no proxy reverso (Nginx/Traefik).
   * No S3/MinIO: uso de SSE-S3 ou SSE-KMS.
   * Variáveis sensíveis (como `SECRET_KEY` e credenciais AWS) obrigatoriamente em variáveis de ambiente.

4. **Proteção Contra CSRF/XSS/Clickjacking**

   * Flask-WTF gera tokens CSRF para todas as rotas de formulário.
   * Cabeçalhos de segurança adicionados por padrão:

     ```plaintext
     Content-Security-Policy: default-src 'self'; img-src 'self' https:;
     X-Frame-Options: DENY
     X-Content-Type-Options: nosniff
     Referrer-Policy: no-referrer-when-downgrade
     ```
   * Sanitização de entradas de texto livre (descrições, nomes) usando `bleach` ou validação manual.

5. **Proteção de API & Rate Limiting**

   * Endpoints do módulo `api/` usam tokens JWT ou OAuth2 Bearer (dependendo da implementação) – facilita uso pelo app mobile.
   * Rate limiter (`Flask-Limiter` + Redis) aplicado em rotas críticas: login, upload, criação de usuários.

6. **LGPD / GDPR**

   * Consentimento explícito no registro de usuário.
   * “Direito ao esquecimento”: endpoint que exclui permanentemente dados de um usuário ou organização, respeitando período de retenção (soft-delete + purga).
   * Logs de auditoria (AuditLog) retêm rastros, porém dados pessoais removidos conforme solicitação.

---

## Logs, Auditoria & Monitoramento

1. **Logging da Aplicação**

   * Logging em JSON (via `python-json-logger`) direcionado a Loki (Grafana) ou a arquivo local.
   * Níveis: DEBUG (apenas dev), INFO, WARNING, ERROR.
   * Exemplo de entrada de log:

     ```json
     {
       "time": "2025-06-05T14:23:11.123Z",
       "level": "ERROR",
       "message": "Erro ao salvar asset",
       "module": "asset.routes",
       "org_id": 3,
       "user_id": 7,
       "path": "/assets/upload"
     }
     ```

2. **AuditLog (Banco)**

   * Cada CRUD importante dispara gravação em `AuditLog`.
   * Armazenamos: `org_id`, `user_id`, `action`, `entity`, `entity_id`, `timestamp`, `ip_address` e `payload` (dados antes e depois).
   * Particionamento mensal para performance (via `pg_partman` ou particionamento nativo do PostgreSQL 16).

3. **Métricas & Monitoramento**

   * **Prometheus** coleta métricas customizadas (contagem de uploads, latência de endpoints, uso de disco).
   * **Grafana** exibe dashboards com:

     * Utilização de CPU, memória, I/O, filas Celery.
     * Latência de endpoints (P95, P99), taxas de erros (5xx).
     * Uso de espaço por organização (para aviso de cota).
   * **Sentry** rastreia exceções em produção, registrando contexto de `org_id` e `user_id`.

4. **Alertas e SLA**

   * Grafana → Opsgenie/Slack:

     * Quota de armazenamento > 80 %.
     * Taxa de erro 5xx > 2 % em janelas de 10 minutos.
     * Latência de upload > 3 segundos.

---

## Usabilidade & Acessibilidade

1. **Design System**

   * Base em Bootstrap 5.3 com tokens de cor que seguem WCAG AA (contraste mínimo 4.5:1).
   * Componentes padrão (botões, cards, modals) em `templates/components/` para consistência visual.

2. **Layout Responsivo**

   * **Grid de Thumbnails**: CSS Grid / Masonry para reflow suave de 320px a 4K.
   * **Navbar Fixa** com campo de busca e menu de usuário.
   * **Sidebar Colapsável** para filtros em telas maiores; em telas pequenas vira dropdown no topo.

3. **Navegação por Teclado & Acessibilidade**

   * **Atalhos**:

     * `Ctrl + K`: foca campo de busca.
     * `Shift + Clique`: seleção múltipla de assets.
     * `Delete`: move seleção para a lixeira.
   * Navegação por `Tab`: foco claro em botões e links.
   * **ARIA Labels** em inputs, botões e tabelas para leitores de tela.

4. **Feedback Claro**

   * **Toasts** e **Alerts** coloridos (verde: sucesso, amarelo: aviso, vermelho: erro) para todas as ações do usuário (ex.: “Upload concluído!”, “Tag duplicada!”).
   * **Empty States** amigáveis: “Nenhuma biblioteca encontrada. Crie a primeira aqui!” com botão chamativo.

5. **Dark Mode**

   * Detecta `prefers-color-scheme` do navegador, mas permite alternar manualmente por ícone (sol/lua) no cabeçalho.
   * Variáveis CSS definem temas claro e escuro (cores, backgrounds, bordas).

6. **Formulários Intuitivos**

   * Validação inline (via HTMX + Flask-WTF), sem recarregar a página.
   * Campos obrigatórios marcados com `*` e mensagens de erro contextualizadas abaixo do campo.

---

## Relatórios

1. **Página de Relatórios (`/reports/assets`)**

   * Exporta lista de assets da organização logada em formato CSV.

     * “Pré-visualizar”: mostra tabela com 5 primeiras linhas + contagem total.
     * “Exportar CSV” / “Exportar Excel” / “Exportar PDF” / “Exportar ZIP”.

2. **Funcionalidades Técnicas**

   * **CSV/Excel**: uso de `pandas` + `openpyxl` para gerar planilhas formatadas (datas, valores numéricos).
   * **PDF**: HTML estilizado via Jinja2 + CSS, convertido por `pdfkit` + `wkhtmltopdf`.
   * **ZIP**: agrupa objetos filtrados em ZIP via `zipstream` para streaming eficiente, sem estourar memória.
   * **Agendamento de Relatórios**:

     * OWNER/MANAGER pode agendar relatórios (diários, semanais, mensais).
     * Celery Beat roda tarefa programada que gera o relatório e envia por e-mail (via `Flask-Mail`), incluindo link seguro com expiração de 24h.

---

## Integração com App Mobile (MAUI)

Se o app mobile será feito em **MAUI**, convém expor APIs RESTful no backend para o MAUI consumir. A seguir os principais pontos:

1. **Blueprint `/api/v1`**

   * Crie um módulo `arkiv_app/api/` com:

     * `routes.py`: define endpoints JSON como `/api/v1/auth/login`, `/api/v1/libraries`, `/api/v1/folders/<id>/assets`, etc.
     * `schemas.py`: define Marshmallow schemas para serialização e validação de payload (UserSchema, LibrarySchema, AssetSchema etc.).
   * As rotas retornam JSON padronizado:

     ```json
     {
       "success": true,
       "data": { ... },
       "message": "Operação realizada com sucesso."
     }
     ```

2. **Autenticação & Autorização**

   * Utilize **JWT** (via `PyJWT` ou `Flask-JWT-Extended`) para autenticar chamadas do app MAUI.
   * No login (web ou mobile), gere token de acesso (e opcionalmente refresh token).
   * Proteja as rotas da API com decorator `@jwt_required()`, verificando se o usuário pertence à organização correta e seu papel.

3. **CORS (Cross-Origin Resource Sharing)**

   * No `run.py` (ou em `__init__.py`), habilite CORS apenas para rotas `/api/*`, restringindo origens (p. ex. `https://meuappmobile.com` ou `http://localhost:3000`).
   * Use `flask-cors` para simplificar:

     ```python
     from flask_cors import CORS
     CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"].split(",")}})
     ```

4. **Padrão de Versionamento**

   * Prefixe as rotas com `/api/v1` na primeira versão.
   * Se no futuro for necessário quebrar compatibilidade, crie `/api/v2` sem impactar o app já publicado.

5. **Endpoints Essenciais para App MAUI**

   * **Autenticação**:

     * `POST /api/v1/auth/login` → `{ email, password }` retorna `access_token` (e opcional `refresh_token`).
     * `POST /api/v1/auth/refresh` → obtém novo access\_token.
   * **Usuário / Perfil**:

     * `GET /api/v1/auth/profile` → retorna dados de perfil do usuário logado (`name`, `email`, `role`, `org_id`).
   * **Bibliotecas**:

     * `GET /api/v1/libraries` → lista bibliotecas da org.
     * `POST /api/v1/libraries` → cria nova biblioteca.
     * `PUT /api/v1/libraries/<id>` → edita nome/descrição.
     * `DELETE /api/v1/libraries/<id>` → remove (soft delete).
   * **Pastas**:

     * `GET /api/v1/libraries/<lib_id>/folders` → lista pastas dentro da biblioteca (incluindo aninhadas).
     * `POST /api/v1/folders` → cria nova pasta (envia `library_id`, `parent_id`, `name`).
     * `PUT /api/v1/folders/<id>` → renomeia ou move.
     * `DELETE /api/v1/folders/<id>` → remove (soft delete).
   * **Assets**:

     * `POST /api/v1/folders/<folder_id>/assets` → upload de arquivo (multipart/form-data).
     * `GET /api/v1/folders/<folder_id>/assets` → lista assets da pasta (paginação, filtros mínimos).
     * `GET /api/v1/assets/<id>` → detalhes do asset (incluindo URL assinado para download).
     * `PUT /api/v1/assets/<id>` → update (ex.: renomear, tags).
     * `DELETE /api/v1/assets/<id>` → soft delete.
   * **Tags**:

     * `GET /api/v1/tags` → lista tags da organização.
     * `POST /api/v1/tags` → cria nova tag.
     * `PUT /api/v1/tags/<id>` → edita nome ou cor.
     * `DELETE /api/v1/tags/<id>` → remove (soft delete).
     * `POST /api/v1/assets/<id>/tags` → associa/desassocia tags do asset.
   * **Busca**:

     * `GET /api/v1/search?q=...` → retorna lista de assets/bibliotecas/pastas que batem com o termo (com facets básicas).

6. **Documentação da API**

   * Use `flask-smorest` ou `Flask-RESTful` com Swagger/OpenAPI para gerar documentação automática.
   * Mantenha o arquivo `docs/api_spec.yaml` sincronizado com os endpoints para facilitar testes manuais (Postman) ou geração de SDK para MAUI (via OpenAPI Generator).

7. **Fluxo de Upload no Mobile**

   * O MAUI envia arquivo via `multipart/form-data` para `/api/v1/folders/<folder_id>/assets`.
   * O backend recebe, salva o arquivo temporariamente, gera `filename_storage` único, dispara task Celery para criar thumbnail (e opcionalmente OCR/IA).
   * Retorna imediatamente ao mobile algo como:

     ```json
     {
       "success": true,
       "data": {
         "id": 123,
         "filename_orig": "foto.jpg",
         "url_preview": "https://cdn.arkiv.app/thumbs/…jpg",
         "status": "processing"
       },
       "message": "Upload recebido. Thumbnail será gerado em alguns segundos."
     }
     ```

8. **Cuidado com Conexão Instável**

   * No MAUI, implementar re-envio em caso de falha de rede (retry) ou upload em chunk.
   * No backend, aceitar `Content-Range` headers se quiser suporte a uploads chunked, mas isso é opcional e pode ficar para versão futuro.

---

## Como Rodar

1. **Clone & Configuração Inicial**

   ```bash
   git clone https://github.com/seu-user/arkiv.git
   cd arkiv
   cp .env.example .env
   # Preencha .env com as credenciais locais (PostgreSQL rodando em localhost, AWS, Stripe, etc.)
   ```

2. **Instale Dependências e Migrations**

   ```bash
   python -m venv venv
   source venv/bin/activate   # no Windows: venv\Scripts\activate
   pip install -r requirements.txt
   flask db upgrade
   python -m arkiv_app.utils.create_initial_data
   ```

   * Cria organização “DemoCorp” e usuário `owner@democorp.com` / `(OWNER)1234`.

3. **Rodar a Aplicação**

   ```bash
   python run.py
   ```

   * Acessar no navegador: `http://localhost:5000`
   * Rotas API: `http://localhost:5000/api/v1/...`

4. **Configurar Celery Worker**

   * Em terminal à parte, execute:

     ```bash
     celery -A arkiv_app.celery_app worker --loglevel=info
     ```
   * O arquivo `celery_app.py` dentro de `arkiv_app/` configura o broker para o Redis, que dispara tarefas de thumbnail, OCR e relatórios agendados.

---

## Roadmap

* **Curto Prazo**

  * Integração com IA tagging (AWS Rekognition).
  * OCR básico (Tesseract) junto ao thumbnail.
  * Documentação completa da API (OpenAPI/Swagger).

* **Médio Prazo**

  * SSO (OAuth2 / SAML) – suporte a Azure AD, Google Workspace.
  * Webhooks configuráveis (novo upload, tag adicionada).
  * Pagamentos recorrentes via Stripe para planos (SaaS).

* **Longo Prazo**

  * Suporte a vídeos (transcodificação automática, streaming HLS).
  * Aplicativos móveis offline (cache & sincronização).
  * ML avançado: reconhecimento facial, detecção de objetos e scene recognition.

---

## Contribua

1. **Abra uma Issue**

   * Descreva bugs ou features antes de começar a codar.

2. **Fork & Branch**

   ```bash
   git clone https://github.com/seu-user/arkiv.git
   cd arkiv
   git checkout -b feature/nome-da-feature
   ```

3. **Commits Semânticos**

   * Use [Conventional Commits](https://www.conventionalcommits.org/) (ex.: `feat: adicionar filtro de tamanho no search`).

4. **Pull Request**

   * Explique claramente as mudanças, inclua screenshots (se UI) e instruções para testar.

5. **Revisão e Merge**

   * Mantenha o código limpo, documentado e siga as boas práticas de segurança e usabilidade aqui descritas.

---

**Contato** → `arkiv@exemplo.com`
Dúvidas, bugs ou sugestões são sempre bem-vindos!
