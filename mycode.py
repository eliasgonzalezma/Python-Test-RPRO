# If executes from local python Kernel
import sys
sys.path.append('./python_env/lib/python3.6/site-packages')

# Import libraries for general use
from unidecode import unidecode # Library to parse format
from bs4 import BeautifulSoup # Library to scripting in HTML
import numpy # Library for math function
import requests # Library for request to a website

# This function returns an array that contains the percentage of the population.
def get_population_percentage(population_array):
    # Get the percentage for each item
    population_percentage = []
    for item in population_array:
        population_percentage.append(item/numpy.sum(population_array)*100)
    
    return numpy.array(population_percentage)

# This function create the output file
def create_output_file(head, data, population_percentage):
    # Concatenate all data Head + Rows + New Colum (percentage)
    result = numpy.concatenate((data, population_percentage.T),axis=1)
    result = numpy.concatenate((head, result), axis=0)
    result = result.astype('str')
    # Save the result in to a csv file 
    return numpy.savetxt('Organización territorial de Chile.csv', result, delimiter=",",fmt="%s")

def get_data():
    try:
        website_text = requests.get('https://es.wikipedia.org/wiki/Chile').text
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    
    # Parse all data in to HTML format
    soup = BeautifulSoup(website_text,'html.parser')
    # Get the table 'Orgazniación ....'
    territory_table = soup.find('table',{'class':'wikitable col1izq col2der col3der col4der col5der col6izq'})
    # Get all data from table - tag <td>
    if territory_table:
        list_td = territory_table.find_all('td')
        # Data Frames
        head = ['Región', 'Población', 'Superficie', 'Densidad', 'Capital', 'Porcentaje']
        data = []
        row = []
        population = []

        for cell in list_td:
            if(list_td.index(cell)==5): # Delete de 'Mapa administrativo' cell
                continue
            if cell.find_all('a'): # Get text for columm that contains an '<a>' tag.
                a = cell.find_all('a')[0]
                row.append(a.get_text())
            else:
                # For numbers parse into american float format
                cell = unidecode(cell.get_text()).replace(" ","").replace(",",".")
                # Delete <sub> tag info
                if "(" in cell:
                    cell = cell.split("(")[0]
                # Add cell to the row's table
                row.append(float(cell))
                # Save the population data to calculate percentage
                if(len(row) == 2):
                    population.append(row[1])
            # Add row to the table
            if len(row) == 5:
                data.append(row)
                row = []  
        return numpy.array([head]), numpy.array(data), numpy.array([population])
    else:
        print("Table not found.")
        return sys.exit(1)

if __name__ == '__main__':
    head,data,population = get_data()
    population_percentage = get_population_percentage(population)
    create_output_file(head,data,population_percentage)
    