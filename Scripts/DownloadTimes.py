import sys
import xlrd
import xlwt


class DownloadTimes:
    def __init__(self, file):
        self.filename = file
        self.country_list = []
        self.ping_list = []  # in ms, multiply by 0.001 to get seconds
        self.download_list = []  # in kbps, multiply by 0.001 to get mbps, by 0.000125 to get MBps
        self.network_list = []

        # song, fb per day, 5 minute youtube video, facebook over month, low quality netflix for 1 hour,
        # high quality netflix for 1 hour
        # self.datasizes = ['4MB', '14.43MB', '30MB', '433MB', '0.7GB', '3GB']
        self.datasizes = [4, 14.43, 30, 433, 700, 3000]  # in MB

    def readsheet(self):
        # Open the Excel worksheet and pass to a parsing function
        workbook = xlrd.open_workbook(self.filename)
        sheet = workbook.sheet_by_name('DownloadFile')

        # Start at row 1 to skip header row
        row = 1

        # Process each row one by one
        while row < sheet.nrows:
            country = sheet.cell(row, 0).value
            ping = sheet.cell(row, 1).value
            download = sheet.cell(row, 2).value
            network = sheet.cell(row, 3).value

            # Convert to seconds, MBps instead of ms, kbps
            ping *= 0.001
            download *= 0.000125

            self.country_list.append(country)
            self.ping_list.append(ping)
            self.download_list.append(download)
            self.network_list.append(network)

            row += 1

        # After all data has been read, compute points and save to Excel

    def writepoints(self):
        # Create a new workbook
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("DownloadTimes-TableauData")

        # Write headers
        sheet.write(0, 0, "Country")
        sheet.write(0, 1, "Network Type")
        sheet.write(0, 2, "Time (minutes)")
        sheet.write(0, 3, "Download Size (MB)")

        row = 1

        # Add rows of values
        for i in range(0, len(self.country_list)):
            # Add (0,0)
            sheet.write(row, 0, self.country_list[i])
            sheet.write(row, 1, self.network_list[i])
            sheet.write(row, 2, 0)
            sheet.write(row, 3, 0)
            row += 1

            # Add (ping time, 0)
            ping_in_minutes = self.ping_list[i] * 0.0166667
            sheet.write(row, 0, self.country_list[i])
            sheet.write(row, 1, self.network_list[i])
            sheet.write(row, 2, ping_in_minutes)
            sheet.write(row, 3, 0)
            row += 1

            # Add (time, data size) for each specified size
            for j in range(0, len(self.datasizes)):
                # Downloadsize = (time after ping)*downloadspeed
                # time after ping = (downloadsize) / downloadspeed
                time_after_ping = self.datasizes[j] / self.download_list[i]

                # total time = time after ping + ping time
                total_time = time_after_ping + self.ping_list[i]
                total_time_in_min = total_time * 0.0166667

                # Add (total time, download size)
                sheet.write(row, 0, self.country_list[i])
                sheet.write(row, 1, self.network_list[i])
                sheet.write(row, 2, total_time_in_min)
                sheet.write(row, 3, self.datasizes[j])

                row += 1

        # Save the worksheet
        outputname = "Download Times.xls"
        workbook.save(outputname)


if __name__ == "__main__":
    # Get the file name with Excel data
    filename = sys.argv[1]

    dt = DownloadTimes(filename)
    dt.readsheet()
    dt.writepoints()
