
# wrfout_extractor 

wrfout_extractor combines two extraction pipelines. `run_slicer.py` is for slicing a subset in the orginal wrfout , and `run_extractor.py` is for extracting desired 2d or 3d variables into csv files.

### Install

Please install python3 using the latest Anaconda3 distribution. [Anaconda3](https://www.anaconda.com/products/individual) with python3.8 has been fully tested, lower version of python3 may also work (without testing).

Now, we recommend to create a new environment in Anaconda and install the `requirements.txt`:

```bash
conda create -n test_wrfextractor python=3.8
conda activate test_wrfextractor
pip install -r requirements.txt
```

### Usage

Setup necessary parameters in `./conf/config.ini`, and run the slicing pipeline first if you do not have subset data.

```bash
python3 run_slicer.py
```

If everything goes smoothly, you would expect to see subset files in the folder as you configured in `[OUTPUT][slicer_output_root]`.

Next, just configure the location and execute ` python3 run_extractor.py` pipeline to archive the variables at a specific site. 
You would expect to see csv files in your specified output folder named like `var2d_S2040060100E2040060102_lat22.5_lon113.95.csv` and `var2d_S2040060100E2040060102_lat22.5_lon113.95.csv`, which stores 2d and 3d variables you prescried in `config.ini`, respectively.

### Input Files

#### config.ini
`./conf/config.ini`: Configure file for the model. You may set IO options and slicer/extractor details in this file.

### Module Files

#### run_slicer.py
`./run_slicer.py`: Main script for the slicer pipeline to get wrfout subset files.

#### run_extractor.py
`./run_extractor.py`: Main script to extract desired variables from subset files. 

#### lib

* `./lib/cfgparser.py`: Module file containing read/write funcs of the `config.ini`

* `./lib/wrf_extractor.py`: Class template to construct an extractor obj

* `./lib/wrf_slicer.py`: Class template to construct a slicer obj

* `./lib/time_manager.py`: Class template to construct time manager obj

* `./lib/utils.py`: Commonly used utilities.

**Any question, please contact Zhenning LI (zhenningli91@gmail.com)**
