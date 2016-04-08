import sys
import xlrd
import xlwt

class WorldBankTimeSeries:
    def __init__(self, file, name, code):
        # Initialize class variables
        self.seriesname = name
        self.seriescode = code

        self.country = []
        self.countrycode = []
        self.year = []
        self.value = []

        # Open the Excel worksheet and pass to a parsing function
        workbook = xlrd.open_workbook(file)
        worksheet = workbook.sheet_by_name('Data')
        self.readsheet(worksheet)

    def readsheet(self, sheet):
        print("Reading rows")

        # Read each row
        row = 1
        while row < sheet.nrows:
            # Only keep rows that match this series (in 2nd column)
            currentseries = sheet.cell(row,3).value

            if str(currentseries) != str(self.seriescode):
                row += 1
                continue

            # Get country name
            countryname = sheet.cell(row,0).value

            # Get country code
            countrycode = sheet.cell(row,1).value

            # Loop through years
            col = 4
            while col < sheet.ncols:
                yearheader = sheet.cell(0, col).value
                seriesyear = "01/01/" + str(yearheader.split(' ')[0])
                seriesvalue = sheet.cell(row, col).value

                if seriesvalue != "..":
                    # Add an entry for (country, countrycode, year, value)
                    self.country.append(countryname)
                    self.countrycode.append(countrycode)
                    self.year.append(seriesyear)
                    self.value.append(seriesvalue)

                    print("Added entry for " + countryname + " in year " + seriesyear)

                # Go to the next column
                col += 1

            row += 1

    def writesheet(self):
        # Create a new workbook
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("TableauData")

        # Add headers
        sheet.write(0,0,"Country Name")
        sheet.write(0,1,"Country Code")
        sheet.write(0,2,"Year")
        sheet.write(0,3,self.seriesname)

        row = 1

        # Add rows of values
        for i in range(0,len(self.country)):
            sheet.write(row,0,self.country[i])
            sheet.write(row,1,self.countrycode[i]);
            sheet.write(row,2,self.year[i]);
            sheet.write(row,3,self.value[i]);
            row += 1

        # Save the worksheet
        outputname = str(self.seriescode) + '.xls'
        workbook.save(outputname)

if __name__ == "__main__":
    # Get the file name with Excel data
    filename = sys.argv[1]
    seriesname = sys.argv[2]
    seriescode = sys.argv[3]

    timeseries = WorldBankTimeSeries(filename, seriesname, seriescode)
    timeseries.writesheet()