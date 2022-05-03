# Gerund Study

University of Rochester, LIN 250 Course Research Project

> Note: For those who cannot setup the anaconda environment using the `environment.yml` file (which seems to be a lot of people), please use the following command:
>
> ```bash
> conda create -n LIN250 -c defaults -c stanfordnlp -c conda-forge python=3.8 autopep8 stanza nltk pandas
> ```

## Setup

To acquire the necessary Python packages to reproduce our results, you can use either `conda` or `pip`.

### Install Using `conda`

After activating the desired virtual environment ([Anaconda's official documentation on virtual environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)), the necessary packages can be installed using the following command.

```bash
$ conda install -c defaults -c stanfordnlp -c conda-forge python=3.8 pandas stanza nltk
```

### Install Using `pip`

We again recommend the use of virtual environment ([Python's official documentation on `venv`](https://docs.python.org/3/library/venv.html)) to avoid any configuration conflicts. After activating the desired virtual environment, the necessary packages can be installed using the following command.

```bash
$ pip install pandas stanza nltk
```

> Note: Some systems may default `pip` command to that of Python 2, which will cause the installation to fail. In such a case, switching to `pip3` typically resolves the issue.

### Download `stanza` Data

Our implementation makes use of the `stanza` package. As part of the installation process, you need to download some data files by first opening a python REPL (accessible by typing the `python` or `python3` command once the desired virtual environment is activated) and type the following.

```python
>>> import stanza
>>> stanza.download('en')
```

### Download `nltk` Data

Our implementation makes use of the Punkt sentence tokenizer provided by the `nltk` package. In order for the tokenizer to function, you need to first download some data files using the following command.

```bash
$ python -m nltk.downloader punkt
```

## Usage

We divided the dataframe generation process into three stages: parse, extract, and classify. To carry out each of the stages, follow the following instructions, assuming the desired virtual environment is activated.

### Parse Stage

During this stage, texts from the COCA corpus are parsed using `stanza` with the results stored as Python pickle files. You can generate the parses for texts contained within `filename` by using the following command.

```bash
$ python parse.py [filename]
```

You may optionally supply the parameter `--directory` to tell `parse.py` to store all the generated Python pickle files under a specific `directory`.

```bash
$ python parse.py --directory [directory] [filename]
```

After running `parse.py`, you should obtain a collection of Python pickle files (i.e., suffix `.pkl`) with names set to the COCA text ID (e.g., `4000568.pkl`).

> Note: You may only supply one `filename` at a time.

### Extract Stage

During this stage, parses of COCA texts are examined and potentially gerunds are extracted using our proposed patterns (see paper). The gerund candidates are also labeled with a "recommendation" for whether it should be excluded (e.g., words such as "king"). The specific recommendations for words that we have devised can be found in `exclude.csv`. To extract the potential gerunds from the parse contained in `filename`, use the following command.

```bash
$ python extract.py exclude.csv [filename]
```

You may optionally supply the parameter `--output` to tell `extract.py` to store the resulting CSV file in a particular `output`.

```bash
$ python extract.py --output [output] exclude.csv [filename]
```

After running `extract.py`, you should obtain a CSV file containing the gerund candidates. This file will be used by the classify stage.

> NOte: You may supply multiple `filename`s (e.g., UNIX wildcard `*.pkl` works).
