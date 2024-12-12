from fastapi import FastAPI, Form, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from auth.hashing import hash_password, verify_password
from auth.models import create_user, get_user_info, get_conversation, update_conversation, get_user_by_username, \
    update_amount
from auth.utils import create_access_token, verify_access_token
from fastapi import Cookie
from pathlib import Path
from fastapi.staticfiles import StaticFiles
import requests
import uvicorn

app = FastAPI()

templates = Jinja2Templates(directory="templates")

static_dir = Path(__file__).parent / "static"

# Mount static directory to serve CSS files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
active_sessions = {}


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Register"})


@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    hashed_pw = hash_password(password)
    user_id = create_user(username, hashed_pw)
    if not user_id:
        raise HTTPException(status_code=400, detail="Username already exists")
    return RedirectResponse(url="/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db_user = get_user_by_username(username)
    if not db_user or not verify_password(password, db_user["password"]):
        return templates.TemplateResponse("login.html",
                                          {"request": request, "title": "Login", "info": "User not found"})
    print("1")
    token = create_access_token({"sub": username})
    active_sessions[token] = username
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@app.api_route("/", methods=["GET", "POST"], response_class=HTMLResponse, )
def handle_form(request: Request, access_token: str = Cookie(None), question: str = Form(None),
                amount: str = Form(None)):
    if not access_token:
        return RedirectResponse(url="/login", status_code=303)

    payload = verify_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")

    if not username:
        response = RedirectResponse(url="/logout", status_code=303)
        return response

    try:
        username_id, amount_of_messages_shown = get_user_info(username)
    except:
        response = RedirectResponse(url="/logout", status_code=303)
        return response


    error = None
    if request.method == "POST":
        if amount:
            try:
                amount = int(amount)
                update_amount(amount=amount, id=username_id)
                username_id, amount_of_messages_shown = get_user_info(username)
            except:
                error = "Must be a number"

        if question:
            print(question)

            ai_response = get_response(text_=question)
            print(ai_response)

            update_conversation(username_id=username_id, user_message=question, ai_response=ai_response)

    model_message = []
    conversation = get_conversation(username_id)
    if not conversation:
        message = {
            "user": "Hello",
            "ai": "How can I assist you?"
        }

        model_message.append(message)


    try:
        for convo in conversation[-amount_of_messages_shown:]:
            message = {
                "user": convo["user_message"],
                "ai": convo["ai_response"]
            }

            model_message.append(message)
    except:
        model_message = [
            {
                "user": "Exception",
                "ai": "Fatal error. Check your db and logout"
            }
        ]

    return templates.TemplateResponse("protected.html",
                                      {"request": request, "title": "Protected", "username": username,
                                       "success_message": model_message, "error": error})


@app.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


def get_response(text_="", cust_sys_=""):
    encoded_text = str(text_)
    encoded_cust_sys = str(cust_sys_)

    port = "8998"

    url = f"http://0.0.0.0:{port}/translate?text={encoded_text}&cust_sys={encoded_cust_sys}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data["ai"]
    else:
        error = f"Error: {response.status_code} - {response.text}"
        return error


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
