from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import TextForm  # Assuming you have created this form
from .utils import process_text, process_pdf  # Helper functions for processing text and PDF

import tensorflow as tf
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.models import load_model
from django.shortcuts import render
from django.http import HttpResponse
from .forms import TextForm
import PyPDF2



def home(request):
    return render(request, 'home.html')

# Register User
def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Save the user and create an account
            user = form.save()
            # Log the user in after successful registration
            login(request, user)  # This logs in the user automatically
            return redirect('dashboard')  # Redirect to dashboard after registration
        else:
            messages.error(request, "Registration failed. Please check your details.")
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})

# Login User
def login_user(request):
    # If the user is already authenticated, redirect them to the dashboard
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)  # Pass request to form to bind the session properly
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if not user.is_active:
                    messages.error(request, 'This account is inactive. Please register again or contact support.')
                    return redirect('register')
                
                # Log the user in
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('user_dashboard')  # Redirect to the user dashboard after successful login
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})
# Logout User
def logout_user(request):
    logout(request)
    return redirect('home')  # ✅ Redirect to Home after logout


import os
import torch
import PyPDF2
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from transformers import BertTokenizer, BertForSequenceClassification
from PIL import Image
import pytesseract

# Load model and tokenizer
MODEL_DIR = os.path.join(settings.BASE_DIR, 'model', 'bert_model')
tokenizer = BertTokenizer.from_pretrained(MODEL_DIR)
model = BertForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

# Extract text from uploaded PDF file
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
        return text.strip()
    except Exception as e:
        print("PDF parsing error:", e)
        return ""
    
def extract_text_from_image(image_file):
    image = Image.open(image_file)  # Open the uploaded image
    text = pytesseract.image_to_string(image)  # Extract text using OCR
    return text.strip()  # Clean and return the result

import torch
from transformers import BertTokenizer, BertForSequenceClassification
import os
from django.conf import settings
import nltk
from nltk.tokenize import sent_tokenize

# Ensure punkt_tab is loaded (assuming it's your custom version of punkt)
nltk.data.path.append(os.path.join(settings.BASE_DIR, "nltk_data"))  # optional: add your custom nltk_data path

def get_prediction_summary(text_input):
    # Update model path using os.path.join with BASE_DIR
    model_path = os.path.join(settings.BASE_DIR, 'model', 'bert_model')  # Adjust the subfolders if necessary

    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForSequenceClassification.from_pretrained(model_path)
    model.eval()

    if not text_input.strip():
        return "No Text Provided", 0, 0

    # Use sentence tokenizer instead of split('.')
    try:
        sentences = nltk.data.load("tokenizers/punkt_tab/english.pickle").tokenize(text_input.strip())
    except LookupError:
        return "punkt_tab resource not found. Please make sure it's installed correctly.", 0, 0

    ai_count = 0
    human_count = 0
    total = len(sentences)

    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=1)[0].tolist()

            ai_score = probs[1]
            human_score = probs[0]

            if ai_score > human_score:
                ai_count += 1
            else:
                human_count += 1

    percent_ai = round((ai_count / total) * 100, 2) if total > 0 else 0
    percent_human = round((human_count / total) * 100, 2) if total > 0 else 0

    if percent_ai > percent_human:
        result_label = "AI-Generated"
    elif percent_human > percent_ai:
        result_label = "Human-Written"
    else:
        result_label = "Mixture Detected"

    return result_label, percent_ai, percent_human









# Dashboard view
@login_required
def user_dashboard(request):
    result = None
    percent_ai = 0
    percent_human = 0
    text_input = ""

    if request.method == 'POST':
        text_input = request.POST.get('text_input', '').strip()
        uploaded_file = request.FILES.get('upload_file')

        if uploaded_file:
            file_type = uploaded_file.content_type
            if file_type == 'application/pdf':
                text_input = extract_text_from_pdf(uploaded_file)
            elif file_type in ['image/jpeg', 'image/png', 'image/jpg']:
                text_input = extract_text_from_image(uploaded_file)
            else:
                text_input = ""

        if text_input:
            result, percent_ai, percent_human = get_prediction_summary(text_input)

    return render(request, 'dashboard.html', {
        'result': result,
        'text_input': text_input,
        'percent_ai': percent_ai,
        'percent_human': percent_human
    })
