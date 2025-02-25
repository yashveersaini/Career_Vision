from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
import joblib
import google.generativeai as genai
import re
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

model_path = os.path.join(os.path.dirname(__file__), "attached_assets", "deemanding_job_model.joblib")
csv_path = os.path.join(os.path.dirname(__file__), "attached_assets", "deemanding_job.csv")

# Load the saved model and label encoders
try:
    model_data = joblib.load(model_path)
    logger.info("Successfully loaded model data")
    pipeline = model_data['pipeline']
    label_encoder = model_data['label_encoder']
    interest_encoder = model_data['interest_encoder']
    X = model_data['X']
    y = model_data['y']
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise


# Function to predict job roles
def predict_job_roles_with_fallback(skills_list, interest, threshold=0.3):
    try:
        # Preprocess input
        skills_text = " ".join(skills_list).lower()
        interest_encoded = interest_encoder.transform([interest])[0]

        # Create input DataFrame
        input_data = pd.DataFrame({
            "skills": [skills_text],
            "interest_encoded": [interest_encoded]
        })

        # Transform input using the pipeline's preprocessor
        input_transformed = pipeline.named_steps['preprocessor'].transform(input_data)

        # Predict job roles (Use probabilities)
        predicted_probs = pipeline.named_steps['classifier'].predict_proba(input_transformed)[0]

        #  Get all roles with probabilities above the threshold
        predicted_roles = []
        for idx, prob in enumerate(predicted_probs):
            if prob >= threshold:
                predicted_roles.append(label_encoder.inverse_transform([idx])[0])

        # Fallback: Use cosine similarity
        if not predicted_roles:
            X_transformed = pipeline.named_steps['preprocessor'].transform(X)
            similarities = cosine_similarity(input_transformed, X_transformed).flatten()
            closest_match_indices = np.argsort(similarities)[-2:][::-1]
            predicted_roles = [label_encoder.inverse_transform([y[idx]])[0] for idx in closest_match_indices]

        return predicted_roles

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return ["Data Analyst", "Software Developer"]  # Safe fallback


