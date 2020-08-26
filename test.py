import json
import boto3
import time
import argparse

client = boto3.client('elbv2')
apic = boto3.client('apigateway')
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', required=True)
    args = parser.parse_args()
    s3_obj =boto3.client('s3')

    s3_clientobj = s3_obj.get_object(Bucket='my123tesbucket', Key='datas.json')
    s3_clientdata = s3_clientobj['Body'].read().decode('utf-8')
 
#Defining the condition for assigning value for different environments
    input=args.env
    s3clientlist=json.loads(s3_clientdata)
    #print("json loaded data")
    #print(s3clientlist)
    for x in s3clientlist:
        #print(x)
        #print(s3clientlist[x])
        for data in s3clientlist[x]:
            if (input == "dev"):
                vpc=data['vpc']
                listener=data['listener']
                nlb=data['nlb']
                alb=data['alb']
                tcp_ports=data['tcp_ports']
                http_ports= data['http_ports']
                http_name=data['http_name']
                api=data['api']
                tcp_name=data['tcp_name']
                health_path=data['health_path']
                stage_names=data['stage_names']
                env="dev"
            elif (input == "prod"):
                vpc=data['vpc']
                listener=data['listener']
                nlb=data['nlb']
                alb=data['alb']
                tcp_ports=data['tcp_ports']
                http_ports= data['http_ports']
                http_name=data['http_name']
                api=data['api']
                tcp_name=data['tcp_name']
                health_path=data['health_path']
                stage_names=data['stage_names']
                env="prod"
            elif (input == "pre"):
                vpc=data['vpc']
                listener=data['listener']
                nlb=data['nlb']
                alb=data['alb']
                tcp_ports=data['tcp_ports']
                http_ports= data['http_ports']
                http_name=data['http_name']
                api=data['api']
                tcp_name=data['tcp_name']
                health_path=data['health_path']
                stage_names=data['stage_names']
                env="pre"
            else:
                print("environment does not exists")

#Calling functions 
    print("test")
    tcp_target_group(env,vpc,nlb,tcp_ports,tcp_name)
    http_target_group(env,vpc,alb,listener,http_ports,http_name,health_path)
    api_create(env,nlb,api,stage_names,tcp_ports)
    


#Target group creation function for network loadbalancer

def tcp_target_group(env,vpc,nlb,tcp_ports,tcp_name):
    count=len(tcp_ports)
    validation = client.describe_target_groups(LoadBalancerArn=nlb,)
    listen_valid = client.describe_listeners(LoadBalancerArn=nlb,)
    i=x=l=0
    while i <count:
        for res in validation['TargetGroups']:
            if('cdb-'+env+tcp_name[i] == res['TargetGroupName']):
                x=1
        if(x!=1):
            response = client.create_target_group(
                Name='cdb-'+env+tcp_name[i],
                Protocol='TCP',
                Port=int(tcp_ports[i]),
                VpcId=vpc,
                TargetType='ip'
            )
            print('cdb-'+env+tcp_name[i]+"target group created")
            for tar in response['TargetGroups']:
                target_arn = tar['TargetGroupArn']
            for lis in listen_valid['Listeners']:
                if(int(tcp_ports[i]) == int(lis['Port'])):
                    l=1
            if(l!=1):
                tcp_listener(int(tcp_ports[i]),nlb,target_arn)
            else:
                print("listener on the port"+tcp_ports[i]+"already exists")
        else:
            print('cdb-'+env+tcp_name[i]+"already exists")
        
        i=i+1

#Listener creation function for network loadbalancer

def tcp_listener(port,nlb,target_arn):
    response = client.create_listener(
        LoadBalancerArn=nlb,
        Protocol='TCP',
        Port=port,
        DefaultActions=[
                {'Type': 'forward','TargetGroupArn': target_arn}
        ]
    )
    print("listener is created for tcp target groups")
    
#Target group creation function for application loadbalancer    
    
