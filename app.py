from flask import Flask, abort, render_template, redirect, session, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from forms import RegistrationForm, LoginForm, CampaignForm, AdRequestForm, SearchForm
from models import InfluencerProfile, db, User, Campaign, AdRequest
from models import AdRequest, Campaign
from flask import render_template
from sqlalchemy import func
from models import User, Campaign, AdRequest, InfluencerProfile



app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, user_type=form.user_type.data)
        db.session.add(user)
        # copy name is session
        session['username'] = user.username

        db.session.commit()

        if user.user_type == 'influencer':
            profile = InfluencerProfile(user_id=user.id, niche="Update your niche", reach=0)
            db.session.add(profile)
            db.session.commit()

        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)





@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            # Store the username in session after successful login
            session['username'] = user.username
            flash('Logged in successfully', 'success')
            # redirect to admin sponsor infulencer dashboard based on user type
            if user.user_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.user_type == 'sponsor':
                return redirect(url_for('sponsor_dashboard'))
            elif user.user_type == 'influencer':
                return redirect(url_for('influencer_dashboard'))
            
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))




@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.user_type != 'admin':
        return redirect(url_for('index'))

    # Query total sponsors and influencers
    total_sponsors = User.query.filter_by(user_type='sponsor').count()
    total_influencers = User.query.filter_by(user_type='influencer').count()

    # Query total ad requests and campaigns
    total_ad_requests = AdRequest.query.count()
    total_campaigns = Campaign.query.count()

    # Retrieve lists of sponsors, influencers, and ad requests for detailed display
    sponsors = User.query.filter_by(user_type='sponsor').all()
    influencers = User.query.filter_by(user_type='influencer').all()
    ad_requests = AdRequest.query.all()
    campaigns = Campaign.query.all()

    return render_template(
        'admin_dashboard.html',
        total_sponsors=total_sponsors,
        total_influencers=total_influencers,
        total_ad_requests=total_ad_requests,
        total_campaigns=total_campaigns,
        sponsors=sponsors,
        influencers=influencers,
        ad_requests=ad_requests,
        campaigns=campaigns
    )












@app.route('/sponsor_dashboard')
@login_required
def sponsor_dashboard():
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    ad_requests = AdRequest.query.filter_by(sponsor_id=current_user.id).all()

    # Filter requests by their status
    accepted_requests = [request for request in ad_requests if request.status == 'Accepted']
    total_accepted_requests = db.session.query(func.count(AdRequest.id)).filter_by(sponsor_id=current_user.id, status='Accepted').scalar()

    rejected_requests = [request for request in ad_requests if request.status == 'Rejected']
    pending_requests = [request for request in ad_requests if request.status == 'Pending']
    total_requests = len(ad_requests)
    #  accepted_requests1 is accepted request by spomnor
    # Calculate total campaigns, influencers, and spent budget
    total_campaigns = len(campaigns)
    total_influencers = len(set(request.influencer_id for request in ad_requests))
    total_spent_budget = sum(request.payment_amount for request in accepted_requests if request.payment_amount)

    return render_template(
        'sponsor_dashboard.html',
        campaigns=campaigns,
        accepted_requests=accepted_requests,
        total_accepted_requests=total_accepted_requests,
        rejected_requests=rejected_requests,
        pending_requests=pending_requests,
        total_campaigns=total_campaigns,
        total_influencers=total_influencers,
        total_spent_budget=total_spent_budget,
        total_requests=total_requests
    )






@app.route('/influencer_dashboard')
@login_required
def influencer_dashboard():
    if current_user.user_type != 'influencer':
        return redirect(url_for('index'))

    # Fetch all ad requests related to the current influencer
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()

    # Calculate totals and other required data
    accepted_requests = [request for request in ad_requests if request.status == 'Accepted']
    total_accepted_requests = len(accepted_requests)
    total_requests = len(ad_requests)

    # Fetch campaigns and calculate total campaigns
    campaigns = Campaign.query.filter_by(visibility='public').all()
    total_campaigns = len(campaigns)

    # Calculate revenue
    revenue = db.session.query(func.sum(AdRequest.payment_amount)).filter_by(influencer_id=current_user.id, status='Accepted').scalar()

    return render_template(
        'influencer_dashboard.html',
        ad_requests=ad_requests,
        total_accepted_requests=total_accepted_requests,
        total_requests=total_requests,
        campaigns=campaigns,
        total_campaigns=total_campaigns,
        revenue=revenue
    )








from datetime import datetime

@app.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if current_user.user_type != 'sponsor':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        niche = request.form.get('niche')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = request.form.get('budget')
        goals = request.form.get('goals')
        visibility = request.form.get('visibility')

        # Convert date strings to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Create new campaign
        new_campaign = Campaign(
            title=title,
            description=description,
            niche=niche,
            start_date=start_date,
            end_date=end_date,
            budget=float(budget),
            goals=goals,
            visibility=visibility,
            sponsor_id=current_user.id
        )
        db.session.add(new_campaign)
        db.session.commit()

        # Redirect back to sponsor dashboard after successful creation
        return redirect(url_for('sponsor_dashboard'))

    return render_template('create_campaign.html')








