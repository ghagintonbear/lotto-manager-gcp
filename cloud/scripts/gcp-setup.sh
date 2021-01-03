#!/bin/bash
set -e # if error exit

# script variables
PROJECT_ID="euro-lotto-manager" # Project IDs must be between 6 and 30 characters.
REGION="europe-west2"  # europe-west2 is London
BUCKET_NAME="results-${PROJECT_ID}"

# Check BILLING_ACCOUNT_ID is set
if [ -n "${BILLING_ACCOUNT_ID}" ]; then
    echo
    echo "Using BILLING_ACCOUNT_ID environment variable."
    echo
else
    echo
    echo "*** ERROR ***"
    echo "Please set BILLING_ACCOUNT_ID environment variable."
    echo "You can find it here: https://console.cloud.google.com/billing"
    echo "Exiting..."
    echo
    exit
fi


echo "*** STEP 1: Requesting for Authentication ***"
echo
gcloud auth login


echo
echo "*** STEP 2: Creating Project ***"
echo
gcloud projects create ${PROJECT_ID}

PROJECT_NUMBER=`gcloud projects list --filter=${PROJECT_ID} --format="value(PROJECT_NUMBER)"`

echo
echo "*** STEP 3: Link Project to billing account ***"
echo
gcloud alpha billing projects link ${PROJECT_ID} \
    --billing-account ${BILLING_ACCOUNT_ID}

echo
echo "*** STEP 4: Selecting Project ***"
echo
gcloud config set project ${PROJECT_ID}


echo
echo "*** STEP 5 Creating buckets ***"
echo
gsutil mb -c standard -l ${REGION} gs://${BUCKET_NAME}  # Where results will be stored