import urllib.request
from html.parser import HTMLParser
from bs4 import BeautifulSoup

import math
import datetime
import time
import os.path

if __name__ == '__main__':
    # define the parameters
    timeoutTime = 10  # type: int
    outputPath = "./images"

    # time intervals (in seconds)
    timeInterval = 60
    totalTime = math.inf
    maxFactor = 0.0

    # done defining the parameters
    cumulTime = 0

    while cumulTime < totalTime:
        # Measure starting time
        startTime = time.time()

        try:
            # Check whether we should capture an image (if it's daytime)
            curDate = datetime.datetime.now()
            if curDate.hour > 7 or curDate.hour < 19:
                print("It's daytime! Trying to capture an image...")

                # Download image
                imageUrl = "http://meteo-laval-web.gel.ulaval.ca/getCamera.php"
                webcamImgData = urllib.request.urlopen(imageUrl, timeout=timeoutTime).read()

                # Parse the html to figure out the precipitation rate
                rainUrl = "http://meteo-laval.gel.ulaval.ca/index.html"
                htmlData = urllib.request.urlopen(rainUrl, timeout=timeoutTime).read()

                soup = BeautifulSoup(htmlData, 'html.parser')
                # Find the rainfall rate
                rainRateStr = soup.find(id="rain_rate").get_text()
                # rainRate = float(rainRateStr.split()[0])

                # Find the wind speed and direction
                windSpeedStr = soup.find(id="vents_avg").get_text()

                # Create filename
                imageFilename = '{:%Y%m%d_%H%M%S}.jpg'.format(curDate)
                outputFile = os.path.join(outputPath, imageFilename)

                # Save to disk
                fw = open(outputFile, 'wb')
                fw.write(webcamImgData)
                fw.close()

                # Append to the .csv file
                csvPath = os.path.join(outputPath, "0-images.csv")
                with open(csvPath, 'a') as fd:
                    print("{}, {}, {}".format(imageFilename, rainRateStr, windSpeedStr), file=fd)
                fd.close()

                # Yay, everything worked!
                print("Successfully saved image %s" % imageFilename)

            else:
                # It's nighttime, don't download anything and wait 5 minutes before we try again.
                time.sleep(5 * 60)

        except urllib.request.URLError as error:
            print("Encountered an URL error: {}".format(error))

        except ValueError:
            print("Encountered an error: {}".format(error))

        # except:
        #     print("Encountered another error... oops!")

        # Measure end time
        elapsedTime = time.time() - startTime

        # Sleep
        if elapsedTime < timeInterval:
            print("Waiting %d seconds for next download" % (timeInterval - elapsedTime))
            time.sleep(timeInterval - elapsedTime)

        cumulTime += timeInterval
