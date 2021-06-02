from email.message import EmailMessage, Message
from typing import List
from sqlalchemy.orm.session import Session
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Response, Request, Cookie
from fastapi.param_functions import Depends
from config import CLIENT_SECRETS_FILE, SCOPES, API_SERVICE_NAME, API_VERSION

from starlette.responses import RedirectResponse
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
from schemas import google as schemas
from schemas import senders as sender_schemas
from schemas import users as user_schemas
from services import google as services
from services import senders as sender_services

router = APIRouter(
  prefix="/accounts",
  tags=["accounts"],
  responses={404: {"description": "Not found"}},
)

@router.get("/{account_id}/senders", response_model=List[sender_schemas.SenderOut])
def get_senders(account_id: int, current_user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return sender_services.get_senders_by_account(db, account_id)

@router.put("/{account_id}/senders")
def update_senders(account_id: int, current_user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = services.get_account(db=db, account_id=account_id)

    gmail = services.initialize_gmail(account)

    return sender_services.generate_senders(db, gmail, account, current_user.id, start_date=account.updated_at)
    

@router.post("/{account_id}/senders")
def generate_initial_senders(account_id: int, current_user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = services.get_account(db=db, account_id=account_id)
    account.owner = current_user
    db.commit()

    gmail = services.initialize_gmail(account)

    return sender_services.generate_senders(db, gmail, account, current_user.id)

@router.get("/oauth2callback", response_model=schemas.AccountOut)
def oauth2callback(request: Request, db: Session = Depends(get_db)):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # TODO: figure out getting state from a cookie in prod, and add state= arg
    # to from_client_secrets_file
    #   What does the state string do? it gets attached as a parameter to the
    #   Google authentication link, so that when they hit /oauth2callback
    #   they can provide that token to prove that it was google and not some
    #   evil third party who discovered this secret endpoint and wants to exploit
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = request.url_for('oauth2callback')

    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    gmail = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)
    results = gmail.users().getProfile(userId='me').execute()

    account = schemas.AccountCreate.parse_obj(
        {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'email': results['emailAddress']
          })

    # TODO: svae credentials, get email from api and save that too, return email+id
    db_account = services.create_account(db=db, account=account)
    return db_account.__dict__

@router.get("/")
def authorize_new_account(request: Request, response: Response):

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = request.url_for("oauth2callback")

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # TODO: figure out saving state as a cookie in prod
    # response.set_cookie(key="google_auth", value=state)
    return RedirectResponse(url=authorization_url)