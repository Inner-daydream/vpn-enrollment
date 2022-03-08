from base64 import encode
import bcrypt
import dynamodb
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-password')    
parser.add_argument('-email')
parser.add_argument('-admin',action='store_true')
parser.add_argument('-displayname')
args = parser.parse_args()
is_admin = args.admin
password = bytes(args.password,'UTF-8')
email = args.email
displayname = args.displayname
hashed_password = bcrypt.hashpw(password,bcrypt.gensalt())
dynamodb.new_user(password=hashed_password,admin=is_admin,Id=email,displayname=displayname)