def http_target_group(env,vpc,alb,listener,http_ports,http_name,health_path):
    count = len(http_ports)
    validation = client.describe_target_groups(LoadBalancerArn=alb,)
    i=x=0
    while(i!=(count)):
        for res in validation['TargetGroups']:
            if('cdb-'+env+http_name[i] == res['TargetGroupName']):
                x=1
        if(x!=1):
            response = client.create_target_group(
                Name='cdb-'+env+http_name[i],
                Protocol='HTTP',
                Port=int(http_ports[i]),
                VpcId=vpc,
                TargetType='ip',
                HealthCheckPath=health_path[i]
            )
            print('cdb-'+env+http_name[i]+"target group created")
            for x in response['TargetGroups']:
                target_arn = x['TargetGroupArn']
            create_rule_and_listener(int(http_ports[i]),target_arn,listener,alb)
        else:
            print('cdb-'+env+http_name[i]+"already exists")
        
        i=i+1

#listener and Rule creation function for application loadbalancer

def create_rule_and_listener(http_ports,target_arn,listener,alb):
    if(http_ports==7001):
        Values=["/pricing*","/cdbHome*","/maintenance*"]
        count=len(Values)
        i=0
        while(i!=count):
            response = client.create_rule(
                ListenerArn=listener,
                Conditions=[
                    {'Field': 'path-pattern','Values': [Values[i]],}
                ],
                Priority=i+2,
                Actions=[
                    {
                        'Type': 'forward',
                        'TargetGroupArn': target_arn,
                    }
                ]
            )
            i=i+1
            print(response)
    if(http_ports==9500):
        Values=["/myTest1","/getUserInfoByNtlm"]
        count=len(Values)
        i=0
        prt=5
        while(i!=count):
            response = client.create_rule(
                ListenerArn=listener,
                Conditions=[
                    {'Field': 'path-pattern','Values': [Values[i]],}
                ],
                Priority=prt,
                Actions=[
                    {
                        'Type': 'forward',
                        'TargetGroupArn': target_arn,
                    }
                ]
            )
            i=i+1
            prt=prt+1
            print(response)
    if(http_ports==9090):
        response = client.create_rule(
            ListenerArn=listener,
            Conditions=[

                {'Field': 'path-pattern','Values': ['/*Apache*'],}
            ],
            Priority=7,
            Actions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': target_arn,
                }
            ]
        )
        response = client.create_rule(
            ListenerArn=listener,
            Conditions=[

                {'Field': 'path-pattern','Values': ['/'],}
            ],
            Priority=9,
            Actions=[
                {   
                    'Type': 'redirect',
                    'RedirectConfig': {
                        'Protocol': 'HTTPS',
                        'Port': '443',
                        'Host': '#{host}',
                        'Path': '/cdbHome/home/home.do',
                        'Query': '#{query}',
                        'StatusCode': 'HTTP_301'
                    },
                }
            ]
        )

        response = client.create_listener(
            LoadBalancerArn=alb,
            Protocol='HTTP',
            Port=80,
            DefaultActions=[
                {   
                    'Type': 'redirect', 
                    'RedirectConfig': {
                        'Protocol': 'HTTPS',
                        'Port': '443',
                        'Host': '#{host}',
                        'Path': '/cdbHome/home/home.do',
                        'Query': '#{query}',
                        'StatusCode': 'HTTP_301'
                    },
                }
            ]
        )

#API stage creation function

def api_create(env,nlb,api,stage_names,tcp_ports):
    #name=stage_names
    validation  = apic.get_stages(restApiId=api,)
    name=["authorization","datasearch","ruleEngine","thirdPartyWrapper","etl","product","facility","pricing","grouping","pricesync"]
    #count = len(stage_names)
    count=len(name)
    i=x=0
    while i < count:
        for res in validation['item']:
            if(name[i] == res['stageName']):
                x=1
        if(x!=1):
            response = apic.create_deployment(
                restApiId=api,
                stageName=name[i],
                variables={
                    'HTTP_ENDPOINT': nlb,
                    'HTTP_PORT':tcp_ports[i]
                },
            )
            print(name[i]+"created")
            
        else:
            print(name[i]+" is already there")
                
        time.sleep(10)
        i=i+1
    
