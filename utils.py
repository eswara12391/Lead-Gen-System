# utils.py - COMPLETE FIX
import re
import google.generativeai as genai
from config import GEMINI_API_KEY

# --- Configure AI ---
AI_AVAILABLE = False
model = None

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # List all available models (for debugging)
        print("🔍 Checking available models...")
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                print(f"  - {m.name}")
        
        # Try to use the most common working models
        preferred_models = [
            'models/gemini-2.0-flash-exp',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'models/gemini-pro'
        ]
        
        for preferred in preferred_models:
            if preferred in available_models:
                try:
                    model = genai.GenerativeModel(preferred)
                    # Skip the test call - just assume it works
                    AI_AVAILABLE = True
                    print(f"✅ Using Gemini model: {preferred}")
                    break
                except Exception as e:
                    print(f"⚠️ {preferred} setup failed: {e}")
                    continue
        
        if not AI_AVAILABLE and available_models:
            # If none of the preferred models work, use the first available
            try:
                model = genai.GenerativeModel(available_models[0])
                AI_AVAILABLE = True
                print(f"✅ Using fallback Gemini model: {available_models[0]}")
            except Exception as e:
                print(f"⚠️ All models failed: {e}")
                AI_AVAILABLE = False
                
    except Exception as e:
        print(f"⚠️ AI Setup Error: {e}. Falling back to hardcoded templates.")
else:
    print("⚠️ No Gemini API key found. Using hardcoded fallback templates.")

# ---------- HELPER: Parse AI Response ----------
def parse_ai_response(text, keys):
    """Extracts sections from AI text like 'Headline: ...' into a dict."""
    result = {}
    for key in keys:
        pattern = rf'{key}:\s*(.*?)(?=\n\w+:|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            result[key.lower()] = match.group(1).strip()
        else:
            result[key.lower()] = f"Could not parse {key}"
    return result

# ---------- 1. PROFILE OPTIMIZATION ----------
def generate_profile_optimization(current_headline, current_about):
    if AI_AVAILABLE and model:
        prompt = f"""
        You are Charlie Hills, a LinkedIn lead generation expert. Rewrite this LinkedIn profile to convert visitors into leads.
        
        Current Headline: {current_headline}
        Current About Section: {current_about}
        
        Output STRICTLY in this exact format:
        Headline: [Write a new, punchy headline stating value proposition]
        About: [Write a 3-paragraph about section using Problem-Agitate-Solution. End with a Call to Action.]
        Experience: [Rewrite experience to highlight 2 key achievements with numbers, focusing on lead generation.]
        """
        try:
            response = model.generate_content(prompt)
            parsed = parse_ai_response(response.text, ['Headline', 'About', 'Experience'])
            
            # Check if we got valid content (no placeholders)
            if ('[Target Audience]' in parsed.get('headline', '') or 
                'Could not parse' in parsed.get('headline', '')):
                print("⚠️ AI returned invalid format. Using fallback.")
                raise Exception("Invalid AI response format")
            
            return {
                "headline": parsed.get('headline', current_headline),
                "about": parsed.get('about', current_about),
                "experience": parsed.get('experience', 'AI generated experience.')
            }
        except Exception as e:
            print(f"AI Error: {e}. Falling back.")
    
    # ---------- FALLBACK (Hardcoded but uses user input) ----------
    return {
        "headline": f"🚀 {current_headline} | Helping [Target Audience] achieve [Specific Result] with [Your Method]",
        "about": f"""{current_about[:100]}...
**The Problem:** Most professionals struggle to turn LinkedIn connections into paying clients. They waste hours posting content that gets zero engagement.
**How I Help:** I use a proven 5-step system that has generated over $2M in pipeline.
**Let's Connect:** Send me a DM with the word "LEADS" and let's chat!""",
        "experience": "🔹 **Lead Generation Architect** (2020-Present)\n- Built automation system generating 150+ leads/month.\n- Scaled personal brand from 2K to 160K followers in 18 months."
    }