@app.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    # Ensure the user is a sponsor
    if current_user.user_type != 'sponsor':
        return redirect(url_for('index'))

    # Query the campaign by its ID
    campaign = Campaign.query.get_or_404(campaign_id)

    # Ensure the campaign belongs to the current user
    if campaign.sponsor_id != current_user.id:
        return redirect(url_for('sponsor_dashboard'))

    if request.method == 'POST':
        # Update campaign details
        campaign.title = request.form.get('title')
        campaign.description = request.form.get('description')
        campaign.niche = request.form.get('niche')
        campaign.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        campaign.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        campaign.budget = float(request.form.get('budget'))
        campaign.goals = request.form.get('goals')
        campaign.visibility = request.form.get('visibility')

        # Commit the changes to the database
        db.session.commit()

        # Redirect back to sponsor dashboard after successful edit
        return redirect(url_for('sponsor_dashboard'))

    # Render the edit campaign form with current campaign data
    return render_template('edit_campaign.html', campaign=campaign)










@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if campaign and campaign.sponsor_id == current_user.id:
        # Delete all associated ad requests
        AdRequest.query.filter_by(campaign_id=campaign_id).delete()
        db.session.delete(campaign)
        db.session.commit()
        flash('Campaign deleted successfully', 'success')
    else:
        flash('Campaign not found or not authorized', 'danger')
    return redirect(url_for('sponsor_dashboard'))




@app.route('/create_ad_request', methods=['GET', 'POST'])
@login_required
def create_ad_request():
    if current_user.user_type != 'sponsor':
        return redirect(url_for('index'))
    form = AdRequestForm()
    if form.validate_on_submit():
        ad_request = AdRequest(
            requirements=form.requirements.data,
            payment_amount=form.payment_amount.data,
            status=form.status.data,
            campaign_id=request.form.get('campaign_id'),
            influencer_id=request.form.get('influencer_id')
        )
        db.session.add(ad_request)
        db.session.commit()
        flash('Ad request created successfully', 'success')
        return redirect(url_for('sponsor_dashboard'))
    return render_template('create_ad_request.html', form=form)

@app.route('/edit_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
@login_required
def edit_ad_request(ad_request_id):
    if current_user.user_type != 'sponsor':
        return redirect(url_for('index'))
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.campaign.sponsor_id != current_user.id:
        return redirect(url_for('index'))
    form = AdRequestForm()
    if form.validate_on_submit():
        ad_request.requirements = form.requirements.data
        ad_request.payment_amount = form.payment_amount.data
        ad_request.status = form.status.data
        db.session.commit()
        flash('Ad request updated successfully', 'success')
        return redirect(url_for('sponsor_dashboard'))
    elif request.method == 'GET':
        form.requirements.data = ad_request.requirements
        form.payment_amount.data = ad_request.payment_amount
        form.status.data = ad_request.status
    return render_template('edit_ad_request.html', form=form)

@app.route('/delete_ad_request/<int:ad_request_id>', methods=['POST'])
@login_required
def delete_ad_request(ad_request_id):
    if current_user.user_type != 'sponsor':
        return redirect(url_for('index'))
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.campaign.sponsor_id != current_user.id:
        return redirect(url_for('index'))
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully', 'success')
    return redirect(url_for('sponsor_dashboard'))

@app.route('/view_campaigns')
@login_required
def view_campaigns():
    if current_user.user_type != 'influencer':
        return redirect(url_for('index'))
    # Exclude campaigns that the influencer has already applied to
    applied_campaign_ids = [ad_request.campaign_id for ad_request in AdRequest.query.filter_by(influencer_id=current_user.id).all()]
    campaigns = Campaign.query.filter(Campaign.visibility == 'public', Campaign.id.notin_(applied_campaign_ids)).all()
    return render_template('view_campaigns.html', campaigns=campaigns)




@app.route('/request_ad', methods=['POST'])
@login_required
def request_ad():
    campaign_id = request.form.get('campaign_id')
    description = request.form.get('description')
    requirements = request.form.get('requirements')
    payment_amount = request.form.get('payment_amount')

    if not all([campaign_id, description, requirements, payment_amount]):
        flash('All fields are required.', 'danger')
        return redirect(url_for('influencer_dashboard'))

    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        flash('Campaign not found.', 'danger')
        return redirect(url_for('influencer_dashboard'))

    ad_request = AdRequest(
        campaign_id=campaign_id,
        influencer_id=current_user.id,
        sponsor_id=campaign.sponsor_id,
        description=description,
        requirements=requirements,
        payment_amount=payment_amount,
        status='Pending'
    )

    db.session.add(ad_request)
    db.session.commit()

    flash('Ad request submitted successfully.', 'success')
    return redirect(url_for('influencer_dashboard'))


@app.route('/negotiate_ad/<int:ad_request_id>', methods=['POST'])
@login_required
def negotiate_ad(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.sponsor_id != current_user.id:
        abort(403)

    payment_amount = request.form.get('payment_amount')
    ad_request.payment_amount = payment_amount
    ad_request.status = 'Negotiation'

    db.session.commit()
    flash('Ad request negotiation submitted.', 'success')
    return redirect(url_for('sponsor_dashboard'))

@app.route('/accept_ad_request/<int:ad_request_id>', methods=['POST'])
@login_required
def accept_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.sponsor_id != current_user.id:
        abort(403)

    ad_request.status = 'Accepted'
    db.session.commit()
    flash('Ad request accepted.', 'success')
    return redirect(url_for('sponsor_dashboard'))




@app.route('/accept_request/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    if current_user.user_type != 'sponsor':
        return redirect(url_for('index'))
    
    ad_request = AdRequest.query.get_or_404(request_id)
    if ad_request.sponsor_id != current_user.id:
        return redirect(url_for('sponsor_dashboard'))

    ad_request.status = 'Accepted'
    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))

@app.route('/reject_request/<int:request_id>', methods=['POST'])
@login_required
def reject_request(request_id):
    if current_user.user_type != 'sponsor':
        return redirect(url_for('index'))
    
    ad_request = AdRequest.query.get_or_404(request_id)
    if ad_request.sponsor_id != current_user.id:
        return redirect(url_for('sponsor_dashboard'))

    ad_request.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))





