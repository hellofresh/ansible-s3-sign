#!/usr/bin/python

def main():

    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        name={'required': True, 'type': 'str' },
        s3_bucket_name={'required': False, 'type': 'str' },
        expire={'default': 60, 'required': False, 'type': 'int' }
    ))

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False )

    if not HAS_BOTO:
      module.fail_json(msg='boto is required.')


    s3_bucket_name = module.params['s3_bucket_name']
    name = module.params['name']
    expire = module.params['expire']
    ec2_url, access_key, secret_key, region = get_ec2_creds(module)
    aws_connect_params = dict(aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key)

    if region:
        host='s3.{}.amazonaws.com'.format(region)
        conn = boto.connect_s3(host=host, **aws_connect_params)
    else:
        conn = boto.connect_s3(**aws_connect_params)

    try:
        bucket = conn.get_bucket(s3_bucket_name)
    except (boto.exception.S3ResponseError, boto.exception.BotoClientError) as E:
        module.fail_json(msg="Failed to connect to s3 bucket '%s'. With error: '%s'" % (s3_bucket_name,E ))

    # TODO: needs class try/except
    s3object = bucket.get_key(name,validate=True)
    if s3object is None:
        module.fail_json(msg="S3 object '%s' does not exists in '%s'" % (name, s3_bucket_name))

    # TODO: needs class try/except
    url=s3object.generate_url(expire, query_auth=True)
    # Exit
    module.exit_json(**{'changed': True, "url": url})

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

# Check boto
HAS_BOTO = False
try:
    import boto
    import boto.s3.connection
    from boto.regioninfo import RegionInfo
    import os
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False


main()
