from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Poll, PollOption, PollVote
from ..utils.audit import record_audit
from ..utils import current_org_id
from . import poll_bp
from .forms import PollForm


@poll_bp.route('/polls')
@login_required
def list_polls():
    org_id = current_org_id()
    polls = Poll.query.filter_by(org_id=org_id).order_by(Poll.created_at.desc()).all()
    return render_template('poll/list.html', polls=polls, title='Enquetes')


@poll_bp.route('/polls/create', methods=['GET', 'POST'])
@login_required
def create_poll():
    form = PollForm()
    if form.validate_on_submit():
        org_id = current_org_id()
        poll = Poll(
            org_id=org_id,
            creator_id=current_user.id,
            question=form.question.data,
            closes_at=form.closes_at.data,
        )
        db.session.add(poll)
        db.session.flush()
        for opt_text in form.options.data:
            if opt_text:
                db.session.add(PollOption(poll_id=poll.id, text=opt_text))
        db.session.commit()
        record_audit('create', 'poll', poll.id, user_id=current_user.id, org_id=org_id)
        flash('Enquete criada', 'success')
        return redirect(url_for('poll.list_polls'))
    return render_template('poll/form.html', form=form, title='Nova Enquete')


@poll_bp.route('/polls/<int:poll_id>/vote/<int:option_id>', methods=['POST'])
@login_required
def vote(poll_id, option_id):
    poll = Poll.query.get_or_404(poll_id)
    option = PollOption.query.get_or_404(option_id)
    existing = PollVote.query.filter_by(option_id=option_id, user_id=current_user.id).first()
    if not existing:
        vote = PollVote(option_id=option.id, user_id=current_user.id)
        db.session.add(vote)
        db.session.commit()
        flash('Voto registrado', 'success')
    return redirect(url_for('poll.list_polls'))