YOUTUBE_VIDEO_LINKS = {
    "Machine Learning Engineer": [
        "https://www.youtube.com/embed/T4MLrtOKPjY?si=nRwq1K0rjBgXCNCt",
        "https://www.youtube.com/embed/AMxtGWcMYd4?si=5q-bC3zQkUdrntFA"
    ],
    "Frontend Developer": [
        "https://www.youtube.com/embed/DbRXv5TXMEE?si=gbZlWP4fyDgiBL_p",
        "https://www.youtube.com/embed/X8BYu3dMKf0?si=ySZgmkYU-M432BiW"
    ],
    "Backend Developer": [
        "https://www.youtube.com/embed/tsTXFiRT8b8?si=BoTO6xfjpxbXTqxU",
        "https://www.youtube.com/embed/QUcC1RB8vy0?si=oFtwWQ-b_JgtwAIM"
    ],
    "Full Stack Developer": [
        "https://www.youtube.com/embed/1IVopxj8q8U?si=EOt6KrXcsFHXtHaK",
        "https://www.youtube.com/embed/G0gKX4wmIGs?si=hg2O_5RHwE2dZWOQ"
    ],
    "Data Analyst": [
        "https://www.youtube.com/embed/o2mDheV9GFU?si=J-WUihm-mHmX90g_",
        "https://www.youtube.com/embed/dMn2QFTyXUQ?si=czy-sidD8n3UHbv0"
    ],
    "AI Engineer": [
        "https://www.youtube.com/embed/MhCHrvfAXlc?si=mmEXBIruylYlRCNI",
        "https://www.youtube.com/embed/efam9B6VKwo?si=kI_gCl45LDPcFO3a"
    ],
    "Cybersecurity Specialist": [
        "https://www.youtube.com/embed/ocDmB0muCC4?si=sjmcOELtI08MkC1e",
        "https://www.youtube.com/embed/eUiIGbDZFQc?si=zKSi0rSpLdZKWN9V"
    ],
    "Mobile App Developer (Android)": [
        "https://www.youtube.com/embed/KAh2TOrtTq4?si=_wvG3wBplCqrJkBR",
        "https://www.youtube.com/embed/AhUL5tHF3uc?si=2q4wmFRmATZsFEWY"
    ],
    "Mobile App Developer (Flutter)": [
        "https://www.youtube.com/embed/KdXp0gv601o?si=aqYmu8J3y1zvzNu2",
        "https://www.youtube.com/embed/oIzwUPr6Eow?si=fYECcmEk0bENRcMh"
    ],
    "Python Developer": [
        "https://www.youtube.com/embed/6R0TkF6Mgrk?si=2PhldJ2RYxirgRwt",
        "https://www.youtube.com/embed/05wsOB7mxmw?si=sTfjcLnJQ85uF9EA"
    ],
    "Cloud Engineer": [
        "https://www.youtube.com/embed/70oYrSnRgoI?si=FgozibvodHv1JXRr",
        "https://www.youtube.com/embed/NBFWgilq0EY?si=8uzCurhu57j-rJfz"
    ],
    "Data Scientist": [
        "https://www.youtube.com/embed/PFPt6PQNslE?si=xM9H1DkPGHW44MT2",
        "https://www.youtube.com/embed/NUpNoK_5NVs?si=EPsmkah0wgJEVZ8X"
    ],
    "DevOps Engineer": [
        "https://www.youtube.com/embed/P77GhVfvuKQ?si=T3f_Hg0zOBstpus2",
        "https://www.youtube.com/embed/lENeZmjD2zc?si=GWxN9KPRuswgQ4mC"
    ],
    "UI/UX Designer": [
        "https://www.youtube.com/embed/GvNPAglqPyY?si=dOiZuoCWQP87O7k7",
        "https://www.youtube.com/embed/FUJ5ZErpFSo?si=Z3OyUDWCDPeuiJuO"
    ],
    "Big Data Engineer": [
        "https://www.youtube.com/embed/Atc7Jt-OhXw?si=-J4YwBFX4K5rSj7a",
        "https://www.youtube.com/embed/rsOSrEbK7sU?si=lNxZOTDG-jcFZMha"
    ],
    "iOS Developer": [
        "https://www.youtube.com/embed/q9XJPz9dSh4?si=U40ZQhzzKIsWW4hC",
        "https://www.youtube.com/embed/CuB3dg8F3sY?si=3GQpyl8o0P5ZQQMN"
    ],
    "Blockchain Developer": [
        "https://www.youtube.com/embed/uULy2rc6YDc?si=H9UTjDlh_Gtn5b8G",
        "https://www.youtube.com/embed/8BpxqVGiuSk?si=DpyNQj04YPf4qv9E"
    ],
    "Game Developer": [
        "https://www.youtube.com/embed/GqKjSpd2zvY?si=UyCRFL9u92I2co66",
        "https://www.youtube.com/embed/qPxvmrtTQ_4?si=OEqZ1xth1RwX3g4Z"
    ],
    "Data Engineer": [
        "https://www.youtube.com/embed/f9KUFEeWMoc?si=sF5vcAx6npHOn2Zj",
        "https://www.youtube.com/embed/IGraly_Lvvg?si=A5NMoZNdLP_BKa3w"
    ],
    "Product Manager": [
        "https://www.youtube.com/embed/J8VBh3JhNDY?si=ZoBfNYqPN_SV4pkP",
        "https://www.youtube.com/embed/HNfVykENVrg?si=_DkEn2EJAmauq7SX"
    ]
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        skills = data.get('skills', [])
        interest = data.get('interest', '')

        if not skills or not interest:
            return jsonify({"error": "Missing skills or interest"}), 400

        predicted_roles = predict_job_roles_with_fallback(skills, interest)

        # Prepare results with embedded YouTube links
        results = []
        for role in predicted_roles:
            video_links = YOUTUBE_VIDEO_LINKS.get(role, [])
            if len(video_links) < 2:
                video_links.extend([
                                       "https://www.youtube.com/embed/dQw4w9WgXcQ",
                                       "https://www.youtube.com/embed/dQw4w9WgXcQ"
                                   ][:2 - len(video_links)])
            results.append({"role": role, "video_links": video_links})

        return jsonify(results)

    except Exception as e:
        logger.error(f"Error in predict route: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/jobs')
def jobs():
    return render_template('jobs.html')


@app.route('/get_jobs')
def get_jobs():
    try:
        # Load job data from CSV
        df = pd.read_csv(csv_path)
        jobs_list = df.to_dict('records')
        return jsonify(jobs_list)
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        return jsonify({"error": "Error fetching job listings"}), 500


# Set up API Key
API_KEY = "AIzaSyBs0W-DuzlhnK_Yw_yJlPY1AaFt9I0CPAs"
genai.configure(api_key=API_KEY)

# Create a model instance
model = genai.GenerativeModel("gemini-pro")


@app.route('/api', methods=['POST'])
def chatbot():
    try:
        user_message = request.json.get('message', '')
        if not user_message:
            return jsonify({"error": "Please enter a message"}), 400

        # Generate response using Gemini
        response = model.generate_content(
            f"You are a career counselor helping users with job-related questions so give answer in short.\nUser: {user_message}")

        # bot_response = response.text
        clean_text = re.sub(r"\*\*(.*?)\*\*", r"\1", response.text)
        return jsonify({"response": clean_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
