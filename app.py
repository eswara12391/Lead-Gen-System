from flask import Flask, render_template, request, jsonify
from models import (
    init_db, save_profile, get_latest_profile,
    save_topic, get_topics_by_niche,
    save_post, get_posts_by_topic,
    save_visual, get_visual_by_post,
    save_analytics, get_all_analytics
)
from utils import (
    generate_profile_optimization,
    generate_content_matrix,
    generate_pas_post,
    generate_visual_script,
    calculate_top_20
)

app = Flask(__name__)

# Initialize Database on startup
with app.app_context():
    if init_db():
        print("✅ Database initialized successfully!")
    else:
        print("❌ Failed to initialize database. Check your MySQL connection in config.py")

# ---------- ROUTES ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/profiles')
def profiles_page():
    return render_template('profile.html')

@app.route('/content')
def content_page():
    return render_template('content.html')

@app.route('/posts')
def posts_page():
    return render_template('posts.html')

@app.route('/visuals')
def visuals_page():
    return render_template('visuals.html')

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/topics')
def topics_page():
    return render_template('content.html')

# ---------- API ENDPOINTS ----------
@app.route('/api/optimize_profile', methods=['POST'])
def api_optimize_profile():
    data = request.json
    current_headline = data.get('headline', 'Your Current Headline')
    current_about = data.get('about', 'Your current about section.')
    
    optimized = generate_profile_optimization(current_headline, current_about)
    save_profile(optimized['headline'], optimized['about'], optimized['experience'])
    
    return jsonify({"success": True, "data": optimized})

@app.route('/api/get_profile', methods=['GET'])
def api_get_profile():
    profile = get_latest_profile()
    return jsonify({"success": True, "data": profile})

@app.route('/api/generate_matrix', methods=['POST'])
def api_generate_matrix():
    data = request.json
    niche = data.get('niche', 'B2B Marketing')
    
    matrix = generate_content_matrix(niche)
    for item in matrix:
        save_topic(niche, item['topic'], item['funnel_stage'], item['content_type'])
    
    return jsonify({"success": True, "data": matrix})

@app.route('/api/get_topics', methods=['POST'])
def api_get_topics():
    data = request.json
    niche = data.get('niche', 'B2B Marketing')
    topics = get_topics_by_niche(niche)
    return jsonify({"success": True, "data": topics})

@app.route('/api/generate_post', methods=['POST'])
def api_generate_post():
    data = request.json
    topic_text = data.get('topic', 'Lead Generation')
    topic_id = data.get('topic_id')
    
    post = generate_pas_post(topic_text)
    if topic_id:
        save_post(topic_id, post['hook'], post['problem'], post['agitate'], post['solution'], post['cta'])
    
    return jsonify({"success": True, "data": post})

@app.route('/api/get_posts', methods=['POST'])
def api_get_posts():
    data = request.json
    topic_id = data.get('topic_id')
    if not topic_id:
        return jsonify({"success": False, "error": "topic_id required"})
    posts = get_posts_by_topic(topic_id)
    return jsonify({"success": True, "data": posts})

@app.route('/api/generate_visual', methods=['POST'])
def api_generate_visual():
    data = request.json
    post_id = data.get('post_id')
    post_data = data.get('post_data', {})
    
    visual = generate_visual_script(post_data)
    if post_id:
        save_visual(post_id, visual['slide_1'], visual['slide_2'], visual['slide_3'])
    
    return jsonify({"success": True, "data": visual})

@app.route('/api/get_visual', methods=['POST'])
def api_get_visual():
    data = request.json
    post_id = data.get('post_id')
    if not post_id:
        return jsonify({"success": False, "error": "post_id required"})
    visual = get_visual_by_post(post_id)
    return jsonify({"success": True, "data": visual})

@app.route('/api/save_analytics', methods=['POST'])
def api_save_analytics():
    data = request.json
    post_title = data.get('post_title')
    impressions = data.get('impressions', 0)
    clicks = data.get('clicks', 0)
    reactions = data.get('reactions', 0)
    comments = data.get('comments', 0)
    
    if impressions > 0:
        engagement_rate = round(((reactions + comments + clicks) / impressions) * 100, 2)
    else:
        engagement_rate = 0.0
    
    save_analytics(post_title, impressions, clicks, reactions, comments, engagement_rate)
    return jsonify({"success": True})

@app.route('/api/get_analytics', methods=['GET'])
def api_get_analytics():
    all_data = get_all_analytics()
    top_20 = calculate_top_20(all_data)
    return jsonify({
        "success": True,
        "all": all_data,
        "top_20": top_20
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)