# ---------- 2. CONTENT MATRIX ----------
def generate_content_matrix(niche):
    if AI_AVAILABLE and model:
        prompt = f"""
        Create a LinkedIn Content Matrix for the niche: {niche}.
        I need 12 content ideas: 4 types (Educational, Inspirational, Storytelling, How-to) x 3 stages (TOFU Awareness, MOFU Consideration, BOFU Conversion).
        Output as a list in this EXACT format:
        Content Type: [Type], Funnel Stage: [Stage], Topic: [Detailed topic]
        """
        try:
            response = model.generate_content(prompt)
            lines = response.text.strip().split('\n')
            matrix = []
            for line in lines:
                if 'Content Type:' in line:
                    type_match = re.search(r'Content Type:\s*(.*?),\s*Funnel Stage:', line)
                    stage_match = re.search(r'Funnel Stage:\s*(.*?),\s*Topic:', line)
                    topic_match = re.search(r'Topic:\s*(.*)', line)
                    if type_match and stage_match and topic_match:
                        matrix.append({
                            "content_type": type_match.group(1).strip(),
                            "funnel_stage": stage_match.group(1).strip(),
                            "topic": topic_match.group(1).strip()
                        })
            if len(matrix) >= 9:
                return matrix
        except Exception as e:
            print(f"AI Error: {e}. Falling back.")
    
    # ---------- FALLBACK ----------
    topics = {
        "Educational": [f"Why {niche} is evolving", f"Top 5 {niche} trends", f"How {niche} impacts revenue"],
        "Inspirational": [f"How I failed mastering {niche}", f"The mindset shift for {niche}", f"Why patience beats perfection in {niche}"],
        "Storytelling": [f"The day I almost quit {niche}", f"Client went $0 to $10k using {niche}", f"Worst advice in {niche}"],
        "How-to": [f"Building a {niche} funnel", f"5 quick wins for {niche}", f"Automate 80% of {niche} outreach"]
    }
    matrix, stages = [], ["TOFU (Awareness)", "MOFU (Consideration)", "BOFU (Conversion)"]
    for ct, t_list in topics.items():
        for i, stage in enumerate(stages):
            matrix.append({"content_type": ct, "funnel_stage": stage, "topic": f"{t_list[i % len(t_list)]} (Variant {i+1})"})
    return matrix

# ---------- 3. PAS POSTS ----------
def generate_pas_post(topic):
    if AI_AVAILABLE and model:
        prompt = f"""
        Write a LinkedIn post using PAS framework about: {topic}.
        Output in this exact format:
        Hook: [Bold opening using [brackets]]
        Problem: [2 sentences]
        Agitate: [3 sentences on negative consequences]
        Solution: [3-4 step solution]
        CTA: [Question to drive comments]
        """
        try:
            response = model.generate_content(prompt)
            parsed = parse_ai_response(response.text, ['Hook', 'Problem', 'Agitate', 'Solution', 'CTA'])
            return {
                "hook": parsed.get('hook', f"[STOP] struggling with {topic}?"),
                "problem": parsed.get('problem', f"Most professionals struggle with {topic}."),
                "agitate": parsed.get('agitate', "You're wasting time and losing money."),
                "solution": parsed.get('solution', "Follow this exact system."),
                "cta": parsed.get('cta', f"👇 Your biggest challenge with {topic}?")
            }
        except Exception as e:
            print(f"AI Error: {e}. Falling back.")
    
    # ---------- FALLBACK ----------
    return {
        "hook": f"[STOP] scrolling if you're struggling with {topic.lower()}.",
        "problem": f"Most professionals in this space are trying to master {topic}, but they make the same mistakes. They focus on tactics instead of strategy.",
        "agitate": f"You're wasting 10+ hours a week on content that barely gets 50 views. Competitors are pulling ahead. You're burning out without results.",
        "solution": f"Here's the exact system I used to dominate {topic}:\n1. Optimize profile.\n2. Use a content matrix.\n3. Engineer PAS posts.\n4. Add visuals.\n5. Double down on data.",
        "cta": f"👇 What's your biggest challenge with {topic}? Drop a comment!"
    }

# ---------- 4. VISUAL SCRIPTS ----------
def generate_visual_script(post):
    problem = post.get('problem', 'lead gen')
    solution = post.get('solution', 'follow the system')
    
    if AI_AVAILABLE and model:
        prompt = f"""
        Create a 3-slide whiteboard script for a LinkedIn carousel.
        Problem: {problem}
        Solution: {solution}
        Output in this exact format:
        Slide 1: [Description]
        Slide 2: [Description]
        Slide 3: [Description]
        """
        try:
            response = model.generate_content(prompt)
            parsed = parse_ai_response(response.text, ['Slide 1', 'Slide 2', 'Slide 3'])
            return {
                "slide_1": parsed.get('slide 1', f"🎯 Problem: {problem}"),
                "slide_2": parsed.get('slide 2', "🔥 Agitation: Wasting time."),
                "slide_3": parsed.get('slide 3', f"✅ Solution: {solution}")
            }
        except Exception as e:
            print(f"AI Error: {e}. Falling back.")
    
    # ---------- FALLBACK ----------
    return {
        "slide_1": f"🎯 SLIDE 1: The Problem\nIllustration: Person staring at laptop, puzzled.\nText: 'Struggling with {problem[:50]}...'",
        "slide_2": "🔥 SLIDE 2: The Agitation\nIllustration: Graph going down, clock ticking.\nText: 'Wasting time. Losing money. Missing targets.'",
        "slide_3": f"✅ SLIDE 3: The Solution\nIllustration: 4-step flowchart.\nText: '{solution[:80]}...'"
    }

# ---------- 5. ANALYTICS ----------
def calculate_top_20(analytics_data):
    if not analytics_data:
        return []
    sorted_data = sorted(analytics_data, key=lambda x: x.get('engagement_rate', 0), reverse=True)
    top_20_count = max(1, int(len(sorted_data) * 0.2))
    return sorted_data[:top_20_count]