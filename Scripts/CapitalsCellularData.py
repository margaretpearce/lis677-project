import sys
import xlrd
import xlwt
from xlutils.copy import copy
import json
import urllib2
import datetime
import time

class CapitalsCellularData():
    def __init__(self, key):
        self.apikey = key
        # self.apirequestfiles = ['Brunei.json', 'Cambodia.json', 'Indonesia.json', 'Laos.json', 'Malaysia.json',
        #                         'Myanmar.json', 'Philippines.json', 'Singapore.json', 'Thailand.json',
        #                         'TimorLeste.json', 'Vietnam.json']
        self.apirequestfiles = ['Malaysia.json']
        self.jsonfilenames = []
        self.countries = []
        self.capitals = []
        self.latitude = []
        self.longitude = []

    def queueapirequests(self):
        # Keep a list of JSON files representing each country

        # Iterate through the list and parse the json
        for i in range(0,len(self.apirequestfiles)):
            # Send all API requests for this country
            self.sendapirequestsbyjson(self.apirequestfiles[i])


    def sendapirequestsbyjson(self, jsonfile):
        # Open the JSON file
        data = open('API Requests/' + jsonfile).read()
        jsondata = json.loads(data)

        # Get country, capital, latitude, longitude, box size for each entry
        country = jsondata["country"]
        capital = jsondata["capital"]
        boundingbox = jsondata["boundingbox"]
        locations = jsondata["locations"]
        numlocations = len(locations)

        # Loop through all locations
        for n in range(0, numlocations):
            latitude = locations[n]["lat"]
            longitude = locations[n]["lng"]

            # Create API request
            outputfile = self.sendapirequest(country, capital, latitude, longitude, boundingbox, n)

            # Save the name of the file
            self.jsonfilenames.append(outputfile)

            # Limit of 5 requests per minute - wait 15 seconds in between each API request
            time.sleep(15)


    def sendapirequest(self, country, capital, latitude, longitude, boxsize, n):
        # Base request URL
        url = "http://api.opensignal.com/v2/networkstats.json?"

        # Append parameters
        url += "lat="
        url += str(latitude)
        url += "&lng="
        url += str(longitude)
        url += "&distance="
        url += str(boxsize)
        url += "&json_format="
        url += str(2)
        url += "&apikey="
        url += str(self.apikey)

        currentdate = str(datetime.date.month) + str(datetime.date.day) + str(datetime.date.year)
        outputfilename = "CapitalsCellularData/" + str(country) + str("_") + str(capital) + str("_") + str(n) + ".json"

        self.countries.append(country)
        self.capitals.append(capital)
        self.latitude.append(latitude)
        self.longitude.append(longitude)

        # Remove any spaces in the output file name
        outputfilename = outputfilename.replace(' ', '')

        # Send request
        # request = urllib2.request.Request(url)
        # with urllib2.request.urlopen(request) as response:
        response = urllib2.urlopen(url)
        result = json.loads(response.read().decode('utf-8'))

        # Save json data to file
        with open(outputfilename, 'w') as outputfile:
            json.dump(result, outputfile)

        return outputfilename

    def queuejsonfiles(self):
        # Loop through collection of json files (generated as output from api requests)
        for i in range(0,len(self.jsonfilenames)):
            self.parsejson(self.jsonfilenames, self.countries, self.capitals)

    def parsejson(self, jsonfilenames, countries, capitals):
        # Initialize collections
        countries_json = []
        capitals_json = []
        parent_network_name_json = []
        parent_network_id_json = []
        network_name_json = []
        network_id_json = []
        network_type_json = []
        reliability_json = []
        avg_rssi_db_json = []
        avg_rssi_asu_json = []
        sample_size_rssi_json = []
        ping_time_json = []
        upload_speed_json = []
        download_speed_json = []
        lat = []
        lng = []

        # Process JSON files one at a time
        for i in range(0, len(jsonfilenames)):
            country = countries[i]
            capital = capitals[i]
            latitude = self.latitude[i]
            longitude = self.longitude[i]
            jsonfilename = jsonfilenames[i]

            # Open the JSON file
            data = open(jsonfilename).read()
            jsondata = json.loads(data)

            if "networkRank" in jsondata:
                # Loop through all network results
                numresults = len(jsondata["networkRank"])

                for n in range(0, numresults):
                    network = jsondata["networkRank"][n]

                    # Get parent network details
                    parentnetworkname = network["networkName"]
                    parentnetworkid = network["networkId"]

                    networktypes = ["type2G", "type3G", "type4G"]

                    # Get network info at all levels (2g, 3g, 4g)
                    for t in range(0, len(networktypes)):
                        if networktypes[t] in network:
                            networkg = network[networktypes[t]]

                            networkname = ""
                            networkid = ""
                            networktype = ""
                            reliability = ""
                            averagerssidb = ""
                            averagerssiasu = ""
                            samplesizerssi = ""
                            pingtime = ""
                            uploadspeed = ""
                            downloadspeed = ""

                            # Get network details
                            if "networkName" in networkg:
                                networkname = networkg["networkName"]
                            if "networkId" in networkg:
                                networkid = networkg["networkId"]
                            if "networkType" in networkg:
                                networktype = networkg["networkType"]
                            if "reliability" in networkg:
                                reliability = networkg["reliability"]
                            if "averageRssiDb" in networkg:
                                averagerssidb = networkg["averageRssiDb"]
                            if "averageRssiAsu" in networkg:
                                averagerssiasu = networkg["averageRssiAsu"]
                            if "sampleSizeRSSI" in networkg:
                                samplesizerssi = networkg["sampleSizeRSSI"]

                            # 4G variation
                            if "averageRsrpDb" in networkg:
                                averagerssidb = networkg["averageRsrpDb"]
                            if "averageRsrpAsu" in networkg:
                                averagerssiasu = networkg["averageRsrpAsu"]
                            if "sampleSizeRSRP" in networkg:
                                samplesizerssi = networkg["sampleSizeRSRP"]

                            if "pingTime" in networkg:
                                pingtime = networkg["pingTime"]
                            if "uploadSpeed" in networkg:
                                uploadspeed = networkg["uploadSpeed"]
                            if "downloadSpeed" in networkg:
                                downloadspeed = networkg["downloadSpeed"]

                            # Append results
                            countries_json.append(country)
                            capitals_json.append(capital)
                            parent_network_name_json.append(parentnetworkname)
                            parent_network_id_json.append(parentnetworkid)
                            network_name_json.append(networkname)
                            network_id_json.append(networkid)
                            network_type_json.append(networktype)
                            reliability_json.append(reliability)
                            avg_rssi_db_json.append(averagerssidb)
                            avg_rssi_asu_json.append(averagerssiasu)
                            sample_size_rssi_json.append(samplesizerssi)
                            ping_time_json.append(pingtime)
                            upload_speed_json.append(uploadspeed)
                            download_speed_json.append(downloadspeed)
                            lat.append(latitude)
                            lng.append(longitude)

        if network_type_json is not None:
            # Write data to Excel
            self.writesheetdata(countries_json, capitals_json, parent_network_name_json, parent_network_id_json,
                            network_name_json, network_id_json, network_type_json, reliability_json,
                            avg_rssi_db_json, avg_rssi_asu_json, sample_size_rssi_json, ping_time_json,
                            upload_speed_json, download_speed_json, lat, lng)

    def writesheetdata(self, countries, capitals, parentnetworkname, parentnetworkid, networkname, networkid,
                       networktype, reliability, avgrssidb, avgrssiasu, samplesize, pingtime, uploadspeed,
                       downloadspeed, lat, lng):
        # Open the current workbook
        outputname = "CapitalsCellularData/CapitalsCellularData.xls"
        workbook = xlrd.open_workbook(outputname)
        unedited_sheet = workbook.sheet_by_name('SignalData')
        row_num = unedited_sheet.nrows
        row = row_num

        # Copy for writing purposes
        wb = copy(workbook)
        sheet = wb.get_sheet(0)

        if row_num == 0:
            # Add headers
            sheet.write(0, 0, "Country")
            sheet.write(0, 1, "Capital")
            sheet.write(0, 2, "Parent Network Name")
            sheet.write(0, 3, "Parent Network ID")
            sheet.write(0, 4, "Network Name")
            sheet.write(0, 5, "Network ID")
            sheet.write(0, 6, "Network Type")
            sheet.write(0, 7, "Reliability")
            sheet.write(0, 8, "Average Rssi Db")
            sheet.write(0, 9, "Average Rssi Asu")
            sheet.write(0, 10, "Sample Size Rssi")
            sheet.write(0, 11, "Ping Time")
            sheet.write(0, 12, "Upload Speed")
            sheet.write(0, 13, "Download Speed")
            sheet.write(0, 14, "Latitude")
            sheet.write(0, 15, "Longitude")
            row = 1

        # Add rows of values
        for i in range(0, len(countries)):
            sheet.write(row, 0, countries[i])
            sheet.write(row, 1, capitals[i])
            sheet.write(row, 2, parentnetworkname[i])
            sheet.write(row, 3, parentnetworkid[i])
            sheet.write(row, 4, networkname[i])
            sheet.write(row, 5, networkid[i])
            sheet.write(row, 6, networktype[i])
            sheet.write(row, 7, reliability[i])
            sheet.write(row, 8, avgrssidb[i])
            sheet.write(row, 9, avgrssiasu[i])
            sheet.write(row, 10, samplesize[i])
            sheet.write(row, 11, pingtime[i])
            sheet.write(row, 12, uploadspeed[i])
            sheet.write(row, 13, downloadspeed[i])
            sheet.write(row, 14, str(lat[i]))
            sheet.write(row, 15, str(lng[i]))
            row += 1

        # Save the worksheet
        wb.save(outputname)

if __name__ == "__main__":
    apikey = sys.argv[1]
    cd = CapitalsCellularData(apikey)
    cd.queueapirequests()
    cd.queuejsonfiles()
