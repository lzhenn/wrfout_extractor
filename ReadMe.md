
# wrfout_extractor 

wrfout_extractor combines two extraction pipelines. `run_slicer.py` is for slicing a subset in the orginal wrfout , and `run_extractor.py` is for extracting desired 2d or 3d variables into csv files.

### Install

Please install python3 using the latest Anaconda3 distribution. [Anaconda3](https://www.anaconda.com/products/individual) with python3.8 has been fully tested, lower version of python3 may also work (without testing).

Now, we recommend to create a new environment in Anaconda and install the `requirements.txt`:

```bash
conda create -n test_prism python=3.8
conda activate test_prism
pip install -r requirements.txt
```

### Usage

Setup necessary parameters in `./conf/config.ini`, and run the slicing pipeline first if you do not have subset data.

```bash
python3 run_slicer.py
```

If things go smothly, you would expect to see subset files as you configured in `[OUTPUT][slicer_output_root]`.

And then run extractor pipeline to get the variables at a specific location.


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
