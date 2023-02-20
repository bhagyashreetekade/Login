#tokens this will generate tokens or a unique string for us

#use to reset the password
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from six import text_type

class TokenGenerator(PasswordResetTokenGenerator):
    #Function will make hash value
    def _make_hash_value(self,user,timestamp):
        return(
            #user.pk is primary key ..a unique code for a user
            text_type(user.pk) + text_type(timestamp)  #this is the unique string which will be used to activate the account of the user

        )
#call class  
generate_token =TokenGenerator()