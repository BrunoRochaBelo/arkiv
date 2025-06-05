"""Seed initial data for development."""
from arkiv_app import create_app
from arkiv_app.extensions import db
from arkiv_app.models import Plan, Organization, User, Membership, Library


def main():
    app = create_app()
    with app.app_context():
        # Criação do plano
        plan = Plan.query.first()
        if not plan:
            plan = Plan(name='Basic', storage_quota_gb=10, price_monthly=0, features={})
            db.session.add(plan)
            db.session.commit()

        # Criação da organização demo
        org = Organization.query.filter_by(slug='democorp').first()
        if not org:
            org = Organization(name='DemoCorp', slug='democorp', plan_id=plan.id)
            db.session.add(org)
            db.session.commit()

        # Criação do usuário owner demo
        user = User.query.filter_by(email='owner@democorp.com').first()
        if not user:
            user = User(name='Owner', email='owner@democorp.com')
            user.set_password('(OWNER)1234')  # Sempre hash da senha!
            db.session.add(user)
            db.session.commit()
            membership = Membership(user_id=user.id, org_id=org.id, role='OWNER')
            db.session.add(membership)
            db.session.commit()

        # Biblioteca default para a organização
        lib = Library.query.filter_by(org_id=org.id, name='Default Library').first()
        if not lib:
            lib = Library(org_id=org.id, name='Default Library', description='Exemplo de biblioteca')
            db.session.add(lib)
            db.session.commit()

        print('Initial data created.')


if __name__ == '__main__':
    main()
