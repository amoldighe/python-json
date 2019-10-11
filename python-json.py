### api-response-time.py checks the stats gathered by the Zabbix server while running Web Monitoring check for API DSP server and leverage them 
### to send tags to the notification server declaring its status and api response time
### PLEASE NOTE: Tags are constructed as <LoginAPI/LoginAPICLUSTER>,<STATUS>,<RESPONSE TIME in seconds>
### amol.di, 10 June 2019

import json
import requests

# Zabbix API server endpoint URL
url = 'http://zabbix.server.ip/zabbix/api_jsonrpc.php'
headers = {'content-type': 'application/json'}
# Zabbix failed step scenario graph id for api servers
api_steps_graph_id = [ '33402' , '33174' , '33165' ]
# Zabbix graph ids for login response time for api servers
api_graph_id = [ '33408' , '33180' , '33171' ]
loop_count = 0

# this loop is going to get the JSON for graph ids and check for failed step
for i in api_steps_graph_id:
    payload = { "jsonrpc": "2.0","method": "history.get","params": {"output": "extend","history": 3,"itemids": (i) ,"sortfield": "clock","sortorder": "DESC","limit": 1},"auth": "dad810e01266e5135f00d8089a377ed7","id": 1 }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    # the JSON response from Zabbix API server is decoded and checked for any failed step
    output_dict = json.loads(response.text)
    api_error = output_dict['result'][0]['value']
    print (i)
    # we are going to construct a URL to be sent to the notification server and the associated tags based on graph status and response time
    if api_error == '0':
        payload = { "jsonrpc": "2.0","method": "history.get","params": {"output": "extend","history": 0,"itemids": (api_graph_id[loop_count]) ,"sortfield": "clock","sortorder": "DESC","limit": 1},"auth": "dad810e01266e5135f00d8089a377ed7","id": 1 }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        output_dict_api = json.loads(response.text)
        api_cluster_rt = output_dict_api['result'][0]['value']
        print (api_cluster_rt)
        url_end= "seconds&message=LoginAPIUP&channel=engineering"
        if (api_graph_id[loop_count]) == '33408':
            url_start= "http://curl-server.ip/alert?to=all&deliverer=0&type=api-endpoint-cluster&tags=LoginAPICluster,UP,RT:"
        elif (api_graph_id[loop_count]) == '33180':
            url_start= "http://curl-server.ip/alert?to=all&deliverer=0&type=api1-dsp-nyc1.do.grid&tags=LoginAPI,UP,RT:"
        elif (api_graph_id[loop_count]) == '33171': 
            url_start= "http://curl-server.ip/alert?to=all&deliverer=0&type=api2-dsp-nyc1.do.grid&tags=LoginAPI,UP,RT:"
        sendurl = url_start + (api_cluster_rt) + url_end
        requests.get(sendurl) 
        loop_count += 1
