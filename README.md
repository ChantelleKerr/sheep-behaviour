# sheep-behaviour

## Create Virtual Environment

```
python3 -m venv venv
```

or

```
python -m venv venv
```

## Activate Virtual Environment

macOS

```
source venv/bin/activate
```

windows

```
venv\Scripts\activate
```

## Install requirements

```
pip install -r requirements.txt
```

## Run Program

```
python3 main.py or python main.py
```
## Run test_data_analysis_plot.py

```
import test_data_analysis_plot
t = test_data_analysis_plot.Testdata_analysis_plot()
t.setUp()
t.test_prepare_data()
t.test_function()
```
