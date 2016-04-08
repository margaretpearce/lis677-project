import sys
import xlrd
import xlwt
import json
import urllib.request
import time
import datetime


class CellularData:
    def __init__(self, file, key):
        self.apikey = key
        self.filename = file

    def readsheet(self, runmode):
        # Open the Excel worksheet and pass to a parsing function
        workbook = xlrd.open_workbook(self.filename)
        sheet = workbook.sheet_by_name('Capitals')

        jsonfilenames = []
        countries = []
        capitals = []

        # Start at row 1 to skip header row
        row = 1

        # Process each city one by one
        while row < sheet.nrows:
            country = sheet.cell(row, 0).value
            capital = sheet.cell(row, 1).value
            latitude = sheet.cell(row, 2).value
            longitude = sheet.cell(row, 3).value
            boxsize = sheet.cell(row, 7).value

            # Mode 1: Get JSON data
            if runmode == '1':
                # Create API request
                self.sendapirequest(country, capital, latitude, longitude, boxsize)

                # Limit of 5 requests per minute - wait 15 seconds in between each API request
                time.sleep(15)

            # Mode 2: Create Excel spreadsheet version from JSON
            elif runmode == '2':
                outputfilename = str(country) + str("_") + str(capital) + ".json"

                jsonfilenames.append(outputfilename)
                capitals.append(capital)
                countries.append(country)

            row += 1

        # After all JSON data has been collected, parse and write it to Excel
        if runmode == '2':
            self.parsejson(jsonfilenames, countries, capitals)

    def sendapirequest(self, country, capital, latitude, longitude, boxsize):
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
        outputfilename = "CellSignalData/" + currentdate + "/" + str(country) + str("_") + str(capital) + ".json"

        # Send request
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.readall().decode('utf-8'))

            # Save json data to file
            with open(outputfilename, 'w') as outputfile:
                json.dump(result, outputfile)

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

        # Process JSON files one at a time
        for i in range(0, len(jsonfilenames)):
            country = countries[i]
            capital = capitals[i]
            jsonfilename = jsonfilenames[i]

            # Open the JSON file
            data = open(jsonfilename).read()
            jsondata = json.loads(data)

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

        # Write data to Excel
        self.writesheetdata(countries_json, capitals_json, parent_network_name_json, parent_network_id_json,
                            network_name_json, network_id_json, network_type_json, reliability_json,
                            avg_rssi_db_json, avg_rssi_asu_json, sample_size_rssi_json, ping_time_json,
                            upload_speed_json, download_speed_json)

    def writesheetdata(self, countries, capitals, parentnetworkname, parentnetworkid, networkname, networkid,
                       networktype, reliability, avgrssidb, avgrssiasu, samplesize, pingtime, uploadspeed,
                       downloadspeed):
        # Create a new workbook
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("TableauData")

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
            row += 1

        # Save the worksheet
        outputname = "CellularData.xls"
        workbook.save(outputname)


if __name__ == "__main__":
    # Get the file name with Excel data
    filename = sys.argv[1]
    apikey = sys.argv[2]
    mode = sys.argv[3]

    cellulardata = CellularData(filename, apikey)
    cellulardata.readsheet(mode)
