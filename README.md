# Lotto-Manager using Google Cloud Platform

Automates Euro-Millions Lottery Syndicate using Google Cloud Platform (GCP). Cloud functions are used to:

* Web-scrape results and prize breakdown,
* Compute prize won by selected numbers,
* Log results in BigQuery,
* Run dynamic SQL queries on all results to produce summary tables.
* Manager is scheduled to run every week, 9am Saturday.

# Background

Forked [lotto-manager](https://github.com/ghagintonbear/lotto-manager) to solve same problem using:
* GCP [Cloud Functions](https://cloud.google.com/functions) with asynchronous requests.
* GCP GitHub gcloud actions to accomplish [CI/CD](https://cloud.google.com/blog/products/devops-sre/cloud-build-brings-advanced-cicd-capabilities-to-github),
* Store results in [Google BigQuery](https://cloud.google.com/bigquery).
* Dynamically generate SQL queries to produce summary tables.
* Schedule actions with [Cloud PubSub](https://cloud.google.com/pubsub).

# Project Structure

```
.
├── cloud_utils                     # Utility functions shared by cloud functions
├── functions                       # Cloud functions
│   ├── publish_message             # Example structure
│   │   ├── src                     # cloud function source code
│   │   │   ├── main.py             # module to be executed
│   │   │   └── requirements.txt    # cloud function requirements
│   │   └── variables.txt           # variables used by ./scripts/cloud-func-build.yaml
│   ├── run_manager
│   └── run_manager_between
├── manager                         # manager source code, also shared by cloud functions
├── scripts                         # shell scripts used to automate builds
│   ├── cloud-func-build.yaml       # instructions used to build cloud function
│   ├── gcp-github-triggers.sh      # script used to build all cloud function github triggers
│   └── gcp-setup.sh                # script used to create bespoke GCP project
├──tests                            # tests for manager package, ran during each deployment
└── selected_numbers.csv            # Numbers selected by players. Loaded to BigQuery by ./scripts/gcp-setup.sh 
```

# Running lotto-manager-gcp

To interact directly with GCP from your local machine, you will need 
[gcloud](https://cloud.google.com/sdk/docs/quickstart) - Google's Cloud SDK. Alternatively, run all `gcloud` commands 
in GCP terminal. 

Steps below will use GCP terminal.

### Steps

1. Open terminal in GCP and clone your forked `lotto-manager-gcp` repo. 
1. Head to scripts directory and run `sh ./gcp-setup.sh '<branch-ref-suffix>'`. This will create a new GCP project with 
   all the appropriate GCP Service APIs and permissions enabled.
1. Then connect your GCP project to your GitHub repo. You will have to do this step manually via the [GCP console](https://console.cloud.google.com/cloud-build/triggers). 
1. Head back to the terminal and run `sh ./gcp-github-triggers.sh '<branch-ref-suffix>'`. This will create GCP build
   triggers for all cloud functions in the `./functions` directory.
1. For the first deployment you will have to be manually trigger all cloud function build triggers, by clicking `run` 
   on the [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers) section of the GCP console.

Now each time you push code to your branch `<branch-ref-suffix>`, cloud functions will rebuild 
(using `./cloud-func-build.yaml`) and deploy using the pushed code. For the build to be successful, all present tests 
must pass.

# Manager

```
.
├── bigquery                     # package which handles writting results to BigQuery
│   ├── __init__.py              # contains high level functions, acts as api
│   ├── queries.py               # functions which dynamically create SQL queries for summary tables
│   ├── read.py                  # extracting information for BigQuery
│   └── write.py                 # logic for writing information to BigQuery
├── check_matches.py             # checks selected numbers againsts scraped results
├── __init__.py
├── scrape_results.py            # using bs4 scrape latest draw results, including prize breakdown
└── tools.py
```

The modules `check_matches.py`, `scrape_results.py` and `tools.py` have mostly remained intact from the original repo. 

## Manager Tests

All the tests in `./tests` directory are tests for the `manager` package. 

Unittest written for:
   
   * `check_matches.py`
   * `scrape_results.py`
   * `tools.py`

Integration tests written for all functions in `./manager/bigquery/*`.

All tests must pass before cloud functions are built by Cloud Build. 

In order for Cloud Build to run tests, it will install all listed dependencies for a given cloud 
function: `./functions/<cloud-func>/src/requirements.txt`.

In order to for Cloud Build to run the integration tests, it will require specific permission to interact with BigQuery.
These are: 
* bigquery.readsessions.getData
* bigquery.readsessions.create
* bigquery.jobs.create
* bigquery.datasets.create
* bigquery.datasets.delete
* bigquery.tables.create
* bigquery.tables.list
* bigquery.tables.delete 
* bigquery.tables.getData

The script - `./scripts/gcp-setup.sh` - creates a custom role with the permissions listed above and assigns it to 
Cloud Build. See "STEP 7/8 Adding permissions" in the script.


# Scripts

### `gcp-setup.sh`

This script is used to create a Google Cloud Project from scratch. It will use Google's `gcloud` sdk and will require 
authorisation to run.

The script expects: 

* One argument, (string) used as a suffix for your project name and id. The same suffix is later used to
  reference to your git branch. e.g. "main" or "##-new-feature".
* Expects an environment variable: `BILLING_ACCOUNT_ID` which should be set to your 
  [GCP billing account ID](https://console.cloud.google.com/billing).
* A CSV in the root directory which contains the selected numbers.

The script will:

1. Create a project and link it to the billing account ID.
1. Enable various GCP APIs like BigQuery, Cloud Functions, etc.
1. Create BigQuery dataset called `manager`, where all high level tables are kept.
1. Validate and upload the selected numbers csv to the `manager` dataset.
1. Provide all the various APIs the minimum permissions needed to do their respective jobs.
1. Create a Cloud Scheduler and Topic to trigger the `lotto-manager` every week.

### `gcp-setup.sh`

The script expects: 
* One argument, (string) reference to your git branch used by CI/CD triggers. i.e. When you push to your branch,
  execute trigger.
  
The script will:
1. Loop over all directories in `./functions` which has a `src` subdirectory. 
1. Then using `gcloud` commands, build instructions from `./scripts/cloud-func-build.yaml` and user defined variables 
   from `./functions/<cloud-func>/variables.txt` to create Cloud Build Triggers for each cloud function if one doesn't 
   already exist. If one exists, skip build.
   
**Note** - If you change `./functions/<cloud-func>/variables.txt` or anything specific to the build instructions 
           you will have to delete the triggers and run the script again.

### `cloud-func-build.yaml`

Build configurations (instructions) used by the Cloud Build Triggers to build each Cloud Function. The configurations
contain two steps:

1. **Run Tests**
   * Copy over the local libraries specified by `load` in `variables.txt` to `./functions/<cloud-func>/`.
   * If manager selected by `load`, also copy over `./tests` to `./functions/<cloud-func>/tests`.
   * Pip install requirements.txt.
   * Run all tests in `./functions/<cloud-func>/tests/`.
   
1. **Deploy Function** if step 1 successful.

#### Cloud function build variables

The expected variables are:
* `trigger`: Trigger type used by cloud function. e.g. `trigger-http`. [Options](https://cloud.google.com/functions/docs/concepts/events-triggers#triggers).
* `runtime`: Language used at runtime. e.g. `runtime=python38`. [Options](https://cloud.google.com/functions/docs/concepts/exec#runtimes).
* `memory`: Cloud function memory allocation. More memory, higher costs. e.g. `memory=128mb`. [Options](https://cloud.google.com/functions/docs/concepts/exec#memory).
* `timeout`: Cloud function execution time out. e.g. `timeout=60s`. [Options](https://cloud.google.com/functions/docs/concepts/exec#timeout). 
* `load`: Used to determine which shared folders to upload with the cloud function. e.g. `load=manager`.
  Options={'cloud_utils', 'manager', 'manager,cloud_utils', ''}.
