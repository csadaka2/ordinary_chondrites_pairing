# Pairing of ordinary chondrites

This project is a model using a probabilistic approach to estimate the pairing between ordianry chondrites based on the model developepd by Hutzler et al. (2016).
This model can be used for a quick pairing assessment of a large number of meteorites.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Example notebook](#examplenb)
- [Contributing](#contributing)
- [References](#references)
- [License](#license)
- [Contact](#contact)

## Introduction
Meteoroids often undergo fragmentation during their atmospheric entry, resulting in the fall of multiple stones.Moreover, individual stones may fragment on the Earth’s surface due to alteration processes. Consequently, multiple fragments from the same meteorite are often found scattered within a geographical area called strewnfield.
In dense collection areas, pairing these fragments is challenging and time-consuming in terms of data acquisition. However, pairing assessment remains extremely important in any study involving a large meteorite collection, as it can reduce statistical bias and prevent duplicate laboratory analyses (Scott, 1984). Pairing is crucial mostly for equilibrated ordinary chondrites, which are the most abundant types of meteorites, and pairing assessment could lead to a staggering different possible pairs, making it unrealistic to check each pair of meteorites individually.
For these reasons, we decided to tackle the pairing problem using a probability approach with a model similar to that developed by Benoit et al. (2000) and Hutzler et al. (2016). The model can be modified accordingly to suit other collections and search areas. Parameters can be easily modified, removed and/or added.

Among the main criteria used in the literature for ordinary chondrites pairing (Benoit et al., 2000; Schlüter et al., 2002), our pairing code incorporates the petrographic type (Van Schmus & Wood, 1967), the weathering grade (Wlotzka, 1993), the fayalite content of olivine, the ferrosilite content of low-Ca pyroxene, the magnetic susceptibility, and the distance between stones. 
We consider that two meteorites from different groups cannot be paired, so we separated H, L, and LL chondrites. We also assume that unequilibrated ordinary chondrites of type 3 cannot be paired with equilibrated chondrites. 
The pairing code calculates a factor P which reflects the likelihood of two meteorites being paired, using the following equation:
P = (Πipiwi ) 1 / ∑wi

Here, *pi* is the probability of pairing for two meteorites for the given criterion i, and *wi* is the weight assigned for each criterion i. 

Given that some criteria are more robust than others, a different weight was assigned to each. Magnetic susceptibility, petrographic type, fayalite content of olivine, and ferrosilite content of low-Ca pyroxene were given a weight of 2, while distance, and weathering grade were given a weight of 1. Missing criteria were assigned a weight of zero for mathematical homogeneity.

P is not a probability hence we use the term factor for mathematical correctness. To invalidate the pairing between two meteorites, it only takes one single criterion being invalid. For this, the weighted geometric mean is a suitable approach for combining probabilities from different criteria when each criterion has a different level of importance (weight). If any of the criteria suggests a very low probability (close to zero), it will significantly impact the overall pairing factor P, potentially invalidating the pairing. In the weighted geometric mean, each value is raised to the power of its assigned weight. It provides a value that involves the whole dataset, giving more weight to the criteria judged more important.
Additionally, each criterion was assigned a probability function. For the weathering grade, petrographic type, and inter-meteorite distance, we applied a discrete function. Magnetic susceptibility, fayalite content, and ferrosilite content probability functions follow a Gaussian distribution. Therefore, for these properties, the factor pi can be computed as the probability that two measurements of a given properties for two meteorites (xA and xB) are from the Gaussian distribution with a standard deviation 𝜎 and a mean value of (xA+xB)/2:

p=e^(-[(xA-xB)/2σ]^2 )

The code returns a symmetrical matrix displaying the pairing factors. These estimates remain qualitative as pairing can never be confirmed with absolute certainty in very dense collection areas, even by checking individual pairs under a microscope. Additional criteria could be used for more accurate diagnostic of this pairing code: shock stage, presence or absence of specific petrographic features (polycrystallinity of troilite, presence of shock veins, presence of melt pockets, …)


## Installation

To get started with this project, follow these steps to set up your environment and install the necessary dependencies.

### Prerequisites

Make sure you have Python installed. You can download it from [python.org](https://www.python.org/).

### Steps

1. **Clone the repository**:

    ```sh
    git clone https://github.com/csadaka2/ordinary_chondrites_pairing
    ```

2. **Navigate to the project directory**:

    ```sh
    cd ordinary_chondrites_pairing
    ```

3. **Create a virtual environment** (optional but recommended):

    ```sh
    python -m venv venv
    ```

4. **Activate the virtual environment**:

    On Windows:
    ```sh
    venv\Scripts\activate
    ```

    On macOS and Linux:
    ```sh
    source venv/bin/activate
    ```

5. **Install the required dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

### requirements.txt

Ensure you have a `requirements.txt` [Requirements](https://github.com/csadaka2/ordinary_chondrites_pairing/blob/main/requirements.txt) file in the root directory of your project that includes **numpy** and **pandas**



## Usage
To use the Ordinary Chondrites Pairing Model, follow these steps:

1. **Import Dependencies**
2. **Read Data and Create Meteorite Instances**: Read data from a CSV file or any other format into a DataFrame and create instances of the Meteorite class.
3. **Calculate Pairing Probabilities: Generate all combinations of length 2 from the list of Meteorite instances, calculate pairing probabilities for each combination, and update a DataFrame to store the probabilities.**
4. **Estimate Meteorites After Pairing:Extract values above the diagonal of the pairing matrix, calculate the mean of the pairing probabilities, and estimate the number of meteorites after pairing.**


   ```python

   import pandas as pd
   import numpy as np
   import itertools

    # Read Data
    data_test = pd.read_csv('meteorite_data.csv', delimiter=';')
    
    # Create a list to store instances of the Meteorite class
    meteorites_list_test = []
    
    # Iterate over each row in the DataFrame to create Meteorite instances
    for index, row in data_test.iterrows():
        meteorites_list_test.append(
            Meteorite(
                name=row["Name"],
                position=(row["Latitude"], row["Longitude"]),
                petrographic_type=row["Petrographic Type"],
                weathering_grade=row["Weathering Grade"],
                fa_content=row["Fayalite Content"],
                fs_content=row["Ferrosilite Content"],
                mag_sus=row["Magnetic Susceptibility"]
            )
        )
    
    
    # Generate all combinations of length 2 from meteorites_list_test
    combinations_test = list(itertools.combinations(meteorites_list_test, 2))
    
    # Create a DataFrame to store pairing probabilities
    df_pairing_test = pd.DataFrame(index=meteorites_list_test, columns=meteorites_list_test)
    
    # Convert index and columns to strings
    df_pairing_test.index = df_pairing_test.index.astype(str)
    df_pairing_test.columns = df_pairing_test.columns.astype(str)
    
    # Calculate pairing probabilities for each combination and update the DataFrame
    for combination in combinations_test:
        pairing_proba = calculate_pairing_probability(met_1=combination[0], met_2=combination[1])
        df_pairing_test.at[str(combination[0]), str(combination[1])] = pairing_proba
        df_pairing_test.at[str(combination[1]), str(combination[0])] = pairing_proba
    
    
    # Extract values above the diagonal of the pairing matrix
    pairing_values_test = df_pairing_test.values
    above_diagonal_values_test = pairing_values_test[np.triu_indices_from(pairing_values_test, k=1)]
    
    # Calculate the mean of the pairing probabilities above the diagonal
    mean_probability_test = np.mean(above_diagonal_values_test)
    
    # Print the mean probability and estimated number of meteorites after pairing
    print("Mean Probability of Pairing: {:.2f}".format(mean_probability_test))
    print("Number of H Chondrites Before Pairing: {}".format(len(data_test)))
    print("Estimated Number of H Chondrites After Pairing: {:.0f}".format(len(data_test) * (1 - mean_probability_test)))
    ```


## Example notebook
Link to an example notebook [Test](https://github.com/csadaka2/ordinary_chondrites_pairing/blob/main/pairing_nb.ipynb)

## Contributing
**Experiment and Customize**:
Feel free to experiment with different parameters, adjust weights, or customize the model according to your specific research needs. 
You can modify the code to incorporate additional criteria or refine existing ones.

## References
- Benoit, P H, D. W. G. Sears, J.M.C. Akridge, P. A. Bland, F.J. Berry, and C.T. Pillinger. 2000. “The Non-Trivial Problem of Meteorite Pairing.” Meteoritics & Planetary Science 35 (2). Wiley-Blackwell: 393–417. doi: 10.1111/j.1945-5100.2000.tb01785.x.
- Hutzler, A., J. Gattacceca, P. Rochette, R. Braucher, B. Carro, E. Christensen, C. Cournede, et al. 2016. “Description of a Very Dense Meteorite Collection Area in Western Atacama: Insight into the Long-Term Composition of the Meteorite Flux to Earth.” Meteoritics & Planetary Science 51 (3). Wiley-Blackwell: 468–82. doi: 10.1111/maps.12607.
- Schlüter, J. , L. Schultz, F. Thiedig, B. O. Al‐Mahdi, and A. E. Abu Aghreb. 2002. “The Dar al Gani Meteorite Field (Libyan Sahara): Geological Setting, Pairing of Meteorites, and Recovery Density.” Meteoritics & Planetary Science 37 (8). Wiley-Blackwell: 1079–93. doi: 10.1111/j.1945-5100.2002.tb00879.x.
- Van Schmus, W. R., and J. A. Wood. 1967. “A Chemical-Petrologic Classification for the Chondritic Meteorites.” Geochimica et Cosmochimica Acta 31 (5). Elsevier BV: 747–65. doi:https://doi.org/10.1016/s0016-7037(67)80030-9.
- Wlotzka F. 1993. A weathering scale for the ordinary chondrites (abstract). Meteoritics 28:460. 


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
Feel free to reach out with any questions or feedback:
- Carine Sadaka : sadaka@cerege.fr or carinesadaka123@gmail.com
- Pierre Sempéré : pierre.sempere.01@gmail.com