@app.route('/reject_ad_request/<int:ad_request_id>', methods=['POST'])
@login_required
def reject_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.sponsor_id != current_user.id:
        abort(403)

    ad_request.status = 'Rejected'
    db.session.commit()
    flash('Ad request rejected.', 'success')
    return redirect(url_for('sponsor_dashboard'))

@app.route('/request_ad_from_influencer/<int:influencer_id>', methods=['POST'])
@login_required
def request_ad_from_influencer(influencer_id):
    if current_user.user_type != 'sponsor':
        return redirect(url_for('index'))

    influencer = User.query.filter_by(id=influencer_id, user_type='influencer').first_or_404()
    form = AdRequestForm()
    if form.validate_on_submit():
        ad_request = AdRequest(
            requirements=form.requirements.data,
            payment_amount=form.payment_amount.data,
            status='Pending',
            campaign_id=None,  # This can be updated if you associate it with a campaign
            influencer_id=influencer_id,
            sponsor_id=current_user.id
        )
        db.session.add(ad_request)
        db.session.commit()
        flash('Ad request sent to influencer', 'success')
        return redirect(url_for('sponsor_dashboard'))

    return redirect(url_for('sponsor_dashboard'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    influencers = []
    campaigns = []
    if form.validate_on_submit():
        search_query = form.search_query.data
        if current_user.user_type == 'sponsor':
            influencers = User.query.filter(User.user_type == 'influencer', User.username.contains(search_query)).all()
        elif current_user.user_type == 'influencer':
            campaigns = Campaign.query.filter(Campaign.visibility == 'public', Campaign.title.contains(search_query)).all()
    return render_template('search.html', form=form, influencers=influencers, campaigns=campaigns)





@app.route('/influencers_list', methods=['GET'])
@login_required
def influencers_list():
    search_query = request.args.get('search_query', '')

    # Querying the database
    if search_query:
        influencers = db.session.query(User, InfluencerProfile).filter(
            (User.username.ilike(f'%{search_query}%')) |
            (InfluencerProfile.niche.ilike(f'%{search_query}%'))
        ).join(InfluencerProfile).filter(User.id == InfluencerProfile.user_id).all()
    else:
        influencers = db.session.query(User, InfluencerProfile).join(InfluencerProfile).all()

    return render_template('influencers_list.html', influencers=influencers)

@app.route('/edit_influencer/<int:influencer_id>', methods=['GET', 'POST'])
@login_required
def edit_influencer(influencer_id):
    influencer_profile = InfluencerProfile.query.filter_by(user_id=influencer_id).first_or_404()

    if request.method == 'POST':
        influencer_profile.niche = request.form['niche']
        influencer_profile.reach = request.form['reach']

        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('influencer_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

    return render_template('edit_influencer.html', influencer_profile=influencer_profile)




@app.route('/ad_request_action/<int:ad_request_id>/<action>', methods=['POST'])
@login_required
def ad_request_action(ad_request_id, action):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if current_user.user_type == 'influencer' and ad_request.influencer_id == current_user.id:
        if action == 'accept':
            ad_request.status = 'Accepted'
        elif action == 'reject':
            ad_request.status = 'Rejected'
        
        db.session.commit()
        flash('Ad request updated successfully', 'success')
        return redirect(url_for('influencer_dashboard'))
    elif current_user.user_type == 'sponsor' and ad_request.campaign.sponsor_id == current_user.id:
        # Add logic for sponsor to negotiate, accept or reject influencer's response
        pass
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
