# CoronaWhy Risk Factors Task Force


<p align="left">
<img width=15% src="https://uploads-ssl.webflow.com/5e729ef3ef0f906b804d4f27/5e77e9db1ede36135bbb1927_logo%203%402x.png" alt=“CoronaWhy” />

<i>A worldwide effort by volunteers to fight Coronavirus (COVID-19)</i>
</p>


![CI](https://github.com/CoronaWhy/task-risk/workflows/CI/badge.svg)


Understanding the COVID-19 Risk Factors

- Documentation: https://corona-task-risk.readthedocs.io/en/latest/
- Task Homepage: https://github.com/CoronaWhy/task-risk
- Main Coronawhy Homepage: https://www.coronawhy.org/


## About CoronaWhy

CoronaWhy is a crowd-sourced team of over 350 engineers, researchers, project managers, and all sorts of other professionals with diverse backgrounds who joined forces to tackle the greatest global problem of today--understanding and conquering the COVID-19 pandemic. This team formed in response to the Kaggle CORD-19 competition to synthesize the flood of new knowledge being generated every day about COVID-19. The goal for the organization is inform policy makers and care providers about how to combat this virus with knowledge from the latest research at their disposal.


## About CoronaWhy Risk Factors Task

This task is oriented towards gathering information and drawing conclusions
about the factors involved in Coronavirus disease. Risk factors include:
aging, gender, pre-existing diseases and a big etcetera.

Progress of this task can be tracked [here](link)

## About CoronaWhy Risk Factors Task Force

*List of collaborators (pending)*

# Install

Also, although it is not strictly required, the usage of a [virtualenv](https://virtualenv.pypa.io/en/latest/)
is highly recommended in order to avoid interfering with other software installed in the system.

These are the minimum commands needed to create a virtualenv using python3.6 for **task-risk**:

```bash
pip install virtualenv
virtualenv -p $(which python3.6) task-risk
```

Afterwards, you have to execute this command to activate the virtualenv:

```bash
source task-risk/bin/activate
```

Remember to execute it every time you start a new console to work on **task-risk**!


With your virtualenv activated, you can clone the repository and install it from
source by running `make install-deveop` on the `stable` branch:

```bash
git clone git@github.com:CoronaWhy/task-risk.git
cd task-risk
git checkout stable
make install-develop
```

Now you have the code installed on your local system, and you are ready to help us with your contribution, but first, please have a look at the [Contributing Guide](https://CoronaWhy.github.io/task-risk/contributing.html).

# Notes

A note on Notebooks: Notebooks are useful for fast prototyping, but as code
base grows, it becomes difficult to maintain, so, in order to work together,
you are encouraged to upload code that integrates with the existing code base
rather than a notebook. Don't reinvent the wheel, if you code a utility
function to load files or clean sentences, think if this can be useful
 to others, in such case, integrate it with the actual code base instead of adding
 it to your main script. Also, check that no one has done it before.

