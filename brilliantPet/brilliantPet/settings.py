from brilliantPet.is_developement import is_developement

aws_access_key_id = 'AKIAYGF7OQSI64ULKAXK'
aws_secret_access_key='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'
region_name = 'us-east-2'

if is_developement:
    from brilliantPet.developement import *

else:
    from brilliantPet.production import *