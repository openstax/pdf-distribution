import boto3

class Config(object):
    def __init__(self, region_name, table_name):
        self.region_name = region_name
        self.table_name  = table_name

        configs = Config.get_configs_from_dynamodb(
            region_name=self.region_name,
            table_name=self.table_name,
        )

        ## The highest version numbered current config
        ## is the one we want.
        def get_version_number(config):
            version_string = config['config_id']['S'] ## e.g., 'ver_123'
            version_number = int(version_string[4:])
            return version_number
        config = sorted(configs, key=get_version_number)[-1]

        self.config_data = config

    def get_version(self):
        return self.config_data['config_id']['S']

    def get_ugly_uri(self, pretty_uri):
        ugly_uri = None
        new_uri = pretty_uri
        while True:
            new_uri = self.config_data['uri_map']['M'] \
                          .get(new_uri,{}) \
                          .get('S', None)
            if new_uri is None:
                break
            elif new_uri == ugly_uri:
                break
            else:
                ugly_uri = new_uri
        return ugly_uri

    def access_is_allowed(self, user, ugly_uri):
        allowed = self.config_data['access_map']['M'] \
                      .get(ugly_uri,{}) \
                      .get('S', '-') \
                      .strip().split()
        return user in allowed

    @staticmethod
    def get_configs_from_dynamodb(region_name, table_name):
        session = boto3.session.Session(region_name=region_name)
        ddb_client = session.client('dynamodb')

        try:
            ## Fetch all configs with is_current set to true.
            ## NOTE: This assumes that DynamoDb does not
            ##       process more than 1MB of data to find
            ##       the desired items.
            ddb_response = ddb_client.scan(
                TableName=table_name,
                ExpressionAttributeValues={
                    ':c': {
                        'BOOL': True,
                    }
                },
                FilterExpression='is_current = :c',
            )
            configs = ddb_response['Items']
        except Exception as error:
            raise RuntimeError('could not get configs (region_name={}, table_name={}): {}'.format(
                region_name,
                table_name,
                str(error),
            ))

        if len(configs) == 0:
            raise RuntimeError('unable to find any table items with is_current == true')
        return configs
