from flask import Blueprint, request, jsonify
from app import db
from app.models import Story, Page, Choice

bp = Blueprint('api', __name__)

API_KEY = "your-secret-api-key-12345"

# ============ READING ENDPOINTS (PUBLIC) ============

@bp.route('/stories', methods=['GET'])
def get_stories():
    """GET /stories?status=published"""
    status = request.args.get('status')
    
    if status:
        stories = Story.query.filter_by(status=status).all()
    else:
        stories = Story.query.all()
    
    return jsonify([s.to_dict() for s in stories])

@bp.route('/stories/<int:story_id>', methods=['GET'])
def get_story(story_id):
    """GET /stories/<id>"""
    story = Story.query.get_or_404(story_id)
    return jsonify(story.to_dict())

@bp.route('/stories/<int:story_id>/start', methods=['GET'])
def get_story_start(story_id):
    """GET /stories/<id>/start"""
    story = Story.query.get_or_404(story_id)
    if not story.start_page_id:
        return jsonify({'error': 'Story has no start page'}), 400
    start_page = Page.query.get(story.start_page_id)
    return jsonify(start_page.to_dict())

@bp.route('/pages/<int:page_id>', methods=['GET'])
def get_page(page_id):
    """GET /pages/<id>"""
    page = Page.query.get_or_404(page_id)
    return jsonify(page.to_dict())

# ============ WRITING ENDPOINTS ============

@bp.route('/stories', methods=['POST'])
def create_story():
    """POST /stories"""
    data = request.json
    story = Story(
        title=data.get('title'),
        description=data.get('description'),
        status=data.get('status', 'published'),
        author_id=data.get('author_id')
    )
    db.session.add(story)
    db.session.commit()
    return jsonify(story.to_dict()), 201

@bp.route('/stories/<int:story_id>', methods=['PUT'])
def update_story(story_id):
    """PUT /stories/<id>"""
    story = Story.query.get_or_404(story_id)
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

@bp.route('/stories/<int:story_id>', methods=['DELETE'])
def delete_story(story_id):
    """DELETE /stories/<id>"""
    story = Story.query.get_or_404(story_id)
    db.session.delete(story)
    db.session.commit()
    return '', 204

@bp.route('/stories/<int:story_id>/pages', methods=['POST'])
def create_page(story_id):
    """POST /stories/<id>/pages"""
    story = Story.query.get_or_404(story_id)
    data = request.json
    
    page = Page(
        story_id=story_id,
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

@bp.route('/pages/<int:page_id>/choices', methods=['POST'])
def create_choice(page_id):
    """POST /pages/<id>/choices"""
    page = Page.query.get_or_404(page_id)
    data = request.json
    
    choice = Choice(
        page_id=page_id,
        text=data.get('text'),
        next_page_id=data.get('next_page_id')
    )
    db.session.add(choice)
    db.session.commit()
    return jsonify(choice.to_dict()), 201

@bp.route('/pages/<int:page_id>', methods=['PUT'])
def update_page(page_id):
    """PUT /pages/<id>"""
    page = Page.query.get_or_404(page_id)
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

@bp.route('/pages/<int:page_id>', methods=['DELETE'])
def delete_page(page_id):
    """DELETE /pages/<id>"""
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    return '', 204

@bp.route('/choices/<int:choice_id>', methods=['DELETE'])
def delete_choice(choice_id):
    """DELETE /choices/<id>"""
    choice = Choice.query.get_or_404(choice_id)
    db.session.delete(choice)
    db.session.commit()
    return '', 204