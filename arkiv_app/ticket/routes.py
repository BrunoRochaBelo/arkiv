from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Ticket
from ..utils.audit import record_audit
from ..utils import current_org_id
from . import ticket_bp
from .forms import TicketForm


@ticket_bp.route('/tickets')
@login_required
def list_tickets():
    org_id = current_org_id()
    tickets = Ticket.query.filter_by(org_id=org_id).order_by(Ticket.created_at.desc()).all()
    return render_template('ticket/list.html', tickets=tickets, title='Chamados')


@ticket_bp.route('/tickets/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        org_id = current_org_id()
        ticket = Ticket(
            org_id=org_id,
            creator_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
        )
        db.session.add(ticket)
        db.session.commit()
        record_audit('create', 'ticket', ticket.id, user_id=current_user.id, org_id=org_id)
        flash('Chamado criado', 'success')
        return redirect(url_for('ticket.list_tickets'))
    return render_template('ticket/form.html', form=form, title='Novo Chamado')
