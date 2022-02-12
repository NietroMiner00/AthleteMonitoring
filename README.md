# Athlete Monitoring

## Installation instructions

### Installation from source
#### 1. Generate config file
Go to the `dash_server\` directory and execute:
```bash
python index.py
```

#### 2. Edit config file
The config file (`config.yml`) is automatically generated. Edit the file and insert your clientID and clientSecret from the [Polar administration panel](https://admin.polaraccesslink.com/).

The file should look something like this:
```yml
access_token:
client_id: dc18d373-50o5-428d-b8bc-cb243350eb7b
client_secret: 99f3a036-8799-47e4-b69b-9be7c9gf1cea
refresh_token:
```

#### 3. Run dash
Now you can start the python script again, like in step 1.

Then go to http://localhost:8050/ to view the application.

### Installation from .exe:
Put the downloaded .exe file into a separate folder named appropriately and execute it.

#### 1. Edit config file
Edit the auto generated config file analog to similar to 2.) in the Installation from source section

#### 2. Run dash
Now you can execute the .exe file again and you will be redirected to the appropriate website. For future visits on the web application use: http://localhost:8050/

## Step-by-Step guide
In the following we will provide you with a detailed manual of how to use every feature of the application.
### Front-page
You will see the front-page every time you will open the app and each time, when you go to an invalid path.

![](https://i.imgur.com/gg2NQG0.png)

It will ask you to choose if there is already local data or if you want to download your data from the Polar API to be analysed.

![](https://i.imgur.com/0ZJH44a.png)

When you want to download training sessions from polar you first have to select your team and your trainings sessions will be displayed. You can mark one or more sessions for download and add them to the download queue. The download starts on pressing the “Download Queue” Button.
The selection of local data is analogue to the download procedure.

### Analysis-page
When you have selected your data you will be redirected to the analysis-page. There you can see the graphs as discussed in the “Resulting graphs” section.

![](https://i.imgur.com/kdN9ZA8.png)

You can de-/select one or multiple players by clicking on the respective player in the legend of the top graph. Each player that is selected will also be displayed as a graph in the zones section at the bottom of the page. Also you can double-click one player to deselect all other players but this one.

The “Zones” section can display two different kinds of Zone diagrams: speed-zones and heart-rate-zones. You can change between the two graphs by clicking on the respective selection button under the “Zones” title. Each graph also differs between the relative or total time spent in minutes. This can also be adjusted with selection buttons. The zones that are displayed in the graphs can also be customized by the user by entering whole numbers, seperated by comma, in the input field under the relative and total selection.

## Information for project optimization

### Downloadspeed

Current Benchmark (Download + Export as .parquet)

JFV U19 2021/22 - 19 Files
From 16:08:41.002688 till 16:22:05.220114
Total time: 13,64 minutes 
Max. single download time: 1.0880410166666665 (61,088 seconds)
Min. single download time: 0.4237647666666666 (25,425 seconds)
Total Average : 0.6701537566666667 (40,209 seconds)
