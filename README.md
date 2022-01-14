# Athlete Monitoring

## Installation instructions
### 1. Generate config file
Go to the `dash_server\` directory and execute:
```bash
python index.py
```

### 2. Edit config file
The config file (`config.yml`) is automatically generated. Edit the file and insert your clientID and clientSecret from the [Polar administration panel](https://admin.polaraccesslink.com/).

The file should look something like this:
```yml
access_token:
client_id: dc18d373-50o5-428d-b8bc-cb243350eb7b
client_secret: 99f3a036-8799-47e4-b69b-9be7c9gf1cea
refresh_token:
```

### 3. Run dash
Now you can start the python script again, like in step 1.

Then go to http://localhost:8050/ to view the application.



## Information for project optimization

### Downloadspeed

Current Benchmark (Download + Export as .parquet)

JFV U19 2021/22 - 19 Files
From 16:08:41.002688 till 16:22:05.220114
Total time: 13,64 minutes 
Max. single download time: 1.0880410166666665 (61,088 seconds)
Min. single download time: 0.4237647666666666 (25,425 seconds)
Total Average : 0.6701537566666667 (40,209 seconds)