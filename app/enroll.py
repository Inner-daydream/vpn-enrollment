"""Provides user enrollment utilities to app and cli"""
import argparse
import bcrypt
from app import dynamodb

def enroll_user(password,email,displayname,admin=False):
    """Creates a new user"""
    password = bytes(password,'UTF-8')
    hashed_password = bcrypt.hashpw(password,bcrypt.gensalt())
    dynamodb.new_user(password=hashed_password,admin=admin,id=email,displayname=displayname)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-password')
    parser.add_argument('-email')
    parser.add_argument('-admin',action='store_true')
    parser.add_argument('-displayname')
    args = parser.parse_args()
    enroll_user(
        password=args.password,
        email=args.email,
        admin=args.admin,
        displayname=args.displayname)
