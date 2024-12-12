import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from myapp.models import Conversation, AmountOfMessagesShown
from myapp.forms import ContactForm, AmountForm


def home(request):
    if not request.user.is_authenticated:
        return redirect('/auth/login/')

    form = ContactForm()
    amount_form = AmountForm()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        amount_form = AmountForm(request.POST)

        if amount_form.is_valid():
            amount = int(amount_form.cleaned_data['amount'])

            amount_messages, created = AmountOfMessagesShown.objects.get_or_create(
                user_id=request.user.id
            )

            # If the object already exists
            if not created:
                amount_messages.shown_messages = amount
                amount_messages.save()

        if form.is_valid():
            user_message = form.cleaned_data['question']
            ai_message = get_response(user_message)

            Conversation.objects.create(user_message=user_message,
                                        ai_message=ai_message,
                                        user_id=request.user.id)

    user_conversation = Conversation.objects.filter(user_id=request.user.id).order_by("-id")

    if not user_conversation.exists():
        user_conversation = Conversation.objects.create(
            user_id=request.user.id,
            user_message="Hello",
            ai_message="How can I assist you today?"
        )
        user_conversation = Conversation.objects.filter(user_id=request.user.id).order_by("-id")

    amount_messages, created = AmountOfMessagesShown.objects.get_or_create(
        user_id=request.user.id
    )

    real_amount = 1
    try:
        real_amount = user_conversation.count()
    except:
        pass

    num_messages_to_show = min(int(amount_messages), real_amount)
    message_modeled = []


    for msg in user_conversation[:num_messages_to_show]:
        message_modeled.append({
            "user": msg.user_message,
            "ai": msg.ai_message
        })


    message_modeled = message_modeled[::-1]
    context = {'form': form, 'amount_form': amount_form, 'success_message': message_modeled}

    return render(request, 'myapp/base.html', context)


def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # Redirect to home or dashboard
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'myapp/login.html')


def custom_logout(request):
    logout(request)
    return redirect('/auth/login/')  # Redirect to login page


def custom_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('/auth/login/')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'myapp/register.html', {'form': form})


def get_response(text_="", cust_sys_=""):
    encoded_text = str(text_)
    encoded_cust_sys = str(cust_sys_)

    port = "8998"

    url = f"http://0.0.0.0:{port}/translate?text={encoded_text}&cust_sys={encoded_cust_sys}"

    try:
        response = requests.get(url)
    except:
        return "Server is down"

    if response.status_code == 200:
        data = response.json()
        return data["ai"]
    else:
        error = f"Error: {response.status_code} - {response.text}"
        return error
