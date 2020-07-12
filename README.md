# DPV_Toolkit
This contains tools for analysis of thermal spray data. Namely, data from the DPV 2000 and ReliaCoat ICP/ECP. Can be used by anyone, but I made it for that *special someone...*

The Toolkit has several tabs:
1. Distributions
2. Noise Removal
3. Data Compiler
4. Modeling

These are ordered to accomodate the existing process map workflow for thermal spray. First, you observe the distributions in your newly acquired data. Then, you perform noise removal. After several runs, you can compile your data and then look at the effect of process conditions on Temperature and Speed.
## Distributions

### This shows the distributions of Temperature, Speed, and Diameter for a given file. 
Simply choose a file, and take a peek.

## Noise Removal

### Implements the HDBscan algorithm to recognize and remove noise. 

After you pick your file, use the sliders to fine-tune the algorithm. 

A complete description of this algorithm can be found at https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html, but I'll explain what the sliders do in layman's terms.

* Epsilon: Sets density threshold above which clusters won't be split up. If you have weird gaps in your filtered data, increase it (corresponds to `cluster_selection_epsilon`)
* Noisiness: The minimum number of points allowed in a cluster (corresponds to `min_cluster_size`)
* Error Size: "Conservativeness" of clustering - sets a harder cutoff for cluster edges. (corresponds to `min_samples`)

As you can guess, these parameters often go against each other, but with practice you'll have an intuitive understanding of what they do.

> Note that (as of version 0.6.9), we only calculate the distance on Temperature and Speed - further investigation is need to optimize the distance function.

## Data Compiler

### Combines many data files into one, including important information given by filename (*creds to Eugenio Garcia-Granados for the gorgeous filenames*).

In the filenames of your DPV files, **you should have consistent filenames that give information about the corresponding condition.** 

For instance, if you used 40 lpm Argon, 4 lpm Hydrogen, 500A current, on the Sinplex gun, on the 12th of July in 2020, your .prt filename might look something like this: 

*Ar40_H4_500A_Sinplex_071220.prt*. 

In fact, you're so beautifully organized that you use that same format for all your data files, even across projects: 

*Argon_Hydrogen_Current_Sinplex_Date*.

Using the Toolkit, you can automatically get these relevant data points by inputting this into the "Filename Configuration" box:

*(Argon:Ar\*)(Hydrogen:_H\*_)(Current:_\*A_)(Gun:Sinplex)(Gun:F4)(Date:_\*.)*

Inside each parentheses, you put the name of the column you want to add, followed by a colon, then the stuff nearby the value you want to record. For numberical values, replace the entire number with an asterisk. 

For example, the Toolkit will look for the value for the *Argon* column after *Ar*, and the value for the *Hydrogen* column in between *_H* and *_*.

Notice that in the filename configuration shown above there are two searcable items for the *Gun* column. For values that choose a set of words, you have to put in every possible option for that column. It won't assign a value for the associated column if it doesn't find a match, so we won't have to worry about the F4 search for this filename.
Multiple matches for the same column can produce errors - the Toolkit reads the searches left-to-right, so you'll be stuck with the rightmost search term if it finds a match. The easiest way to prevent this is smart filenaming. 


## Modeling

### Displays means/stds of Temperature and Speed, categorized by chosen columns.

This is the last stage of the process map process - looking at your chosen variables' effects on temperature and speed.

After you choose a data file, the left populates with the names of the columns in your file. Choose the names yuo want to separate by (hold shift to select multiple), and watch your hard work appear before you. 
