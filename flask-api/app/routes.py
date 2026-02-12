from flask import Blueprint, request, jsonify
from app import db
from app.models import Story, Page, Choice

bp = Blueprint('api', __name__)

API_KEY = "your-secret-api-key-12345"

def check_api_key():
    """Level 16: Protect write endpoints"""
    api_key = request.headers.get('X-API-KEY')
    return api_key == API_KEY


bp.route('/stories', methods=['GET'])
def get_stories():
    """GET /stories?status=published"""
    status = request.args.get('status')
    
    if status:
        stories = Story.query.filter_by(status=status).all()
    else:
        stories = Story.query.all()
    
    return jsonify([s.to_dict() for s in stories])
@bp.route('/stories/<int:id>', methods=['GET'])
def get_story(id):
    """GET /stories/<id>"""
    story = Story.query.get_or_404(id)
    return jsonify(story.to_dict())

@bp.route('/stories/<int:id>/start', methods=['GET'])
def get_story_start(id):
    """GET /stories/<id>/start"""
    story = Story.query.get_or_404(id)
    if not story.start_page_id:
        return jsonify({'error': 'Story has no start page'}), 400
    
    start_page = Page.query.get(story.start_page_id)
    return jsonify(start_page.to_dict())

@bp.route('/pages/<int:id>', methods=['GET'])
def get_page(id):
    """GET /pages/<id> → returns page text + choices"""
    page = Page.query.get_or_404(id)
    return jsonify(page.to_dict())


@bp.route('/stories', methods=['POST'])
def create_story():
    """POST /stories"""
    
    data = request.json
    story = Story(
        title=data.get('title'),
        description=data.get('description'),
        status=data.get('status', 'published')
    )
    db.session.add(story)
    db.session.commit()
    return jsonify(story.to_dict()), 201

@bp.route('/stories/<int:id>', methods=['PUT'])
def update_story(id):
    """PUT /stories/<id>"""
    
    story = Story.query.get_or_404(id)
    data = request.json
    
    if 'title' in data:
        story.title = data['title']
    if 'description' in data:
        story.description = data['description']
    if 'status' in data:
        story.status = data['status']
    if 'start_page_id' in data:
        story.start_page_id = data['start_page_id']
    if 'illustration' in data:
        story.illustration = data['illustration']
    
    db.session.commit()
    return jsonify(story.to_dict())

@bp.route('/stories/<int:id>', methods=['DELETE'])
def delete_story(id):
    """DELETE /stories/<id>"""
    
    story = Story.query.get_or_404(id)
    db.session.delete(story)
    db.session.commit()
    return '', 204

@bp.route('/stories/<int:id>/pages', methods=['POST'])
def create_page(id):
    """POST /stories/<id>/pages"""
    
    story = Story.query.get_or_404(id)
    data = request.json
    
    page = Page(
        story_id=id,
        text=data.get('text'),
        is_ending=data.get('is_ending', False),
        ending_label=data.get('ending_label'),
        illustration=data.get('illustration')
    )
    db.session.add(page)
    db.session.commit()
    
    if not story.start_page_id:
        story.start_page_id = page.id
        db.session.commit()
    
    return jsonify(page.to_dict()), 201

@bp.route('/pages/<int:id>/choices', methods=['POST'])
def create_choice(id):
    """POST /pages/<id>/choices"""
    
    page = Page.query.get_or_404(id)
    data = request.json
    
    choice = Choice(
        page_id=id,
        text=data.get('text'),
        next_page_id=data.get('next_page_id')
    )
    db.session.add(choice)
    db.session.commit()
    return jsonify(choice.to_dict()), 201


@bp.route('/pages/<int:id>', methods=['PUT'])
def update_page(id):
    """Update a page"""
    page = Page.query.get_or_404(id)
    data = request.json
    
    if 'text' in data:
        page.text = data['text']
    if 'is_ending' in data:
        page.is_ending = data['is_ending']
    if 'ending_label' in data:
        page.ending_label = data['ending_label']
    if 'illustration' in data:
        page.illustration = data['illustration']
    
    db.session.commit()
    return jsonify(page.to_dict())

@bp.route('/pages/<int:id>', methods=['DELETE'])
def delete_page(id):
    """Delete a page"""
    page = Page.query.get_or_404(id)
    db.session.delete(page)
    db.session.commit()
    return '', 204

@bp.route('/choices/<int:id>', methods=['DELETE'])
def delete_choice(id):
    """Delete a choice"""
    choice = Choice.query.get_or_404(id)
    db.session.delete(choice)
    db.session.commit()
    return '', 204